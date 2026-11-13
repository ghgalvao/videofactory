# STYLE — Blueprint (planta técnica)

Status: a criar · Template: `video/blueprint.html` · 9:16 · 35–45 s · R$ 0

## Quando usar
"Como funciona" de máquinas, equipamentos, obras e instalações. É o estilo natural para clientes industriais (equipamentos, inox, climatização). Não usar para temas sem objeto físico.

## Roteiro
Gancho → vista geral → peça 1 (nome + função) → peça 2 → fluxo de energia/material → resumo das etapas → CTA.
Exemplo de gancho: "Seu ar-condicionado não cria frio. Ele tira o calor de dentro."

## Planos-tipo
| Plano | Duração | O que aparece | O que muda |
|---|---|---|---|
| Vista geral | 4–5 s | desenho completo em linhas | linhas se desenham |
| Peça | 5–6 s cada | moldura de zoom na peça + nome | cota corre de ponta a ponta |
| Fluxo | 6–8 s | setas/partículas no caminho | fluxo anima na fala |
| Resumo | 5 s | etapas numeradas 1→4 | etapas acendem em sequência |
| CTA | 3 s | carimbo técnico ("APROVADO", "SEGUE") | carimbo bate |

## Visual
- Fundo `#0b3a6b` com grade fina `#1d5a96` (a cada 40 px) e grade grossa (a cada 200 px).
- Linhas `#ffffff` 3–4 px; cotas `#ffd23f`; destaque de peça `#4fe3ff`.
- Fonte técnica local com licença livre (ex.: IBM Plex Mono para rótulos, Barlow Condensed para títulos; a conferir).
- Carimbo/legenda de planta no canto ("FOLHA 1/4", nome do projeto).

## Movimento
- Linhas se desenham (`stroke-dashoffset`), cotas "escorrem" (0,5 s), zoom com moldura retangular (0,6 s, `power2.inOut`).
- Fluxo: partículas ao longo do caminho, como no `mechanism-3d`.
- Proibido: elementos em perspectiva realista (tudo em vista ortográfica/corte).

## Som
Bip curto por cota, zumbido elétrico baixo, música eletrônica leve.

## Entradas necessárias
Desenho SVG por plano (frontal ou corte), lista de peças, função de cada uma; para cliente, dados técnicos do fabricante.

## Aceite
Nome e função de cada peça corretos; nenhuma cota com número inventado (sem fonte, mostrar só o nome); contraste legível.

## Teste sugerido
"Como funciona um ar-condicionado split" (condensadora, evaporadora, compressor, tubulação).

## Riscos e licenças
Medidas e especificações só de documentação técnica; marca do fabricante só com autorização.
