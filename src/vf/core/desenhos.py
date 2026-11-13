"""Ilustrações vetoriais 1280x720 para o estilo documental (substituem fotos de arquivo quando não há licença/arquivo).

desenho = fazenda | paris | hangar | voo | demoiselle | biplano
"""
import random


def _ceu(idc, c1, c2):
    return (f'<defs><linearGradient id="{idc}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c1}"/>'
            f'<stop offset="1" stop-color="{c2}"/></linearGradient></defs><rect width="1280" height="720" fill="url(#{idc})"/>')


def _bis14(x, y, s=1.0, cor='#f4efe2'):
    """14-Bis estilizado: célula-cauda (canard) à frente, asas em caixa (cellular), roda e hélice."""
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="#3a3228" stroke-width="5" stroke-linejoin="round">'
            f'<rect x="-250" y="-70" width="330" height="62" fill="{cor}"/><rect x="-250" y="-8" width="330" height="62" fill="{cor}"/>'
            + ''.join(f'<line x1="{x0}" y1="-70" x2="{x0}" y2="54"/>' for x0 in (-250, -140, -30, 80)) +
            f'<polygon points="-250,-30 -330,-10 -250,10" fill="#e6dcc4"/>'
            f'<rect x="-330" y="-34" width="70" height="46" fill="{cor}" transform="rotate(-8 -295 -10)"/>'
            f'<line x1="80" y1="-10" x2="250" y2="-10" stroke-width="7"/>'
            f'<polygon points="250,-30 330,-52 330,32 250,10" fill="{cor}"/>'
            f'<circle cx="-170" cy="110" r="30" fill="#2b2b2b"/><circle cx="-40" cy="110" r="30" fill="#2b2b2b"/>'
            f'<line x1="-170" y1="54" x2="-170" y2="110"/><line x1="-40" y1="54" x2="-40" y2="110"/>'
            f'<line x1="-345" y1="-60" x2="-345" y2="40" stroke-width="9"/></g>')


def desenho_svg(nome: str) -> str:
    r = random.Random(4)
    if nome == 'fazenda':
        cafe = ''.join(f'<circle cx="{x}" cy="{y}" r="{10 + (y - 470) // 18}" fill="#2f6a35"/>'
                       for y in range(470, 700, 38) for x in range(30 + (y // 38 % 2) * 30, 1280, 60))
        return (_ceu('fz', '#bfe3f5', '#f6efd2') +
                '<circle cx="1040" cy="150" r="70" fill="#ffe27a"/>'
                '<path d="M0 380 L220 230 L430 380 Z M300 380 L560 190 L820 380 Z M700 380 L930 260 L1180 380 Z" fill="#8aa7a0"/>'
                '<rect y="360" width="1280" height="360" fill="#8cc271"/>'
                '<path d="M0 470 Q320 410 640 460 T1280 450 L1280 720 L0 720 Z" fill="#6aa65a"/>' + cafe +
                '<g><rect x="520" y="300" width="230" height="130" fill="#f3e3c2" stroke="#6b5a3c" stroke-width="5"/>'
                '<polygon points="500,300 635,220 770,300" fill="#b5503c" stroke="#6b5a3c" stroke-width="5"/>'
                '<rect x="610" y="350" width="50" height="80" fill="#8a6a42"/></g>')
    if nome in ('paris', 'paris2'):
        torre = ('<g stroke="#4a4f5a" stroke-width="6" fill="none" stroke-linejoin="round">'
                 '<polygon points="760,690 800,690 790,420 770,420" fill="#6b717d"/>'
                 '<path d="M700 690 L752 470 L808 470 L860 690"/><path d="M752 470 L765 330 L795 330 L808 470"/>'
                 '<path d="M770 330 L780 120 L790 330" /><line x1="722" y1="600" x2="838" y2="600"/>'
                 '<line x1="745" y1="520" x2="815" y2="520"/><line x1="768" y1="400" x2="792" y2="400"/>'
                 '<path d="M706 670 Q780 560 854 670"/></g>')
        pred = ''.join(f'<rect x="{x}" y="{600 - h}" width="{w}" height="{h + 120}" fill="{c}"/>'
                       for x, w, h, c in [(0, 110, 70, '#d6cdb8'), (110, 90, 110, '#c9bfa6'), (200, 130, 60, '#d9d1be'),
                                          (330, 100, 90, '#cbc2ab'), (930, 120, 80, '#d6cdb8'), (1050, 90, 120, '#c9bfa6'), (1140, 140, 70, '#d9d1be')])
        dir = ('<g transform="translate(330 190)"><ellipse cx="0" cy="0" rx="190" ry="52" fill="#f3d9b0" stroke="#7a5a2c" stroke-width="6"/>'
               '<rect x="-60" y="52" width="120" height="22" rx="6" fill="#8a6a42"/><line x1="-40" y1="52" x2="-50" y2="30" stroke="#7a5a2c" stroke-width="4"/>'
               '<line x1="40" y1="52" x2="50" y2="30" stroke="#7a5a2c" stroke-width="4"/>'
               '<line x1="190" y1="0" x2="215" y2="0" stroke="#7a5a2c" stroke-width="8"/>'
               '<polygon points="-190,0 -230,-26 -230,26" fill="#d9a56a" stroke="#7a5a2c" stroke-width="5"/></g>')
        return (_ceu('pr', '#a9d4ef', '#f3ecd9') + pred + torre + (dir if nome == 'paris' else '') +
                '<rect y="690" width="1280" height="30" fill="#8b8f74"/>')
    if nome == 'hangar':
        return ('<rect width="1280" height="720" fill="#d8c9a6"/><rect y="520" width="1280" height="200" fill="#a58f66"/>'
                '<path d="M0 0 L1280 0 L1280 160 Q640 40 0 160 Z" fill="#8f7e5a"/>'
                '<rect x="140" y="170" width="260" height="300" fill="#efe7cf" stroke="#7a6a48" stroke-width="6"/>'
                '<rect x="880" y="170" width="260" height="300" fill="#efe7cf" stroke="#7a6a48" stroke-width="6"/>'
                + _bis14(640, 440, 1.0))
    if nome == 'voo':
        gente = ''.join(f'<circle cx="{r.randint(60, 1220)}" cy="{r.randint(620, 690)}" r="9" fill="#3a3228"/>' for _ in range(46))
        return (_ceu('vo', '#9fd0ee', '#f1ecd6') + '<rect y="560" width="1280" height="160" fill="#7fb36a"/>'
                '<path d="M0 560 Q320 520 640 556 T1280 548 L1280 600 L0 600 Z" fill="#69a05a"/>' + gente +
                '<ellipse cx="640" cy="590" rx="260" ry="14" fill="rgba(0,0,0,0.18)"/>' + _bis14(640, 400, 0.85))
    if nome == 'demoiselle':
        return (_ceu('dm', '#b6dcf2', '#f6efd9') + '<rect y="600" width="1280" height="120" fill="#86b873"/>'
                '<g stroke="#4a3b24" stroke-width="7" stroke-linecap="round" transform="translate(640 380)">'
                '<line x1="-330" y1="0" x2="300" y2="0" stroke-width="10"/><line x1="-330" y1="0" x2="-180" y2="-70"/>'
                '<polygon points="-90,-12 -40,-120 40,-120 120,-12" fill="#f4efe2"/><polygon points="-90,12 -40,120 40,120 120,12" fill="#f4efe2"/>'
                '<polygon points="-330,0 -380,-60 -300,-8" fill="#f4efe2"/><line x1="-30" y1="0" x2="-30" y2="150"/>'
                '<circle cx="-30" cy="170" r="24" fill="#2b2b2b"/><circle cx="170" cy="150" r="20" fill="#2b2b2b"/><line x1="130" y1="0" x2="170" y2="150"/>'
                '<line x1="320" y1="-60" x2="320" y2="60" stroke-width="10"/></g>')
    if nome == 'biplano':
        return (_ceu('bp', '#cde6f4', '#f7f0da') + '<rect y="610" width="1280" height="110" fill="#e0cfa4"/>'
                '<g stroke="#4a3b24" stroke-width="6" stroke-linejoin="round" transform="translate(640 380)">'
                '<rect x="-300" y="-110" width="600" height="46" fill="#f4efe2"/><rect x="-300" y="30" width="600" height="46" fill="#f4efe2"/>'
                + ''.join(f'<line x1="{x}" y1="-64" x2="{x}" y2="30"/>' for x in (-260, -120, 0, 120, 260)) +
                '<line x1="-60" y1="-10" x2="320" y2="-10" stroke-width="10"/><polygon points="320,-50 380,-70 380,40 320,20" fill="#f4efe2"/>'
                '<line x1="-60" y1="-40" x2="-60" y2="70"/><circle cx="-130" cy="150" r="22" fill="#2b2b2b"/><line x1="-130" y1="76" x2="-130" y2="150"/></g>')
    raise SystemExit(f'desenho desconhecido: {nome}')
