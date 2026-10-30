# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Grava (ou fotografa) uma página HTML no Chrome instalado, sem janela — para comparar com a referência.

    uv run gravar.py <url> <saida.mp4> [--segundos 9] [--largura 1536 --altura 864] [--esperar 2.5]
    uv run gravar.py <url> <saida.png> --foto [--em 0]          (foto depois de --esperar + --em segundos)
    uv run gravar.py <url> <saida.png> --foto --congelar        (pausa as animações GSAP/CSS antes da foto)

- Usa o Google Chrome do sistema (channel="chrome"): nada de baixar navegador.
- O vídeo vem do screencast do Chrome (quadros com o tempo real de cada um) e é montado com ffmpeg a 30 fps.
- Páginas com WebGL que carregam texturas locais precisam de http:// (não file://): sirva a pasta antes.
"""
from __future__ import annotations

import argparse
import base64
import subprocess
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('url')
    ap.add_argument('saida')
    ap.add_argument('--segundos', type=float, default=9)
    ap.add_argument('--largura', type=int, default=1536)
    ap.add_argument('--altura', type=int, default=864)
    ap.add_argument('--esperar', type=float, default=2.5, help='segundos para carregar fontes, texturas e CDN')
    ap.add_argument('--foto', action='store_true')
    ap.add_argument('--em', type=float, default=0, help='na foto: segundos extras depois de --esperar')
    ap.add_argument('--congelar', action='store_true', help='na foto: pausa GSAP e animações CSS')
    ap.add_argument('--antes', default='', help='JS rodado logo antes de gravar/fotografar (ex.: reiniciar a linha do tempo)')
    a = ap.parse_args()
    saida = Path(a.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        nav = p.chromium.launch(channel='chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required', '--hide-scrollbars',
                                                                        '--enable-unsafe-swiftshader', '--use-angle=metal'])
        pag = nav.new_page(viewport={'width': a.largura, 'height': a.altura}, device_scale_factor=1)
        erros = []
        pag.on('pageerror', lambda e: erros.append(str(e)))
        pag.on('console', lambda m: erros.append(m.text) if m.type == 'error' else None)
        pag.goto(a.url, wait_until='networkidle')
        pag.wait_for_timeout(a.esperar * 1000)
        if a.antes:
            pag.evaluate(f"() => {{ {a.antes}; }}")   # descarta o retorno (objetos do GSAP não serializam)
        if a.foto:
            pag.wait_for_timeout(a.em * 1000)
            if a.congelar:
                pag.evaluate("window.gsap && gsap.globalTimeline.pause(); document.getAnimations().forEach(x => x.pause())")
            pag.screenshot(path=str(saida))
        else:
            cdp = pag.context.new_cdp_session(pag)
            quadros: list[tuple[float, bytes]] = []
            ligado = [True]

            def quadro(e):
                if not ligado[0]:
                    return   # quadros que chegam depois de parar (o navegador já pode estar fechando)
                quadros.append((e['metadata']['timestamp'], base64.b64decode(e['data'])))
                try:
                    cdp.send('Page.screencastFrameAck', {'sessionId': e['sessionId']})
                except Exception:  # noqa: BLE001
                    pass
            cdp.on('Page.screencastFrame', quadro)
            cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': 88, 'maxWidth': a.largura, 'maxHeight': a.altura})
            fim = time.time() + a.segundos
            while time.time() < fim:
                pag.wait_for_timeout(100)
            ligado[0] = False
            cdp.send('Page.stopScreencast')
            with tempfile.TemporaryDirectory() as d:
                lista = []
                for i, (ts, img) in enumerate(quadros):
                    f = Path(d) / f'q{i:05d}.jpg'
                    f.write_bytes(img)
                    dur = (quadros[i + 1][0] - ts) if i + 1 < len(quadros) else 0.05
                    lista.append(f"file '{f}'\nduration {max(dur, 0.001):.4f}")
                lista.append(f"file '{Path(d) / f'q{len(quadros) - 1:05d}.jpg'}'")
                (Path(d) / 'lista.txt').write_text('\n'.join(lista))
                subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(Path(d) / 'lista.txt'),
                                '-vf', f'fps=30,scale={a.largura}:{a.altura}', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18',
                                '-t', str(a.segundos), str(saida)], check=True)
        nav.close()
    if erros:
        print('erros na página:\n  ' + '\n  '.join(erros[:10]))
    print(saida)


if __name__ == '__main__':
    main()
