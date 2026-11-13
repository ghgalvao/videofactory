# STYLE — Ken Burns (motion comic)

Status: a criar · Template: comando de montagem (`vf montar`, a criar) · 16:9 e 9:16 · 30 s a 15 min · créditos de imagem

## Quando usar
Narração longa sobre uma sequência de imagens ilustradas geradas por IA (referência: canais de narração com imagens ilustradas). Melhor custo para vídeos longos de YouTube.

## Roteiro
Uma imagem para cada 3–6 s de fala. O roteiro é dividido em cenas numeradas, e cada cena vira um prompt de imagem com o mesmo personagem.

## Planos-tipo
| Plano | Duração | O que aparece | O que muda |
|---|---|---|---|
| Cena | 3–6 s | imagem cheia | um movimento de câmera por cena |
| Destaque | 2–3 s | número/selo sobre a imagem | pop do selo |
| Virada | 1 s | tela escura ou flash | silêncio + corte seco |

## Visual
- Imagens numeradas `01..NN` na pasta do job, mesma proporção do vídeo.
- Correção de cor e vinheta **iguais para o vídeo inteiro** (imagens de origens diferentes parecem do mesmo filme).
- Legenda na faixa inferior sem cobrir rosto; selos e números no estilo do canal.

## Movimento
- Ciclo sem repetição imediata: zoom in → pan lateral → zoom out → pan vertical.
- Escala total entre 1,00 e 1,12 (mais que isso pixeliza); velocidade constante dentro da cena.
- Troca de cena: corte seco no ritmo da fala; deslize curto (0,3 s) só em mudança de assunto.
- Tremor curto em impacto.

## Som
Efeito suave por corte, música que cresce nos picos, silêncio antes da virada.

## Entradas necessárias
Imagens (≥ 1 a cada 5 s), ficha do personagem para consistência, `storyboard.json` ligando frases a imagens.

## Aceite
Nenhuma imagem repetida; movimento variado; cor consistente; legenda nunca sobre rosto; ritmo de corte acompanha a fala.

## Teste sugerido
4 a 6 imagens num vídeo de 30–40 s (9:16) e o mesmo em 16:9.

## Riscos e licenças
Consistência de personagem depende da ferramenta de imagem; termos de uso comercial da ferramenta que gerou a imagem.
