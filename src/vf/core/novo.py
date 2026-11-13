"""`vf novo ESTILO JOB`: cria a pasta do job já com roteiro-modelo e storyboard-esqueleto do estilo."""
import shutil

from .paths import ROOT, Job

CENAS = {'paper': 'paper', 'mechanism-3d': 'panela', 'whiteboard': 'quadro', 'blueprint': 'blueprint',
         'fintech-motion': 'fintech', 'data-infographic': 'fintech', 'stick-figure': 'fintech',
         'ken-burns': 'fintech', 'biz-saas-demo': 'fintech', 'documentary': 'documental', 'pixel-avatar': 'pixel-avatar'}  # estilo → cena do storyboard.json


def novo(estilo: str, nome: str, saida: str) -> Job:
    pasta = ROOT / 'styles' / estilo
    if not pasta.exists():
        raise SystemExit(f'estilo desconhecido: {estilo} (veja `vf estilos`)')
    job = Job(saida, nome)
    if job.entrada.exists() and any(job.entrada.iterdir()):
        raise SystemExit(f'{job.raiz} já tem arquivos em 1-entrada; escolha outro nome')
    job.criar()
    modelo_roteiro = pasta / 'roteiro.modelo.txt'
    modelo_sb = pasta / 'storyboard.modelo.json'
    if modelo_roteiro.exists():
        shutil.copyfile(modelo_roteiro, job.roteiro)
    else:
        job.roteiro.write_text('[GANCHO]?\n[CONTEXTO].\n[...].\n\nSegue pra [PRÓXIMO].\n', encoding='utf-8')
    if modelo_sb.exists():
        shutil.copyfile(modelo_sb, job.storyboard)
    elif estilo in CENAS:
        job.storyboard.write_text('{"cena": "%s", "planos": []}\n' % CENAS[estilo], encoding='utf-8')
    return job
