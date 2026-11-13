# STYLE — Oferta de varejo (modelo parametrizado)

Status: pronto (v1) · Template: `video/oferta.html` · Comando: `vf oferta <job>` · 9:16 · 12–25 s · R$ 0

## Quando usar
Ofertas semanais e datas comerciais de comércio local: açougue, mercado, padaria, hortifruti, loja.
Um modelo, vários clientes: troca nome da promoção, produtos, preços, logo, WhatsApp e cores.

## Como usar
1. `uv run vf oferta <job>` — na 1ª vez cria `1-entrada/oferta.json` de exemplo (use `--exemplo` para já gerar com ele).
2. Edite **só o `oferta.json`** (roteiro.txt e storyboard.json são regerados a cada execução).
3. Fotos e logo em `1-entrada/imagens/` e o nome do arquivo no JSON (`"foto": "costela.png"`, `"logo": "logo.png"`).
   PNG com fundo transparente fica melhor. Vazio = placeholder ("SUA LOGO AQUI" / desenho de tábua com carne).
4. `uv run vf oferta <job>` gera narração + folha em `2-aprovar/`; `--animar` gera o vídeo em `3-final/`.

## Campos do oferta.json
| Campo | Exemplo | Observação |
|---|---|---|
| linha1 / linha2 | "SEXTOU" / "NO AÇOUGUE" | título 3D (linha2 em branco) |
| placa | "OFERTA RELÂMPAGO" | placa de madeira da abertura |
| chamada | "Sextou no açougue! Oferta relâmpago!" | fala da abertura (vira 1 frase só) |
| produtos[] | nome, fala, preco "19,90", unidade kg/un/pct/lt/dz, foto | 1 plano por produto; preço falado "19 reais e 90 o quilo" |
| cta / whatsapp / validade | "Chama no WhatsApp…" / "(64) 9…" / "domingo" | plano final |
| cores | fundo0/1/2, ouro1/2, borda | identidade do cliente |
| voz / taxa | pt-BR-AntonioNeural / "+20%" | locução de varejo, rápida |

## Planos (gerados)
Abertura (logo + título 3D com blur + placa) → um plano por produto (título no topo, etiqueta, foto sobe, selo de preço bate e pulsa) → CTA (título, barra de WhatsApp pulsando, validade).
Fundo: gradiente radial + raios girando + brilho pulsando. Sem legenda (vídeo visual + locução).

## Limites
- Foto de produto vem do cliente ou de banco livre; o motor não gera nem recorta foto.
- Sem música/efeitos (motor ainda não tem).
- Não copiar arte de terceiros: o modelo tem identidade própria; troque as cores por cliente.
