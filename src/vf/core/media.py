"""Utilitários de mídia: tempo, subprocess, download/recorte do trecho, abertura de vídeo."""
import subprocess
import sys
from pathlib import Path

import cv2

PAD = 1.0  # folga baixada antes/depois (keyframes); o corte real usa INICIO/FIM exatos


def seg(s: str) -> float:
    p = [float(x) for x in s.replace(',', '.').split(':')]
    return p[0] if len(p) == 1 else p[0] * 60 + p[1] if len(p) == 2 else p[0] * 3600 + p[1] * 60 + p[2]


def ts(x):
    """Segundos → timestamp ASS (h:mm:ss.cc)."""
    x = max(0.0, x)
    return f'{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}'


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        sys.exit(f'falhou: {cmd[0]} {cmd[1] if len(cmd) > 1 else ""}\n{r.stderr[-1500:]}')
    return r


def baixar(url, ini, fim, pasta: Path) -> Path:
    """Trecho [ini-PAD, fim+PAD] em pasta/trecho.mp4. Arquivo local é recortado; URL via yt-dlp."""
    out = pasta / 'trecho.mp4'
    if out.exists():
        return out
    if Path(url).is_file():  # arquivo local: só recorta (reencoda pra o corte cair no quadro exato)
        print('  recortando do arquivo local...')
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(max(0, ini - PAD)), '-to', str(fim + PAD), '-i', url,
             '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-c:a', 'aac', '-b:a', '192k', str(out)])
        return out
    print('  baixando trecho...')
    run([sys.executable, '-m', 'yt_dlp', '--no-warnings', '--js-runtimes', 'node',
         '-f', 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/bv*[height<=1080]+ba/b', '--merge-output-format', 'mp4',
         '--download-sections', f'*{max(0, ini - PAD)}-{fim + PAD}', '--force-keyframes-at-cuts',
         '-o', str(out), url])
    return out


def abrir(video: Path):
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        sys.exit(f'OpenCV não abriu {video} (caminho com acento?)')
    return cap
