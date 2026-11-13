# videoFactory: instruções para agentes (Codex, Gemini, Copilot, Cursor e outros)

As regras do projeto valem para qualquer agente e estão em **[CLAUDE.md](CLAUDE.md)**. Leia esse arquivo inteiro antes de qualquer tarefa; onde ele diz "Claude" ou "Claude Code", entenda "o agente".

## Skills
- As mesmas skills ficam em dois lugares: `.claude/skills/` (Claude Code, **fonte**) e `.agents/skills/` (Codex e agentes do padrão Agent Skills, **cópia**).
- Para mudar uma skill: edite em `.claude/skills/` e rode `uv run python ferramentas/sincronizar-skills.py`. Nunca edite a cópia.
- Como chamar: no Claude Code, `/vf-video`; no Codex, `$vf-video` (ou `/skills` para escolher). O agente também escolhe a skill sozinho quando o pedido bate com a descrição dela.

## O que o agente precisa conseguir fazer
- Rodar comandos no terminal (`uv run vf ...`, `ffmpeg`, `pnpm` dentro de `video/`).
- **Ver imagens**: a folha de aprovação (`2-aprovar/storyboard_folha.png`) e os quadros do vídeo precisam ser olhados antes de renderizar e antes de entregar. Sem isso, o fluxo de aprovação não funciona.
- Pesquisa na web é opcional (skills de pesquisa e referência).
- Conectores (ElevenLabs, navegador) são opcionais; a voz pode vir de Edge, Kokoro, Voicebox ou de um arquivo de áudio externo (ver `docs/TECHNIQUE.md`).
