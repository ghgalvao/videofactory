# Vídeos para empresas, marcas e SaaS

Como transformar um cliente em vídeos usando as receitas de `styles/biz-*`. Direção geral: `docs/DIRECTOR.md`.

## 1. Qual receita para qual objetivo

| O cliente quer... | Receita | Estilo base |
|---|---|---|
| ser conhecido / apresentar a empresa | `biz-brand-intro` | paper, whiteboard |
| explicar um produto físico | `biz-product-explainer` | blueprint, mechanism-3d |
| mostrar um software | `biz-saas-demo` | saas (a criar) |
| provar resultado | `biz-social-proof` | paper, data-infographic |
| lançar algo ou fazer oferta | `biz-launch` | paper |
| manter o perfil vivo toda semana | `biz-tips-faq` | animated-caption, paper |

## 2. Briefing (10 perguntas, antes de qualquer roteiro)
1. O que a empresa vende, em uma frase?
2. Quem compra (cargo, setor, região)?
3. Qual dor o cliente do cliente tem antes de comprar?
4. Quais são os 3 diferenciais reais (com prova)?
5. Que números a empresa pode mostrar publicamente?
6. Qual é o tom de voz (técnico, próximo, divertido, sério)?
7. O que **não** pode ser dito (promessas, concorrentes, preços)?
8. Onde os vídeos vão rodar (Instagram, YouTube, site, anúncio) e em quais formatos?
9. Qual a ação desejada no fim (WhatsApp, site, orçamento, teste grátis)?
10. Quem aprova (nome) e em quanto tempo responde?

## 3. Identidade: `marca.json`
Um por cliente, em `Clientes/<Cliente>/video/marca.json` (modelo: `docs/marca.exemplo.json`).
Campos: nome, cores (primária, secundária, destaque, fundo, texto), fontes (título, corpo) **com licença**, logo (SVG/PNG transparente), tom, CTA, contatos, proibidos.
Os templates trocam os tokens fixos pelos do `marca.json`. Fonte sem licença livre ou fornecida pelo cliente → usar uma fonte livre parecida e avisar.

## 4. Portões de aprovação (cliente)
1. **Briefing + roteiro** (texto) → aprovado por escrito.
2. **Folha do storyboard** (`vf storyboard JOB`) → aprovada.
3. **Vídeo final** → até 1 rodada de ajuste incluída; mudança de roteiro depois do portão 1 é retrabalho.
Aprovação sempre da pessoa definida no briefing (pergunta 10).

## 5. Checklist legal e de reputação
- [ ] Logo, fotos, nomes e números **enviados ou autorizados** pelo cliente (guardar a autorização).
- [ ] Depoimento: autorização de nome, cargo, imagem e citação (LGPD).
- [ ] Preço e condições exatamente como o cliente escreveu (CDC).
- [ ] Afirmação comparativa ou de desempenho com comprovação; sem citar concorrente.
- [ ] Setores regulados (saúde, financeiro, alimentos) revisados pelo cliente e pelas regras do conselho/órgão do setor.
- [ ] Dados de tela (SaaS) fictícios ou de ambiente de teste.
- [ ] Música e efeitos com licença para uso comercial.

## 6. Entregáveis padrão
Por vídeo: MP4 9:16 (Reels/Shorts/TikTok); opcionais 1:1 e 16:9; legenda `.srt`; capa (frame escolhido); texto do post com CTA e hashtags.
Por série (`biz-tips-faq`): calendário com temas e datas, vinheta própria.

## 7. Escopo antes de produzir
Quantidade de vídeos, receitas, formatos, prazos, rodadas de ajuste e preço **fechados por escrito antes de começar**. Material de amostra para proposta é marcado como "exemplo" e não é entregue como produto.
