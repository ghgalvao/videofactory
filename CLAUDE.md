# CLAUDE.md — como usar o videoFactory

Você (Claude) está no **motor** de vídeos curtos. O usuário traz um tema ou roteiro; você conduz o fluxo até o MP4 em `saida/<job>/3-final/`. Responda no idioma do usuário (o projeto é em português).

## Primeira coisa ao abrir o repo

1. Confira o ambiente antes de qualquer vídeo:
   ```powershell
   uv --version; ffmpeg -version | Select-Object -First 1; node --version; pnpm --version
   ```
   Faltou algo? Passe ao usuário os comandos de instalação do [README.md](README.md) (winget). Não instale nada sem pedir.
2. Se `.venv/` ou `video/node_modules/` não existem: `uv sync` e `cd video; pnpm install`.
3. Teste rápido: `uv run vf estilos` (lista estilos). Se funcionar, o motor está pronto.

## Fluxo de um vídeo (sempre nesta ordem)

```
tema → roteiro → narração → checar → folha de aprovação → [usuário aprova] → render
```

| Passo | Comando | Saída |
|---|---|---|
| Criar job do estilo | `uv run vf novo <estilo> <job>` | `saida/<job>/1-entrada/` com roteiro e storyboard-modelo |
| Escrever roteiro | editar `1-entrada/roteiro.txt` (ver `docs/DIRECTOR.md`) | uma frase por linha; linha em branco = pausa |
| Narrar | `uv run vf narrate saida/<job>/1-entrada/roteiro.txt --nome <job> --engine edge --modelo small` | `_interno/narration.wav`, `words.json` |
| Montar storyboard | editar `1-entrada/storyboard.json` (receita em `styles/<estilo>/STYLE.md`) | planos por frase |
| Checar | `uv run vf checar <job>` | erros de roteiro, tempo e margem |
| Folha | `uv run vf storyboard <job>` | `2-aprovar/storyboard_folha.png` |
| Render | `uv run vf storyboard <job> --animar` | `3-final/video.mp4` |

Regras do fluxo:
- **Portão de aprovação:** mostre a folha (`2-aprovar/`) e espere o OK do usuário antes do `--animar`. Render custa minutos.
- Olhe a folha você mesmo antes de mostrar (texto cortado, sobreposição, card cobrindo o rosto). Corrija e regere.
- `<job>` é o nome relativo a `saida/` (ex.: `meu-video` ou `cliente/meu-video`), nunca o caminho completo.
- Mudou só o storyboard? Não precisa narrar de novo. Mudou o roteiro? Narre de novo (o cache de voz reaproveita frases iguais).
- Estrutura de pastas do job: [docs/JOBS.md](docs/JOBS.md). O usuário só precisa abrir `2-aprovar/` e `3-final/`.
- Para o usuário ver e organizar os vídeos: `uv run vf panel` (galerias em `galleries.json`, fora do git). Guia para humanos: `guide.html`.

## Skills do motor

Em `.claude/skills/` (documentadas na página Skills do painel): `/vf-video` (fluxo completo), `/vf-script` (roteiro), `/vf-adjust` (ajuste sem refazer), `/vf-batch` (série em lote), `/vf-research` (estudo com fontes), `/vf-reference` (analisar referência), `/vf-voice` (voz), `/vf-sound` (efeitos), `/vf-avatar` (personagem), `/vf-carousel` (carrossel vivo 4:5 com som; comando `vf carrossel`), `/vf-images` (busca imagens livres com crédito), `/vf-client` (pasta e abas de cada cliente; comando `vf client`), `/vf-docs` (proposta, contrato, extrato e orçamento em PDF; comando `vf doc`), `/vf-assets` (catálogo de fotos e vídeos do cliente; comando `vf assets`), `/vf-brand` (identidade e forma da marca do cliente; comando `vf brand colors`), `/vf-review` (revisão de texto do cliente; comando `vf review`), `/vf-pack` (pack de posts com grade e plano de publicação; comando `vf pack`). Quando o pedido do usuário bater com uma delas, siga a skill.

Skills do HyperFrames (`/hyperframes`, `/hyperframes-cli`) ficam em `.claude/skills/`, copiadas de `video/node_modules/hyperframes/dist/skills/` (mesma versão fixada, 0.9.13). Use ao criar ou editar templates em `video/*.html`. **As regras deste repo vencem** (formato do vídeo, estilos, pasta de jobs); ao subir a versão do pacote, recopie as pastas. A `media-use` (puxa HeyGen) não foi copiada.

## Leitura antes de dirigir um vídeo

1. [docs/DIRECTOR.md](docs/DIRECTOR.md): roteiro, fatos, ritmo, checklist final.
2. `styles/<estilo>/STYLE.md`: receita do estilo (campos do storyboard, duração por plano).
3. Um exemplo em `styles/<estilo>/exemplos/` (roteiro + storyboard + folha prontos para copiar).
4. Só se algo quebrar: [docs/TECHNIQUE.md](docs/TECHNIQUE.md) (armadilhas do HyperFrames, desempenho).

Catálogo de estilos e quando usar cada um: [docs/ESTILOS.md](docs/ESTILOS.md), [docs/CATALOGO.md](docs/CATALOGO.md).

## Vozes (`--engine`)

| Motor | Quando usar | Observação |
|---|---|---|
| `edge` | padrão, testes, lotes | online, grátis, rápido. `--voz pt-BR-AntonioNeural` |
| `kokoro` | offline | local, qualidade menor em PT |
| `voicebox` | voz clonada ou desenhada | precisa do app Voicebox aberto (API em 127.0.0.1:17493); lento em CPU. Direção por frase em `1-entrada/direcao_audio.json` (ver docstring de `src/vf/tts/voicebox.py`) |

- Voz clonada **só de quem autorizou por escrito**. Nunca clone voz de pessoa pública, dublador ou personagem.
- Amostras de voz ficam em `voices/` (fora do git). Nunca faça commit delas.
- `--modelo small` no Whisper se a máquina tiver pouca memória.

## Estilo avatar explicando (`cena: "pixel-avatar"`)

Template `video/pixel-avatar.html`: fundo claro, contador do passo, título em 2 linhas, um cartão HTML por passo e um avatar na metade de baixo que troca de pose por passo e mexe a boca com a fala.

Campos por plano: `frases`, `pose`, `l1`, `l2` (título; **não use `t1`**, é reservado para tempo), `card` (HTML; classes `.card .jan .bar .cod .kw .pv .ok .cm .lin .tag .linha .col .tile .mini .botao .chip`; `.in` com `data-d` anima a entrada), `quadro`, `contador: false` para esconder o contador. No topo do storyboard: `trilha: ["repo", "nome"]`.

Dois modos de avatar:
- **Pixel art (padrão):** desenhado por código no template; poses `neutro aponta joinha explica cruzado peito ok`.
- **Ilustrado:** `storyboard.avatar` com uma imagem PNG (fundo transparente) por pose em `1-entrada/imagens/`:
  ```json
  "avatar": { "escala": 1.35, "centro": 540, "base": 1920, "poses": {
    "explica": { "arquivo": "personagem-explica.png", "w": 521, "h": 660, "cx": 304,
                 "boca": [304, 228, 34], "bocaAlt": 12, "olhos": [[233,168,42,19],[332,165,27,20]],
                 "pelo": "#232325", "bocas": { "meio": "personagem-explica-meio.png", "aberta": "personagem-explica-aberta.png" } } } }
  ```
  `cx` = x do centro do rosto (fica alinhado em `centro`); `boca` = [x, y, largura]; `olhos` = [x, y, largura, altura] para a piscada; `pelo` = cor da pálpebra. Sem `bocas`, a boca é desenhada por cima; com `bocas`, troca a imagem (as variações precisam ser idênticas à pose fora da boca).
  Gerar poses: mesma referência de personagem, mesmo enquadramento (busto), fundo branco liso. Recorte o fundo (flood fill a partir das bordas) e corte na cintura antes de usar.

## Som (efeitos)

`ferramentas/sound-layer/` (ver o README de lá). Fluxo: `sfx.py browse` para escolher sons → `cues.json` → `mix.py` → `qa.py video.mp4 --audio <pasta>`.
- Rode os scripts **de dentro de** `ferramentas/sound-layer/` com caminhos **relativos e sem acento** (o `mix.py` lê o JSON sem UTF-8).
- O kit (`sfx.py kit`) baixa pacotes CC0; alguns sites exigem download manual em `audio/kit/_raw/`. Peça ao usuário, não contorne bloqueios.
- Guarde o vídeo sem som também (`3-final/video-sem-som.mp4`).

## Regras do repositório

- **Código novo em inglês:** nomes de arquivos, pastas, variáveis, funções, rotas e chaves JSON. Textos para o usuário seguem em português. Não renomeie o legado em português sem pedido.

- **Identidade do cliente sempre:** toda peça de cliente leva a marca do `marca.json` dele. Carrossel, apresentação e documentos já leem sozinhos; no vídeo, `"client": "clients/<slug>"` no storyboard aplica a cor de destaque (legenda, selos, cena), as cores e a fonte do template (`TEMA_POR_CENA` em `modes/storyboard.py`) e a logo. Não copie cor à mão no job; `tema` no storyboard só para o que a marca não cobre (ex.: azul do fluxo frio). Template novo de vídeo: registrar as variáveis dele em `TEMA_POR_CENA`.
- **Multiagente:** `AGENTS.md` (Codex e outros), `GEMINI.md` e `.github/copilot-instructions.md` apontam para este arquivo. Skills: fonte em `.claude/skills/`, cópia em `.agents/skills/` (Codex). Mudou uma skill: rode `uv run python ferramentas/sincronizar-skills.py` no mesmo commit.
- **Motor agnóstico:** nada de cliente, marca, canal ou nome pessoal em código, docs ou exemplos do repo. Dados de marca ficam na pasta de trabalho do usuário (`marca.json`, ver `docs/marca.exemplo.json`). Antes de commitar: `git diff --cached | grep -i <nomes do usuário/cliente>`.
- Fora do git (já no `.gitignore`): `saida/`, `voices/`, `video/assets/job|app|brand/`, `_arquivo/`.
- Dependências: Python só via `uv`; Node só via `pnpm` e só dentro de `video/`.
- Não envie frames ou vídeos do usuário para serviços externos (ex.: análise por IA na nuvem) sem pedir.
- Não baixe binários externos (ex.: Rhubarb para lip sync) sem pedir.
- Commit e push só quando o usuário pedir.

## Armadilhas rápidas

- Caminho com acento quebra ffmpeg/JSON em alguns scripts: prefira caminhos relativos.
- `vf storyboard` reclama "rode antes `vf narrate`": falta `_interno/narration.wav` ou `words.json` (ou o nome do job veio com `saida/` na frente).
- Card muito alto cobre o rosto do avatar: reduza o conteúdo ou o `padding` do card.
- Render lento: feche outros apps; CPU é o gargalo (ver `docs/TECHNIQUE.md`).
