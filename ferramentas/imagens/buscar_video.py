"""Busca VÍDEOS de licença livre (Wikimedia Commons, Internet Archive e, com chave, Pexels) e baixa com crédito.

Sem chave: Commons + Internet Archive. Pexels só liga se existir PEXELS_API_KEY (variável de ambiente ou
videoFactory/.env; chave grátis em pexels.com/api; NUNCA cole a chave no chat). Só biblioteca padrão.

  python buscar_video.py buscar "stock market" [--licencas cc0,pdm] [--n 10] [--max-seg 60] [--out PASTA]
  python buscar_video.py baixar PASTA/candidatos.json 2 [--para 1-entrada/videos] [--nome fundo]

Licenças: cc0, pdm (domínio público) por padrão; by, by-sa exigem crédito. Pexels usa licença própria
("pexels": uso livre sem crédito obrigatório, mas não revender o clipe sem alteração nem sugerir endosso de
pessoas/marcas): só entra com `--licencas ...,pexels`. Nunca nc/nd.
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from buscar import PERMITIDAS, UA, _get, _limpa  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
EXT_VIDEO = ('.mp4', '.webm', '.ogv', '.mov')


def _chave(nome: str) -> str:
    if os.environ.get(nome):
        return os.environ[nome]
    env = RAIZ / '.env'
    if env.exists():
        for linha in env.read_text(encoding='utf-8').splitlines():
            if linha.strip().startswith(nome + '='):
                return linha.split('=', 1)[1].strip().strip('"\'')
    return ''


def commons(q: str, licencas: list, n: int) -> list:
    p = {'action': 'query', 'format': 'json', 'generator': 'search', 'gsrsearch': f'{q} filetype:video',
         'gsrnamespace': 6, 'gsrlimit': min(n * 2, 30), 'prop': 'imageinfo',
         'iiprop': 'url|size|mime|extmetadata', 'iiurlwidth': 400}
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
                    'largura': ii.get('width'), 'altura': ii.get('height'), 'duracao': ii.get('duration')})
    return out


def archive(q: str, licencas: list, n: int) -> list:
    clausulas = []  # uma consulta por grupo de licença: o OR com curinga composto devolve vazio no Archive
    if 'cc0' in licencas or 'pdm' in licencas:
        clausulas.append('licenseurl:*publicdomain*')
    if 'by' in licencas:
        clausulas.append('licenseurl:*licenses/by/*')
    if 'by-sa' in licencas:
        clausulas.append('licenseurl:*licenses/by-sa/*')
    out = []
    for cl in clausulas:
        p = [('q', f'({q}) AND mediatype:movies AND {cl}'), ('fl[]', 'identifier'), ('fl[]', 'title'),
             ('fl[]', 'creator'), ('fl[]', 'licenseurl'), ('rows', min(n, 15)), ('output', 'json')]
        d = _get('https://archive.org/advancedsearch.php?' + urllib.parse.urlencode(p))
        for r in d.get('response', {}).get('docs', []):
            url_lic = r.get('licenseurl') or ''
            lic = ('by-sa' if '/by-sa/' in url_lic else 'by' if '/by/' in url_lic else
                   'cc0' if 'zero' in url_lic else 'pdm')
            if lic not in licencas and not (lic in ('cc0', 'pdm') and ({'cc0', 'pdm'} & set(licencas))):
                continue
            ident = r['identifier']
            autor = r.get('creator')
            out.append({'fonte': 'archive.org', 'titulo': r.get('title') or ident,
                        'autor': ', '.join(autor) if isinstance(autor, list) else (autor or ''), 'licenca': lic,
                        'versao': '', 'pagina': f'https://archive.org/details/{ident}', 'url': '',
                        'identificador': ident, 'miniatura': f'https://archive.org/services/img/{ident}',
                        'largura': None, 'altura': None, 'duracao': None})
    return out


def pexels(q: str, n: int, orientacao: str | None) -> list:
    chave = _chave('PEXELS_API_KEY')
    if not chave:
        return []
    p = {'query': q, 'per_page': min(n, 15)}
    if orientacao:
        p['orientation'] = {'tall': 'portrait', 'wide': 'landscape', 'square': 'square'}[orientacao]
    req = urllib.request.Request('https://api.pexels.com/videos/search?' + urllib.parse.urlencode(p),
                                 headers={'Authorization': chave, 'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode('utf-8'))
    out = []
    for v in d.get('videos', []):
        arquivos = [f for f in v.get('video_files', []) if f.get('file_type') == 'video/mp4' and f.get('width')]
        if not arquivos:
            continue
        melhor = max((f for f in arquivos if f['width'] <= 1920), key=lambda f: f['width'], default=arquivos[0])
        out.append({'fonte': 'pexels', 'titulo': f'Pexels {v["id"]}', 'autor': (v.get('user') or {}).get('name', ''),
                    'licenca': 'pexels', 'versao': '', 'pagina': v.get('url', ''), 'url': melhor['link'],
                    'miniatura': v.get('image', ''), 'largura': melhor['width'], 'altura': melhor.get('height'),
                    'duracao': v.get('duration')})
    return out


def _resolver_archive(c: dict) -> str:
    """Escolhe o arquivo de vídeo leve do item (derivado h.264 antes do original)."""
    meta = _get(f'https://archive.org/metadata/{c["identificador"]}')
    arqs = [f for f in meta.get('files', []) if f.get('name', '').lower().endswith(EXT_VIDEO)]
    if not arqs:
        sys.exit('item do Internet Archive sem arquivo de vídeo baixável')
    pref = [f for f in arqs if 'h.264' in (f.get('format') or '').lower() or f['name'].lower().endswith('.mp4')]
    escolha = min(pref or arqs, key=lambda f: int(f.get('size') or 10**12))
    return f'https://archive.org/download/{c["identificador"]}/{urllib.parse.quote(escolha["name"])}'


def buscar(a):
    licencas = [x.strip().lower() for x in a.licencas.split(',')]
    ruins = [x for x in licencas if x not in PERMITIDAS | {'pexels'}]
    if ruins:
        sys.exit(f'licença não permitida: {ruins}. Use {sorted(PERMITIDAS | {"pexels"})} (nunca nc/nd).')
    achados = []
    fontes = [('commons', lambda: commons(a.consulta, licencas, a.n)),
              ('archive.org', lambda: archive(a.consulta, licencas, a.n))]
    if 'pexels' in licencas:
        if _chave('PEXELS_API_KEY'):
            fontes.append(('pexels', lambda: pexels(a.consulta, a.n, a.orientacao)))
        else:
            print('  aviso: Pexels pedido mas falta PEXELS_API_KEY (variável de ambiente ou videoFactory/.env)', file=sys.stderr)
    for nome, f in fontes:
        try:
            achados += f()
        except Exception as e:
            print(f'  aviso: {nome} falhou ({e})', file=sys.stderr)
    achados = [c for c in achados if not c.get('duracao') or c['duracao'] <= a.max_seg]
    achados = achados[:a.n]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(achados, 1):
        c['n'] = i
        if c['miniatura']:
            try:
                arq = out / f'cand-{i:02d}.jpg'
                arq.write_bytes(_get(c['miniatura'], binario=True)); c['arquivo_miniatura'] = str(arq)
            except Exception:
                pass
        dur = f'{c["duracao"]:.0f}s' if c.get('duracao') else '?s'
        res = f'{c["largura"]}x{c["altura"]}' if c.get('largura') else 'res ?'
        print(f'{i:2}. [{c["licenca"].upper()}] {c["titulo"][:55]!r} · {c["autor"][:25]} · {dur} · {res} · {c["fonte"]}')
    (out / 'candidatos.json').write_text(json.dumps(achados, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\n{len(achados)} candidatos em {out}. Olhe cand-NN.jpg (poster) e rode: baixar {out / "candidatos.json"} <n>')


def baixar(a):
    cands = json.loads(Path(a.candidatos).read_text(encoding='utf-8'))
    c = next((x for x in cands if x['n'] == a.n), None)
    if not c:
        sys.exit(f'candidato {a.n} não existe')
    url = c['url'] or _resolver_archive(c)
    ext = Path(urllib.parse.urlparse(url).path).suffix.lower() or '.mp4'
    nome = (a.nome or re.sub(r'[^a-z0-9]+', '-', c['titulo'].lower()).strip('-')[:40] or f'video{a.n}') + ext
    pasta = Path(a.para); pasta.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r, (pasta / nome).open('wb') as f:
        while bloco := r.read(1 << 20):
            f.write(bloco)
    lic = c['licenca'].upper() + (f' {c["versao"]}' if c['versao'] else '')
    exige = c['licenca'] in ('by', 'by-sa')
    linha = (f'- `{nome}` — "{c["titulo"]}" de {c["autor"] or "autor desconhecido"} · {lic} · {c["pagina"]}'
             f'{" · **CRÉDITO OBRIGATÓRIO NA LEGENDA**" if exige else ""}\n')
    with (pasta / 'CREDITOS.md').open('a', encoding='utf-8') as f:
        f.write(linha)
    print(f'baixado: {pasta / nome} ({(pasta / nome).stat().st_size / 1e6:.1f} MB)\ncrédito: {linha.strip()}')
    if exige:
        print('ATENÇÃO: esta licença exige crédito no post; copie a linha acima para a legenda.')
    if c['licenca'] == 'pexels':
        print('Pexels: não revender o clipe sem alteração; sem sugerir endosso de pessoas ou marcas que aparecem.')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('buscar'); b.add_argument('consulta')
    b.add_argument('--licencas', default='cc0,pdm'); b.add_argument('--n', type=int, default=10)
    b.add_argument('--orientacao', choices=['tall', 'wide', 'square'])
    b.add_argument('--max-seg', type=int, default=120, help='descarta clipes mais longos que isto')
    b.add_argument('--out', default='_busca_videos')
    d = sub.add_parser('baixar'); d.add_argument('candidatos'); d.add_argument('n', type=int)
    d.add_argument('--para', default='1-entrada/videos'); d.add_argument('--nome')
    a = p.parse_args()
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, 'reconfigure'):
            s.reconfigure(encoding='utf-8', errors='replace')
    buscar(a) if a.cmd == 'buscar' else baixar(a)


if __name__ == '__main__':
    main()
