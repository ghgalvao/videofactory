"""Modelo de vídeo de OFERTA de varejo (açougue, mercado, padaria...): oferta.json → roteiro + storyboard → vídeo.

Uso:  vf oferta <job>            1ª vez cria 1-entrada/oferta.json de exemplo; depois gera narração + folha
      vf oferta <job> --animar   renderiza o vídeo final
Edite SÓ o oferta.json (roteiro.txt e storyboard.json são regerados a cada execução).
Fotos/logo: arquivos em 1-entrada/imagens/ (PNG com fundo transparente fica melhor); vazio = placeholder.
"""
import json
import os
import re
from argparse import Namespace

from .paths import Job

EXEMPLO = {
    "linha1": "SEXTOU",
    "linha2": "NO AÇOUGUE",
    "placa": "OFERTA RELÂMPAGO",
    "chamada": "Sextou no açougue! Oferta relâmpago!",
    "logo": "",
    "produtos": [
        {"nome": "COSTELA SUÍNA", "fala": "Costela suína", "preco": "19,90", "unidade": "kg", "foto": ""},
        {"nome": "PICANHA", "fala": "Picanha", "preco": "69,90", "unidade": "kg", "foto": ""}
    ],
    "cta": "Chama no WhatsApp e garanta o seu!",
    "whatsapp": "(00) 90000-0000",
    "validade": "domingo",
    "cores": {"fundo0": "#5c0006", "fundo1": "#b3000c", "fundo2": "#ff4a1c", "ouro1": "#ffd23f", "ouro2": "#ff8a00", "borda": "#3d0800"},
    "voz": "pt-BR-AntonioNeural",
    "taxa": "+20%"
}
UNID_TELA = {'kg': 'O KG', 'un': 'A UNIDADE', 'pct': 'O PACOTE', 'lt': 'O LITRO', 'dz': 'A DÚZIA'}
UNID_FALA = {'kg': 'o quilo', 'un': 'a unidade', 'pct': 'o pacote', 'lt': 'o litro', 'dz': 'a dúzia'}


def _preco_falado(p: str) -> str:
    reais, _, cent = p.replace('.', '').partition(',')
    cent = cent.ljust(2, '0')[:2] if cent else '00'
    return f'{int(reais)} reais' + ('' if cent == '00' else f' e {int(cent)}')


def gerar(job: Job, d: dict):
    frases = [re.sub(r'\s*[.!?]+\s*', ', ', d['chamada'].strip()).strip(', ') + '!']  # chamada = 1 frase só
    for p in d['produtos']:
        u = UNID_FALA.get(p.get('unidade', ''), '')
        frases.append(f'{p["fala"]} por apenas {_preco_falado(p["preco"])}{" " + u if u else ""}.')
    fim = [d.get('cta', 'Chama no WhatsApp e garanta o seu!')]
    if d.get('validade'):
        fim.append(f'Oferta válida até {d["validade"]}, ou enquanto durar o estoque.')
    job.roteiro.write_text(' '.join(frases) + '\n\n' + ' '.join(fim) + '\n', encoding='utf-8')

    def logo(y, k=0.0):
        el = {"tipo": "pilula", "x": 540, "y": y, "entrada": "cima", "frase": 1, "atraso": k}
        if d.get('logo'):
            el['arquivo'] = d['logo']
        else:
            el['texto'] = 'SUA LOGO AQUI'
        return el
    planos = [{"id": 1, "frases": [1], "quadro": 99, "elementos": [
        logo(300),
        {"tipo": "t3d", "texto": d['linha1'], "s": 190, "x": 540, "y": 760, "rot": -3, "entrada": "blur", "frase": 1, "atraso": 0.1},
        {"tipo": "t3d", "texto": d['linha2'], "s": 130, "x": 540, "y": 970, "rot": -3, "branco": True, "entrada": "blur", "frase": 1, "atraso": 0.45},
        {"tipo": "placa", "texto": d['placa'], "x": 540, "y": 1170, "rot": -3, "entrada": "baixo", "frase": 1, "atraso": 0.9}]}]
    for i, p in enumerate(d['produtos']):
        f = i + 2
        prod = {"tipo": "produto", "x": 540, "y": 1010, "w": 860, "entrada": "baixo", "frase": f, "atraso": 0.05}
        if p.get('foto'):
            prod['arquivo'] = p['foto']
        planos.append({"id": f, "frases": [f], "quadro": 99, "elementos": [
            {"tipo": "t3d", "texto": f'{d["linha1"]} {d["linha2"]}', "s": 92, "x": 540, "y": 300, "rot": -2, "entrada": "cima", "frase": f, "atraso": 0.0},
            prod,
            {"tipo": "etiq", "texto": p['nome'], "x": 540, "y": 600, "rot": -2, "entrada": "esq" if i % 2 == 0 else "dir", "frase": f, "atraso": 0.25},
            {"tipo": "preco", "valor": p['preco'], "unidade": UNID_TELA.get(p.get('unidade', ''), ''), "x": 660, "y": 1360,
             "entrada": "bate", "frase": f, "atraso": 0.9}]})
    n = len(d['produtos']) + 2
    cta = list(range(n, n + len(fim)))
    planos.append({"id": n, "frases": cta, "quadro": 99, "elementos": [
        logo(330),
        {"tipo": "t3d", "texto": d['linha1'], "s": 150, "x": 540, "y": 680, "rot": -3, "entrada": "blur", "frase": n, "atraso": 0.0},
        {"tipo": "t3d", "texto": d['linha2'], "s": 120, "x": 540, "y": 840, "rot": -3, "branco": True, "entrada": "blur", "frase": n, "atraso": 0.2},
        {"tipo": "zap", "texto": d['whatsapp'], "x": 540, "y": 1140, "entrada": "baixo", "frase": n, "atraso": 0.5, "pulsa": True},
        {"tipo": "aviso", "texto": (f'OFERTA VÁLIDA ATÉ {d["validade"].upper()} OU ENQUANTO DURAR O ESTOQUE' if d.get('validade') else 'ENQUANTO DURAR O ESTOQUE'),
         "x": 540, "y": 1290, "entrada": "fade", "frase": cta[-1], "atraso": 0.1}]})
    sb = {"cena": "oferta", "dy": 0, "tema": d.get('cores', {}), "legenda": {"texto": "#ffffff", "destaque": "#ffd23f"},
          "substituicoes": [], "planos": planos}
    job.storyboard.write_text(json.dumps(sb, ensure_ascii=False, indent=1), encoding='utf-8')


def executar(a):
    job = Job(a.saida, a.job).criar()
    cfg = job.entrada / 'oferta.json'
    if not cfg.exists():
        (job.entrada / 'imagens').mkdir(exist_ok=True)
        cfg.write_text(json.dumps(EXEMPLO, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'criado {cfg} (exemplo). Edite e rode de novo: vf oferta {a.job}')
        if not a.exemplo:
            return
    d = json.loads(cfg.read_text(encoding='utf-8'))
    antigo = job.roteiro.read_text(encoding='utf-8') if job.roteiro.exists() else ''
    gerar(job, d)
    from ..modes import narrate, storyboard
    if a.refazer or not job.words.exists() or job.roteiro.read_text(encoding='utf-8') != antigo:
        os.environ['VF_TAXA'] = d.get('taxa', '+20%')
        narrate.executar(Namespace(roteiro=str(job.roteiro), nome=a.job, engine='edge', voz=d.get('voz'), modelo='small',
                                   renderer='ass', refazer=True, saida=a.saida))
    storyboard.executar(Namespace(job=a.job, animar=a.animar, saida=a.saida))
