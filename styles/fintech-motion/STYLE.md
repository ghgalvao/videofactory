# STYLE — Fintech motion (interface escura)

Status: testado (v0, interno) · Template: `video/fintech.html` + `core/fintech.py` · 9:16 · 25–40 s · R$ 0
Origem: validação do formato de reel de app financeiro (06/11/2026). Marca e texto do teste são fictícios (GastoZap).

## Quando usar
Anúncio ou explicação de produto digital (fintech, SaaS, app): uma dor do dia a dia → o produto resolvendo. Liga com `biz-saas-demo`.

## Roteiro
Dor com número (salário, saldo) → o "jeito antigo" falhando (planilha esquecida) → virada ("o problema nunca foi X, foi Y") → o produto em ação (conversa no WhatsApp) → CTA "em breve".

## Elementos (storyboard.json, cena "fintech")
`mini` · `frase` (g = grande verde) · `rotulo` · `saldo` (de → ate, contar_frase) · `moedas` (some_frase) · `calendario` · `planilha` · `carimbo` · `celular` (msgs de bot/eu, áudio) · `callout` (texto + alvo [x,y], linha fina com ponto).
Entradas: `pop`, `baixo`, `cima`, `fade`, `bate`, `abre`.

## Visual
Fundo `#06080b` com grade fina (54 px) e brilho radial vermelho/verde sutil; verde `#3ddc84` para o positivo e destaque; vermelho `#ff5a5a` para perda/alerta; cartões brancos de interface; legenda branca grossa com sombra, palavra falada em verde.
Fontes de sistema (Segoe UI, Consolas). Callouts em monoespaçada.

## Movimento
Entradas suaves de 0,4–0,55 s; contador do saldo desce em ~1,8 s; moedas somem uma a uma (0,16 s de intervalo); linhas de callout se desenham em 0,4 s; mensagens do celular entram na fala correspondente.

## Som
(a fazer) clique, "ding" no registro, whoosh nas trocas; música tech leve.

## Aceite
Cada número tem origem no roteiro; nenhum dado real de pessoa; marca fictícia identificada no teste; celular sem espaço vazio grande.

## Pendências
Preencher o espaço vazio do celular; som; versão 16:9; registrar em `vf estilos`.

## Riscos e licenças
Peça de produto financeiro: não prometer resultado; regras de publicidade (CDC e do setor). Não copiar texto nem marca de terceiros.
