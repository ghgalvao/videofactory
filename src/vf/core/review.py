"""Text review of a client's jobs before anything goes out: spelling, blocked claims, open placeholders, caption limits.

  vf review <client> <job> [<job> ...]     reviews jobs (names relative to the client folder)
  vf review <client> --all                 reviews every job that has a carrossel.json

Reads 1-entrada/carrossel.json (every slide text), legenda.txt and notas.md. Writes 2-aprovar/revisao.md.
Rules come from the client's marca.json (all optional lists):
  bloqueados   regex that must never appear (claims or names the client has not authorised)  -> ERROR
  atencao      regex that needs the client's confirmation before publishing                    -> WARNING
  vocabulario  words the spell checker should accept (trade terms, place names)
Always checked: [CONFIRMAR] left in art or caption, caption length (2200) and hashtags (30), long art texts, spelling.
A clean review is not an approval: someone still looks at the PNGs and signs off.
"""
import json
import re
from pathlib import Path

from .client import OPEN, home
from .paths import SAIDA_PADRAO

# o dicionário embutido é de português europeu: aceita aqui o que é correto no Brasil e vocabulário de rede social
BR_EXTRA = {'conosco', 'galpão', 'galpões', 'bio', 'link', 'stories', 'feed', 'reels', 'online', 'whatsapp', 'instagram',
            'orçamentos', 'equipamentos', 'sustentabilidade', 'contato', 'contatos', 'epis', 'epi', 'nrs',
            'regulamentadoras', 'regulamentadora', 'regulamentadores'}
MAX_CAPTION, MAX_HASHTAGS, MAX_TITLE, MAX_TEXT = 2200, 30, 64, 130
WORD = re.compile(r"[A-Za-zÀ-ÿ]{3,}")


def _texts(cfg: dict) -> list:
    out = []
    for i, s in enumerate(cfg.get('slides', []), 1):
        for k in ('rotulo', 'titulo', 'texto', 'numero', 'cta'):
            if s.get(k):
                out.append((f'slide {i} {k}', str(s[k])))
        for n, it in enumerate(s.get('itens', []), 1):
            out.append((f'slide {i} item {n}', it))
        for n, ch in enumerate(s.get('chips', []), 1):
            out.append((f'slide {i} chip {n}', ch))
    return out


def _vocab(marca: dict, client_dir: Path) -> set:
    words = {w.lower() for w in re.findall(WORD, ' '.join(marca.get('vocabulario', []) + [marca.get('nome', '')]))}
    idx = client_dir / 'assets' / 'index.json'
    if idx.is_file():
        for it in json.loads(idx.read_text(encoding='utf-8'))['items']:
            for t in it.get('tags', []):
                words |= {w.lower() for w in re.findall(WORD, t)}
    return words


def review_job(client: str, job: str, saida=SAIDA_PADRAO) -> dict:
    from spellchecker import SpellChecker
    h = home(client, saida)
    jd = h / job
    cfg_f = jd / '1-entrada' / 'carrossel.json'
    if not cfg_f.is_file():
        raise SystemExit(f'review: {cfg_f} não existe')
    cfg = json.loads(cfg_f.read_text(encoding='utf-8'))
    marca = json.loads((h / 'marca.json').read_text(encoding='utf-8'))
    cap_f, notes_f = jd / '1-entrada' / 'legenda.txt', jd / '1-entrada' / 'notas.md'
    caption = cap_f.read_text(encoding='utf-8') if cap_f.is_file() else ''
    notes = notes_f.read_text(encoding='utf-8') if notes_f.is_file() else ''
    parts = _texts(cfg) + ([('legenda', caption)] if caption else [])
    errors, warns = [], []
    for where, text in parts:
        if OPEN in text:
            errors.append(f'{where}: {OPEN} dentro do texto que vai ao público')
        for rx in marca.get('bloqueados', []):
            m = re.search(rx, text, re.I)
            if m:
                errors.append(f'{where}: "{m.group(0)}" é bloqueado no marca.json')
        for rx in marca.get('atencao', []):
            m = re.search(rx, text, re.I)
            if m:
                warns.append(f'{where}: "{m.group(0)}" precisa de confirmação do cliente')
    for where, text in _texts(cfg):
        limit = MAX_TITLE if where.endswith('titulo') else MAX_TEXT if where.endswith('texto') else None
        if limit and len(text) > limit:
            warns.append(f'{where}: {len(text)} caracteres (acima de {limit}); confira se cabe na arte')
    if caption:
        if len(caption) > MAX_CAPTION:
            errors.append(f'legenda: {len(caption)} caracteres (máximo {MAX_CAPTION})')
        tags = re.findall(r'#\w+', caption)
        if len(tags) > MAX_HASHTAGS:
            errors.append(f'legenda: {len(tags)} hashtags (máximo {MAX_HASHTAGS})')
        if not re.search(r'link na bio|orçamento|fale|contato|solicite', caption, re.I):
            warns.append('legenda: sem chamada para ação')
    else:
        warns.append('legenda.txt ausente')
    sp = SpellChecker(language='pt')
    known = _vocab(marca, h) | BR_EXTRA
    seen = set()
    for where, text in parts:
        clean = re.sub(r'#\w+|https?://\S+', ' ', text)
        for w in re.findall(WORD, clean):
            lw = w.lower()
            if lw in known or lw in seen or lw not in sp.unknown([lw]):
                continue
            seen.add(lw)
            sug = sp.correction(lw)
            warns.append(f'ortografia: "{w}" ({where})' + (f'; sugestão: {sug}' if sug and sug != lw else ''))
    pending = [l.strip('- ').strip() for l in notes.splitlines() if re.search(r'\[CONFIRMAR\]|PENDENTE|BLOQUEADO', l)]
    return {'job': job, 'errors': errors, 'warnings': warns, 'pending': pending}


def write_report(client: str, r: dict, saida=SAIDA_PADRAO) -> Path:
    out = home(client, saida) / r['job'] / '2-aprovar' / 'revisao.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [f'# Revisão: {r["job"]}', '', f'Resultado: **{"REPROVADO" if r["errors"] else "sem erros"}** · '
             f'{len(r["errors"])} erros · {len(r["warnings"])} avisos · {len(r["pending"])} pendências', '']
    for title, items in (('Erros (corrigir antes de publicar)', r['errors']), ('Avisos', r['warnings']),
                         ('Pendências com o cliente (notas.md)', r['pending'])):
        lines += [f'## {title}'] + ([f'- {i}' for i in items] or ['- nenhum']) + ['']
    lines.append('Revisão automática não substitui o olhar humano nas imagens.')
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return out


def run(a):
    h = home(a.cliente, a.saida)
    jobs = a.jobs or ([p.parent.parent.name for p in sorted(h.glob('*/1-entrada/carrossel.json'))] if a.todos else [])
    if not jobs:
        raise SystemExit('review: nenhum job com carrossel.json encontrado' if a.todos else 'review: informe jobs ou use --all')
    bad = 0
    for j in jobs:
        r = review_job(a.cliente, j, a.saida)
        write_report(a.cliente, r, a.saida)
        bad += bool(r['errors'])
        print(f'{j:28} erros {len(r["errors"]):2}  avisos {len(r["warnings"]):2}  pendências {len(r["pending"]):2}')
        for e in r['errors']:
            print('   ERRO ', e)
    print(f'\n{len(jobs) - bad}/{len(jobs)} sem erros. Relatórios em <job>/2-aprovar/revisao.md')
