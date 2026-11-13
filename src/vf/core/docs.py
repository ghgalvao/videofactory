"""Client documents (proposal, contract, service statement, estimate) from data files, always exportable as PDF.

  vf doc new <client> <type>     creates documentos/<type>.json prefilled from the client folder (never overwrites)
  vf doc build <client> <type>   renders documentos/<type>-<date>.html and .pdf (headless Chrome or Edge)
  vf doc list <client>           documents and their data files

Types: proposal, contract, statement, estimate, presentation (16:9 slides, see core/slides.py). Data: saida/clients/<client>/documentos/<type>.json.
Issuer (the agency): saida/agency.json. Client identity: saida/clients/<client>/marca.json.
Totals, balance and amounts in words are computed here, never typed by hand. A document that still has [CONFIRMAR]
in its data is built as a DRAFT (watermark and -rascunho in the file name), never as final.
"""
import base64
import html
import json
import subprocess
from datetime import date
from pathlib import Path

from .client import OPEN, home
from .paths import SAIDA_PADRAO

TYPES = {'proposal': 'Proposta comercial', 'contract': 'Contrato de prestação de serviços',
         'statement': 'Extrato de serviços', 'estimate': 'Orçamento', 'presentation': 'Apresentação'}
MONTHS = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro',
          'novembro', 'dezembro']

AGENCY_MODEL = {'nome': OPEN, 'razao_social': OPEN, 'documento': OPEN, 'representante': OPEN, 'cidade': OPEN,
                'email': OPEN, 'telefone': OPEN, 'pix': OPEN, 'logo': None, 'cor': '#1f2937'}

MODELS = {
    'statement': {
        'data': 'hoje', 'entregues': [{'item': OPEN, 'descricao': '', 'status': 'Entregue'}],
        'investimento': [{'descricao': 'Valor total do projeto', 'valor': 0}], 'pago': 0,
        'recorrente': [{'descricao': OPEN, 'valor': 0, 'periodicidade': 'ano'}],
        'observacoes': ['Pedidos adicionais têm escopo e orçamento definidos por escrito antes de começar.'],
    },
    'proposal': {
        'data': 'hoje', 'validade_dias': 15, 'resumo': OPEN,
        'entregaveis': [{'titulo': OPEN, 'descricao': '', 'itens': []}],
        'investimento': [{'descricao': OPEN, 'valor': 0}], 'condicoes_pagamento': OPEN,
        'prazos': [OPEN], 'premissas': ['Textos, fotos e logos enviados ou autorizados pelo cliente.',
                                        'Uma rodada de ajuste incluída; mudança de escopo depois da aprovação é orçada à parte.'],
        'proximos_passos': ['Aprovação desta proposta por escrito.'],
    },
    'estimate': {
        'data': 'hoje', 'validade_dias': 15,
        'itens': [{'descricao': OPEN, 'quantidade': 1, 'valor_unitario': 0}], 'desconto': 0,
        'condicoes_pagamento': OPEN, 'observacoes': [],
    },
    'presentation': {
        'data': 'hoje', 'titulo': OPEN,
        'slides': [{'tipo': 'capa', 'kicker': '', 'titulo': OPEN, 'subtitulo': ''},
                   {'tipo': 'texto', 'titulo': OPEN, 'texto': [OPEN], 'itens': []},
                   {'tipo': 'cta', 'titulo': OPEN, 'texto': '', 'contato': []}],
    },
    'contract': {
        'data': 'hoje', 'cidade': OPEN,
        'cliente': {'razao_social': OPEN, 'documento': OPEN, 'representante': OPEN, 'endereco': OPEN},
        'objeto': [{'titulo': OPEN, 'descricao': ''}],
        'investimento': [{'descricao': OPEN, 'valor': 0}], 'forma_pagamento': OPEN,
        'prazo_entrega': OPEN, 'rodadas_ajuste': 1, 'recorrencia': None,
        'propriedade_intelectual': 'Após a quitação integral, os direitos de uso das peças entregues passam à CONTRATANTE. '
                                   'Materiais de terceiros (fontes, fotos, músicas) seguem a licença de origem.',
        'confidencialidade': 'As partes mantêm sigilo sobre informações comerciais trocadas durante o contrato.',
        'rescisao': 'Qualquer parte pode rescindir com aviso por escrito de 15 dias; o trabalho já executado é devido.',
        'foro': OPEN, 'clausulas_extras': [],
    },
}


# ---------- formatting ----------
def money(v) -> str:
    s = f'{float(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'R$ {s}'


_UN = ['zero', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove', 'dez', 'onze', 'doze', 'treze',
       'quatorze', 'quinze', 'dezesseis', 'dezessete', 'dezoito', 'dezenove']
_DEZ = ['', '', 'vinte', 'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta', 'oitenta', 'noventa']
_CEN = ['', 'cento', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos', 'seiscentos', 'setecentos', 'oitocentos',
        'novecentos']


def _upto999(n: int) -> str:
    if n == 100:
        return 'cem'
    c, r = divmod(n, 100)
    parts = [_CEN[c]] if c else []
    if r:
        d, u = divmod(r, 10)
        parts.append(_UN[r] if r < 20 else _DEZ[d] + (f' e {_UN[u]}' if u else ''))
    return ' e '.join(parts)


def _words(n: int) -> str:
    if n == 0:
        return 'zero'
    if n >= 10**9:
        raise ValueError('valor grande demais para escrever por extenso')
    mi, rest = divmod(n, 10**6)
    mil, un = divmod(rest, 1000)
    comps = [(mi, 'um milhão' if mi == 1 else f'{_upto999(mi)} milhões'),
             (mil, 'mil' if mil == 1 else f'{_upto999(mil)} mil'), (un, _upto999(un))]
    comps = [(n_, t) for n_, t in comps if n_]
    out = comps[0][1]
    for i, (n_, t) in enumerate(comps[1:], 1):
        e = i == len(comps) - 1 and (n_ < 100 or n_ % 100 == 0)
        out += (' e ' if e else ' ') + t
    return out


def in_words(v) -> str:
    cents = round(float(v) * 100)
    reais, c = divmod(cents, 100)
    unit = 'real' if reais == 1 else ('de reais' if reais and reais % 10**6 == 0 else 'reais')
    out = f'{_words(reais)} {unit}' if reais or not c else ''
    if c:
        out += (' e ' if out else '') + f'{_words(c)} {"centavo" if c == 1 else "centavos"}'
    return out


def long_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f'{d.day} de {MONTHS[d.month - 1]} de {d.year}'


def _today() -> str:
    return date.today().isoformat()


def _e(x) -> str:
    return html.escape(str(x))


def _open_marks(obj) -> int:
    return json.dumps(obj, ensure_ascii=False).count(OPEN)


# ---------- paths and data ----------
def _agency_file(saida) -> Path:
    return Path(saida) / 'agency.json'


def _read(path: Path, what: str) -> dict:
    if not path.is_file():
        raise SystemExit(f'doc: {what} não existe: {path}')
    return json.loads(path.read_text(encoding='utf-8'))


def new(client: str, kind: str, saida=SAIDA_PADRAO) -> list:
    if kind not in TYPES:
        raise SystemExit(f'doc: tipo {kind!r} desconhecido. Use: {", ".join(TYPES)}')
    h = home(client, saida)
    if not (h / 'marca.json').is_file():
        raise SystemExit(f'doc: cliente {client!r} sem marca.json. Rode `vf client new {client} "Nome"`.')
    made = []
    ag = _agency_file(saida)
    if not ag.is_file():
        ag.write_text(json.dumps(AGENCY_MODEL, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        made.append(str(ag))
    f = h / 'documentos' / f'{kind}.json'
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(MODELS[kind], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        made.append(str(f))
    return made


# ---------- rendering ----------
CSS = """
@page{size:A4;margin:16mm 15mm}
*{box-sizing:border-box}
body{font:11pt/1.5 "Segoe UI",Arial,sans-serif;color:#1c2430;margin:0}
.wrap{max-width:180mm;margin:0 auto}
header{display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid var(--cor);padding-bottom:10px;margin-bottom:18px}
header img{max-height:46px;max-width:150px}
h1{font-size:20pt;margin:0 0 2px}
.sub{color:#5b6573;font-size:10pt}
h2{font-size:12.5pt;margin:20px 0 6px;color:var(--cor);break-after:avoid}
table{width:100%;border-collapse:collapse;margin:6px 0 10px;font-size:10.5pt}
th,td{border-bottom:1px solid #d9dee5;padding:6px 8px;text-align:left;vertical-align:top}
th{background:#f3f5f8;font-size:9.5pt;text-transform:uppercase;letter-spacing:.04em}
td.r,th.r{text-align:right;white-space:nowrap}
tr.total td{font-weight:700;border-top:2px solid var(--cor)}
ul{margin:4px 0 8px;padding-left:20px}
.parties p{margin:2px 0}
.sign{display:flex;gap:30px;margin-top:46px;break-inside:avoid}
.sign div{flex:1;border-top:1px solid #1c2430;padding-top:6px;text-align:center;font-size:10pt}
footer{margin-top:26px;color:#5b6573;font-size:9pt;border-top:1px solid #d9dee5;padding-top:8px}
section{break-inside:avoid}
.draft{position:fixed;top:42%;left:0;right:0;text-align:center;font-size:90pt;font-weight:800;color:rgba(200,30,30,.12);transform:rotate(-24deg);z-index:9;pointer-events:none}
@media print{body{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
"""


def _img(path: Path | None) -> str:
    if not path or not path.is_file():
        return ''
    mime = {'.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}.get(path.suffix.lower(), 'image/png')
    return f'<img alt="" src="data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}">'


def _table(head: list, rows: list, right: tuple = ()) -> str:
    th = ''.join(f'<th class="{"r" if i in right else ""}">{_e(h)}</th>' for i, h in enumerate(head))
    body = ''.join('<tr>' + ''.join(f'<td class="{"r" if i in right else ""}">{c}</td>'
                                    for i, c in enumerate(r)) + '</tr>' for r in rows)
    return f'<table><tr>{th}</tr>{body}</table>'


def _list(items) -> str:
    return '<ul>' + ''.join(f'<li>{_e(i)}</li>' for i in items) + '</ul>' if items else ''


def _total_rows(rows: list, key: str = 'valor') -> tuple[list, float]:
    total = sum(float(r.get(key, 0)) for r in rows)
    return [[_e(r['descricao']), money(r[key])] for r in rows] + [['<b>Total</b>', f'<b>{money(total)}</b>']], total


def render_statement(d, ag, cl):
    rows, total = _total_rows(d['investimento'])
    paid = float(d.get('pago', 0))
    out = '<h2>1. Serviços entregues</h2>' + _table(['Item', 'Descrição', 'Situação'], [
        [_e(x['item']), _e(x.get('descricao', '')), _e(x.get('status', ''))] for x in d['entregues']])
    out += '<h2>2. Investimento</h2>' + _table(['Descrição', 'Valor'], rows, (1,))
    out += _table(['Posição', 'Valor'], [['Já pago', money(paid)], ['<b>Saldo pendente</b>', f'<b>{money(total - paid)}</b>']], (1,))
    if d.get('recorrente'):
        out += '<h2>3. Serviços recorrentes</h2>' + _table(['Descrição', 'Periodicidade', 'Valor'], [
            [_e(x['descricao']), _e(x['periodicidade']), money(x['valor'])] for x in d['recorrente']], (2,))
    if d.get('observacoes'):
        out += '<h2>Observações</h2>' + _list(d['observacoes'])
    return out


def _price(v) -> str:
    return money(v) if isinstance(v, (int, float)) else _e(v)


def render_proposal(d, ag, cl):
    if d.get('opcoes'):  # formatos alternativos: o cliente escolhe um, então não há total
        rows = [[f'<b>{_e(r["descricao"])}</b>' + (f'<br><span class="sub">{_e(r["detalhe"])}</span>' if r.get('detalhe') else ''),
                 _price(r['valor'])] for r in d['investimento']]
    else:
        rows, total = _total_rows(d['investimento'])
    out = f'<h2>Resumo</h2><p>{_e(d["resumo"])}</p><h2>O que será entregue</h2>'
    for x in d['entregaveis']:
        out += f'<section><b>{_e(x["titulo"])}</b><p>{_e(x.get("descricao", ""))}</p>{_list(x.get("itens"))}</section>'
    out += '<h2>Investimento</h2>' + _table(['Formato' if d.get('opcoes') else 'Descrição', 'Valor'], rows, (1,))
    if d.get('avulsos'):
        out += '<h2>Avulsos</h2>' + _table(['Serviço', 'Valor'], [[_e(r['descricao']), _price(r['valor'])] for r in d['avulsos']], (1,))
    out += f'<p>{_e(d["condicoes_pagamento"])}</p>'
    out += '<h2>Prazos</h2>' + _list(d['prazos']) + '<h2>Premissas</h2>' + _list(d['premissas'])
    out += '<h2>Próximos passos</h2>' + _list(d['proximos_passos'])
    out += f'<p class="sub">Proposta válida por {int(d["validade_dias"])} dias a partir de {long_date(_iso(d))}.</p>'
    return out


def render_estimate(d, ag, cl):
    rows = [[_e(i['descricao']), f'{i["quantidade"]:g}', money(i['valor_unitario']),
             money(i['quantidade'] * i['valor_unitario'])] for i in d['itens']]
    sub = sum(i['quantidade'] * i['valor_unitario'] for i in d['itens'])
    disc = float(d.get('desconto', 0))
    rows.append(['<b>Subtotal</b>', '', '', f'<b>{money(sub)}</b>'])
    if disc:
        rows.append(['Desconto', '', '', f'- {money(disc)}'])
    rows.append(['<b>Total</b>', '', '', f'<b>{money(sub - disc)}</b>'])
    out = '<h2>Itens</h2>' + _table(['Descrição', 'Qtd', 'Unitário', 'Total'], rows, (1, 2, 3))
    out += f'<p>{_e(d["condicoes_pagamento"])}</p>' + _list(d.get('observacoes'))
    out += f'<p class="sub">Orçamento válido por {int(d["validade_dias"])} dias. Escreva por extenso: {_e(in_words(sub - disc))}.</p>'
    return out


def render_contract(d, ag, cl):
    c = d['cliente']
    rows, total = _total_rows(d['investimento'])
    out = ('<section class="parties"><h2>1. Das partes</h2>'
           f'<p><b>CONTRATADA:</b> {_e(ag["razao_social"])}, {_e(ag["documento"])}, representada por {_e(ag["representante"])}.</p>'
           f'<p><b>CONTRATANTE:</b> {_e(c["razao_social"])}, {_e(c["documento"])}, representada por {_e(c["representante"])}, '
           f'{_e(c["endereco"])}.</p></section>')
    out += '<h2>2. Do objeto</h2><ul>' + ''.join(
        f'<li><b>{_e(o["titulo"])}:</b> {_e(o.get("descricao", ""))}</li>' for o in d['objeto']) + '</ul>'
    out += ('<h2>3. Do valor e do pagamento</h2>' + _table(['Descrição', 'Valor'], rows, (1,)) +
            f'<p>Valor total: <b>{money(total)}</b> ({_e(in_words(total))}). {_e(d["forma_pagamento"])}</p>')
    out += (f'<h2>4. Do prazo e dos ajustes</h2><p>{_e(d["prazo_entrega"])} Estão incluídas '
            f'{int(d["rodadas_ajuste"])} rodada(s) de ajuste; mudanças de escopo são orçadas à parte.</p>')
    n = 5
    if d.get('recorrencia'):
        r = d['recorrencia']
        out += (f'<h2>{n}. Da recorrência</h2><p>{_e(r["descricao"])}: <b>{money(r["valor"])}</b> por {_e(r["periodicidade"])} '
                f'({_e(in_words(r["valor"]))}).</p>')
        n += 1
    for titulo, chave in (('Da propriedade intelectual', 'propriedade_intelectual'), ('Da confidencialidade', 'confidencialidade'),
                          ('Da rescisão', 'rescisao')):
        out += f'<h2>{n}. {titulo}</h2><p>{_e(d[chave])}</p>'
        n += 1
    for x in d.get('clausulas_extras', []):
        out += f'<h2>{n}. {_e(x["titulo"])}</h2><p>{_e(x["texto"])}</p>'
        n += 1
    out += f'<h2>{n}. Do foro</h2><p>Fica eleito o foro de {_e(d["foro"])} para dirimir dúvidas deste contrato.</p>'
    out += (f'<p>{_e(d["cidade"])}, {long_date(_iso(d))}.</p><div class="sign"><div>{_e(c["razao_social"])}<br>Contratante</div>'
            f'<div>{_e(ag["razao_social"])}<br>Contratada</div></div>')
    return out


def _iso(d) -> str:
    return _today() if d.get('data') in (None, '', 'hoje') else d['data']


RENDER = {'statement': render_statement, 'proposal': render_proposal, 'estimate': render_estimate,
          'contract': render_contract}


def render(client: str, kind: str, saida=SAIDA_PADRAO) -> tuple[str, int]:
    h = home(client, saida)
    d = _read(h / 'documentos' / f'{kind}.json', f'dados de {kind} (rode `vf doc new {client} {kind}`)')
    ag = _read(_agency_file(saida), 'saida/agency.json')
    cl = _read(h / 'marca.json', 'marca.json')
    if kind == 'presentation':
        from . import slides
        marks = _open_marks(d)
        return slides.render(d, cl, ag, h, bool(marks)), marks
    marks = _open_marks(d) + _open_marks(ag)
    logo = (cl.get('logo') or {}).get('arquivo')
    color = (cl.get('cores') or {}).get('destaque') or ag.get('cor', '#1f2937')
    body = RENDER[kind](d, ag, cl)
    page = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{_e(TYPES[kind])} {_e(cl["nome"])}</title>'
            f'<style>:root{{--cor:{color}}}{CSS}</style></head><body>{"<div class=draft>RASCUNHO</div>" if marks else ""}'
            f'<div class="wrap"><header><div><h1>{_e(TYPES[kind])}</h1><div class="sub">{_e(cl["nome"])} · '
            f'{long_date(_iso(d))}</div></div>{_img(h / logo) if logo else ""}</header>{body}'
            f'<footer>{_e(ag.get("razao_social") or ag.get("nome"))} · {_e(ag.get("email", ""))} · {_e(ag.get("telefone", ""))}'
            f'</footer></div></body></html>')
    return page, marks


def to_pdf(html_file: Path, pdf_file: Path):
    from ..panel.manual import find_browser
    tmp = pdf_file.with_suffix('.tmp.pdf')
    cmd = [find_browser(), '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--virtual-time-budget=4000',
           f'--print-to-pdf={tmp}', html_file.resolve().as_uri()]
    subprocess.run(cmd, capture_output=True, timeout=120)
    if not tmp.is_file():
        raise SystemExit('doc: o navegador não gerou o PDF')
    tmp.replace(pdf_file)


def build(client: str, kind: str, saida=SAIDA_PADRAO) -> dict:
    page, marks = render(client, kind, saida)
    folder = home(client, saida) / 'documentos'
    d = _read(folder / f'{kind}.json', kind)
    base = f'{kind}-{_iso(d)}' + ('-rascunho' if marks else '')
    htm, pdf = folder / f'{base}.html', folder / f'{base}.pdf'
    htm.write_text(page, encoding='utf-8')
    to_pdf(htm, pdf)
    return {'html': htm, 'pdf': pdf, 'open': marks}


def listing(client: str, saida=SAIDA_PADRAO) -> list:
    folder = home(client, saida) / 'documentos'
    return sorted(p.name for p in folder.iterdir() if p.suffix in ('.json', '.pdf')) if folder.is_dir() else []


def run(a):
    if a.acao == 'list':
        for n in listing(a.cliente, a.saida):
            print(' ', n)
        return
    if not a.tipo:
        raise SystemExit(f'doc {a.acao}: informe o tipo ({", ".join(TYPES)})')
    if a.acao == 'new':
        made = new(a.cliente, a.tipo, a.saida)
        print('criado:' if made else 'já existe, nada sobrescrito.')
        for m in made:
            print('  +', m)
        return
    r = build(a.cliente, a.tipo, a.saida)
    print(f'PDF: {r["pdf"]}\nHTML: {r["html"]}')
    if r['open']:
        print(f'ATENÇÃO: {r["open"]} {OPEN} nos dados. Gerado como RASCUNHO; resolva antes de enviar.')
