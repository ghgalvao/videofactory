"""Interface de motor de TTS. Trocar de motor = novo arquivo que implementa `synthesize`."""
from pathlib import Path
from typing import Protocol


class TTSEngine(Protocol):
    def preparar(self) -> None:
        """Carrega o modelo (separado para medir o custo de carga)."""
        ...

    def synthesize(self, text: str, out_wav: Path) -> int:
        """Grava `text` falado em `out_wav` (PCM16 mono). Retorna o sample rate."""
        ...


def criar(nome: str, voz: str | None = None) -> TTSEngine:
    if nome == 'kokoro':
        from .kokoro import KokoroEngine
        return KokoroEngine(voz or 'pf_dora')
    if nome == 'edge':
        from .edge import EdgeEngine
        return EdgeEngine(voz or 'pt-BR-AntonioNeural')
    if nome == 'voicebox':
        from .voicebox import VoiceboxEngine
        return VoiceboxEngine(voz)
    raise SystemExit(f'motor de TTS desconhecido: {nome} (disponíveis: kokoro, edge, voicebox)')
