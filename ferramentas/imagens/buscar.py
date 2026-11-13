"""Busca imagens de licença livre (Openverse + Wikimedia Commons) e baixa com o crédito registrado.

Sem chave de API, só biblioteca padrão. Só a consulta (palavras do tema) sai da máquina.

  python buscar.py buscar "bitcoin coin" [--licencas cc0,pdm] [--n 12] [--orientacao tall|wide|square]
      -> lista candidatos numerados e grava candidatos.json + miniaturas em --out
  python buscar.py baixar candidatos.json 3 [--para 1-entrada/imagens] [--nome capa]
      -> baixa a imagem nº 3 (maior resolução disponível) e acrescenta a linha em CREDITOS.md

Licenças aceitas por padrão: cc0, pdm (domínio público). `--licencas cc0,pdm,by,by-sa` libera as que exigem
crédito (o crédito vai para CREDITOS.md e DEVE aparecer na legenda do post). Nunca `nc` nem `nd`.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

UA = 'videoFactory-imagens/1.0 (busca de imagens livres)'
PERMITIDAS = {'cc0', 'pdm', 'by', 'by-sa'}  # nunca nc / nd


def _get(url: str, binario: bool = False):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        dados = r.read()
    return dados if binario else json.loads(dados.decode('utf-8'))


def openverse(q: str, licencas: list, n: int, orientacao: str | None) -> list:
    p = {'q': q, 'license': ','.join(licencas), 'page_size': min(n, 20), 'mature': 'false'}
    if orientacao:
        p['aspect_ratio'] = orientacao
    d = _get('https://api.openverse.org/v1/images/?' + urllib.parse.urlencode(p))
    out = []
    for r in d.get('results', []):
        out.append({'fonte': 'openverse', 'titulo': r.get('title') or '', 'autor': r.get('creator') or '',
                    'licenca': (r.get('license') or '').lower(), 'versao': r.get('license_version') or '',
                    'pagina': r.get('foreign_landing_url') or '', 'url': r.get('url') or '',
                    'miniatura': r.get('thumbnail') or '', 'largura': r.get('width'), 'altura': r.get('height'),
                    'origem': r.get('source') or ''})
    return out


def _limpa(html: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html or '')).strip()


def commons(q: str, licencas: list, n: int) -> list:
    p = {'action': 'query', 'format': 'json', 'generator': 'search', 'gsrsearch': f'{q} filetype:bitmap',
         'gsrnamespace': 6, 'gsrlimit': min(n, 20), 'prop': 'imageinfo',
         'iiprop': 'url|size|extmetadata', 'iiurlwidth': 400}
    d = _get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(p))
    out = []
    for pg in (d.get('query', {}).get('pages', {}) or {}).values():
        ii = (pg.get('imageinfo') or [{}])[0]
        m = ii.get('extmetadata', {})
        nome = (m.get('LicenseShortName', {}).get('value') or '').lower()
        lic = ('cc0' if 'cc0' in nome else 'pdm' if 'public domain' in nome or nome == 'pd' else
               'by-sa' if 'by-sa' in nome else 'by' if nome.startswith('cc by') else '')
        if lic not in licencas or not ii.get('url'):
            continue
        out.append({'fonte': 'commons', 'titulo': _limpa(m.get('ObjectName', {}).get('value')) or pg.get('title', ''),
                    'autor': _limpa(m.get('Artist', {}).get('value')), 'licenca': lic, 'versao': '',
                    'pagina': ii.get('descriptionurl', ''), 'url': ii['url'], 'miniatura': ii.get('thumburl', ''),
                    'largura': ii.get('width'), 'altura': ii.get('height'), 'origem': 'wikimedia commons'})
    return out


def buscar(a):
    licencas = [x.strip().lower() for x in a.licencas.split(',')]
    ruins = [x for x in licencas if x not in PERMITIDAS]
    if ruins:
        sys.exit(f'licença não permitida: {ruins}. Use {sorted(PERMITIDAS)} (nunca nc/nd).')
    achados = []
    for nome, f in (('openverse', lambda: openverse(a.consulta, licencas, a.n, a.orientacao)),
                    ('commons', lambda: commons(a.consulta, licencas, a.n))):
        try:
            achados += f()
        except Exception as e:  # uma fonte fora do ar não derruba a outra
            print(f'  aviso: {nome} falhou ({e})', file=sys.stderr)
    vistos, unicos = set(), []
    for c in achados:
        if c['url'] and c['url'] not in vistos and (c['largura'] or 0) >= a.min_largura:
            vistos.add(c['url']); unicos.append(c)
    unicos = unicos[:a.n]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(unicos, 1):
        c['n'] = i
        if c['miniatura']:
            try:
                arq = out / f'cand-{i:02d}.jpg'
                arq.write_bytes(_get(c['miniatura'], binario=True)); c['arquivo_miniatura'] = str(arq)
            except Exception:
                pass
        print(f'{i:2}. [{c["licenca"].upper()}] {c["titulo"][:60]!r} · {c["autor"][:30]} · {c["largura"]}x{c["altura"]} · {c["fonte"]}')
    (out / 'candidatos.json').write_text(json.dumps(unicos, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\n{len(unicos)} candidatos em {out}. Olhe as miniaturas (cand-NN.jpg) e rode: baixar {out / "candidatos.json"} <n>')


def baixar(a):
    cands = json.loads(Path(a.candidatos).read_text(encoding='utf-8'))
    c = next((x for x in cands if x['n'] == a.n), None)
    if not c:
        sys.exit(f'candidato {a.n} não existe')
    ext = Path(urllib.parse.urlparse(c['url']).path).suffix.lower() or '.jpg'
    nome = (a.nome or re.sub(r'[^a-z0-9]+', '-', c['titulo'].lower()).strip('-')[:40] or f'img{a.n}') + ext
    pasta = Path(a.para); pasta.mkdir(parents=True, exist_ok=True)
    (pasta / nome).write_bytes(_get(c['url'], binario=True))
    cred = pasta / 'CREDITOS.md'
    lic = c['licenca'].upper() + (f' {c["versao"]}' if c['versao'] else '')
    exige = c['licenca'] in ('by', 'by-sa')
    linha = (f'- `{nome}` — "{c["titulo"]}" de {c["autor"] or "autor desconhecido"} · {lic} · {c["pagina"]}'
             f'{" · **CRÉDITO OBRIGATÓRIO NA LEGENDA**" if exige else ""}\n')
    with cred.open('a', encoding='utf-8') as f:
        f.write(linha)
    print(f'baixada: {pasta / nome}\ncrédito: {linha.strip()}')
    if exige:
        print('ATENÇÃO: esta licença exige crédito no post; copie a linha acima para a legenda.')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('buscar'); b.add_argument('consulta')
    b.add_argument('--licencas', default='cc0,pdm'); b.add_argument('--n', type=int, default=12)
    b.add_argument('--orientacao', choices=['tall', 'wide', 'square'])
    b.add_argument('--min-largura', type=int, default=1000)
    b.add_argument('--out', default='_busca_imagens')
    d = sub.add_parser('baixar'); d.add_argument('candidatos'); d.add_argument('n', type=int)
    d.add_argument('--para', default='1-entrada/imagens'); d.add_argument('--nome')
    a = p.parse_args()
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, 'reconfigure'):
            s.reconfigure(encoding='utf-8', errors='replace')
    buscar(a) if a.cmd == 'buscar' else baixar(a)


if __name__ == '__main__':
    main()
