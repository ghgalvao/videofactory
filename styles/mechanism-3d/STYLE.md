# STYLE — Mecanismo 3D em corte (low-poly)

Template: `video/panela.html` (campo `look`: `brinquedo` ou `premium`; base 3D em `video/assets/vendor/three-premium.min.js`). 9:16. Melhor para explicar ciclos e fluxos de aparelhos.

## Visual
- **Luz**: `HemisphereLight` (1,15) + `DirectionalLight` (0,75) com sombra suave (mapa 2048). Fundo creme `#f6e7cf`.
- **Sombreamento "cel"**: `MeshToonMaterial` com `gradientMap` de 3 tons (95/175/255). Sem degradê liso.
- **Contorno**: casco invertido (`BackSide`) escalado por eixo, espessura ≈ 0,012–0,016 m; **não** aplicar em painéis transparentes.
- **Corte transversal**: painéis do aparelho com opacidade 0,14 (fundo 0,35); interior visível. Em planos de foco (compressor, grade, tubo) **esconder o interior** (`estado.foco`) para não poluir.
- **Fluido**: ~70 partículas ao longo de um caminho poligonal; cor por trecho: comprimido vermelho → grade laranja → líquido claro → tubo fino azul → evaporador ciano. Parado no storyboard; em fluxo ao animar.
- **Cenário**: cozinha com piso de ladrilho (textura por código), bancada, janela, relógio, planta. Nunca fundo vazio.
- **Personagem**: cabeça esférica grande, tronco/membros em cápsula, olhos com pupila, sobrancelhas, mãos e sapatos; poses `assustado`, `aponta`, `acena`. Pivô no ombro (rotação z: 0 = braço para baixo; esquerdo negativo abre para fora; direito positivo).
- **Selo**: pílula amarela com borda e sombra de tinta, posicionado por projeção 3D→2D, **limitado pela própria largura** (evita corte nas bordas), entra com "pop" 0,25 s.
- **Barra de ciclo** no topo (4 etapas), etapa ativa em amarelo.

## Câmera
- Um enquadramento por plano; fov 40 (plano aberto), 44–70 (close). Transição de 0,6 s com `smoothstep`; deriva lenta (5%) ao animar.
- Distância mínima ~1,6 m do objeto de foco; abaixo disso fica abstrato.
- **Câmera olhando para +z inverte o eixo x** (mundo +x aparece à esquerda). Posicionar personagem do lado visível e fora da linha câmera→objeto.

## Roteiro-tipo (≈ 40 s, 8 planos)
Gancho em pergunta (1) · "não faz X, move Y" (2) · etapa 1 (3) · etapa 2 (4) · etapa 3 (5) · etapa 4 (6) · dica prática com comparação (7) · CTA (8).

## Limites
Personagem em blocos arredondados, sem expressão de fala. Sem som. Para acabamento acima disso: modelos CC0 ou arte de IA (ver `docs/DIRECTOR.md`).
