"""Client workspace standard: one folder per client with the same tabs as the agency hub.

  vf client new <slug> "<Name>"   creates the skeleton (nothing is overwritten)
  vf client check <slug>          reports what each tab still lacks, and every [CONFIRM] still open
  vf client list                  every client with its status

The folder lives in saida/clients/<slug>/ (outside git). The engine only versions this standard, never client data.

saida/clients/<slug>/
  LEIA-ANTES.md        rules of use, who decides, what is internal
  visao-geral.md       overview tab: business, contacts, commercial status, next steps
  brief.md             briefing tab
  marca.json           identity tab (model: docs/marca.exemplo.json)
  identidade/guia-visual.md   identity tab: shape language, typography, composition, do and don't
  social/plano.md      social tab: grid, highlights, key dates, pillars
  social/calendario.md social tab: month by month
  documentos/          documents tab: proposal, contract, invoices
  assets/{brand,images,video,print,docs}   materials tab, with assets/index.json (catalog)
  references/ research/ exports/
  <job>/               production tab: each job follows 1-entrada, 2-aprovar, 3-final, _interno
"""
import json
import re
from pathlib import Path

from .paths import ROOT, SAIDA_PADRAO

CLIENTS = 'clients'
OPEN = '[CONFIRMAR]'
ASSET_DIRS = ('brand', 'images', 'video', 'print', 'docs')

# tab label (same names as the hub) -> (folder or file, kind)
TABS = (
    ('Visão geral', 'visao-geral.md', 'file'),
    ('Briefing', 'brief.md', 'file'),
    ('Identidade', 'marca.json', 'file'),
    ('Social', 'social/plano.md', 'file'),
    ('Documentos', 'documentos', 'dir'),
    ('Materiais', 'assets', 'dir'),
)
EXTRA_FILES = ('LEIA-ANTES.md', 'identidade/guia-visual.md', 'social/calendario.md')
MARCA_KEYS = ('nome', 'cores', 'fontes', 'logo', 'tom', 'cta', 'contatos', 'proibidos', 'formatos', 'aprovador')
COLOR_KEYS = ('primaria', 'secundaria', 'destaque', 'fundo', 'texto')

TEMPLATES = {
    'LEIA-ANTES.md': """# {name}: regras de uso

**Uso interno.** Nada daqui sai para o cliente sem decisão de quem toca a conta.
- Quem decide e quem aprova: {OPEN}
- Escopo e preço de produção combinados por escrito antes de começar: {OPEN}
- Tudo marcado {OPEN} precisa de confirmação do cliente antes de publicar.
""",
    'visao-geral.md': """# {name}: visão geral

## Negócio
O que vende, para quem, onde atua. {OPEN}

## Contatos
| Pessoa | Papel | Canal | Decide? |
|---|---|---|---|
| {OPEN} | | | |

## Situação comercial
Escopo, valor, pago e pendente. {OPEN}

## Próximos passos
- [ ] {OPEN}
""",
    'brief.md': """# {name}: briefing

## Objetivo
## Público
## Tom de voz
## Plataformas e frequência
## Diferenciais reais (com prova)
## Números que podem ser públicos
## O que não pode ser dito
## Quem aprova e em quanto tempo
""",
    'identidade/guia-visual.md': """# {name}: guia visual

Como a marca se parece além das cores. Extraído do site, dos impressos e do logo (`/vf-brand`).

## Formas e composição
(ex.: cantos, inclinações, faixas, grades, uso de foto, margens)
## Tipografia
(títulos, apoio, caixa alta, pesos)
## Cor e fundo
(proporção, gradientes, onde entra o destaque)
## Fotografia
(estilo, tratamento, o que evitar)
## Faça e não faça
""",
    'social/plano.md': """# {name}: plano de conteúdo

## Perfil
## Pilares
## Grid inicial
### Post 1 -
## Destaques
## Datas prioritárias
## Frequência
""",
    'social/calendario.md': """# {name}: calendário

| Data | Peça | Pilar | Status |
|---|---|---|---|
""",
}


def home(slug: str, saida=SAIDA_PADRAO) -> Path:
    return Path(saida) / CLIENTS / slug


def _fill(text: str, name: str) -> str:
    return text.replace('{name}', name).replace('{OPEN}', OPEN)


def new(slug: str, name: str, saida=SAIDA_PADRAO) -> list:
    h = home(slug, saida)
    made = []
    for rel, tpl in TEMPLATES.items():
        f = h / rel
        if not f.exists():
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(_fill(tpl, name), encoding='utf-8')
            made.append(rel)
    marca = h / 'marca.json'
    if not marca.exists():
        model = json.loads((ROOT / 'docs' / 'marca.exemplo.json').read_text(encoding='utf-8'))
        model['nome'] = name
        model['descricao'] = OPEN
        marca.write_text(json.dumps(model, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        made.append('marca.json')
    for d in ('documentos', 'references', 'research', 'exports', *(f'assets/{x}' for x in ASSET_DIRS)):
        (h / d).mkdir(parents=True, exist_ok=True)
    return made


def _open_marks(h: Path) -> list:
    marks = []
    for f in sorted(h.rglob('*')):
        if f.suffix in ('.md', '.json') and f.is_file() and 'assets' not in f.relative_to(h).parts:
            n = f.read_text(encoding='utf-8', errors='replace').count(OPEN)
            if n:
                marks.append((f.relative_to(h).as_posix(), n))
    return marks


def _jobs(h: Path) -> list:
    return sorted(p.name for p in h.iterdir() if p.is_dir() and (p / '1-entrada').is_dir())


def check(slug: str, saida=SAIDA_PADRAO) -> dict:
    h = home(slug, saida)
    if not h.is_dir():
        raise SystemExit(f'client: {h} não existe. Crie com `vf client new {slug} "Nome"`.')
    tabs, problems = {}, []
    for label, rel, kind in TABS:
        p = h / rel
        if kind == 'file':
            ok = p.is_file() and p.stat().st_size > 0
            thin = ok and p.suffix == '.md' and len(re.sub(r'#.*|\s', '', p.read_text(encoding='utf-8'))) < 120
        else:
            ok = p.is_dir() and any(x.is_file() for x in p.rglob('*'))
            thin = False
        tabs[label] = 'ok' if ok and not thin else ('vazia' if not ok else 'rascunho')
    for rel in EXTRA_FILES:
        if not (h / rel).is_file():
            problems.append(f'falta {rel}')
    marca = h / 'marca.json'
    if marca.is_file():
        m = json.loads(marca.read_text(encoding='utf-8'))
        problems += [f'marca.json sem "{k}"' for k in MARCA_KEYS if k not in m]
        problems += [f'marca.json cores sem "{k}"' for k in COLOR_KEYS if k not in m.get('cores', {})]
        logo = (m.get('logo') or {}).get('arquivo')
        if logo and not (h / logo).is_file():
            problems.append(f'logo não encontrada: {logo}')
    if not (h / 'assets' / 'index.json').is_file():
        problems.append('falta assets/index.json (catálogo de imagens: /vf-assets)')
    return {'tabs': tabs, 'problems': problems, 'open': _open_marks(h), 'jobs': _jobs(h)}


def listing(saida=SAIDA_PADRAO) -> list:
    base = Path(saida) / CLIENTS
    return sorted(p.name for p in base.iterdir() if (p / 'marca.json').is_file()) if base.is_dir() else []


def run(a):
    if a.acao == 'list':
        for s in listing(a.saida):
            r = check(s, a.saida)
            falta = [t for t, v in r['tabs'].items() if v != 'ok']
            print(f'{s:24} {len(r["jobs"])} jobs · abas incompletas: {", ".join(falta) or "nenhuma"}')
        return
    if a.acao == 'new':
        if not a.nome:
            raise SystemExit('client new: informe o nome. Ex.: vf client new acme "Acme Ltda"')
        made = new(a.slug, a.nome, a.saida)
        print(f'cliente {a.slug}: {len(made)} arquivos criados' if made else f'cliente {a.slug}: já tem o esqueleto completo')
        for m in made:
            print('  +', m)
        return
    r = check(a.slug, a.saida)
    print(f'Cliente {a.slug}')
    for label, status in r['tabs'].items():
        print(f'  {label:12} {status}')
    print(f'  Produção     {len(r["jobs"])} jobs' + (f' ({", ".join(r["jobs"])})' if r['jobs'] else ''))
    for p in r['problems']:
        print('  !', p)
    if r['open']:
        print(f'  {OPEN} em aberto: ' + ', '.join(f'{f} ({n})' for f, n in r['open']))


def _read_text(p: Path) -> str:
    return p.read_text(encoding='utf-8') if p.is_file() else ''


def view(h: Path) -> dict:
    """Everything the panel shows for one client folder (same tabs as `check`)."""
    from .docs import TYPES
    docs = {}
    for kind in TYPES:
        files = sorted((h / 'documentos').glob(f'{kind}-*.pdf'), key=lambda f: f.stat().st_mtime, reverse=True)
        docs[kind] = {'label': TYPES[kind], 'data': (h / 'documentos' / f'{kind}.json').is_file(),
                      'pdfs': [{'name': f.name, 'path': f.relative_to(h).as_posix(), 'size': f.stat().st_size,
                                'mtime': f.stat().st_mtime, 'draft': f.stem.endswith('-rascunho')} for f in files[:5]]}
    other = [{'name': f.name, 'path': f.relative_to(h).as_posix(), 'size': f.stat().st_size, 'mtime': f.stat().st_mtime}
             for f in sorted((h / 'documentos').glob('*')) if f.suffix == '.pdf' and not any(f.name.startswith(k + '-') for k in TYPES)]
    idx = h / 'assets' / 'index.json'
    catalog = []
    if idx.is_file():
        for i in json.loads(idx.read_text(encoding='utf-8')).get('items', []):
            catalog.append({k: i.get(k) for k in ('id', 'path', 'kind', 'area', 'w', 'h', 'dur', 'orient', 'quality', 'subject', 'tags', 'use',
                                                  'people', 'rights', 'note', 'duplicate_of', 'blank')})
    marca = json.loads(_read_text(h / 'marca.json') or '{}')
    packs = []
    for g in sorted((h / 'exports').glob('*/grade.png')) if (h / 'exports').is_dir() else []:
        n = g.parent.name
        packs.append({'name': n, 'grade': g.relative_to(h).as_posix(),
                      'zip': f'exports/{n}.zip' if (h / 'exports' / f'{n}.zip').is_file() else '',
                      'resumo': f'exports/{n}/resumo.md' if (h / 'exports' / n / 'resumo.md').is_file() else ''})
    return {'slug': h.name, 'packs': packs, 'catalog': catalog, 'check': check(h.name, h.parent.parent), 'marca': marca,
            'overview': _read_text(h / 'visao-geral.md'), 'guide': _read_text(h / 'identidade' / 'guia-visual.md'),
            'plan': _read_text(h / 'social' / 'plano.md'), 'calendar': _read_text(h / 'social' / 'calendario.md'),
            'warning': _read_text(h / 'LEIA-ANTES.md'), 'docs': docs, 'other_pdfs': other}
