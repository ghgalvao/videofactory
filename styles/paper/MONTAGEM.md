# Paper montável — como escrever o storyboard.json

Template genérico: `video/paper.html`, montado por `src/vf/core/paper.py`. **Não editar HTML por vídeo**: tudo vem do `storyboard.json`.
Exemplo completo e validado: `styles/paper/exemplos/e1-mar-salgado/storyboard.json`.

## Passo a passo de um vídeo (qualquer modelo consegue)
1. Copiar o roteiro de `saida/JOB/1-entrada/direcao.md` para `saida/JOB/1-entrada/roteiro.txt` (números por extenso). **Deixar uma linha em branco antes da frase do CTA** (vira pausa de 0,7 s na voz).
2. `uv run vf narrate saida/JOB/1-entrada/roteiro.txt --nome JOB --engine edge --modelo small`
3. Escrever `saida/JOB/1-entrada/storyboard.json` (formato abaixo), um plano por linha da tabela de direção.
4. `uv run vf storyboard JOB` → olhar `2-aprovar/storyboard_folha.png` → corrigir posições → repetir → **aprovação**.
5. `uv run vf storyboard JOB --animar` → `3-final/video.mp4`.

## Estrutura
```json
{"cena": "paper",
 "legenda": {"texto": "#1b1f2a", "destaque": "#c0261f"},
 "substituicoes": [{"de": "trinta e cinco gramas", "para": "35 g"}],
 "planos": [{"id": 1, "frases": [1, 2], "quadro": 99, "elementos": [ ... ]}]}
```
- `frases`: números das frases do roteiro (frase termina em . ? !) que cabem no plano. Planos em ordem, sem buracos.
- `quadro`: segundos após o início do plano para a foto da folha; `99` = fim do plano (tudo já montado).
- Para a folha 4×2, usar **8 planos**.
- `dy` (opcional, padrão 50): desloca todos os elementos para baixo, para equilibrar com a legenda.

## Elemento (posição pelo CENTRO, quadro 1080×1920)
Campos comuns: `tipo`, `x`, `y`, `w` (largura), `s` (tamanho da fonte), `rot` (graus), `cor`, `entrada`, `frase`+`atraso` **ou** `t`, `efeito`.
- Tempo: `"frase": 3` entra no início da frase 3 (+`atraso`, padrão 0,1 s). Sem `frase`: `"t": 0.6` = segundos após o início do plano.
- `entrada`: `cima`, `baixo`, `esquerda`, `direita`, `bate` (carimbo), `cai` (com quique), `cresce`, `pop`.
- `efeito` (0,6 s após entrar): `tremor`, `balanca`, `pulsa`.
- Texto: `*palavra*` = marca-texto amarelo; `\n` = quebra de linha.

| tipo | campos próprios | padrão |
|---|---|---|
| `faixa` | `texto` | papel rasgado com 2 fitas, w 920, s 120 |
| `selo` | `texto` | papel menor com 1 fita, w 440, s 70 |
| `carimbo` | `texto` | vermelho, s 90, rot −6 |
| `texto` | `texto` | itálico Georgia, w 900, s 54 |
| `objeto` | `nome`, `rotulo` | SVG: `copo`, `pedra`, `nuvem`, `sol`, `mar`, `rio`, `graos`, `seta` (girar com `rot`) |
| `calendario` | `topo`, `grande`, `sub` | cabeçalho vermelho, w 680, s 220 |
| `barras` | `titulo`, `max`, `linhas[{rotulo, valor, texto?, cor, frase, atraso}]` | barra proporcional a `max`; sem `texto`, o valor sobe em contador |
| `numero` | `valor`, `dec`, `pre`, `suf` | contador gigante vermelho, s 300 |
| `etiqueta` | `topo`, `grande` | CTA, w 640 |

## Regras de composição (receita `STYLE.md`)
- Zona de conteúdo: y entre ~350 e ~1400 (topo livre para a interface do app; legenda em ~1670).
- No máximo 4 elementos por plano; 1 foco por vez; carimbo por último.
- Centro vertical do plano ≈ y 900 (o `dy` já soma 50).
- **Nunca usar a classe `.clip` num contêiner de plano** sem `.plano.clip` (a margem da legenda empurrava tudo 60 px à direita). Evitar sobrar vazio grande entre o conteúdo e a legenda.
- Objeto novo no SVG: adicionar em `objeto_svg()` de `core/paper.py` (traço branco de adesivo: `ST`).
