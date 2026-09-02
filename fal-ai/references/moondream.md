# Moondream 3 Preview (fal)

Fonte: `https://fal.ai/models/fal-ai/moondream3-preview/<mode>/llms.txt`  
Preço (snapshot docs): **$0.4 / M input tokens**, **$3.5 / M output tokens**.

Coords `detect` / `point`: **normalizadas 0–1** (origem canto superior esquerdo).

---

## detect — `fal-ai/moondream3-preview/detect`

Object detection por texto. Primário para segmentar regiões em mocks (img-to-html).

**Input**

| Campo | Tipo | Notas |
|-------|------|-------|
| `image_url` | string | URL (upload local via `fal_client.upload_file`) |
| `prompt` | string | Objeto a achar — ex. `"card"`, `"sidebar"`, `"button"` |
| `preview` | bool | default `false` — se `true`, devolve imagem com boxes desenhados |

**Output**

| Campo | Tipo | Notas |
|-------|------|-------|
| `objects` | list | `{x_min,y_min,x_max,y_max}` normalizados |
| `image` | ImageFile? | só com `preview` |
| `finish_reason` | string | |
| `usage_info` | object | tokens / timings |

**Pixels** (script já faz):

```
x0 = x_min * W
y0 = y_min * H
x1 = x_max * W
y1 = y_max * H
```

**Prompts úteis p/ UI mock**

- `card` / `UI card` / `panel`
- `sidebar` / `navigation`
- `button` / `pill button`
- `text input` / `search bar`
- `avatar` / `icon`

Um prompt = uma classe. Para várias classes, chamar N vezes (CLI: vários `--prompt`).

---

## query — `fal-ai/moondream3-preview/query`

Pergunta aberta / JSON na imagem.

**Input:** `image_url`, `prompt`; opcional `reasoning` (default true), `temperature`, `top_p`  
**Output:** `output` (string), `reasoning?`, `usage_info`

Peça JSON explícito no prompt (“Reply with JSON only: …”).

---

## point — `fal-ai/moondream3-preview/point`

Centro/âncora de objetos (não bbox).

**Input:** `image_url`, `prompt`, `preview?`  
**Output:** `points: [{x,y}, …]` normalizados; `image?`

---

## caption — `fal-ai/moondream3-preview/caption`

**Input:** `image_url`; `length`: `short` | `normal` | `long`  
**Output:** `output` (caption string)

---

## segment — `fal-ai/moondream3-preview/segment`

Máscara pixel-level (image-to-image). Campo do objeto é `object` (não `prompt`).

**Input**

| Campo | Tipo | Notas |
|-------|------|-------|
| `image_url` | string | required |
| `object` | string | required — ex. `"card"`, `"mango"` |
| `spatial_references` | list? | pontos `{x,y}` ou boxes `[x1,y1,x2,y2]` (0–1); dá pra alimentar com saída do `point` |
| `preview` | bool | default `false` — `true` → devolve imagem máscara binária |
| `settings` | object? | sampling (raro na CLI) |

**Output**

| Campo | Tipo | Notas |
|-------|------|-------|
| `bbox` | Object? | `{x_min,y_min,x_max,y_max}` normalizados |
| `path` | string? | SVG path data da máscara |
| `image` | ImageFile? | máscara binária (com `preview`) |
| `usage_info` | object | |

CLI: `--object`, `--ref-point x,y`, `--ref-box x1,y1,x2,y2`, `--mask-out mask.png`.

---

## curl (detect)

```bash
IMG_URL=$(python -c "import fal_client; print(fal_client.upload_file('mock.png'))")

curl -s -X POST "https://fal.run/fal-ai/moondream3-preview/detect" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"image_url\":\"$IMG_URL\",\"prompt\":\"card\"}"
```
