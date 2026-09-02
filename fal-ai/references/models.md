# fal.ai — modelos clássicos (endpoint IDs)

IDs para `fal_client.subscribe("<id>", arguments={…})`.  
Schema/preço atuais: `https://fal.ai/models/<id>/llms.txt`

## Visão / VLM

| Nome | Endpoint ID | Notas |
|------|-------------|-------|
| Moondream 3 Detect | `fal-ai/moondream3-preview/detect` | Bboxes — ver [moondream.md](moondream.md) |
| Moondream 3 Query | `fal-ai/moondream3-preview/query` | Q&A / JSON |
| Moondream 3 Point | `fal-ai/moondream3-preview/point` | Pontos |
| Moondream 3 Caption | `fal-ai/moondream3-preview/caption` | Caption |
| Moondream 3 Segment | `fal-ai/moondream3-preview/segment` | Máscara + bbox — layout UI |
| **Florence-2 OCR** | **`fal-ai/florence-2-large/ocr-with-region`** | **Texto + bbox — img-to-html2** — [florence-ocr.md](florence-ocr.md) |
| Florence-2 (outros) | `fal-ai/florence-2-large/*` | open-vocabulary-detection, caption-to-phrase-grounding, … |

## Text → image

| Nome | Endpoint ID |
|------|-------------|
| FLUX.1 [dev] | `fal-ai/flux/dev` |
| FLUX.1 [schnell] | `fal-ai/flux/schnell` |
| FLUX.1 [pro] | `fal-ai/flux-pro` |
| FLUX.2 | `fal-ai/flux-2` (checar variantes no gallery) |
| SDXL | `fal-ai/stable-diffusion-v3-medium` / SDXL paths no gallery |
| Recraft V3 | `fal-ai/recraft-v3` |
| Ideogram V3 | `fal-ai/ideogram/v3` |

## Image edit / inpaint

| Nome | Endpoint ID |
|------|-------------|
| FLUX.1 Fill / Redux | `fal-ai/flux/dev/redux` (e fill siblings) |
| FLUX Kontex | variants `fal-ai/flux-pro/kontext` |
| Nano Banana (Gemini image) | paths `fal-ai/nano-banana*` no gallery |

## Video

| Nome | Endpoint ID |
|------|-------------|
| Kling | `fal-ai/kling-video/*` |
| MiniMax / Hailuo | `fal-ai/minimax-video/*` |
| Luma Ray | `fal-ai/luma-dream-machine` |
| Runway | `fal-ai/runway-*` |

## Áudio / TTS / STT

| Nome | Endpoint ID |
|------|-------------|
| Whisper | `fal-ai/whisper` |
| Wizper (fast) | `fal-ai/wizper` |
| Dia TTS / similares | gallery `fal-ai/*tts*` |

## Util platform

| Uso | URL |
|-----|-----|
| Pricing de um endpoint | `GET https://api.fal.ai/v1/models/pricing?endpoint_id=<id>` + `Authorization: Key $FAL_KEY` |
| CDN upload | `fal_client.upload_file(path)` → `https://v3.fal.media/files/…` |
| Sync run | `POST https://fal.run/<endpoint-id>` |
| Queue | client `submit` / docs queue |

IDs mudam (preview → GA). Se `subscribe` 404, reabrir o `llms.txt` do modelo no site.
