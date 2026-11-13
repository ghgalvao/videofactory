"""Legenda animada DINÂMICA (variante do animated-caption): palavra por palavra com pop, destaques por frase,
selo de seção, cor de fundo por seção, flash na troca, zoom lento e barra de progresso.

Entrada extra opcional do job: `1-entrada/destaques.json`
{
  "destaques": [{"frase": "nao precisa", "cor": "#ff4d4d", "efeito": "tremor"}],   # efeito: tremor | pulso | (vazio)
  "cta": "salva"                                                                      # palavra que abre a seção final
}
`frase` é comparada sem acento, sem pontuação e em minúsculas. `cor` vazia = cor da seção.
Seções: abertura (até o 1º "Mito <um|dois|três>"), "MITO n" (selo carimbado) e CTA.
"""
import html
import json
import re
import unicodedata
from pathlib import Path

from .paths import ROOT

TEMPLATE = ROOT / 'video' / 'legenda-dinamica.html'
PALETA = ['#7fc8d9', '#b9a3e8', '#f0a868', '#9bd8a0']  # seções de mito 1, 2, 3, 4...
COR_ABERTURA = '#e8c46a'
COR_CTA = '#9bd8a0'
NUMEROS = {'um': 1, 'dois': 2, 'tres': 3, 'quatro': 4, 'cinco': 5}


def _norm(s: str) -> str:
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', s)


def _secoes(palavras, dur, cta):
    """Retorna [{ini, fim, cor, selo}] cobrindo 0..dur."""
    marcos = [(0.0, COR_ABERTURA, 0)]
    n = [_norm(p['word']) for p in palavras]
    for i, w in enumerate(n):
        if w == 'mito' and i + 1 < len(n) and n[i + 1] in NUMEROS:
            k = NUMEROS[n[i + 1]]
            marcos.append((palavras[i]['start'], PALETA[(k - 1) % len(PALETA)], k))
        elif cta and w == _norm(cta) and True:
            marcos.append((palavras[i]['start'], COR_CTA, 0))
            break
    return [{'ini': m[0], 'fim': marcos[j + 1][0] if j + 1 < len(marcos) else dur, 'cor': m[1], 'selo': m[2]}
            for j, m in enumerate(marcos)]


def _grupos(palavras, secoes, max_palavras=3):
    """Telas de até `max_palavras`; quebra em pontuação final e na troca de seção."""
    grupos, atual = [], []
    sec_atual = 0

    def fechar():
        nonlocal atual
        if atual:
            grupos.append((sec_atual, atual))
            atual = []

    for p in palavras:
        s = next((k for k, sec in enumerate(secoes) if p['start'] < sec['fim']), len(secoes) - 1)
        if s != sec_atual:
            fechar()
            sec_atual = s
        atual.append(p)
        if len(atual) >= max_palavras or re.search(r'[.?!:]$', p['word']):
            fechar()
    fechar()
    return grupos


def _destaques(palavras, cfg):
    """índice da palavra → (cor, efeito) para todas as palavras cobertas por uma frase de destaque."""
    n = [_norm(p['word']) for p in palavras]
    saida = {}
    for d in cfg.get('destaques', []):
        alvo = [_norm(x) for x in d['frase'].split()]
        for i in range(len(n) - len(alvo) + 1):
            if n[i:i + len(alvo)] == alvo:
                for j in range(i, i + len(alvo)):
                    saida[j] = (d.get('cor') or '', d.get('efeito') or '')
    return saida


def gerar_html(palavras, dur: float, config: dict | None = None, template: Path = TEMPLATE) -> str:
    cfg = config or {}
    secoes = _secoes(palavras, dur, cfg.get('cta', ''))
    indice = {id(p): i for i, p in enumerate(palavras)}
    marcados = _destaques(palavras, cfg)
    grupos = _grupos(palavras, secoes)

    selos, partes, anims = [], [], []
    for k, sec in enumerate(secoes):
        anims.append(f'      tl.to(":root", {{"--g": "{sec["cor"]}", duration: 0.6, ease: "power2.out"}}, {sec["ini"]:.3f});')
        anims.append(f'      tl.set("#prog", {{backgroundColor: "{sec["cor"]}"}}, {sec["ini"]:.3f});')
        if sec['selo']:
            dsel = max(sec['fim'] - sec['ini'], 0.2)
            selos.append(f'      <div id="n{k}" class="clip num" data-start="{sec["ini"]:.3f}" data-duration="{dsel:.3f}" '
                         f'data-track-index="1" style="color:{sec["cor"]}">{sec["selo"]}</div>')
            selos.append(f'      <div id="s{k}" class="clip selo" data-start="{sec["ini"]:.3f}" data-duration="{dsel:.3f}" '
                         f'data-track-index="1" style="color:{sec["cor"]}"><b>MITO {sec["selo"]}</b><i></i></div>')
            anims.append(f'      tl.fromTo("#n{k}", {{opacity: 0, scale: 1.12, y: 40}}, {{opacity: 0.07, scale: 1, y: 0, duration: 0.9, ease: "power3.out"}}, {sec["ini"]:.3f});')
            anims.append(f'      tl.fromTo("#s{k} b", {{opacity: 0, y: -24}}, {{opacity: 1, y: 0, duration: 0.5, ease: "power3.out"}}, {sec["ini"] + 0.1:.3f});')
            anims.append(f'      tl.fromTo("#s{k} i", {{scaleX: 0}}, {{scaleX: 1, duration: 0.6, ease: "power3.out"}}, {sec["ini"] + 0.2:.3f});')

    for i, (s, g) in enumerate(grupos):
        ini = max(0.0, g[0]['start'])
        sec = secoes[s]
        prox = grupos[i + 1][1][0]['start'] if i + 1 < len(grupos) else dur
        fim = min(g[-1]['end'] + 0.3, prox, dur)
        fim = max(fim, ini + 0.15)
        spans = []
        for j, p in enumerate(g):
            cor_d, efeito = marcados.get(indice[id(p)], (None, ''))
            forte = indice[id(p)] in marcados
            txt = re.sub(r'[.,;:]+$', '', p['word'])
            estilo = ' class="forte"' if forte else ''
            spans.append(f'<span id="g{i}w{j}"{estilo}>{html.escape(txt)}</span>')
            base = (cor_d or sec['cor']) if forte else '#f4f1ea'
            t0, t1 = p['start'], p['end']
            # pop de entrada na hora da fala
            anims.append(f'      tl.fromTo("#g{i}w{j}", {{opacity: 0, scale: 0.94, y: 34, color: "{base}"}}, '
                         f'{{opacity: 1, scale: 1.05, y: 0, duration: 0.32, ease: "power3.out"}}, {t0:.3f});')
            anims.append(f'      tl.to("#g{i}w{j}", {{scale: 1, duration: 0.25, ease: "power2.out"}}, {t0 + 0.32:.3f});')
            if not forte:  # palavra falada fica na cor da seção enquanto é dita
                anims.append(f'      tl.set("#g{i}w{j}", {{color: "{sec["cor"]}"}}, {t0:.3f});')
                anims.append(f'      tl.set("#g{i}w{j}", {{color: "#f4f1ea"}}, {max(t1, t0 + 0.12):.3f});')
            if efeito == 'tremor':
                anims.append(f'      tl.to("#g{i}w{j}", {{x: 9, rotation: 1.5, duration: 0.05, repeat: 9, yoyo: true, ease: "none"}}, {t0 + 0.12:.3f});')
                anims.append(f'      tl.set("#g{i}w{j}", {{x: 0, rotation: 0}}, {t0 + 0.12 + 0.5:.3f});')
            elif efeito == 'pulso':
                anims.append(f'      tl.to("#g{i}w{j}", {{scale: 1.12, duration: 0.3, repeat: 3, yoyo: true, ease: "sine.inOut"}}, {t0 + 0.26:.3f});')
        partes.append(f'      <div id="g{i}" class="clip" data-start="{ini:.3f}" data-duration="{fim - ini:.3f}" '
                      f'data-track-index="0"><p class="fala">{"".join(spans)}</p></div>')
        # zoom lento durante a tela + saída seca
        anims.append(f'      tl.fromTo("#g{i} .fala", {{scale: 0.985}}, {{scale: 1.025, duration: {fim - ini:.3f}, ease: "none"}}, {ini:.3f});')
        anims.append(f'      tl.to("#g{i}", {{opacity: 0, y: -30, duration: 0.16, ease: "power1.in"}}, {max(fim - 0.16, ini):.3f});')

    modelo = template.read_text(encoding='utf-8')
    return (modelo.replace('__DURACAO__', f'{dur:.3f}')
                  .replace('__SELOS__', '\n'.join(selos))
                  .replace('__GRUPOS__', '\n'.join(partes))
                  .replace('__ANIMACOES__', '\n'.join(anims)))


def carregar_config(entrada: Path) -> dict:
    arq = entrada / 'destaques.json'
    return json.loads(arq.read_text(encoding='utf-8')) if arq.exists() else {}
