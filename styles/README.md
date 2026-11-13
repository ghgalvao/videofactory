# Receitas por estilo

Cada pasta tem um `STYLE.md` fixo (modelo: `_TEMPLATE.md`). A receita separa **o visual e o som** (fixos) da **história** (que muda a cada vídeo).

Antes de produzir, ler nesta ordem: `docs/DIRECTOR.md` (direção) → `styles/<estilo>/STYLE.md` (receita) → `docs/TECHNIQUE.md` (técnica). Para clientes: `docs/RECEITAS-EMPRESA.md`.

## Estilos de conteúdo

| Pasta | Melhor para | Template | Status | Teste |
|---|---|---|---|---|
| `paper` | notícia, dados, comparação | `video/paper.html` | **testado** | E1 |
| `mechanism-3d` | como aparelhos funcionam | `video/panela.html` (`look`: brinquedo ou premium) | pronto | E2 |
| `animated-caption` | citação, lista, volume | `video/template.html` | pronto | E3 |
| `simple-caption` | rascunho, conferir voz/tempo | ffmpeg + `.ass` | pronto | E3 |
| `whiteboard` | conceito e processo | `video/quadro.html` | a criar | E4 |
| `blueprint` | máquina, obra, instalação | `video/blueprint.html` | a criar | E5 |
| `data-infographic` | economia, estatística | `video/dados.html` | a criar | E6 |
| `stick-figure` | história/curiosidade com narrador | `video/boneco.html` | a criar | E7 |
| `ken-burns` | narração longa com imagens de IA | comando de montagem | a criar | E8 |
| `carrossel-vivo` | carrossel de Instagram animado, com som por slide | `vf carrossel` → `video/carrossel.html` (4:5) | pronto | C1 |
| `documentary` | biografia, história | `video/documental.html` | a criar | E9 |

## Receitas para empresas, marcas e SaaS

| Pasta | Objetivo do cliente | Estilo base | Teste |
|---|---|---|---|
| `biz-brand-intro` | apresentar a marca | paper ou whiteboard | B1 |
| `biz-product-explainer` | explicar um produto físico | mechanism-3d ou blueprint | B2 |
| `biz-saas-demo` | mostrar um software funcionando | `video/saas.html` (a criar) | B3 |
| `biz-social-proof` | depoimento, caso de sucesso | paper ou data-infographic | B4 |
| `biz-launch` | lançamento, novidade, oferta | paper | B5 |
| `biz-tips-faq` | série de dicas e FAQ | animated-caption ou paper | B6 |

Toda receita de empresa lê a identidade do cliente em `marca.json` (modelo: `docs/marca.exemplo.json`).

## Exemplos
Cada estilo testado tem `exemplos/<job>/` com `video.mp4` (versão leve, 540 px), `folha.jpg` (folha de aprovação), `roteiro.txt` e `storyboard.json` (e `direcao.md` quando houver). Use como referência visual e como modelo de storyboard. Imagens de entrada não vão junto.
