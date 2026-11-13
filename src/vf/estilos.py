"""Registro dos estilos do videoFactory. `uv run vf estilos` lista.

Cada estilo tem uma receita fixa em `styles/<pasta>/STYLE.md` (visual, movimento, som, aceite).
status: 'testado' (gerou vídeo aprovado), 'pronto' (template funciona, pouco testado), 'a criar' (só receita).
"""
from .core.paths import ROOT

ESTILOS = [
    # (pasta, tipo, status, formato, template, teste, uso)
    ('paper', 'conteúdo', 'testado', '9:16', 'video/paper.html (montável)', 'E1', 'colagem de papel: notícia, dados, comparação'),
    ('mechanism-3d', 'conteúdo', 'pronto', '9:16', 'video/panela.html (look brinquedo|premium)', 'E2', '3D: como aparelhos funcionam'),
    ('animated-caption', 'conteúdo', 'pronto', '9:16', 'video/template.html', 'E3', 'legenda palavra por palavra'),
    ('simple-caption', 'conteúdo', 'pronto', '9:16', 'ffmpeg + .ass', '—', 'rascunho para conferir voz/tempo'),
    ('whiteboard', 'conteúdo', 'pronto', '9:16', 'video/quadro.html', 'E4', 'quadro branco com traço à mão'),
    ('blueprint', 'conteúdo', 'pronto', '9:16', 'video/blueprint.html', 'E5', 'planta técnica: máquinas e instalações'),
    ('data-infographic', 'conteúdo', 'pronto', '9:16', 'video/fintech.html (grafico, bonecos)', 'E6', 'gráficos e números com fonte'),
    ('stick-figure', 'conteúdo', 'pronto', '9:16', 'video/fintech.html (cenario, boneco)', 'E7', 'bonequinho narrador com cenários'),
    ('ken-burns', 'conteúdo', 'pronto', '9:16', 'video/fintech.html (imagem)', 'E8', 'imagens com zoom/pan e narração'),
    ('documentary', 'conteúdo', 'pronto', '16:9', 'video/documental.html', 'E9', 'foto/ilustração, biografia e história'),
    ('pixel-avatar', 'conteúdo', 'pronto', '9:16', 'video/pixel-avatar.html', '—', 'personagem explicando passo a passo, cartão por passo e boca na fala'),
    ('fintech-motion', 'conteúdo', 'pronto', '9:16', 'video/fintech.html', '—', 'motion de produto/finanças com celular e callouts'),
    ('carrossel-vivo', 'conteúdo', 'pronto', '4:5', 'vf carrossel → video/carrossel.html', 'C1', 'carrossel de Instagram animado, com som por slide'),
    ('biz-saas-demo', 'empresa', 'pronto', '9:16', 'video/fintech.html (tela)', 'B3', 'demonstração de software com telas reais'),
    ('oferta-varejo', 'empresa', 'pronto', '9:16', 'vf oferta → video/oferta.html', '—', 'oferta de varejo a partir de oferta.json'),
    ('biz-brand-intro', 'empresa', 'a criar', '9:16', 'paper/whiteboard + marca.json', 'B1', 'apresentação de marca'),
    ('biz-product-explainer', 'empresa', 'pronto', '9:16', 'blueprint + tema da marca + fotos', 'B2', 'explicador de produto físico'),
    ('biz-social-proof', 'empresa', 'a criar', '9:16', 'paper/data-infographic + marca.json', 'B4', 'depoimento e caso de sucesso'),
    ('biz-launch', 'empresa', 'a criar', '9:16', 'paper + marca.json', 'B5', 'lançamento, novidade'),
    ('biz-tips-faq', 'empresa', 'a criar', '9:16', 'animated-caption/paper + marca.json', 'B6', 'série de dicas e FAQ'),
]


def listar():
    for pasta, tipo, status, formato, template, teste, uso in ESTILOS:
        receita = ROOT / 'styles' / pasta / 'STYLE.md'
        aviso = '' if receita.exists() else '  [sem receita!]'
        print(f'[{status:7}] {pasta:22} {tipo:8} {formato:12} teste {teste:3}  {uso}{aviso}')
        print(f'          template: {template}  ·  receita: styles/{pasta}/STYLE.md')
    print('\nDireção: docs/DIRECTOR.md · Técnica: docs/TECHNIQUE.md · Empresas: docs/RECEITAS-EMPRESA.md')
