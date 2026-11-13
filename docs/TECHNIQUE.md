# TECHNIQUE — como o videoFactory funciona por dentro

Estilo e direção: `styles/*/STYLE.md`, `docs/DIRECTOR.md`. Estilos listados: `uv run vf estilos`.

## Versões fixadas
Python 3.12 (uv) · HyperFrames 0.9.13 · GSAP 3.15.0 (local em `video/assets/vendor/`) · Three.js 0.160.1 (UMD, local) · faster-whisper (int8, CPU) · yt-dlp 2026.10.26 · FFmpeg 9.0.2.

## Pipeline
0. **Estrutura do job** (`saida/<job>/`): `1-entrada/` (roteiro, direcao, storyboard.json, imagens) · `2-aprovar/` (folha) · `3-final/` (video.mp4) · `_interno/` (narração, tempos, cache, temporários). Ver `saida/LEIA-ME.md`. Código em `core/paths.py` (`Job`); jobs antigos migram com `vf organizar --todos`.
1. `vf narrate roteiro.txt --nome JOB [--engine edge|kokoro] [--modelo small]` → `_interno/narration.wav` + `_interno/words.json` (todas as palavras do roteiro, com tempo). Linha em branco no roteiro = pausa de 0,7 s (Edge).
   - Texto = roteiro; tempo = Whisper; casamento por `difflib` (`core/timing.py`). Palavras sem par são interpoladas.
2. `1-entrada/storyboard.json` (`cena`, `legenda`, `substituicoes`, `planos[frases, quadro]`; 3D: `cam`, `estado`, `tag`, `passo`).
3. `vf storyboard JOB` → `hyperframes snapshot --at ... --keep` → `2-aprovar/storyboard_folha.png` (4×2).
4. `vf storyboard JOB --animar` → `hyperframes render` em `_interno/` → movido para `3-final/video.mp4` ao terminar.

## Voz
- **Edge `pt-BR-AntonioNeural`, +15 %** (serviço online não oficial; checar termos antes de monetizar). 124 palavras ≈ 49 s.
- **Kokoro** local (pf_dora, pm_alex, pm_santa): artificial. Exige espeak-ng; `misaki` troca o espeak pelo embutido (sem pt-BR), por isso `tts/kokoro.py` força o instalado.
- **ElevenLabs**: planejado (chave só no `.env` local; nunca no chat).
- Whisper `medium` estourou memória uma vez → usar `--modelo small`.

## Como o HTML é gerado
`core/hyperframes.gerar_html` lê o template, injeta grupos de legenda (palavras, tempo), animações GSAP e `__DADOS__`. Cenas 2D declaram cada plano com `data-start="__S{n}_T0__"`. Cenas 3D leem `DADOS.shots` e desenham em `draw(t)` (função pura do tempo; o `tl.to(estado.t)` do GSAP chama `draw` a cada seek).

## Regras do HyperFrames que já nos mordem
- Todo elemento temporal precisa de `data-start`/`data-duration`; timeline registrada em `window.__timelines["main"]`.
- Sem `Math.random`, `Date.now` ou fetch (use PRNG com semente fixa).
- Tempos de plano são **absolutos** na timeline; tweens de plano usam `T(i)=shots[i].t0`.

## Armadilhas conhecidas
- **pnpm dentro de `video/` escreveu no lockfile da raiz do monorepo** → `video/pnpm-workspace.yaml` isola o projeto. Não rode `pnpm add` fora dele.
- Nome de variável repetido em `<script>` (ex.: `contorno`) derruba a cena inteira (quadro em branco). Conferir a folha após cada mudança.
- Aba do Chrome (Claude in Chrome) trava com vídeo tocando: usar aba nova; capturar com o vídeo pausado.
- Fonte "Arial Black" cai em fallback no render; Impact e Georgia funcionam.
- `snapshot --describe` envia quadros ao Gemini: **não usar**.
- **Vídeo todo preto, só legenda, e MP4 pequeno (~1 MB para 45 s)** = erro de sintaxe no `<script>` da cena. Causa comum: patch em Python com `'\n'` dentro de string JS vira quebra de linha real. Conferir com `node --check` no script extraído de `video/index.html` e olhar a folha antes do render.
- **Div temporal vazia ganha altura total** no HyperFrames: rótulo com `translateY(-50%)` sai centenas de px fora do lugar. Dar altura fixa e posicionar com `top` explícito.
- **O runtime controla `visibility` dos elementos temporais** (ex.: `.clip` da legenda): para esconder num trecho, usar classe no `#root` com `display:none !important`, não `style.visibility`.
- **Comando interrompido no meio** (render + mux) pode deixar `video.mp4` igual ao `video-sem-som.mp4`: refazer o mux e conferir o sincronismo (correlação do áudio do MP4 com o `mix.wav`, offset 0 ms).
- **Voz externa (ElevenLabs etc.):** converter para `_interno/narration.wav` (mono, 24 kHz, s16), apagar `_interno/whisper.json`, transcrever e alinhar ao `roteiro.txt` (`transcrever` + `alinhar`), conferir 0 palavras interpoladas e recalcular as cues de som pelo início de cada frase. O plano grátis do ElevenLabs não tem licença comercial e bloqueia chamadas pelo conector MCP ("unusual activity"): gerar no site, com plano pago para cliente.
- **PDF não toca vídeo** fora do Acrobat: no slide `video` da apresentação use `link` (YouTube não listado ou Drive) na capa e no botão. Testar o link sem login (`curl` deve dar 200; o Drive com `usp=drive_link` restrito dá 401).

## Desempenho (CPU, esta máquina)
Narração 4 s ≈ 3 s (Kokoro) · Whisper small 49 s de áudio ≈ 35 s · render 3D 43 s de vídeo ≈ 140 s · render papel 49 s ≈ poucos minutos.

## Próximos itens técnicos
Efeitos sonoros/música e mixagem · modo 16:9 · `marca.json` por cliente · `vf watch <link>` (baixar + quadros + transcrição) · montagem de pasta de imagens (Ken Burns).

## Decisão (06/11/2026)
- **Voz fica por último.** Foco nos vídeos: estilos, roteiro, storyboard e som. Voz provisória: Edge `pt-BR-AntonioNeural`.
- Ideias de voz para depois: Chatterbox ou OpenVoice no Colab, ElevenLabs, voz própria.

## Comandos que economizam token (06/11/2026)
- `vf novo <estilo> <job>`: cria o job com roteiro-modelo e storyboard-esqueleto do estilo (`styles/<estilo>/roteiro.modelo.txt`, `storyboard.modelo.json`; hoje só `paper`).
- `vf checar <job>`: valida por script, sem imagem: frases cobertas, tipos/entradas válidos, margens, centro vertical, duração dos planos, dígitos no roteiro, pausa antes do CTA. `--completo` roda também o `hyperframes check`. Pegou um erro real no E1 (CTA entrando uma frase cedo).
- Fluxo barato: `vf novo` → preencher roteiro e storyboard → `vf narrate` → `vf checar` (corrigir) → `vf storyboard` → aprovação → `--animar`.
- Modelo: Opus para construir template de estilo novo; Sonnet para produzir; sessão nova por vídeo.
