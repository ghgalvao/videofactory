"""Montador do estilo quadro branco: elementos do storyboard.json → traços SVG que se desenham + texto escrito à mão.

Elemento (posições em px, quadro 1080x1920; tudo desenhado em sequência, um traço por vez):
  {"tipo": "linha|seta|onda|circulo|arco|sol|palito|triangulo|caminho|bolinhas|sublinhado|texto",
   "cor": "#1b1f2a", "w": 7, "vel": 700,              # largura do traço (px) e velocidade (px/s)
   "frase": 2, "atraso": 0.2,                         # começa na frase N (+atraso) ou "t" (s após o início do plano)
   ...campos do tipo}
Campos por tipo:
  linha/seta: x1,y1,x2,y2          onda: x0,x1,y,amp,comp   circulo: x,y,r     arco: x,y,r,a0,a1 (graus, 0=direita, horário)
  sol: x,y,r                       palito: x,y,esc (esc 1 = 300 px de altura)   triangulo: x,y,l
  caminho: pts [[x,y],...]         bolinhas: pts [[x,y],...], r            sublinhado: x0,x1,y
  texto: texto, x, y, s (px), cor, "vel" = letras/s (padrão 22); aceita \\n.
Opções comuns: "preencher": cor de preenchimento (aparece ao fim do traço).
"""
import html
import math

TINTA = '#1b1f2a'
PASSO = 14  # distância entre pontos do traço (px): é o que dá o tremor de mão


def _tremor(pts, forca=1.7):
    """Reamostra a cada PASSO px e aplica um tremor determinístico (sem Math.random)."""
    if len(pts) < 2:
        return pts
    out = [pts[0]]
    acum = 0.0
    k = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d = math.hypot(x1 - x0, y1 - y0)
        n = max(int(d // PASSO), 1)
        for i in range(1, n + 1):
            f = i / n
            k += 1
            out.append((x0 + (x1 - x0) * f + math.sin(k * 1.9) * forca, y0 + (y1 - y0) * f + math.cos(k * 1.3) * forca))
        acum += d
    out[-1] = pts[-1]
    return out


def _comprimento(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def _arco(x, y, r, a0, a1, n=64):
    return [(x + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), y + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def _tracos(e):
    """Devolve a lista de traços (pontos) do elemento, na ordem em que são desenhados."""
    t = e['tipo']
    if t == 'linha':
        return [[(e['x1'], e['y1']), (e['x2'], e['y2'])]]
    if t == 'seta':
        x1, y1, x2, y2 = e['x1'], e['y1'], e['x2'], e['y2']
        a = math.atan2(y2 - y1, x2 - x1)
        c = e.get('ponta', 34)
        cab = [(x2 - c * math.cos(a - 0.5), y2 - c * math.sin(a - 0.5)), (x2, y2),
               (x2 - c * math.cos(a + 0.5), y2 - c * math.sin(a + 0.5))]
        return [[(x1, y1), (x2, y2)], cab]
    if t == 'onda':
        x0, x1, y, amp, comp = e['x0'], e['x1'], e['y'], e['amp'], e['comp']
        n = int((x1 - x0) / 4)
        return [[(x0 + (x1 - x0) * i / n, y + amp * math.sin(2 * math.pi * (x1 - x0) * i / n / comp)) for i in range(n + 1)]]
    if t == 'circulo':
        return [_arco(e['x'], e['y'], e['r'], -90, 270)]
    if t == 'arco':
        return [_arco(e['x'], e['y'], e['r'], e['a0'], e['a1'])]
    if t == 'sol':
        x, y, r = e['x'], e['y'], e['r']
        raios = [[(x + r * 1.3 * math.cos(math.radians(a)), y + r * 1.3 * math.sin(math.radians(a))),
                  (x + r * 1.75 * math.cos(math.radians(a)), y + r * 1.75 * math.sin(math.radians(a)))] for a in range(0, 360, 45)]
        return [_arco(x, y, r, -90, 270)] + raios
    if t == 'retangulo':  # canto superior esquerdo + tamanho
        x, y, w, h = e['x'], e['y'], e['w_r'], e['h']
        return [[(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]]
    if t == 'moldura':  # cantoneiras de zoom em volta de um retângulo
        x, y, w, h, c = e['x'], e['y'], e['w_r'], e['h'], e.get('c', 46)
        return [[(x, y + c), (x, y), (x + c, y)], [(x + w - c, y), (x + w, y), (x + w, y + c)],
                [(x + w, y + h - c), (x + w, y + h), (x + w - c, y + h)], [(x + c, y + h), (x, y + h), (x, y + h - c)]]
    if t == 'cota':  # linha de cota com marcas nas pontas (sem número)
        x1, y1, x2, y2 = e['x1'], e['y1'], e['x2'], e['y2']
        a = math.atan2(y2 - y1, x2 - x1) + math.pi / 2
        dx, dy = 20 * math.cos(a), 20 * math.sin(a)
        return [[(x1, y1), (x2, y2)], [(x1 - dx, y1 - dy), (x1 + dx, y1 + dy)], [(x2 - dx, y2 - dy), (x2 + dx, y2 + dy)]]
    if t == 'serpentina':  # zigue-zague: `passes` idas e voltas entre x e x+w, descendo de y a y+h
        x, y, w, h, n = e['x'], e['y'], e['w_r'], e['h'], e.get('passes', 5)
        pts = []
        for i in range(n):
            ya = y + h * i / (n - 1)
            pts += [(x, ya), (x + w, ya)] if i % 2 == 0 else [(x + w, ya), (x, ya)]
        return [pts]
    if t == 'ventilador':
        cx, cy, r = e['x'], e['y'], e['r']
        pas = [_arco(cx, cy, r, -90, 270)]
        for k in range(4):
            base = k * 90
            pas.append([(cx + r * 0.88 * u * math.cos(math.radians(base + 70 * u)), cy + r * 0.88 * u * math.sin(math.radians(base + 70 * u)))
                        for u in [i / 12 for i in range(13)]])
        return pas
    if t == 'palito':
        x, y, s = e['x'], e['y'], e.get('esc', 1.0)
        cabeca = _arco(x, y - 110 * s, 42 * s, 90, 450)
        corpo = [(x, y - 68 * s), (x, y + 70 * s)]
        bracos = [(x - 70 * s, y - 40 * s), (x, y - 20 * s), (x + 70 * s, y - 40 * s)] if not e.get('olha_cima') else \
                 [(x - 60 * s, y - 120 * s), (x, y - 20 * s), (x + 60 * s, y - 120 * s)]
        pernas = [(x - 55 * s, y + 160 * s), (x, y + 70 * s), (x + 55 * s, y + 160 * s)]
        return [cabeca, corpo, bracos, pernas]
    if t == 'triangulo':
        x, y, l = e['x'], e['y'], e['l']
        h = l * math.sqrt(3) / 2
        return [[(x, y - 2 * h / 3), (x + l / 2, y + h / 3), (x - l / 2, y + h / 3), (x, y - 2 * h / 3)]]
    if t == 'caminho':
        return [[tuple(p) for p in e['pts']]]
    if t == 'bolinhas':
        return [_arco(p[0], p[1], e.get('r', 22), -90, 270, 28) for p in e['pts']]
    if t == 'sublinhado':
        x0, x1, y = e['x0'], e['x1'], e['y']
        n = int((x1 - x0) / 6)
        return [[(x0 + (x1 - x0) * i / n, y + 7 * math.sin(i * 0.9)) for i in range(n + 1)]]
    raise SystemExit(f'quadro: tipo desconhecido: {t}')


def _texto_html(eid, e):
    letras, k = [], 0
    for ch in e['texto']:
        if ch == '\n':
            letras.append('<br>')
        else:
            letras.append(f'<span id="{eid}c{k}">{html.escape(ch)}</span>')
            k += 1
    fonte = f' font-family:{e["fonte"]};' if e.get('fonte') else ''
    if e.get('ancora') == 'esq':  # x = borda esquerda
        fonte += ' transform:translate(0,-50%); text-align:left;'
    return (f'<div class="txt{" mono" if e.get("mono") else ""}" id="{eid}" style="left:{e["x"]}px; top:{e["y"]}px; font-size:{e.get("s", 110)}px; '
            f'color:{e.get("cor", TINTA)};{fonte}">{"".join(letras)}</div>'), k


def _fluxo(eid, e, t0, t_fim, dy, svg, anims):
    """Partículas (círculos) percorrendo `pts` em loop até t_fim. cor muda para cor2 depois do trecho `virar` (0..1)."""
    pts = [(x, y + dy) for x, y in e['pts']]
    segs = [(a, b, math.hypot(b[0] - a[0], b[1] - a[1])) for a, b in zip(pts, pts[1:])]
    total = sum(sg[2] for sg in segs)
    vel, n, r = e.get('vel', 260), e.get('n', 5), e.get('r', 11)
    per = total / vel
    cor, cor2, virar = e.get('cor', '#4fe3ff'), e.get('cor2', e.get('cor', '#4fe3ff')), e.get('virar', 1.0)
    for k in range(n):
        pid = f'{eid}f{k}'
        svg.append(f'<circle id="{pid}" cx="{pts[0][0]}" cy="{pts[0][1]}" r="{r}" fill="{cor}" opacity="0"/>')
        t = t0 + k * per / n
        while t < t_fim:  # última volta pode ficar pela metade (o plano some antes)
            anims.append(f"      tl.set('#{pid}', {{opacity: 1, attr: {{cx: {pts[0][0]:.1f}, cy: {pts[0][1]:.1f}, fill: '{cor}'}}}}, {t:.3f});")
            acum = 0.0
            for a, b, d in segs:
                dd = d / vel
                if acum / total >= virar - 1e-9 and cor2 != cor:
                    anims.append(f"      tl.set('#{pid}', {{attr: {{fill: '{cor2}'}}}}, {t + acum / vel:.3f});")
                anims.append(f"      tl.to('#{pid}', {{attr: {{cx: {b[0]:.1f}, cy: {b[1]:.1f}}}, duration: {dd:.3f}, ease: 'none'}}, {t + acum / vel:.3f});")
                acum += d
            anims.append(f"      tl.set('#{pid}', {{opacity: 0}}, {t + per:.3f});")
            t += per


def montar(planos: list, frases: list, dy: int = 0, padrao: str = TINTA) -> dict:
    """Retorna __PLANOS__ (HTML) e __ANIM_PLANOS__ (JS) para video/quadro.html. Avisa se um desenho passa do fim do plano."""
    blocos, anims = [], []
    for p in planos:
        n = p['id']
        dur = max(p['t1'] - p['t0'], 0.1)
        svg, textos, fotos = [], [], []  # fotos ficam por baixo dos traços
        cursor = p['t0'] + 0.05
        for k, e in enumerate(p.get('elementos', [])):
            e = dict(e)
            e.setdefault('cor', padrao)
            eid = f'p{n}e{k}'
            ini = (frases[e['frase'] - 1] + e.get('atraso', 0.1)) if 'frase' in e else p['t0'] + e.get('t', 0.05)
            t = max(ini, cursor)
            if e['tipo'] == 'texto':
                tag, qtd = _texto_html(eid, e)
                textos.append(tag)
                vel = e.get('vel', 22)
                anims.append(f"      tl.set('#{eid}', {{opacity: 1}}, {t:.3f});")
                anims.append(f"      escreve('#{eid}', {qtd}, {t:.3f}, {1 / vel:.4f});")
                cursor = t + qtd / vel + 0.04
                continue
            if e['tipo'] == 'carimbo':
                linhas = '<br>'.join(html.escape(x) for x in e['texto'].split(chr(10)))
                cor = e.get('cor', TINTA)
                textos.append(f'<div class="stamp" id="{eid}" style="left:{e["x"]}px; top:{e["y"]}px;">'
                              f'<div class="stampi" style="color:{cor}; border-color:{cor}; font-size:{e.get("s", 110)}px; '
                              f'transform:rotate({e.get("rot", -4)}deg);">{linhas}</div></div>')
                anims.append(f"      carimbo('#{eid} .stampi', {max(ini, cursor):.3f});")
                cursor = max(ini, cursor) + 0.5
                continue
            if e['tipo'] == 'imagem':  # logo/foto (src preenchido por _preparar_imagens); "cartao": fundo claro
                cls = ' cartao' if e.get('cartao') else (' foto' if e.get('foto') else '')
                fotos.append(f'<div class="img{cls}" id="{eid}" '
                              f'style="left:{e["x"]}px; top:{e["y"] + dy}px; width:{e.get("larg", 800)}px;"><img src="{e["src"]}" /></div>')
                anims.append(f"      tl.fromTo('#{eid}', {{opacity: 0, scale: 0.86}}, {{opacity: 1, scale: 1, duration: 0.5, ease: 'back.out(1.6)'}}, {t:.3f});")
                if e.get('zoom'):  # Ken Burns leve dentro da moldura até o fim do plano
                    anims.append(f"      tl.fromTo('#{eid} img', {{scale: 1}}, {{scale: {e['zoom']}, duration: {max(p['t1'] - t, 0.5):.3f}, ease: 'none'}}, {t:.3f});")
                cursor = t + 0.5
                continue
            if e['tipo'] == 'fluxo':  # partículas andando por um caminho, sem bloquear o desenho
                _fluxo(eid, e, ini, p['t1'] - 0.5, dy, svg, anims)
                continue
            cor, larg, vel = e.get('cor', TINTA), e.get('w', 7), e.get('vel', 700)
            cursor_el = t
            for j, pts in enumerate(_tracos(e)):
                pts = _tremor(pts)
                d = 'M' + ' L'.join(f'{x:.1f} {y + dy:.1f}' for x, y in pts)
                dd = max(_comprimento(pts) / vel, 0.12)
                tid = f'{eid}t{j}'
                svg.append(f'<path id="{tid}" d="{d}" pathLength="1" fill="none" stroke="{cor}" stroke-width="{larg}" '
                           f'stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"/>')
                anims.append(f"      traco('#{tid}', {cursor_el:.3f}, {dd:.3f});")
                if e.get('preencher') and j == 0:
                    svg[-1] = svg[-1].replace('fill="none"', f'fill="{e["preencher"]}" fill-opacity="0"')
                    anims.append(f"      tl.to('#{tid}', {{attr: {{'fill-opacity': 1}}, duration: 0.3}}, {cursor_el + dd:.3f});")
                cursor_el += dd + 0.01
            cursor = cursor_el + 0.03
        if cursor > p['t1'] - 0.3:
            print(f'  AVISO plano {n}: desenho termina em {cursor:.1f}s, plano acaba em {p["t1"]:.1f}s (apertar vel/atraso)')
        blocos.append(
            f'      <div id="p{n}" class="clip plano" data-start="{p["t0"]:.3f}" data-duration="{dur:.3f}" data-track-index="1">'
            f'{"".join(fotos)}<svg class="lousa" viewBox="0 0 1080 1920" width="1080" height="1920">{"".join(svg)}</svg>{"".join(textos)}'
            + (f'<div class="folha">{html.escape(p["folha"])}</div>' if p.get('folha') else '') +
            f'<div class="limpa" id="p{n}l"></div><div class="apagador" id="p{n}a"></div></div>')
        if p is not planos[-1]:  # último plano fica na tela até o fim
            anims.append(f"      apaga('#p{n}l', '#p{n}a', {max(p['t1'] - 0.45, p['t0']):.3f});")
    return {'__PLANOS__': '\n'.join(blocos), '__ANIM_PLANOS__': '\n'.join(anims)}
