# Estilos do videoFactory

Lista viva: `uv run vf estilos` (fonte: `src/vf/estilos.py`). Atualize os dois ao criar um estilo.

**Receitas fixas:** cada estilo tem `styles/<pasta>/STYLE.md` (índice em `styles/README.md`): 11 de conteúdo e 6 para empresas (`biz-*`, guia em `docs/RECEITAS-EMPRESA.md`). A tabela abaixo é o resumo; a receita é a fonte de verdade.

## Fluxo padrão (todos os estilos)
1. `roteiro.txt` em `saida/JOB/` (frases curtas; números por extenso para a voz).
2. `uv run vf narrate saida/JOB/roteiro.txt --nome JOB --engine edge --modelo small` → `narration.wav` + `words.json`.
3. `saida/JOB/storyboard.json`: `cena`, `legenda` (cores), `substituicoes` (fala por extenso → numeral na legenda) e `planos` (`frases`, `quadro`; câmera/estado quando 3D).
4. `uv run vf storyboard JOB` → `storyboard_folha.png`. **Aprovar antes de animar.**
5. `uv run vf storyboard JOB --animar` → `video.mp4`.

## Estilos
| Estilo | Status | Formato | Melhor para |
|---|---|---|---|
| papel (colagem 2D) | **testado**, aprovado | 9:16 | notícia, dados, comparação |
| panela (3D brinquedo ou premium, campo `look`) | pronto | 9:16 | mecanismos, como funciona |
| legenda animada / legenda ass | pronto | 9:16 | base rápida |
| ken burns (motion comic) | planejado | 16:9 e 9:16 | pasta de imagens de IA + zoom/pan |
| bonequinho + imagens | planejado | 16:9 e 9:16 | narrador 2D sobre imagens |
| foto de arquivo (documental) | planejado | 16:9 | true crime/história (atenção à licença das fotos) |
| quadro branco, blueprint | planejado | 9:16 | explicar processos |

## Como criar um estilo novo
1. Copiar `video/paper.html` (2D, DOM + GSAP) ou `video/panela.html` (3D).
2. Um bloco por plano com `data-start="__S{n}_T0__"` e `data-duration="__S{n}_D__"`; tempos das frases em `DADOS.frases`.
3. Registrar em `src/vf/estilos.py` e nesta tabela.

## Pendências conhecidas
- Centralizar verticalmente o conteúdo do estilo papel; efeitos sonoros e música; modo 16:9.
- Voz: Edge `pt-BR-AntonioNeural` (serviço não oficial; checar termos) ou ElevenLabs (chave só no `.env` local).
- Fatos: conferir números de notícia na fonte oficial antes de postar.
