"""Reads the engine's Claude Code skills (.claude/skills/*/SKILL.md) so the panel can document them."""
import re

from ..core.paths import ROOT

SKILLS_DIR = ROOT / '.claude' / 'skills'
ORDER = ['vf-video', 'vf-script', 'vf-adjust', 'vf-batch', 'vf-research', 'vf-reference', 'vf-voice', 'vf-sound', 'vf-avatar']
SECTIONS = {'Quando usar': 'when', 'Como usar': 'usage', 'O que faz': 'steps', 'Entrega': 'output', 'Regras': 'rules'}


def _frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            meta[key.strip()] = value.strip().strip('"')
    return meta, text[m.end():]


def read_skills() -> list[dict]:
    if not SKILLS_DIR.is_dir():
        return []
    skills = []
    for path in SKILLS_DIR.glob('*/SKILL.md'):
        meta, body = _frontmatter(path.read_text(encoding='utf-8'))
        item = {'name': meta.get('name', path.parent.name), 'description': meta.get('description', ''),
                'args': meta.get('argument-hint', ''), 'path': path.relative_to(ROOT).as_posix()}
        for title, key in SECTIONS.items():
            m = re.search(rf'^## {re.escape(title)}\s*\n(.*?)(?=^## |\Z)', body, re.S | re.M)
            item[key] = m.group(1).strip() if m else ''
        usage = re.search(r'```\w*\n(.*?)```', item['usage'], re.S)
        item['examples'] = [l for l in usage.group(1).splitlines() if l.strip()] if usage else []
        skills.append(item)
    rank = {n: i for i, n in enumerate(ORDER)}
    skills.sort(key=lambda s: (rank.get(s['name'], 99), s['name']))
    return skills
