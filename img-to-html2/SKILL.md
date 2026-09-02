---
name: img-to-html2
description: >-
  Image→HTML v2: wireframe ASCII tipado + aprovação do usuário + detecção de
  fontes (fal-ai OCR + Gemini 3.1 Pro via OpenRouter) → typography.css +
  index.html shell p/ validar tipografia. Use when the user mentions img-to-html2.
disable-model-invocation: true
---

# Img → HTML 2

Pipeline em **duas etapas** com **gate de aprovação** entre elas.

```
reference → wireframe.txt → [usuário aprova] → crops + Gemini 3.1 Pro → typography.css + index.html (shell)
```

Saída base: `design-systems/<slug>-regions/`

---

## Etapa 1 — Wireframe ASCII tipado

**Sem Moondream / boxes / crops nesta etapa.**

Entrega: `wireframe.txt` — planta ASCII **fechada**, com **tags tipadas** (mesmo id de tag = mesmo estilo na etapa 2).

### Estilo do quadro

- Um retângulo externo; largura fixa (~78–88 cols); linhas alinhadas.
- Espaço: 1 linha em branco entre seções grandes; dentro da região, ar leve (não esmagar).
- Sem prosa, NOTES, legendas longas, cores.
- Texto **ilegível** → `[t2: …]` — **não inventar** latin falso.

### Regiões (caixas)

Rótulo **na borda superior** da caixa.

| Borda | Uso |
|-------|-----|
| `nav` | chrome superior |
| `hero` | bloco principal |
| `media` | coluna/área só de arte |
| `card` / `card2` / `card3`… | mesmo visual = mesmo tipo; variante = `card2` |
| `quote` | balão / depoimento |
| `form` | formulário |
| `rail` | coluna lateral de métricas |
| `section` | faixa genérica |

### Tags de elemento (vocabulário fechado)

Todo texto visível entra **dentro** de uma tag. Nada solto.

| Tag | Significado |
|-----|-------------|
| `[h1:`…`]` `[h2:`…`]` `[h3:`…`]` | Títulos |
| `[t1:`…`]` `[t2:`…`]` `[t3:`…`]` | Corpo / meta / micro — **mesmo id = mesma tipografia** |
| `[btn:`…`]` `[btn2:`…`]` | Botões — **mesmo id = mesmo estilo** |
| `[lnk:`…`]` | Link (nav) |
| `[in:`…`]` | Placeholder / texto de input — **também entra na detecção de fonte** |
| `[ico:`…`]` | Ícone |
| `[img:`…`]` | Raster / 3D |
| `[av:`…`]` | Avatar |
| `[chart:`…`]` | Gráfico |

Botão com ícone: `[btn: [ico:plus] View Star Map]`.  
`btn` vs `btn2`: dois estilos claros (sólido vs ghost). Terceiro → `btn3`.

Referência de densidade: [`references/wireframe.example.txt`](references/wireframe.example.txt)

### Output etapa 1

```
design-systems/<slug>-regions/
  reference.[ext]
  wireframe.txt
```

### Fluxo etapa 1

1. Pasta + copiar `reference.*`
2. Read imagem → `wireframe.txt`
3. Mostrar path + resumo ao usuário. **Parar.**

---

## Gate — Aprovação do wireframe

**Não avance para etapa 2 sem aprovação explícita do usuário.**

Apresente o `wireframe.txt` (ou diff) e pergunte se a estrutura, tags e textos estão corretos. Só continue quando o usuário confirmar (ex.: “aprovado”, “pode seguir”, “ok”).

Correções pedidas → editar `wireframe.txt` → mostrar de novo → aguardar nova aprovação.

---

## Etapa 2 — Detecção de fontes + shell tipográfico

Objetivo: identificar **uma fonte por role tipográfico** do wireframe (inclui `in`), salvar em `typography.css` e montar um `index.html` **simples** (casca) para validar visualmente se as fontes batem com o mock.

Skills / deps auxiliares:

- **`fal-ai`** — Florence-2 `ocr-with-region` (bbox por label); ver [`fal-ai/references/florence-ocr.md`](../fal-ai/references/florence-ocr.md)
- **OpenRouter** — `google/gemini-3.1-pro-preview` (visão) p/ inferir Google Font + peso; chave `OPENROUTER_API_KEY` (cwd `.env` ou `~/.env`)
- Script local: **`scripts/crop_text.py`** (OCR + crops deste pipeline)

**Não** usar a skill [`find-font`](../find-font/SKILL.md) neste pipeline (fica disponível avulsa).

### Roles a detectar

Extrair do `wireframe.txt` todos os **ids de tag com texto** que aparecem:

`h1` `h2` `h3` `t1` `t2` `t3` `lnk` `btn` `btn2` `in` …

- **Uma detecção por id** — amostra OCR = tag **mais longa** daquele id (desde que seja **uma linha visual**; headline em 3 linhas = 3 tags `[h1:]`, não uma concatenada)
- **Uma frase por linha** no wireframe — nunca juntar linhas visuais distintas numa tag
- Repetições do mesmo id **não** geram novas detecções
- `[ico:` / `[img:` / `[chart:` / `[av:` → fora do escopo de fonte
- **`[in:`** → **entra** (placeholder de input tem tipografia própria)

### 2.1 — Bboxes + crops (Florence-2 OCR, **1 call por imagem**)

**Usar só** `fal-ai/florence-2-large/ocr-with-region`. **Não** Moondream detect/segment para tipografia.

```bash
uv run ~/.agents/skills/img-to-html2/scripts/crop_text.py \
  --project design-systems/<slug>-regions \
  --overlay
```

O script:
1. Lê `wireframe.txt` → `{ role: [frases…] }` — **uma frase por tag/linha**; ignora `[ico:` embutido; **inclui `in`**
2. **Uma** chamada OCR na `reference.*` → `typography/ocr-with-region.json`
3. Por role: tenta cada frase do wireframe da **mais longa para a mais curta**; prefere **match exato** (score 1.0), senão a de maior score
4. Bbox px: `[x, y, x+w, y+h]` + pad 2px → crop PIL
5. Grava `{role}.png`, `{role}-hi.png`, `font-meta.json`, `ocr-matches.json`
6. Com `--overlay`: `typography/crops-overlay.png` (debug)

Chamada directa (referência):

```python
import fal_client
url = fal_client.upload_file("reference.jpg")
raw = fal_client.subscribe(
    "fal-ai/florence-2-large/ocr-with-region",
    arguments={"image_url": url},
)
```

Schema / match / pricing: [`fal-ai/references/florence-ocr.md`](../fal-ai/references/florence-ocr.md)

Regras:
- Wireframe: **uma frase por linha visual** — headline em 3 linhas = 3 tags `[h1:]`, não uma tag concatenada
- Wireframe localiza o bbox; Florence devolve `ocr_label` (debug / meta)
- Tags partidas por colunas `│` no ASCII quebram o parser — manter cada tag numa linha
- `[btn: … [ico:…]]` → wireframe sample = só o texto (`LAUNCH MISSION`), OCR devolve bbox só dos glifos
- Se role falhar match → corrigir string no wireframe ou escolher outra amostra da mesma tag

### 2.2 — Saída dos crops

Dois PNGs por role em `typography/crops/`:

| Arquivo | Uso |
|---------|-----|
| `{role}.png` | OCR bbox (+ pad 2px) — **só texto**; **este** vai para o Gemini |
| `{role}-hi.png` | invert / upscale / borda — **não** enviar ao Gemini (só debug opcional) |

Salvar `typography/font-meta.json` com `{ role: { text, box_px, crop, crop_hi, wireframe_sample } }`.

**`text`** = **`ocr_label` exato** do Florence (case-sensitive; debug).

**`wireframe_sample`** = frase do wireframe usada só para localizar o bbox (debug).

### 2.3 — Gemini 3.1 Pro via OpenRouter (paralelo)

Para **cada** role em `font-meta.json`, em **paralelo**:

1. Ler `{role}.png` (**crop original**, nunca `-hi`)
2. `POST https://openrouter.ai/api/v1/chat/completions` com:
   - `model`: **`google/gemini-3.1-pro-preview`**
   - `OPENROUTER_API_KEY` do env / `~/.env`
   - `content`: texto + `image_url` (data-URL `data:image/png;base64,…`)
3. Prompt (fixo o sentido):

```
This is a tight single-line crop of UI text from a design mock.
Identify the most likely Google Font family and the CSS font-weight.
Reply with ONLY compact JSON (no markdown):
{"family":"Poppins","weight":500,"confidence":0-100,"alternatives":["Montserrat","DM Sans"],"notes":"brief glyph clues"}
Prefer real Google Fonts names. weight must be a number (100–900).
```

4. Parsear o JSON de cada resposta (tolerar fence \`\`\`json se vier)
5. Salvar tudo em `typography/gemini-font-results.json`:

```json
{
  "btn2": {
    "text": "Summarize Text",
    "crop": "typography/crops/btn2.png",
    "box_px": [440, 375, 521, 392],
    "result": {
      "family": "Poppins",
      "weight": 500,
      "confidence": 85,
      "alternatives": ["Montserrat", "DM Sans"],
      "notes": "…"
    }
  }
}
```

6. **Só depois** de **todos** os roles retornarem → escrever `typography.css` + `index.html`

Se um role falhar (timeout / JSON inválido): anotar `error` no results, usar fallback `family: "Inter"`, `weight: 400`, e seguir — não travar o pipeline.

### 2.4 — typography.css

Arquivo canônico da tipografia (o `index.html` **só** importa este CSS — sem duplicar `font-family` / `font-weight` inline).

Path: `design-systems/<slug>-regions/typography.css`

```css
/* Google Fonts CDN — famílias + pesos inferidos pelo Gemini */
@import url("https://fonts.googleapis.com/css2?family=Poppins:wght@500&family=…&display=swap");

/* Roles tipográficos (= ids de tag do wireframe) */
.h1 {
  font-family: "Figtree", sans-serif;
  font-weight: 500;
  font-size: 34px; /* box_px height */
}

.in { … }
.btn2 { … }
```

Regras:
- `family` / `weight` ← Gemini; se null / erro → `Inter` / `400`
- **Google Fonts CDN** (`@import` com famílias **únicas** + pesos usados) — não baixar TTF local neste pipeline
- Uma classe por role: `.h1`, `.t1`, `.btn`, `.btn2`, `.in`, …
- `font-size` ← altura do bbox OCR (`box_px[3] - box_px[1]`)
- `color` / `letter-spacing` — **não** inventar; omitir salvo medição explícita
- Comentário no topo: role → fonte → weight → confidence
- Bruto fica em `typography/gemini-font-results.json`
- No `index.html`, **não** sobrescrever `font-family` / `font-weight` / `font-size` das classes de role (só layout/chrome)

### 2.5 — index.html (shell tipográfico)

Recriar **casca simplificada** do mock — **não** pixel-perfect ainda:

- Viewport fixo = canvas do `reference`
- Fundo externo preto/cinza escuro; **box principal** (`.shell`) com border-radius + borda sutil
- Caixinhas `.box` / `.ph` nos slots `[img:]` / `[chart:]` (sem assets reais)
- **Todos os textos** do wireframe, nas posições aproximadas do layout — wireframe + referência servem só para **validar** se as fontes bateram
- Placeholders de input usam classe `.in` (fonte do Gemini)
- `<link rel="stylesheet" href="typography.css">` — tipografia **só** daí (não redefinir `.h1`/`.t1`/`.in`/… no `<style>` do index)
- Layout / chrome / cores de UI podem ficar no `<style>` do index; classes de role só tipográficas
- **Caixa literal do wireframe** no HTML — sem `text-transform` global; cada string com a capitalização exata do wireframe/OCR
- CTAs: classes separadas para `btn` vs `btn2` (fontes podem diferir)
- Acentos do mock quando visíveis na referência

Objetivo: o usuário abre `index.html` lado a lado com `reference.*` e julga **só tipografia** antes de seguir para HTML final.

### Output etapa 2

```
design-systems/<slug>-regions/
  reference.[ext]
  wireframe.txt
  typography.css
  index.html
  typography/
    ocr-with-region.json
    ocr-matches.json
    font-meta.json
    gemini-font-results.json
    crops-overlay.png
    crops/
      h1.png  h1-hi.png
      in.png  in-hi.png
      lnk.png lnk-hi.png
      …
```

### Fluxo etapa 2

1. Listar roles únicos do `wireframe.txt` aprovado (inclui `in` se houver)
2. `crop_text.py` → OCR + crops → `ocr-with-region.json`, `typography/crops/`, `font-meta.json`
3. **Gemini 3.1 Pro** (OpenRouter) em **paralelo** por role, crop **original** → `gemini-font-results.json`
4. Quando **todos** retornarem → escrever `typography.css` (CDN)
5. Escrever `index.html` shell (linkando `typography.css`)
6. Reportar paths + tabela role → family → weight → confidence. **Parar** — aguardar feedback do usuário sobre tipografia.

---

## Chat

- **Após etapa 1:** path do wireframe + pedir aprovação
- **Após etapa 2:** paths + tabela resumo Gemini; pedir se tipografia está ok

## Fora de escopo (por enquanto)

- HTML pixel-perfect / assets raster / QA diff
- Múltiplas rodadas de Gemini sem pedido do usuário
- Detectar fonte de `[ico:` (SVG/CSS na etapa final)
- find-font local (`:8000`) neste pipeline
