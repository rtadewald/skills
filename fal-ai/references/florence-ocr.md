# Florence-2 Large — OCR with Region (fal)

Fonte: `https://fal.ai/models/fal-ai/florence-2-large/ocr-with-region/llms.txt`

**Primary for img-to-html2 typography crops** — tight text bboxes, not Moondream.

## Endpoint

| Campo | Valor |
|-------|-------|
| ID | `fal-ai/florence-2-large/ocr-with-region` |
| URL | `POST https://fal.run/fal-ai/florence-2-large/ocr-with-region` |

## Pricing (Platform API, snapshot)

- **$0.00125 / compute second** (USD)
- 1 chamada por imagem → todos os blocos de texto
- Mock 1024×682 ≈ ~10–15 s compute → **~$0.01–0.02 por referência**
- Confirmar: `GET https://api.fal.ai/v1/models/pricing?endpoint_id=fal-ai/florence-2-large/ocr-with-region`

## Input

```json
{ "image_url": "https://…" }
```

Local file → `fal_client.upload_file(path)` primeiro.

## Output

```json
{
  "results": {
    "quad_boxes": [
      { "x": 77.3, "y": 135.4, "w": 246.8, "h": 40.2, "label": "EXPLORE." }
    ]
  }
}
```

- Coordenadas em **pixels** da imagem original (x, y, w, h)
- `label` = texto detectado (pode ter prefixo `</s>` — strip antes do match)
- Converter para crop: `[x, y, x+w, y+h]`

## Match wireframe → bbox

Não há parâmetro `text_input`. Fluxo:

1. OCR uma vez na `reference.*`
2. Por role, `sample_text` do wireframe (primeira tag)
3. Match `label` ≈ `sample_text` (exact → contains → token overlap)
4. PIL crop + pad 2px

Script: `img-to-html2/scripts/crop_text.py`

## Não usar para tipografia

| Endpoint | Por quê |
|----------|---------|
| Moondream `detect` | Região semântica larga |
| Moondream `segment` | Máscara agrupa texto + ícones |
| `open-vocabulary-detection` | Falhou vazio no NOVA mock |
| `caption-to-phrase-grounding` | Bbox gigante |

## Python

```python
import fal_client

url = fal_client.upload_file("reference.jpg")
raw = fal_client.subscribe(
    "fal-ai/florence-2-large/ocr-with-region",
    arguments={"image_url": url},
)
for box in raw["results"]["quad_boxes"]:
    label = box["label"].replace("</s>", "").strip()
    x0, y0 = int(box["x"]), int(box["y"])
    x1, y1 = x0 + int(box["w"]), y0 + int(box["h"])
```
