---
name: vf-images
description: Busca imagens e vídeos de licença livre (CC0/domínio público, ou CC BY com crédito) para um job do videoFactory, escolhe olhando as miniaturas, baixa e registra o crédito. Use quando o usuário pedir imagem, foto, vídeo de apoio, b-roll, "acha uma imagem/vídeo de X", fundo para o carrossel ou digitar /vf-images.
argument-hint: "<o que a imagem mostra> <job> [--licencas cc0,pdm,by,by-sa] [--orientacao tall|wide|square]"
---

# vf-images

Imagens: `ferramentas/imagens/buscar.py`. Vídeos: `ferramentas/imagens/buscar_video.py` (seção "Vídeos" no fim).

## Quando usar
Qualquer job (carrossel, ken-burns, documentary, fintech...) que precise de foto ou ilustração real. **Sem gerador pago por enquanto** (Higgsfield e similares fora). Ordem de preferência: imagem que o usuário já tem → busca livre → pedir ao usuário.

## Como usar
```
/vf-images "moedas de bitcoin sobre fundo escuro" minha-galeria/c1-basis
/vf-images "gráfico de candles" minha-galeria/c1-basis --licencas cc0,pdm,by --orientacao tall
```

## O que faz
1. **Traduzir o pedido em 2–3 consultas** curtas, em inglês e em português (as fontes são majoritariamente em inglês). Use o que a imagem *mostra*, não o conceito abstrato ("coins on dark table", não "arbitragem").
2. **Buscar** (de dentro de `videoFactory/`):
   ```
   uv run python ferramentas/imagens/buscar.py buscar "<consulta>" --n 12 --out saida/<job>/_interno/busca
   ```
   Fontes: Openverse e Wikimedia Commons, sem chave. Padrão só `cc0,pdm`. `by`/`by-sa` só se o usuário aceitar dar crédito na legenda; **nunca** `nc`/`nd`. Resolução mínima 1000 px de largura.
3. **Olhar as miniaturas** (`cand-NN.jpg`) com a ferramenta de imagem e escolher você: tema certo, sem marca d'água, sem logo de terceiros, sem rosto de pessoa identificável (a menos que o usuário peça), composição que aguenta texto por cima (o template escurece o fundo a 38 %). Nenhuma boa? Refine a consulta uma vez; depois **peça ao usuário** descrevendo o que procurou.
4. **Baixar** a escolhida:
   ```
   uv run python ferramentas/imagens/buscar.py baixar saida/<job>/_interno/busca/candidatos.json <n> --para saida/<job>/1-entrada/imagens --nome fundo-capa
   ```
   Isso grava o arquivo e acrescenta fonte, autor e licença em `1-entrada/imagens/CREDITOS.md`.
5. **Usar:** carrossel → campo `imagem` do slide (`"imagem": "fundo-capa.jpg"`). Outros estilos → `arquivo` do elemento `imagem` no storyboard.
6. Se a licença é `BY`/`BY-SA`, **copie a linha de crédito para `legenda.txt`** do post e avise o usuário.

## Entrega
Arquivo em `1-entrada/imagens/`, linha em `CREDITOS.md`, e uma frase: o que foi escolhido, a licença e se há crédito obrigatório.

## Regras
- Confira a licença **na página de origem** (`pagina` no candidato) quando o crédito for obrigatório ou a foto tiver pessoas/marcas.
- Não baixe de Google Imagens, Pinterest, redes sociais nem banco com licença própria. Só as fontes do script (ou o que o usuário mandar).
- Nunca invente autor ou licença. Sem dado, escreva "autor desconhecido" (o script já faz isso).
- Não guarde as imagens de busca fora do job; `_interno/busca` pode ser apagada depois.
- Só a consulta sai da máquina. Não coloque nome de cliente, projeto ou dado privado na consulta.

## Vídeos (b-roll, fundo em movimento)
Mesmo fluxo (consulta curta → candidatos → olhar o poster `cand-NN.jpg` → baixar → crédito), com `buscar_video.py`:
```
uv run python ferramentas/imagens/buscar_video.py buscar "stock market trading" --n 10 --max-seg 60 --out saida/<job>/_interno/busca_video
uv run python ferramentas/imagens/buscar_video.py baixar saida/<job>/_interno/busca_video/candidatos.json <n> --para saida/<job>/1-entrada/videos --nome b-roll-1
```
- Fontes sem chave: **Wikimedia Commons** (qualidade irregular, muito conteúdo jornalístico e institucional) e **Internet Archive** (acervo de domínio público: filmes antigos, institucionais; relevância fraca, **sempre olhar o poster** e, se preciso, abrir a `pagina`).
- **Pexels: desligado por decisão do usuário (13/11/2026), sem chave. Não use `--licencas ...pexels` e não peça a chave.** O código existe (liga só com `PEXELS_API_KEY` e a licença `pexels` pedida) para quando o usuário decidir usar.
- Padrão `cc0,pdm`. `by`/`by-sa` exigem crédito na legenda (o script avisa). Nunca `nc`/`nd`.
- Commons costuma entregar `.ogv`/`.webm`: converta para MP4 antes de usar no HyperFrames: `ffmpeg -i in.ogv -c:v libx264 -pix_fmt yuv420p -an out.mp4`.
- Arquivo grande? Confira duração e tamanho antes de baixar; `--max-seg` descarta clipes longos quando a fonte informa a duração (Archive não informa).
- Vídeo com áudio de terceiros (voz, música): descarte ou tire o som (`-an`); não misture música de terceiros sem licença própria conferida.
- **Carrossel:** coloque o arquivo em `1-entrada/videos/` e use `"video": "nome.mp4"` no slide. O `vf carrossel` converte para MP4 sem áudio no formato 4:5 (aceita `.ogv`/`.webm`, não precisa converter antes). Clipe mais curto que o slide: o fundo some no fim, escolha um de 4 s ou mais. Para só um quadro parado: `ffmpeg -ss 2 -i clip.mp4 -frames:v 1 fundo.jpg` e use como `imagem`.
