# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "python-dotenv"]
# ///
"""Edita a foto de um item para anúncio com um modelo de imagem barato do OpenRouter.

    uv run editar_foto.py <foto.jpg> <saida.png> "<o que fazer>" [--modelo google/gemini-2.5-flash-image] [--tamanho 2K]

A chave vem de OPENROUTER_API_KEY (ambiente ou .env da pasta atual).
"""
import argparse
import base64
import mimetypes
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

REGRA = ('Edite esta foto de um item usado para um anúncio de classificados. Mantenha o MESMO item, idêntico: '
         'modelo, cores, logos, desgaste e qualquer defeito visível (nunca esconda defeitos, nunca invente partes). '
         'Mantenha o mesmo ângulo e enquadramento. Resultado fotorrealista, sem texto. Pedido: ')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('foto')
    ap.add_argument('saida')
    ap.add_argument('pedido')
    ap.add_argument('--modelo', default='google/gemini-2.5-flash-image')
    ap.add_argument('--tamanho', help='1K, 2K ou 4K (só nos modelos que aceitam, ex.: google/gemini-3-pro-image-preview)')
    ap.add_argument('--proporcao', default='9:16')
    a = ap.parse_args()
    load_dotenv(Path.cwd() / '.env')
    chave = os.environ.get('OPENROUTER_API_KEY')
    if not chave:
        sys.exit('Falta OPENROUTER_API_KEY (ambiente ou .env).')
    tipo = mimetypes.guess_type(a.foto)[0] or 'image/jpeg'
    dados = base64.b64encode(Path(a.foto).read_bytes()).decode()
    r = requests.post('https://openrouter.ai/api/v1/chat/completions', timeout=180,
                      headers={'Authorization': f'Bearer {chave}'},
                      json={'model': a.modelo, 'modalities': ['image', 'text'],
                            'messages': [{'role': 'user', 'content': [
                                {'type': 'text', 'text': REGRA + a.pedido},
                                {'type': 'image_url', 'image_url': {'url': f'data:{tipo};base64,{dados}'}}]}],
                            **({'image_config': {'image_size': a.tamanho, 'aspect_ratio': a.proporcao}} if a.tamanho else {})})
    r.raise_for_status()
    msg = r.json()['choices'][0]['message']
    imagens = msg.get('images') or []
    if not imagens:
        sys.exit(f'O modelo não devolveu imagem: {(msg.get("content") or "")[:300]}')
    url = imagens[0]['image_url']['url']
    Path(a.saida).write_bytes(base64.b64decode(url.split(',', 1)[1]))
    custo = r.json().get('usage', {}).get('cost')
    print(f'{a.saida}  ({a.modelo}{f", US$ {custo:.4f}" if custo else ""})')


if __name__ == '__main__':
    main()
