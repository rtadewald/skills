---
name: to-img
description: >-
  Gera n imagens em paralelo via OpenRouter (default gpt2 @ 1K) a partir de
  qualquer pedido do usuário e salva em mocks/. Use when the user mentions to-img.
disable-model-invocation: true
---

# To Img

Recebe qualquer pedido de imagem do usuário e gera **n** versões em paralelo via OpenRouter. Default: `gpt2` (GPT Image 2), `1K`, `16:9`. Salva em `mocks/`.

## Fluxo

1. Pegue o pedido do usuário. Se ele não disser **n**, pergunte (default **3**). Se passar uma imagem de referência, use como `--input-image`.
2. Monte o `--prompt` a partir do pedido. Se for tela de app, deixe explícito que é um aplicativo usável.
3. Olhe `mocks/` e use o próximo `{n}` livre (ou o que o usuário indicar): `{n}-a.png`, `{n}-b.png`, `{n}-c.png`…
4. Dispare as **n** chamadas em paralelo no cwd do usuário, com `OPENROUTER_API_KEY` (`.env` do projeto ou `~/.env`):

```bash
uv run ~/.agents/skills/openrouter-img/scripts/generate_image.py \
  --prompt "..." --filename "mocks/{n}-a.png" \
  --model gpt2 --resolution 1K --aspect-ratio 16:9 &

uv run ~/.agents/skills/openrouter-img/scripts/generate_image.py \
  --prompt "..." --filename "mocks/{n}-b.png" \
  --model gpt2 --resolution 1K --aspect-ratio 16:9 &

wait
```

Cada versão pode ter um prompt ligeiramente diferente (mesma ideia, outro ângulo), se fizer sentido. Suba resolução / mude modelo só se o usuário pedir. Com referência: acrescente `--input-image` em todas.

5. Mostre os paths e pare.
