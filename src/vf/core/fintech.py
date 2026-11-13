"""Montador do estilo fintech-motion: elementos de cada plano do storyboard.json → HTML + animação (video/fintech.html).

Posições pelo CENTRO (x, y) em px, quadro 1080x1920. Tempo: "frase": N (+"atraso") ou "t" (s após o início do plano).
Tipos: mini · frase (g=true: grande verde) · rotulo · saldo(de, ate, pre) · moedas(n, some) · calendario(dia, mes)
       planilha(arquivo, linhas) · carimbo · celular(marca, msgs) · callout(texto, alvo[x,y])
Entradas: pop · baixo · cima · fade · bate · abre
"""
import html

from vf.core import cenarios, desenhos

BARRAS = {'prefixo': 'R$ '}
LIN, NOME_H, TRK = 140, 46, 60   # gráfico de barras: passo da linha, altura do nome, altura da trilha


def _esc(s):
    return html.escape(str(s))


def _el(eid: str, e: dict, dy: int) -> str:
    t = e['tipo']
    x, y, rot = e.get('x', 540), e.get('y', 960) + dy, e.get('rot', 0)
    pos = f'left:{x}px; top:{y}px;'
    if t == 'mini':
        return f'<div class="el mini" id="{eid}" style="{pos}">{_esc(e["texto"])}</div>'
    if t == 'frase':
        cor = f' color:{e["cor"]};' if e.get('cor') else ''
        tam = f' font-size:{e["s"]}px;' if e.get('s') else ''
        return f'<div class="el frase{" g" if e.get("g") else ""}" id="{eid}" style="{pos}{cor}{tam}">{_esc(e["texto"])}</div>'
    if t == 'logo':
        return f'<img class="el logo" id="{eid}" src="{_esc(e["src"])}" style="{pos} width:{e.get("w", 600)}px;" />'
    if t == 'rotulo':
        return f'<div class="el rotulo" id="{eid}" style="{pos}">{_esc(e["texto"])}</div>'
    if t == 'saldo':
        return (f'<div class="el" id="{eid}" style="{pos} width:760px;"><div class="saldo">0</div>'
                f'<div class="linhaverde" style="margin-top:22px;"></div></div>')
    if t == 'moedas':
        moedas = ''.join('<div class="moeda">$</div>' for _ in range(e.get('n', 10)))
        return f'<div class="el moedas" id="{eid}" style="{pos}">{moedas}</div>'
    if t == 'calendario':
        return (f'<div class="el cal" id="{eid}" data-rot="{rot}" style="{pos}"><div class="t">{_esc(e.get("mes", "NOV"))}</div>'
                f'<div class="d">{_esc(e["dia"])}</div></div>')
    if t == 'planilha':
        linhas = ''.join(f'<div class="tr"><b>{_esc(a)}</b><span>{_esc(b)}</span><i>{_esc(c)}</i></div>' for a, b, c in e['linhas'])
        return (f'<div class="el sheet" id="{eid}" data-rot="{rot}" style="{pos}"><div class="h">{_esc(e["arquivo"])}</div>'
                f'<div class="tr"><b style="font-size:24px;">{_esc(e.get("cab", ["DATA", "GASTO", "VALOR"])[0])}</b>'
                f'<span style="font-size:24px;color:#6b7280;">{_esc(e.get("cab", ["DATA", "GASTO", "VALOR"])[1])}</span>'
                f'<i style="font-size:24px;color:#6b7280;">{_esc(e.get("cab", ["DATA", "GASTO", "VALOR"])[2])}</i></div>{linhas}</div>')
    if t == 'carimbo':
        return f'<div class="el carimbo" id="{eid}" data-rot="{rot or -4}" style="{pos}">{_esc(e["texto"])}</div>'
    if t == 'celular':
        msgs = ''
        for i, m in enumerate(e['msgs']):
            cls = 'bot' if m['de'] == 'bot' else 'eu'
            if m.get('audio'):
                corpo = f'<div class="aud"><div class="p">▶</div><div class="w"></div><small>{_esc(m["audio"])}</small></div>'
            else:
                corpo = m['texto'].replace('{ok}', '<span class="ok">✓</span>')
            msgs += f'<div class="b {cls}" id="{eid}m{i}">{corpo}</div>'
        return (f'<div class="el phone" id="{eid}" style="{pos}"><div class="top"><div class="av">{_esc(e.get("marca", "G")[0])}</div>'
                f'<div><div class="nm">{_esc(e.get("marca", "Assistente"))}</div><div class="on">online</div></div></div>'
                f'<div class="msgs">{msgs}</div></div>')
    # --- oferta de varejo (video/oferta.html) ---
    if t == 't3d':
        tam = f' font-size:{e["s"]}px;' if e.get('s') else ''
        txt = _esc(e['texto'])
        return (f'<div class="el t3d{" branco" if e.get("branco") else ""}" id="{eid}" data-rot="{rot}" style="{pos}{tam}">'
                f'<span class="tb">{txt}</span><span class="tf">{txt}</span></div>')
    if t == 'placa':
        return f'<div class="el placa" id="{eid}" data-rot="{rot}" style="{pos}">{_esc(e["texto"])}</div>'
    if t == 'pilula':
        corpo = f'<img src="{_esc(e["src"])}" />' if e.get('src') else _esc(e.get('texto', 'SUA LOGO AQUI'))
        return f'<div class="el pilula" id="{eid}" style="{pos}">{corpo}</div>'
    if t == 'etiq':
        return f'<div class="el etiq" id="{eid}" data-rot="{rot}" style="{pos}">{_esc(e["texto"])}</div>'
    if t == 'preco':
        inteiro, _, cent = str(e['valor']).partition(',')
        return (f'<div class="el preco" id="{eid}" data-rot="{rot or -5}" style="{pos}"><div class="pre">{_esc(e.get("pre", "POR APENAS"))}</div>'
                f'<div class="v">R$ {_esc(inteiro)}<small>,{_esc(cent or "00")}</small></div>'
                + (f'<div class="u">{_esc(e["unidade"])}</div>' if e.get('unidade') else '') + '</div>')
    if t == 'produto':
        w = e.get('w', 820)
        if e.get('src'):
            corpo = f'<img src="{_esc(e["src"])}" />'
        else:  # placeholder: tábua + peça de carne estilizada
            corpo = ('<svg viewBox="0 0 820 520"><ellipse cx="410" cy="380" rx="400" ry="120" fill="#8a4b1c"/>'
                     '<ellipse cx="410" cy="360" rx="392" ry="112" fill="#c27a3a"/>'
                     '<path d="M150 330 C120 220 260 150 420 160 C600 170 700 230 680 320 C660 400 520 420 400 410 C260 400 170 390 150 330 Z" fill="#c43a33"/>'
                     '<path d="M210 300 C300 250 420 280 520 240 M240 350 C340 320 470 350 600 300 M300 210 C380 230 470 200 560 220" '
                     'stroke="#f3d3c8" stroke-width="14" fill="none" stroke-linecap="round"/>'
                     '<path d="M640 260 C700 240 760 250 770 280 C780 310 730 330 690 310" fill="#f1e6d2" stroke="#d8c8ae" stroke-width="6"/>'
                     '<text x="410" y="480" text-anchor="middle" font-family="Segoe UI" font-weight="700" font-size="30" fill="#ffe9c7">FOTO DO PRODUTO</text></svg>')
        return f'<div class="el produto" id="{eid}" style="{pos} width:{w}px;">{corpo}</div>'
    if t == 'zap':
        ic = ('<div class="ic"><svg viewBox="0 0 48 48" width="56" height="56"><path d="M24 4C13 4 4 12.6 4 23.2c0 4 1.3 7.7 3.5 10.8L5 44l10.4-2.8'
              'c2.6 1.3 5.6 2 8.6 2 11 0 20-8.6 20-19.2S35 4 24 4z" fill="#1fae54"/><path d="M17 15c.6-1 1.6-1 2.2 0l2.3 4.4c.3.7.1 1.4-.4 1.9l-1.4 1.3'
              'c1.3 2.9 3.4 5 6.3 6.3l1.3-1.4c.5-.5 1.3-.7 1.9-.4l4.4 2.3c1 .6 1 1.6 0 2.2-1.6 1.3-3.6 2-5.6 1.5-6.2-1.6-11-6.4-12.6-12.6-.5-2 .2-4 1.6-5.5z" '
              'fill="#fff"/></svg></div>')
        return f'<div class="el zap" id="{eid}" style="{pos}">{ic}<span>{_esc(e["texto"])}</span></div>'
    if t == 'aviso':
        return f'<div class="el aviso" id="{eid}" style="{pos}">{_esc(e["texto"])}</div>'
    if t == 'foto':
        w, h = e.get('w', 1200), e.get('h', 675)
        if e.get('arquivo'):
            corpo = f'<img src="{_esc(e["src"])}" />'
        else:
            corpo = f'<svg viewBox="0 0 1280 720" preserveAspectRatio="xMidYMid slice">{desenhos.desenho_svg(e["desenho"])}</svg>'
        return f'<div class="el foto" id="{eid}" style="{pos} width:{w}px; height:{h}px;"><div class="kb">{corpo}</div></div>'
    if t == 'titulo':
        tam = f' font-size:{e["s"]}px;' if e.get('s') else ''
        return f'<div class="el titulo" id="{eid}" style="{pos}{tam}">{_esc(e["texto"])}</div>'
    if t == 'linha_tempo':
        marcos = e['marcos']
        n = len(marcos)
        itens = ''.join(f'<div class="marco" id="{eid}m{i}" style="left:{(i + 0.5) / n * 1500:.0f}px;top:0;"><b>{_esc(m["data"])}</b>'
                        f'{_esc(m.get("texto", ""))}<i></i></div>' for i, m in enumerate(marcos))
        return (f'<div class="el tlinha" id="{eid}" style="{pos}"><div style="position:absolute;left:0;top:132px;width:1500px;height:8px;'
                f'background:#cfd3d8;border-radius:4px;"></div>{itens}</div>')
    if t == 'creditos':
        linhas = ''.join(f'<div>{_esc(x)}</div>' for x in e['linhas'])
        return f'<div class="el creditos" id="{eid}" style="{pos}"><div class="rolo">{linhas}</div></div>'
    if t == 'imagem':
        return (f'<div class="cen kb" id="{eid}" style="position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;">'
                f'<img src="{_esc(e["src"])}" style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;'
                f'filter:contrast(1.06) saturate(1.05);" />'
                '<div style="position:absolute;inset:0;background:radial-gradient(ellipse at center,transparent 55%,rgba(0,0,0,0.55) 100%);"></div></div>')
    if t == 'cenario':
        return cenarios.cenario_html(eid, e)
    if t == 'boneco':
        return cenarios.boneco_html(eid, e, pos)
    if t == 'bonecos':
        fig = ('<svg viewBox="0 0 70 110" width="70" height="110"><circle class="on" cx="35" cy="22" r="18" fill="rgba(255,255,255,0.18)"/>'
               '<path class="on" d="M8 108 C8 66 62 66 62 108 Z" fill="rgba(255,255,255,0.18)"/></svg>')
        itens = ''.join(f'<div id="{eid}b{i}">{fig}</div>' for i in range(e.get('n', 10)))
        return f'<div class="el bonecos" id="{eid}" style="{pos}">{itens}</div>'
    if t == 'grafico':
        w, linhas = e.get('w', 900), e['linhas']
        h = len(linhas) * LIN - (LIN - NOME_H - TRK)
        corpo = ''
        for i, r in enumerate(linhas):
            partes = r.get('partes') or [{'v': r['valor'], 'cor': r.get('cor', '#5aa9e6')}]
            segs = ''.join(f'<div class="bar" id="{eid}l{i}s{j}" style="background:{p_["cor"]};"></div>' for j, p_ in enumerate(partes))
            corpo += (f'<div class="lin" style="top:{i * LIN}px;"><div class="nm" id="{eid}l{i}n">{_esc(r["nome"])}</div>'
                      f'<div class="trk">{segs}<span class="vl" id="{eid}l{i}v">0</span></div></div>')
        d = e.get('destaque')
        if d:
            L = d['de'] / e['eixo'] * w
            W = (d['ate'] - d['de']) / e['eixo'] * w
            T = d['de_linha'] * LIN + NOME_H - 8
            H = (d['ate_linha'] - d['de_linha']) * LIN + TRK + 16
            corpo += f'<div class="destaque" id="{eid}d" style="left:{L:.0f}px;top:{T:.0f}px;width:{W:.0f}px;height:{H:.0f}px;"></div>'
        return f'<div class="el gr" id="{eid}" style="{pos} width:{w}px; height:{h}px;">{corpo}</div>'
    if t == 'tela':
        w = e.get('w', 600)
        ar = e.get('ar', 1.6)
        h = round(w / ar)
        aneis = ''.join(
            f'<div class="anel" id="{eid}r{i}" style="left:{a["x"]*100}%;top:{a["y"]*100}%;width:{a["w"]*100}%;height:{a["h"]*100}%;"></div>'
            for i, a in enumerate(e.get('aneis', [])))
        corpo = (f'<div class="vp" style="width:{w}px;height:{h}px;"><div class="zoom" style="width:{w}px;height:{h}px;">'
                 f'<img src="{_esc(e["src"])}" style="width:{w}px;height:{h}px;" />{aneis}</div></div>')
        if e.get('moldura', 'janela') == 'celular':
            return f'<div class="el tela cel" id="{eid}" style="{pos}">{corpo}</div>'
        return (f'<div class="el tela jan" id="{eid}" style="{pos}"><div class="barra"><i></i><i></i><i></i></div>{corpo}</div>')
    if t == 'callout':
        ax, ay = e['alvo']
        ay += dy
        return (f'<div class="fixo" id="{eid}"><svg width="1080" height="1920" style="position:absolute;left:0;top:0;">'
                f'<line x1="{x}" y1="{y}" x2="{ax}" y2="{ay}" stroke="#cfd3d8" stroke-width="3"/>'
                f'<circle cx="{ax}" cy="{ay}" r="9" fill="#ff5a5a"/></svg>'
                f'<div class="el callout" style="{pos}">{_esc(e["texto"])}</div></div>')
    raise SystemExit(f'fintech: tipo desconhecido {t}')


def _anim(eid: str, e: dict, t: float, frases: list) -> list[str]:
    sel = f'#{eid}'
    tp = e['tipo']
    js = []
    if tp == 'callout':
        js.append(f"      linha('{sel}', {t:.3f});")
        return js
    if tp in ('preco', 't3d', 'zap') and e.get('pulsa', tp == 'preco'):
        js = [f"      ent('{sel}', '{e.get('entrada', 'bate')}', {t:.3f});"]
        fim = e['_t0'] + e['_dur']
        n = max(1, int((fim - t - 0.8) / 0.9))
        js.append(f"      tl.to('{sel}', {{ scale: 1.07, duration: 0.45, yoyo: true, repeat: {n * 2 - 1}, ease: 'sine.inOut' }}, {t + 0.6:.3f});")
        return js
    if tp == 'foto':
        t0, dur = e['_t0'], e['_dur']
        js = [f"      ent('{sel}', '{e.get('entrada', 'fade')}', {t:.3f});"]
        f = {'zoom_in': (1.0, 1.07, 0, 0, 0, 0), 'zoom_out': (1.07, 1.0, 0, 0, 0, 0),
             'pan_esq': (1.08, 1.08, 30, -30, 0, 0), 'pan_dir': (1.08, 1.08, -30, 30, 0, 0),
             'pan_cima': (1.08, 1.08, 0, 0, 24, -24)}[e.get('mov', 'zoom_in')]
        js.append(f"      tl.fromTo('{sel} .kb', {{ scale: {f[0]}, x: {f[2]}, y: {f[4]} }}, {{ scale: {f[1]}, x: {f[3]}, y: {f[5]}, duration: {dur:.3f}, ease: 'none' }}, {t0:.3f});")
        return js
    if tp == 'titulo':
        return [f"      tl.fromTo('{sel}', {{ clipPath: 'inset(0 100% 0 0)' }}, {{ clipPath: 'inset(0 0% 0 0)', duration: {e.get('dur', 1.6)}, ease: 'none' }}, {t:.3f});"]
    if tp == 'linha_tempo':
        js = [f"      ent('{sel}', 'fade', {t:.3f});"]
        for i, m in enumerate(e['marcos']):
            tm = (frases[m['frase'] - 1] + m.get('atraso', 0.1)) if 'frase' in m else t + 0.6 + 1.2 * i
            js.append(f"      tl.from('{sel}m{i}', {{ opacity: 0, y: 30, duration: 0.4 }}, {tm:.3f});")
            js.append(f"      tl.to('{sel}m{i} i', {{ backgroundColor: 'var(--verde)', scale: 1.5, duration: 0.3 }}, {tm:.3f});")
        return js
    if tp == 'creditos':
        t0, dur = e['_t0'], e['_dur']
        return [f"      tl.fromTo('{sel} .rolo', {{ y: 260 }}, {{ y: -260, duration: {dur:.3f}, ease: 'none' }}, {t0:.3f});"]
    if tp == 'imagem':
        t0, dur = e['_t0'], e['_dur']
        f = {'zoom_in': (1.0, 1.12, 0, 0, 0, 0), 'zoom_out': (1.12, 1.0, 0, 0, 0, 0),
             'pan_esq': (1.12, 1.12, 50, -50, 0, 0), 'pan_dir': (1.12, 1.12, -50, 50, 0, 0),
             'pan_cima': (1.12, 1.12, 0, 0, 60, -60), 'pan_baixo': (1.12, 1.12, 0, 0, -60, 60)}[e.get('mov', 'zoom_in')]
        js = [f"      tl.fromTo('#{eid} img', {{ scale: {f[0]}, x: {f[2]}, y: {f[4]} }}, {{ scale: {f[1]}, x: {f[3]}, y: {f[5]}, duration: {dur:.3f}, ease: 'none' }}, {t0:.3f});"]
        if e.get('tremor_frase'):
            tr = frases[e['tremor_frase'] - 1] + e.get('tremor_atraso', 0.1)
            js.append(f"      tl.to('#{eid}', {{ x: 8, duration: 0.05, yoyo: true, repeat: 7, ease: 'none' }}, {tr:.3f});")
        return js
    if tp == 'cenario':
        return cenarios.cenario_anim(eid, e, t, frases)
    if tp == 'boneco':
        return cenarios.boneco_anim(eid, e, t)
    if tp == 'bonecos':
        js.append(f"      ent('{sel}', '{e.get('entrada', 'pop')}', {t:.3f});")
        ta = (frases[e['acende_frase'] - 1] + e.get('acende_atraso', 0.1)) if 'acende_frase' in e else t + 0.8
        for i in range(e.get('acesos', 4)):
            js.append(f"      tl.to('{sel}b{i} .on', {{ fill: '{e.get('cor', '#f5b301')}', duration: 0.25 }}, {ta + 0.22 * i:.3f});")
        return js
    if tp == 'grafico':
        eixo, dec, suf = e['eixo'], e.get('dec', 1), e.get('suf', '')
        for i, r in enumerate(e['linhas']):
            tr = (frases[r['frase'] - 1] + r.get('atraso', 0.1)) if 'frase' in r else t + 0.4 * i
            partes = r.get('partes') or [{'v': r['valor']}]
            js.append(f"      tl.to('{sel}l{i}n', {{ opacity: 1, duration: 0.3 }}, {tr:.3f});")
            js.append(f"      tl.to('{sel}l{i}v', {{ opacity: 1, duration: 0.2 }}, {tr:.3f});")
            for j, p_ in enumerate(partes):
                js.append(f"      barra('{sel}l{i}s{j}', {p_['v'] / eixo * 100:.3f}, {tr + 0.3 * j:.3f});")
            tot = sum(p_['v'] for p_ in partes)
            js.append(f"      contar('{sel}l{i}v', 0, {tot}, {dec}, '', {tr:.3f}, {0.9 + 0.3 * (len(partes) - 1):.2f}, '{suf}');")
        d = e.get('destaque')
        if d:
            td = (frases[d['frase'] - 1] + d.get('atraso', 0.1)) if 'frase' in d else t + 2
            js.append(f"      tl.from('{sel}d', {{ scale: 1.5, opacity: 0, duration: 0.45, ease: 'back.out(2)' }}, {td:.3f});")
        return js
    if tp == 'tela':
        js.append(f"      ent('{sel}', '{e.get('entrada', 'baixo')}', {t:.3f});")
        def _tt(d, base):
            return (frases[d['frase'] - 1] + d.get('atraso', 0.1)) if 'frase' in d else base + d.get('t', 0.8)
        f = e.get('foco')
        if f:
            js.append(f"      tl.to('{sel} .zoom', {{ scale: {f['z']}, transformOrigin: '{f['x']*100}% {f['y']*100}%', duration: 1.0, ease: 'power2.inOut' }}, {_tt(f, t):.3f});")
        for i, a in enumerate(e.get('aneis', [])):
            js.append(f"      tl.from('{sel}r{i}', {{ scale: 1.6, opacity: 0, duration: 0.4, ease: 'back.out(2)' }}, {_tt(a, t):.3f});")
        return js
    if tp == 'celular':
        js.append(f"      ent('{sel}', '{e.get('entrada', 'baixo')}', {t:.3f});")
        for i, m in enumerate(e['msgs']):
            tm = (frases[m['frase'] - 1] + m.get('atraso', 0.1)) if 'frase' in m else t + 0.6 + 1.3 * i
            js.append(f"      mostra('{sel}m{i}', {tm:.3f});")
        return js
    js.append(f"      ent('{sel}', '{e.get('entrada', 'pop')}', {t:.3f});")
    if tp == 'saldo':
        tc = (frases[e['contar_frase'] - 1] + e.get('contar_atraso', 0.1)) if 'contar_frase' in e else t + e.get('espera', 0.6)
        js.append(f"      contar('{sel} .saldo', {e['de']}, {e.get('ate', e['de'])}, {e.get('dec', 0)}, '{e.get('pre', 'R$ ')}', {tc:.3f}, {e.get('dur', 1.6)}, '{e.get('suf', '')}');")
    if tp == 'moedas' and e.get('some'):
        ts = (frases[e['some_frase'] - 1] if 'some_frase' in e else t + 1.0) + e.get('some_atraso', 0.1)
        js.append(f"      some('{sel}', {ts:.3f}, {e.get('passo', 0.18)});")
    return js


def montar(planos: list, frases: list, dy: int = 0) -> dict:
    blocos, anims = [], []
    for p in planos:
        dur = max(p['t1'] - p['t0'], 0.1)
        filhos = []
        for k, e in enumerate(p.get('elementos', [])):
            eid = f'p{p["id"]}e{k}'
            e['_t0'], e['_dur'] = p['t0'], dur
            filhos.append(_el(eid, e, dy))
            t = (frases[e['frase'] - 1] + e.get('atraso', 0.1)) if 'frase' in e else p['t0'] + e.get('t', 0.05 + 0.3 * k)
            anims.extend(_anim(eid, e, t, frases))
        blocos.append(f'      <div id="p{p["id"]}" class="clip plano" data-start="{p["t0"]:.3f}" data-duration="{dur:.3f}" '
                      f'data-track-index="1">{"".join(filhos)}</div>')
    return {'__PLANOS__': '\n'.join(blocos), '__ANIM_PLANOS__': '\n'.join(anims)}
