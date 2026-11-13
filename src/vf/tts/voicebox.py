"""Voicebox (app local de voz, github.com/jamiepine/voicebox) via API REST em 127.0.0.1:17493.

Usa um perfil de voz criado no app (clonado, pronto ou desenhado). `--voz` = nome do perfil (ou o começo dele) ou o id.
Variáveis opcionais: VF_VOICEBOX_URL (padrão http://127.0.0.1:17493), VF_VOICEBOX_ENGINE (qwen | chatterbox | ...,
padrão: motor padrão do perfil ou qwen), VF_VOICEBOX_MODELO (0.6B | 1.7B, padrão 0.6B).

Pausas: igual ao Edge, uma **linha em branco** no roteiro vira PAUSA_BLOCO s de silêncio.

Direção de áudio (opcional): VF_DIRECAO_AUDIO aponta para um JSON (o narrate usa 1-entrada/direcao_audio.json):
  {"padrao": {"tom": "referencia"}, "tons": {"persuasivo": "voz-persuasivo", ...},
   "frases": {"1": {"tom": "persuasivo", "pausa": 0.5, "vel": 1.05}, ...}}
A frase N é contada como no storyboard (termina em . ? !). "tom" escolhe o perfil (a instrução de tom do
Qwen não funciona com voz clonada: testado em 08/11/2026). "pausa" = silêncio depois (s); "vel" = velocidade (atempo).
VF_VOICEBOX_SEED fixa a semente (padrão 7) para a voz ficar igual entre frases.
Cache: VF_VOZ_CACHE (o narrate usa _interno/voz-cache) guarda cada trecho gerado, com chave em texto + perfil +
motor + modelo + semente. Mudou uma frase do roteiro? Só ela é gerada de novo; pausa e velocidade não regeram.
Só use voz clonada de quem autorizou por escrito.
"""
import hashlib
import json
import shutil
import os
import re
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 24000
PAUSA_BLOCO = 0.7      # linha em branco no roteiro
PAUSA_PONTO = 0.28     # fim de frase
PAUSA_PERGUNTA = 0.40  # depois de pergunta
PAUSA_VIRGULA = 0.12   # frase longa quebrada na vírgula


def _req(url: str, dados: dict | None = None, timeout: int = 60):
    corpo = json.dumps(dados).encode('utf-8') if dados is not None else None
    r = urllib.request.Request(url, data=corpo, method='POST' if dados is not None else 'GET',
                               headers={'Content-Type': 'application/json'} if dados is not None else {})
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return resp.read()


class VoiceboxEngine:
    def __init__(self, voz: str | None):
        self.base = os.environ.get('VF_VOICEBOX_URL', 'http://127.0.0.1:17493').rstrip('/')
        self.voz = voz
        self.modelo = os.environ.get('VF_VOICEBOX_MODELO', '1.7B')
        self.seed = int(os.environ.get('VF_VOICEBOX_SEED', '7'))
        self.direcao = {}
        self.perfis = []
        self.engine = os.environ.get('VF_VOICEBOX_ENGINE')
        self.perfil = None
        self.reaproveitados = 0

    def preparar(self) -> None:
        try:
            perfis = json.loads(_req(self.base + '/profiles'))
        except Exception as e:
            raise SystemExit(f'voicebox: API fora do ar em {self.base} (abra o app Voicebox). {e}')
        if isinstance(perfis, dict):
            perfis = perfis.get('items') or perfis.get('profiles') or []
        self.perfis = perfis
        dp = os.environ.get('VF_DIRECAO_AUDIO')
        if dp and Path(dp).exists():
            self.direcao = json.loads(Path(dp).read_text(encoding='utf-8'))
            print(f'  voicebox: direção de áudio {dp}')
        alvo = (self.voz or '').lower()
        for p in perfis:
            if p.get('id') == self.voz or (alvo and p.get('name', '').lower().startswith(alvo)):
                self.perfil = p
                break
        if not self.perfil:
            nomes = ', '.join(p.get('name', '?') for p in perfis)
            raise SystemExit(f'voicebox: perfil "{self.voz}" não encontrado. Perfis: {nomes}')
        self.engine = self.engine or self.perfil.get('default_engine') or 'qwen'
        saude = json.loads(_req(self.base + '/health'))
        print(f'  voicebox: perfil "{self.perfil["name"]}", motor {self.engine} {self.modelo}, '
              f'{"GPU" if saude.get("gpu_available") else "CPU (lento)"}')

    def _perfil_do_tom(self, tom: str | None) -> str:
        if not tom or tom == 'referencia':
            return self.perfil['id']
        nome = (self.direcao.get('tons', {}).get(tom) or tom).lower()
        for p in self.perfis:
            if p.get('name', '').lower().startswith(nome):
                return p['id']
        raise SystemExit(f'voicebox: tom "{tom}" sem perfil (procurei "{nome}")')

    def _bloco(self, texto: str, wav: Path, perfil_id: str | None = None):
        pid = perfil_id or self.perfil['id']
        cache = os.environ.get('VF_VOZ_CACHE')
        if cache:
            chave = hashlib.sha1(f'{texto}|{pid}|{self.engine}|{self.modelo}|{self.seed}'.encode('utf-8')).hexdigest()[:16]
            guardado = Path(cache) / f'{chave}.wav'
            if guardado.exists():
                self.reaproveitados += 1
                shutil.copyfile(guardado, wav)
                return
        self._gerar(texto, wav, pid)
        if cache:
            guardado.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(wav, guardado)

    def _gerar(self, texto: str, wav: Path, pid: str):
        g = json.loads(_req(self.base + '/generate', {
            'profile_id': pid, 'text': texto, 'language': 'pt', 'seed': self.seed,
            'engine': self.engine, 'model_size': self.modelo}, timeout=120))
        gid = g.get('id') or g.get('generation_id')
        # o status vem como stream de eventos (text/event-stream) até a geração terminar
        fim = False
        while not fim:
            with urllib.request.urlopen(f'{self.base}/generate/{gid}/status', timeout=900) as resp:
                for linha in resp:
                    linha = linha.decode('utf-8', 'replace').strip()
                    if not linha.startswith('data:'):
                        continue
                    st = json.loads(linha[5:])
                    estado = str(st.get('status', '')).lower()
                    if estado in ('completed', 'complete', 'done', 'success'):
                        fim = True
                        break
                    if estado in ('failed', 'error', 'cancelled'):
                        raise SystemExit(f'voicebox: geração falhou: {st}')
            if not fim:
                time.sleep(1)
        with tempfile.TemporaryDirectory() as tmp:
            bruto = Path(tmp) / 'voz.bin'
            bruto.write_bytes(_req(f'{self.base}/audio/{gid}', timeout=120))
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(bruto), '-ac', '1', '-ar', str(SR),
                            '-c:a', 'pcm_s16le', str(wav)], check=True)

    @staticmethod
    def _limpar(t: str) -> str:
        """Pontuação que o modelo lê mal vira pontuação simples."""
        t = re.sub(r'\s*[—–]\s*', ', ', t)            # travessão vira vírgula
        t = re.sub(r'[()\[\]"“”«»]', '', t)            # parênteses e aspas somem
        t = t.replace('...', '.').replace('…', '.')
        t = re.sub(r'\s*;\s*', ', ', t)
        t = re.sub(r'\s*:\s*', '. ', t)                 # dois-pontos vira fim de frase
        return ' '.join(t.split())

    @staticmethod
    def _frases(bloco: str) -> list[tuple[str, float]]:
        """Divide em frases (e frases longas nas vírgulas). Retorna (texto, pausa depois em s)."""
        out = []
        for f in re.findall(r'[^.!?]+[.!?]?', bloco):
            f = f.strip()
            if not f:
                continue
            fim = f[-1] if f[-1] in '.!?' else '.'
            pedacos = [f] if len(f) <= 140 else [p.strip() for p in re.split(r',\s*', f) if p.strip()]
            for k, p in enumerate(pedacos):
                if k < len(pedacos) - 1:
                    out.append((p.rstrip(',') + ',', PAUSA_VIRGULA))
                else:
                    if p[-1] not in '.!?':
                        p += fim
                    out.append((p, PAUSA_PERGUNTA if fim == '?' else PAUSA_PONTO))
        return out

    def synthesize(self, text: str, out_wav: Path) -> int:
        blocos = [b for b in re.split(r'\n\s*\n', text) if b.strip()]
        conf = self.direcao.get('frases', {})
        padrao = self.direcao.get('padrao', {})
        partes, n, k = [], 0, 0
        with tempfile.TemporaryDirectory() as tmp:
            for i, bloco in enumerate(blocos):
                frases = [f.strip() for f in re.findall(r'[^.!?]+[.!?]?', ' '.join(bloco.split())) if f.strip()]
                for j, frase in enumerate(frases):
                    n += 1                                        # frase N, igual ao storyboard
                    d = {**padrao, **conf.get(str(n), {})}
                    pid = self._perfil_do_tom(d.get('tom'))
                    pedacos = self._frases(self._limpar(frase))
                    for m, (pedaco, pausa_int) in enumerate(pedacos):
                        w = Path(tmp) / f'p{k}.wav'; k += 1
                        self._bloco(pedaco, w, pid)
                        if d.get('vel') and abs(d['vel'] - 1) > 0.01:
                            w2 = Path(tmp) / f'v{k}.wav'
                            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(w), '-filter:a', f'atempo={d["vel"]}', str(w2)], check=True)
                            w = w2
                        audio, _ = sf.read(str(w), dtype='float32')
                        partes.append(_aparar(audio))
                        if m < len(pedacos) - 1:
                            partes.append(np.zeros(int(SR * pausa_int), dtype='float32'))
                    ultima = j == len(frases) - 1
                    if ultima and i == len(blocos) - 1:
                        break
                    base = PAUSA_BLOCO if ultima else (PAUSA_PERGUNTA if frase.endswith('?') else PAUSA_PONTO)
                    partes.append(np.zeros(int(SR * d.get('pausa', base)), dtype='float32'))
                    print(f'    frase {n} ok ({d.get("tom", "referencia")})', flush=True)
        sf.write(str(out_wav), np.concatenate(partes), SR, subtype='PCM_16')
        if self.reaproveitados:
            print(f'    cache: {self.reaproveitados} trecho(s) reaproveitado(s)', flush=True)
        return SR

def _aparar(a: np.ndarray, limiar: float = 0.01) -> np.ndarray:
    """Tira o silêncio do começo e do fim de cada frase (as pausas quem controla somos nós)."""
    idx = np.where(np.abs(a) > limiar)[0]
    if len(idx) == 0:
        return a
    ini, fim = max(idx[0] - int(0.02 * SR), 0), min(idx[-1] + int(0.06 * SR), len(a))
    return a[ini:fim]
