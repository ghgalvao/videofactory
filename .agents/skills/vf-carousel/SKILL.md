---
name: vf-carousel
description: Cria um carrossel vivo (slides 4:5 animados com som) no videoFactory: expande um pedido curto em carrossel.json, gera PNGs para aprovar, anima e prepara o som. Use quando o usuário pedir carrossel, "carrossel animado", "carrossel com motion", slides de Instagram ou digitar /vf-carousel.
argument-hint: "<tema ou pedido curto> [galeria] [--ref <link|arquivo>] [--fidelidade baixa|media|alta] [--slides N] [--tom didatico|viral|expert]"
---

# vf-carousel

## Quando usar
Quando o usuário quer um carrossel de Instagram/LinkedIn que prenda o feed: cada slide é uma mini-animação (texto, elementos e som no tempo certo), entregue como PNG estático **e** MP4 por slide. Padrão do vídeo "Carrosséis VIRAIS com Motion Graphics por R$0": o modelo escreve código, não vídeo.

## Como usar
```
/vf-carousel "spot × futuros: o que é basis" minha-galeria --slides 6 --tom didatico
/vf-carousel "mesmo estilo deste" minha-galeria --ref saida/minha-galeria/references/files/print-01.png --fidelidade media
```

## A escada de 7 níveis (suba só até onde o pedido pede)
| Nível | O que é | Neste repo |
|---|---|---|
| 1 | Prompt solto | evite: resultado genérico |
| 2 | **Regras fixas + prompt bom** | `styles/carrossel-vivo/REGRAS.md` (leia sempre) + este skill expande o pedido |
| 3 | Referência visual (site, print, carrossel salvo) | `--ref`; o skill analisa com `/vf-reference` |
| 4 | **Skill** que melhora o prompt | este arquivo |
| 5 | Imagens | **sem Higgsfield nem gerador pago por enquanto.** Precisa de imagem? Use `/vf-images` (Openverse e Wikimedia Commons, só licença livre, crédito em `1-entrada/imagens/CREDITOS.md`); sem achar boa, peça ao usuário. Entra em `1-entrada/imagens/` e no campo `imagem` |
| 6 | Sistema próprio: ghostwriter por tom, brand kit, nº de slides, fidelidade, galeria de inspirações | flags acima, `marca.json`, `saida/<galeria>/references/` |
| 7 | **Aprender com o que o usuário gostou** | salvar bons carrosséis como referência (passo 6) |

## O que faz
1. **Ler:** `styles/carrossel-vivo/REGRAS.md`, `styles/carrossel-vivo/STYLE.md` e, se houver galeria, `saida/<galeria>/references/index.json` (o "por que gostei" de cada referência orienta layout e ritmo). Marca do cliente: no `carrossel.json` use `"client": "clients/<cliente>"` e o carrossel lê `saida/clients/<cliente>/marca.json` (cores, fonte do título, logo; modelo em `docs/marca.exemplo.json`). Dado de cliente fica só em `saida/`, nunca no repo. O `tema` do JSON ainda vence. Foto do cliente: `"asset": "img-079"` no slide pega do catálogo (`/vf-assets`). Marca com bloco `forma` (`/vf-brand`) ganha fundo diagonal, etiquetas inclinadas e título em caixa alta.
2. **Expandir o pedido** (o que o vídeo chama de melhorar o prompt). Responda em 5 linhas antes de escrever: público, promessa da capa, nº de slides (padrão 6–7, máx. 10), ritmo (`rapido|medio|calmo`), tom. Pedido vago? Decida você, avise a decisão; só pergunte se mudar o resultado de forma cara (imagens pagas, fato que você não consegue conferir).
3. **Copy:** escreva o texto segundo o tom (`didatico`, `viral`, `expert`, `storyteller`). Fatos e números com duas fontes conferidas (use `/vf-research` se o tema pede); número de exemplo marcado como ilustrativo. Legenda do post (≤ 5 linhas + CTA) vai em `1-entrada/legenda.txt`.
4. **Montar** `1-entrada/carrossel.json` (modelo: `styles/carrossel-vivo/exemplos/carrossel-teste/carrossel.json`). Tipos: `capa`, `texto`, `lista`, `numero`, `cta`. Cada slide = uma ideia.
5. **PNG primeiro:** `uv run vf carrossel <job>` → olhe você mesmo `2-aprovar/carrossel_folha.png` (texto cortado? capa legível em miniatura? um destaque por slide?). Corrija, regere, **mostre ao usuário e espere o OK**.
6. **Animar** (depois do OK): `uv run vf carrossel <job> --animar` → `3-final/animado/NN.mp4` e `_interno/som/cues.json`. Confira um MP4 (quadros com ffmpeg ou `snapshot`): o estado final tem de ser igual ao PNG.
7. **Som** (se o usuário quiser): `uv run vf carrossel <job> --som` gera os cues por slide, mixa com o sound-layer (-14 LUFS) e junta ao MP4 (original fica em `NN-sem-som.mp4`). Depois rode o QA por slide (`cd ferramentas/sound-layer; uv run scripts/qa.py <mp4> --audio <_interno/som/mix-NN>`) e relate o resultado como está: o ouvido final é do usuário.
8. **Aprender:** se o usuário gostou, `/vf-reference saida/<galeria>/<job>/3-final/png/01.png <galeria>` e pergunte "por que gostou?". Sem galeria, crie a pasta de referências: o nível 7 é isso.

## Entrega
`3-final/png/*.png` (postar), `3-final/animado/*.mp4` (postar como vídeo-carrossel; com som após `--som`), `2-aprovar/carrossel_folha.png`, `1-entrada/legenda.txt`, e uma nota curta: decisões tomadas, o que é ilustrativo, o que ficou abaixo do ideal.

## Regras
- Nunca animar sem a folha aprovada. Nunca usar gerador de imagem pago; imagem só do usuário ou de fonte livre com crédito.
- Não copiar arte, texto ou layout de carrossel de terceiros; referência orienta estrutura e ritmo.
- Mudou só o texto? Edite o JSON e regere; não mexa no template. Pedido que o template não cobre (slide novo, entrada nova) → edite `video/carrossel.html` e `core/carrossel.py:SOM`, e confira a folha.
- O tempo de cada elemento vem de `montar_slide`; nunca edite o `cues.json` à mão (som e imagem se separam).
- Rodar um render por vez (o HyperFrames usa `video/index.html` compartilhado).

## No painel
Job com `1-entrada/carrossel.json` aparece no painel como carrossel (capa, N slides, status: `a aprovar` com PNG, `pronto` com MP4 animado). A gaveta mostra os slides, a legenda, as notas, a revisão e o zip.
