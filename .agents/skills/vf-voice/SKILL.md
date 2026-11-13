---
name: vf-voice
description: Cuida da voz de um job do videoFactory (escolher motor e voz, comparar vozes, direção por frase com tom, pausa e velocidade no Voicebox). Use quando o usuário falar de voz, narração, entonação, velocidade ou digitar /vf-voice.
argument-hint: "<job> [compare|direct] [perfil do Voicebox]"
---

# vf-voice

## Quando usar
Quando a voz padrão (Edge) não serve: para comparar opções, usar uma voz própria ou dar direção frase a frase.

## Como usar
```
/vf-voice science-channel/why-sky-is-blue compare
/vf-voice science-channel/why-sky-is-blue direct "Minha voz"
```

## O que faz
**Modo `compare`:** gere só a primeira frase do roteiro com Edge (`pt-BR-AntonioNeural`, `pt-BR-FranciscaNeural`), Kokoro e, se o app Voicebox estiver aberto, os perfis disponíveis. Salve em `2-aprovar/voice-test/` com o nome do motor e da voz e peça ao usuário para ouvir.

**Modo `direct`:**
1. Confira se o Voicebox está aberto (API em `127.0.0.1:17493`); liste os perfis.
2. Escreva `1-entrada/direcao_audio.json`: `padrao` (tom de referência), `tons` (nome → perfil) e `frases` (número da frase → `tom`, `pausa` em s, `vel`). Ex.: gancho mais animado, pausa de 0,5 s antes da chamada, frases longas a 1,05.
3. Narre com `uv run vf narrate ... --engine voicebox --voz "<perfil>" --modelo small`. O cache reaproveita frases já geradas.
4. Avise o tempo gasto e, se estiver lento sem GPU, sugira testar no modelo 0.6B e gerar a final uma vez só.

## Entrega
Arquivos de teste para comparar, ou a narração nova em `_interno/narration.wav` com a direção salva no job.

## Regras
- Voz clonada só da pessoa que autorizou por escrito. Nunca voz de pessoa pública, dublador ou personagem, nem como "máscara" sobre outra gravação.
- Instrução de tom do Qwen não funciona com voz clonada: use um perfil por tom.
