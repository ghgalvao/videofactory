# STYLE — carrossel-vivo

Status: pronto · Template: `video/carrossel.html` (via `vf carrossel`) · Formato: 4:5 (1080×1350), um arquivo por slide · Duração: 3–6 s por slide · Custo: R$ 0

Origem do padrão: vídeo "Crie Carrosséis VIRAIS com Motion Graphics por R$0" (Felipe Borges, Fala IA!). Ideia central: o modelo não faz vídeo, **escreve código**; uma página HTML controla cada elemento segundo a segundo, e por isso texto fica nítido e som cai no segundo certo.

## Quando usar
Carrossel de Instagram/LinkedIn que precisa parar o feed: explicar um conceito em passos, listar sinais, mostrar um número, apresentar um produto. **Não usar** para narrativa longa com voz (use `paper`, `animated-caption`) nem para dado que exige gráfico (use `data-infographic`).

## Roteiro
Fórmula: **capa-gancho → 3 a 7 slides de uma ideia cada → slide de chamada**. Uma ideia por slide, título de até 8 palavras, texto de até 20. Segue `docs/DIRECTOR.md`. Gancho exemplo: "Basis é o preço da pressa".

## Slides-tipo (campo `tipo` do carrossel.json)
| Tipo | O que aparece | Ordem de entrada |
|---|---|---|
| `capa` | rótulo, título grande no pé do slide, texto curto | rótulo → título (palavra por palavra) → texto |
| `texto` | rótulo, título, parágrafo | rótulo → título → texto |
| `lista` | rótulo, título, `itens[]` numerados | rótulo → título → itens, um a um |
| `numero` | rótulo, número gigante, título, texto | rótulo → número (bate) → título → texto |
| `cta` | rótulo, título, texto, botão `cta` | … → botão (bate, com chime) |

Campos opcionais em qualquer slide: `chips[]` (etiquetas), `imagem` (arquivo em `1-entrada/imagens/`) ou `video` (clipe em `1-entrada/videos/`, b-roll livre; vira MP4 sem áudio 1080×1350 e toca atrás do slide). Fundo com mídia recebe véu escuro em gradiente para o texto ler; escolha clipe com **pelo menos a duração do slide** (3–5 s), o aviso do comando diz se faltar. Fonte e crédito: `/vf-images`.

## Visual
Tokens em `tema` (padrão): `fundo #0e1116`, `fundo2 #1a2230`, `texto #f2f4f7`, `mudo #8b93a1`, `destaque #f5b942` — **uma cor de destaque só**. Fontes locais: Barlow Condensed (títulos, números), IBM Plex Mono (rótulos, paginação), Segoe UI (texto). Margens 96 px; rodapé com marca e `n / total`; barra de progresso do slide embaixo. Com marca de cliente: troque o `tema` pelo `marca.json` (ver `docs/RECEITAS-EMPRESA.md`).

## Movimento
Cada elemento tem um instante `t` calculado em `core/carrossel.py:montar_slide` (intervalo pelo `ritmo`: rapido 0,16 s · medio 0,28 s · calmo 0,42 s). Entradas: `palavras` (título), `sobe`, `direita`, `bate` (número, botão), `barra`, `fade`. Luz de fundo deriva devagar. **Todo slide termina com 1,3 s parado e completo**: esse estado final é o PNG estático. Proibido: `Math.random`, `Date.now`, fetch, loop infinito, elemento que sai antes do fim.

## Som
Sai dos mesmos tempos do movimento: `vf carrossel <job> --som` gera `_interno/som/cues-NN.json` (formato do sound-layer, um por slide, **um hero por slide**: cta > número > título), mixa e junta ao MP4. O som de impacto cai no pouso do elemento, não no início da entrada. Mapa papel → som: rótulo `tick` · título `thump+tap` (hero) · texto `swish` · item `pop` · número `hit` (hero) · chip `tap` · barra `swish` · botão `chime` (hero). Uma família sonora por carrossel; música só se o usuário pedir (CC0, volume baixo, mesma faixa em todos os slides).

## Entradas necessárias
`1-entrada/carrossel.json` (ver `exemplos/carrossel-teste/`). Imagens só se o usuário tiver ou pedir geração. Marca/tema opcional.

## Aceite
- Folha `2-aprovar/carrossel_folha.png` aprovada **antes** de qualquer `--animar`.
- Nenhum texto cortado, sobreposto ou menor que 40 px; um destaque por slide; capa legível em miniatura.
- Slide animado: o estado final é idêntico ao PNG.
- Fatos e números com fonte conferida; número de exemplo deve dizer que é ilustrativo.
- `vf-sound` sem falha no QA (quando o usuário pedir som).

## Teste sugerido
`exemplos/carrossel-teste/carrossel.json` (conceito de basis, números marcados como ilustrativos). `uv run vf carrossel c1-basis --exemplo`.

## Riscos e licenças
- Fontes: Barlow Condensed e IBM Plex Mono são OFL. Sons do sound-layer são CC0.
- Imagens: sem gerador pago por enquanto. Só do usuário ou de fonte livre (CC0/domínio público) com crédito registrado em `1-entrada/imagens/CREDITOS.md`.
- Não copiar arte, texto ou layout de carrossel de terceiros: a referência orienta estrutura e ritmo, não conteúdo.
