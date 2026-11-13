"""Gallery workspace: the gallery's home folder holds its brief, brand, assets, references and research.

saida/<gallery>/
  brief.md            the gallery PRD (audience, tone, goals) read by the agent before creating jobs
  brand.json          name, colors, fonts, logo, call to action
  assets/<category>/  uploaded files (brand, characters, images, audio, docs)
  references/         index.json + files/ + notes/ + <slug>.md analyses (link, file or text references)
  research/           <slug>.md studies with sources
  exports/            generated files (brand manual PDF)
"""
import json
import re
import shutil
import time
import unicodedata
from pathlib import Path

ASSET_CATEGORIES = ('brand', 'characters', 'images', 'audio', 'docs')
WORKSPACE_DIRS = {'assets', 'references', 'research', 'exports'}
ALLOWED_EXT = {
    '.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.mp4', '.mov', '.webm', '.m4v',
    '.mp3', '.wav', '.m4a', '.ogg', '.ttf', '.otf', '.woff', '.woff2', '.pdf', '.txt', '.md', '.json',
}
CATEGORY_BY_EXT = {
    'images': {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.mp4', '.mov', '.webm', '.m4v'},
    'audio': {'.mp3', '.wav', '.m4a', '.ogg'},
    'brand': {'.ttf', '.otf', '.woff', '.woff2'},
    'docs': {'.pdf', '.txt', '.md', '.json'},
}
MAX_UPLOAD = 500 * 1024 * 1024
BRIEF_TEMPLATE = """# {name}

## Tipo
(marca, canal, página, cliente, campanha ou série)

## Objetivo
O que esta galeria precisa alcançar.

## Público
Quem assiste ou lê, o que sabe e o que quer.

## Tom de voz
Como fala (e o que evita).

## Plataformas e frequência

## Estilos preferidos do motor

## Primeiros temas
1.
2.
3.
"""


class WorkspaceError(ValueError):
    pass


def slugify(text: str, fallback: str = 'item') -> str:
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')[:60] or fallback


def safe_filename(name: str) -> str:
    stem, ext = Path(name).stem, Path(name).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise WorkspaceError(f'tipo de arquivo não aceito: {ext or "sem extensão"}')
    return slugify(stem, 'file') + ext


def unique_path(folder: Path, filename: str) -> Path:
    target = folder / filename
    n = 2
    while target.exists():
        target = folder / f'{Path(filename).stem}-{n}{Path(filename).suffix}'
        n += 1
    return target


def guess_category(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return next((c for c, exts in CATEGORY_BY_EXT.items() if ext in exts), 'docs')


def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return default


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(path)


def _file_entry(home: Path, f: Path) -> dict:
    st = f.stat()
    return {'name': f.name, 'path': f.relative_to(home).as_posix(), 'size': st.st_size, 'mtime': st.st_mtime}


def read(home: Path, gallery_name: str) -> dict:
    brief = home / 'brief.md'
    assets = []
    for cat in ASSET_CATEGORIES:
        folder = home / 'assets' / cat
        if folder.is_dir():
            assets += [dict(_file_entry(home, f), category=cat) for f in sorted(folder.iterdir()) if f.is_file()]
    refs = _read_json(home / 'references' / 'index.json', [])
    research = []
    if (home / 'research').is_dir():
        for f in sorted((home / 'research').glob('*.md')):
            first = next((l.lstrip('# ').strip() for l in f.read_text(encoding='utf-8').splitlines() if l.strip()), f.stem)
            research.append(dict(_file_entry(home, f), title=first))
    exports = [_file_entry(home, f) for f in sorted((home / 'exports').glob('*'))] if (home / 'exports').is_dir() else []
    return {
        'brief': brief.read_text(encoding='utf-8') if brief.is_file() else '',
        'brief_template': BRIEF_TEMPLATE.format(name=gallery_name),
        'brand': _read_json(home / 'brand.json', {}),
        'assets': assets, 'references': refs, 'research': research, 'exports': exports,
        'categories': list(ASSET_CATEGORIES),
    }


def save_brief(home: Path, text: str) -> None:
    if len(text) > 200_000:
        raise WorkspaceError('brief grande demais')
    home.mkdir(parents=True, exist_ok=True)
    (home / 'brief.md').write_text(text, encoding='utf-8')


def save_brand(home: Path, data) -> dict:
    if not isinstance(data, dict):
        raise WorkspaceError('formato inválido')
    hexcolor = re.compile(r'^#[0-9a-fA-F]{6}$')
    colors = [c for c in data.get('colors', []) if isinstance(c, dict) and hexcolor.match(str(c.get('hex', '')))][:12]
    clean = {
        'name': str(data.get('name', ''))[:80],
        'tagline': str(data.get('tagline', ''))[:160],
        'colors': [{'name': str(c.get('name', ''))[:40], 'hex': c['hex'].lower()} for c in colors],
        'fonts': {'display': str(data.get('fonts', {}).get('display', ''))[:60],
                  'body': str(data.get('fonts', {}).get('body', ''))[:60]},
        'logo': str(data.get('logo', ''))[:200],
        'icon': str(data.get('icon', ''))[:200],
        'cta': str(data.get('cta', ''))[:160],
        'voice': [str(v)[:120] for v in data.get('voice', []) if str(v).strip()][:12],
        'avoid': [str(v)[:120] for v in data.get('avoid', []) if str(v).strip()][:12],
    }
    _write_json(home / 'brand.json', clean)
    return clean


def upload(home: Path, area: str, category: str, filename: str, stream, length: int, meta: dict) -> dict:
    if length <= 0 or length > MAX_UPLOAD:
        raise WorkspaceError('arquivo vazio ou maior que 500 MB')
    name = safe_filename(filename)
    if area == 'assets':
        category = category if category in ASSET_CATEGORIES else guess_category(name)
        folder = home / 'assets' / category
    elif area == 'references':
        folder = home / 'references' / 'files'
    else:
        raise WorkspaceError('área inválida')
    folder.mkdir(parents=True, exist_ok=True)
    target = unique_path(folder, name)
    left = length
    with target.open('wb') as fh:
        while left > 0:
            chunk = stream.read(min(1024 * 1024, left))
            if not chunk:
                break
            fh.write(chunk)
            left -= len(chunk)
    if left:
        target.unlink(missing_ok=True)
        raise WorkspaceError('envio interrompido')
    if area == 'references':
        return add_reference(home, {'type': 'file', 'title': meta.get('title') or Path(filename).stem,
                                    'source': target.relative_to(home).as_posix(), 'why': meta.get('why', ''),
                                    'tags': meta.get('tags', '')})
    return dict(_file_entry(home, target), category=category)


def add_reference(home: Path, data: dict) -> dict:
    kind = data.get('type')
    if kind not in ('link', 'file', 'text'):
        raise WorkspaceError('tipo de referência inválido')
    title = str(data.get('title', '')).strip()[:120]
    source = str(data.get('source', '')).strip()
    if kind == 'link' and not re.match(r'^https?://', source):
        raise WorkspaceError('o link precisa começar com http:// ou https://')
    index_path = home / 'references' / 'index.json'
    index = _read_json(index_path, [])
    ref_id = slugify(title or source, 'ref')
    while any(r['id'] == ref_id for r in index):
        ref_id += '-2'
    if kind == 'text':
        notes = home / 'references' / 'notes'
        notes.mkdir(parents=True, exist_ok=True)
        (notes / f'{ref_id}.md').write_text(source, encoding='utf-8')
        source = f'references/notes/{ref_id}.md'
    tags = data.get('tags', '')
    tags = [t.strip() for t in (tags.split(',') if isinstance(tags, str) else tags) if str(t).strip()][:10]
    entry = {'id': ref_id, 'type': kind, 'title': title or source[:80], 'source': source,
             'why': str(data.get('why', '')).strip()[:1000], 'tags': tags,
             'date': time.strftime('%Y-%m-%d'), 'analysis': ''}
    index.insert(0, entry)
    _write_json(index_path, index)
    return entry


def trash(home: Path, relpath: str) -> dict:
    target = (home / relpath).resolve()
    if not target.is_relative_to(home.resolve()) or not target.is_file():
        raise WorkspaceError('arquivo não encontrado')
    top = target.relative_to(home.resolve()).parts[0]
    if top not in ('assets', 'references', 'research', 'exports'):
        raise WorkspaceError('só arquivos de assets, referências, pesquisas ou exports')
    bin_dir = home / '.trash' / time.strftime('%Y%m%d')
    bin_dir.mkdir(parents=True, exist_ok=True)
    dest = unique_path(bin_dir, target.name)
    shutil.move(str(target), str(dest))
    index_path = home / 'references' / 'index.json'
    rel = target.relative_to(home.resolve()).as_posix()
    if top == 'references' and index_path.is_file():
        index = [r for r in _read_json(index_path, []) if r.get('source') != rel]
        _write_json(index_path, index)
    return {'ok': True, 'trash': dest.relative_to(home).as_posix()}


def remove_reference(home: Path, ref_id: str) -> dict:
    index_path = home / 'references' / 'index.json'
    index = _read_json(index_path, [])
    ref = next((r for r in index if r['id'] == ref_id), None)
    if not ref:
        raise WorkspaceError('referência não encontrada')
    if ref['type'] in ('file', 'text'):
        try:
            trash(home, ref['source'])
        except WorkspaceError:
            pass
    _write_json(index_path, [r for r in _read_json(index_path, []) if r['id'] != ref_id])
    return {'ok': True}
