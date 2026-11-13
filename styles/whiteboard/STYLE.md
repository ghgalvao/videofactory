# STYLE — Quadro branco (traço à mão)

Status: a criar · Template: `video/quadro.html` · 9:16 · 35–45 s · R$ 0

## Quando usar
Explicar um conceito ou processo passo a passo, com desenhos simples ("por que o céu é azul", "como funciona o juro composto"). Não usar para notícia com muitos números (use `paper` ou `data-infographic`).

## Roteiro
Pergunta → desenho 1 (o elemento) → desenho 2 (o que acontece) → conexão com setas → conclusão em uma frase → CTA.
Exemplo de gancho: "Se a luz do sol é branca, por que o céu é azul?"

## Planos-tipo
| Plano | Duração | O que aparece | O que muda |
|---|---|---|---|
| Pergunta | 3 s | pergunta escrita à mão | letras se escrevem |
| Elemento | 5–6 s | 1–2 desenhos | traço se desenha |
| Processo | 6–8 s | setas, ondas, etapas numeradas | traços em sequência na fala |
| Conexão | 5 s | quadro inteiro com setas | câmera recua e mostra tudo |
| Conclusão | 4 s | frase-chave sublinhada | sublinhado em vermelho |
| CTA | 3 s | "segue" desenhado | apagador limpa o quadro |

## Visual
- Fundo `#faf8f2` com textura leve (mesma técnica de textura do `paper`); traço `#1b1f2a` 7 px, pontas arredondadas; **uma** cor de destaque (`#d6342b` ou `#2a6fdb`).
- Letra manuscrita local com licença OFL (ex.: Caveat ou Patrick Hand, a conferir) em `video/assets/fonts/`.
- Desenhos em SVG simples: seta, caixa, círculo, sol, onda, gota, pessoa-palito, engrenagem.
- No máximo 3 desenhos por plano; margens de 90 px.

## Movimento
- Traço "se desenha" com `stroke-dasharray`/`stroke-dashoffset`, velocidade ≈ 600 px/s.
- Texto escrito letra a letra rápido (≈ 25 letras/s).
- Transição de plano: varredura do apagador (0,4 s) ou recuo de câmera.
- Proibido: desenhos aparecendo prontos (sem traço) e mais de um traço simultâneo.

## Som
Caneta riscando (baixo, só enquanto desenha), "pop" no sublinhado, música leve.

## Entradas necessárias
Roteiro + lista de desenhos por plano (o que desenhar e em que frase).

## Aceite
Traço legível no celular; cada desenho entra na frase que o cita; quadro nunca poluído.

## Teste sugerido
"Por que o céu é azul" (espalhamento de Rayleigh; conferir em fonte de divulgação científica).

## Riscos e licenças
Fonte manuscrita só com licença livre; não desenhar personagens protegidos.
