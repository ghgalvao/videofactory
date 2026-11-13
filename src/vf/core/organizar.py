"""Migra jobs antigos (arquivos soltos) para a estrutura por etapa: 1-entrada, 2-aprovar, 3-final, _interno."""
import shutil
from pathlib import Path

from .paths import APROVAR, ENTRADA, FINAL, INTERNO

ENTRADA_ARQ = {'roteiro.txt', 'direcao.md', 'storyboard.json', 'storyboard.md'}
ENTRADA_DIR = {'imagens'}
APROVAR_ARQ = {'storyboard_folha.png'}
FINAL_ARQ = {'video.mp4', 'video_ass.mp4'}
MARCADORES = ENTRADA_ARQ | {'words.json', 'video.mp4', 'narration.wav'}  # arquivos que identificam uma pasta de job
PASTAS_NOVAS = {ENTRADA, APROVAR, FINAL, INTERNO}


def eh_job(p: Path) -> bool:
    return p.is_dir() and p.name not in PASTAS_NOVAS and any((p / m).exists() for m in MARCADORES)


def jobs_em(saida: Path) -> list[Path]:
    achados = []
    for p in sorted(saida.rglob('*')):
        if p.is_dir() and eh_job(p) and not any(x in PASTAS_NOVAS for x in p.relative_to(saida).parts):
            achados.append(p)
    return achados


def destino(p: Path, job: Path) -> Path | None:
    nome = p.name
    if nome in PASTAS_NOVAS:
        return None
    if p.is_dir():
        if nome.startswith('.video.hf-transaction'):
            return Path('__apagar__')
        return job / (ENTRADA if nome in ENTRADA_DIR else INTERNO) / nome
    if nome in ENTRADA_ARQ:
        return job / ENTRADA / nome
    if nome in APROVAR_ARQ:
        return job / APROVAR / nome
    if nome in FINAL_ARQ:
        return job / FINAL / nome
    return job / INTERNO / nome


def organizar(job: Path, simular: bool = False) -> list[str]:
    """Retorna a lista de movimentos. Não mexe em job já organizado."""
    if (job / ENTRADA).exists():
        return []
    mov = []
    for p in sorted(job.iterdir()):
        d = destino(p, job)
        if d is None:
            continue
        if d.name == '__apagar__':
            mov.append(f'apagar  {p.name}')
            if not simular:
                shutil.rmtree(p, ignore_errors=True)
            continue
        mov.append(f'{p.name:34} -> {d.parent.name}/')
        if not simular:
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(d))
    if not simular:
        for pasta in (ENTRADA, APROVAR, FINAL, INTERNO):
            (job / pasta).mkdir(exist_ok=True)
    return mov
