"""CARROSSEL VIVO: carrossel de Instagram (4:5, 1080x1350) em que cada slide é uma mini-animação com som.

Uso:  vf carrossel <job>            1ª vez cria 1-entrada/carrossel.json de exemplo; depois gera os PNG estáticos
      vf carrossel <job> --animar   renderiza um MP4 por slide (sem som) 
      vf carrossel <job> --som      mixa o som de cada slide (sound-layer) e junta ao MP4
Edite SÓ o carrossel.json. Saídas:
  3-final/png/NN.png        slide estático (estado final da animação) — sai SEMPRE primeiro, é o que se aprova
  3-final/animado/NN.mp4    slide animado (só com --animar)
  _interno/som/cues-NN.json cue sheet do sound-layer por slide (gerado pelo --som, dos mesmos tempos da animação)

Os tempos de cada elemento nascem aqui (`montar_slide`) e vão para o HTML e para o cues.json: um lugar só,
por isso som e imagem não se separam.
"""
import json
import shutil
import subprocess
from pathlib import Path

from .hyperframes import VIDEO, pnpm_hyperframes
from .paths import ROOT, Job

LARGURA, ALTURA = 1080, 1350
DIM = {'post': (1080, 1350), 'story': (1080, 1920)}  # formato do carrossel.json: 'post' (4:5) ou 'story' (9:16)
MARGENS_STORY = {'mt': '270px', 'mb': '400px', 'rb': '230px', 'lt': '250px'}  # fora da área coberta pela interface do Stories
RITMOS = {'rapido': 0.16, 'medio': 0.28, 'calmo': 0.42}  # intervalo entre elementos de um slide (s)
SEGURA = 1.3        # tempo parado com tudo visível no fim do slide (s)
DUR_MIN = 3.0
FPS = 30
PAPEIS = ('rotulo', 'titulo', 'texto', 'item', 'numero', 'chip', 'barra', 'cta')
# papel → (entrada visual, som do sound-layer, peso, o que o qa.py confere na imagem)
SOM = {
    'rotulo': ('fade', 'tick', 'support', 'land'),
    'titulo': ('palavras', 'thump+tap', 'hero', 'land'),
    'texto': ('sobe', 'swish', 'support', 'move'),
    'item': ('direita', 'pop', 'support', 'land'),
    'numero': ('bate', 'hit', 'hero', 'land'),
    'chip': ('bate', 'tap', 'support', 'land'),
    'barra': ('barra', 'swish', 'support', 'move'),
    'cta': ('bate', 'chime', 'hero', 'land'),
}
TEMA = {'fundo': '#0e1116', 'fundo2': '#1a2230', 'texto': '#f2f4f7', 'mudo': '#8b93a1', 'destaque': '#f5b942'}

EXEMPLO = {
    "titulo": "Spot × futuros: o que é basis",
    "ritmo": "medio",
    "tema": TEMA,
    "marca": "Marca Exemplo",
    "slides": [
        {"tipo": "capa", "rotulo": "ARBITRAGEM EM 5 TELAS", "titulo": "Basis é o preço da pressa",
         "texto": "Quanto o futuro paga (ou cobra) a mais que o spot."},
        {"tipo": "texto", "rotulo": "01 · DEFINIÇÃO", "titulo": "Basis = futuro − spot",
         "texto": "É a diferença entre o preço do contrato futuro e o do ativo à vista, no mesmo momento."},
        {"tipo": "lista", "rotulo": "02 · LEITURA", "titulo": "Três sinais no número",
         "itens": ["Positivo: o futuro está mais caro (contango)", "Negativo: o futuro está mais barato",
                   "Perto de zero: o mercado concorda no preço"]},
        {"tipo": "numero", "rotulo": "03 · EXEMPLO DIDÁTICO", "numero": "+1,2%",
         "titulo": "Valores inventados para ilustrar", "texto": "Futuro 101,2 e spot 100: basis de 1,2% do spot."},
        {"tipo": "cta", "rotulo": "PRÓXIMO PASSO", "titulo": "Veja o basis ao vivo",
         "texto": "Painel Spot × futuros.", "cta": "Teste grátis"}
    ]
}


def montar_slide(slide: dict, i: int, n: int, ritmo: str) -> dict:
    """slide do JSON → slide resolvido: elementos com tempo `t` (s), papel e entrada. Fonte única do tempo."""
    gap = RITMOS.get(ritmo, RITMOS['medio'])
    els, t = [], 0.15

    def add(papel, texto, extra=None, atraso=0.0):
        nonlocal t
        entrada, _, _, _ = SOM[papel]
        els.append({'id': f's{i}e{len(els)}', 'papel': papel, 'texto': texto, 't': round(t + atraso, 3),
                    'entrada': entrada, **(extra or {})})
        palavras = len(texto.split()) if papel == 'titulo' else 0
        t += gap + (0.06 * max(palavras - 1, 0) if papel == 'titulo' else 0)

    tipo = slide.get('tipo', 'texto')
    if slide.get('rotulo'):
        add('rotulo', slide['rotulo'])
    if tipo == 'numero' and slide.get('numero'):
        add('numero', slide['numero'])
    if slide.get('titulo'):
        add('titulo', slide['titulo'])
    if slide.get('texto'):
        add('texto', slide['texto'])
    for k, it in enumerate(slide.get('itens', [])):
        add('item', it, {'ordem': k + 1})
    if slide.get('chips'):
        for c in slide['chips']:
            add('chip', c)
    if tipo == 'cta' and slide.get('cta'):
        add('cta', slide['cta'])
    if not els:
        raise SystemExit(f'slide {i + 1}: vazio (precisa de rotulo, titulo, texto, itens, numero ou cta)')
    fig = slide.get('figura', '')
    t_fig = round(t, 3)
    dur = max(DUR_MIN, round((t_fig + 0.5 if fig else els[-1]['t'] + 0.9) + SEGURA, 3))
    return {'idx': i + 1, 'figura': fig, 't_fig': t_fig, 'total': n, 'tipo': tipo, 'dur': dur, 'elementos': els, 'imagem': slide.get('imagem', ''),
            'video': slide.get('video', '')}


PRIORIDADE_HERO = ('cta', 'numero', 'titulo')  # um único som forte por slide: o elemento de maior prioridade


ENTRADA_DUR = {'palavras': 0.42, 'sobe': 0.5, 'direita': 0.45, 'bate': 0.38, 'barra': 0.5, 'fade': 0.35}  # = template


def _instante_som(e: dict, visual: str) -> float:
    """Som de 'land' bate quando o elemento pousa (fim da entrada); 'move' pega o meio do movimento."""
    dur = ENTRADA_DUR.get(e['entrada'], 0.4)
    if e['entrada'] == 'palavras':
        dur += 0.06 * (len(e['texto'].split()) - 1)
    fim = {'bate': 0.62, 'palavras': 0.85}.get(e['entrada'], 0.9)  # ease-out: o movimento "para" antes do fim nominal
    return round(e['t'] + (dur * fim if visual == 'land' else dur * 0.4), 3)


def cues_slide(s: dict) -> dict:
    """Cue sheet do sound-layer de UM slide (t relativo ao início dele). Um hero só; os demais viram support."""
    papeis = {e['papel'] for e in s['elementos']}
    hero = next((p for p in PRIORIDADE_HERO if p in papeis), None)
    out = []
    for e in s['elementos']:
        _, som, peso, visual = SOM[e['papel']]
        if peso == 'hero' and e['papel'] != hero:
            peso = 'support'
        out.append({'id': f'{e["id"]}-{e["papel"]}', 't': _instante_som(e, visual), 'sound': som, 'weight': peso,
                    'align': 'peak', 'visual': visual})
    ultimo = max(c['t'] for c in out)
    return {'fps': FPS, 'duration_s': s['dur'], 'energy': 'punchy', 'kit': 'audio/kit',
            'silence_ok': [[round(ultimo + 0.35, 2), s['dur']]], 'cues': out}  # fim parado do slide é silêncio planejado


def _html(slide: dict, tema: dict, marca: str, kit: dict | None = None) -> str:
    modelo = (VIDEO / 'carrossel.html').read_text(encoding='utf-8')
    dados = {'slide': slide, 'marca': marca, 'logo': (kit or {}).get('logo_src', ''), 'forma': bool((kit or {}).get('forma'))}
    vars_ = dict(tema)
    deg = ((kit or {}).get('forma') or {}).get('degrade')
    if deg:
        vars_.update({'ga': deg[0], 'gb': deg[1], 'gc': deg[2], 'veu': ','.join(str(int(deg[2].lstrip('#')[i:i + 2], 16)) for i in (0, 2, 4))})
    w, h = slide.get('w', 1080), slide.get('h', 1350)
    if h > 1350:
        vars_.update({k: v for k, v in MARGENS_STORY.items()})
    css = ''
    if kit and kit.get('fonte_titulo'):
        vars_['ftitulo'] = f'"{kit["fonte_titulo"]}"'
        vars_['ktitulo'] = kit['escala_titulo']
        css += f'@font-face{{font-family:"{kit["fonte_titulo"]}";src:url("{kit["fonte_src"]}");font-weight:100 900}}'
    css += ':root{' + ';'.join(f'--{k}:{v}' for k, v in vars_.items()) + '}'
    v = slide.get('video')
    tag = (f'<video id="vfundo" class="clip" src="{v["src"]}" muted playsinline data-start="0" '
           f'data-duration="{min(slide["dur"], v["dur"]):.3f}"></video>') if v else ''
    return (modelo.replace('__DURACAO__', f'{slide["dur"]:.3f}').replace('__TEMA__', css).replace('__VIDEO__', tag)
            .replace('__DADOS__', json.dumps(dados, ensure_ascii=False)).replace('__W__', str(w)).replace('__H__', str(h)))


def _mix(a: str, b: str, t: float) -> str:
    ca, cb = [int(a.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)], [int(b.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02x}' for x, y in zip(ca, cb))


def _luma(h: str) -> float:
    r, g, b = [int(h.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _client_brand(job: Job, d: dict, saida) -> dict | None:
    """d['client'] = pasta do cliente em saida/ (ex.: 'clients/acme') com marca.json no formato de docs/marca.exemplo.json.
    O carrossel é tema escuro: a cor primária vira o fundo (se ela for clara, fundo e texto trocam de lugar).
    O `tema` do carrossel.json ainda vence. Dado de cliente nunca fica no repo: só em saida/."""
    nome = d.get('client')
    if not nome:
        return None
    pasta = Path(saida) / nome
    arq = pasta / 'marca.json'
    if not arq.exists():
        raise SystemExit(f'carrossel: {arq} não existe (modelo: docs/marca.exemplo.json)')
    m = json.loads(arq.read_text(encoding='utf-8'))
    c = m['cores']
    escuro, claro = (c['primaria'], c['fundo']) if _luma(c['primaria']) < 0.5 else (c['texto'], c['primaria'])
    destino = VIDEO / 'assets' / 'job' / job.nome.replace('/', '_')
    destino.mkdir(parents=True, exist_ok=True)
    marca = {'marca': m['nome'].upper(),
             'tema': {'fundo': escuro, 'fundo2': c['secundaria'], 'texto': claro,
                      'mudo': _mix(claro, escuro, 0.45), 'destaque': c['destaque']}}
    forma = m.get('forma')
    if d.get('variante'):
        forma = (m.get('forma_variantes') or {}).get(d['variante'])
        if not forma:
            raise SystemExit(f'carrossel: variante {d["variante"]!r} não existe em forma_variantes do marca.json')
    if forma and forma.get('degrade'):
        marca['forma'] = forma
        marca['tema']['fundo'], marca['tema']['fundo2'] = forma['degrade'][2], forma['degrade'][1]
    logo = (m.get('logo') or {}).get('arquivo')
    if logo and (pasta / logo).exists():
        shutil.copy2(pasta / logo, destino / 'logo.png')
        marca['logo_src'] = f'assets/job/{destino.name}/logo.png'
    f = (m.get('fontes') or {}).get('titulo') or {}
    fonte = (ROOT / f['arquivo']) if f.get('arquivo') else None
    if fonte and fonte.exists():
        shutil.copy2(fonte, destino / fonte.name)
        marca['fonte_titulo'] = f['familia']
        marca['fonte_src'] = f'assets/job/{destino.name}/{fonte.name}'
        marca['escala_titulo'] = d.get('escala_titulo', 0.6 if f['familia'] in LARGAS else 1)
    return marca


LARGAS = {'Orbitron'}  # famílias largas: título menor para caber


def _resolve_assets(job: Job, d: dict, saida):
    """slide.asset = id do catálogo do cliente (assets/index.json). Copia o arquivo para 1-entrada/imagens e vira slide.imagem."""
    if not any(s.get('asset') for s in d['slides']):
        return
    if not d.get('client'):
        raise SystemExit('carrossel: "asset" no slide exige "client" no carrossel.json')
    base = Path(saida) / d['client'] / 'assets'
    cat = {i['id']: i for i in json.loads((base / 'index.json').read_text(encoding='utf-8'))['items']}
    pasta = job.entrada / 'imagens'
    pasta.mkdir(parents=True, exist_ok=True)
    for s in d['slides']:
        if s.get('asset'):
            i = cat.get(s['asset'])
            if not i:
                raise SystemExit(f'carrossel: asset {s["asset"]} não existe no catálogo')
            if 'discard' in i['use'] or i['blank']:
                raise SystemExit(f'carrossel: asset {s["asset"]} está descartado no catálogo')
            nome = f'{s["asset"]}{Path(i["path"]).suffix.lower()}'
            shutil.copy2(base / i['path'], pasta / nome)
            s['figura' if s.get('tipo') == 'figura' else 'imagem'] = nome


def _duracao(arq: Path) -> float:
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(arq)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def _videos(job: Job, slides: list):
    """slide.video = arquivo em 1-entrada/videos/ (b-roll livre). Vira MP4 H.264 sem áudio em video/assets/job/."""
    destino = VIDEO / 'assets' / 'job' / job.nome.replace('/', '_')
    for s in slides:
        if not s['video']:
            continue
        origem = job.entrada / 'videos' / s['video']
        if not origem.exists():
            raise SystemExit(f'slide {s["idx"]}: vídeo {origem} não existe')
        destino.mkdir(parents=True, exist_ok=True)
        alvo = destino / (origem.stem + '.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(origem), '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                        '-vf', f'scale={s["w"]}:{s["h"]}:force_original_aspect_ratio=increase,crop={s["w"]}:{s["h"]},fps=30',
                        '-movflags', '+faststart', str(alvo)], check=True)
        dur = _duracao(alvo)
        if dur < s['dur']:
            print(f'  AVISO slide {s["idx"]}: vídeo tem {dur:.1f}s e o slide {s["dur"]:.1f}s; o fundo some no fim (use clipe mais longo)')
        s['video'] = {'src': f'assets/job/{destino.name}/{alvo.name}', 'dur': dur}


def _imagens(job: Job, slides: list):
    """slide.imagem = arquivo em 1-entrada/imagens/ (do usuário ou de fonte livre); copia para video/assets/job/."""
    destino = VIDEO / 'assets' / 'job' / job.nome.replace('/', '_')
    for s in slides:
        for chave in ('imagem', 'figura'):
            if not s[chave]:
                continue
            origem = job.entrada / 'imagens' / s[chave]
            if not origem.exists():
                raise SystemExit(f'slide {s["idx"]}: imagem {origem} não existe')
            destino.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(origem, destino / s[chave])
            s[chave] = f'assets/job/{destino.name}/{s[chave]}'


def validar(d: dict):
    if not d.get('slides'):
        raise SystemExit('carrossel.json: falta "slides"')
    if d.get('ritmo', 'medio') not in RITMOS:
        raise SystemExit(f'carrossel.json: ritmo deve ser {list(RITMOS)}')
    if d.get('formato', 'post') not in DIM:
        raise SystemExit(f'carrossel.json: formato deve ser {list(DIM)}')
    if len(d['slides']) > 10:
        raise SystemExit('carrossel.json: o Instagram aceita até 10 slides')
    for k in TEMA:
        if k not in {**TEMA, **d.get('tema', {})}:
            raise SystemExit(f'carrossel.json: tema sem "{k}"')


def estaticos(job: Job, slides: list, tema: dict, marca: str, kit: dict | None = None):
    pasta = job.final / 'png'
    pasta.mkdir(parents=True, exist_ok=True)
    for f in pasta.glob('*.png'):
        f.unlink()
    bruto = job.interno / 'png_bruto'
    for s in slides:
        (VIDEO / 'index.html').write_text(_html(s, tema, marca, kit), encoding='utf-8')
        if bruto.exists():
            shutil.rmtree(bruto)
        bruto.mkdir(parents=True)
        t = round(s['dur'] - 0.05, 2)
        pnpm_hyperframes('snapshot', '.', '--at', str(t), '--no-end', '--keep', '--output', str(bruto.resolve()))
        achados = list(bruto.glob('*.png'))
        if not achados:
            raise SystemExit(f'slide {s["idx"]}: snapshot não gerou PNG')
        shutil.copyfile(achados[0], pasta / f'{s["idx"]:02d}.png')
        print(f'  slide {s["idx"]}/{s["total"]}: {pasta / (str(s["idx"]).zfill(2) + ".png")}')
    shutil.rmtree(bruto, ignore_errors=True)
    folha(job, pasta)


def folha(job: Job, pasta: Path):
    """2-aprovar/carrossel_folha.png: todos os slides lado a lado, para aprovar de uma vez."""
    arquivos = sorted(pasta.glob('*.png'))
    n = len(arquivos)
    cw, ch = 360, 450
    cols = min(n, 5)
    entradas = [x for a in arquivos for x in ('-i', str(a))]
    escala = ''.join(f'[{i}:v]scale={cw}:{ch}[s{i}];' for i in range(n))
    layout = '|'.join(f'{(i % cols) * cw}_{(i // cols) * ch}' for i in range(n))
    fc = (escala.replace('[s0];', '[o]') if n == 1 else
          escala + ''.join(f'[s{i}]' for i in range(n)) + f'xstack=inputs={n}:layout={layout}[o]')
    job.aprovar.mkdir(parents=True, exist_ok=True)
    saida = job.aprovar / 'carrossel_folha.png'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *entradas, '-filter_complex', fc, '-map', '[o]', str(saida)], check=True)
    print(f'  folha: {saida}')


def animados(job: Job, slides: list, tema: dict, marca: str, kit: dict | None = None):
    pasta = job.final / 'animado'
    pasta.mkdir(parents=True, exist_ok=True)
    pnpm = shutil.which('pnpm') or 'pnpm'
    for s in slides:
        (VIDEO / 'index.html').write_text(_html(s, tema, marca, kit), encoding='utf-8')
        alvo = pasta / f'{s["idx"]:02d}.mp4'
        print(f'  renderizando slide {s["idx"]}/{s["total"]} ({s["dur"]:.1f}s)...')
        r = subprocess.run([pnpm, 'exec', 'hyperframes', 'render', '.', '-o', str(alvo.resolve()), '--fps', str(FPS),
                            '-q', 'looks'], cwd=VIDEO, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode != 0:
            raise SystemExit(f'hyperframes render falhou no slide {s["idx"]}:\n{(r.stdout + r.stderr)[-2000:]}')
    for velho in pasta.glob('*-sem-som.mp4'):  # re-render invalida o original guardado pelo --som
        velho.unlink()
    print(f'  MP4 em {pasta}  (próximo passo: vf carrossel {job.nome} --som)')


def som(job: Job, slides: list):
    """Mixa o som de cada slide (sound-layer) e junta ao MP4. Guarda o original como NN-sem-som.mp4."""
    raiz = ROOT / 'ferramentas' / 'sound-layer'
    if not (raiz / 'audio' / 'kit' / 'catalog.json').exists():
        raise SystemExit('som: kit de sons ausente; rode `uv run scripts/sfx.py kit` em ferramentas/sound-layer')
    uv = shutil.which('uv') or 'uv'
    (job.interno / 'som').mkdir(parents=True, exist_ok=True)
    n = len(slides)
    for i in range(1, n + 1):
        cue = job.interno / 'som' / f'cues-{i:02d}.json'
        cue.write_text(json.dumps(cues_slide(slides[i - 1]), ensure_ascii=False, indent=1), encoding='utf-8')
        mp4 = job.final / 'animado' / f'{i:02d}.mp4'
        if not mp4.exists():
            raise SystemExit(f'som: falta {mp4}; rode antes `vf carrossel {job.nome} --animar`')
        sem = mp4.with_name(f'{i:02d}-sem-som.mp4')
        if not sem.exists():
            shutil.copyfile(mp4, sem)
        pasta = job.interno / 'som' / f'mix-{i:02d}'
        pasta.mkdir(parents=True, exist_ok=True)
        r = subprocess.run([uv, 'run', 'scripts/mix.py', str(cue.resolve()), '--out', str(pasta.resolve())], cwd=raiz,
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode != 0:
            raise SystemExit(f'mix do slide {i} falhou:\n' + (r.stdout + r.stderr)[-1500:])
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(sem), '-i', str(pasta / 'mix.wav'), '-map', '0:v', '-map', '1:a',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', str(mp4)], check=True)
        print(f'  slide {i}/{n}: som aplicado em {mp4}')


def executar(a):
    job = Job(a.saida, a.job).criar()
    cfg = job.entrada / 'carrossel.json'
    if not cfg.exists():
        (job.entrada / 'imagens').mkdir(exist_ok=True)
        cfg.write_text(json.dumps(EXEMPLO, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'criado {cfg} (exemplo). Edite e rode de novo: vf carrossel {a.job}')
        if not a.exemplo:
            return
    if getattr(a, 'som', False):
        d = json.loads(cfg.read_text(encoding='utf-8'))
        validar(d)
        som(job, [montar_slide(x, i, len(d['slides']), d.get('ritmo', 'medio')) for i, x in enumerate(d['slides'])])
        return
    if not (VIDEO / 'node_modules').exists():
        raise SystemExit('carrossel: rode `pnpm install` dentro de videoFactory/video')
    d = json.loads(cfg.read_text(encoding='utf-8'))
    validar(d)
    kit = _client_brand(job, d, a.saida)
    tema = {**TEMA, **(kit or {}).get('tema', {}), **d.get('tema', {})}
    n = len(d['slides'])
    _resolve_assets(job, d, a.saida)
    w, h = DIM[d.get('formato', 'post')]
    slides = [montar_slide(s, i, n, d.get('ritmo', 'medio')) for i, s in enumerate(d['slides'])]
    for s in slides:
        s['w'], s['h'] = w, h
    _imagens(job, slides)
    _videos(job, slides)
    marca = d.get('marca') or (kit or {}).get('marca', '')
    estaticos(job, slides, tema, marca, kit)
    if a.animar:
        animados(job, slides, tema, marca, kit)
