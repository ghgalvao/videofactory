"""Modo storyboard: planos de cena (storyboard.json) + tempos da narração → folha de aprovação e vídeo.

  vf storyboard JOB            gera 2-aprovar/storyboard_folha.png (um quadro por plano) para aprovação
  vf storyboard JOB --animar   renderiza 3-final/video.mp4 com a cena animada (depois da aprovação)
"""
import json
import re
import subprocess
from pathlib import Path

import soundfile as sf

from ..core.hyperframes import VIDEO, gerar_html, pnpm_hyperframes, preparar_projeto, renderizar
from ..core.paths import ROOT, Job
from ..core.timing import normalizar


def _fim_de_frase(token: str) -> bool:
    return bool(re.search(r'[.?!]$', token))


def calcular_planos(planos: list, palavras: list, dur: float):
    """Retorna (planos com t0/t1, instante de início de cada frase). Frases terminam em . ? !"""
    inicios = [0]
    for i, w in enumerate(palavras):
        if _fim_de_frase(w['word']) and i + 1 < len(palavras):
            inicios.append(i + 1)
    n_frases = len(inicios)
    saida = []
    for p in planos:
        f0, f1 = min(p['frases']), max(p['frases'])
        if f1 > n_frases:
            raise SystemExit(f'plano {p["id"]} usa a frase {f1}, mas o roteiro tem {n_frases} frases')
        saida.append(dict(p, t0=round(palavras[inicios[f0 - 1]]['start'], 3)))
    for i, p in enumerate(saida):
        p['t1'] = saida[i + 1]['t0'] if i + 1 < len(saida) else round(dur, 3)
    saida[0]['t0'] = 0.0
    frases_t0 = [round(palavras[i]['start'], 3) for i in inicios]
    return saida, frases_t0


def aplicar_substituicoes(palavras: list, subs: list) -> list:
    """Troca sequências de palavras faladas por um texto de legenda (ex.: 'dois vírgula seis por cento' → '2,6%').

    Só afeta a legenda; o tempo vai do início da primeira ao fim da última palavra da sequência.
    """
    norm = [normalizar(w['word']) for w in palavras]
    out, i = [], 0
    while i < len(palavras):
        for s in subs:
            alvo = [normalizar(x) for x in s['de'].split()]
            if norm[i:i + len(alvo)] == alvo:
                ultimo = palavras[i + len(alvo) - 1]['word']
                pont = re.search(r'[.?!;:,]+$', ultimo)
                out.append({'word': s['para'] + (pont.group(0) if pont else ''),
                            'start': palavras[i]['start'], 'end': palavras[i + len(alvo) - 1]['end']})
                i += len(alvo)
                break
        else:
            out.append(palavras[i]); i += 1
    return out


def _preparar_imagens(job: Job, planos: list):
    """Elementos `imagem`: copia 1-entrada/imagens/<arquivo> para video/assets/job/<job>/ (placeholder se faltar)."""
    import shutil
    destino = ROOT / 'video' / 'assets' / 'job' / job.nome.replace('/', '_')
    destino.mkdir(parents=True, exist_ok=True)
    faltando = []
    for p in planos:
        for e in p.get('elementos', []):
            if e.get('tipo') not in ('imagem', 'foto', 'produto', 'pilula') or not e.get('arquivo'):
                continue
            origem = job.entrada / 'imagens' / e['arquivo']
            alvo = destino / e['arquivo']
            if origem.exists():
                shutil.copyfile(origem, alvo)
            else:
                faltando.append(e['arquivo'])
                import subprocess
                subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=c=0x181e2c:s=1080x1920',
                                '-vf', 'drawbox=x=40:y=40:w=1000:h=1840:color=0x5a6482:t=6', '-frames:v', '1', str(alvo)], check=True)
            e['src'] = f'assets/job/{destino.name}/{e["arquivo"]}'
    if faltando:
        print(f'  AVISO imagens faltando (placeholder): {", ".join(faltando)}')


def _preparar_fotos(job: Job, sb: dict, planos: list):
    """plano.foto = {arquivo | asset}: copia a foto (de 1-entrada/imagens ou do catálogo do cliente) para video/assets/job/<job>/ e grava foto.src."""
    import shutil
    destino = ROOT / 'video' / 'assets' / 'job' / job.nome.replace('/', '_')
    for p in planos:
        f = p.get('foto')
        if not f:
            continue
        destino.mkdir(parents=True, exist_ok=True)
        if f.get('asset'):
            base = ROOT / 'saida' / sb['client'] / 'assets'
            itens = {i['id']: i for i in json.loads((base / 'index.json').read_text(encoding='utf-8'))['items']}
            i = itens.get(f['asset'])
            if not i or 'discard' in i['use'] or i['blank']:
                raise SystemExit(f'plano {p["id"]}: asset {f["asset"]} não existe ou está descartado no catálogo')
            origem = base / i['path']
            nome = f'{f["asset"]}{origem.suffix.lower()}'
        else:
            origem = job.entrada / 'imagens' / f['arquivo']
            nome = origem.name
        if not origem.exists():
            raise SystemExit(f'plano {p["id"]}: foto {origem} não existe')
        shutil.copyfile(origem, destino / nome)
        f['src'] = f'assets/job/{destino.name}/{nome}'


# Brand variables each template exposes, filled from the client's marca.json (keys: destaque, primaria, secundaria, fonte).
TEMA_POR_CENA = {
    'trocador': {'laranja': 'destaque'},
    'blueprint': {'azul': 'primaria', 'grade': 'secundaria', 'ciano': 'destaque', 'brilho': 'destaque/0.7',
                  'stampbg': 'primaria/0.9', 'ftitulo': 'fonte'},
    'quadro': {},
    'fintech': {'verde': 'destaque'}, 'documental': {'verde': 'destaque'}, 'oferta': {'verde': 'destaque'},
}
FONTES_DO_MOTOR = {'Orbitron', 'Barlow Condensed', 'Plex Mono'}


def _rgba(hexa: str, a: float) -> str:
    h = hexa.lstrip('#')
    return f'rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})'


def marca_do_cliente(sb: dict) -> dict:
    """marca.json do cliente do storyboard ("client": "clients/<slug>"), ou {} sem cliente."""
    if not sb.get('client'):
        return {}
    f = ROOT / 'saida' / sb['client'] / 'marca.json'
    if not f.is_file():
        raise SystemExit(f'storyboard: "client" aponta para {sb["client"]}, mas {f} não existe')
    return json.loads(f.read_text(encoding='utf-8'))


def tema_da_marca(cena: str, marca: dict) -> dict:
    """Variáveis CSS do template preenchidas com a marca: a identidade vale sem copiar cor à mão em cada job."""
    cores = marca.get('cores') or {}
    fonte = ((marca.get('fontes') or {}).get('titulo') or {}).get('familia')
    base = {'destaque': cores.get('destaque'), 'primaria': cores.get('primaria'), 'secundaria': cores.get('secundaria'),
            'fonte': f'"{fonte}"' if fonte in FONTES_DO_MOTOR else None}
    out = {}
    for var, chave in TEMA_POR_CENA.get(cena, {}).items():
        nome, _, alfa = chave.partition('/')
        v = base.get(nome)
        if v:
            out[var] = _rgba(v, float(alfa)) if alfa else v
    return out


def _html(job: Job, animado: bool):
    sb = json.loads(job.storyboard.read_text(encoding='utf-8'))
    palavras = json.loads(job.words.read_text(encoding='utf-8'))
    wav = job.wav
    dur = sf.info(str(wav)).duration
    planos, frases_t0 = calcular_planos(sb['planos'], palavras, dur)
    template = ROOT / 'video' / f'{sb["cena"]}.html'
    avatar = sb.get('avatar')
    if avatar and avatar.get('poses'):  # avatar ilustrado: 1-entrada/imagens/<arquivo> vai para video/assets/job/<job>/
        import shutil
        destino = ROOT / 'video' / 'assets' / 'job' / job.nome.replace('/', '_')
        destino.mkdir(parents=True, exist_ok=True)
        for pose in avatar['poses'].values():
            shutil.copyfile(job.entrada / 'imagens' / pose['arquivo'], destino / pose['arquivo'])
            pose['src'] = f'assets/job/{destino.name}/{pose["arquivo"]}'
            for forma, arq in list(pose.get('bocas', {}).items()):  # boca por imagem: {"meio": "...png", "aberta": "...png"}
                shutil.copyfile(job.entrada / 'imagens' / arq, destino / arq)
                pose['bocas'][forma] = f'assets/job/{destino.name}/{arq}'
    _preparar_fotos(job, sb, planos)
    marca = marca_do_cliente(sb)
    logo_marca = (marca.get('logo') or {}).get('arquivo')
    if not sb.get('logo') and logo_marca:  # sem logo no job: usa a do cliente (marca.json)
        import shutil
        origem = ROOT / 'saida' / sb['client'] / logo_marca
        if origem.is_file():
            (job.entrada / 'imagens').mkdir(parents=True, exist_ok=True)
            shutil.copyfile(origem, job.entrada / 'imagens' / origem.name)
            sb['logo'] = origem.name
    logo_src = ''
    if sb.get('logo'):  # logo do cliente em 1-entrada/imagens/ vai para video/assets/job/<job>/ (cena 3D e fechos)
        import shutil
        destino = ROOT / 'video' / 'assets' / 'job' / job.nome.replace('/', '_')
        destino.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(job.entrada / 'imagens' / sb['logo'], destino / sb['logo'])
        logo_src = f'assets/job/{destino.name}/{sb["logo"]}'
    extra = {'__DADOS__': json.dumps({'shots': planos, 'animado': animado, 'frases': frases_t0, 'look': sb.get('look', ''), 'textos': sb.get('textos', {}),
                                          'palavras': [[round(w['start'], 3), round(w['end'], 3), w['word']] for w in palavras],
                                          'avatar': avatar, 'theme': sb.get('theme'), 'logo': logo_src}, ensure_ascii=False),
             '__DURACAO_NUM__': f'{dur:.3f}', '__TITULO__': sb.get('titulo', ''),
             '__TRILHA__': json.dumps(sb.get('trilha', ['', '']), ensure_ascii=False)}
    for p in planos:  # cenas 2D declaram o tempo de cada plano no HTML estático
        extra[f'__S{p["id"]}_T0__'] = f'{p["t0"]:.3f}'
        extra[f'__S{p["id"]}_D__'] = f'{max(p["t1"] - p["t0"], 0.1):.3f}'
    if sb['cena'] == 'paper':  # estilo paper montável: elementos de cada plano vêm do storyboard.json
        from ..core.paper import montar
        extra.update(montar(planos, frases_t0, sb.get('dy', 50)))
    elif sb['cena'] in ('quadro', 'blueprint'):  # quadro branco: traços e texto à mão vêm do storyboard.json
        from ..core.quadro import montar
        _preparar_imagens(job, planos)
        extra.update(montar(planos, frases_t0, sb.get('dy', 0), sb.get('cor_padrao', '#1b1f2a')))
    elif sb['cena'] in ('fintech', 'documental', 'oferta'):  # estilo fintech-motion/documental, mesmo princípio
        from ..core.fintech import montar
        _preparar_imagens(job, planos)
        extra.update(montar(planos, frases_t0, sb.get('dy', 0)))
    tema = {**tema_da_marca(sb['cena'], marca), **sb.get('tema', {})}  # marca do cliente; o job pode sobrescrever
    extra['__TEMA__'] = ':root{' + ';'.join(f'--{k}:{c}' for k, c in tema.items()) + '}' if tema else ''
    estilo = {'destaque': (marca.get('cores') or {}).get('destaque', '#ffd23f'), **sb.get('legenda', {})}
    legenda_palavras = aplicar_substituicoes(palavras, sb.get('substituicoes', []))
    html = gerar_html(legenda_palavras, dur, template=template, extra=extra, max_palavras=estilo.get('max_palavras', 2),
                      cor_texto=estilo.get('texto', '#ffffff'), cor_destaque=estilo.get('destaque', '#ffd23f'))
    return html, planos, palavras, dur, wav


def folha(job: Job):
    html, planos, _, _, wav = _html(job, animado=False)
    preparar_projeto(html, wav)
    quadros = job.quadros
    quadros.mkdir(parents=True, exist_ok=True)
    for f in quadros.glob('*.png'):
        f.unlink()
    # instante dentro de cada plano: câmera já assentou e o selo já apareceu
    tempos = [round(min(p['t0'] + p.get('quadro', 1.0), p['t1'] - 0.1), 2) for p in planos]
    print('  planos:', [(p['id'], p['t0'], p['t1']) for p in planos])
    print('  quadros em:', tempos)
    pnpm_hyperframes('snapshot', '.', '--at', ','.join(str(t) for t in tempos), '--no-end', '--keep',
                     '--output', str(quadros.resolve()))
    arquivos = [quadros / f'at-{t:g}s.png' for t in tempos]
    faltando = [a.name for a in arquivos if not a.exists()]
    if faltando:
        raise SystemExit(f'snapshot não gerou: {faltando}; encontrados: {[f.name for f in quadros.glob("*.png")]}')
    job.aprovar.mkdir(parents=True, exist_ok=True)
    saida = job.folha
    entradas = [x for a in arquivos for x in ('-i', str(a))]
    n = len(arquivos)
    paisagem = json.loads(job.storyboard.read_text(encoding='utf-8')).get('cena') == 'documental'
    cw, ch, cols = (640, 360, 3) if paisagem else (360, 640, 4)
    escala = ''.join(f'[{i}:v]scale={cw}:{ch}[s{i}];' for i in range(n))
    layout = '|'.join(f'{(i % cols) * cw}_{(i // cols) * ch}' for i in range(n))
    fc = escala + ''.join(f'[s{i}]' for i in range(n)) + f'xstack=inputs={n}:layout={layout}[o]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *entradas, '-filter_complex', fc, '-map', '[o]', str(saida)], check=True)
    print(f'  folha: {saida}')
    return saida


def animar(job: Job):
    html, planos, palavras, dur, wav = _html(job, animado=True)
    renderizar(palavras, dur, wav, job.video_tmp, html=html)  # temporários do HyperFrames ficam em _interno
    print(f'  pronto: {job.publicar()}')


def executar(a):
    job = Job(a.saida, a.job)
    if not job.words.exists():
        raise SystemExit(f'{job.raiz}: rode antes `vf narrate` (precisa de narration.wav e words.json em _interno/)')
    if not job.storyboard.exists():
        raise SystemExit(f'{job.raiz}: falta 1-entrada/storyboard.json')
    job.criar()
    animar(job) if a.animar else folha(job)
