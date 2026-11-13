"""Cenários vetoriais (fundos) e bonequinho de palitos para o estilo stick-figure. Tudo SVG, sem imagem externa.

cenario: cena = ceu_lua | ceu | mar | recife | terra | terra_lua  (+ some_frase, reduz_frase, oscila_frase ...)
boneco: pose = aponta | lanterna | mede | triste | bracos | polegar | acena ; expr = feliz | triste | assustado | serio | curioso | pensativo
"""
import random

W, H = 1080, 1920


def _estrelas(seed: int, n: int, ymax: int) -> str:
    r = random.Random(seed)
    out = []
    for _ in range(n):
        out.append(f'<circle cx="{r.randint(10, W - 10)}" cy="{r.randint(10, ymax)}" r="{r.choice([1.5, 2, 2.5, 3.2])}" '
                   f'fill="#fff" opacity="{r.choice([0.45, 0.7, 0.95])}"/>')
    return ''.join(out)


def _onda(y0: int, amp: int, per: int, cor: str, op: float) -> str:
    pts = [f'M0 {y0}']
    for x in range(0, W + per, per):
        pts.append(f'Q{x + per // 4} {y0 - amp} {x + per // 2} {y0}')
        pts.append(f'Q{x + per * 3 // 4} {y0 + amp} {x + per} {y0}')
    pts.append(f'L{W + per * 2} {H} L0 {H} Z')
    return f'<path d="{" ".join(pts)}" fill="{cor}" opacity="{op}"/>'


def cenario_html(eid: str, e: dict) -> str:
    c = e['cena']
    defs = ''
    corpo = ''
    if c in ('ceu_lua', 'ceu'):
        defs = (f'<linearGradient id="{eid}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1233"/><stop offset="1" stop-color="#04060f"/></linearGradient>'
                f'<radialGradient id="{eid}l" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff6d8" stop-opacity="0.55"/><stop offset="1" stop-color="#fff6d8" stop-opacity="0"/></radialGradient>')
        corpo = f'<rect width="{W}" height="{H}" fill="url(#{eid}g)"/>' + _estrelas(7, 110, 1500)
        if c == 'ceu_lua':
            corpo += (f'<g id="{eid}m"><circle cx="760" cy="520" r="330" fill="url(#{eid}l)"/>'
                      '<circle cx="760" cy="520" r="130" fill="#f4efe0"/><circle cx="725" cy="490" r="26" fill="#d9d2bd"/>'
                      '<circle cx="800" cy="560" r="34" fill="#d9d2bd"/><circle cx="780" cy="470" r="14" fill="#d9d2bd"/></g>'
                      f'<circle id="{eid}f" cx="760" cy="520" r="130" fill="#fff" opacity="0"/>')
        else:
            corpo += f'<ellipse id="{eid}gl" cx="760" cy="520" rx="420" ry="420" fill="url(#{eid}l)" opacity="0"/>'
    elif c == 'mar':
        defs = f'<linearGradient id="{eid}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#101c44"/><stop offset="1" stop-color="#2b3f78"/></linearGradient>'
        corpo = (f'<rect width="{W}" height="{H}" fill="url(#{eid}g)"/>' + _estrelas(11, 60, 700) +
                 f'<g id="{eid}w">'
                 + _onda(980, 34, 360, '#1d5a8a', 0.9) + _onda(1060, 30, 300, '#17497a', 0.95) + _onda(1150, 26, 260, '#10385f', 1) + '</g>'
                 f'<rect y="1500" width="{W}" height="420" fill="#c9b78a"/>')
    elif c == 'recife':
        defs = f'<linearGradient id="{eid}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#04435f"/><stop offset="1" stop-color="#021722"/></linearGradient>'
        cor = ''
        for x, h, col in [(120, 330, '#ff7a9c'), (300, 240, '#ffb24d'), (520, 380, '#ff7a9c'), (760, 270, '#c47bff'), (940, 340, '#ffb24d')]:
            cor += (f'<path d="M{x} 1900 L{x} {1900 - h} M{x} {1900 - h * 0.6:.0f} L{x - 55} {1900 - h * 0.85:.0f} '
                    f'M{x} {1900 - h * 0.45:.0f} L{x + 60} {1900 - h * 0.75:.0f}" stroke="{col}" stroke-width="22" stroke-linecap="round" fill="none"/>')
        r = random.Random(3)
        bolhas = ''.join(f'<circle id="{eid}p{i}" cx="{r.randint(100, 980)}" cy="{r.randint(1500, 1800)}" r="{r.choice([6, 8, 11])}" fill="#ffd1e0" opacity="0"/>' for i in range(22))
        corpo = f'<rect width="{W}" height="{H}" fill="url(#{eid}g)"/>{cor}{bolhas}'
    elif c in ('terra', 'terra_lua'):
        defs = f'<radialGradient id="{eid}e" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#6fb7ff"/><stop offset="1" stop-color="#0b3a8a"/></radialGradient>'
        cx, cy, rr = (540, 780, 270) if c == 'terra' else (400, 800, 210)
        cont = (f'<ellipse cx="{cx - rr * .25:.0f}" cy="{cy - rr * .2:.0f}" rx="{rr * .3:.0f}" ry="{rr * .22:.0f}" fill="#3f9d5a"/>'
                f'<ellipse cx="{cx + rr * .3:.0f}" cy="{cy + rr * .25:.0f}" rx="{rr * .28:.0f}" ry="{rr * .2:.0f}" fill="#3f9d5a"/>'
                f'<ellipse cx="{cx - rr * .05:.0f}" cy="{cy + rr * .55:.0f}" rx="{rr * .2:.0f}" ry="{rr * .1:.0f}" fill="#3f9d5a"/>')
        eixo = f'<line x1="{cx}" y1="{cy - rr - 90}" x2="{cx}" y2="{cy + rr + 90}" stroke="#ffd45c" stroke-width="8" stroke-dasharray="22 14"/>'
        corpo = (f'<rect width="{W}" height="{H}" fill="#03050c"/>' + _estrelas(5, 140, 1700) +
                 f'<g id="{eid}t"><circle cx="{cx}" cy="{cy}" r="{rr}" fill="url(#{eid}e)"/>{cont}{eixo}</g>')
        if c == 'terra_lua':
            corpo += (f'<g id="{eid}m"><circle cx="820" cy="640" r="62" fill="#cfcabb"/><circle cx="800" cy="625" r="12" fill="#b3ae9e"/>'
                      '<circle cx="838" cy="660" r="15" fill="#b3ae9e"/></g>')
    else:
        raise SystemExit(f'cenario desconhecido: {c}')
    return (f'<div class="cen" id="{eid}" style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;">'
            f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{defs}</defs>{corpo}</svg></div>')


def cenario_anim(eid: str, e: dict, t: float, frases: list) -> list[str]:
    s = f'#{eid}'
    c = e['cena']
    js = []

    def tt(chave, padrao):
        if chave + '_frase' in e:
            return frases[e[chave + '_frase'] - 1] + e.get(chave + '_atraso', 0.1)
        return t + padrao
    if c == 'ceu_lua' and e.get('some_frase'):
        ts = tt('some', 1.5)
        js.append(f"      tl.to('{s}f', {{ opacity: 1, duration: 0.12 }}, {ts:.3f});")
        js.append(f"      tl.to('{s}m', {{ opacity: 0, duration: 0.01 }}, {ts + 0.12:.3f});")
        js.append(f"      tl.to('{s}f', {{ opacity: 0, scale: 3, svgOrigin: '760 520', duration: 0.6, ease: 'power2.out' }}, {ts + 0.12:.3f});")
    if c == 'ceu':
        js.append(f"      tl.fromTo('{s}gl', {{ opacity: 0.9 }}, {{ opacity: 0, duration: 0.8 }}, {t:.3f});")
    if c == 'mar':
        tr = tt('reduz', 1.0)
        js.append(f"      gsap.set('{s}w', {{ svgOrigin: '540 1500' }});")
        js.append(f"      tl.to('{s}w', {{ scaleY: 0.45, svgOrigin: '540 1500', duration: 1.4, ease: 'power2.inOut' }}, {tr:.3f});")
    if c == 'recife':
        for i in range(22):
            js.append(f"      tl.fromTo('{s}p{i}', {{ y: 0, opacity: 0.9 }}, {{ y: -900, opacity: 0, duration: 5.5, ease: 'none' }}, {t + 0.25 * i:.3f});")
    if c == 'terra':
        to = tt('oscila', 0.6)
        js.append(f"      gsap.set('{s}t', {{ rotation: -23.5, svgOrigin: '540 780' }});")
        for k, rot in enumerate([14, -42, 8, -23.5]):
            js.append(f"      tl.to('{s}t', {{ rotation: {rot}, svgOrigin: '540 780', duration: 1.1, ease: 'sine.inOut' }}, {to + 1.15 * k:.3f});")
    if c == 'terra_lua':
        js.append(f"      gsap.set('{s}t', {{ rotation: -23.5, svgOrigin: '400 800' }});")
        js.append(f"      tl.to('{s}m', {{ x: 70, y: -25, duration: 6, ease: 'none' }}, {t:.3f});")
    return js


POSES = {
    'aponta': ([(180, 150), (130, 230), (110, 300)], [(180, 150), (250, 100), (320, 50)]),
    'lanterna': ([(180, 150), (130, 230), (110, 300)], [(180, 150), (260, 190), (330, 200)]),
    'mede': ([(180, 150), (115, 185), (150, 225)], [(180, 150), (245, 185), (210, 225)]),
    'triste': ([(180, 150), (140, 230), (130, 310)], [(180, 150), (220, 230), (230, 310)]),
    'bracos': ([(180, 150), (120, 210), (215, 205)], [(180, 150), (240, 210), (150, 205)]),
    'polegar': ([(180, 150), (130, 230), (110, 300)], [(180, 150), (260, 190), (285, 110)]),
    'acena': ([(180, 150), (130, 230), (110, 300)], [(180, 150), (255, 120), (285, 60)]),
}
BOCAS = {
    'feliz': '<path d="M152 92 Q180 124 208 92" />',
    'triste': '<path d="M155 112 Q180 88 205 112" />',
    'assustado': '<ellipse cx="180" cy="106" rx="11" ry="15" />',
    'serio': '<path d="M158 104 H202" />',
    'curioso': '<path d="M162 102 Q180 114 198 102" />',
    'pensativo': '<path d="M160 106 H190 L200 100" />',
}


def boneco_html(eid: str, e: dict, pos: str) -> str:
    pose = e.get('pose', 'serio')
    L, R = POSES.get(pose, POSES['triste'])
    pl = lambda pts: ' '.join(f'{x},{y}' for x, y in pts)
    extra = ''
    if pose == 'lanterna':
        extra = ('<polygon points="335,196 700,40 700,360" fill="#fff6c0" opacity="0.22" stroke="none"/>'
                 '<rect x="318" y="188" width="34" height="22" rx="4" fill="#ffd45c" stroke="none"/>')
    if pose == 'polegar':
        extra = '<line x1="285" y1="110" x2="285" y2="80" />'
    w = e.get('w', 330)
    olhos = '<circle cx="164" cy="64" r="5.5" fill="#fff" stroke="none"/><circle cx="196" cy="64" r="5.5" fill="#fff" stroke="none"/>'
    return (f'<div class="el boneco" id="{eid}" style="{pos} width:{w}px;"><svg viewBox="-20 -10 440 530" width="{w}" overflow="visible" '
            f'stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none">'
            f'<circle cx="180" cy="70" r="42" fill="rgba(0,0,0,0.35)"/>{olhos}{BOCAS.get(e.get("expr", "serio"), BOCAS["serio"])}'
            f'<line x1="180" y1="112" x2="180" y2="300"/><polyline points="180,300 130,480"/><polyline points="180,300 230,480"/>'
            f'<polyline points="{pl(L)}"/><g id="{eid}ar"><polyline points="{pl(R)}"/>{extra}</g></svg></div>')


def boneco_anim(eid: str, e: dict, t: float) -> list[str]:
    js = [f"      ent('#{eid}', '{e.get('entrada', 'baixo')}', {t:.3f});"]
    if e.get('pose') == 'acena':
        js.append(f"      tl.to('#{eid}ar', {{ rotation: 16, svgOrigin: '180 150', duration: 0.3, yoyo: true, repeat: 7, ease: 'sine.inOut' }}, {t + 0.5:.3f});")
    return js
