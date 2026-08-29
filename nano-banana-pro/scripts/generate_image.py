# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow",
#     "python-dotenv",
#     "requests",
# ]
# ///
"""
Generate or edit images using Google's Nano Banana models, via two interchangeable backends:

  --provider gemini      -> Google Gemini API directly (needs GEMINI_API_KEY)
  --provider openrouter  -> OpenRouter aggregator (needs OPENROUTER_API_KEY)

Both support text-to-image and image-to-image (--input-image), resolution (512/1K/2K/4K; default 512) and
aspect ratio. Model IDs differ per provider:
  gemini     : gemini-3-pro-image-preview (Pro) | gemini-3.1-flash-image-preview (Flash)
  openrouter : google/gemini-3-pro-image-preview | google/gemini-3.1-flash-image-preview
"""
import argparse
import base64
import mimetypes
import os
import sys

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = {
    "gemini": "gemini-3.1-flash-image-preview",
    "openrouter": "google/gemini-3.1-flash-image-preview",
}


def read_image_data_url(path):
    with open(path, "rb") as f:
        data = f.read()
    mime, _ = mimetypes.guess_type(path)
    mime = mime or "image/png"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}", mime, data


def ensure_parent(out_path):
    d = os.path.dirname(out_path)
    if d:
        os.makedirs(d, exist_ok=True)


def gen_gemini(args, api_key):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    parts = [args.prompt]
    if args.input_image:
        _, mime, data = read_image_data_url(args.input_image)
        parts.append(types.Part.from_bytes(data=data, mime_type=mime))

    image_cfg = {"image_size": args.resolution}
    if args.aspect_ratio:
        image_cfg["aspect_ratio"] = args.aspect_ratio
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(**image_cfg),
    )
    resp = client.models.generate_content(model=args.model, contents=parts, config=config)
    for cand in (resp.candidates or []):
        for part in (cand.content.parts or []):
            inline = getattr(part, "inline_data", None)
            if inline and inline.data:
                return inline.data
    raise RuntimeError(f"Nenhuma imagem retornada.{(' ' + (resp.text or '')) if getattr(resp, 'text', None) else ''}")


def gen_openrouter(args, api_key):
    import requests

    content = []
    if args.input_image:
        data_url, _, _ = read_image_data_url(args.input_image)
        content.append({"type": "image_url", "image_url": {"url": data_url}})
    content.append({"type": "text", "text": args.prompt})

    image_cfg = {"image_size": args.resolution}
    if args.aspect_ratio:
        image_cfg["aspect_ratio"] = args.aspect_ratio
    body = {
        "model": args.model,
        "messages": [{"role": "user", "content": content}],
        "modalities": ["image", "text"],
        "image_config": image_cfg,
    }
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=body, timeout=300,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"OpenRouter HTTP {resp.status_code}: {resp.text[:500]}")
    data = resp.json()
    try:
        images = data["choices"][0]["message"]["images"]
        url = images[0]["image_url"]["url"]
    except (KeyError, IndexError, TypeError):
        msg = ""
        try:
            msg = data["choices"][0]["message"].get("content") or ""
        except Exception:
            msg = str(data)[:500]
        raise RuntimeError(f"Nenhuma imagem retornada pelo OpenRouter. {msg}")
    b64 = url.split(",", 1)[1] if "," in url else url
    return base64.b64decode(b64)


def main():
    p = argparse.ArgumentParser(description="Gera/edita imagens (Nano Banana) via Gemini ou OpenRouter")
    p.add_argument("--prompt", required=True)
    p.add_argument("--filename", required=True)
    p.add_argument("--resolution", default="512", choices=["512", "1K", "2K", "4K"])
    p.add_argument("--aspect-ratio", default=None, help="ex.: 16:9, 1:1, 4:3")
    p.add_argument("--input-image", default=None, help="Imagem de entrada para edição (image-to-image)")
    p.add_argument("--provider", default="gemini", choices=["gemini", "openrouter"])
    p.add_argument("--model", default=None, help="ID do modelo (default depende do provider)")
    p.add_argument("--api-key", default=None, help="Sobrescreve a env var da chave")
    args = p.parse_args()

    if args.model is None:
        args.model = DEFAULT_MODEL[args.provider]

    if args.input_image and not os.path.isfile(args.input_image):
        print(f"ERROR: Input image not found: {args.input_image}", file=sys.stderr)
        sys.exit(1)

    if args.provider == "openrouter":
        api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
        key_name = "OPENROUTER_API_KEY"
        runner = gen_openrouter
    else:
        api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
        key_name = "GEMINI_API_KEY"
        runner = gen_gemini

    if not api_key:
        print(f"ERROR: No API key found. Set {key_name} (env/.env) or pass --api-key.", file=sys.stderr)
        sys.exit(1)

    try:
        img_bytes = runner(args, api_key)
    except Exception as e:
        print(f"ERROR: image generation failed ({args.provider}/{args.model}): {e}", file=sys.stderr)
        sys.exit(1)

    out_path = os.path.abspath(args.filename)
    ensure_parent(out_path)
    with open(out_path, "wb") as f:
        f.write(img_bytes)
    print(f"Image saved to: {out_path}")


if __name__ == "__main__":
    main()
