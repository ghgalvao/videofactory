"""Task queue for the panel: runs the engine's own commands, one at a time, with a live log.

Only a fixed set of actions is allowed, each mapped to a `vf` command, and only for jobs inside saida/.
Arguments are passed as a list (no shell), so job names and options cannot inject commands.
"""
import collections
import itertools
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

from ..core.paths import ENTRADA, ROOT, SAIDA_PADRAO, Job

ENGINES = ('edge', 'kokoro', 'voicebox')
JOB_NAME = re.compile(r'^[a-z0-9][a-z0-9-]{0,60}(/[a-z0-9][a-z0-9-]{0,60}){0,3}$')
MAX_LOG = 2000
ACTION_LABELS = {'new': 'criar job', 'narrate': 'narrar', 'check': 'checar', 'sheet': 'gerar folha', 'render': 'animar'}


class TaskError(ValueError):
    pass


def available_styles() -> list[str]:
    return sorted(d.name for d in (ROOT / 'styles').iterdir() if (d / 'STYLE.md').is_file())


def _job_dir(name: str) -> Path:
    if not JOB_NAME.match(name or ''):
        raise TaskError('nome de job inválido: use letras minúsculas, números, hífen e / para subpasta')
    target = (SAIDA_PADRAO / name).resolve()
    if not target.is_relative_to(SAIDA_PADRAO.resolve()):
        raise TaskError('o job precisa ficar dentro de saida/')
    return target


def build_command(action: str, job: str, options: dict) -> list[str]:
    base = [sys.executable, '-m', 'vf']
    target = _job_dir(job)
    if action == 'new':
        style = str(options.get('style', ''))
        if style not in available_styles():
            raise TaskError(f'estilo desconhecido: {style}')
        if (target / ENTRADA).exists():
            raise TaskError(f'o job {job} já existe')
        return base + ['novo', style, job]
    j = Job(SAIDA_PADRAO, job)
    if not (j.entrada.is_dir() or j.final.is_dir()):
        raise TaskError(f'job não encontrado: {job}')
    if action == 'narrate':
        if not j.roteiro.is_file():
            raise TaskError('o job não tem 1-entrada/roteiro.txt')
        engine = str(options.get('engine', 'edge'))
        if engine not in ENGINES:
            raise TaskError(f'motor de voz inválido: {engine}')
        cmd = base + ['narrate', str(j.roteiro.relative_to(ROOT).as_posix()), '--nome', job,
                      '--engine', engine, '--modelo', 'small']
        voice = str(options.get('voice', '')).strip()
        if voice:
            if len(voice) > 80 or any(c in voice for c in '\r\n\0'):
                raise TaskError('nome de voz inválido')
            cmd += ['--voz', voice]
        elif engine == 'voicebox':
            raise TaskError('informe o perfil de voz do Voicebox')
        if j.wav.exists():
            cmd.append('--refazer')
        return cmd
    if action in ('check', 'sheet', 'render'):
        if not (j.wav.is_file() and j.words.is_file()):
            raise TaskError('narre o job antes')
        if not j.storyboard.is_file():
            raise TaskError('o job não tem 1-entrada/storyboard.json')
        if action == 'check':
            return base + ['checar', job]
        if action == 'sheet':
            return base + ['storyboard', job]
        if not j.folha.is_file():
            raise TaskError('gere e aprove a folha antes de animar')
        return base + ['storyboard', job, '--animar']
    raise TaskError(f'ação desconhecida: {action}')


class TaskQueue:
    def __init__(self):
        self._ids = itertools.count(1)
        self._lock = threading.Lock()
        self._wake = threading.Event()
        self.tasks: collections.OrderedDict[int, dict] = collections.OrderedDict()
        self._proc: subprocess.Popen | None = None
        threading.Thread(target=self._worker, daemon=True).start()

    def submit(self, action: str, job: str, options: dict) -> dict:
        cmd = build_command(action, job, options or {})
        with self._lock:
            busy = [t for t in self.tasks.values() if t['job'] == job and t['status'] in ('queued', 'running')]
            if busy:
                raise TaskError(f'o job {job} já tem uma tarefa na fila')
            task = {'id': next(self._ids), 'action': action, 'label': ACTION_LABELS[action], 'job': job,
                    'status': 'queued', 'command': ' '.join(['vf'] + cmd[3:]), 'log': [], 'code': None,
                    'created': time.time(), 'started': None, 'ended': None, '_cmd': cmd}
            self.tasks[task['id']] = task
            while len(self.tasks) > 100:
                oldest = next(iter(self.tasks.values()))
                if oldest['status'] in ('queued', 'running'):
                    break
                self.tasks.popitem(last=False)
        self._wake.set()
        return self.public(task)

    def cancel(self, task_id: int) -> dict:
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                raise TaskError('tarefa não existe')
            if task['status'] == 'queued':
                task['status'] = 'cancelled'
                task['ended'] = time.time()
            elif task['status'] == 'running' and self._proc:
                task['status'] = 'cancelling'
                _kill_tree(self._proc)
        return self.public(task)

    def public(self, task: dict, since: int = 0) -> dict:
        out = {k: v for k, v in task.items() if not k.startswith('_') and k != 'log'}
        out['log'] = task['log'][since:]
        out['log_size'] = len(task['log'])
        return out

    def listing(self) -> list[dict]:
        with self._lock:
            return [self.public(t, max(len(t['log']) - 3, 0)) for t in reversed(self.tasks.values())]

    def _next(self) -> dict | None:
        with self._lock:
            for t in self.tasks.values():
                if t['status'] == 'queued':
                    t['status'] = 'running'
                    t['started'] = time.time()
                    return t
        return None

    def _worker(self):
        while True:
            task = self._next()
            if not task:
                self._wake.wait()
                self._wake.clear()
                continue
            env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUNBUFFERED='1')
            try:
                self._proc = subprocess.Popen(task['_cmd'], cwd=str(ROOT), env=env, stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
                for line in self._proc.stdout:
                    line = line.rstrip()
                    if line:
                        task['log'].append(line[:500])
                        if len(task['log']) > MAX_LOG:
                            del task['log'][:200]
                code = self._proc.wait()
            except OSError as e:
                task['log'].append(f'erro ao iniciar: {e}')
                code = -1
            finally:
                self._proc = None
            with self._lock:
                task['code'] = code
                task['ended'] = time.time()
                task['status'] = 'cancelled' if task['status'] == 'cancelling' else ('done' if code == 0 else 'failed')


def _kill_tree(proc: subprocess.Popen) -> None:
    if sys.platform == 'win32':
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(proc.pid)], capture_output=True)
    else:
        proc.terminate()
