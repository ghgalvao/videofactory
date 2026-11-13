"""Renderizador HyperFrames (opcional): gera a composição vertical a partir de words.json e renderiza MP4.

O projeto HyperFrames fica em video/. A cada render, index.html e narration.wav são
sobrescritos; por isso um render por vez (CLI, não paralelo).
"""
import html
import shutil
import subprocess
import sys
from pathlib import Path

from .paths import ROOT
from .subtitles import agrupar

VIDEO = ROOT / 'video'
TEMPLATE = VIDEO / 'template.html'
COR_DESTAQUE = '#ffd23f'
COR_TEXTO = '#ffffff'


def gerar_html(palavras, dur: float, template: Path = TEMPLATE, extra: dict | None = None,
               max_palavras: int = 4, cor_texto: str = COR_TEXTO, cor_destaque: str = COR_DESTAQUE) -> str:
    """palavras: [{'word','start','end'}] do words.json. Retorna o index.html da composição.

    `extra` troca marcadores adicionais do template (ex.: __DADOS__) antes de devolver.
    `max_palavras`: palavras por tela de legenda.
    """
    grupos = agrupar([{'s': p['start'], 'e': p['end'], 'w': p['word']} for p in palavras], 0, dur,
                     max_palavras=max_palavras)
    partes, anims = [], []
    for i, g in enumerate(grupos):
        ini = max(0.0, g[0]['s'])
        prox = grupos[i + 1][0]['s'] if i + 1 < len(grupos) else dur
        fim = min(g[-1]['e'] + 0.35, prox, dur)  # tela fica um pouco mais, sem atropelar a próxima
        spans = ''.join(f'<span id="g{i}w{j}">{html.escape(w["w"])}</span>' for j, w in enumerate(g))
        partes.append(f'      <div id="g{i}" class="clip" data-start="{ini:.3f}" '
                      f'data-duration="{max(fim - ini, 0.1):.3f}" data-track-index="0">'
                      f'<p class="fala">{spans}</p></div>')
        anims.append(f'      tl.fromTo("#g{i}", {{opacity: 0, y: 24}}, '
                     f'{{opacity: 1, y: 0, duration: 0.15, ease: "power2.out"}}, {ini:.3f});')
        for j, w in enumerate(g):  # palavra falada fica amarela enquanto é dita
            anims.append(f'      tl.set("#g{i}w{j}", {{color: "{cor_destaque}"}}, {w["s"]:.3f});')
            anims.append(f'      tl.set("#g{i}w{j}", {{color: "{cor_texto}"}}, {w["e"]:.3f});')
        anims.append(f'      tl.to("#g{i}", {{opacity: 0, duration: 0.12, ease: "power1.in"}}, '
                     f'{max(fim - 0.12, ini):.3f});')
    modelo = template.read_text(encoding='utf-8')
    saida = (modelo.replace('__DURACAO__', f'{dur:.3f}')
                   .replace('__GRUPOS__', '\n'.join(partes))
                   .replace('__ANIMACOES__', '\n'.join(anims)))
    for chave, valor in (extra or {}).items():
        saida = saida.replace(chave, valor)
    return saida


def preparar_projeto(html: str, wav: Path):
    """Grava index.html e narration.wav no projeto video/ (sem renderizar)."""
    if not (VIDEO / 'node_modules').exists():
        raise SystemExit('hyperframes: rode `pnpm install` dentro de videoFactory/video')
    shutil.copyfile(wav, VIDEO / 'narration.wav')
    (VIDEO / 'index.html').write_text(html, encoding='utf-8')


def pnpm_hyperframes(*args: str) -> subprocess.CompletedProcess:
    """Roda `pnpm exec hyperframes ...` com cwd em video/."""
    pnpm = shutil.which('pnpm') or 'pnpm'
    r = subprocess.run([pnpm, 'exec', 'hyperframes', *args], cwd=VIDEO, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    if r.returncode != 0:
        sys.exit(f'hyperframes {args[0]} falhou:\n{(r.stdout + r.stderr)[-2000:]}')
    return r


def renderizar(palavras, dur: float, wav: Path, out_mp4: Path, fps: int = 30,
               html: str | None = None):
    """Copia a narração para o projeto, grava index.html e renderiza com `pnpm exec hyperframes render`.

    html: se None, usa o template de legenda (template.html). Passe o HTML pronto para outras cenas.
    """
    if not (VIDEO / 'node_modules').exists():
        raise SystemExit('renderer hyperframes: rode `pnpm install` dentro de videoFactory/video')
    print('  renderizando (HyperFrames)...')
    shutil.copyfile(wav, VIDEO / 'narration.wav')
    (VIDEO / 'index.html').write_text(html if html is not None else gerar_html(palavras, dur), encoding='utf-8')
    pnpm = shutil.which('pnpm') or 'pnpm'
    r = subprocess.run([pnpm, 'exec', 'hyperframes', 'render', '.', '-o', str(out_mp4.resolve()),
                        '--fps', str(fps), '-q', 'looks'], cwd=VIDEO, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    if r.returncode != 0:
        sys.exit(f'hyperframes render falhou:\n{(r.stdout + r.stderr)[-2000:]}')
