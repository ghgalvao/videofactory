"""Slide deck (16:9) for a client presentation, built from documentos/presentation.json.

The deck uses the client's marca.json (colors, title font, logo, diagonal shape) so it reads as their brand.
Images are paths relative to the client folder; they are downscaled to JPEG and embedded, so the same HTML
works offline, inside the panel and when printed to PDF (one 1920x1080 page per slide).

Slide types (field "tipo"):
  capa      titulo, subtitulo, kicker, imagem
  secao     numero, titulo, texto
  texto     titulo, texto (str or list of paragraphs), itens, imagem
  numeros   titulo, itens [{valor, rotulo}], nota
  galeria   titulo, texto, imagens [{arquivo, legenda}]
  tabela    titulo, cabecalho [], linhas [[]], nota
  planos    titulo, planos [{nome, preco, sub, destaque, itens []}], nota
  passos    titulo, itens [{titulo, texto}]
  video     titulo, texto, poster, arquivo, link (plays inside the panel; in the PDF the poster opens `link`, e.g. YouTube)
  cta       titulo, texto, contato []
Any text may use *word* to paint that word in the accent color.
"""
import base64
import html
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FONT = ROOT / 'video' / 'assets' / 'fonts' / 'Orbitron.ttf'

CSS = """
@page{size:1920px 1080px;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0b0f16;font-family:"Segoe UI",Inter,Arial,sans-serif;color:var(--txt)}
.slide{position:relative;width:1920px;height:1080px;overflow:hidden;background:var(--bg);break-after:page;padding:110px 130px 120px}
.slide::before{content:"";position:absolute;inset:-20%;background:linear-gradient(var(--ang),var(--g1),var(--g2) 55%,var(--g3));opacity:.9;z-index:0}
.slide>*{position:relative;z-index:1}
.slide .faixa{position:absolute;right:-180px;top:-200px;width:620px;height:1500px;background:rgba(255,255,255,.035);transform:rotate(14deg);z-index:0}
h1,h2,.num b,.plano .preco,.passo i{font-family:"Titulo","Segoe UI",sans-serif;text-transform:uppercase;letter-spacing:2px}
h1{font-size:104px;line-height:1.02;font-weight:800}
h2{font-size:62px;line-height:1.08;font-weight:800;margin-bottom:46px;max-width:1500px}
.acc{color:var(--acc)}
.kicker{display:inline-block;align-self:flex-start;position:relative;padding:12px 34px;margin-bottom:38px;font:600 26px/1 "Segoe UI",sans-serif;letter-spacing:6px;text-transform:uppercase;color:#fff}
.kicker::before{content:"";position:absolute;inset:0;background:var(--acc);transform:skewX(-14deg);z-index:-1}
p,li{font-size:34px;line-height:1.45;color:var(--txt2)}
p+p{margin-top:18px}
ul{list-style:none;margin-top:18px}
li{padding-left:42px;position:relative;margin:12px 0}
li::before{content:"";position:absolute;left:0;top:.55em;width:18px;height:18px;background:var(--acc);transform:skewX(-14deg)}
.rodape{position:absolute;left:130px;right:130px;bottom:46px;display:flex;justify-content:space-between;align-items:center;font-size:22px;color:var(--txt3);z-index:2}
.rodape img{height:40px}
.capa{display:flex;flex-direction:column;justify-content:center}
.capa .bgimg{position:absolute;inset:0;background-size:cover;background-position:center;opacity:.28;z-index:0}
.capa .logo{height:120px;margin-bottom:70px;align-self:flex-start}
.capa .sub{font-size:40px;margin-top:34px;max-width:1300px;color:var(--txt2)}
.secao{display:flex;flex-direction:column;justify-content:center}
.secao .n{font-family:"Titulo",sans-serif;font-size:220px;line-height:1;color:var(--acc);opacity:.9;font-weight:800}
.lado{display:grid;grid-template-columns:1.1fr .9fr;gap:80px;align-items:center}
.lado img{width:100%;max-height:720px;object-fit:cover;border:5px solid var(--acc);box-shadow:0 30px 80px rgba(0,0,0,.5)}
.nums{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:40px;margin-top:20px}
.num{background:rgba(255,255,255,.05);border-left:8px solid var(--acc);padding:44px 40px}
.num b{display:block;font-size:84px;color:#fff;font-weight:800}
.num span{font-size:30px;color:var(--txt2)}
.nota{margin-top:34px;font-size:26px;color:var(--txt3)}
.gal{display:flex;gap:34px;align-items:flex-start;justify-content:center}
.gal figure{flex:1;min-width:0}
.gal img{display:block;width:100%;height:auto;max-height:610px;object-fit:contain}
.gal figcaption{font-size:24px;color:var(--txt2);margin-top:14px;text-align:center}
.gal.cover img{object-fit:cover;border:4px solid rgba(255,255,255,.12)}
table{width:100%;border-collapse:collapse;font-size:30px}
th{font:700 22px/1.2 "Segoe UI",sans-serif;letter-spacing:3px;text-transform:uppercase;color:var(--acc);text-align:left;padding:0 22px 18px;border-bottom:3px solid var(--acc)}
td{padding:22px;border-bottom:1px solid rgba(255,255,255,.12);color:var(--txt2);vertical-align:top}
td:first-child{color:#fff;font-weight:600}
.planos{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:36px;align-items:stretch}
.plano{background:rgba(255,255,255,.05);padding:46px 42px;display:flex;flex-direction:column;border-top:8px solid rgba(255,255,255,.18)}
.plano.dest{background:rgba(255,107,53,.12);border-top-color:var(--acc);transform:translateY(-18px);box-shadow:0 30px 70px rgba(0,0,0,.45)}
.plano .tag{align-self:flex-start;margin-bottom:22px}
.plano h3{margin-bottom:18px;font:800 38px/1.1 "Titulo",sans-serif;text-transform:uppercase;letter-spacing:2px;color:#fff}
.plano .preco{font-size:62px;color:var(--acc);margin:22px 0 4px;font-weight:800}
.plano .sub{font-size:24px;color:var(--txt3)}
.plano li{font-size:27px;margin:9px 0}
.passos{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:34px}
.passo{background:rgba(255,255,255,.05);padding:40px 34px;border-top:6px solid var(--acc)}
.passo i{font-style:normal;font-size:64px;color:var(--acc);font-weight:800;display:block;margin-bottom:12px}
.passo b{display:block;font-size:32px;color:#fff;margin-bottom:12px}
.passo p{font-size:27px}
.video{display:grid;grid-template-columns:.9fr 1.1fr;gap:80px;align-items:center}
.video .tela{height:600px;aspect-ratio:9/16;justify-self:center;border:5px solid var(--acc);box-shadow:0 30px 80px rgba(0,0,0,.6);background:#000;position:relative}
.video .tela img,.video .tela video{width:100%;height:100%;object-fit:cover;display:block}
.video .play{position:absolute;inset:0;margin:auto;width:150px;height:150px;border-radius:50%;background:rgba(255,107,53,.92)}
.video .play::after{content:"";position:absolute;left:58px;top:44px;border-left:50px solid #fff;border-top:31px solid transparent;border-bottom:31px solid transparent}
.tela-link{display:flex;flex-direction:column;align-items:center;gap:18px;text-decoration:none;justify-self:center}
.assistir{position:relative;font:700 30px/1 "Segoe UI",sans-serif;color:#fff;letter-spacing:4px;text-transform:uppercase;padding:22px 48px}
.assistir::before{content:"";position:absolute;inset:0;background:var(--acc);transform:skewX(-14deg);z-index:-1;box-shadow:0 14px 36px rgba(0,0,0,.45)}
.cta{display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}
.cta .logo{height:130px;margin-bottom:60px}
.cta .kicker{align-self:center}
.cta p{max-width:1300px}
.cta .contatos{margin-top:50px;display:flex;gap:50px;flex-wrap:wrap;justify-content:center}
.cta .contatos span{font-size:30px;color:#fff;border-bottom:3px solid var(--acc);padding-bottom:6px}
.draft{position:absolute;top:40px;right:60px;z-index:5;font:700 22px/1 "Segoe UI";letter-spacing:4px;color:#fff;background:#c0392b;padding:10px 18px}
@media screen{body{padding:24px 0}.slide{margin:0 auto 24px;zoom:var(--z,1)}}
@media print{body{background:none;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
"""

FIT = """<script>
(function(){function fit(){var z=Math.min(1,(window.innerWidth-16)/1920);document.documentElement.style.setProperty('--z',z)}
fit();window.addEventListener('resize',fit);
var q=new URLSearchParams(location.search),g=q.get('g');
if(g){document.querySelectorAll('.tela-link').forEach(function(a){var t=a.querySelector('.tela');a.replaceWith(t)});document.querySelectorAll('[data-video]').forEach(function(t){var v=document.createElement('video');v.controls=true;v.preload='metadata';
v.poster=t.querySelector('img').src;v.src='/file?g='+encodeURIComponent(g)+'&b=0&p='+encodeURIComponent(t.getAttribute('data-video'));t.innerHTML='';t.appendChild(v)})}})();
</script>"""


def _e(x) -> str:
    return html.escape(str(x or ''))


def _t(x) -> str:
    """Escaped text with *accent* marks and line breaks."""
    return re.sub(r'\*([^*]+)\*', r'<span class="acc">\1</span>', _e(x)).replace('\n', '<br>')


def _paras(x) -> str:
    return ''.join(f'<p>{_t(p)}</p>' for p in ([x] if isinstance(x, str) else (x or [])) if p)


def _items(x) -> str:
    return f'<ul>{"".join(f"<li>{_t(i)}</li>" for i in x)}</ul>' if x else ''


def _has_alpha(p: Path) -> bool:
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=pix_fmt',
                        '-of', 'csv=p=0', str(p)], capture_output=True, text=True)
    return any(x in r.stdout for x in ('rgba', 'ya', 'argb', 'bgra', 'pal8'))


class Images:
    """Downscaled, embedded images (cached per build)."""

    def __init__(self, home: Path):
        self.home, self.cache = home, {}

    def src(self, rel: str, width: int = 1400) -> str:
        if not rel:
            return ''
        key = (rel, width)
        if key in self.cache:
            return self.cache[key]
        p = (self.home / rel)
        if not p.is_file():
            raise SystemExit(f'apresentação: imagem não existe: {rel}')
        if p.suffix.lower() == '.png' and p.stat().st_size < 400_000:
            data, mime = p.read_bytes(), 'image/png'
        else:
            png = p.suffix.lower() == '.png' and _has_alpha(p)  # keeps transparency (logos)
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / ('x.png' if png else 'x.jpg')
                subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(p), '-frames:v', '1',
                                '-vf', f"scale='min({width},iw)':-2", *([] if png else ['-q:v', '4']), str(out)], check=True)
                data, mime = out.read_bytes(), 'image/png' if png else 'image/jpeg'
        uri = f'data:{mime};base64,{base64.b64encode(data).decode()}'
        self.cache[key] = uri
        return uri


def _tela(s: dict, img: Images) -> str:
    tela = (f'<div class="tela" data-video="{_e(s.get("arquivo"))}"><img src="{img.src(s["poster"], 900)}" alt>'
            '<span class="play"></span></div>')
    if not s.get('link'):
        return tela
    return (f'<a class="tela-link" href="{_e(s["link"])}">{tela}<span class="assistir">&#9654;&nbsp; Assistir ao vídeo</span></a>')


def _slide(s: dict, img: Images, logo: str) -> str:
    k = s.get('tipo', 'texto')
    h2 = f'<h2>{_t(s["titulo"])}</h2>' if s.get('titulo') and k not in ('capa', 'secao', 'cta') else ''
    kick = f'<span class="kicker">{_e(s["kicker"])}</span>' if s.get('kicker') else ''
    if k == 'capa':
        bg = f'<div class="bgimg" style="background-image:url({img.src(s["imagem"], 1920)})"></div>' if s.get('imagem') else ''
        return (f'<section class="slide capa">{bg}{f"<img class=logo src={logo} alt>" if logo else ""}{kick}'
                f'<h1>{_t(s.get("titulo"))}</h1><p class="sub">{_t(s.get("subtitulo"))}</p></section>')
    if k == 'secao':
        return (f'<section class="slide secao"><div class="faixa"></div><div class="n">{_e(s.get("numero"))}</div>{kick}'
                f'<h1>{_t(s.get("titulo"))}</h1>{_paras(s.get("texto"))}</section>')
    if k == 'cta':
        cont = ''.join(f'<span>{_e(c)}</span>' for c in s.get('contato') or [])
        return (f'<section class="slide cta">{f"<img class=logo src={logo} alt>" if logo else ""}{kick}'
                f'<h1>{_t(s.get("titulo"))}</h1>{_paras(s.get("texto"))}<div class="contatos">{cont}</div></section>')
    body = ''
    if k == 'texto':
        txt = _paras(s.get('texto')) + _items(s.get('itens'))
        body = (f'<div class="lado"><div>{txt}</div><img src="{img.src(s["imagem"])}" alt></div>'
                if s.get('imagem') else txt)
    elif k == 'numeros':
        it = s.get('itens') or []
        body = (f'<div class="nums" style="--n:{len(it)}">' +
                ''.join(f'<div class="num"><b>{_t(i.get("valor"))}</b><span>{_t(i.get("rotulo"))}</span></div>' for i in it) + '</div>')
    elif k == 'galeria':
        figs = ''
        for i in s.get('imagens') or []:
            cap = f'<figcaption>{_t(i["legenda"])}</figcaption>' if i.get('legenda') else ''
            figs += f'<figure><img src="{img.src(i["arquivo"], 900)}" alt>{cap}</figure>'
        body = _paras(s.get('texto')) + f'<div class="gal{" cover" if s.get("cobrir") else ""}">{figs}</div>'
    elif k == 'tabela':
        head = ''.join(f'<th>{_e(c)}</th>' for c in s.get('cabecalho') or [])
        rows = ''.join('<tr>' + ''.join(f'<td>{_t(c)}</td>' for c in r) + '</tr>' for r in s.get('linhas') or [])
        body = f'<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>'
    elif k == 'planos':
        pl = s.get('planos') or []
        cards = ''
        for p in pl:
            tag = f'<span class="kicker tag">{_e(p["destaque"])}</span>' if isinstance(p.get('destaque'), str) else ''
            preco = f'<div class="preco">{_e(p["preco"])}</div>' if p.get('preco') else ''
            sub = f'<div class="sub">{_e(p["sub"])}</div>' if p.get('sub') else ''
            cards += (f'<div class="plano{" dest" if p.get("destaque") else ""}">{tag}<h3>{_t(p.get("nome"))}</h3>'
                      f'{preco}{sub}{_items(p.get("itens"))}</div>')
        body = f'<div class="planos" style="--n:{len(pl)}">{cards}</div>'
    elif k == 'passos':
        it = s.get('itens') or []
        body = (f'<div class="passos" style="--n:{len(it)}">' + ''.join(
            f'<div class="passo"><i>{n:02d}</i><b>{_t(i.get("titulo"))}</b><p>{_t(i.get("texto"))}</p></div>'
            for n, i in enumerate(it, 1)) + '</div>')
    elif k == 'video':
        body = (f'<div class="video"><div>{_paras(s.get("texto"))}{_items(s.get("itens"))}</div>'
                + _tela(s, img) + '</div>')
    else:
        raise SystemExit(f'apresentação: tipo de slide desconhecido: {k!r}')
    nota = f'<p class="nota">{_t(s["nota"])}</p>' if s.get('nota') else ''
    return f'<section class="slide"><div class="faixa"></div>{kick}{h2}{body}{nota}</section>'


def render(d: dict, cl: dict, ag: dict, home: Path, draft: bool) -> str:
    cores, forma = cl.get('cores') or {}, cl.get('forma') or {}
    deg = forma.get('degrade') or [cores.get('secundaria', '#1c2b37'), cores.get('primaria', '#0f172a'), cores.get('primaria', '#0f172a')]
    img = Images(home)
    logo_rel = (cl.get('logo') or {}).get('arquivo')
    logo = img.src(logo_rel, 900) if logo_rel else ''
    font = (f'@font-face{{font-family:"Titulo";src:url(data:font/ttf;base64,{base64.b64encode(FONT.read_bytes()).decode()})}}'
            if FONT.is_file() else '')
    root = (f':root{{--bg:{cores.get("primaria", "#0f172a")};--acc:{cores.get("destaque", "#ff6b35")};--txt:#f8fafc;'
            f'--txt2:rgba(248,250,252,.82);--txt3:rgba(248,250,252,.55);--g1:{deg[0]};--g2:{deg[1]};--g3:{deg[-1]};'
            f'--ang:{90 + int(forma.get("inclinacao_graus", -14))}deg}}')
    slides = d.get('slides') or []
    pages = []
    for n, s in enumerate(slides, 1):
        sec = _slide(s, img, logo)
        foot = '' if s.get('tipo') in ('capa', 'cta') else (
            f'<div class="rodape"><span>{_e(d.get("titulo"))}</span><span>{f"<img src={logo} alt>" if logo else ""}</span>'
            f'<span>{n:02d} / {len(slides):02d}</span></div>')
        mark = '<div class="draft">RASCUNHO</div>' if draft else ''
        pages.append(sec.replace('</section>', foot + mark + '</section>', 1) if sec.endswith('</section>') else sec)
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
            f'<title>{_e(d.get("titulo"))} · {_e(cl.get("nome"))}</title><style>{font}{root}{CSS}</style></head><body>'
            + ''.join(pages) + FIT + '</body></html>')
