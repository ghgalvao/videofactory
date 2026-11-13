# Estrutura de um job (um vídeo por pasta)

Cada vídeo (job) tem sempre as mesmas 4 pastas, na ordem do fluxo:

```
<job>/
  1-entrada/   O QUE DEFINE O VÍDEO (pode editar):  roteiro.txt · direcao.md · storyboard.json · imagens/
  2-aprovar/   PARA VOCÊ OLHAR E APROVAR:       storyboard_folha.png
  3-final/     SAÍDA PRONTA PARA PUBLICAR:           video.mp4  (capa e legenda quando existirem)
  _interno/    USO DO SISTEMA (ignore):              narration.wav · words.json · whisper.json · legenda.ass · quadros · temporários
```

## Regras
- **Você só precisa abrir `2-aprovar/` e `3-final/`.**
- Aprovou a folha? Peça "anima o <job>". O vídeo aparece em `3-final/`.
- Quer mudar o texto ou um plano? Edite (ou peça) `1-entrada/roteiro.txt` e `1-entrada/storyboard.json`.
- `_interno/` pode ser apagada a qualquer momento: o sistema regenera (a narração é refeita e gasta ~1 min).
- O vídeo é sempre escrito em `_interno/` e movido para `3-final/` só quando termina; então `3-final/` nunca tem arquivo pela metade.

## Pastas de cliente
Uma subpasta por cliente (`cliente/<job>`), com `marca.json` e `LEIA-ANTES.md`.
Rascunho interno: não enviar ao cliente sem decisão do responsável.

## Comandos úteis
- `uv run vf organizar --simular` mostra o que seria arrumado em jobs antigos; `uv run vf organizar --todos` arruma.
- `uv run vf storyboard <job>` gera a folha; `uv run vf storyboard <job> --animar` gera o vídeo.
