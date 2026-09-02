---
name: fal-ai
description: >-
  Call fal.ai Model APIs (auth, upload, subscribe/queue, parse responses). Use
  when the user mentions fal-ai, fal.ai, FAL_KEY, Moondream detect/query/point,
  Florence-2 OCR, or needs text/UI boxes for img-to-html. Prefer scripts under
  fal-ai/scripts/ and img-to-html2/scripts/crop_text.py for typography crops.
disable-model-invocation: true
---

# fal.ai

Skill de integração com a **fal Model API**: autenticar, enviar imagem, chamar endpoint, tratar resposta.

Docs ao vivo por modelo: `https://fal.ai/models/<endpoint-id>/llms.txt`

## Auth

1. Chave: `FAL_KEY` (env, cwd `.env`, ou `~/.env`)
2. Header HTTP: `Authorization: Key $FAL_KEY`
3. Python: `pip install fal-client` — o client lê `FAL_KEY` sozinho

Nunca hardcode a chave. Se faltar → pedir ao usuário / falhar com mensagem clara.

## Padrão de chamada (Python)

```python
import fal_client

# Local file → URL temporária no CDN fal
url = fal_client.upload_file("mock.png")

result = fal_client.subscribe(
    "fal-ai/moondream3-preview/detect",
    arguments={"image_url": url, "prompt": "UI card"},
)
# result é um dict com o schema do modelo
```

| Método | Quando |
|--------|--------|
| `fal_client.subscribe(id, arguments=…)` | Default — bloqueia até o resultado |
| `fal_client.submit(id, arguments=…)` + `.get()` | Fire-and-forget / paralelizar vários jobs |
| `POST https://fal.run/<endpoint-id>` | curl / sem client |

Upload: `upload_file(path)` (sync) ou `upload_file_async`. Aceita PNG/JPG/WebP.

## Tratar resposta

- Sempre checar campos do schema do endpoint (varia por modelo).
- Coordenadas Moondream (`detect` / `point`) vêm **normalizadas 0–1** relativas à imagem — converter para pixels com `x * width`, `y * height`.
- `usage_info` / billing: tokens ou unidade do modelo; preços mudam → confiar na página do modelo ou Platform Pricing API.
- Erros HTTP 4xx: chave inválida / input; 5xx: retry com `submit` ou avisar.

## Florence-2 OCR (tipografia img-to-html2)

**Primary para crops de texto** — bbox tight por string detectada.

| Endpoint ID | Uso |
|-------------|-----|
| `fal-ai/florence-2-large/ocr-with-region` | OCR + `{x,y,w,h,label}` por bloco — **1 call/imagem** |

```python
result = fal_client.subscribe(
    "fal-ai/florence-2-large/ocr-with-region",
    arguments={"image_url": url},
)
# result["results"]["quad_boxes"] → match label ↔ wireframe sample_text
```

Batch crops: `uv run ~/.agents/skills/img-to-html2/scripts/crop_text.py --project design-systems/<slug>-regions`

Schema / pricing / match: [references/florence-ocr.md](references/florence-ocr.md)

## Moondream 3 (layout UI, não tipografia)

Família `fal-ai/moondream3-preview/*` — visão barata para **segmentar layout** (cards, painéis, botões). **Não** usar detect/segment para crops de fonte.

| Alias | Endpoint ID | Uso |
|-------|-------------|-----|
| `detect` | `fal-ai/moondream3-preview/detect` | Bboxes por prompt (“card”, “sidebar”) — layout UI |
| `query` | `fal-ai/moondream3-preview/query` | Pergunta VLM / JSON estruturado |
| `point` | `fal-ai/moondream3-preview/point` | Pontos (x,y) normalizados |
| `caption` | `fal-ai/moondream3-preview/caption` | Caption short/normal/long |
| `segment` | `fal-ai/moondream3-preview/segment` | Máscara pixel + SVG `path` + bbox |

### CLI (preferir isto)

```bash
uv run ~/.agents/skills/fal-ai/scripts/moondream.py detect \
  --image path/to/mock.png \
  --prompt "card" \
  --out boxes.json

# multi-prompt (várias classes → um JSON)
uv run ~/.agents/skills/fal-ai/scripts/moondream.py detect \
  --image mock.png \
  --prompt "card" --prompt "button" --prompt "sidebar" \
  --out regions.json --overlay overlay.png
```

Outros modos: `query`, `point`, `caption`, `segment` (mesmo script, subcomando).

```bash
# máscara pixel-level (+ bbox / SVG path)
uv run ~/.agents/skills/fal-ai/scripts/moondream.py segment \
  --image mock.png --object "card" \
  --out segment.json --mask-out mask.png
```

`detect` → boxes px `[x0,y0,x1,y1]`; `segment` → máscara + `path` SVG + bbox. Schema: [references/moondream.md](references/moondream.md).

## Catálogo clássico

Endpoints frequentes (IDs prontos p/ `subscribe`): ver [references/models.md](references/models.md).

Antes de inventar um ID, abrir `https://fal.ai/models/<id>/llms.txt`.

## Regras pro agente

1. Preferir `scripts/moondream.py` a reescrever o client.
2. Rodar no **cwd do usuário** (paths de imagem relativos ao projeto).
3. Não colar `FAL_KEY` no chat / commits.
4. **Tipografia / crops de texto** → Florence-2 `ocr-with-region` via `crop_text.py`. **Layout** (cards, folds) → Moondream `detect`.
5. Schema Moondream → [references/moondream.md](references/moondream.md). Schema OCR → [references/florence-ocr.md](references/florence-ocr.md).
