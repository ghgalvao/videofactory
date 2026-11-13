# videoFactory

> Usando com o Claude Code: abra o Claude na pasta do repo. Ele lê o [CLAUDE.md](CLAUDE.md) e conduz instalação e fluxo.

Motor local de vídeos curtos por **estilos**. Você escreve (ou pede ao Claude) um roteiro; o motor narra, marca o tempo de cada palavra, monta as cenas a partir de um `storyboard.json`, gera uma **folha de aprovação** e, depois de aprovada, renderiza o MP4.

```
roteiro.txt → narração (Edge TTS) → tempos por palavra (Whisper) → storyboard.json → folha de aprovação → vídeo (HyperFrames)
```

## Estado atual

| Item | Situação |
|---|---|
| Motor e 15 estilos | Funcionando, instalação **nativa no Windows** |
| Exemplos por estilo | `styles/<estilo>/exemplos/` (vídeo leve, folha, roteiro, storyboard) |
| Docker | **Ainda não.** Em construção (ver Roadmap) |
| MCP (usar pelo chat do Claude) | **Ainda não.** Em construção |
| Pasta de trabalho fora do motor | **Ainda não.** Hoje os vídeos saem em `saida/` dentro do projeto |
| Som (efeitos) | Funcionando via `ferramentas/sound-layer` (efeitos CC0, mix e QA). Música ainda não |
| Fontes | Os templates ainda usam fontes do Windows; troca por fontes livres em andamento |

## Instalação nativa (Windows 10/11)

No PowerShell, uma vez:

```powershell
winget install astral-sh.uv
winget install Gyan.FFmpeg
winget install OpenJS.NodeJS.LTS
npm install -g pnpm
```

Feche e abra o terminal. Na pasta do projeto:

```powershell
uv sync                         # Python 3.12 e dependências
cd video; pnpm install; cd ..   # HyperFrames (render)
```

O primeiro uso baixa o modelo do Whisper (uma vez). Use `--modelo small` se faltar memória.

## Uso

```powershell
uv run vf estilos                                   # lista os estilos e onde está a receita de cada um
uv run vf novo paper meu-video                      # cria o job com roteiro e storyboard-modelo do estilo
uv run vf narrate saida/meu-video/1-entrada/roteiro.txt --nome meu-video --engine edge --modelo small
uv run vf checar meu-video                          # valida roteiro, tempos e margens
uv run vf storyboard meu-video                      # gera a folha em 2-aprovar/
uv run vf storyboard meu-video --animar             # renderiza o vídeo em 3-final/
uv run vf oferta minha-oferta --exemplo             # vídeo de oferta de varejo a partir de oferta.json
uv run vf panel                                     # painel local: galerias, etapa de cada job e player
```

Estrutura de cada job (`1-entrada`, `2-aprovar`, `3-final`, `_interno`): [docs/JOBS.md](docs/JOBS.md).

Guia com passo a passo marcável e galeria dos exemplos: abra `guide.html` no navegador.

## Onde está cada coisa

```
src/vf/         CLI e núcleo (montadores de cena, narração, legenda, render)
video/          templates HyperFrames (*.html) e assets fixos (vendor, fontes)
styles/         uma pasta por estilo: STYLE.md (receita) + exemplos/
docs/           direção (DIRECTOR), técnica (TECHNIQUE), estilos, catálogo, receitas para empresas, PRD, tarefas
models/         yunet.onnx (detecção de rosto do `vf cut`)
```

Para criar um vídeo bom, leia nesta ordem: `docs/DIRECTOR.md` → `styles/<estilo>/STYLE.md` → um exemplo em `styles/<estilo>/exemplos/`.

## Roadmap (para o uso em rede, cada pessoa com seus tokens)

1. Fontes livres embutidas no projeto (fim da dependência de fontes do Windows).
2. Motor gravando na **pasta de trabalho** do usuário, com `marca.json` lido pelos templates.
3. Servidor **MCP** + comando `init`: o Claude roda numa pasta de trabalho qualquer e chama o motor.
4. Imagem **Docker** com tudo dentro (Python, Node, FFmpeg, Chromium, Whisper), com GPU NVIDIA quando houver.
5. Som: música e efeitos livres de direitos, mixados com a narração.

Tarefas detalhadas: [docs/task-master.md](docs/task-master.md).
