---
name: vf-review
description: Revisa os textos dos jobs de um cliente antes de qualquer envio (ortografia, afirmações bloqueadas, números a confirmar, [CONFIRMAR] esquecido, limites da legenda) e grava a revisão no job. Use quando o usuário pedir revisar texto, conferir português, "tem erro?", checar antes de publicar ou digitar /vf-review.
argument-hint: "<cliente> <job...|--all>"
---

# vf-review

```
uv run vf review <cliente> p01-apresentacao p02-caldeiraria     # jobs escolhidos
uv run vf review <cliente> --all                                # todos que têm carrossel.json
```
Lê `1-entrada/carrossel.json` (todo texto de slide), `legenda.txt` e `notas.md`; grava `2-aprovar/revisao.md`.

## O que confere
- **Erro (reprova):** `[CONFIRMAR]` dentro do texto que vai ao público; termo da lista `bloqueados` do `marca.json`; legenda acima de 2200 caracteres ou com mais de 30 hashtags.
- **Aviso:** número ou promessa da lista `atencao` do `marca.json`; título ou texto longo demais para a arte; legenda sem chamada para ação; ortografia (dicionário pt, com o vocabulário do cliente e as tags do catálogo aceitos).
- **Pendências:** linhas com `[CONFIRMAR]`, `PENDENTE` ou `BLOQUEADO` do `notas.md`.

## Regras
- As listas `bloqueados`, `atencao` e `vocabulario` moram no `marca.json` do cliente (modelo: `docs/marca.exemplo.json`). Mude a regra no `marca.json`, não no código.
- O dicionário embutido é de português europeu: palavra correta no Brasil que ele não conhece entra em `vocabulario` (ou em `BR_EXTRA` no código, se valer para todo cliente).
- Revisão limpa não é aprovação: olhe os PNGs (texto cabe? foto certa? pessoa com EPI?) e só então aprove.
- Afirmação que o usuário confirmou (certificação, cliente citado, contato) fica registrada no `marca.json` com a fonte e a data, para a regra deixar de bloquear.
