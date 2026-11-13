---
name: vf-assets
description: Cataloga as imagens e vídeos de um cliente (assets/index.json) com assunto, tags, uso, pessoas, direitos e qualidade, e acha o arquivo certo para cada peça. Use quando o usuário falar de fotos do cliente, "organizar as imagens", "qual foto usar", materiais do site ou impressos, ou digitar /vf-assets.
argument-hint: "<cliente> [scan|sheet|set|find]"
---

# vf-assets

Todo carrossel, post ou vídeo de cliente escolhe a imagem **pelo catálogo**, nunca por nome de arquivo solto. Ordem de fontes: material do cliente (site, impressos, pasta de portfólio) → busca livre (`/vf-images`) → pedir ao usuário.

## Comandos (de dentro de `videoFactory/`)
```
uv run vf assets scan <cliente>                  # indexa assets/{images,video,print,brand}
uv run vf assets sheet <cliente> [--novos]       # folhas numeradas em exports/assets-folha-N.png
uv run vf assets set <cliente> img-034 img-035 --subject "..." --tags a,b --use cover,proof --people yes --rights ok --note "..."
uv run vf assets find <cliente> --use cover --orient vertical --min media --tag guindaste
```
`scan` mantém o que já foi descrito, numera novos arquivos, marca **duplicatas** (hash perceptual), **vazios** (imagem lisa) e a qualidade (alta ≥ 1600 px no lado maior, média ≥ 900, baixa abaixo).

## Fluxo
1. Copie os arquivos do cliente para `assets/images/<origem>/`, `assets/video/`, `assets/print/`, `assets/brand/`.
2. `scan`, depois `sheet --novos`. **Olhe cada folha** com a ferramenta de imagem.
3. Para cada item (ou grupo) rode `set`: `subject` em uma frase do que se **vê**; `tags` curtas; `use` entre `cover`, `background`, `detail`, `proof`, `team`, `logo`, `discard`; `people yes|no`; `rights ok|confirm`; `note` com o que checar.
4. Lixo (máscara, colagem, logo em fundo branco, imagem estourada) recebe `--use discard`: o `find` nunca devolve descartados, vazios nem duplicatas.
5. Peça nova: `find` com o filtro, escolha, e cite o `id` no job. Foto de qualidade `baixa` só entra como fundo escurecido.

## Regras de direitos e segurança
- `rights ok` só para material que o cliente enviou ou publicou como dele. Banco de imagens do site, rosto reconhecível e logo de terceiros ficam `confirm` até haver autorização por escrito.
- Pessoa em obra: confira EPI completo antes de usar; sem EPI, descarte.
- Não use logos de clientes do cliente sem autorização deles.
- Original maior existe? Peça ou procure antes de usar um arquivo `baixa` em destaque.
- O catálogo mora em `saida/clients/<cliente>/assets/index.json` (fora do git). Nada de cliente em código, docs ou exemplos do repo.
