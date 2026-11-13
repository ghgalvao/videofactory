---
name: vf-avatar
description: Prepara um personagem para o estilo pixel-avatar do videoFactory (prompts de poses para gerador de imagem, recorte de fundo, marcação de olhos e boca, bloco "avatar" do storyboard). Use quando o usuário quiser um personagem explicando, mandar poses ou folha de personagem, ou digitar /vf-avatar.
argument-hint: "<prompts|prepare> <pasta das imagens ou da folha> [job]"
---

# vf-avatar

## Quando usar
Para ter um personagem que troca de pose a cada passo e mexe a boca com a fala, a partir de imagens geradas por você.

## Como usar
```
/vf-avatar prompts assets/characters/mascot-sheet.png
/vf-avatar prepare saida/science-channel/assets/characters science-channel/why-sky-is-blue
```

## Ferramenta de imagem (fora do motor)
O motor não gera o personagem: a folha de referência e as fichas de poses (e de bocas) saem de uma ferramenta de imagem externa, e o motor só recorta, marca e anima.
- **Recomendada: Google Flow** (ou o Gemini com edição de imagem, que usa o mesmo modelo). Mantém o personagem consistente a partir de uma folha anexada; peça a referência com peso alto (60 a 70%).
- Alternativas: ChatGPT (imagens), Midjourney (com referência de personagem). Escolha **uma** por personagem e não troque no meio.
- **Poses:** gere cada pose a partir da mesma folha, em busto, fundo branco liso, boca fechada, 3:4. Gere 2 a 4 variações e escolha a mais fiel.
- **Bocas:** use **edição** da imagem da pose (não geração nova): pedir para mudar só a boca. Geração nova muda roupa, cabelo ou ângulo e a boca não encaixa (aconteceu nos testes).
- Salve tudo em `assets/characters/` da galeria, com o nome da pose no arquivo (`aponta.png`, `aponta-boca-aberta.png`).
- Licença: confira os termos da ferramenta para uso comercial antes de publicar; personagem de terceiros ou pessoa real só com autorização.

## O que faz
**Modo `prompts`** (antes de gerar as imagens; os prompts saem prontos para colar na ferramenta escolhida):
1. Descreva o personagem a partir da folha de referência (cores, roupa, traços).
2. Escreva o bloco base (anexar a folha, busto, fundo branco liso, boca fechada, 3:4, sem logo) e uma linha por pose: neutro, aponta, explica, joinha, cruzado (e ok, peito, pensando, ombros, laptop se pedirem).
3. Escreva os prompts de **edição** (não geração) para bocas meio aberta e aberta, que precisam sair idênticas à pose fora da boca.

**Modo `prepare`** (com as imagens prontas):
1. Agrupe as imagens por pose (ignore duplicatas por hash) e mostre uma folha de contato.
2. Recorte o fundo branco por preenchimento a partir das bordas e corte na cintura; salve PNG transparente em `1-entrada/imagens/` do job.
3. Detecte olhos (manchas brancas) e nariz em cada pose; boca logo abaixo do nariz. Desenhe os marcadores numa folha e mostre para conferir.
4. Se houver variações de boca, compare com a pose base: se mudou algo fora da boca, avise e não use.
5. Monte o bloco `"avatar"` do storyboard (`escala`, `centro`, `base`, e por pose: `arquivo`, `w`, `h`, `cx`, `boca`, `bocaAlt`, `olhos`, `pelo`, `bocas`) e associe uma pose a cada plano conforme a frase.
6. Gere a folha e **espere o ok** antes de animar.

## Entrega
Poses recortadas no job, `storyboard.json` com o avatar configurado e a folha para aprovar.

## Regras
- Use sempre a mesma folha de referência e uma só ferramenta de imagem por personagem.
- Título dos planos em `l1`/`l2` (`t1` é reservado para tempo).
- Personagem de terceiros ou pessoa real só com autorização.
