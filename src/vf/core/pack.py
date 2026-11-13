"""Content pack for a client: the posts, captions, review, grid preview and publishing plan, in one folder and one zip.

  vf pack new <client> [<pack>]                       writes <pack>.json from the jobs named pNN-* (edit titles and order)
  vf pack build <client> [<pack>] [--inicio YYYY-MM-DD] [--por-semana 3]

<pack>.json (default pack-01) lives in saida/clients/<client>/:
  {"nome": "...", "posts": [{"job": "p01-...", "titulo": "..."}], "destaques": "d01-..."}
Build writes exports/<pack>/ with one folder per post (PNGs, legenda.txt, notas.md, revisao.md), the highlight covers,
grade.png (how the profile grid reads), resumo.md (review status, pending items, publishing plan) and <pack>.zip.
Publishing order is the reverse of the grid order, so the first post ends at the top left of the profile.
The review is rerun at build time; a job with review errors is listed as BLOCKED and its PNGs are not packed.
"""
import json
import shutil
import zipfile
from datetime import date, timedelta
from pathlib import Path

import cv2
import numpy as np

from .client import home
from .paths import SAIDA_PADRAO
from .review import review_job, write_report

CELL = (360, 450)
GAP = 6
WEEKDAYS = {1: (2,), 2: (0, 3), 3: (0, 2, 4), 4: (0, 1, 3, 4), 5: (0, 1, 2, 3, 4)}  # Monday = 0
DAYS = ['seg', 'ter', 'qua', 'qui', 'sex', 'sáb', 'dom']


def _pack_file(h: Path, pack: str) -> Path:
    return h / f'{pack}.json'


def new(client: str, pack: str = 'pack-01', saida=SAIDA_PADRAO) -> Path:
    h = home(client, saida)
    f = _pack_file(h, pack)
    if f.exists():
        raise SystemExit(f'pack: {f} já existe (não sobrescrevo)')
    posts = []
    for j in sorted(h.glob('p[0-9][0-9]-*/1-entrada/carrossel.json')):
        cfg = json.loads(j.read_text(encoding='utf-8'))
        posts.append({'job': j.parent.parent.name, 'titulo': cfg.get('titulo', j.parent.parent.name)})
    dest = next((p.parent.parent.name for p in sorted(h.glob('d[0-9][0-9]-*/1-entrada/carrossel.json'))), None)
    f.write_text(json.dumps({'nome': pack, 'posts': posts, 'destaques': dest}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return f


def _pngs(h: Path, job: str) -> list:
    return sorted((h / job / '3-final' / 'png').glob('*.png'))


def _grid(covers: list, out: Path, cols: int = 3):
    cells = []
    for c in covers:
        img = cv2.imdecode(np.fromfile(str(c), np.uint8), cv2.IMREAD_COLOR) if c else None
        cells.append(cv2.resize(img, CELL, interpolation=cv2.INTER_AREA) if img is not None else np.full((CELL[1], CELL[0], 3), 40, np.uint8))
    while len(cells) % cols:
        cells.append(np.full((CELL[1], CELL[0], 3), 255, np.uint8))
    rows = []
    for i in range(0, len(cells), cols):
        parts = []
        for c in cells[i:i + cols]:
            parts += [c, np.full((CELL[1], GAP, 3), 255, np.uint8)]
        row = np.hstack(parts[:-1])
        rows += [row, np.full((GAP, row.shape[1], 3), 255, np.uint8)]
    cv2.imencode('.png', np.vstack(rows[:-1]))[1].tofile(str(out))


def _schedule(n: int, start: date, per_week: int) -> list:
    days = WEEKDAYS.get(per_week, WEEKDAYS[3])
    out, d = [], start
    while len(out) < n:
        if d.weekday() in days:
            out.append(d)
        d += timedelta(days=1)
    return out


def _clean(out: Path):
    """Empties exports/<pack>: only files this command wrote, always inside the client's exports folder."""
    if out.exists():
        for p in sorted(out.rglob('*'), reverse=True):
            p.unlink() if p.is_file() else p.rmdir()
    out.mkdir(parents=True, exist_ok=True)


def build(client: str, pack: str = 'pack-01', start: date | None = None, per_week: int = 3, saida=SAIDA_PADRAO) -> dict:
    h = home(client, saida)
    cfg = json.loads(_pack_file(h, pack).read_text(encoding='utf-8'))
    out = h / 'exports' / pack
    _clean(out)
    rows, covers, pending, blocked = [], [], [], []
    for n, post in enumerate(cfg['posts'], 1):
        job = post['job']
        r = review_job(client, job, saida)
        write_report(client, r, saida)
        pngs = _pngs(h, job)
        ok = bool(pngs) and not r['errors']
        if ok:
            d = out / f'{n:02d}-{job.split("-", 1)[1]}'
            d.mkdir()
            for k, p in enumerate(pngs, 1):
                shutil.copy2(p, d / f'{k:02d}.png')
            for name, src in (('legenda.txt', h / job / '1-entrada' / 'legenda.txt'), ('notas.md', h / job / '1-entrada' / 'notas.md'),
                              ('revisao.md', h / job / '2-aprovar' / 'revisao.md')):
                if src.is_file():
                    shutil.copy2(src, d / name)
            covers.append(pngs[0])
        else:
            blocked.append(job)
            covers.append(None)
        pending += [(n, post['titulo'], x) for x in r['pending']]
        rows.append((n, post['titulo'], len(pngs), r, ok))
    _grid(covers, out / 'grade.png')
    hl = cfg.get('destaques')
    n_hl = 0
    if hl and _pngs(h, hl):
        (out / 'destaques').mkdir()
        for k, p in enumerate(_pngs(h, hl), 1):
            shutil.copy2(p, out / 'destaques' / f'{k:02d}.png')
            n_hl += 1
    start = start or date.today() + timedelta(days=(7 - date.today().weekday()) % 7 or 7)
    dates = _schedule(len(rows), start, per_week)
    plan = {n: dates[len(rows) - n] for n, *_ in rows}  # last post first: post 1 is published last
    md = [f'# {cfg["nome"]}: resumo', '', f'{len(rows)} posts · {sum(1 for r in rows if r[4])} prontos para aprovação · {len(blocked)} bloqueados', '',
          '## Posts', '', '| # | Post | Slides | Erros | Avisos | Pendências | Publicar em |', '|---|---|---|---|---|---|---|']
    for n, titulo, ns, r, ok in rows:
        d = plan[n]
        md.append(f'| {n} | {titulo}{"" if ok else " **(BLOQUEADO)**"} | {ns} | {len(r["errors"])} | {len(r["warnings"])} | {len(r["pending"])} | {DAYS[d.weekday()]} {d.strftime("%d/%m")} |')
    md += ['', '## Ordem de publicação', '',
           'Publique do **último para o primeiro**: assim o Post 1 fica no canto superior esquerdo do perfil e o grid se lê de 1 a 12 (veja `grade.png`). '
           f'Sugestão de {per_week} posts por semana, a partir de {start.strftime("%d/%m/%Y")}; datas são sugestão, não regra.', '',
           '## Pendências antes de publicar', '']
    md += [f'- Post {n} ({t}): {x}' for n, t, x in pending] or ['- nenhuma']
    md += ['', '## Destaques', '', f'{n_hl} capas em `destaques/` (story 1080x1920; o Instagram recorta em círculo).', '',
           'Nada deste pacote foi enviado ao cliente. Aprovação final é humana.']
    (out / 'resumo.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    z = out.parent / f'{pack}.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(out.rglob('*')):
            if p.is_file():
                zf.write(p, p.relative_to(out.parent).as_posix())
    return {'dir': out, 'zip': z, 'posts': len(rows), 'blocked': blocked, 'pending': len(pending)}


def run(a):
    if a.acao == 'new':
        print(f'criado {new(a.cliente, a.pack, a.saida)}')
        return
    r = build(a.cliente, a.pack, date.fromisoformat(a.inicio) if a.inicio else None, a.por_semana, a.saida)
    print(f'{r["posts"]} posts · {len(r["blocked"])} bloqueados · {r["pending"]} pendências\nPasta: {r["dir"]}\nZIP:   {r["zip"]}')
    if r['blocked']:
        print('BLOQUEADOS (erros de revisão ou sem PNG):', ', '.join(r['blocked']))
