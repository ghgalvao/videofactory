# STYLE — Papel (colagem editorial 2D)

Template: `video/paper.html` (montável). Exemplos: `styles/paper/exemplos/` (o `imposto-seletivo` foi feito no template antigo e fica só como referência visual). Formato 9:16 (1080x1920). Melhor para notícia, dados, comparação.

## Visual
- **Mesa**: kraft `#c9a877` com textura gerada por código (ruído + fibras, semente fixa → determinístico).
- **Peças de papel**: `#f4efe3` com textura própria, sombra dupla (curta e dura + longa e macia), rotação leve (-2° a +3°), borda rasgada por `clip-path` irregular, fita adesiva amarela semitransparente.
- **Tinta**: `#1b1f2a`. **Carimbo**: vermelho `#c0261f`, borda 12 px, texto Impact caixa-alta, `mix-blend-mode: multiply`, filtro `feTurbulence + feDisplacementMap` para borda "suja". **Marca-texto**: amarelo `#ffd23f` em `skewX(-4°)`, nasce da esquerda (`scaleX 0→1`).
- **Tipografia**: Impact (títulos, números), Georgia (corpo, jornal). Fontes do sistema; sem CDN.
- **Objetos**: formas SVG chapadas com contorno branco grosso (efeito adesivo recortado) e sem marca real (lata "REFRI", garrafa "CERVEJA", maço "CIGARRO").
- **Legenda**: tarja de papel com borda 6 px de tinta e sombra dura, Impact 92 px, **no máximo 2 palavras**, levemente rotacionada (-1,2°). Palavra falada em vermelho, o resto em tinta. Números em dígitos (`substituicoes` do storyboard), mesmo que a voz fale por extenso.

## Movimento
- Peça entra com `back.out(1.6)` em 0,5 s (de baixo, de cima ou de lado, variando).
- Carimbo "bate": escala 2,4→1, 0,28 s, `back.out(2.2)`, opacidade final 0,92.
- Calendário e etiquetas: `bounce.out`.
- Barras crescem em 0,9 s (`power3.out`) **no instante da frase que fala daquela barra**; o número sobe junto (contador).
- Tremor curto (±8 px, 5 repetições) em destaque forte (ex.: o número mais alto).
- Proibido: fade lento, zoom lento sem motivo, mais de 2 elementos entrando juntos.

## Composição
- Zona segura: topo livre até y≈200, legenda em y≈1670; conteúdo entre 230 e 1500.
- **Centralizar o bloco de cada plano na vertical** (falha conhecida da v1: sobrou vazio no terço de baixo).
- Um assunto por plano; 3 a 6 s por plano (planos com gráfico podem ir a 12 s se a fala percorre vários itens).

## Planos-tipo
Gancho (objetos caem + faixa de título) · Documento (recorte de jornal + marca-texto) · Conceito (carimbo + selos colados) · Data (folha de calendário) · Dados (gráfico de barras sincronizado) · Destaque (barra gigante + número) · Ressalva (carimbo "medida provisória" + "?") · CTA (etiqueta + "segue!").

## Limites
Sem som ainda. Gráficos precisam de dado confirmado em fonte oficial. Sem rostos nem marcas de terceiros.
