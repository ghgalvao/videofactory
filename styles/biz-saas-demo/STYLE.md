# STYLE — Demonstração de SaaS

Status: a criar · Template: `video/saas.html` · 9:16 e 16:9 · 30–60 s · R$ 0

## Quando usar
Mostrar um software resolvendo um problema em poucos cliques: lançamento de funcionalidade, página de vendas, anúncio, onboarding. Serve para produtos próprios e de clientes.

## Roteiro
Dor em uma frase → "olha como fica" → 3 passos na tela (clique → resultado) → resultado final (número ou antes/depois) → CTA (testar, agendar demo).
Exemplo de gancho: "Ainda montando relatório na planilha toda sexta?"

## Planos-tipo
| Plano | Duração | O que aparece | O que muda |
|---|---|---|---|
| Dor | 3–4 s | planilha/papel bagunçado | itens caem/empilham |
| Produto | 3 s | moldura de navegador/celular com a tela inicial | moldura entra |
| Passo | 5–8 s cada | tela + cursor | cursor clica; zoom no elemento; selo explica |
| Resultado | 4–5 s | tela final + número | contador / antes-depois |
| CTA | 3–4 s | logo + URL + botão | botão "pulsa" 1× |

## Visual
- Telas reais do produto (capturas enviadas pelo cliente) **ou** recriadas em HTML com as cores do `marca.json`.
- Moldura de navegador (desktop) ou celular (vertical), sombra suave, fundo com a cor primária da marca.
- Cursor grande e visível, círculo de clique; selos explicativos no estilo do `paper` com cores da marca.
- Dados de exemplo **fictícios e marcados como exemplo** (nunca dado real de usuário).

## Movimento
Cursor com trajetória suave (curva, 0,5–0,8 s); clique com onda; zoom de 1,0 → 1,6 no elemento (0,5 s, `power2.inOut`) e volta; transição de tela por deslize.

## Som
Clique, "whoosh" na troca de tela, "ding" no resultado, música tech leve.

## Entradas necessárias
Capturas das telas (ou URL de ambiente de teste e permissão), roteiro dos 3 passos, `marca.json`, URL do CTA.

## Aceite
Cada passo mostra um clique e um resultado visível; nenhum dado pessoal real na tela; texto da UI legível no celular (zoom quando preciso).

## Teste sugerido
Demonstração fictícia de um app de tarefas (telas recriadas em HTML).

## Riscos e licenças
Capturas só de ambiente de teste ou com dados fictícios (LGPD); marcas de terceiros na tela (integrações) só como aparecem no produto, sem destaque.
