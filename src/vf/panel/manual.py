"""Brand manual generated from the gallery (brand.json, brief.md, assets, job sheets) and exported to PDF.

Same sections as a hand-made manual: cover, logo on approved backgrounds, colors (HEX/RGB/CMYK),
typography, tone of voice, clear space and minimum size, don'ts, applications and files.
"""
import html
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import quote

from ..core.paths import APROVAR

CHROME_CANDIDATES = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
]


class ManualError(RuntimeError):
    pass


def _e(s) -> str:
    return html.escape(str(s or ''))


def _rgb(hexcolor: str) -> tuple[int, int, int]:
    h = hexcolor.lstrip('#')
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _cmyk(r: int, g: int, b: int) -> str:
    if (r, g, b) == (0, 0, 0):
        return '0 0 0 100'
    c, m, y = 1 - r / 255, 1 - g / 255, 1 - b / 255
    k = min(c, m, y)
    return ' '.join(str(round(100 * (v - k) / (1 - k))) for v in (c, m, y)) + f' {round(100 * k)}'


def _luminance(hexcolor: str) -> float:
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = _rgb(hexcolor)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def _ink_on(hexcolor: str) -> str:
    return '#11151c' if _luminance(hexcolor) > 0.45 else '#ffffff'


def _brief_section(brief: str, title: str) -> str:
    m = re.search(rf'^##\s*{re.escape(title)}\s*\n(.*?)(?=^##\s|\Z)', brief, re.S | re.M | re.I)
    return m.group(1).strip() if m else ''


def _sheets(folders: list[Path], limit: int = 6) -> list[Path]:
    found = []
    for base in folders:
        if base.is_dir():
            found += list(base.glob(f'**/{APROVAR}/storyboard_folha.png'))
    found.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return found[:limit]


def _inline(text: str) -> str:
    out = html.escape(text)
    out = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', out)
    return re.sub(r'`(.+?)`', r'<code>\1</code>', out)


def _md_sections(md: str) -> dict:
    parts = re.split(r'^##\s+(.+?)\s*$', md, flags=re.M)
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def _md_html(text: str) -> str:
    """Bullets and paragraphs of a guide section as HTML (bold and code supported)."""
    items = [l[2:].strip() for l in text.splitlines() if l.startswith('- ')]
    paras = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith('- ')]
    return ('<ul>' + ''.join(f'<li>{_inline(i)}</li>' for i in items) + '</ul>' if items else '') + \
        ''.join(f'<p>{_inline(p)}</p>' for p in paras)


def load_brand(home: Path) -> dict:
    """Brand data for the manual. marca.json (client standard) wins; brand.json (gallery workspace) is the fallback."""
    f = home / 'marca.json'
    if f.is_file():
        try:
            m = json.loads(f.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            m = {}
        c = m.get('cores', {})
        labels = (('destaque', 'Destaque'), ('primaria', 'Primária'), ('secundaria', 'Apoio'), ('texto', 'Texto'), ('fundo', 'Fundo claro'))
        colors = [{'name': n, 'hex': c[k]} for k, n in labels if c.get(k)]
        grads = []
        if (m.get('forma') or {}).get('degrade'):
            grads.append({'name': 'Fundo (padrão)', 'tones': m['forma']['degrade']})
        for k, v in (m.get('forma_variantes') or {}).items():
            if v.get('degrade'):
                grads.append({'name': f'Variante {k}', 'tones': v['degrade']})
        fonts = m.get('fontes') or {}
        guide = home / 'identidade' / 'guia-visual.md'
        return {
            'client': True, 'name': m.get('nome', ''), 'tagline': m.get('descricao', ''), 'colors': colors, 'gradients': grads,
            'accent': c.get('destaque'), 'cover': c.get('primaria') or c.get('destaque'),
            'fonts': {'display': (fonts.get('titulo') or {}).get('familia', ''), 'body': (fonts.get('corpo') or {}).get('familia', '')},
            'logo': (m.get('logo') or {}).get('arquivo', ''), 'cta': (m.get('cta') or {}).get('texto', ''),
            'tone': m.get('tom', ''), 'avoid': m.get('proibidos', []), 'contacts': m.get('contatos', {}),
            'certs': (m.get('certificacoes') or {}).get('itens', []), 'authorized': (m.get('clientes_autorizados') or {}).get('nomes', []),
            'guide': _md_sections(guide.read_text(encoding='utf-8')) if guide.is_file() else {}}
    if (home / 'brand.json').is_file():
        try:
            return json.loads((home / 'brand.json').read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            pass
    return {}


def _catalog_photos(home: Path, limit: int = 6) -> list:
    idx = home / 'assets' / 'index.json'
    if not idx.is_file():
        return []
    items = [i for i in json.loads(idx.read_text(encoding='utf-8')).get('items', [])
             if i['kind'] == 'image' and 'cover' in i.get('use', []) and not i['blank'] and not i['duplicate_of'] and 'discard' not in i['use']]
    items.sort(key=lambda i: ({'alta': 0, 'media': 1, 'baixa': 2}[i['quality']], i['orient'] != 'vertical'))
    return items[:limit]


def _pack_grids(home: Path) -> list:
    return sorted((home / 'exports').glob('*/grade.png')) if (home / 'exports').is_dir() else []


def build_html(gallery: dict, home: Path, folders: list[Path]) -> str:
    def url(path: Path) -> str:
        for i, base in enumerate(folders):
            try:
                rel = path.resolve().relative_to(base.resolve()).as_posix()
                return f'/file?g={quote(gallery["id"])}&b={i}&p={quote(rel)}'
            except ValueError:
                continue
        return ''

    brand = load_brand(home)
    brief = (home / 'brief.md').read_text(encoding='utf-8') if (home / 'brief.md').is_file() else ''
    name = brand.get('name') or gallery['name']
    colors = brand.get('colors') or [{'name': 'principal', 'hex': '#2d6be0'}]
    primary = brand.get('accent') or colors[0]['hex']
    cover_bg = brand.get('cover') or primary
    dark = next((c['hex'] for c in colors if _luminance(c['hex']) < 0.08), '#11151c')
    fonts = brand.get('fonts') or {}
    display, body = fonts.get('display') or 'Archivo', fonts.get('body') or 'Inter'
    logo_path = home / brand['logo'] if brand.get('logo') else None
    icon_path = home / brand['icon'] if brand.get('icon') else None
    logo = (f'<img class="logo" src="{url(logo_path)}" alt="{_e(name)}">' if logo_path and logo_path.is_file()
            else f'<span class="wordmark">{_e(name)}</span>')
    icon = f'<img class="icon" src="{url(icon_path)}" alt="">' if icon_path and icon_path.is_file() else ''
    families = '&'.join('family=' + quote(f).replace('%20', '+') + ':wght@400;600;800' for f in dict.fromkeys([display, body]))

    swatches = ''.join(
        f'<div class="sw"><div class="chip" style="background:{c["hex"]};color:{_ink_on(c["hex"])}">{_e(c.get("name", ""))}</div>'
        f'<div class="sw-body"><code>{c["hex"].upper()}</code><span>RGB {" ".join(map(str, _rgb(c["hex"])))}</span>'
        f'<span>CMYK {_cmyk(*_rgb(c["hex"]))}</span></div></div>' for c in colors)
    tone = _brief_section(brief, 'Tom de voz') or brand.get('tone', '')
    audience = _brief_section(brief, 'Público')
    goal = _brief_section(brief, 'Objetivo')
    voice = ''.join(f'<li>{_e(v)}</li>' for v in brand.get('voice', []))
    avoid = ''.join(f'<li>{_e(v)}</li>' for v in brand.get('avoid', []))
    voice = voice or ''
    sheets = ''.join(f'<figure><img src="{url(p)}" alt=""><figcaption>{_e(p.parent.parent.name)}</figcaption></figure>'
                     for p in _sheets(folders))
    brand_files = sorted((home / 'assets' / 'brand').glob('*')) if (home / 'assets' / 'brand').is_dir() else []
    files = ''.join(f'<li><code>{_e(f.relative_to(home).as_posix())}</code></li>' for f in brand_files)

    sections = []
    n = 0

    def section(title, eyebrow, content, note=''):
        nonlocal n
        n += 1
        sections.append(f'<section><header><span class="eyebrow">{n:02d} · {eyebrow}</span><h2>{title}</h2>'
                        f'{f"<p>{note}</p>" if note else ""}</header>{content}</section>')

    section('Logo e fundos aprovados', 'Logo',
            f'<div class="bgs"><div class="bg" style="background:#ffffff">{logo}<span>fundo claro</span></div>'
            f'<div class="bg" style="background:{dark};color:#fff">{logo}<span>fundo escuro</span></div>'
            f'<div class="bg" style="background:{primary};color:{_ink_on(primary)}">{logo}<span>cor principal</span></div></div>'
            + (f'<div class="icon-row">{icon}<span>ícone: para espaços pequenos (avatar, favicon, ícone de app)</span></div>' if icon else ''),
            'Use o logo sempre a partir do arquivo original. Em fundo de cor ou foto, confira o contraste antes de publicar.')
    grads = ''.join(
        f'<div class="grad"><div class="gbar" style="background:linear-gradient(90deg,{",".join(g["tones"])})"></div>'
        f'<div class="gtxt"><b>{_e(g["name"])}</b><span>{" · ".join(t.upper() for t in g["tones"])}</span></div></div>'
        for g in brand.get('gradients', []))
    section('Cores', 'Cor', f'<div class="swatches">{swatches}</div>' + (f'<h3 class="sub">Fundos em degradê</h3><div class="grads">{grads}</div>' if grads else ''),
            'A primeira cor é a principal: botões, destaques e chamadas. CMYK é uma conversão aproximada: confirme com a gráfica.')
    section('Tipografia', 'Tipografia',
            f'<div class="type"><div><span class="eyebrow">Títulos · {_e(display)}</span><p class="t-display">{_e(name)}</p></div>'
            f'<div><span class="eyebrow">Texto · {_e(body)}</span><p class="t-body">Texto corrido, legendas e informações. '
            f'Frases curtas, uma ideia por linha nos vídeos.</p></div></div>')
    if tone or voice or avoid or audience or goal:
        section('Tom de voz', 'Voz',
                (f'<div class="tone">{f"<div><h3>Objetivo</h3><p>{_e(goal)}</p></div>" if goal else ""}'
                 f'{f"<div><h3>Público</h3><p>{_e(audience)}</p></div>" if audience else ""}'
                 f'{f"<div><h3>Como fala</h3><p>{_e(tone)}</p></div>" if tone else ""}</div>'
                 f'<div class="lists">{f"<div><h3>Palavras que usa</h3><ul>{voice}</ul></div>" if voice else ""}'
                 f'{f"<div><h3>Evita</h3><ul>{avoid}</ul></div>" if avoid else ""}</div>'))
    guide = brand.get('guide') or {}
    if guide.get('Formas e composição') or guide.get('Fotografia'):
        demo = (f'<div class="shapes"><span class="tagdemo" style="--c:{primary}">Etiqueta</span>'
                f'<span class="tagdemo band">Faixa translúcida</span><span class="tagdemo num" style="--c:{primary}">20+</span></div>')
        blocks = ''.join(f'<div class="gcard"><h3>{_e(k)}</h3>{_md_html(guide[k])}</div>'
                         for k in ('Formas e composição', 'Tipografia', 'Cor e fundo', 'Variantes', 'Fotografia') if guide.get(k))
        section('Forma da marca', 'Forma', demo + f'<div class="gcards">{blocks}</div>',
                'O que dá a cara da marca além das cores: formas, ângulos, tipografia e uso de foto.')
    photos = _catalog_photos(home)
    if photos:
        figs = ''.join(f'<figure><img loading="lazy" src="{url(home / "assets" / i["path"])}" alt=""><figcaption>{_e(i["subject"][:70])}</figcaption></figure>'
                       for i in photos)
        section('Fotografia', 'Imagem', f'<div class="apps">{figs}</div>', 'Fotos do catálogo do cliente marcadas para capa.')
    section('Respiro e tamanho mínimo', 'Tamanho',
            f'<div class="rules"><div class="space"><span class="tag">respiro</span>{logo}</div>'
            f'<div><p>Deixe em volta do logo um espaço livre de pelo menos um quarto da altura dele. Nada de texto, borda ou outro logo dentro dessa área.</p>'
            f'<p>Tamanho mínimo: 80 px de largura na tela e 20 mm no impresso. Abaixo disso, use o ícone.</p></div></div>')
    section('Usos proibidos', 'Não fazer',
            f'<div class="donts"><div class="dont"><div class="stage">{logo.replace("class=", "style=\"transform:scaleX(1.4)\" class=", 1)}</div><p>Esticar ou achatar.</p></div>'
            f'<div class="dont"><div class="stage">{logo.replace("class=", "style=\"filter:hue-rotate(150deg)\" class=", 1)}</div><p>Trocar as cores.</p></div>'
            f'<div class="dont"><div class="stage" style="background:{primary}">{logo.replace("class=", "style=\"opacity:.35\" class=", 1)}</div><p>Usar sem contraste.</p></div>'
            f'<div class="dont"><div class="stage">{logo.replace("class=", "style=\"filter:drop-shadow(4px 4px 3px rgba(0,0,0,.6))\" class=", 1)}</div><p>Aplicar sombra ou efeito.</p></div></div>')
    pack = ''.join(f'<figure><img src="{url(g)}" alt=""><figcaption>{_e(g.parent.name)}: grade do perfil</figcaption></figure>' for g in _pack_grids(home))
    covers = ''
    for cfg in sorted(home.glob('p[0-9][0-9]-*/3-final/png/01.png'))[:6]:
        covers += f'<figure><img loading="lazy" src="{url(cfg)}" alt=""><figcaption>{_e(cfg.parent.parent.parent.name)}</figcaption></figure>'
    if sheets or pack or covers:
        section('Aplicações', 'Em uso', f'<div class="apps">{pack}{covers}{sheets}</div>', 'Peças produzidas para esta marca.')
    ct = brand.get('contacts') or {}
    facts = ''
    if ct:
        rows = ''.join(f'<li><b>{_e(k.replace("_", " "))}:</b> {_e(v)}</li>' for k, v in ct.items() if k != 'fonte')
        facts += f'<div class="gcard"><h3>Contatos oficiais</h3><ul>{rows}</ul></div>'
    if brand.get('certs'):
        facts += '<div class="gcard"><h3>Certificações</h3><ul>' + ''.join(f'<li>{_e(c)}</li>' for c in brand['certs']) + '</ul></div>'
    if brand.get('authorized'):
        facts += '<div class="gcard"><h3>Clientes que podem ser citados</h3><ul>' + ''.join(f'<li>{_e(c)}</li>' for c in brand['authorized']) + '</ul></div>'
    if facts:
        section('Dados que podem ser usados', 'Dados', f'<div class="gcards">{facts}</div>', 'Informações confirmadas pelo responsável da marca.')
    if files:
        section('Arquivos', 'Arquivos', f'<ul class="files">{files}</ul>')

    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Manual de marca · {_e(name)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{families}&family=JetBrains+Mono:wght@400&display=swap">
<style>
:root{{--primary:{primary};--cover:{cover_bg};--ink:#11151c;--muted:#5a6270;--line:#e3e6ec;--page:#f4f5f8}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--page);color:var(--ink);font:15px/1.55 '{_e(body)}',system-ui,sans-serif}}
main{{max-width:980px;margin:0 auto;padding:28px 20px 60px;display:grid;gap:48px}}
h1,h2,h3{{font-family:'{_e(display)}',system-ui,sans-serif;margin:0;line-height:1.1}}
h2{{font-size:26px}}h3{{font-size:15px;margin-bottom:4px}}
p{{margin:0;max-width:64ch}}
code{{font-family:'JetBrains Mono',monospace;font-size:.85em}}
.eyebrow{{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}}
section{{display:grid;gap:16px;break-inside:avoid}}
section>header{{display:grid;gap:6px}}
.cover{{background:var(--cover);color:{_ink_on(cover_bg)};border-radius:20px;padding:56px 44px;display:grid;gap:28px;min-height:420px;align-content:space-between}}
.cover .eyebrow{{color:inherit;opacity:.75}}
.cover h1{{font-size:44px}}
.logo{{max-width:min(100%,320px);max-height:120px;object-fit:contain;display:block}}
.wordmark{{font-family:'{_e(display)}',system-ui,sans-serif;font-weight:800;font-size:34px;letter-spacing:-.01em}}
.bgs{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.bg{{border-radius:14px;padding:34px 20px 14px;display:grid;gap:22px;justify-items:center;border:1px solid var(--line)}}
.bg .logo{{max-width:200px;max-height:80px}}.bg .wordmark{{font-size:24px}}
.bg span{{font-family:'JetBrains Mono',monospace;font-size:11px;opacity:.75}}
.icon-row{{display:flex;gap:14px;align-items:center;background:#fff;border-radius:14px;padding:16px}}
.icon{{width:64px;height:64px;object-fit:contain}}
.swatches{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}}
.sw{{background:#fff;border-radius:14px;overflow:hidden;border:1px solid var(--line)}}
.chip{{height:100px;display:flex;align-items:flex-end;padding:10px 12px;font-weight:600;text-transform:capitalize}}
.sw-body{{padding:10px 12px;display:grid;gap:2px;font-size:12.5px;color:var(--muted)}}
.sw-body code{{color:var(--ink);font-size:13px}}
.type{{display:grid;gap:18px;background:#fff;border-radius:14px;padding:22px;border:1px solid var(--line)}}
.t-display{{font-family:'{_e(display)}',system-ui,sans-serif;font-weight:800;font-size:40px;line-height:1.05}}
.t-body{{font-size:17px}}
.tone,.lists{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}}
.tone>div,.lists>div{{background:#fff;border-radius:14px;padding:16px 18px;border:1px solid var(--line)}}
.lists ul{{margin:0;padding-left:18px}}
.rules{{display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:center;background:#fff;border-radius:14px;padding:22px;border:1px solid var(--line)}}
.rules p+p{{margin-top:10px}}
.space{{position:relative;justify-self:center;padding:28px;outline:1.5px dashed var(--primary);border-radius:4px}}
.space .tag{{position:absolute;top:4px;left:6px;font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--primary)}}
.donts{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
.dont{{background:#fff;border-radius:14px;overflow:hidden;border:1px solid var(--line)}}
.stage{{height:120px;display:grid;place-items:center;padding:14px;position:relative;overflow:hidden}}
.stage .logo{{max-width:140px;max-height:60px}}.stage .wordmark{{font-size:20px}}
.stage::after{{content:"";position:absolute;inset:10px;background:linear-gradient(to top right,transparent calc(50% - 1px),#c2341f calc(50% - 1px),#c2341f calc(50% + 1px),transparent calc(50% + 1px));opacity:.6}}
.dont p{{padding:10px 14px 14px;font-size:13px}}
.apps{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}}
.apps figure{{margin:0;background:#fff;border-radius:14px;overflow:hidden;border:1px solid var(--line)}}
.apps img{{width:100%;display:block}}
.apps figcaption{{padding:8px 12px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted)}}
.files{{margin:0;padding-left:18px;display:grid;gap:4px}}
@media (max-width:760px){{.bgs,.donts,.rules{{grid-template-columns:1fr 1fr}}}}
.sub{{margin-top:6px;font-size:13px;color:var(--muted)}}
.grads{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}}
.grad{{background:#fff;border-radius:14px;overflow:hidden;border:1px solid var(--line)}}
.gbar{{height:70px}}.gtxt{{padding:10px 12px;display:grid;gap:2px;font-size:12.5px;color:var(--muted)}}.gtxt b{{color:var(--ink)}}
.gcards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}}
.gcard{{background:#fff;border-radius:14px;padding:16px 18px;border:1px solid var(--line)}}
.gcard ul{{margin:6px 0 0;padding-left:18px;display:grid;gap:4px}}.gcard p{{margin-top:6px}}
.shapes{{display:flex;flex-wrap:wrap;gap:14px;align-items:center;background:#11151c;border-radius:14px;padding:22px}}
.tagdemo{{position:relative;isolation:isolate;color:#fff;padding:10px 26px;font-family:'JetBrains Mono',monospace;font-size:13px;letter-spacing:.12em;text-transform:uppercase}}
.tagdemo::before{{content:"";position:absolute;inset:0;background:var(--c,#ffffff22);transform:skewX(-14deg);z-index:-1}}
.tagdemo.band::before{{background:rgba(255,255,255,.12)}}.tagdemo.num{{font-size:26px;font-family:'{_e(display)}',system-ui,sans-serif}}
@page{{size:A4;margin:12mm}}
@media print{{body{{background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}}main{{padding:0;gap:28px}}.cover{{min-height:250mm;break-after:page}}section{{break-inside:avoid}}}}
</style></head><body><main>
<div class="cover"><span class="eyebrow">Manual de marca</span><div style="display:grid;gap:18px">{logo}<h1>{_e(name)}</h1>
{f"<p>{_e(brand.get('tagline'))}</p>" if brand.get('tagline') else ''}</div>
{f"<p>{_e(brand.get('cta'))}</p>" if brand.get('cta') else '<span></span>'}</div>
{''.join(sections)}
</main></body></html>"""


def find_browser() -> str:
    for exe in ('chrome', 'google-chrome', 'chromium', 'msedge'):
        found = shutil.which(exe)
        if found:
            return found
    for path in CHROME_CANDIDATES:
        if os.path.isfile(path):
            return path
    raise ManualError('não achei o Chrome ou o Edge para gerar o PDF')


def export_pdf(manual_url: str, home: Path) -> Path:
    out = home / 'exports' / 'manual-de-marca.pdf'
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix('.tmp.pdf')
    cmd = [find_browser(), '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
           '--virtual-time-budget=8000', f'--print-to-pdf={tmp}', manual_url]
    try:
        subprocess.run(cmd, capture_output=True, timeout=90)
    except subprocess.TimeoutExpired as e:
        raise ManualError('o navegador demorou demais para gerar o PDF') from e
    if not tmp.is_file() or tmp.stat().st_size < 1000:
        raise ManualError('o PDF não foi gerado')
    tmp.replace(out)
    return out
