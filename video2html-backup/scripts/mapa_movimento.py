# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "scipy", "pillow"]
# ///
"""Mapa de movimento de um vídeo de UI: ONDE algo se mexe, QUANTO e QUANDO.

    uv run mapa_movimento.py <video.mp4> <pasta_saida> [--largura-ref 1536] [--limiar 0.18] [--min-area 40]

Saídas em <pasta_saida>:
  movimento.png   mapa de calor (desvio por pixel ao longo do tempo) sobre o 1º quadro, com as regiões numeradas
  regioes.json    cada região: caixa (em px da referência), área, intensidade, curva de atividade, picos e período
  curvas.png      a atividade de cada região ao longo do tempo (uma linha por região)
  quadros/        o quadro de maior atividade de cada região (r01.jpg…) e uma folha com 9 quadros do vídeo

Não sabe O QUE se mexe nem COMO — isso é o analisar_video.py (modelo multimodal) + os seus olhos nos quadros.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

W, H = 480, 270  # resolução de análise (16:9)


def ler_quadros(video: Path, fps: float = 15) -> tuple[np.ndarray, float, tuple[int, int]]:
    info = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                           '-of', 'csv=p=0', str(video)], capture_output=True, text=True).stdout.strip().split(',')
    tam = (int(info[0]), int(info[1]))
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(video), '-vf', f'fps={fps},scale={W}:{H},format=gray',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32), fps, tam


def periodo(curva: np.ndarray, fps: float) -> float | None:
    """Período dominante (s) pela autocorrelação; None se a curva não se repete."""
    c = curva - curva.mean()
    if np.allclose(c, 0):
        return None
    ac = np.correlate(c, c, 'full')[len(c) - 1:]
    ac /= ac[0]
    for i in range(int(fps * 0.4), len(ac) - 1):  # ignora defasagens < 0,4 s
        if ac[i] > 0.35 and ac[i] >= ac[i - 1] and ac[i] >= ac[i + 1]:
            return round(i / fps, 2)
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('saida')
    ap.add_argument('--largura-ref', type=int, default=1536, help='largura da imagem de referência (as caixas saem nessa escala)')
    ap.add_argument('--limiar', type=float, default=0.18, help='fração do desvio máximo que conta como movimento')
    ap.add_argument('--min-area', type=int, default=40, help='área mínima de uma região (px na resolução de análise)')
    ap.add_argument('--fundir', type=float, default=0.7, help='correlação mínima para fundir pedaços vizinhos')
    ap.add_argument('--separar', type=float, default=0.8, help='janela (s) para separar regiões grandes pelo momento do pico; 0 desliga')
    a = ap.parse_args()
    video, saida = Path(a.video), Path(a.saida)
    (saida / 'quadros').mkdir(parents=True, exist_ok=True)

    f, fps, _ = ler_quadros(video)
    n = len(f)
    sd = f.std(0)
    base = np.median(f, 0)

    # regiões: pixels que se mexem acima do limiar, unidos por dilatação (um feixe + o nó viram uma região só)
    mascara = sd > a.limiar * sd.max()
    mascara = ndimage.binary_dilation(mascara, iterations=3)
    rot, _ = ndimage.label(mascara)
    # regiões grandes que juntam coisas encostadas (um anel + feixes) são separadas pelo MOMENTO do pico de cada pixel:
    # o que acende em tempos diferentes vira região diferente
    pico_px = np.abs(f - base).argmax(0) / fps
    mascaras = []
    for i in range(1, rot.max() + 1):
        m = rot == i
        if m.sum() < a.min_area:
            continue
        if m.sum() > 0.12 * mascara.sum() and a.separar:
            faixas = np.floor(pico_px / a.separar)
            sub, nsub = ndimage.label(m & (sd > a.limiar * sd.max()), structure=np.ones((3, 3)))
            partes = []
            for fx in np.unique(faixas[m]):
                mm = ndimage.binary_dilation(m & (faixas == fx) & (sd > a.limiar * sd.max()), iterations=2) & m
                r2, _ = ndimage.label(mm)
                partes += [r2 == j for j in range(1, r2.max() + 1) if (r2 == j).sum() >= a.min_area]
            mascaras += partes or [m]
        else:
            mascaras.append(m)
    # funde de volta pedaços vizinhos que se mexem juntos (curvas de atividade correlacionadas): o anel que brilha
    # inteiro volta a ser um; feixes que acendem em tempos diferentes continuam separados
    curva = lambda m: np.abs(f[:, m] - base[m]).mean(1)
    grupos = [[m, curva(m)] for m in mascaras]
    mudou = True
    while mudou and len(grupos) > 1:
        mudou = False
        for i in range(len(grupos)):
            viz = ndimage.binary_dilation(grupos[i][0], iterations=4)
            for j in range(i + 1, len(grupos)):
                if not (viz & grupos[j][0]).any():
                    continue
                ci, cj = grupos[i][1], grupos[j][1]
                if np.std(ci) and np.std(cj) and np.corrcoef(ci, cj)[0, 1] > a.fundir:
                    m = grupos[i][0] | grupos[j][0]
                    grupos[i] = [m, curva(m)]
                    del grupos[j]
                    mudou = True
                    break
            if mudou:
                break
    mascaras = [g[0] for g in grupos]
    escala = a.largura_ref / W
    regioes = []
    for m in mascaras:
        ys, xs = np.nonzero(m)
        fatia = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
        area = int(m.sum())
        atividade = np.abs(f[:, m] - base[m]).mean(1)  # quanto a região difere do "repouso" em cada quadro
        pico = int(atividade.argmax())
        ativo = atividade > atividade.min() + 0.5 * (atividade.max() - atividade.min())
        janelas, ini = [], None
        for j, v in enumerate(ativo):
            if v and ini is None:
                ini = j
            if (not v or j == n - 1) and ini is not None:
                janelas.append([round(ini / fps, 2), round(j / fps, 2)])
                ini = None
        y0, y1, x0, x1 = fatia[0].start, fatia[0].stop, fatia[1].start, fatia[1].stop
        regioes.append({
            'caixa': [round(x0 * escala), round(y0 * escala), round((x1 - x0) * escala), round((y1 - y0) * escala)],
            'area': area, 'intensidade': round(float(sd[m].mean()), 2), 'pico_s': round(pico / fps, 2),
            'janelas_ativas_s': janelas, 'periodo_s': periodo(atividade, fps),
            'curva': [round(float(x), 2) for x in atividade[:: max(1, int(fps / 5))]],  # 5 amostras/s
        })
    regioes.sort(key=lambda r: -r['intensidade'] * r['area'])
    for i, r in enumerate(regioes, 1):
        r['id'] = f'r{i:02d}'

    # imagens: mapa de calor + caixas
    q0 = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(video), '-vframes', '1', '-vf', f'scale={W * 2}:{H * 2}',
                         '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True, check=True).stdout
    from io import BytesIO
    fundo = Image.open(BytesIO(q0)).convert('RGB')
    calor = (np.clip(sd / sd.max(), 0, 1) * 255).astype(np.uint8)
    cor = np.stack([calor, (calor * 0.55).astype(np.uint8), np.zeros_like(calor)], -1)
    cor = Image.fromarray(cor).resize(fundo.size)
    mapa = Image.blend(Image.eval(fundo, lambda v: v // 3), cor, 0.65)
    d = ImageDraw.Draw(mapa)
    try:
        fonte = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 15)
    except OSError:
        fonte = ImageFont.load_default()
    k2 = 2 * W / a.largura_ref
    for r in regioes:
        x, y, w, h = [v * k2 for v in r['caixa']]
        d.rectangle([x, y, x + w, y + h], outline=(80, 200, 255), width=2)
        d.text((x + 3, y + 2), r['id'], fill=(255, 255, 255), font=fonte)
    mapa.save(saida / 'movimento.png')

    # curvas
    ch, cw = 46, 720
    curvas = Image.new('RGB', (cw + 60, ch * max(1, len(regioes)) + 20), (12, 14, 18))
    d = ImageDraw.Draw(curvas)
    for i, r in enumerate(regioes):
        c = np.array(r['curva'])
        c = (c - c.min()) / (np.ptp(c) or 1)
        y0 = 10 + i * ch
        pts = [(55 + j * cw / max(1, len(c) - 1), y0 + ch - 8 - v * (ch - 14)) for j, v in enumerate(c)]
        d.line(pts, fill=(90, 190, 255), width=2)
        d.text((6, y0 + ch / 2 - 8), r['id'], fill=(220, 220, 220), font=fonte)
    curvas.save(saida / 'curvas.png')

    # quadros: o pico de cada região + folha 3×3
    for r in regioes:
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(r['pico_s']), '-i', str(video), '-vframes', '1',
                        '-vf', 'scale=960:-2', '-strict', '-1', str(saida / 'quadros' / f'{r["id"]}.jpg')])
    dur = n / fps
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(video), '-vf', f'fps={9 / dur:.4f},scale=640:-2,tile=3x3',
                    '-frames:v', '1', '-strict', '-1', str(saida / 'quadros' / 'folha.jpg')])

    (saida / 'regioes.json').write_text(json.dumps({'video': str(video), 'duracao_s': round(dur, 2), 'fps_analise': fps,
                                                    'largura_ref': a.largura_ref, 'regioes': regioes}, indent=1, ensure_ascii=False))
    print(f'{len(regioes)} regiões · {dur:.1f} s → {saida}')
    for r in regioes:
        print(f"  {r['id']} caixa={r['caixa']} int={r['intensidade']} pico={r['pico_s']}s período={r['periodo_s']} ativas={r['janelas_ativas_s'][:3]}")


if __name__ == '__main__':
    main()
