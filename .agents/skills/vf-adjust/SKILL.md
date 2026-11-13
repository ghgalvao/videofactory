---
name: vf-adjust
description: Ajusta um job do videoFactory sem refazer tudo (um plano do storyboard, uma frase da narração, cores, ordem). Use quando o usuário pedir mudança num vídeo existente, "no plano 3...", "troca essa frase" ou digitar /vf-adjust.
argument-hint: "<job> <o que mudar>"
---

# vf-adjust

## Quando usar
Depois de ver a folha ou o vídeo, para corrigir só o que precisa: um plano, uma frase, uma cor, a ordem das cenas.

## Como usar
```
/vf-adjust science-channel/why-sky-is-blue plano 3 o texto encosta na margem
/vf-adjust clients/product-launch troca a frase 4 por "o preço vale até sexta"
/vf-adjust clients/promo-video cor de destaque #ff7a00 em todos os planos
```

## O que faz
1. Leia o job: `1-entrada/storyboard.json`, `1-entrada/roteiro.txt` e a folha em `2-aprovar/`.
2. Veja também os pedidos abertos em `1-entrada/requests.md`, se existir, e trate os que tiverem a ver.
3. **Mudança visual** (plano, cor, ordem, cartão): edite só o `storyboard.json`. A narração não muda.
4. **Mudança de texto**: edite a frase no `roteiro.txt` e narre de novo (`uv run vf narrate ...`); o cache de voz reaproveita as frases iguais. Avise se a mudança altera o tempo dos planos.
5. Rode `uv run vf checar <job>` e `uv run vf storyboard <job>`. Mostre a folha nova destacando o que mudou. **Pare e espere o ok** antes de animar.
6. Marque em `requests.md` (se existir) os pedidos atendidos.

## Entrega
Folha nova em `2-aprovar/` com o ajuste; vídeo só depois do ok.

## Regras
- Mexa no mínimo necessário. Não reescreva planos que o usuário não citou.
- Não refaça narração para mudança só visual.
