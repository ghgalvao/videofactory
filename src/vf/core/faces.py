"""Câmera virtual 9:16: posição X do corte seguindo rosto (YuNet), com fallback por movimento."""
import json
import shutil
import tempfile
from pathlib import Path

import cv2
import numpy as np

from .media import abrir
from .paths import MODELS

YUNET = MODELS / 'yunet.onnx'
YUNET_URL = 'https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx'


def rastrear(video: Path, pasta: Path, t0, t1, ignorar_canto) -> list:
    """Lista de X (pixels) do canto esquerdo do recorte, um por quadro. Cache em pasta/cropx.json."""
    js = pasta / 'cropx.json'
    if js.exists():
        return json.loads(js.read_text())
    print('  rastreando rostos...')
    if not YUNET.exists():
        import urllib.request
        YUNET.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(YUNET_URL, YUNET)
    cap = abrir(video); fps = cap.get(cv2.CAP_PROP_FPS)
    W, H = int(cap.get(3)), int(cap.get(4)); CW = H * 9 / 16; HALF = CW / 2
    cap.set(cv2.CAP_PROP_POS_MSEC, t0 * 1000)
    # o leitor ONNX do OpenCV não abre caminho com acento ("Produção"): usa cópia no temp
    modelo = Path(tempfile.gettempdir()) / 'yunet_vf.onnx'
    if not modelo.exists():
        shutil.copy(YUNET, modelo)
    fd = cv2.FaceDetectorYN.create(str(modelo), '', (W, H), 0.6, 0.3, 5000)
    # 2ª tentativa pra plano aberto (rosto pequeno): imagem 2x e limiar menor
    fd2 = cv2.FaceDetectorYN.create(str(modelo), '', (W * 2, H * 2), 0.5, 0.3, 5000)
    n = int(round((t1 - t0) * fps))
    alvo, cortes, prev, cur, rival_n = [None] * n, [0], None, None, 0
    # movimento por coluna (média móvel), pra plano aberto: quem fala gesticula, mediador
    # e plateia ficam parados. Ignora faixa de cima/baixo (placar e cronômetro mudam).
    SW, SH = 320, 180; box = max(3, int(SW * 9 / 16 * H / W / 2))
    prevg, mov = None, np.zeros(SW)
    for i in range(n):
        ok, img = cap.read()
        if not ok:
            n = i; alvo = alvo[:n]; break
        small = cv2.resize(img, (SW, SH))
        hsv = cv2.cvtColor(cv2.resize(small, (160, 90)), cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [16, 8], [0, 180, 0, 256]); cv2.normalize(hist, hist)
        corte = prev is not None and cv2.compareHist(prev, hist, cv2.HISTCMP_BHATTACHARYYA) > 0.35
        prev = hist
        g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.int16)
        if corte:
            cortes.append(i); cur = None; mov[:] = 0
        elif prevg is not None:
            d = np.abs(g - prevg)[int(SH * 0.12):int(SH * 0.78)]
            if ignorar_canto:
                d[int(d.shape[0] * 0.55):, int(SW * 0.80):] = 0
            mov = 0.9 * mov + 0.1 * (d > 18).sum(0)
        prevg = g
        if i % 2 and not corte:
            continue
        _, f = fd.detect(img); esc = 1
        if f is None:
            _, f = fd2.detect(cv2.resize(img, (W * 2, H * 2))); esc = 2
        faces = [(float((x + w / 2) / esc), float(w / esc)) for x, y, w, h in (f[:, :4] if f is not None else [])
                 if not (ignorar_canto and x / esc > 0.80 * W and y / esc > 0.55 * H)]
        if not faces or max(q[1] for q in faces) < 0.035 * W:
            # plano aberto: rosto ausente ou minúsculo → enquadra a região com mais movimento
            if mov.sum() > 0:
                alvo[i] = float((np.argmax(np.convolve(mov, np.ones(box), mode='same')) + 0.5) * W / SW)
            cur = None
            continue
        faces = [q for q in faces if q[1] >= 0.035 * W]
        maior = max(faces, key=lambda q: q[1])
        if cur is None:
            cur = maior
        else:
            # fica no mesmo rosto (o mais perto do anterior); só troca se outro for bem
            # maior por ~0,5s seguidos — evita a câmera pular entre pessoas
            mesmo = min(faces, key=lambda q: abs(q[0] - cur[0]))
            if abs(mesmo[0] - cur[0]) < mesmo[1] * 1.5:
                cur = mesmo
            if maior[1] > cur[1] * 1.4 and abs(maior[0] - cur[0]) > maior[1]:
                rival_n += 1
                if rival_n >= 8:
                    cur, rival_n = maior, 0
            else:
                rival_n = 0
        alvo[i] = cur[0]
    cortes.append(n)
    xs = np.zeros(n)
    # plano sem rosto (aberto, gente pequena demais): mantém a última posição conhecida em vez
    # de centralizar — o centro costuma ser palco vazio
    conhecidos = [v for v in alvo if v is not None]
    ultimo = conhecidos[0] if conhecidos else W / 2
    for a, b in zip(cortes, cortes[1:]):
        if b <= a:
            continue
        s = np.array([np.nan if v is None else v for v in alvo[a:b]], float)
        idx = np.arange(len(s)); ok = ~np.isnan(s)
        s = np.interp(idx, idx[ok], s[ok]) if ok.any() else np.full(len(s), ultimo)
        ultimo = s[-1]
        sig = 10; k = np.arange(-3 * sig, 3 * sig + 1); g = np.exp(-k ** 2 / (2 * sig ** 2)); g /= g.sum()
        xs[a:b] = np.clip(np.convolve(np.pad(s, 3 * sig, mode='edge'), g, mode='valid'), HALF, W - HALF)
    res = [float(x - HALF) for x in xs]
    js.write_text(json.dumps(res))
    return res
