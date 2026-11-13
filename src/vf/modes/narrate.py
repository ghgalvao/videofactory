"""Modo narrate: roteiro.txt → narração (TTS) → tempos por palavra → vídeo vertical legendado.

Saídas organizadas por etapa (ver core/paths.py): entrada em 1-entrada/, vídeo em 3-final/, resto em _interno/.
"""
import json
import shutil
import time
from pathlib import Path

import soundfile as sf

from ..core import hyperframes as hf
from ..core import legenda_dinamica as ld
from ..core.paths import Job
from ..core.render import render_fundo
from ..core.subtitles import legenda
from ..core.timing import alinhar
from ..core.transcribe import transcrever
from ..tts.base import criar


def _etapa(nome, tempos, fn, *a, **kw):
    t = time.perf_counter()
    r = fn(*a, **kw)
    tempos[nome] = round(time.perf_counter() - t, 2)
    return r


def executar(a):
    origem = Path(a.roteiro)
    nome = a.nome or origem.stem
    job = Job(a.saida, nome).criar()
    if origem.resolve() != job.roteiro.resolve():  # guarda uma cópia do roteiro na entrada do job
        shutil.copyfile(origem, job.roteiro)
    texto = job.roteiro.read_text(encoding='utf-8').strip()
    if not texto:
        raise SystemExit('narrate: roteiro vazio')
    wav, words, video = job.wav, job.words, job.video_tmp
    tempos = {}
    print(f'[{nome}] roteiro: {len(texto.split())} palavras')

    if not wav.exists() or a.refazer:
        import os
        if (job.entrada / 'direcao_audio.json').exists():  # direção de áudio do job (tom/pausa/velocidade por frase)
            os.environ['VF_DIRECAO_AUDIO'] = str(job.entrada / 'direcao_audio.json')
        os.environ['VF_VOZ_CACHE'] = str(job.interno / 'voz-cache')  # frase já gerada não é gerada de novo
        motor = criar(a.engine, a.voz)
        _etapa('carregar_tts', tempos, motor.preparar)
        _etapa('narrar', tempos, motor.synthesize, texto, wav)
        (job.interno / 'whisper.json').unlink(missing_ok=True)  # narração nova invalida o cache do Whisper
        words.unlink(missing_ok=True)
        print(f'  narração: {wav}')

    if not words.exists() or a.refazer:
        palavras = _etapa('transcrever', tempos, transcrever, wav, job.interno, a.modelo)
        alinhadas, interp = _etapa('alinhar', tempos, alinhar, texto, palavras)
        words.write_text(json.dumps(alinhadas, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'  words.json: {len(alinhadas)} palavras ({interp} interpoladas)')
    else:
        alinhadas = json.loads(words.read_text(encoding='utf-8'))

    dur = sf.info(str(wav)).duration
    if a.renderer == 'hyperframes':
        _etapa('render_hyperframes', tempos, hf.renderizar, alinhadas, dur, wav, video)
    elif a.renderer == 'dinamico':
        pagina = ld.gerar_html(alinhadas, dur, ld.carregar_config(job.roteiro.parent))
        _etapa('render_hyperframes', tempos, hf.renderizar, alinhadas, dur, wav, video, html=pagina)
    else:
        palavras_ass = [{'s': w['start'], 'e': w['end'], 'w': w['word']} for w in alinhadas]
        ass = _etapa('render_ass', tempos, legenda, palavras_ass, job.interno, 0.0, dur, 'vertical', '', '', True)
        _etapa('render_video', tempos, render_fundo, wav, ass, video, dur)
    print(f'  pronto: {job.publicar()}')
    print('  tempos (s): ' + json.dumps(tempos, ensure_ascii=False))
    return tempos
