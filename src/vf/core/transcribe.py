"""Transcrição com faster-whisper (CPU, int8) → lista de palavras com tempo."""
import json
import os
import wave
from pathlib import Path

import numpy as np

from .media import run

_modelos = {}


def ler_wav(caminho) -> np.ndarray:
    """Lê wav PCM16 mono direto com `wave` (contorna PyAV incompatível com Python 3.14)."""
    with wave.open(str(caminho)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def transcrever(video: Path, pasta: Path, nome_modelo: str):
    """Palavras [{'s', 'e', 'w'}] do vídeo. Cache em pasta/whisper.json."""
    js = pasta / 'whisper.json'
    if js.exists():
        return json.loads(js.read_text(encoding='utf-8'))
    print('  transcrevendo...')
    wav = pasta / 'audio.wav'
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-ac', '1', '-ar', '16000', str(wav)])
    a = ler_wav(wav)
    os.environ.setdefault('HF_HUB_DISABLE_SYMLINKS_WARNING', '1')
    from faster_whisper import WhisperModel
    if nome_modelo not in _modelos:
        _modelos[nome_modelo] = WhisperModel(nome_modelo, device='cpu', compute_type='int8')
    segs, _ = _modelos[nome_modelo].transcribe(a, language='pt', word_timestamps=True, beam_size=5)
    palavras = [{'s': w.start, 'e': w.end, 'w': w.word.strip()} for s in segs for w in s.words if w.word.strip()]
    js.write_text(json.dumps(palavras, ensure_ascii=False), encoding='utf-8')
    wav.unlink(missing_ok=True)
    return palavras
