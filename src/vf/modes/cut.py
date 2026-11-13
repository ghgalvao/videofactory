"""Modo cut: vídeo existente → corte vertical legendado (portado de cortes.py)."""
from pathlib import Path

from ..core.faces import rastrear
from ..core.media import PAD, baixar, seg
from ..core.render import render
from ..core.subtitles import legenda
from ..core.transcribe import transcrever


def cortar(url, ini, fim, nome, a):
    pasta = Path(a.saida) / nome
    pasta.mkdir(parents=True, exist_ok=True)
    print(f'[{nome}] {ini:.1f}s -> {fim:.1f}s')
    video = baixar(url, ini, fim, pasta)
    t0 = min(PAD, ini); t1 = t0 + (fim - ini)  # posição do corte dentro do trecho baixado
    palavras = transcrever(video, pasta, a.modelo)
    ass = legenda(palavras, pasta, ini, fim, a.layout, a.titulo, a.subtitulo, a.refazer_legenda)
    cropx = rastrear(video, pasta, t0, t1, a.ignorar_canto) if a.layout == 'vertical' else None
    out = pasta / f'{nome}_{a.layout}.mp4'
    render(video, ass, out, t0, t1, a.layout, cropx)
    print(f'  pronto: {out}')


def executar(a):
    if a.lote:
        for ln in Path(a.lote).read_text(encoding='utf-8').splitlines():
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            ini, fim, nome = ln.split(maxsplit=2)
            cortar(a.fonte, seg(ini), seg(fim), nome.strip(), a)
    else:
        if not (a.inicio and a.fim and a.nome):
            raise SystemExit('cut: informe INICIO FIM --nome (ou --lote arquivo)')
        cortar(a.fonte, seg(a.inicio), seg(a.fim), a.nome, a)
