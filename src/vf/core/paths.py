"""Caminhos do projeto e organização de um job (pasta de um vídeo).

saida/<job>/
  1-entrada/   o que define o vídeo e pode ser editado: roteiro.txt, direcao.md, storyboard.json, imagens/
  2-aprovar/   o que você precisa olhar e aprovar: storyboard_folha.png
  3-final/     o que sai para publicar: video.mp4 (capa e legenda quando existirem)
  _interno/    uso do sistema: narration.wav, words.json, whisper.json, legenda.ass, quadros, temporários
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # videoFactory/
MODELS = ROOT / 'models'
SAIDA_PADRAO = ROOT / 'saida'

ENTRADA, APROVAR, FINAL, INTERNO = '1-entrada', '2-aprovar', '3-final', '_interno'


class Job:
    """Caminhos de um job. `nome` pode ter subpastas (ex.: 'cliente/b1-apresentacao')."""

    def __init__(self, saida, nome: str):
        self.nome = nome
        self.raiz = Path(saida) / nome
        self.entrada = self.raiz / ENTRADA
        self.aprovar = self.raiz / APROVAR
        self.final = self.raiz / FINAL
        self.interno = self.raiz / INTERNO

    def criar(self):
        for p in (self.entrada, self.aprovar, self.final, self.interno):
            p.mkdir(parents=True, exist_ok=True)
        return self

    # entrada
    @property
    def roteiro(self): return self.entrada / 'roteiro.txt'
    @property
    def storyboard(self): return self.entrada / 'storyboard.json'
    # aprovar
    @property
    def folha(self): return self.aprovar / 'storyboard_folha.png'
    # final
    @property
    def video_final(self): return self.final / 'video.mp4'
    # interno
    @property
    def wav(self): return self.interno / 'narration.wav'
    @property
    def words(self): return self.interno / 'words.json'
    @property
    def quadros(self): return self.interno / 'storyboard_quadros'
    @property
    def video_tmp(self): return self.interno / 'video.mp4'  # render escreve aqui; depois vai para 3-final

    def publicar(self):
        """Move o render de _interno para 3-final e limpa temporários do HyperFrames."""
        self.final.mkdir(parents=True, exist_ok=True)
        shutil.move(str(self.video_tmp), str(self.video_final))
        for t in self.interno.glob('.video.hf-transaction*'):
            shutil.rmtree(t, ignore_errors=True)
        return self.video_final
