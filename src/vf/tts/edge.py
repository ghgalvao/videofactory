"""Edge TTS (vozes neurais da Microsoft, pt-BR). Usa serviço online não oficial: confira os termos de uso.

Vozes pt-BR masculinas: pt-BR-AntonioNeural. Femininas: pt-BR-FranciscaNeural, pt-BR-ThalitaMultilingualNeural.

Pausas: uma **linha em branco** no roteiro vira uma pausa de PAUSA_BLOCO s entre os blocos
(use antes do CTA e antes da virada do vídeo).
"""
import asyncio
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 24000
PAUSA_BLOCO = 0.7  # segundos de silêncio entre blocos separados por linha em branco


class EdgeEngine:
    def __init__(self, voz: str, taxa: str = '+15%'):
        self.voz = voz
        import os
        self.taxa = os.environ.get('VF_TAXA', taxa)

    def preparar(self) -> None:
        import edge_tts  # noqa: F401  (só confere que está instalado)

    def _bloco(self, texto: str, wav: Path):
        import edge_tts

        async def gerar(mp3: str):
            await edge_tts.Communicate(texto, self.voz, rate=self.taxa).save(mp3)

        with tempfile.TemporaryDirectory() as tmp:
            mp3 = str(Path(tmp) / 'voz.mp3')
            asyncio.run(gerar(mp3))
            # wav PCM16 mono 24 kHz: formato que o resto do pipeline espera
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-ac', '1', '-ar', str(SR),
                            '-c:a', 'pcm_s16le', str(wav)], check=True)

    def synthesize(self, text: str, out_wav: Path) -> int:
        blocos = [b.strip() for b in re.split(r'\n\s*\n', text) if b.strip()]
        if len(blocos) <= 1:
            self._bloco(' '.join(text.split()), out_wav)
            return SR
        partes = []
        with tempfile.TemporaryDirectory() as tmp:
            for i, b in enumerate(blocos):
                w = Path(tmp) / f'b{i}.wav'
                self._bloco(' '.join(b.split()), w)
                audio, _ = sf.read(str(w), dtype='float32')
                partes.append(audio)
                if i < len(blocos) - 1:
                    partes.append(np.zeros(int(SR * PAUSA_BLOCO), dtype='float32'))
        sf.write(str(out_wav), np.concatenate(partes), SR, subtype='PCM_16')
        return SR
