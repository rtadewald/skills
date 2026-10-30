# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "scipy", "pillow"]
# ///
"""Compara o MOVIMENTO do HTML gravado com o do vídeo de referência (fase de vida).

    uv run comparar_movimento.py <video_ref.mp4> <video_html.mp4> <pasta_saida> [--largura-ref 1536]

Saídas em <pasta_saida>:
  ref/ e html/       o mapa de movimento de cada vídeo (mapa_movimento.py)
  lado-a-lado.mp4    os dois vídeos juntos (ref | html), para ver o ritmo
  mapas.jpg          os dois mapas de movimento lado a lado
  comparar.html      página com os vídeos sincronizados + mapas (abrir num servidor local)
  no terminal        para cada região viva da referência: a energia de movimento no HTML na mesma caixa (alarme se ~0)

Os números são alarme, não nota: o HTML pode (e deve) ter vida própria além da referência. O juízo de ritmo e caráter
é seu (e, se quiser, do analisar_video.py --comparar).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
from mapa_movimento import W, H, ler_quadros  # noqa: E402


def energia(video: Path) -> np.ndarray:
    f, _, _ = ler_quadros(video)
    return f.std(0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('ref')
    ap.add_argument('html')
    ap.add_argument('saida')
    ap.add_argument('--largura-ref', type=int, default=1536)
    a = ap.parse_args()
    out = Path(a.saida)
    out.mkdir(parents=True, exist_ok=True)
    for nome, v in (('ref', a.ref), ('html', a.html)):
        subprocess.run(['uv', 'run', str(AQUI / 'mapa_movimento.py'), v, str(out / nome), '--largura-ref', str(a.largura_ref)],
                       check=True, stdout=subprocess.DEVNULL)

    ref = json.loads((out / 'ref' / 'regioes.json').read_text())
    e_ref, e_html = energia(Path(a.ref)), energia(Path(a.html))
    k = W / a.largura_ref
    print(f"{'região':7} {'caixa':22} {'ref':>6} {'html':>6}  situação")
    alarmes = 0
    for r in ref['regioes']:
        x, y, w, h = [int(round(v * k)) for v in r['caixa']]
        er, eh = e_ref[y:y + h, x:x + w].mean(), e_html[y:y + h, x:x + w].mean()
        situ = 'ok' if eh >= 0.35 * er else ('fraco' if eh >= 0.12 * er else 'PARADO')
        alarmes += situ == 'PARADO'
        print(f"{r['id']:7} {str(r['caixa']):22} {er:6.1f} {eh:6.1f}  {situ}")
    extra = (e_html > 0.25 * e_html.max()) & (e_ref < 0.08 * e_ref.max())
    print(f'movimento só no HTML: {extra.mean() * 100:.1f}% da tela (vida própria: esperado em parte)')
    print(f'{alarmes} região(ões) da referência paradas no HTML')

    a1, a2 = Image.open(out / 'ref' / 'movimento.png'), Image.open(out / 'html' / 'movimento.png')
    m = Image.new('RGB', (a1.width * 2 + 8, a1.height), (0, 0, 0))
    m.paste(a1, (0, 0))
    m.paste(a2, (a1.width + 8, 0))
    m.save(out / 'mapas.jpg', quality=88)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', a.ref, '-i', a.html, '-filter_complex',
                    '[0:v]scale=768:432,setsar=1[a];[1:v]scale=768:432,setsar=1,trim=0:12[b];[a][b]hstack=shortest=1',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', str(out / 'lado-a-lado.mp4')], check=True)
    rel = lambda p: Path(p).resolve().as_posix()
    (out / 'comparar.html').write_text(f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Movimento · ref × html</title>
<link rel="stylesheet" href="data:text/css,body{{margin:0;background:%23070b10;color:%23c9d6e0;font:14px system-ui}}main{{padding:20px;display:grid;gap:16px}}.v{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}video,img{{width:100%;border-radius:10px;display:block}}h1{{font-size:16px;margin:0}}button{{font:inherit;padding:6px 12px;border-radius:8px;border:1px solid %23345;background:%23101820;color:inherit;cursor:pointer}}">
</head><body><main><h1>Referência (esq.) × HTML (dir.)</h1>
<div class="v"><video id="a" src="{Path(a.ref).name if Path(a.ref).parent == out else rel(a.ref)}" muted loop playsinline autoplay></video><video id="b" src="{Path(a.html).name if Path(a.html).parent == out else rel(a.html)}" muted loop playsinline autoplay></video></div>
<div><button id="s">⟲ Sincronizar</button></div>
<img src="mapas.jpg" alt="mapas de movimento"><img src="ref/curvas.png" alt="curvas da referência">
</main><script src="data:text/javascript,const a=document.getElementById('a'),b=document.getElementById('b');document.getElementById('s').onclick=()=>{{a.currentTime=b.currentTime=0;a.play();b.play()}}"></script></body></html>''', encoding='utf-8')
    print(out / 'comparar.html')


if __name__ == '__main__':
    main()
