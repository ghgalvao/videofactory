# DIRECTOR — como dirigir um vídeo no videoFactory

Regras de história, ritmo, câmera e checagem. Vale para todos os estilos (`styles/*/STYLE.md`). Técnica e comandos: `docs/TECHNIQUE.md`.

## 1. Roteiro
- **Gancho nos primeiros 3 s**: pergunta que a pessoa quer responder, ou contradição ("a parte de trás da geladeira é quente, se ela serve pra gelar?"). Nunca "Oi, hoje eu trago 5 dicas".
- Estrutura: **gancho → problema → solução (passo a passo) → prova/dado → ressalva → CTA**.
- Frases curtas (até ~15 palavras), uma ideia por frase, linguagem falada. 12 a 16 frases para ~40 s.
- **Números por extenso** no texto da voz ("sessenta e seis vírgula sete por cento"); o numeral aparece na legenda via `substituicoes`.
- Termo técnico só depois de explicado; cada termo novo ganha um selo.
- **Pausa antes do CTA**: deixar uma **linha em branco** no `roteiro.txt` antes da chamada final (o motor Edge insere 0,7 s de silêncio por linha em branco). Vale também antes de uma virada forte.
- Fechamento: ressalva honesta (ex.: "é medida provisória, pode mudar") e CTA curto.
- **Duração-alvo 35–45 s** (Reels/Shorts). Acima de 50 s só se cada plano tiver mudança visual.

## 2. Fatos e ética (antes de renderizar)
- Todo número vem de fonte oficial ou de duas fontes que concordam. Se divergirem, **marcar no roteiro e conferir** antes de publicar (ex.: cigarro 66,7%).
- Sem marcas, logos ou rostos de terceiros. Fotos só com licença. Sem voz clonada sem autorização por escrito.
- Cliente: texto, logo e fotos só com autorização dele; escopo e preço fechados antes de produzir.

## 3. Storyboard (portão de aprovação)
- Quebrar o roteiro em **6–8 planos** (`frases` por plano em `storyboard.json`).
- **Mudança visível a cada 3–6 s**; nunca dois planos seguidos com o mesmo enquadramento.
- Todo termo do roteiro tem selo/destaque **no instante em que é dito**.
- Gerar a folha (`vf storyboard JOB`) e **só animar após aprovação**.

## 4. Ritmo e câmera
- Entrada de elemento: 0,3–0,6 s, seca (`back.out`/`bounce.out`), nunca fade lento.
- No máximo 2 elementos novos por vez; o olho precisa de um ponto de foco.
- Câmera: um movimento por plano (dolly, orbit, zoom curto), 0,6 s para trocar de plano.
- Momento de impacto (número forte, ressalva): tremor curto + carimbo.

## 5. Som (a implementar)
- Voz limpa (Edge Antonio +15% ou ElevenLabs) normalizada em −14 LUFS.
- Efeitos: carimbo, papel, "pop" do selo, whoosh de troca de plano. Música baixa livre de direitos (−22 LUFS) sem competir com a voz.
- Sem som, a nota máxima do vídeo fica em "bom"; com som, "profissional".

## 6. Checagem final (checklist)
- [ ] Gancho em ≤ 3 s e pergunta/contradição.
- [ ] Nenhum plano > 6 s sem mudança (exceto gráfico sincronizado à fala).
- [ ] Todo termo tem selo no tempo da fala.
- [ ] Personagem/elementos dentro do quadro; legenda dentro da margem segura; conteúdo centralizado.
- [ ] Números iguais aos da fonte; ressalva presente.
- [ ] Voz natural; sem corte de palavra no fim.
- [ ] Quadro conferido em 8 pontos do vídeo antes de entregar.
- [ ] Se algo falhar: corrigir uma vez; se continuar, simplificar o plano em vez de insistir.
