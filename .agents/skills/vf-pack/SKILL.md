---
name: vf-pack
description: Monta o pack de conteúdo de um cliente (posts, legendas, revisão, grade do perfil, plano de publicação) em pasta e zip prontos para aprovar. Use quando o usuário pedir "pack", pacote de posts, grid do Instagram, entregar o conteúdo do cliente, ou digitar /vf-pack.
argument-hint: "<cliente> [pack-01] [--inicio AAAA-MM-DD]"
---

# vf-pack

Pack = tudo que o cliente precisa para aprovar e publicar, numa pasta só: `saida/clients/<cliente>/exports/<pack>/` e `<pack>.zip`.

## Fluxo completo (cliente já com marca, catálogo e plano)
1. `/vf-client`, `/vf-brand` e `/vf-assets` feitos (marca.json com `forma`, `assets/index.json`).
2. Um job por post em `saida/clients/<cliente>/pNN-nome/1-entrada/` com `carrossel.json` (`"client": "clients/<cliente>"`, slides com `"asset": "img-NNN"`), `legenda.txt` e `notas.md` (pendências). Texto vem do plano de conteúdo do cliente; afirmação sem fonte ou sem confirmação do usuário não entra.
3. `uv run vf carrossel clients/<cliente>/pNN-nome` por job (post único é 1 slide; story usa `"formato": "story"`; destaques em job `dNN-...`).
4. `uv run vf pack new <cliente>` cria o `pack-01.json` (ordem e títulos; edite).
5. `uv run vf pack build <cliente> --inicio 2026-12-01 --por-semana 3` revisa todos os textos (`/vf-review`), copia PNGs e legendas, gera `grade.png` (como o perfil vai ler), `resumo.md` (status, pendências, plano de publicação) e o zip.
6. Job com erro de revisão aparece **BLOQUEADO** e não entra no pacote até corrigir.

## No painel
`uv run vf panel`: cada post aparece como cartão com a capa e a gaveta mostra os slides, legenda, notas, revisão e **Baixar tudo (zip)**; o pack aparece na aba **Social** do cliente com a grade e o botão de baixar o zip.

## Regras
- Publicar do último para o primeiro: o Post 1 fica no canto superior esquerdo do perfil.
- Nada é enviado ao cliente pelo pack: é amostra interna até o usuário decidir. Aprovação final é humana.
- Foto de pessoa só com EPI completo e autorização de imagem; material sem foto confirmada fica como PENDENTE no `notas.md`.
- Escopo, preço e aprovador fechados por escrito antes de entregar (`/vf-docs`, aba Documentos).
