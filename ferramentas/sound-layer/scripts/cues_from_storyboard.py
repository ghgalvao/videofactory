"""Cue sheet for sound-layer from a pixel-avatar storyboard + words.json.
Usage (from ferramentas/sound-layer): python cues_from_sb.py <job_dir_relative> <out_json>"""
import json, re, sys
from pathlib import Path

job = Path(sys.argv[1]); out = Path(sys.argv[2])
sb = json.load(open(job / '1-entrada/storyboard.json', encoding='utf-8'))
words = json.load(open(job / '_interno/words.json', encoding='utf-8'))
import soundfile as sf
dur = sf.info(str(job / '_interno/narration.wav')).duration

starts = [0]
for i, w in enumerate(words):
    if re.search(r'[.?!]["”)]*$', w['word'].strip()) and i + 1 < len(words):
        starts.append(i + 1)
F = [words[i]['start'] for i in starts]
planos = sb['planos']
t0s = [0.0] + [F[min(p['frases']) - 1] for p in planos[1:]]

cues = []
def add(t, sound, weight='support', visual=None, pan=0.0):
    c = {'id': f'c{len(cues)}', 't': round(t, 3), 'sound': sound, 'weight': weight, 'align': 'peak', 'pan': pan}
    if visual: c['visual'] = visual
    cues.append(c)

tag_re = re.compile(r'<(\w+)([^>]*)>')
attr = lambda a, k: (re.search(k + r'="([^"]*)"', a) or [None, None])[1]

for i, p in enumerate(planos):
    t0 = t0s[i]
    if i > 0:
        add(t0 - 0.3, 'whoosh', visual='cut', pan=-0.2 if i % 2 else 0.2)
    k = 0
    for m in tag_re.finditer(p.get('card', '')):
        a = m.group(2)
        cls = attr(a, 'class') or ''
        def when(fk, dk, dflt):
            off = float(attr(a, dk)) if attr(a, dk) is not None else dflt
            f = attr(a, fk)
            return (F[int(f) - 1] + off) if f else t0 + off
        if re.search(r'\bin\b', cls):
            fx = attr(a, 'data-fx')
            d = when('data-f', 'data-d', 0.1 if attr(a, 'data-f') else 0.45 + k * 0.32); k += 1
            if fx == 'stamp':
                add(d + 0.22, 'hit', weight='hero' if 'ISCA' in p.get('card', '')[m.end():m.end() + 20] else 'support', visual='land')
            elif fx == 'pop':
                add(d + 0.12, 'pop')
            elif fx in ('left', 'right'):
                add(d + 0.15, 'swish', pan=-0.3 if fx == 'left' else 0.3)
        if attr(a, 'data-onf') or attr(a, 'data-on'):
            add(when('data-onf', 'data-on', 0), 'glitch')
        if 'count' in cls.split():
            add(when('data-f', 'data-d', 0.3), 'ui')

# drop cues that crowd each other (keep the first; heroes always win)
cues.sort(key=lambda c: c['t'])
kept = []
for c in cues:
    if kept and c['t'] - kept[-1]['t'] < 0.18:
        if c['weight'] == 'hero':
            kept[-1] = c
        continue
    kept.append(c)
for n, c in enumerate(kept):
    c['id'] = f'c{n:02d}'

sheet = {'fps': 30, 'duration_s': round(dur, 3), 'energy': 'punchy', 'kit': 'audio/kit',
         'voice': [{'file': str(job / '_interno/narration.wav').replace('\\', '/'), 'start_s': 0}],
         'cues': kept}
json.dump(sheet, open(out, 'w', encoding='utf-8'), indent=1)
print(len(kept), 'cues ->', out)
