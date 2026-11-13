"""Montador do estilo paper: transforma os `elementos` de cada plano do storyboard.json em HTML + animação.

Elemento (todas as posições pelo CENTRO, em px, quadro 1080x1920):
  {"tipo": "faixa|selo|carimbo|texto|objeto|calendario|barras|numero|etiqueta",
   "x": 540, "y": 400, "w": 900, "s": 120, "rot": -2, "cor": "#c0261f",
   "entrada": "cima|baixo|esquerda|direita|bate|cai|cresce|pop",
   "frase": 3, "atraso": 0.3,      # entra no início da frase 3 (+atraso). Sem "frase": usa "t" (s após o início do plano)
   "t": 0.6, "efeito": "tremor|balanca|pulsa", ...campos do tipo}
Texto aceita *palavra* (marca-texto amarelo) e \\n (quebra de linha).
"""
import html
import re

ST = 'stroke="#fff" stroke-width="12" stroke-linejoin="round" paint-order="stroke"'
VERMELHO = '#c0261f'


def _graos():
    pos = [(30, 60, 15), (62, 40, -20), (95, 70, 35), (128, 45, 10), (160, 72, -30), (80, 95, 5), (140, 100, 25), (45, 98, -12)]
    q = ''.join(f'<rect x="{x}" y="{y}" width="20" height="20" rx="3" transform="rotate({r} {x + 10} {y + 10})" '
                f'fill="#ffffff" stroke="#b8c4d0" stroke-width="3"/>' for x, y, r in pos)
    return f'<svg viewBox="0 0 200 140" width="100%">{q}</svg>'


def _sol():
    raios = ''.join(f'<rect x="94" y="6" width="12" height="40" rx="6" transform="rotate({i * 45} 100 100)"/>' for i in range(8))
    return f'<svg viewBox="0 0 200 200" width="100%"><g fill="#ffb300">{raios}</g><circle cx="100" cy="100" r="52" fill="#ffd23f" {ST}/></svg>'


def objeto_svg(nome: str, cor: str | None, rotulo: str) -> str:
    rot = html.escape(rotulo or '')
    if nome == 'copo':
        return (f'<svg viewBox="0 0 200 220" width="100%"><path d="M30 20 H170 L152 205 H48 Z" fill="#eaf4fb" {ST}/>'
                f'<path d="M37 80 H163 L152 205 H48 Z" fill="{cor or "#2f6fb5"}"/>'
                f'<path d="M30 20 H170" stroke="#9fb6c8" stroke-width="6"/>'
                f'<text x="100" y="160" text-anchor="middle" font-family="Impact" font-size="40" fill="#fff">{rot}</text></svg>')
    if nome == 'pedra':
        return (f'<svg viewBox="0 0 220 160" width="100%"><polygon points="20,140 40,60 95,25 165,40 205,115 150,150" fill="{cor or "#8e9199"}" {ST}/>'
                '<polygon points="95,25 165,40 120,70 70,60" fill="#a7aab2"/><circle cx="80" cy="105" r="8" fill="#6f727a"/>'
                '<circle cx="140" cy="95" r="6" fill="#6f727a"/></svg>')
    if nome == 'nuvem':
        return (f'<svg viewBox="0 0 240 200" width="100%"><g fill="#eef2f7" {ST}><circle cx="75" cy="85" r="45"/><circle cx="125" cy="65" r="55"/>'
                '<circle cx="175" cy="90" r="42"/><rect x="40" y="85" width="170" height="45" rx="22"/></g>'
                '<g fill="#4f8fe0"><ellipse cx="75" cy="165" rx="7" ry="12"/><ellipse cx="125" cy="178" rx="7" ry="12"/><ellipse cx="175" cy="165" rx="7" ry="12"/></g></svg>')
    if nome == 'sol':
        return _sol()
    if nome == 'mar':
        return (f'<svg viewBox="0 0 400 160" width="100%"><path d="M0 40 Q50 10 100 40 T200 40 T300 40 T400 40 V160 H0 Z" fill="{cor or "#2f6fb5"}" {ST}/>'
                '<path d="M0 78 Q50 52 100 78 T200 78 T300 78 T400 78" fill="none" stroke="#5f9ad8" stroke-width="8"/></svg>')
    if nome == 'rio':
        d = 'M20 20 C140 60 60 160 200 170 S 330 230 390 290'
        return (f'<svg viewBox="0 0 410 310" width="100%"><path d="{d}" fill="none" stroke="#fff" stroke-width="72" stroke-linecap="round"/>'
                f'<path d="{d}" fill="none" stroke="{cor or "#6fb3e8"}" stroke-width="54" stroke-linecap="round"/></svg>')
    if nome == 'graos':
        return _graos()
    if nome == 'seta':
        return f'<svg viewBox="0 0 200 80" width="100%"><path d="M10 30 H140 V10 L190 40 L140 70 V50 H10 Z" fill="{cor or "#1b1f2a"}" {ST}/></svg>'
    raise SystemExit(f'objeto desconhecido: {nome} (copo, pedra, nuvem, sol, mar, rio, graos, seta)')


def _txt(s: str) -> str:
    esc = html.escape(s or '')
    esc = re.sub(r'\*(.+?)\*', r'<span class="marca-wrap"><span class="marca-fundo"></span>\1</span>', esc)
    return esc.replace('\n', '<br />')


def _peca(conteudo: str, w: int, pad: str, fitas: int) -> str:
    fita = ''
    if fitas >= 1:
        fita += '<div class="fita" style="left:40px; top:-28px; transform: rotate(-8deg);"></div>'
    if fitas >= 2:
        fita += '<div class="fita" style="right:40px; top:-24px; transform: rotate(7deg);"></div>'
    return f'<div class="peca rasgado" style="width:{w}px; padding:{pad};">{conteudo}</div>{fita}'


def _html_el(eid: str, e: dict, dy: int = 0) -> str:
    tipo = e['tipo']
    x, y, rot = e.get('x', 540), e.get('y', 960) + dy, e.get('rot', 0)
    pos = f'left:{x}px; top:{y}px;'
    cor = e.get('cor')
    if tipo in ('faixa', 'selo'):
        w = e.get('w', 920 if tipo == 'faixa' else 440)
        s = e.get('s', 120 if tipo == 'faixa' else 70)
        dentro = f'<div class="titulo" style="font-size:{s}px; text-align:center; color:{cor or "var(--tinta)"};">{_txt(e["texto"])}</div>'
        miolo = _peca(dentro, w, '44px 46px' if tipo == 'faixa' else '34px 30px', 2 if tipo == 'faixa' else 1)
        return f'<div class="el" id="{eid}" data-rot="{rot}" style="{pos}">{miolo}</div>'
    if tipo == 'carimbo':
        s = e.get('s', 90)
        return (f'<div class="el carimbo titulo" id="{eid}" data-rot="{rot or -6}" '
                f'style="{pos} font-size:{s}px; border-color:{cor or VERMELHO}; color:{cor or VERMELHO};">{_txt(e["texto"])}</div>')
    if tipo == 'texto':
        return (f'<div class="el" id="{eid}" data-rot="{rot}" style="{pos} width:{e.get("w", 900)}px; font-size:{e.get("s", 54)}px; '
                f'font-style:italic; text-align:center;">{_txt(e["texto"])}</div>')
    if tipo == 'objeto':
        svg = objeto_svg(e['nome'], cor, e.get('rotulo', ''))
        return f'<div class="el" id="{eid}" data-rot="{rot}" style="{pos} width:{e.get("w", 300)}px;">{svg}</div>'
    if tipo == 'calendario':
        dentro = (f'<div style="background:{cor or "#b8312a"}; padding:26px 10px; text-align:center;"><div class="titulo" style="font-size:78px; color:#f4efe3;">{_txt(e.get("topo", ""))}</div></div>'
                  f'<div class="titulo" style="font-size:{e.get("s", 220)}px; text-align:center; margin-top:24px;">{_txt(e.get("grande", ""))}</div>'
                  f'<div style="font-size:64px; text-align:center; font-weight:bold; margin:16px 0 34px;">{_txt(e.get("sub", ""))}</div>')
        return f'<div class="el" id="{eid}" data-rot="{rot}" style="{pos}">{_peca(dentro, e.get("w", 680), "0", 1)}</div>'
    if tipo == 'barras':
        linhas = ''
        for i, ln in enumerate(e['linhas']):
            linhas += (f'<div class="linha" id="{eid}r{i}"><div class="rot">{_txt(ln["rotulo"])}</div><div class="lin">'
                       f'<div class="bar" style="background:{ln.get("cor", "#3b5b8c")};"></div><div class="titulo val">{html.escape(ln.get("texto", ""))}</div></div></div>')
        dentro = (f'<div class="titulo" style="font-size:80px; text-align:center; margin-bottom:56px;">{_txt(e.get("titulo", ""))}</div>{linhas}')
        return f'<div class="el" id="{eid}" data-rot="{rot}" style="{pos}">{_peca(dentro, e.get("w", 940), "56px 60px 20px", 1)}</div>'
    if tipo == 'numero':
        return (f'<div class="el titulo num" id="{eid}" data-rot="{rot}" style="{pos} font-size:{e.get("s", 300)}px; '
                f'color:{cor or VERMELHO}; white-space:nowrap;">{html.escape(e.get("pre", ""))}0{html.escape(e.get("suf", ""))}</div>')
    if tipo == 'etiqueta':
        dentro = (f'<div class="titulo" style="font-size:{e.get("s", 90)}px; text-align:center;">{_txt(e.get("topo", ""))}</div>'
                  f'<div class="titulo" style="font-size:{e.get("s2", 190)}px; text-align:center; color:{cor or VERMELHO}; margin-top:18px;">{_txt(e.get("grande", ""))}</div>')
        return f'<div class="el" id="{eid}" data-rot="{rot or -4}" style="{pos}">{_peca(dentro, e.get("w", 640), "66px 30px", 1)}</div>'
    raise SystemExit(f'tipo de elemento desconhecido: {tipo}')


def _js_el(eid: str, e: dict, t: float, frases: list) -> list[str]:
    sel = f'#{eid}'
    js = [f"      ent('{sel}', '{e.get('entrada', 'bate' if e['tipo'] == 'carimbo' else 'pop')}', {t:.3f});"]
    textos = ' '.join(str(e.get(k, '')) for k in ('texto', 'topo', 'grande', 'titulo'))
    if '*' in textos:
        js.append(f"      marca('{sel}', {t + 0.5:.3f});")
    if e.get('efeito'):
        js.append(f"      efeito('{sel}', '{e['efeito']}', {t + 0.6:.3f});")
    if e['tipo'] == 'numero':
        js.append(f"      contador('{sel}', {e['valor']}, {e.get('dec', 0)}, '{e.get('pre', '')}', '{e.get('suf', '')}', {t + 0.15:.3f}, {e.get('dur', 1.0)});")
    if e['tipo'] == 'barras':
        maximo = e.get('max') or max(ln['valor'] for ln in e['linhas'])
        largura_max = e.get('largura_max', 600)
        for i, ln in enumerate(e['linhas']):
            tl = (frases[ln['frase'] - 1] + ln.get('atraso', 0.1)) if 'frase' in ln else t + 0.5 + 0.6 * i
            larg = max(ln['valor'] / maximo * largura_max, 14)
            rsel = f'{sel}r{i}'
            js.append(f"      barra('{rsel}', {larg:.1f}, {tl:.3f});")
            if 'texto' in ln:
                js.append(f"      textoEm('{rsel}', {tl + 0.5:.3f});")
            else:
                js.append(f"      contador('{rsel} .val', {ln['valor']}, {ln.get('dec', 0)}, '', '{ln.get('suf', '')}', {tl:.3f}, 0.9);")
    return js


def montar(planos: list, frases: list, dy: int = 50) -> dict:
    """Retorna os marcadores __PLANOS__ (HTML) e __ANIM_PLANOS__ (JS) para video/paper.html."""
    blocos, anims = [], []
    for p in planos:
        n = p['id']
        dur = max(p['t1'] - p['t0'], 0.1)
        filhos = []
        for k, e in enumerate(p.get('elementos', [])):
            eid = f'p{n}e{k}'
            filhos.append(_html_el(eid, e, dy))
            t = (frases[e['frase'] - 1] + e.get('atraso', 0.1)) if 'frase' in e else p['t0'] + e.get('t', 0.05 + 0.35 * k)
            anims.extend(_js_el(eid, e, t, frases))
        blocos.append(f'      <div id="p{n}" class="clip plano" data-start="{p["t0"]:.3f}" data-duration="{dur:.3f}" '
                      f'data-track-index="1">{"".join(filhos)}</div>')
    return {'__PLANOS__': '\n'.join(blocos), '__ANIM_PLANOS__': '\n'.join(anims)}
