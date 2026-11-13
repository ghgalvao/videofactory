"""Style catalog for the panel: human names from each STYLE.md title, plus kind, status, format and an example."""
import re

from ..core.paths import ROOT
from ..estilos import ESTILOS

KIND = {'conteúdo': 'content', 'empresa': 'business'}
STATUS = {'testado': 'tested', 'pronto': 'ready', 'a criar': 'recipe'}
DETAIL_OVERRIDE = {'simple-caption': 'rascunho rápido'}  # STYLE.md titles that carry technical notes
EXTRA = []  # styles that live only as a template (no styles/<key>/ folder yet)


def _title(key: str) -> tuple[str, str]:
    recipe = ROOT / 'styles' / key / 'STYLE.md'
    if not recipe.is_file():
        return key, ''
    first = recipe.read_text(encoding='utf-8').splitlines()[0]
    title = re.sub(r'^#\s*STYLE\s*[—-]\s*', '', first).strip()
    m = re.match(r'^(.*?)\s*\((.*)\)\s*$', title)
    return (m.group(1), m.group(2)) if m else (title, '')


def _example(key: str) -> dict | None:
    folder = ROOT / 'styles' / key / 'exemplos'
    if not folder.is_dir():
        return None
    for d in sorted(folder.iterdir()):
        if (d / 'video.mp4').is_file():
            return {'name': d.name, 'video': f'{key}/exemplos/{d.name}/video.mp4'}
    return None


def catalog() -> list[dict]:
    out = []
    for key, kind, status, fmt, _template, _test, use in ESTILOS:
        name, detail = _title(key)
        detail = DETAIL_OVERRIDE.get(key, detail)
        out.append({'key': key, 'name': name, 'detail': detail, 'kind': KIND.get(kind, 'content'),
                    'status': STATUS.get(status, 'ready'), 'format': fmt, 'use': use,
                    'creatable': (ROOT / 'styles' / key / 'STYLE.md').is_file(), 'example': _example(key)})
    out += [dict(e, example=None) for e in EXTRA]
    return out
