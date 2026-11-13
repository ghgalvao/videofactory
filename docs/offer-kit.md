# Kit de ofertas para varejo — plano de produto

Status: proposta para decisão dos sócios · criado em 10/11/2026.
Pesquisa de mercado com nomes e números: fica fora do repositório, na galeria `kit-ofertas` do painel (ver "Onde está cada coisa").

## 1. A ideia em uma frase

O mercado manda a lista de ofertas da semana e recebe o **kit pronto**: vídeos com locução e capa, carrossel para o feed e encarte para o WhatsApp, tudo com a marca dele. O motor gera as três peças a partir da **mesma lista**.

## 2. Decisão proposta

| Caminho | Situação | Por quê |
|---|---|---|
| **Serviço pronto ("a gente faz por você")** | recomendado | Os concorrentes que anunciam vendem "faça você mesmo" barato. Nenhum anúncio ativo oferece o kit pronto. Ticket maior, poucos clientes já pagam a operação e o motor atual aguenta os primeiros. |
| App próprio (SaaS self-service) | depois | Exige site com login, cobrança recorrente, editor, suporte e render na nuvem. Preço de mercado perto de R$ 68/mês: margem só com volume e tráfego pago. Só começa com clientes do serviço pedindo. |
| Afiliação ao produto de um concorrente | opcional | Renda rápida sem construir, mas o cliente é do produtor. Só vale depois de ver comissão, recorrência e o produto por dentro. |

## 3. Mercado (resumo)

- Biblioteca de Anúncios da Meta, Brasil, 10/11/2026: um produtor de "vídeo de ofertas com locução" tem **44 anúncios ativos**, **38 criados entre 5 e 9/11** (gancho de Black Friday) e cerca de 71 contando variações. Os primeiros, de meados de outubro, seguem no ar.
- Oferta dele: 300 vídeos com locução por **R$ 67,99/mês**, "mais de mil temas", escolha de locutor.
- O mesmo produtor vende uma família de produtos baratos na plataforma de afiliados: encarte com IA por R$ 47,90 (pagamento único, acesso vitalício) e cartaz com IA por R$ 37 a R$ 47,90 (pagamento único). Modelo de infoproduto, não SaaS.
- Pelo menos outros 3 concorrentes com anúncios ativos. O mais estruturado tem plano grátis e Pro a R$ 69/mês (encarte, cartaz, etiqueta e vídeo MP4, sem locução citada).
- Preço âncora que o dono de mercado vê: **grátis a R$ 69/mês, ou R$ 37–48 uma vez**.
- Lacunas: ninguém nos anúncios faz pelo cliente; ninguém cita carrossel para o feed; só um vende locução.
- Os próprios mercados anunciam o mesmo formato: grupo VIP de ofertas no WhatsApp, encarte da semana, vídeos de 17 a 20 s, validade explícita.
- Limite: a Biblioteca não mostra gasto nem alcance de anúncio comercial. Tempo no ar sugere retorno, não prova.
- Estudo completo, com tabela comparativa, análise do anúncio, perguntas em aberto e como atualizar: `saida/kit-ofertas/research/market-ads-library.md`.

## 4. O que o motor tem e o que falta

| Peça | Situação | Detalhe | Esforço |
|---|---|---|---|
| Gerador de vídeo de oferta (`vf oferta`) | temos | Vídeo a partir de `1-entrada/oferta.json` (produtos, preços, WhatsApp, validade, cores) | — |
| Locução | temos | Edge, ElevenLabs ou voz clonada com autorização | — |
| Capa e primeiro quadro | temos | Capa em HTML → PNG, aplicada no início do vídeo | — |
| Efeitos sonoros | temos | `ferramentas/sound-layer/` (1.139 sons CC0, mix presa à animação, −14 LUFS) | — |
| Fila de render e painel | temos | `vf panel`, "Aprovar e animar" em fila | — |
| Foto real do produto | parcial | Campo `foto` existe; falta recorte de fundo automático e encaixe no selo | 1 sessão |
| Logo do cliente | parcial | Campo `logo` existe; testar com logos reais | pequeno |
| Encarte digital | falta | Folha com os produtos da semana: imagem para WhatsApp + PDF para impressão, mesmos temas | 1 sessão |
| Carrossel para o feed | falta | Capa com gancho, card por produto ou categoria, fechamento com WhatsApp e validade, 1080×1350 | 1 sessão |
| Cartaz de gôndola | falta | Cartaz de preço para imprimir | pequeno |
| Temas | falta | Hoje 1 layout com cores trocáveis. Meta: Black Friday, Fim de semana, Sextou, Açougue, Hortifrúti, Bebidas | 1 sessão |
| Formatos 4:5 e 1:1 | falta | Só sai 9:16; feed e anúncio pedem 4:5 | médio |
| Encarte rápido em vídeo | falta | 10 a 20 produtos, 2 a 3 s cada, locução corrida | médio |
| Entrada simples | falta | Lista colada do WhatsApp ou planilha → `oferta.json` com um comando | 1 sessão |
| Música de fundo | falta | Trilha livre por tema (já no backlog do `task-master`) | pequeno |
| Voz com licença comercial | falta | Edge usa acesso não oficial; para vender, serviço com licença comercial clara | pequeno |

Total para o kit completo: **5 a 6 sessões**. Princípio: **uma lista, três entregas** — cada preço é digitado e conferido uma vez.

## 5. Monetização (hipóteses a validar com 3 a 5 mercados)

| Plano | Entrega por semana | Preço a testar | Para quem |
|---|---|---|---|
| Essencial | 1 encarte + 1 carrossel + 2 vídeos com capa | R$ 247/mês | mercadinho, açougue, hortifrúti |
| Completo | 1 encarte + 2 carrosséis + 4 vídeos + cartazes + versão para status | R$ 497/mês | mercado de bairro que já posta toda semana |
| Rede | kit completo por loja | sob consulta | redes de 2 a 6 lojas |

- Custo por peça: render local sem custo por vídeo; encarte e carrossel são imagens (segundos); voz com licença comercial custa centavos por vídeo.
- Custo real é tempo: meta de **30 min por cliente por semana** para o kit inteiro.
- Referência: 10 clientes no Completo ≈ R$ 5 mil/mês com ~5 h de operação por semana.
- Upsell: cartaz impresso, locução para carro de som, anúncio gerenciado.

## 6. Funil

1. **Atenção** — anúncio local ou abordagem direta. Métrica: custo por conversa no WhatsApp.
2. **Conversa** — o dono manda a lista da semana e o logo. Métrica: % que manda a lista.
3. **Amostra em 24 h** — kit com os produtos e preços dele (vídeo com capa, carrossel, encarte). Momento decisivo.
4. **Teste de 2 semanas** — ele posta. Métrica: % que posta a amostra.
5. **Assinatura** — plano mensal recorrente.
6. **Indicação e upsell** — desconto por indicação. Métrica: cancelamento < 10%/mês.

## 7. Anúncios

Os criativos são feitos pelo próprio motor (cada anúncio é demonstração do produto). Ganchos:
- "Uma lista de ofertas. Vídeo, carrossel e encarte prontos."
- "Você manda a lista. A gente devolve o kit amanhã."
- "Mercado que posta vídeo vende mais no fim de semana?" (pergunta, sem prometer número)
- "Black Friday do seu mercado, pronta em 24 horas." (datas fortes: Black Friday, Natal, Páscoa, Dia das Mães, aniversário da loja)

Teste inicial sugerido: R$ 30/dia por 7 dias, um público local, 3 criativos; seguir com o de conversa mais barata.

## 8. Canais

| Canal | Como | Quando |
|---|---|---|
| Venda direta na região | WhatsApp ou visita com a amostra pronta, feita com o encarte que o mercado já publicou | já |
| Anúncio local (Meta) | raio da cidade, criativos acima | com 2–3 clientes de prova |
| Gráficas e agências de encarte | revendem o kit para os clientes delas | fase 2 |
| Distribuidoras e atacadistas | oferecem como benefício aos mercadinhos que atendem | fase 2 |
| Associações comerciais | palestra curta ou condição para associados | fase 2 |
| Plataforma de afiliados | quando houver versão self-service | fase 3 |

## 9. Fases e critérios para avançar

| Fase | Quando | Entregas | Avança quando |
|---|---|---|---|
| 1. Kit completo no motor | semanas 1–2 | foto com recorte, 6 temas, 4:5, encarte e carrossel da mesma lista, entrada pela lista do WhatsApp, voz licenciada | kit de 10 produtos sai em < 20 min de trabalho |
| 2. 5 a 10 clientes | meses 1–2 | venda direta com amostra, preço testado, rotina semanal | 5 clientes pagando, nenhum cancelamento no 2º mês |
| 3. 30 a 50 clientes | meses 3–4 | anúncio local, parceiros, render em fila noturna, um operador | custo de aquisição pago em ≤ 2 meses de assinatura |
| 4. Self-service | mês 5+ | site com login e editor, render na nuvem, cobrança recorrente, afiliados | só com o serviço estável e demanda de quem quer fazer sozinho |

## 10. Riscos

| Risco | Gravidade | Por quê | Como evitar |
|---|---|---|---|
| Preço errado publicado | alta | Pelo CDC, a oferta divulgada obriga o fornecedor | Aprovação do cliente por escrito antes de publicar, sempre; nunca publicar sem o "ok" |
| Licença da voz | alta | Edge é acesso não oficial; plano grátis do ElevenLabs pode não permitir uso comercial | Conferir termos; vender só com voz de licença comercial clara |
| Imagem de marca nos produtos | média | Embalagens e logos de fabricantes são de terceiros | Fotos do próprio mercado; nada que sugira patrocínio da marca |
| Concorrência barata | média | Várias ferramentas < R$ 70/mês | Vender o kit pronto, rapidez e locução, não preço |
| Gargalo de CPU | média | Render de vídeo leva minutos | Fila noturna; > 30 clientes: máquina dedicada ou nuvem |
| Dependência da Meta | média | Bloqueio da conta de anúncio | Venda direta e parceiros como canais fixos |
| Inadimplência e cancelamento | baixa | Comércio pequeno corta custo em mês fraco | Cobrança recorrente automática, relatório mensal do entregue |
| Sazonalidade | baixa | Picos em datas fortes | Pacotes de datas vendidos com antecedência |

## 11. Próximos passos

- [ ] Conferir comissão e regras do produto concorrente na plataforma de afiliados (decide a afiliação como teste paralelo)
- [ ] Conversar com 3 a 5 mercados da região (como divulgam hoje, quanto pagariam)
- [ ] Motor: foto real com recorte e 6 temas
- [ ] Motor: formato 4:5 e encarte rápido em vídeo
- [ ] Motor: lista do WhatsApp → `oferta.json` com um comando
- [ ] Motor: encarte e carrossel a partir da mesma lista
- [ ] Trocar a voz de testes por uma com licença comercial
- [ ] Fazer 3 kits de amostra com encartes reais e oferecer aos mercados

## Onde está cada coisa

- **Este arquivo (repositório do motor):** plano e decisões, versionado para os sócios. Sem nomes de clientes nem de marcas de terceiros (regra do repositório).
- **Tarefas do motor:** `docs/task-master.md`, seção "Fase 7 — Kit de ofertas".
- **Galeria `kit-ofertas` no painel** (`vf panel`, pasta `saida/kit-ofertas/`): briefing, pesquisa de mercado com nomes de concorrentes e links, referência do anúncio e a página visual do plano (`assets/docs/plano.html`).
