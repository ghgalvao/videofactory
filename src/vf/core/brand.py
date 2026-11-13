"""Brand extraction helpers.

  vf brand colors <image> [--k 6]    dominant colors of a print, site capture or logo (hex, share, role guess)

Measures instead of guessing: run it on the flyer, the cover of the presentation and the site capture, then write the
values into marca.json (cores, forma) and identidade/guia-visual.md. The result is a starting point, not a verdict:
a person confirms the final palette against the client's editable files.
"""
import cv2
import numpy as np


def _read(path: str):
    img = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise SystemExit(f'brand: não consegui ler {path}')
    return img


def dominant(path: str, k: int = 6) -> list:
    img = _read(path)
    scale = 240 / max(img.shape[:2])
    small = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    data = small.reshape(-1, 3).astype(np.float32)
    _, labels, centers = cv2.kmeans(data, k, None, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5), 3,
                                    cv2.KMEANS_PP_CENTERS)
    counts = np.bincount(labels.flatten(), minlength=k)
    out = []
    for c, n in sorted(zip(centers, counts), key=lambda x: -x[1]):
        b, g, r = (int(v) for v in c)
        hsv = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0][0]
        hue, sat, val = int(hsv[0]) * 2, int(hsv[1]) / 255, int(hsv[2]) / 255
        role = ('neutro escuro' if val < 0.22 else 'neutro claro' if sat < 0.12 and val > 0.8 else
                'cinza' if sat < 0.15 else 'cor de marca')
        out.append({'hex': f'#{r:02x}{g:02x}{b:02x}', 'share': round(100 * n / len(labels), 1), 'hue': hue,
                    'sat': round(sat, 2), 'val': round(val, 2), 'role': role})
    return out


def run(a):
    if a.acao == 'colors':
        for c in dominant(a.imagem, a.k):
            print(f'{c["hex"]}  {c["share"]:5.1f}%  matiz {c["hue"]:3}  sat {c["sat"]:.2f}  brilho {c["val"]:.2f}  {c["role"]}')
