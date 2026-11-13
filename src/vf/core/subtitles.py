"""Legenda .ass: agrupamento de palavras em falas e escrita do arquivo."""
import re
from pathlib import Path

from .media import PAD, ts

ESTILOS = {
    'vertical': """Style: F,Arial Black,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,7,3,2,70,70,560,1
Style: H1,Arial Black,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,3,14,0,8,60,60,150,1
Style: H2,Arial,30,&H00E6E6E6,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,3,10,0,8,60,60,240,1""",
    'desfocado': """Style: F,Arial Black,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,6,2,8,70,70,1300,1
Style: H1,Arial Black,58,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,4,0,8,60,60,250,1
Style: H2,Arial,40,&H00D0D0D0,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,3,0,8,60,60,330,1""",
}


def agrupar(palavras, t0, t1, max_palavras=4, max_dur=1.8):
    """Agrupa palavras em falas curtas (listas de dicts); quebra em pontuação, pausa ou tamanho."""
    out, cur = [], []
    for w in palavras:
        if w['e'] < t0 or w['s'] > t1:
            continue
        if cur and (w['s'] - cur[-1]['e'] > 0.5 or len(cur) >= max_palavras or w['e'] - cur[0]['s'] > max_dur):
            out.append(cur); cur = []
        cur.append(w)
        if re.search(r'[.?!;:]$', w['w']):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def blocos(palavras, t0, t1, max_palavras=4, max_dur=1.8):
    """(início, fim, texto) de cada fala. Mesmo agrupamento de `agrupar`."""
    return [(c[0]['s'], c[-1]['e'], ' '.join(x['w'] for x in c))
            for c in agrupar(palavras, t0, t1, max_palavras, max_dur)]


def legenda(palavras, pasta: Path, ini, fim, layout, titulo, subtitulo, refazer) -> Path:
    ass = pasta / 'legenda.ass'
    if ass.exists() and not refazer:
        return ass
    # tempos do Whisper são relativos ao trecho baixado (que começa em ini - PAD)
    base = min(PAD, ini)
    t0, t1 = base, base + (fim - ini)
    dur = fim - ini
    ev = []
    if titulo:
        ev.append(f'Dialogue: 0,{ts(0)},{ts(dur)},H1,,0,0,0,,{titulo}')
    if subtitulo:
        ev.append(f'Dialogue: 0,{ts(0)},{ts(dur)},H2,,0,0,0,,{subtitulo}')
    bl = blocos(palavras, t0, t1)
    for i, (a, b, txt) in enumerate(bl):
        nxt = bl[i + 1][0] if i + 1 < len(bl) else t1
        b = min(max(b, a + 0.6), nxt) if nxt > a else b  # mínimo legível sem atropelar a próxima
        ev.append(f'Dialogue: 1,{ts(a - t0)},{ts(b - t0)},F,,0,0,0,,{{\\fad(60,40)}}{txt}')
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{ESTILOS[layout]}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass.write_text(head + '\n'.join(ev) + '\n', encoding='utf-8-sig')
    print(f'  legenda: {len(bl)} falas -> {ass}')
    return ass
