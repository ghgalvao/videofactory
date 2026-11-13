---
name: vf-batch
description: Produz uma série de vídeos em lote no videoFactory (vários roteiros aprovados juntos, narração e folhas em sequência, render pela fila do painel). Use quando o usuário pedir série, lote, "5 vídeos sobre", episódios ou digitar /vf-batch.
argument-hint: "<estilo> <galeria> <quantidade> <tema geral ou lista de temas>"
---

# vf-batch

## Quando usar
Para produzir vários vídeos de uma vez, mantendo o mesmo estilo e tom, sem aprovar um por um.

## Como usar
```
/vf-batch whiteboard science-channel 5 curiosidades do corpo humano
/vf-batch paper science-channel 3 por que o céu é azul; marés; vulcões
```

## O que faz
1. Leia `brief.md` da galeria (se existir) e a receita do estilo.
2. Proponha a lista de episódios (títulos e gancho de cada um). **Espere o ok da lista.**
3. Crie um job por episódio, com nome em inglês e numerado: `<galeria>/<serie>-01-<slug>`, `-02-`...
4. Escreva todos os roteiros e mostre juntos, numerados. **Espere o ok** (o usuário pode aprovar alguns e pedir ajuste em outros).
5. Para cada roteiro aprovado: narre, monte o storyboard, rode `vf checar` e gere a folha.
6. Mostre todas as folhas juntas. **Espere o ok** de cada uma.
7. Para animar: diga ao usuário para clicar em "Aprovar e animar" em cada job no painel (`uv run vf panel`), que põe tudo na fila e roda um de cada vez; ou, se ele preferir, rode `uv run vf storyboard <job> --animar` um por vez.

## Entrega
N jobs na galeria, cada um com roteiro, narração, storyboard e folha; os vídeos saem pela fila.

## Regras
- Mesmo estilo, mesma voz e mesma chamada final em toda a série, salvo pedido contrário.
- Fatos de cada episódio com duas fontes.
- Render é pesado: nunca rode dois ao mesmo tempo.
