"""Panel server (standard library only).

Routes:
  GET  /                         panel page
  GET  /api/galleries            user galleries + the fixed examples gallery
  PUT  /api/galleries            saves the user galleries to galleries.json
  GET  /api/gallery/<id>         scans the gallery folders and returns its items (jobs, examples, loose videos)
  GET  /file?g=<id>&b=<n>&p=<rel> serves a file from inside the gallery (with Range, so videos can seek)
  POST /api/open                 opens an item's folder in the file manager
  GET  /api/setup                live check of the required and optional tools
  GET  /api/skills               the engine's Claude Code skills (.claude/skills), for the Skills page
  GET  /api/gallery/<id>/workspace          brief, brand, assets, references, research of the gallery
  PUT  /api/gallery/<id>/brief|brand        saves brief.md / brand.json in the gallery home folder
  POST /api/gallery/<id>/upload?area=..     raw body upload (X-Filename header) to assets/ or references/
  POST /api/gallery/<id>/references         adds a link or text reference
  GET  /manual?g=<id>                        brand manual built from the gallery (print-ready)
  POST /api/gallery/<id>/manual-pdf         exports the manual to exports/manual-de-marca.pdf
  POST /api/gallery/<id>/references/<r>/remove, /trash   moves files to .trash (never deletes)
  GET  /api/tasks                task queue (narrate, check, sheet, render, new job) + available styles
  GET  /api/tasks/<id>?since=n   one task with its log from line n
  POST /api/tasks                queues an engine command for a job inside saida/
  POST /api/tasks/<id>/cancel    cancels a queued or running task
  GET  /guide                    the engine guide (guide.html), with its example videos under /styles/

Security: listens on 127.0.0.1 only, checks the Host header (against DNS rebinding), accepts writes only
from its own origin and only serves files that are inside the gallery's registered folders.
"""
import io
import json
import mimetypes
import os
import re
import subprocess
import sys
import threading
import webbrowser
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from ..core.paths import APROVAR, ENTRADA, FINAL, INTERNO, ROOT, SAIDA_PADRAO
from .runner import TaskError, TaskQueue, available_styles
from .setup_check import check as check_setup
from .skills_doc import read_skills
from . import workspace as ws
from . import manual
from ..core import client as client_mod
from ..core import docs as docs_mod
from .styles_catalog import catalog as styles_catalog

GALLERIES_FILE = ROOT / 'galleries.json'
PAGE = Path(__file__).with_name('panel.html')
GUIDE = ROOT / 'guide.html'
LEARN_JS = Path(__file__).with_name('learn.js')
STYLES = ROOT / 'styles'
EXAMPLES = {'id': 'examples', 'name': 'Exemplos do motor', 'folders': ['styles'], 'fixed': True}
DEFAULT = {'version': 1, 'galleries': [{'id': 'my-videos', 'name': 'Meus vídeos', 'folders': ['saida']}]}
SKIP = {*ws.WORKSPACE_DIRS, INTERNO, 'node_modules', '.git', '.venv', '__pycache__', '.hyperframes', ENTRADA, APROVAR, FINAL}
MAX_DEPTH = 4
VIDEO_EXT = {'.mp4', '.webm', '.mov', '.m4v'}
mimetypes.add_type('video/mp4', '.mp4')
QUEUE: TaskQueue | None = None
mimetypes.add_type('text/plain', '.md')
mimetypes.add_type('text/javascript', '.js')


# ---------- galleries ----------

def read_galleries() -> dict:
    if not GALLERIES_FILE.exists():
        save_galleries(DEFAULT)
    try:
        return json.loads(GALLERIES_FILE.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return DEFAULT


def save_galleries(data: dict) -> None:
    tmp = GALLERIES_FILE.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(GALLERIES_FILE)


def client_galleries(known: list) -> list[dict]:
    """One gallery per client folder (saida/clients/<slug>/marca.json), found on disk: no registration needed."""
    root = (SAIDA_PADRAO / client_mod.CLIENTS).resolve()
    have = {resolve_folder(f) for g in known for f in g.get('folders', [])}
    out = []
    for d in sorted(root.iterdir()) if root.is_dir() else []:
        if (d / 'marca.json').is_file() and d.resolve() not in have:
            try:
                name = json.loads((d / 'marca.json').read_text(encoding='utf-8')).get('nome') or d.name
            except (OSError, json.JSONDecodeError):
                name = d.name
            out.append({'id': f'client-{d.name}', 'name': name, 'folders': [f'saida/{client_mod.CLIENTS}/{d.name}']})
    return out


def all_galleries() -> list[dict]:
    """Galleries for the menu. The generic saida/clients container is replaced by the Clientes section (one entry per client)."""
    root = (SAIDA_PADRAO / client_mod.CLIENTS).resolve()
    kept = []
    for g in [EXAMPLES] + list(read_galleries().get('galleries', [])):
        folders = [resolve_folder(f) for f in g.get('folders', [])]
        if len(folders) == 1 and folders[0] == root:
            continue
        if len(folders) == 1 and folders[0].parent == root and (folders[0] / 'marca.json').is_file():
            g = dict(g, kind='client')
        kept.append(g)
    return kept + [dict(g, kind='client') for g in client_galleries(kept)]


def find_gallery(gid: str) -> dict | None:
    return next((g for g in all_galleries() if g['id'] == gid), None)


def resolve_folder(folder: str) -> Path:
    p = Path(os.path.expandvars(os.path.expanduser(folder)))
    return (p if p.is_absolute() else ROOT / p).resolve()


def validate(data) -> tuple[dict | None, str]:
    if not isinstance(data, dict) or not isinstance(data.get('galleries'), list):
        return None, 'formato inválido'
    clean, ids = [], set()
    for g in data['galleries']:
        name = str(g.get('name', '')).strip()[:80]
        folders = [str(p).strip() for p in g.get('folders', []) if str(p).strip()][:20]
        if not name or not folders:
            return None, f'a galeria "{name or "?"}" precisa de nome e de pelo menos uma pasta'
        gid = re.sub(r'[^a-z0-9-]+', '-', str(g.get('id') or name).lower()).strip('-') or 'gallery'
        while gid in ids or gid == EXAMPLES['id']:
            gid += '-2'
        ids.add(gid)
        missing = []
        for p in folders:
            target = resolve_folder(p)
            if target.is_dir():
                continue
            if target.is_relative_to(SAIDA_PADRAO.resolve()):
                target.mkdir(parents=True, exist_ok=True)
            else:
                missing.append(p)
        if missing:
            return None, f'pasta não encontrada: {missing[0]} (fora de saida/ a pasta precisa existir)'
        clean.append({'id': gid, 'name': name, 'folders': folders})
    return {'version': 1, 'galleries': clean}, ''


# ---------- scanning ----------

def is_job(d: Path) -> bool:
    return any((d / s).is_dir() for s in (ENTRADA, APROVAR, FINAL))


def is_example(d: Path) -> bool:
    return (d / 'video.mp4').is_file() and (d / 'roteiro.txt').is_file()


def rel(base: Path, p: Path) -> str:
    return p.relative_to(base).as_posix()


def job_name(d: Path) -> str:
    try:
        return d.resolve().relative_to(SAIDA_PADRAO.resolve()).as_posix()
    except ValueError:
        return ''


def next_command(d: Path, steps: dict) -> str:
    name = job_name(d)
    if not name:
        return ''
    if steps['video'] or not steps['script']:
        return ''
    if not steps['narration']:
        return f'uv run vf narrate saida/{name}/1-entrada/roteiro.txt --nome {name} --engine edge --modelo small'
    if not steps['sheet']:
        return f'uv run vf checar {name}; uv run vf storyboard {name}'
    return f'uv run vf storyboard {name} --animar'


def carousel_info(base: Path, d: Path) -> dict | None:
    """A carousel job (1-entrada/carrossel.json): cover, slide PNGs, caption, notes, review, animated MP4 count."""
    cfg_f = d / ENTRADA / 'carrossel.json'
    if not cfg_f.is_file():
        return None
    try:
        cfg = json.loads(cfg_f.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        cfg = {}
    pngs = sorted((d / FINAL / 'png').glob('*.png')) if (d / FINAL / 'png').is_dir() else []
    animated = sorted((d / FINAL / 'animado').glob('[0-9][0-9].mp4')) if (d / FINAL / 'animado').is_dir() else []
    files = {}
    for key, p in (('sheet', d / APROVAR / 'carrossel_folha.png'), ('caption', d / ENTRADA / 'legenda.txt'),
                   ('notes', d / ENTRADA / 'notas.md'), ('review', d / APROVAR / 'revisao.md'), ('json', cfg_f)):
        if p.is_file():
            files[key] = rel(base, p)
    if pngs:
        files['cover'] = rel(base, pngs[0])
    status = 'ready' if animated else ('review' if pngs else 'script')
    return {'slides': len(cfg.get('slides', [])), 'format': cfg.get('formato', 'post'), 'png': [rel(base, p) for p in pngs],
            'animated': len(animated), 'status': status, 'files': files}


def job_item(i: int, base: Path, d: Path) -> dict:
    inp, rev, out, internal = d / ENTRADA, d / APROVAR, d / FINAL, d / INTERNO
    steps = {
        'script': (inp / 'roteiro.txt').is_file(),
        'narration': (internal / 'narration.wav').is_file(),
        'storyboard': (inp / 'storyboard.json').is_file(),
        'sheet': (rev / 'storyboard_folha.png').is_file(),
        'video': (out / 'video.mp4').is_file(),
    }
    files = {}
    if steps['video']: files['video'] = rel(base, out / 'video.mp4')
    if steps['sheet']: files['sheet'] = rel(base, rev / 'storyboard_folha.png')
    if steps['script']: files['script'] = rel(base, inp / 'roteiro.txt')
    if steps['storyboard']: files['storyboard'] = rel(base, inp / 'storyboard.json')
    extras = [rel(base, x) for x in sorted(out.glob('*'))
              if x.suffix.lower() in VIDEO_EXT and x.name != 'video.mp4'] if out.is_dir() else []
    if steps['video']: status = 'ready'
    elif steps['sheet']: status = 'review'
    elif steps['narration'] or steps['storyboard']: status = 'production'
    else: status = 'script'
    carousel = carousel_info(base, d)
    if carousel:
        steps, status = None, carousel['status']
        files = carousel.pop('files')
        extras = []
    times = [p.stat().st_mtime for p in (inp, rev, out, internal) if p.exists()]
    return {'type': 'job', 'carousel': carousel, 'name': rel(base, d), 'base': i, 'folder': rel(base, d) or '.', 'status': status,
            'steps': steps, 'files': files, 'extras': extras, 'command': '' if carousel else next_command(d, steps), 'job': job_name(d),
            'mtime': max(times) if times else d.stat().st_mtime}


def example_item(i: int, base: Path, d: Path) -> dict:
    files = {'video': rel(base, d / 'video.mp4'), 'script': rel(base, d / 'roteiro.txt')}
    if (d / 'folha.jpg').is_file(): files['sheet'] = rel(base, d / 'folha.jpg')
    if (d / 'storyboard.json').is_file(): files['storyboard'] = rel(base, d / 'storyboard.json')
    style = d.parent.parent.name if d.parent.name == 'exemplos' else ''
    prompt = (d / 'prompt.txt').read_text(encoding='utf-8').strip() if (d / 'prompt.txt').is_file() else ''
    return {'type': 'example', 'name': d.name, 'style': style, 'prompt': prompt, 'base': i, 'folder': rel(base, d), 'status': 'ready',
            'steps': None, 'files': files, 'extras': [], 'command': '', 'mtime': (d / 'video.mp4').stat().st_mtime}


def file_item(i: int, base: Path, f: Path) -> dict:
    return {'type': 'file', 'name': rel(base, f), 'base': i, 'folder': rel(base, f.parent) or '.', 'status': 'ready',
            'steps': None, 'files': {'video': rel(base, f)}, 'extras': [], 'command': '', 'mtime': f.stat().st_mtime}


def scan(g: dict) -> dict:
    items, warnings = [], []
    for i, folder in enumerate(g['folders']):
        base = resolve_folder(folder)
        if not base.is_dir():
            warnings.append(f'pasta não encontrada: {folder}')
            continue
        stack = [(base, 0)]
        while stack:
            d, depth = stack.pop()
            if d != base and is_job(d):
                items.append(job_item(i, base, d)); continue
            if d != base and is_example(d):
                items.append(example_item(i, base, d)); continue
            try:
                children = sorted(d.iterdir())
            except OSError:
                continue
            for x in children:
                if x.is_file() and x.suffix.lower() in VIDEO_EXT:
                    items.append(file_item(i, base, x))
                elif x.is_dir() and depth < MAX_DEPTH and x.name not in SKIP and not x.name.startswith('.'):
                    stack.append((x, depth + 1))
    items.sort(key=lambda it: it['mtime'], reverse=True)
    return {'id': g['id'], 'items': items, 'warnings': warnings}


def gallery_home(gid: str) -> tuple[dict | None, Path | None]:
    g = find_gallery(gid)
    if not g or g.get('fixed'):
        return None, None
    return g, resolve_folder(g['folders'][0])


def gallery_slug(home: Path) -> str:
    try:
        return home.relative_to(SAIDA_PADRAO.resolve()).as_posix()
    except ValueError:
        return ''


def inside(g: dict, base_idx: int, relpath: str) -> Path | None:
    if not (0 <= base_idx < len(g['folders'])):
        return None
    base = resolve_folder(g['folders'][base_idx])
    target = (base / unquote(relpath)).resolve()
    return target if target == base or target.is_relative_to(base) else None


EDITABLE = {'brief.md', 'visao-geral.md', 'LEIA-ANTES.md', 'marca.json', 'identidade/guia-visual.md', 'social/plano.md', 'social/calendario.md'}


def client_slug(home: Path) -> str | None:
    """Slug of a client folder (saida/clients/<slug>), or None when the gallery is not a client."""
    return home.name if home.parent == (SAIDA_PADRAO / client_mod.CLIENTS).resolve() and (home / 'marca.json').is_file() else None


# ---------- HTTP ----------

class PanelHandler(BaseHTTPRequestHandler):
    server_version = 'vf-panel'

    def log_message(self, fmt, *args):  # quiet; errors go back in the response
        pass

    def _allowed(self, value: str | None, prefix: str = '') -> bool:
        port = self.server.server_address[1]
        return value in (f'{prefix}127.0.0.1:{port}', f'{prefix}localhost:{port}')

    def _host_ok(self) -> bool:
        return self._allowed(self.headers.get('Host'))

    def _origin_ok(self) -> bool:
        origin = self.headers.get('Origin')
        return origin is None or self._allowed(origin, 'http://')

    def _json(self, code: int, data) -> None:
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get('Content-Length') or 0)
        if n > 1_000_000:
            return None
        try:
            return json.loads(self.rfile.read(n) or b'null')
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        if not self._host_ok():
            return self._json(403, {'error': 'host não permitido'})
        u = urlparse(self.path)
        if u.path in ('/', '/index.html'):
            return self._send_file(PAGE)
        if u.path in ('/md.js', '/vendor/marked.umd.js'):
            return self._send_file(Path(__file__).parent / u.path.lstrip('/'))
        if u.path in ('/learn.js', '/workspace.js', '/wizard.js'):
            return self._send_file(Path(__file__).with_name(u.path[1:]))
        if u.path == '/guide':
            return self._send_file(GUIDE) if GUIDE.is_file() else self._json(404, {'error': 'guide.html não encontrado'})
        if u.path.startswith('/styles/'):
            target = (STYLES / unquote(u.path[len('/styles/'):])).resolve()
            if not target.is_relative_to(STYLES.resolve()) or not target.is_file():
                return self._json(404, {'error': 'arquivo não existe'})
            return self._send_file(target)
        if u.path == '/api/tasks':
            return self._json(200, {'tasks': QUEUE.listing(), 'styles': available_styles()})
        m = re.match(r'^/api/tasks/(\d+)$', u.path)
        if m:
            task = QUEUE.tasks.get(int(m.group(1)))
            if not task:
                return self._json(404, {'error': 'tarefa não existe'})
            since = int((parse_qs(u.query).get('since') or ['0'])[0] or 0)
            return self._json(200, QUEUE.public(task, since))
        if u.path == '/manual':
            g, home = gallery_home(parse_qs(u.query).get('g', [''])[0])
            if not g:
                return self._json(404, {'error': 'galeria não existe'})
            body = manual.build_html(g, home, [resolve_folder(f) for f in g['folders']]).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            return self.wfile.write(body)
        if u.path == '/api/styles':
            return self._json(200, {'styles': styles_catalog()})
        if u.path == '/api/skills':
            return self._json(200, {'skills': read_skills()})
        if u.path == '/api/setup':
            return self._json(200, {'items': check_setup()})
        if u.path == '/api/galleries':
            return self._json(200, {'galleries': all_galleries(), 'file': str(GALLERIES_FILE)})
        m = re.match(r'^/api/gallery/([^/]+)/workspace$', u.path)
        if m:
            g, home = gallery_home(unquote(m.group(1)))
            if not g:
                return self._json(404, {'error': 'galeria não existe'})
            data = ws.read(home, g['name'])
            data.update({'home': g['folders'][0], 'slug': gallery_slug(home)})
            return self._json(200, data)
        m = re.match(r'^/api/gallery/([^/]+)/zip$', u.path)
        if m:
            q = parse_qs(u.query)
            g = find_gallery(unquote(m.group(1)))
            try:
                target = inside(g, int(q.get('b', ['0'])[0]), q.get('p', [''])[0]) if g else None
            except ValueError:
                target = None
            if not target or not target.is_dir() or not (target / ENTRADA / 'carrossel.json').is_file():
                return self._json(404, {'error': 'job de carrossel não encontrado'})
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                for p in sorted((target / FINAL / 'png').glob('*.png')):
                    zf.write(p, f'png/{p.name}')
                for p in sorted((target / FINAL / 'animado').glob('[0-9][0-9].mp4')) if (target / FINAL / 'animado').is_dir() else []:
                    zf.write(p, f'animado/{p.name}')
                for p, name in ((target / ENTRADA / 'legenda.txt', 'legenda.txt'), (target / ENTRADA / 'notas.md', 'notas.md'),
                                (target / APROVAR / 'revisao.md', 'revisao.md')):
                    if p.is_file():
                        zf.write(p, name)
            data = buf.getvalue()
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', f'attachment; filename="{target.name}.zip"')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            return self.wfile.write(data)
        m = re.match(r'^/api/gallery/([^/]+)/client$', u.path)
        if m:
            g, home = gallery_home(unquote(m.group(1)))
            if not g or not client_slug(home):
                return self._json(404, {'error': 'esta galeria não é um cliente'})
            return self._json(200, client_mod.view(home))
        if u.path.startswith('/api/gallery/'):
            g = find_gallery(unquote(u.path.rsplit('/', 1)[1]))
            return self._json(200, scan(g)) if g else self._json(404, {'error': 'galeria não existe'})
        if u.path == '/file':
            q = parse_qs(u.query)
            g = find_gallery(q.get('g', [''])[0])
            try:
                target = inside(g, int(q.get('b', ['0'])[0]), q.get('p', [''])[0]) if g else None
            except ValueError:
                target = None
            if not target or not target.is_file():
                return self._json(404, {'error': 'arquivo fora da galeria ou inexistente'})
            return self._send_file(target)
        return self._json(404, {'error': 'rota não existe'})

    def _send_file(self, target: Path):
        size = target.stat().st_size
        ctype = mimetypes.guess_type(target.name)[0] or 'application/octet-stream'
        if target.suffix == '.json':
            ctype = 'application/json; charset=utf-8'
        elif target.suffix == '.html':
            ctype = 'text/html; charset=utf-8'
        elif ctype.startswith('text/'):
            ctype += '; charset=utf-8'
        start, end, partial = 0, size - 1, False
        m = re.match(r'bytes=(\d*)-(\d*)', self.headers.get('Range', ''))
        if m and size:
            if m.group(1):
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else size - 1
            else:
                start = max(size - int(m.group(2) or 0), 0)
            end = min(end, size - 1)
            if start > end:
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{size}')
                self.end_headers()
                return
            partial = True
        self.send_response(206 if partial else 200)
        self.send_header('Content-Type', ctype)
        self.send_header('Accept-Ranges', 'bytes')
        if target.suffix in ('.html', '.js'):
            self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(end - start + 1 if size else 0))
        if partial:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        with target.open('rb') as fh:
            fh.seek(start)
            left = end - start + 1 if size else 0
            try:
                while left > 0:
                    chunk = fh.read(min(256 * 1024, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
            except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                pass

    def do_PUT(self):
        if not (self._host_ok() and self._origin_ok()):
            return self._json(403, {'error': 'origem não permitida'})
        path = urlparse(self.path).path
        m = re.match(r'^/api/gallery/([^/]+)/(brief|brand)$', path)
        if m:
            g, home = gallery_home(unquote(m.group(1)))
            if not g:
                return self._json(404, {'error': 'galeria não existe'})
            body = self._body() or {}
            try:
                if m.group(2) == 'brief':
                    ws.save_brief(home, str(body.get('text', '')))
                    return self._json(200, {'ok': True})
                return self._json(200, ws.save_brand(home, body))
            except ws.WorkspaceError as e:
                return self._json(400, {'error': str(e)})
        m = re.match(r'^/api/gallery/([^/]+)/file$', path)
        if m:
            g, home = gallery_home(unquote(m.group(1)))
            if not g or not client_slug(home):
                return self._json(404, {'error': 'esta galeria não é um cliente'})
            body = self._body() or {}
            rel_path, text = str(body.get('path', '')), body.get('text')
            if rel_path not in EDITABLE or not isinstance(text, str) or len(text) > 400_000:
                return self._json(400, {'error': 'arquivo não editável pelo painel'})
            if rel_path.endswith('.json'):
                try:
                    json.loads(text)
                except json.JSONDecodeError as e:
                    return self._json(400, {'error': f'JSON inválido: {e}'})
            target = home / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding='utf-8')
            return self._json(200, {'ok': True})
        m = re.match(r'^/api/gallery/([^/]+)/doc/(proposal|contract|statement|estimate|presentation)$', path)
        if m:
            g, home = gallery_home(unquote(m.group(1)))
            if not g or not client_slug(home):
                return self._json(404, {'error': 'esta galeria não é um cliente'})
            body = self._body()
            if not isinstance(body, dict) or len(json.dumps(body)) > 400_000:
                return self._json(400, {'error': 'dados inválidos'})
            (home / 'documentos').mkdir(exist_ok=True)
            (home / 'documentos' / f'{m.group(2)}.json').write_text(json.dumps(body, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            return self._json(200, {'ok': True})
        if path != '/api/galleries':
            return self._json(404, {'error': 'rota não existe'})
        clean, error = validate(self._body())
        if not clean:
            return self._json(400, {'error': error})
        save_galleries(clean)
        return self._json(200, {'galleries': all_galleries(), 'file': str(GALLERIES_FILE)})

    def do_POST(self):
        if not (self._host_ok() and self._origin_ok()):
            return self._json(403, {'error': 'origem não permitida'})
        u = urlparse(self.path)
        path = u.path
        m = re.match(r'^/api/gallery/([^/]+)/doc/(proposal|contract|statement|estimate|presentation)/(new|build)$', path)
        if m:
            g, home = gallery_home(unquote(m.group(1)))
            slug = client_slug(home) if g else None
            if not slug:
                return self._json(404, {'error': 'esta galeria não é um cliente'})
            try:
                if m.group(3) == 'new':
                    return self._json(200, {'created': [Path(x).name for x in docs_mod.new(slug, m.group(2))]})
                r = docs_mod.build(slug, m.group(2))
            except SystemExit as e:
                return self._json(400, {'error': str(e)})
            except (OSError, subprocess.SubprocessError) as e:
                return self._json(500, {'error': str(e)})
            return self._json(200, {'pdf': r['pdf'].relative_to(home).as_posix(), 'open': r['open']})
        m = re.match(r'^/api/gallery/([^/]+)/manual-pdf$', path)
        if m:
            g, home = gallery_home(unquote(m.group(1)))
            if not g:
                return self._json(404, {'error': 'galeria não existe'})
            port = self.server.server_address[1]
            try:
                out = manual.export_pdf(f'http://127.0.0.1:{port}/manual?g={g["id"]}', home)
            except manual.ManualError as e:
                return self._json(500, {'error': str(e)})
            return self._json(200, {'path': out.relative_to(home).as_posix(), 'size': out.stat().st_size})
        m = re.match(r'^/api/gallery/([^/]+)/(upload|references|trash)(?:/([^/]+)/remove)?$', path)
        if m:
            g, home = gallery_home(unquote(m.group(1)))
            if not g:
                return self._json(404, {'error': 'galeria não existe'})
            try:
                if m.group(2) == 'upload':
                    q = {k: v[0] for k, v in parse_qs(u.query).items()}
                    name = unquote(self.headers.get('X-Filename', ''))
                    length = int(self.headers.get('Content-Length') or 0)
                    return self._json(200, ws.upload(home, q.get('area', 'assets'), q.get('category', ''), name,
                                                     self.rfile, length, q))
                if m.group(2) == 'references' and m.group(3):
                    return self._json(200, ws.remove_reference(home, unquote(m.group(3))))
                body = self._body() or {}
                if m.group(2) == 'references':
                    return self._json(200, ws.add_reference(home, body))
                return self._json(200, ws.trash(home, str(body.get('path', ''))))
            except ws.WorkspaceError as e:
                return self._json(400, {'error': str(e)})
        if path == '/api/tasks':
            d = self._body() or {}
            try:
                return self._json(200, QUEUE.submit(str(d.get('action', '')), str(d.get('job', '')), d.get('options') or {}))
            except TaskError as e:
                return self._json(400, {'error': str(e)})
        m = re.match(r'^/api/tasks/(\d+)/cancel$', path)
        if m:
            try:
                return self._json(200, QUEUE.cancel(int(m.group(1))))
            except TaskError as e:
                return self._json(404, {'error': str(e)})
        if path != '/api/open':
            return self._json(404, {'error': 'rota não existe'})
        d = self._body() or {}
        g = find_gallery(str(d.get('g', '')))
        try:
            target = inside(g, int(d.get('b', 0)), str(d.get('p', ''))) if g else None
        except ValueError:
            target = None
        if not target or not target.exists():
            return self._json(404, {'error': 'pasta fora da galeria'})
        folder = target if target.is_dir() else target.parent
        if sys.platform == 'win32':
            os.startfile(str(folder))  # folder validated above
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', str(folder)])
        else:
            subprocess.Popen(['xdg-open', str(folder)])
        return self._json(200, {'ok': True, 'folder': str(folder)})


def run(args) -> None:
    global QUEUE
    SAIDA_PADRAO.mkdir(parents=True, exist_ok=True)  # clone novo: a pasta dos jobs ainda não existe
    read_galleries()
    QUEUE = TaskQueue()
    srv = ThreadingHTTPServer(('127.0.0.1', args.port), PanelHandler)
    url = f'http://127.0.0.1:{args.port}/'
    print(f'painel: {url}  (Ctrl+C para fechar)')
    print(f'  galerias em {GALLERIES_FILE}')
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\npainel fechado')
    finally:
        srv.server_close()
