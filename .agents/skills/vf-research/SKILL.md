---
name: vf-research
description: Pesquisa um tema e grava um estudo com fontes conferidas na galeria do videoFactory, para servir de base aos roteiros. Use quando o usuário pedir pesquisa, estudo, levantamento de dados, "o que dizer sobre X" ou digitar /vf-research.
argument-hint: "<tema> [galeria]"
---

# vf-research

## Quando usar
Antes de escrever roteiros sobre um assunto, para ter os fatos conferidos, os ângulos possíveis e as fontes num lugar só, reaproveitável por vários vídeos.

## Como usar
```
/vf-research como funcionam as marés science-channel
/vf-research quanto sal tem na água do mar science-channel
/vf-research tendências de formato de reels 2026
```

## O que faz
1. Leia o `brief.md` da galeria (público e tom) e os estudos que já existem em `research/`, para não repetir.
2. Defina 5 a 8 perguntas que o público faria sobre o tema.
3. Pesquise e responda cada uma. **Todo número, data e afirmação com duas fontes independentes**, com link e data de acesso. Prefira fontes primárias (órgão oficial, estudo, documentação). Marque claramente o que é consenso, o que é controverso e o que não deu para confirmar.
4. Liste ângulos de vídeo: 5 ganchos possíveis e os mitos comuns que o estudo derruba.
5. Grave em `saida/<galeria>/research/<slug>.md` (sem galeria: `saida/_shared/research/`) com: tema, data, perguntas, achados, fontes, ângulos e "como usar no roteiro".

## Entrega
Um estudo em Markdown com fontes, pronto para o `/vf-script` e o `/vf-video` usarem.

## Regras
- Saúde, dinheiro e direito: escreva com cautela, sem promessa de resultado, e aponte quando o assunto pede profissional.
- Não invente fonte. Se não achar duas, diga que não confirmou.
- Cite trechos curtos; resuma com suas palavras.
