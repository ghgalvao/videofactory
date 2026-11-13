"""CLI da videoFactory.

  uv run vf cut FONTE [INICIO FIM --nome NOME | --lote arquivo] [opções]
  uv run vf narrate ROTEIRO [opções]          (em construção)
"""
import argparse
import sys

from .core.paths import SAIDA_PADRAO
from .modes import cut, narrate, storyboard


def montar_parser():
    p = argparse.ArgumentParser(prog='vf', description='Fábrica de vídeos curtos verticais (CPU only)')
    sub = p.add_subparsers(dest='modo', required=True)

    c = sub.add_parser('cut', help='vídeo existente → corte vertical legendado',
                       description='FONTE: link do YouTube ou arquivo local. INICIO/FIM: segundos, mm:ss ou hh:mm:ss.')
    c.add_argument('fonte')
    c.add_argument('inicio', nargs='?'); c.add_argument('fim', nargs='?')
    c.add_argument('--nome'); c.add_argument('--lote', help='uma linha por corte: INICIO FIM NOME')
    c.add_argument('--layout', default='vertical', choices=['vertical', 'desfocado'])
    c.add_argument('--titulo', default=''); c.add_argument('--subtitulo', default='')
    c.add_argument('--modelo', default='medium', help='tiny/base/small/medium/large-v3')
    c.add_argument('--ignorar-canto', action='store_true', help='ignora rostos no canto inferior direito (Libras)')
    c.add_argument('--refazer-legenda', action='store_true', help='regera legenda.ass (perde edições manuais)')
    c.add_argument('--saida', default=str(SAIDA_PADRAO), help='pasta dos jobs')

    n = sub.add_parser('narrate', help='roteiro.txt → narração → vídeo vertical legendado',
                       description='Gera narration.wav, words.json e video.mp4 em saida/<nome>/.')
    n.add_argument('roteiro', help='arquivo .txt com o roteiro')
    n.add_argument('--nome', help='nome do job (padrão: nome do arquivo)')
    n.add_argument('--engine', default='kokoro', choices=['kokoro', 'edge', 'voicebox'])
    n.add_argument('--voz', default=None,
                   help='kokoro: pf_dora (padrão), pm_alex, pm_santa. edge: pt-BR-AntonioNeural (padrão), pt-BR-FranciscaNeural. voicebox: nome do perfil criado no app')
    n.add_argument('--modelo', default='medium', help='modelo Whisper para os tempos por palavra')
    n.add_argument('--renderer', default='ass', choices=['ass', 'hyperframes', 'dinamico'],
                   help='ass: ffmpeg rápido (padrão). hyperframes: legenda animada. ')
    n.add_argument('--refazer', action='store_true', help='regera narração, tempos e vídeo')
    n.add_argument('--saida', default=str(SAIDA_PADRAO), help='pasta dos jobs')
    of = sub.add_parser('oferta', help='vídeo de oferta de varejo a partir de 1-entrada/oferta.json',
                        description='1ª vez cria oferta.json de exemplo. Depois: narração + folha; --animar gera o vídeo.')
    of.add_argument('job'); of.add_argument('--animar', action='store_true')
    of.add_argument('--refazer', action='store_true', help='regera a narração mesmo sem mudança no texto')
    of.add_argument('--exemplo', action='store_true', help='na 1ª vez, já gera usando o exemplo')
    of.add_argument('--saida', default=str(SAIDA_PADRAO), help='pasta dos jobs')
    cv = sub.add_parser('carrossel', help='carrossel vivo (4:5): PNG por slide, depois MP4 animado + cues de som',
                        description='1ª vez cria carrossel.json de exemplo. Depois: PNG + folha; --animar gera os MP4.')
    cv.add_argument('job'); cv.add_argument('--animar', action='store_true')
    cv.add_argument('--som', action='store_true', help='mixa o som de cada slide e junta ao MP4 (depois do --animar)')
    cv.add_argument('--exemplo', action='store_true', help='na 1ª vez, já gera usando o exemplo')
    cv.add_argument('--saida', default=str(SAIDA_PADRAO), help='pasta dos jobs')
    cl = sub.add_parser('client', help='gestão de cliente: esqueleto, checagem das abas e lista',
                        description='new <slug> "Nome" cria o esqueleto; check <slug> mostra o que falta; list lista os clientes.')
    cl.add_argument('acao', choices=['new', 'check', 'list'])
    cl.add_argument('slug', nargs='?'); cl.add_argument('nome', nargs='?')
    cl.add_argument('--saida', default=str(SAIDA_PADRAO), help='pasta dos jobs')
    dc = sub.add_parser('doc', help='documentos do cliente (proposta, contrato, extrato, orçamento) em PDF',
                        description='new <cliente> <tipo> cria os dados; build gera HTML e PDF; list mostra os arquivos.')
    dc.add_argument('acao', choices=['new', 'build', 'list'])
    dc.add_argument('cliente'); dc.add_argument('tipo', nargs='?')
    dc.add_argument('--saida', default=str(SAIDA_PADRAO), help='pasta dos jobs')
    asg = sub.add_parser('assets', help='catálogo de imagens e vídeos do cliente (assets/index.json)',
                         description='scan indexa; sheet gera folhas numeradas; set descreve itens; find procura.')
    asg.add_argument('acao', choices=['scan', 'sheet', 'set', 'find'])
    asg.add_argument('cliente'); asg.add_argument('ids', nargs='*')
    asg.add_argument('--subject'); asg.add_argument('--tags'); asg.add_argument('--use')
    asg.add_argument('--people', choices=['yes', 'no']); asg.add_argument('--rights', choices=['ok', 'confirm'])
    asg.add_argument('--note'); asg.add_argument('--tag'); asg.add_argument('--orient', choices=['vertical', 'horizontal', 'square'])
    asg.add_argument('--min', choices=['media', 'alta']); asg.add_argument('--novos', action='store_true', help='sheet: só os sem descrição')
    asg.add_argument('--saida', default=str(SAIDA_PADRAO), help='pasta dos jobs')
    bd = sub.add_parser('brand', help='extração de marca: cores dominantes de um impresso, captura ou logo',
                        description='colors <imagem> [--k 6] mede as cores; use no flyer, na capa do PDF e na captura do site.')
    bd.add_argument('acao', choices=['colors']); bd.add_argument('imagem'); bd.add_argument('--k', type=int, default=6)
    rv = sub.add_parser('review', help='revisão de texto dos jobs do cliente: ortografia, bloqueios, pendências, legenda',
                        description='review <cliente> <job...> ou --all. Regras em marca.json (bloqueados, atencao, vocabulario).')
    rv.add_argument('cliente'); rv.add_argument('jobs', nargs='*'); rv.add_argument('--all', dest='todos', action='store_true')
    rv.add_argument('--saida', default=str(SAIDA_PADRAO), help='pasta dos jobs')
    pk = sub.add_parser('pack', help='pack de conteúdo do cliente: posts, legendas, revisão, grade e plano de publicação em pasta e zip',
                        description='new <cliente> cria o pack.json; build gera exports/<pack>/ e o zip (revisa os textos antes).')
    pk.add_argument('acao', choices=['new', 'build']); pk.add_argument('cliente'); pk.add_argument('pack', nargs='?', default='pack-01')
    pk.add_argument('--inicio', help='primeira data de publicação (AAAA-MM-DD)'); pk.add_argument('--por-semana', type=int, default=3)
    pk.add_argument('--saida', default=str(SAIDA_PADRAO), help='pasta dos jobs')
    sub.add_parser('estilos', help='lista os estilos de vídeo disponíveis e planejados')
    nv = sub.add_parser('novo', help='cria um job novo com roteiro-modelo e storyboard-esqueleto do estilo',
                        description='Ex.: vf novo paper e2-meu-tema. Estilos: veja `vf estilos`.')
    nv.add_argument('estilo'); nv.add_argument('job')
    nv.add_argument('--saida', default=str(SAIDA_PADRAO), help='pasta dos jobs')
    ck = sub.add_parser('checar', help='valida roteiro, storyboard e margens sem olhar imagem',
                        description='Valida o job por script (zero visão): roteiro, tempos, frases, elementos e margens.')
    ck.add_argument('job')
    ck.add_argument('--completo', action='store_true', help='também roda o `hyperframes check` (lint/layout/contraste)')
    ck.add_argument('--saida', default=str(SAIDA_PADRAO), help='pasta dos jobs')
    o = sub.add_parser('organizar', help='migra jobs antigos para 1-entrada / 2-aprovar / 3-final / _interno',
                       description='Sem argumentos, lista os jobs. Use --todos ou nomes de jobs. --simular só mostra o que faria.')
    o.add_argument('jobs', nargs='*', help="nomes dos jobs (ex.: e1-mar-salgado, cliente/b1-apresentacao)")
    o.add_argument('--todos', action='store_true', help='todos os jobs de saida/')
    o.add_argument('--simular', action='store_true', help='não move nada, só mostra')
    o.add_argument('--saida', default=str(SAIDA_PADRAO), help='pasta dos jobs')
    s = sub.add_parser('storyboard', help='planos de cena → folha de aprovação (e depois o vídeo animado)',
                       description='Usa saida/<job>/storyboard.json + words.json + narration.wav.')
    s.add_argument('job', help='nome do job (pasta em saida/)')
    s.add_argument('--animar', action='store_true', help='renderiza o vídeo animado (após aprovar a folha)')
    s.add_argument('--saida', default=str(SAIDA_PADRAO), help='pasta dos jobs')
    pn = sub.add_parser('panel', help='painel local: galerias, etapa de cada job e visualização dos vídeos')
    pn.add_argument('--port', type=int, default=8765, help='porta local (padrão 8765)')
    pn.add_argument('--no-browser', action='store_true', help='não abre o navegador')
    return p


def main():
    for stream in (sys.stdout, sys.stderr):  # Windows: pipe/Git Bash usam cp1252 e quebram em acento e seta
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    a = montar_parser().parse_args()
    if a.modo == 'cut':
        cut.executar(a)
    elif a.modo == 'novo':
        from .core.novo import novo
        j = novo(a.estilo, a.job, a.saida)
        print(f'job criado: {j.raiz}')
        print(f'  1) edite 1-entrada/roteiro.txt (troque os [colchetes]) e 1-entrada/storyboard.json')
        print(f'  2) vf narrate {j.roteiro} --nome {a.job} --engine edge --modelo small')
        print(f'  3) vf checar {a.job}  ->  vf storyboard {a.job}  ->  vf storyboard {a.job} --animar')
    elif a.modo == 'checar':
        from .core.checar import checar
        from .core.paths import Job
        job = Job(a.saida, a.job)
        erros, avisos = checar(job)
        for e in erros:
            print(f'ERRO   {e}')
        for w in avisos:
            print(f'AVISO  {w}')
        print()
        print(f'{len(erros)} erro(s), {len(avisos)} aviso(s)' + ('  ->  pronto para aprovar a folha' if not erros else ''))
        if a.completo and not erros and job.words.exists():
            from .modes.storyboard import _html
            from .core.hyperframes import pnpm_hyperframes, preparar_projeto
            html, _, _, _, wav = _html(job, animado=False)
            preparar_projeto(html, wav)
            r = pnpm_hyperframes('check', '.')
            print((r.stdout + r.stderr)[-1500:])
        raise SystemExit(1 if erros else 0)
    elif a.modo == 'organizar':
        from pathlib import Path
        from .core.organizar import jobs_em, organizar
        saida = Path(a.saida)
        alvos = jobs_em(saida) if (a.todos or not a.jobs) else [saida / j for j in a.jobs]
        for j in alvos:
            mov = organizar(j, a.simular)
            rot = 'SIMULAÇÃO' if a.simular else 'organizado'
            print(f'[{j.relative_to(saida)}] {rot}: {len(mov)} movimentos' if mov else f'[{j.relative_to(saida)}] já organizado')
            if a.simular or not a.todos:
                for m in mov:
                    print('   ', m)
    elif a.modo == 'estilos':
        from .estilos import listar
        listar()
    elif a.modo == 'oferta':
        from .core.oferta import executar as oferta
        oferta(a)
    elif a.modo == 'pack':
        from .core.pack import run as pack
        pack(a)
    elif a.modo == 'review':
        from .core.review import run as review
        review(a)
    elif a.modo == 'brand':
        from .core.brand import run as brand
        brand(a)
    elif a.modo == 'assets':
        from .core.assets import run as assets
        assets(a)
    elif a.modo == 'doc':
        from .core.docs import run as doc
        doc(a)
    elif a.modo == 'client':
        from .core.client import run as client
        if a.acao != 'list' and not a.slug:
            raise SystemExit('client: informe o slug do cliente')
        client(a)
    elif a.modo == 'carrossel':
        from .core.carrossel import executar as carrossel
        carrossel(a)
    elif a.modo == 'storyboard':
        storyboard.executar(a)
    elif a.modo == 'narrate':
        narrate.executar(a)
    elif a.modo == 'panel':
        from .panel.server import run
        run(a)
    else:
        print(f'vf {a.modo}: ainda não implementado')


if __name__ == '__main__':
    main()
