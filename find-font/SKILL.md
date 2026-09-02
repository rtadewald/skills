---
name: find-font
description: >-
  Detect a font from a single-line glyph crop via local find-font API on :8000
  (exact TTF file_url + weight_css + letter_spacing + color + overlay_png). Use
  when the user mentions find-font or find-font on port 8000.
disable-model-invocation: true
---

# Find Font

Detecta a fonte de um **crop de texto** usando a API local em `http://127.0.0.1:8000/find-font`.

## Pré-requisitos do crop

- **Uma linha só** — sem quebra de linha no recorte
- **Texto legível** — crop ajustado ao glyph/word (pouco padding extra)
- **`text` case-sensitive** — copie exatamente o que aparece no crop (`EXPLORE.` ≠ `Explore.`)
- Para **cor / `font_size_px` / tracking** fiéis ao mock, use o crop **normal** (não o `-hi` invertido/upscalado). O `-hi` serve só se a prioridade for match de glifo e você for ignorar `color`/`font_size_px`.

## Chamada

```bash
curl -X POST "http://127.0.0.1:8000/find-font" \
  -F "text=EXPLORE." \
  -F "image=@input/sua-imagem.png"
```

Substitua `text` e o path do `@image` pelos valores reais.

## Resposta

```json
{
  "font": "Funnel Display",
  "variant": "Funnel Display — weight 500",
  "weight": 500,
  "weight_css": 400,
  "italic": false,
  "score": 0.8943,
  "overlap": 0.8662,
  "tracking": 0.0238,
  "letter_spacing": "0.044em",
  "font_size_px": 75.9,
  "file": "fonts/google/ofl/funneldisplay/FunnelDisplay[wght].ttf",
  "file_url": "http://127.0.0.1:8000/font-file/fonts/google/ofl/funneldisplay/FunnelDisplay[wght].ttf",
  "license_url": "http://127.0.0.1:8000/font-file/fonts/google/ofl/funneldisplay/OFL.txt",
  "color": "#fdfdfe",
  "background": "#04070c",
  "css": "font-family: \"Funnel Display\"; font-weight: 400; …",
  "overlay_png": "data:image/png;base64,…"
}
```

| Campo | Uso |
|-------|-----|
| `font` | Nome da família |
| `weight` | Peso que casou nos pixels (variáveis) — **não** use direto no CSS |
| `weight_css` | Peso para CSS (desconta engorde de tela) — **use este** |
| `letter_spacing` | Pronto p/ CSS, ex. `0.044em` |
| `font_size_px` | Corpo em px da imagem enviada |
| `color` / `background` | Cores detectadas no crop |
| `file_url` | **Baixar este TTF** e servir via `@font-face` local — **não** Google Fonts CDN |
| `overlay_png` | PNG de sobreposição (data-URL base64) — **salvar como log** a cada request |
| `score` | Confiança; ~≥0.85 costuma ser a fonte exata |

## Log de sobreposição (obrigatório)

A **cada** chamada a `/find-font`, se a resposta tiver `overlay_png` (ou `sobreposicao` / URL equivalente):

1. Decodar o data-URL (`data:image/png;base64,…`) → bytes PNG.
2. Salvar em disco, **um arquivo por request**, ex.:
   - `typography/logs/{role}-sobreposicao.png` (pipeline img-to-html2)
   - ou `…/logs/{slug}-sobreposicao.png` (chamada avulsa)
3. **Não** embutir o base64 em `find-font-results.json` (infla demais) — no JSON guarde só o path relativo, ex. `"overlay_log": "typography/logs/h1-sobreposicao.png"`.

Serve para conferir depois se o match visual bateu.

Há também `POST /overlay` na mesma API se precisar regenerar a sobreposição para uma candidata (`file` / `weight` / `tracking`).

## Fluxo do agente (fidedignidade)

1. Crop single-line + `text` exato.
2. `POST /find-font`.
3. **Salvar** `overlay_png` → log PNG (acima).
4. **Baixar** `file_url` para o projeto (ex. `typography/fonts/…`).
5. Gerar CSS com `@font-face { src: url(arquivo-local) }` + `font-weight: weight_css` + `letter-spacing` + `color` (+ `font-size` se for o shell).
6. **Não** substituir por CDN Google Fonts — o arquivo local é a fonte da verdade.
7. Reportar `font`, `weight_css`, `letter_spacing`, `color`, `score`, path local + path do log de sobreposição.
