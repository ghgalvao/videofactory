"""Live check of the tools the engine needs, with the command to fix each missing one."""
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path

from ..core.paths import ROOT

SOUND_CATALOG = ROOT / 'ferramentas' / 'sound-layer' / 'audio' / 'kit' / 'catalog.json'
HF_CACHE = Path.home() / '.cache' / 'huggingface' / 'hub'


def _version(cmd: list[str]) -> str:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        line = (out.stdout or out.stderr).strip().splitlines()
        return line[0][:80] if line else ''
    except (OSError, subprocess.SubprocessError):
        return ''


def _tool(tool_id: str, name: str, exe: str, args: list[str], fix: str, required: bool, use: str) -> dict:
    path = shutil.which(exe)
    return {'id': tool_id, 'name': name, 'ok': bool(path), 'required': required, 'use': use,
            'detail': _version([path, *args]) if path else 'não encontrado no PATH', 'fix': '' if path else fix}


def _whisper_models() -> list[str]:
    if not HF_CACHE.is_dir():
        return []
    return sorted(d.name.split('--')[-1] for d in HF_CACHE.iterdir() if 'whisper' in d.name.lower())


def _voicebox() -> dict:
    try:
        with urllib.request.urlopen('http://127.0.0.1:17493/health', timeout=0.8) as r:
            data = json.loads(r.read() or b'{}')
        gpu = 'com GPU' if data.get('gpu_available') else 'sem GPU (lento)'
        return {'ok': True, 'detail': f'app aberto, {gpu}'}
    except Exception:
        return {'ok': False, 'detail': 'app fechado ou não instalado'}


def check() -> list[dict]:
    items = [
        _tool('uv', 'uv (Python e dependências)', 'uv', ['--version'], 'winget install astral-sh.uv', True,
              'roda o motor: uv run vf ...'),
        _tool('ffmpeg', 'FFmpeg', 'ffmpeg', ['-version'], 'winget install Gyan.FFmpeg', True,
              'áudio, cortes e junção do vídeo'),
        _tool('node', 'Node.js', 'node', ['--version'], 'winget install OpenJS.NodeJS.LTS', True,
              'render dos templates (HyperFrames)'),
        _tool('pnpm', 'pnpm', 'pnpm', ['--version'], 'npm install -g pnpm', True,
              'instala o HyperFrames em video/'),
        _tool('git', 'Git', 'git', ['--version'], 'winget install Git.Git', False,
              'baixar e atualizar o motor (git pull)'),
        _tool('claude', 'Claude Code', 'claude', ['--version'], 'npm install -g @anthropic-ai/claude-code', False,
              'pedir vídeos em português; o CLAUDE.md guia o fluxo'),
    ]
    venv = (ROOT / '.venv').is_dir()
    items.append({'id': 'venv', 'name': 'Dependências Python do motor', 'ok': venv, 'required': True,
                  'use': 'Whisper, TTS e o CLI vf', 'detail': '.venv pronto' if venv else '.venv não existe',
                  'fix': '' if venv else 'uv sync'})
    nm = (ROOT / 'video' / 'node_modules').is_dir()
    items.append({'id': 'hyperframes', 'name': 'HyperFrames (render)', 'ok': nm, 'required': True,
                  'use': 'grava o MP4 a partir do template', 'detail': 'video/node_modules pronto' if nm else 'não instalado',
                  'fix': '' if nm else 'cd video; pnpm install; cd ..'})
    models = _whisper_models()
    items.append({'id': 'whisper', 'name': 'Modelo do Whisper', 'ok': bool(models), 'required': False,
                  'use': 'tempo de cada palavra (baixa sozinho na 1ª narração)',
                  'detail': ', '.join(models) if models else 'ainda não baixado: baixa na primeira narração',
                  'fix': ''})
    vb = _voicebox()
    items.append({'id': 'voicebox', 'name': 'Voicebox (voz própria)', 'ok': vb['ok'], 'required': False,
                  'use': '--engine voicebox: voz clonada com autorização ou desenhada', 'detail': vb['detail'],
                  'fix': '' if vb['ok'] else 'baixe em github.com/jamiepine/voicebox e deixe o app aberto'})
    kit = SOUND_CATALOG.is_file()
    count = 0
    if kit:
        try:
            data = json.loads(SOUND_CATALOG.read_text(encoding='utf-8'))
            count = len(data.get('sounds', data) if isinstance(data, dict) else data)
        except (OSError, json.JSONDecodeError):
            pass
    items.append({'id': 'soundkit', 'name': 'Biblioteca de efeitos sonoros', 'ok': kit, 'required': False,
                  'use': 'efeitos CC0 para mixar com a narração',
                  'detail': f'{count} sons' if kit else 'ainda não montada',
                  'fix': '' if kit else 'cd ferramentas/sound-layer; uv run scripts/sfx.py kit'})
    return items
