# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow"]
# ///
"""Compara a foto do HTML com a imagem de referência (fase estática): onde e quanto diferem.

    uv run comparar_quadro.py <referencia.png> <foto.png> <pasta_saida> [--regioes "nome:x,y,w,h;nome2:x,y,w,h"]

Saídas: lado-a-lado.jpg · mistura.jpg (50 %) · diferenca.jpg (mapa de calor) · zoom-<nome>.jpg (ref | html, por região)
e no terminal a diferença média de luminância (0–255) na tela toda e por região. Use junto com o modo ?estatico da página.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('referencia')
    ap.add_argument('foto')
    ap.add_argument('saida')
    ap.add_argument('--regioes', default='')
    a = ap.parse_args()
    out = Path(a.saida)
    out.mkdir(parents=True, exist_ok=True)
    ref = Image.open(a.referencia).convert('RGB')
    foto = Image.open(a.foto).convert('RGB').resize(ref.size, Image.LANCZOS)
    r = np.asarray(ref).astype(np.float32)
    f = np.asarray(foto).astype(np.float32)
    lum = lambda x: x @ np.array([0.299, 0.587, 0.114], np.float32)
    dif = np.abs(lum(r) - lum(f))

    lado = Image.new('RGB', (ref.width * 2, ref.height))
    lado.paste(ref, (0, 0))
    lado.paste(foto, (ref.width, 0))
    lado.save(out / 'lado-a-lado.jpg', quality=88)
    Image.blend(ref, foto, 0.5).save(out / 'mistura.jpg', quality=88)
    calor = np.clip(dif * 4, 0, 255).astype(np.uint8)
    Image.fromarray(np.stack([calor, calor // 2, 255 - calor], -1)).save(out / 'diferenca.jpg', quality=88)

    print(f'diferença média de luminância: {dif.mean():.2f}/255 (tela toda)')
    for item in filter(None, a.regioes.split(';')):
        nome, caixa = item.split(':')
        x, y, w, h = map(int, caixa.split(','))
        print(f'  {nome:<14} {dif[y:y + h, x:x + w].mean():6.2f}/255')
        z = Image.new('RGB', (w * 2, h))
        z.paste(ref.crop((x, y, x + w, y + h)), (0, 0))
        z.paste(foto.crop((x, y, x + w, y + h)), (w, 0))
        escala = max(1, 900 // (w * 2))
        z.resize((w * 2 * escala, h * escala), Image.NEAREST).save(out / f'zoom-{nome}.jpg', quality=90)


if __name__ == '__main__':
    main()
