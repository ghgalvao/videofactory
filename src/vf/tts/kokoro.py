"""Kokoro (82M, roda em CPU). pt-BR via espeak-ng.

Vozes pt-BR: pf_dora (feminina, padrão), pm_alex, pm_santa (masculinas).
Windows: instale o espeak-ng (MSI oficial). Caminho padrão: C:\\Program Files\\eSpeak NG.
"""
import os
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 24000
PAUSA = np.zeros(int(SR * 0.2), dtype=np.float32)  # silêncio entre trechos que o Kokoro separa
ESPEAK_DIR = Path(os.environ.get('VF_ESPEAK_DIR', r'C:\Program Files\eSpeak NG'))


def _espeak_do_sistema():
    """misaki sobrescreve lib/dados do espeak com o embutido (sem pt-br). Força o instalado."""
    lib = ESPEAK_DIR / 'libespeak-ng.dll'
    dados = ESPEAK_DIR / 'espeak-ng-data'
    if not (lib.exists() and dados.exists()):
        return
    from phonemizer.backend.espeak.wrapper import EspeakWrapper
    EspeakWrapper.set_library(str(lib))
    EspeakWrapper.set_data_path(str(dados))


class KokoroEngine:
    def __init__(self, voz: str):
        os.environ.setdefault('HF_HUB_DISABLE_SYMLINKS_WARNING', '1')
        from kokoro import KPipeline  # importar o misaki troca o espeak; corrigimos logo abaixo
        _espeak_do_sistema()
        self.voz = voz
        self._pipe = None
        self._KPipeline = KPipeline

    def _carregar(self):
        if self._pipe is None:
            self._pipe = self._KPipeline(lang_code='p')
        return self._pipe

    def preparar(self) -> None:
        self._carregar()

    def synthesize(self, text: str, out_wav: Path) -> int:
        pipe = self._carregar()
        partes = []
        for _, _, audio in pipe(text, voice=self.voz):
            partes.append(np.asarray(audio, dtype=np.float32))
            partes.append(PAUSA)
        if not partes:
            raise SystemExit('Kokoro não gerou áudio para o texto')
        sf.write(str(out_wav), np.concatenate(partes[:-1]), SR, subtype='PCM_16')
        return SR
