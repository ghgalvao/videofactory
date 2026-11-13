---
name: vf-reference
description: Analisa uma referência (link, arquivo ou texto) e transforma em direção para o videoFactory (estrutura, ritmo, edição, estilo do motor mais próximo). Use quando o usuário mandar um vídeo, post, print ou anotação dizendo "quero nesse estilo", "analisa esse reel" ou digitar /vf-reference.
argument-hint: "<link | caminho do arquivo | texto> [galeria]"
---

# vf-reference

## Quando usar
Quando você viu algo que quer usar como modelo de formato: um reel, um canal, um post, um print ou uma anotação sua.

## Como usar
```
/vf-reference https://www.instagram.com/reel/XXXX science-channel
/vf-reference saida/science-channel/references/files/print-01.png science-channel
/vf-reference "abre com a pergunta, mostra o erro comum e termina com a regra" science-channel
```

## O que faz
1. **Ler a referência.**
   - Link de vídeo: use a skill `watch` se estiver instalada, **com `--engine local`** (não envie o vídeo para serviço externo sem o usuário autorizar). Sem a skill, peça prints ou a transcrição.
   - Arquivo: abra a imagem, o PDF ou o vídeo (quadros com ffmpeg).
   - Texto: use como está.
2. **Analisar:** duração, gancho (o que acontece nos 3 primeiros segundos), estrutura por blocos com tempo, ritmo de corte, tipo de legenda, enquadramento, personagens, voz e música, chamada final.
3. **Traduzir para o motor:** qual estilo do videoFactory chega mais perto, o que já dá para reproduzir, o que falta (ex.: precisa de imagens externas ou de estilo novo) e um roteiro-esqueleto no mesmo formato.
4. **Guardar** (se houver galeria): em `saida/<galeria>/references/`, registre a referência em `index.json` (`title`, `type` link|file|text, `source`, `why`, `tags`, `date`, `analysis`) e grave a análise em `references/<slug>.md`. Pergunte ao usuário por que salvou, se ele não disse; esse "por que" é o que mais orienta os próximos vídeos.

## Entrega
Análise em tópicos com tempos, o estilo recomendado e o esqueleto de roteiro; arquivo salvo nas referências da galeria.

## Regras
- Mesmo formato, identidade própria: não copie arte, personagem, texto ou música da referência.
- Não baixe nem guarde o vídeo de terceiros na galeria sem o usuário pedir.
