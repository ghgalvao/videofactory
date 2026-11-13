---
name: vf-client
description: Abre, organiza e confere a pasta de um cliente do videoFactory no padrão da agência (abas Visão geral, Briefing, Identidade, Social, Documentos, Materiais, Produção). Use quando o usuário falar de cliente novo, "onboarding", "organizar o cliente", "o que falta do cliente X", ou digitar /vf-client.
argument-hint: "<slug> [\"Nome do cliente\"]"
---

# vf-client

Todo cliente vive em `saida/clients/<slug>/` com as mesmas abas do hub da agência. O motor versiona só este padrão; **dado de cliente nunca entra no repo** (regra do CLAUDE.md).

## Padrão (uma pasta, seis abas)
| Aba | Onde | Conteúdo |
|---|---|---|
| Visão geral | `visao-geral.md` | negócio, contatos e quem decide, situação comercial, próximos passos |
| Briefing | `brief.md` | objetivo, público, tom, plataformas, diferenciais, o que não dizer, aprovador |
| Identidade | `marca.json` + `identidade/guia-visual.md` | cores, fontes, logo, tom, CTA e a **forma** da marca (composição, formas, tipografia) |
| Social | `social/plano.md`, `social/calendario.md` | pilares, grid, destaques, datas, frequência, calendário |
| Documentos | `documentos/` | proposta, contrato, extratos |
| Materiais | `assets/{brand,images,video,print,docs}` + `assets/index.json` | arquivos do cliente, catalogados |
| Produção | `<job>/` | cada job com `1-entrada`, `2-aprovar`, `3-final`, `_interno` |

Mais `LEIA-ANTES.md` (uso interno, quem decide, o que ainda não foi combinado), `references/`, `research/`, `exports/`.

## No painel
`uv run vf panel`: todo cliente de `saida/clients/<slug>/` (com `marca.json`) aparece sozinho na seção **Clientes** do menu, com as abas Produção, Visão geral, Briefing, Identidade, Social, Documentos e Materiais. Não precisa registrar nada. A aba **Identidade** é o manual de marca (montado do `marca.json`, do guia visual e das fotos, com Baixar PDF); **Materiais** é o catálogo de fotos com filtros; **Documentos** é uma tabela com Baixar PDF. Textos em markdown aparecem formatados (mesmo motor `marked` do hub) e têm botão Editar.

## Fluxo
1. **Cliente novo:** `uv run vf client new <slug> "Nome"` cria o esqueleto sem sobrescrever nada.
2. **Preencher a partir do que o cliente já tem** (site, impressos, redes, conversa). Não invente: o que não está nas fontes vira `[CONFIRMAR]`.
3. **Conferir:** `uv run vf client check <slug>` mostra o estado de cada aba, o que falta e todos os `[CONFIRMAR]` em aberto. `uv run vf client list` lista todos.
4. Antes de produzir para o cliente: escopo e preço fechados por escrito (aba Visão geral) e aprovador definido (marca.json).
5. Marca e fotos entram por `/vf-brand` e `/vf-assets` quando existirem; carrossel e vídeos leem o `marca.json` (`"client": "clients/<slug>"` no `carrossel.json`).

## Regras
- Cliente existente sem esqueleto: rode `vf client new` (não sobrescreve) e depois mova o que já existe para o lugar certo.
- Contatos, valores e situação comercial ficam só em `visao-geral.md` e `LEIA-ANTES.md` (privados em `saida/`).
- Peça gerada é amostra interna até o usuário decidir levar ao cliente.
- Nada de nome de cliente em código, docs ou exemplos do repo.
