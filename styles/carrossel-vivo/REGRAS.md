# REGRAS — carrossel vivo (o "CLAUDE.md" do carrossel)

Leia **antes** de escrever qualquer `carrossel.json`. É o que separa carrossel que prende de carrossel com cara de IA (nível 2 do vídeo de origem: instruções fixas + prompt bem escrito).

## 1. Conteúdo
1. **Uma ideia por slide.** Capa promete, miolo entrega, último slide chama para uma ação só.
2. Título ≤ 8 palavras, em afirmação (não rótulo vazio). Texto ≤ 20 palavras. Lista ≤ 4 itens de ≤ 12 palavras.
3. Capa: gancho que cria curiosidade ou tensão. Nunca "Introdução". Slide 2 entrega a primeira resposta, não repete a capa.
4. Número só se a fonte foi conferida (duas fontes para fato). Número inventado para exemplo vem com "valores ilustrativos" na tela.
5. Português do Brasil, sem travessão como muleta, sem "você sabia?", sem emoji de enfeite.

## 2. Ritmo e peso (o que o vídeo chama de "suavidade, peso e ritmo")
1. **Ritmo** por assunto: `rapido` (0,16 s) para listas e dicas; `medio` (0,28 s) padrão; `calmo` (0,42 s) para conceito denso. Um ritmo por carrossel.
2. **Peso:** o elemento mais importante do slide é o único que "bate" (número, botão) e recebe som `hero`. O resto entra leve (fade, sobe).
3. Ordem de leitura = ordem de entrada: rótulo → título → texto/itens → destaque. Nada entra antes do que explica.
4. Cada slide termina parado e completo por 1,3 s: quem pausa vê o slide inteiro; esse quadro é o PNG.
5. Entrada ≤ 0,5 s por elemento. Nada sai da tela. Sem loop, sem tremor decorativo.

## 3. Som
1. Todo som nasce de um elemento visível, no mesmo `t`. O cues.json é gerado do HTML; **não** editar tempo de som à mão.
2. Máximo um som `hero` a cada ~4 s. Rótulo e item usam sons curtos (`tick`, `pop`).
3. Nunca sintetizar batida, clique ou whoosh. Biblioteca CC0 do sound-layer, uma família por carrossel.
4. O ouvido final é do usuário: relatar o que o QA acusou e o que ficou abaixo do ideal.

## 4. Visual anti-"slop"
1. **Cor:** nada de paleta padrão do assistente (roxo/azul-neon, gradiente arco-íris). Fundo escuro neutro + **uma** cor de destaque. Com marca, usar o `tema` da marca.
2. **Tipografia:** no máximo duas famílias (títulos condensados + mono para rótulos). Contraste AA. Texto ≥ 40 px.
3. Sem borda forte em volta de tudo, sem sombra pesada, sem cartão dentro de cartão.
4. Imagem (do usuário ou de fonte livre CC0, nunca gerador pago por enquanto) entra como fundo atrás do texto (o template põe véu escuro) ou como figura única; vídeo de fundo só se o movimento reforça a ideia do slide; nunca banco de imagem genérico.
5. Referência = estrutura e ritmo, não cópia. Fidelidade `baixa` (só clima), `média` (layout e ritmo), `alta` (mesma grade); padrão é `média`.

## 5. Processo (obrigatório, nesta ordem)
1. Ler `styles/carrossel-vivo/STYLE.md`, este arquivo e as referências da galeria (`saida/<galeria>/references/`).
2. Escrever o `carrossel.json` (ou expandir o pedido curto: `/vf-carousel`).
3. `vf carrossel <job>` → **PNGs + folha** → usuário aprova.
4. Só depois: `vf carrossel <job> --animar` → `/vf-sound <job>`.
5. Gostou do resultado? **Salvar como referência** (`/vf-reference`, com o "por que gostei"). É assim que o processo aprende o gosto do usuário.
