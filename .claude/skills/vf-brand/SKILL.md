---
name: vf-brand
description: Extrai a identidade de um cliente (cores medidas, fontes, logo, forma da marca) de site, impressos e logo, grava marca.json e identidade/guia-visual.md, e faz os modelos de arte usarem essa forma. Use quando o usuário pedir identidade visual do cliente, "padrão visual", "usar a cara da marca", analisar flyer, folder, site ou perfil, ou digitar /vf-brand.
argument-hint: "<cliente> [fonte: flyer, folder, site, logo]"
---

# vf-brand

Marca não é só cor. O que dá a cara é a **forma**: ângulos, etiquetas, faixas, tipografia, uso de foto. Esta skill mede o que dá para medir e descreve o resto olhando o material do cliente.

## Fontes, em ordem de confiança
1. Impressos que o cliente já usa (flyer, folder, cartão): é a identidade em uso.
2. Site no ar (CSS em `repos/` ou captura de tela).
3. Logo e manual de marca, se existirem (vetor sempre que houver).
4. Perfil de rede social.

## Fluxo
1. Reúna as fontes em `saida/clients/<cliente>/assets/{print,brand,images}`.
2. **Meça as cores** (de dentro de `videoFactory/`): `uv run vf brand colors <imagem> --k 7`. Rode no flyer, na capa do folder e na captura do site. Separe o que é marca do que é foto: foto traz cores soltas.
3. **Olhe o material** (imagem aberta, não só os números) e descreva em `identidade/guia-visual.md`: formas e composição, tipografia, cor e fundo, fotografia, faça e não faça.
4. **Grave `marca.json`** (modelo em `docs/marca.exemplo.json`): `cores`, `fontes` com licença, `logo` (arquivo dentro de `assets/`), `tom`, `cta`, `proibidos`, e o bloco `forma`:
   ```json
   "forma": {"fundo": "diagonal", "degrade": ["#claro", "#meio", "#escuro"], "inclinacao_graus": -14,
             "etiqueta": "inclinada", "caixa_alta": true, "faixa_translucida": true}
   ```
   `degrade` são os três tons do fundo medidos no impresso. Com `forma`, o carrossel usa fundo diagonal, etiquetas e faixas inclinadas e título em caixa alta; sem `forma`, usa o tema escuro liso.
5. **Teste em uma peça real** (`vf carrossel <job>` com `"client": "clients/<cliente>"`) e compare lado a lado com o impresso. Ajuste `forma`/`guia-visual` até bater.
6. `uv run vf client check <cliente>`: a aba Identidade precisa estar `ok` e sem valor inventado.

## Regras
- Valor medido recebe a fonte ("medido no flyer"); valor estimado recebe `[CONFIRMAR]`. Diferença entre impresso e site (ex.: laranja do flyer vs do site) vai anotada, e o site manda no digital.
- Fonte do cliente sem licença livre: use a parecida livre e avise. Fonte do site em OFL entra direto.
- Logo vetorial sempre que existir; PNG só transparente e grande. Nunca recorte logo de PDF em fundo branco.
- Não use logos de clientes do cliente sem autorização deles.
- Dado de cliente fica só em `saida/` (fora do git); nada de nome de cliente em código, docs ou exemplos do repo.
