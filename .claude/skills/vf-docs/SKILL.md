---
name: vf-docs
description: Gera documentos do cliente em PDF (proposta comercial, contrato de prestação de serviços, extrato de serviços, orçamento) a partir de dados estruturados, com valores calculados e por extenso. Use quando o usuário pedir proposta, contrato, extrato, orçamento, "documento para o cliente", PDF, ou digitar /vf-docs.
argument-hint: "<cliente> <presentation|proposal|contract|statement|estimate>"
---

# vf-docs

Documentos ficam em `saida/clients/<cliente>/documentos/` (aba Documentos). Sempre saem em **HTML e PDF**.

## Comandos (de dentro de `videoFactory/`)
```
uv run vf doc new <cliente> <tipo>     # cria documentos/<tipo>.json com o modelo (não sobrescreve)
uv run vf doc build <cliente> <tipo>   # gera documentos/<tipo>-<data>.html e .pdf
uv run vf doc list <cliente>
```
Tipos: `presentation` (apresentação em slides 16:9), `proposal` (proposta), `contract` (contrato), `statement` (extrato), `estimate` (orçamento).

**Apresentação:** `documentos/presentation.json` traz `titulo` e uma lista de `slides`. Cada slide tem um `tipo` (capa, secao, texto, numeros, galeria, tabela, planos, passos, video, cta) e os campos listados em `src/vf/core/slides.py`. Imagens e vídeos são caminhos relativos à pasta do cliente. Use só peças e fotos que já existem nela, com direitos ok no catálogo. `*palavra*` pinta a palavra na cor de destaque. O PDF sai com uma página por slide. No painel, o botão **Ver** abre os slides, e o slide de vídeo toca o vídeo ali mesmo.

## No painel
Cliente na seção **Clientes** do painel ganha a aba **Documentos**: criar dados, editar o JSON, gerar PDF e **baixar PDF**. Mesmas regras de rascunho.

## Fluxo
1. `vf doc new`. Na 1ª vez cria também `saida/agency.json` (quem emite: razão social, documento, representante, cidade, e-mail, telefone, PIX). Preencha uma vez.
2. Preencha o JSON do documento **só com dado confirmado pelo usuário ou lido de fonte** (visão geral do cliente, proposta aprovada, comprovantes). O que não souber fica `[CONFIRMAR]`.
3. `vf doc build`. Total, saldo e valor por extenso são calculados pelo código: nunca digite soma à mão.
4. Se sobrou `[CONFIRMAR]` nos dados do documento ou na `agency.json`, o PDF sai como **RASCUNHO** (marca d'água e `-rascunho` no nome). Só vira final sem marca nenhuma em aberto.
5. Abra o PDF e confira número, nome e data antes de entregar ao usuário.

## Regras
- Valores, prazos, cláusulas e partes vêm do usuário ou de documento anterior dele. Não invente.
- **Conflito entre documentos** (ex.: valor anual diferente no contrato e no extrato) não se resolve sozinho: aponte ao usuário, que decide.
- O modelo de contrato é um ponto de partida, não parecer jurídico: recomende revisão do texto-base por advogado uma vez.
- Documento é uso interno até o usuário decidir enviar. Nunca envie ao cliente.
- Contato, CNPJ e valores ficam só em `saida/` (fora do git). Nada disso entra em código, docs ou exemplos do repo.
- Nota fiscal não é gerada aqui (é fiscal, outro processo).
