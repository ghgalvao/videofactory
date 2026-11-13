"""Alinha o roteiro (texto verdadeiro) com as palavras do Whisper (tempos verdadeiros).

Texto e ordem vêm do roteiro. Tempos vêm do Whisper, casando sequências com difflib.
Palavras do roteiro sem par no Whisper recebem tempo interpolado entre vizinhas.
"""
import difflib
import re


def normalizar(w: str) -> str:
    return re.sub(r'[\W_]+', '', w.lower())


def alinhar(roteiro: str, palavras_whisper: list[dict]):
    """roteiro: texto. palavras_whisper: [{'s','e','w'}].

    Retorna (lista [{'word','start','end'}] com todas as palavras do roteiro, nº interpoladas).
    """
    tokens = roteiro.split()
    a = [normalizar(t) for t in tokens]
    b = [normalizar(p['w']) for p in palavras_whisper]
    tempos = [None] * len(tokens)

    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                p = palavras_whisper[j1 + k]
                tempos[i1 + k] = (p['s'], p['e'])
        elif tag == 'replace' and j2 > j1:
            # mesmo trecho falado com outras palavras: divide o intervalo do Whisper igualmente
            s0, e0 = palavras_whisper[j1]['s'], palavras_whisper[j2 - 1]['e']
            n = i2 - i1
            for k in range(n):
                tempos[i1 + k] = (s0 + (e0 - s0) * k / n, s0 + (e0 - s0) * (k + 1) / n)
        # 'insert' (roteiro sem par) fica None; 'delete' (Whisper extra) é descartado

    interpoladas = _preencher(tempos)
    saida = [{'word': t, 'start': round(s, 3), 'end': round(e, 3)} for t, (s, e) in zip(tokens, tempos)]
    return saida, interpoladas


def _preencher(tempos):
    """Preenche None por interpolação linear entre o fim anterior e o início seguinte."""
    n_interp = 0
    i = 0
    while i < len(tempos):
        if tempos[i] is not None:
            i += 1
            continue
        j = i
        while j < len(tempos) and tempos[j] is None:
            j += 1
        inicio = tempos[i - 1][1] if i > 0 else 0.0
        if j < len(tempos):
            fim = tempos[j][0]
        else:
            fim = inicio + 0.35 * (j - i)  # sem palavra seguinte: ~0,35 s por palavra
        n = j - i
        passo = max(fim - inicio, 0.0) / n
        for k in range(n):
            tempos[i + k] = (inicio + passo * k, inicio + passo * (k + 1))
        n_interp += n
        i = j
    return n_interp
