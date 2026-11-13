"""Render ffmpeg: layout vertical (câmera virtual) e desfocado, com legenda .ass e loudnorm."""
import subprocess
import sys
from pathlib import Path

import cv2

from .media import abrir

AUDIO = ['-c:a', 'aac', '-b:a', '160k', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-movflags', '+faststart']
VIDEO = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p']


def render_fundo(audio: Path, ass: Path, out: Path, dur: float, cor='0x0E1116'):
    """Fundo sólido 1080x1920 + narração + legenda .ass (modo narrate)."""
    print('  renderizando (fundo + legenda)...')
    cwd = ass.parent
    subprocess.run(['ffmpeg', '-v', 'error', '-y',
                    '-f', 'lavfi', '-i', f'color=c={cor}:s=1080x1920:r=30:d={dur:.3f}',
                    '-i', audio.name,
                    '-filter_complex', f'[0:v]subtitles={ass.name}[v]', '-map', '[v]', '-map', '1:a',
                    *VIDEO, *AUDIO, '-t', f'{dur:.3f}', out.name], cwd=cwd, check=True)


def render(video: Path, ass: Path, out: Path, t0, t1, layout, cropx):
    print('  renderizando...')
    sub = f"subtitles={ass.name}"  # roda com cwd na pasta do corte (caminho do Windows quebra o filtro)
    cwd = ass.parent
    if layout == 'desfocado':
        fc = ('[0:v]fps=30,split=2[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=28:2,eq=brightness=-0.22:saturation=0.8[bg];'
              f'[b]scale=1296:-2,crop=1080:ih[fg];[bg][fg]overlay=0:495,{sub}[v]')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-to', str(t1), '-i', video.name,
                        '-filter_complex', fc, '-map', '[v]', '-map', '0:a', *VIDEO, *AUDIO, out.name], cwd=cwd, check=True)
        return
    cap = abrir(video); fps = cap.get(cv2.CAP_PROP_FPS); H = int(cap.get(4)); CW = round(H * 9 / 16)
    cap.set(cv2.CAP_PROP_POS_MSEC, t0 * 1000)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1080x1920',
                           '-r', f'{fps}', '-i', '-', '-ss', str(t0), '-to', str(t1), '-i', video.name,
                           '-filter_complex', f'[0:v]unsharp=5:5:0.6:5:5:0,{sub}[v]', '-map', '[v]', '-map', '1:a',
                           *VIDEO, *AUDIO, '-shortest', out.name], stdin=subprocess.PIPE, cwd=cwd)
    for x in cropx:
        ok, img = cap.read()
        if not ok:
            break
        x0 = int(round(x))
        ff.stdin.write(cv2.resize(img[:, x0:x0 + CW], (1080, 1920), interpolation=cv2.INTER_LANCZOS4).tobytes())
    ff.stdin.close(); ff.wait()
    if ff.returncode:
        sys.exit('ffmpeg falhou no render')
