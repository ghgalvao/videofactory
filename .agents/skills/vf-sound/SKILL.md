---
name: vf-sound
description: Aplica efeitos sonoros a um vídeo pronto do videoFactory com o sound-layer (escolha de sons CC0, cues pela linha do tempo, mix e QA). Use quando o usuário pedir efeitos sonoros, som, sound design ou digitar /vf-sound.
argument-hint: "<job>"
---

# vf-sound

## Quando usar
Depois que o vídeo está aprovado, para dar ritmo com efeitos (entradas, trocas de plano, destaques) sem abafar a voz.

## Como usar
```
/vf-sound science-channel/why-sky-is-blue
```

## O que faz
1. Leia `ferramentas/sound-layer/README.md` e `PROMPT.md`. Confira se a biblioteca existe (`ferramentas/sound-layer/audio/kit/catalog.json`); se não, peça ao usuário para rodar `uv run scripts/sfx.py kit` (alguns pacotes exigem download manual em `audio/kit/_raw/`).
2. Tire os tempos dos movimentos do próprio storyboard e de `_interno/words.json` (entradas, cortes, destaques). Não invente quadros.
3. Escolha cada som com `sfx.py browse --type <tipo> --like "<material, peso, clima>"` e olhe a imagem gerada. Uma família sonora por vídeo; um destaque forte a cada ~4 s no máximo.
4. Monte `_interno/som/cues.json` (formato: `uv run scripts/mix.py --schema`) com caminhos **relativos e sem acento**, rodando de dentro de `ferramentas/sound-layer/`.
5. `uv run scripts/mix.py <cues> --out <pasta>` e depois `uv run scripts/qa.py <video> --audio <pasta>`. Corrija o que o QA apontar (som abafado pela voz → som mais brilhante ou tempo ajustado). Pausa proposital: marque `silence_ok`.
6. Junte o mix ao vídeo. Guarde o original como `3-final/video-sem-som.mp4` e o novo como `3-final/video.mp4`.

## Entrega
Vídeo com efeitos em `3-final/video.mp4`, versão sem som ao lado, e o relatório do QA (LUFS, pico, falhas restantes).

## Regras
- Nunca sintetize batidas, cliques ou whooshes; nada de som de meme.
- Nunca afrouxe um limite do QA para passar.
- O ouvido final é do usuário: avise o que ficou abaixo do ideal.
