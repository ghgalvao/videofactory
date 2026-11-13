"""Catalog of a client's images and videos: assets/index.json, so any piece can pick the right file.

  vf assets scan <client>                       indexes assets/ (keeps tags already written; flags duplicates and blank files)
  vf assets sheet <client>                      numbered contact sheets in exports/ (look at them to tag)
  vf assets set <client> <id...> [--subject ..] [--tags a,b] [--use cover,background,detail] [--people yes|no]
                                [--rights ok|confirm] [--note ..]
  vf assets find <client> [--tag t] [--use u] [--orient vertical|horizontal|square] [--min media|alta] [--subject text]

Each item: id, path, kind, size, orientation, quality, perceptual hash, duplicate of, blank flag, plus the fields a person
or the agent fills after looking at the sheet: subject, tags, use, people, rights, note.
Rights default to "confirm": material the client sent is theirs, but third-party faces, logos and plants need written OK.
"""
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from .client import home
from .paths import SAIDA_PADRAO

SCAN_DIRS = ('images', 'video', 'print', 'brand')
IMG_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
VID_EXT = {'.mp4', '.mov', '.webm', '.m4v'}
USES = ('cover', 'background', 'detail', 'proof', 'team', 'logo', 'discard')
QUALITY_RANK = {'baixa': 0, 'media': 1, 'alta': 2}
CELL = (240, 190)
PER_SHEET = 24
COLS = 6


def _imread(p: Path):
    return cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)


def _dhash(img) -> int:
    g = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (9, 8), interpolation=cv2.INTER_AREA)
    bits = (g[:, 1:] > g[:, :-1]).flatten()
    return int(''.join('1' if b else '0' for b in bits), 2)


def _video_info(p: Path) -> dict:
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                        'stream=width,height:format=duration', '-of', 'json', str(p)], capture_output=True, text=True)
    d = json.loads(r.stdout or '{}')
    s = (d.get('streams') or [{}])[0]
    return {'w': s.get('width'), 'h': s.get('height'), 'dur': round(float(d.get('format', {}).get('duration', 0)), 1)}


def _video_frame(p: Path, dur: float):
    tmp = p.with_suffix('.thumb.png')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(max(dur / 2, 0)), '-i', str(p), '-frames:v', '1', str(tmp)],
                   capture_output=True)
    img = _imread(tmp) if tmp.is_file() else None
    if tmp.is_file():
        tmp.unlink()
    return img


def _quality(w: int, h: int, kind: str) -> str:
    long_side = max(w or 0, h or 0)
    if kind == 'video':
        return 'alta' if long_side >= 1280 else 'media' if long_side >= 720 else 'baixa'
    return 'alta' if long_side >= 1600 else 'media' if long_side >= 900 else 'baixa'


def _orient(w: int, h: int) -> str:
    return 'square' if w and h and abs(w - h) / max(w, h) < 0.06 else ('horizontal' if (w or 0) > (h or 0) else 'vertical')


def _tokens(rel: str) -> list:
    stem = Path(rel).stem.lower()
    return [t for t in re.split(r'[^a-z0-9]+', stem) if t and not t.isdigit() and len(t) > 2][:6]


def _hamming(a: int, b: int) -> int:
    return bin(a ^ b).count('1')


def index_path(slug: str, saida=SAIDA_PADRAO) -> Path:
    return home(slug, saida) / 'assets' / 'index.json'


def load(slug: str, saida=SAIDA_PADRAO) -> dict:
    f = index_path(slug, saida)
    return json.loads(f.read_text(encoding='utf-8')) if f.is_file() else {'version': 1, 'items': []}


def save(slug: str, data: dict, saida=SAIDA_PADRAO):
    data['updated'] = datetime.now().isoformat(timespec='seconds')
    index_path(slug, saida).write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def scan(slug: str, saida=SAIDA_PADRAO) -> dict:
    base = home(slug, saida) / 'assets'
    if not base.is_dir():
        raise SystemExit(f'assets: {base} não existe. Rode `vf client new {slug} "Nome"`.')
    old = {i['path']: i for i in load(slug, saida)['items']}
    nxt = {k: 1 + max([int(i['id'].split('-')[1]) for i in old.values() if i['id'].startswith(k)] or [0])
           for k in ('img', 'vid')}
    items, seen = [], []
    for d in SCAN_DIRS:
        for f in sorted((base / d).rglob('*')) if (base / d).is_dir() else []:
            ext = f.suffix.lower()
            if ext not in IMG_EXT | VID_EXT:
                continue
            rel = f.relative_to(base).as_posix()
            kind = 'video' if ext in VID_EXT else 'image'
            if kind == 'video':
                info = _video_info(f)
                w, h, dur = info['w'], info['h'], info['dur']
                img = _video_frame(f, dur)
            else:
                img = _imread(f)
                if img is None:
                    continue
                h, w = img.shape[:2]
                dur = None
            prev = old.get(rel, {})
            if prev:
                pid = prev['id']
            else:
                key = 'vid' if kind == 'video' else 'img'
                pid = f'{key}-{nxt[key]:03d}'
                nxt[key] += 1
            hsh = _dhash(img) if img is not None else 0
            blank = bool(img is not None and float(np.std(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))) < 10)
            dup = next((s[0] for s in seen if hsh and _hamming(hsh, s[1]) <= 4), None)
            seen.append((pid, hsh))
            items.append({
                'id': pid, 'path': rel, 'kind': kind, 'area': d, 'w': w, 'h': h, 'dur': dur,
                'bytes': f.stat().st_size, 'orient': _orient(w, h), 'quality': _quality(w, h, kind),
                'dhash': format(hsh, '016x'), 'duplicate_of': dup, 'blank': blank,
                'subject': prev.get('subject', ''), 'tags': prev.get('tags') or _tokens(rel),
                'use': prev.get('use', []), 'people': prev.get('people'), 'rights': prev.get('rights', 'confirm'),
                'note': prev.get('note', ''),
            })
    data = {'version': 1, 'items': items}
    save(slug, data, saida)
    return data


def sheets(slug: str, saida=SAIDA_PADRAO, only_untagged: bool = False) -> list:
    base = home(slug, saida) / 'assets'
    items = [i for i in load(slug, saida)['items'] if not (only_untagged and i['subject'])]
    out_dir = home(slug, saida) / 'exports'
    out_dir.mkdir(exist_ok=True)
    made = []
    for n in range(0, len(items), PER_SHEET):
        chunk = items[n:n + PER_SHEET]
        rows = (len(chunk) + COLS - 1) // COLS
        sheet = np.full((rows * CELL[1], COLS * CELL[0], 3), 255, np.uint8)
        for k, it in enumerate(chunk):
            f = base / it['path']
            img = _imread(f) if it['kind'] == 'image' else _video_frame(f, it['dur'] or 0)
            if img is None:
                continue
            h, w = img.shape[:2]
            s = min((CELL[0] - 6) / w, (CELL[1] - 22) / h)
            th = cv2.resize(img, (max(1, int(w * s)), max(1, int(h * s))), interpolation=cv2.INTER_AREA)
            x, y = (k % COLS) * CELL[0], (k // COLS) * CELL[1]
            sheet[y + 20:y + 20 + th.shape[0], x + 3:x + 3 + th.shape[1]] = th
            flag = ' DUP' if it['duplicate_of'] else (' VAZIA' if it['blank'] else '')
            cv2.putText(sheet, f'{it["id"]} {it["w"]}x{it["h"]}{flag}', (x + 3, y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 1, cv2.LINE_AA)
        f = out_dir / f'assets-folha-{n // PER_SHEET + 1}.png'
        cv2.imencode('.png', sheet)[1].tofile(str(f))
        made.append(f)
    return made


def set_fields(slug: str, ids: list, fields: dict, saida=SAIDA_PADRAO) -> int:
    data = load(slug, saida)
    hit = 0
    for it in data['items']:
        if it['id'] in ids:
            for k, v in fields.items():
                if v is not None:
                    it[k] = v
            hit += 1
    if hit != len(ids):
        raise SystemExit(f'assets: ids não encontrados ({len(ids) - hit}). Rode `vf assets scan {slug}`.')
    save(slug, data, saida)
    return hit


def find(slug: str, saida=SAIDA_PADRAO, tag=None, use=None, orient=None, min_quality=None, subject=None) -> list:
    out = []
    for i in load(slug, saida)['items']:
        if i['blank'] or i['duplicate_of'] or 'discard' in i['use']:
            continue
        if tag and tag.lower() not in [t.lower() for t in i['tags']]:
            continue
        if use and use not in i['use']:
            continue
        if orient and i['orient'] != orient:
            continue
        if min_quality and QUALITY_RANK[i['quality']] < QUALITY_RANK[min_quality]:
            continue
        if subject and subject.lower() not in i['subject'].lower():
            continue
        out.append(i)
    return out


def summary(slug: str, saida=SAIDA_PADRAO) -> dict:
    items = load(slug, saida)['items']
    return {'total': len(items), 'untagged': sum(1 for i in items if not i['subject']),
            'duplicates': sum(1 for i in items if i['duplicate_of']), 'blank': sum(1 for i in items if i['blank']),
            'low': sum(1 for i in items if i['quality'] == 'baixa')}


def run(a):
    if a.acao == 'scan':
        d = scan(a.cliente, a.saida)
        s = summary(a.cliente, a.saida)
        print(f'{s["total"]} arquivos indexados: {s["untagged"]} sem descrição, {s["duplicates"]} duplicados, '
              f'{s["blank"]} vazios, {s["low"]} de baixa resolução')
        return
    if a.acao == 'sheet':
        for f in sheets(a.cliente, a.saida, only_untagged=a.novos):
            print(f)
        return
    if a.acao == 'set':
        ids = [x for x in a.ids if re.match(r'^(img|vid)-\d+$', x)]
        yn = {'yes': True, 'no': False, None: None}
        n = set_fields(a.cliente, ids, {
            'subject': a.subject, 'tags': [t.strip() for t in a.tags.split(',')] if a.tags else None,
            'use': [u.strip() for u in a.use.split(',')] if a.use else None,
            'people': yn[a.people], 'rights': a.rights, 'note': a.note}, a.saida)
        print(f'{n} itens atualizados')
        return
    for i in find(a.cliente, a.saida, a.tag, a.use, a.orient, a.min, a.subject):
        print(f'{i["id"]:8} {i["orient"]:10} {i["quality"]:5} {",".join(i["tags"])[:34]:34} {i["path"]}')
