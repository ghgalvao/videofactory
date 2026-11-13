---
name: vf-script
description: Escreve, enxuga ou reforça o roteiro de um vídeo do videoFactory (gancho, fatos com duas fontes, chamada final, ganchos alternativos). Use quando o usuário pedir só o roteiro, quiser encurtar um roteiro, pedir ganchos ou digitar /vf-script.
argument-hint: "<tema ou job> [curto|ganchos|conferir]"
---

# vf-script

## Quando usar
Quando você quer trabalhar só no texto: escrever um roteiro novo, cortar um que ficou longo, testar ganchos ou conferir os fatos antes de narrar.

## Como usar
```
/vf-script por que o mar é salgado
/vf-script science-channel/why-sky-is-blue curto
/vf-script science-channel/why-sky-is-blue ganchos
/vf-script science-channel/moon-tides conferir
```

## O que faz
1. **Contexto.** Leia `docs/DIRECTOR.md`. Se for um job existente, leia o `roteiro.txt` dele; se estiver numa galeria, leia `brief.md` (público, tom) e os estudos em `research/` sobre o tema.
2. **Modo novo (padrão).** Roteiro de 30 a 45 s: gancho em até 3 s (pergunta, número ou contradição), uma frase por linha, um fato surpreendente, linha em branco antes da chamada final. Números por extenso quando a voz precisar ler (ex.: "dois mil e vinte e dois").
3. **Modo `curto`.** Corte até a duração pedida (padrão 35 s) sem perder gancho nem o fato principal. Mostre antes e depois lado a lado.
4. **Modo `ganchos`.** Cinco ganchos de até 12 palavras: pergunta, número, contradição, cena e promessa. Indique o seu favorito e por quê.
5. **Modo `conferir`.** Liste cada número, data e afirmação com duas fontes. Marque o que não confirmou e reescreva essas frases de forma cautelosa.
6. Se houver job, grave em `1-entrada/roteiro.txt` só depois do ok do usuário (guarde a versão anterior como `roteiro_v<n>.txt`).

## Entrega
Roteiro pronto para narrar (ou a lista de ganchos, ou o relatório de fatos), com as fontes na resposta.

## Regras
- Nada de promessa de ganho, resultado garantido ou urgência falsa.
- Fato sem duas fontes não entra como certeza.
- Não narre: isso é do `/vf-video` ou do botão Narrar no painel.
