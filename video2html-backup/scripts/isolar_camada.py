# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow"]
# ///
"""Isola a arte clara (traços, linhas, brilhos) da referência sobre uma placa de fundo — para virar uma camada própria.

    uv run isolar_camada.py <referencia.png> <placa.png> <saida.png> [--excluir "x,y,w,h;x,y,w,h"] [--manter "x,y,w,h"] [--suave 2]
    uv run isolar_camada.py <referencia.png> <placa.png> <saida.png> --modo duplo      (arte escura E clara: fundos claros)

A camada sai em RGB sobre preto e deve ser usada com `mix-blend-mode: screen` por cima da placa: a conta é o inverso do screen
(O = 1 − (1 − R)/(1 − P)), então placa + camada reproduz a referência onde ela é mais clara que a placa. --excluir zera regiões
(textos, anéis, painéis que serão HTML/SVG); --manter limita a camada a uma caixa. Também grava <saida>-mascara.png (para o
caminhos.py). Ideal para arte luminosa fina (neurônios, circuitos, filamentos) que uma segmentação comum não recorta bem.

--modo duplo (fundos claros, ex.: tinta sobre papel com brasas): grava <saida>-escura.png (use com `mix-blend-mode: multiply`,
O = R/P: branco onde não há nada) e <saida>-clara.png (com `screen`, o que é mais claro que a placa). placa → multiply → screen
reproduz a imagem nos dois sentidos.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def caixas(texto: str) -> list[tuple[int, int, int, int]]:
    return [tuple(map(int, c.split(','))) for c in filter(None, texto.split(';'))]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('referencia')
    ap.add_argument('placa')
    ap.add_argument('saida')
    ap.add_argument('--excluir', default='')
    ap.add_argument('--manter', default='')
    ap.add_argument('--suave', type=float, default=2, help='desfoque (px) da borda das regiões excluídas')
    ap.add_argument('--limiar', type=float, default=10, help='diferença mínima (0–255) que conta como traço')
    ap.add_argument('--modo', choices=['claro', 'duplo'], default='claro')
    a = ap.parse_args()
    ref = Image.open(a.referencia).convert('RGB')
    placa = Image.open(a.placa).convert('RGB').resize(ref.size, Image.LANCZOS)
    R = np.asarray(ref).astype(np.float32) / 255
    P = np.asarray(placa).astype(np.float32) / 255
    O = np.clip(1 - (1 - R) / np.maximum(1 - P, 1e-3), 0, 1)
    dif = (R - P).max(2) * 255
    O[dif < a.limiar] = 0
    E = np.clip(R / np.maximum(P, 1e-3), 0, 1)   # camada escura (multiply)
    E[(P - R).max(2) * 255 < a.limiar] = 1

    mascara = Image.new('L', ref.size, 255 if not a.manter else 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(mascara)
    for x, y, w, h in caixas(a.manter):
        d.rectangle([x, y, x + w, y + h], fill=255)
    for x, y, w, h in caixas(a.excluir):
        d.rectangle([x, y, x + w, y + h], fill=0)
    if a.suave:
        mascara = mascara.filter(ImageFilter.GaussianBlur(a.suave))
    M = np.asarray(mascara).astype(np.float32)[..., None] / 255
    O *= M
    E = 1 - (1 - E) * M
    out = Path(a.saida)
    if a.modo == 'duplo':
        Image.fromarray((E * 255).astype(np.uint8)).save(out.with_name(out.stem + '-escura.png'))
        Image.fromarray((O * 255).astype(np.uint8)).save(out.with_name(out.stem + '-clara.png'))
        escuro = ((1 - E.min(2)) * 255 > 28).astype(np.uint8) * 255
        Image.fromarray(escuro).save(out.with_name(out.stem + '-mascara.png'))
        print(out.with_name(out.stem + '-escura.png'), '+ -clara.png', f'· {(escuro > 0).mean() * 100:.1f}% da tela é arte escura')
        return
    Image.fromarray((O * 255).astype(np.uint8)).save(out)
    traço = ((O.max(2) * 255) > 28).astype(np.uint8) * 255
    Image.fromarray(traço).save(out.with_name(out.stem + '-mascara.png'))
    print(out, f'· {(traço > 0).mean() * 100:.1f}% da tela é traço')


if __name__ == '__main__':
    main()
