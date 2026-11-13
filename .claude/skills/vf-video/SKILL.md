---
name: vf-video
description: Produz um vídeo completo no videoFactory (roteiro → narração → storyboard → folha → render) com duas paradas para aprovação. Use quando o usuário pedir "faz um vídeo", "cria um vídeo sobre X", "vídeo no estilo Y" ou digitar /vf-video.
argument-hint: "<estilo> <tema> [galeria] [duração em s]"
---

# vf-video

## Quando usar
Para fazer um vídeo do zero: você dá o estilo e o tema, o Claude conduz tudo e para nos dois portões (roteiro e folha).

## Como usar
```
/vf-video whiteboard por que o céu é azul
/vf-video paper por que o mar é salgado science-channel 45
```

## O que faz
1. **Contexto.** Leia `CLAUDE.md`, `docs/DIRECTOR.md`, `styles/<estilo>/STYLE.md` e um exemplo em `styles/<estilo>/exemplos/` (o `prompt.txt` do exemplo mostra o nível de detalhe esperado). Estilo desconhecido: rode `uv run vf estilos` e sugira os 3 mais próximos.
2. **Galeria.** Se o usuário indicou uma galeria (subpasta de `saida/`), leia o que existir nela: `brief.md` (público, tom, objetivo), `brand.json` (cores, fontes), `references/` e `research/`. Sem galeria, pergunte em qual pasta criar ou use `saida/`.
3. **Job.** Nome em inglês, minúsculas e hífen (ex.: `why-sky-is-blue`). Rode `uv run vf novo <estilo> <galeria>/<job>`.
4. **Roteiro.** Gancho nos 3 primeiros segundos, uma frase por linha, linha em branco antes da chamada final, duração alvo (padrão 40 s). Todo número e data com duas fontes, listadas abaixo do roteiro na resposta. Grave em `1-entrada/roteiro.txt`. **Pare e espere o ok.**
5. **Narração.** `uv run vf narrate saida/<job>/1-entrada/roteiro.txt --nome <job> --engine edge --modelo small` (outro motor só se o usuário pedir; ver `/vf-voice`).
6. **Storyboard.** Monte `1-entrada/storyboard.json` pela receita do estilo, um plano por frase ou grupo curto de frases, usando cores e fontes do `brand.json` quando houver. Rode `uv run vf checar <job>` e corrija até 0 erros.
7. **Folha.** `uv run vf storyboard <job>`. Olhe a folha você mesmo (texto cortado, sobreposição, cena fora do tema), corrija e gere de novo. Mostre ao usuário. **Pare e espere o ok.**
8. **Render.** `uv run vf storyboard <job> --animar`. Informe o caminho de `3-final/video.mp4`.

## Entrega
`saida/<galeria>/<job>/3-final/video.mp4`, mais roteiro, storyboard e folha no job. O job aparece no painel (`uv run vf panel`) com todas as etapas.

## Regras
- Nunca anime sem o ok da folha. Nunca pule o ok do roteiro.
- Nada de cliente, marca ou nome pessoal dentro do motor: só na pasta do job ou da galeria.
- Se o usuário disser "só gera e manda", pule a conferência quadro a quadro, mas mantenha `vf checar`.
