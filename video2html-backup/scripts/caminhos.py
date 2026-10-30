# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "scipy", "scikit-image", "pillow"]
# ///
"""Extrai caminhos (polilinhas) sobre os traços de uma camada: do centro até cada ponta e até alvos dados.

    uv run caminhos.py <mascara.png> <saida.json> --centro x,y [--alvos "id:x,y;id2:x,y"] [--min-comp 60] [--simplificar 1.5]

Esqueletiza a máscara (do isolar_camada.py), liga pedaços vizinhos, acha o menor caminho do centro a cada ponta do esqueleto
(as "pontas" dos dendritos, filamentos, circuitos) e a cada alvo (ex.: o anel de um agente), e simplifica (Ramer–Douglas–Peucker).
Saída: {"centro": [x, y], "pontas": [[[x, y], …], …], "alvos": {"id": [[x, y], …]}} — em px da imagem. Faíscas, feixes e pulsos que
"andam pelo desenho" leem esse JSON (canvas: interpolar ao longo da polilinha; SVG: virar um `d`).
"""
from __future__ import annotations

import argparse
import heapq
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize


def rdp(pts: list[tuple[float, float]], eps: float) -> list[tuple[float, float]]:
    if len(pts) < 3:
        return pts
    a, b = np.array(pts[0]), np.array(pts[-1])
    ab = b - a
    n = np.hypot(*ab) or 1e-9
    d = [abs(ab[0] * (p[1] - a[1]) - ab[1] * (p[0] - a[0])) / n for p in pts[1:-1]]
    i = int(np.argmax(d)) + 1
    if d[i - 1] > eps:
        return rdp(pts[:i + 1], eps)[:-1] + rdp(pts[i:], eps)
    return [pts[0], pts[-1]]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('mascara')
    ap.add_argument('saida')
    ap.add_argument('--centro', required=True)
    ap.add_argument('--alvos', default='')
    ap.add_argument('--min-comp', type=float, default=60, help='comprimento mínimo (px) de um caminho até ponta')
    ap.add_argument('--simplificar', type=float, default=1.5)
    ap.add_argument('--ligar', type=int, default=3, help='dilatação (px) antes de esqueletizar: une traços quase encostados')
    a = ap.parse_args()
    m = np.asarray(Image.open(a.mascara).convert('L')) > 127
    m = ndimage.binary_dilation(m, iterations=a.ligar)
    esq = skeletonize(m)
    H, W = esq.shape
    cx, cy = map(int, a.centro.split(','))
    ys, xs = np.nonzero(esq)
    # o ponto do esqueleto mais perto de um ponto qualquer
    perto = lambda x, y: (lambda i: (int(xs[i]), int(ys[i])))(int(np.argmin((xs - x) ** 2 + (ys - y) ** 2)))
    ini = perto(cx, cy)
    # Dijkstra no esqueleto (8 vizinhos)
    dist = {ini: 0.0}
    pai: dict[tuple[int, int], tuple[int, int]] = {}
    fila = [(0.0, ini)]
    viz = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    while fila:
        dd, (x, y) = heapq.heappop(fila)
        if dd > dist.get((x, y), 1e18):
            continue
        for ox, oy in viz:
            nx, ny = x + ox, y + oy
            if 0 <= nx < W and 0 <= ny < H and esq[ny, nx]:
                nd = dd + (1.4142 if ox and oy else 1.0)
                if nd < dist.get((nx, ny), 1e18):
                    dist[(nx, ny)] = nd
                    pai[(nx, ny)] = (x, y)
                    heapq.heappush(fila, (nd, (nx, ny)))

    def caminho(p):
        out = [p]
        while out[-1] in pai:
            out.append(pai[out[-1]])
        return [(float(x), float(y)) for x, y in reversed(out)]

    # pontas: pixels do esqueleto alcançáveis com 1 vizinho só
    vizinhos = ndimage.convolve(esq.astype(np.uint8), np.ones((3, 3), np.uint8), mode='constant') - 1
    pontas = [(int(x), int(y)) for y, x in zip(*np.nonzero(esq & (vizinhos == 1))) if (int(x), int(y)) in dist]
    caminhos = [rdp(caminho(p), a.simplificar) for p in pontas if dist[p] >= a.min_comp]
    alvos = {}
    for item in filter(None, a.alvos.split(';')):
        nome, xy = item.split(':')
        tx, ty = map(int, xy.split(','))
        alc = [(k, v) for k, v in dist.items() if (k[0] - tx) ** 2 + (k[1] - ty) ** 2 < 30 ** 2]
        if alc:
            p = min(alc, key=lambda kv: (kv[0][0] - tx) ** 2 + (kv[0][1] - ty) ** 2)[0]
            alvos[nome] = rdp(caminho(p), a.simplificar) + [(float(tx), float(ty))]
        else:
            print(f'  alvo {nome}: nenhum traço alcançável a menos de 30 px de ({tx},{ty})')
    r = lambda c: [[round(x, 1), round(y, 1)] for x, y in c]
    Path(a.saida).write_text(json.dumps({'centro': [cx, cy], 'pontas': [r(c) for c in caminhos],
                                         'alvos': {k: r(v) for k, v in alvos.items()}}, ensure_ascii=False))
    print(f'{a.saida} · {len(caminhos)} caminhos até pontas · alvos: {", ".join(alvos) or "-"}')


if __name__ == '__main__':
    main()
