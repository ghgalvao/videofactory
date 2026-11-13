"""Validação automática do job (sem olhar imagem): roteiro, storyboard.json e margens dos elementos."""
import json
import re

import soundfile as sf

from ..modes.storyboard import calcular_planos
from .paths import Job

TIPOS = {'faixa', 'selo', 'carimbo', 'texto', 'objeto', 'calendario', 'barras', 'numero', 'etiqueta'}
ENTRADAS = {'cima', 'baixo', 'esquerda', 'direita', 'bate', 'cai', 'cresce', 'pop'}
OBJETOS = {'copo', 'pedra', 'nuvem', 'sol', 'mar', 'rio', 'graos', 'seta'}
W_PADRAO = {'faixa': 920, 'selo': 440, 'texto': 900, 'objeto': 300, 'calendario': 680, 'barras': 940, 'etiqueta': 640}
L, R, T, B = 30, 1050, 200, 1620  # margens do quadro 1080x1920 (topo livre para a interface, legenda embaixo)


def _largura(e: dict) -> float:
    if e['tipo'] in W_PADRAO:
        return e.get('w', W_PADRAO[e['tipo']])
    texto = max((len(x) for x in str(e.get('texto', e.get('suf', ''))).split('\n')), default=1)
    if e['tipo'] == 'carimbo':
        return texto * e.get('s', 90) * 0.55 + 68
    n = len(str(int(e.get('valor', 0)))) + len(str(e.get('pre', ''))) + len(str(e.get('suf', '')))  # numero
    return n * e.get('s', 300) * 0.5


def checar(job: Job) -> tuple[list[str], list[str]]:
    erros, avisos = [], []
    if not job.roteiro.exists():
        erros.append('falta 1-entrada/roteiro.txt')
        return erros, avisos
    texto = job.roteiro.read_text(encoding='utf-8')

    # ---- roteiro ----
    if re.search(r'\d', re.sub(r'\[[^\]]*\]', '', texto)):
        avisos.append('roteiro tem dígitos: escreva números por extenso para a voz (use "substituicoes" na legenda)')
    blocos = [b for b in re.split(r'\n\s*\n', texto.strip()) if b.strip()]
    if len(blocos) < 2:
        avisos.append('sem linha em branco antes do CTA (a voz emenda a última frase; deixe uma linha em branco)')
    palavras_roteiro = len(texto.split())
    if palavras_roteiro < 60 or palavras_roteiro > 140:
        avisos.append(f'roteiro com {palavras_roteiro} palavras (alvo ~80–120 para 35–45 s)')

    # ---- tempo ----
    dur = None
    if job.wav.exists():
        dur = sf.info(str(job.wav)).duration
        if dur < 30 or dur > 52:
            avisos.append(f'narração com {dur:.0f} s (alvo 35–45 s para Reels/Shorts)')
    else:
        avisos.append('narração ainda não gerada (rode vf narrate); validação de tempos pulada')

    # ---- storyboard ----
    if not job.storyboard.exists():
        erros.append('falta 1-entrada/storyboard.json')
        return erros, avisos
    try:
        sb = json.loads(job.storyboard.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        erros.append(f'storyboard.json inválido: {e}')
        return erros, avisos
    planos = sb.get('planos', [])
    usadas: list[int] = []
    for p in planos:
        usadas += p.get('frases', [])
    if sorted(usadas) != list(range(1, (max(usadas) if usadas else 0) + 1)):
        erros.append(f'frases do storyboard com buraco ou repetição: {sorted(usadas)}')
    n_frases = len(re.findall(r'[.?!](?:\s|$)', texto))
    if usadas and max(usadas) != n_frases:
        avisos.append(f'storyboard cobre até a frase {max(usadas)}, mas o roteiro tem {n_frases} frases')
    if len(planos) != 8:
        avisos.append(f'{len(planos)} planos (a folha 4×2 foi pensada para 8)')

    tempos = None
    if job.words.exists():
        try:
            tempos, _ = calcular_planos(planos, json.loads(job.words.read_text(encoding='utf-8')), dur or 0)
        except SystemExit as e:
            erros.append(str(e))
    for i, p in enumerate(planos):
        n = p.get('id', i + 1)
        els = p.get('elementos', [])
        if sb.get('cena') != 'paper':
            continue  # validação de elementos só existe para o estilo paper
        if sb.get('cena') == 'paper' and not els:
            erros.append(f'plano {n} sem elementos')
        if len(els) > 4:
            avisos.append(f'plano {n}: {len(els)} elementos (receita: no máximo 4, um foco por vez)')
        if tempos:
            d = tempos[i]['t1'] - tempos[i]['t0']
            if d > 9.5:
                avisos.append(f'plano {n} dura {d:.1f} s: dividir ou adicionar mudança visível (alvo 3–6 s, até ~9 s com gráfico)')
            if d < 1.5:
                avisos.append(f'plano {n} dura só {d:.1f} s')
        ys = []
        for k, e in enumerate(els):
            nome = f'plano {n}, elemento {k + 1} ({e.get("tipo", "?")})'
            if e.get('tipo') not in TIPOS:
                erros.append(f'{nome}: tipo desconhecido'); continue
            if e.get('entrada') and e['entrada'] not in ENTRADAS:
                erros.append(f'{nome}: entrada "{e["entrada"]}" desconhecida')
            if e['tipo'] == 'objeto' and e.get('nome') not in OBJETOS:
                erros.append(f'{nome}: objeto "{e.get("nome")}" não existe ({", ".join(sorted(OBJETOS))})')
            if e['tipo'] == 'barras' and not e.get('linhas'):
                erros.append(f'{nome}: barras sem linhas')
            x, y = e.get('x', 540), e.get('y', 960) + sb.get('dy', 50)
            ys.append(y)
            w = _largura(e)
            if x - w / 2 < L or x + w / 2 > R:
                avisos.append(f'{nome}: pode sair da margem horizontal (x {x}, largura ~{w:.0f})')
            if y < T or y > B:
                avisos.append(f'{nome}: y {y} fora da zona segura ({T}–{B})')
            for campo in ('texto', 'topo', 'grande', 'titulo'):
                if len(str(e.get(campo, ''))) > 42:
                    avisos.append(f'{nome}: campo "{campo}" longo ({len(str(e[campo]))} caracteres); encurte')
        if ys and not (650 <= sum(ys) / len(ys) <= 1150):
            avisos.append(f'plano {n}: conteúdo fora do centro vertical (média y {sum(ys) / len(ys):.0f}; ideal 700–1100)')
    return erros, avisos
