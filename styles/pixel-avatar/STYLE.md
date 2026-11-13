# STYLE — Avatar explicando (pixel art ou ilustrado)

Personagem na metade de baixo da tela que troca de pose a cada passo e mexe a boca com a fala; em cima, contador do passo, título em duas linhas e um cartão por passo (código, lista, botões, comparação).

## Quando usar
Passo a passo, tutorial curto, "N dicas", explicação de conceito com um apresentador fixo. Bom para canal com mascote.

## Formato
9:16 · 25 a 45 s · um passo por frase (2 a 4 s cada) · template `video/pixel-avatar.html` · cena `pixel-avatar`.

## Storyboard
No topo: `"cena": "pixel-avatar"` e `"trilha": ["repo", "nome"]` (texto pequeno no canto).

Por plano:
- `frases`: frases do roteiro que o plano cobre.
- `pose`: `neutro`, `aponta`, `joinha`, `explica`, `cruzado`, `peito` ou `ok`.
- `l1`, `l2`: título em duas linhas (a segunda sai em azul). Não use `t1`: é reservado para tempo.
- `card`: HTML do cartão. Classes prontas: `.card`, `.jan` + `.bar` (janela com bolinhas), `.cod` + `.lin` (linhas de código; `.kw`, `.pv`, `.ok`, `.cm` para cores), `.linha` e `.col` (alinhar), `.tile` (quadrado colorido), `.mini` (cartão pequeno), `.botao`, `.chip`, `.tag`. Elementos com `.in` entram animados; `data-d` é o atraso em segundos.
- `contador: false` esconde o "$ 01/04" (use no gancho e na chamada final).
- `quadro`: segundo do plano usado na folha de aprovação.

## Personagem
- **Pixel art (padrão):** desenhado por código no template (pessoa neutra de blusa). Para outro personagem, troque as cores em `C` ou desenhe outro em `corpo()`.
- **Ilustrado:** bloco `"avatar"` no storyboard com uma imagem por pose (PNG sem fundo) em `1-entrada/imagens/`; boca e piscada desenhadas por cima ou bocas por imagem. Use a skill `/vf-avatar` para gerar e preparar as poses.

## Tema, halo e personagem que flutua
- `theme` (topo do storyboard): troca as cores do fundo creme. Chaves: `bg`, `ink`, `accent` (2ª linha do título, contador), `accentSoft`, `muted`, `line`, `card`, `cardBorder`, `glow` (luz radial atrás do personagem).
- `avatar.halo`: cor do contorno de luz em volta do personagem ilustrado (use quando o personagem é escuro e o fundo também).
- `avatar.float`: `true` ou `{ "amp": 16, "period": 2.6, "sway": 1.5 }`. O personagem flutua sem parar, com sombra no chão que encolhe quando ele sobe.
- `place` por plano: posição do personagem, com deslize de `avatar.glide` segundos (padrão 0,6) entre um plano e o outro. Nomes prontos: `bottom`, `bottom-left`, `bottom-right`, `middle` (grande, para plano sem cartão), `corner-left`, `corner-right` (pequeno, para cartão grande); ou `{ "x": 540, "y": 1840, "scale": 1 }` (x/y = ponto de baixo do personagem).
- Personagem sem boca: omita `boca` na pose. Sem `olhos`, não pisca.
- Exemplo: galeria de mascote em tema escuro com 8 poses e `place` variando a cada plano.
- Boca escondida (cachecol, máscara): `scarf: [x, y, w, h]` na pose; essa região estufa de leve com a fala (`scarfAmt`, padrão 0,05). O balanço do corpo ao falar fica desligado; `avatar.tremor: true` religa.

## Cartões mais ricos (efeitos por peça)
- **Tempo pela frase:** `data-f="N"` faz a peça entrar quando a frase N do roteiro começa (+ `data-d` segundos). Trocar a narração não desmonta o vídeo. Sem `data-f`, `data-d` conta do início do passo.
- **Entrada:** `data-fx` = `pop`, `stamp` (carimbo que bate e treme o palco), `left`, `right`; `data-rot` = rotação final.
- **Mudança no meio do passo:** `data-onf="N"` (ou `data-on` em s) põe `data-state="on"`: `.flag` acende em vermelho, `.riscado` risca, `.dim` apaga.
- **Saída:** `data-outf="N"` (ou `data-out`).
- **Número que conta:** `<span class="count big" data-from="0" data-to="7.2" data-dec="1" data-pre="US$ " data-suf=" bi" data-dur="2">`.
- Peças prontas: `.carimbo`, `.big`, `.addr` (endereço em fonte mono), `.bar-up` (barra de gráfico).
- `trilha: ["", ""]` esconde o texto do canto superior.
- Folha com mais de 8 planos funciona (o `checar` só avisa). Para vídeos de 60–90 s, 12–14 planos.

## Ritmo
- Gancho com pergunta ou promessa e pose `aponta`.
- Uma ideia por passo; o cartão entra logo depois do título.
- Chamada final com `joinha` e sem contador.

## Aceite
- Nenhum cartão cobre o rosto do personagem.
- Título com no máximo ~16 caracteres por linha.
- `vf checar` sem erros e folha aprovada antes de animar.
