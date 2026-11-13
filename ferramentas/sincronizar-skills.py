"""Espelha as skills de .claude/skills (fonte, Claude Code) em .agents/skills (Codex e outros agentes do padrão Agent Skills).

  uv run python ferramentas/sincronizar-skills.py           copia (apaga o espelho e recria)
  uv run python ferramentas/sincronizar-skills.py --checar  só confere; sai com erro se o espelho estiver desatualizado

Edite sempre em .claude/skills e rode este script. Cópia em vez de symlink: no Windows o git costuma
gravar symlink como arquivo de texto.
"""
import filecmp
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FONTE = RAIZ / '.claude' / 'skills'
ESPELHO = RAIZ / '.agents' / 'skills'


def diferencas(a: Path, b: Path) -> list[str]:
    if not b.is_dir():
        return [str(b.relative_to(RAIZ))]
    c = filecmp.dircmp(a, b)
    out = [str((a / n).relative_to(RAIZ)) for n in c.left_only + c.diff_files]
    out += [str((b / n).relative_to(RAIZ)) for n in c.right_only]
    for sub in c.common_dirs:
        out += diferencas(a / sub, b / sub)
    return out


if __name__ == '__main__':
    if '--checar' in sys.argv:
        d = diferencas(FONTE, ESPELHO)
        if d:
            print('skills desatualizadas em .agents/skills (rode ferramentas/sincronizar-skills.py):')
            print('\n'.join(f'  {x}' for x in d[:20]))
            sys.exit(1)
        print('skills sincronizadas')
        sys.exit(0)
    if ESPELHO.exists():
        shutil.rmtree(ESPELHO)
    shutil.copytree(FONTE, ESPELHO)
    print(f'{sum(1 for _ in ESPELHO.iterdir())} skills copiadas para {ESPELHO.relative_to(RAIZ)}')
