---
name: img-to-html
description: >-
  Recria um mock de UI (imagem) como HTML + CSS + JS estáticos (sem framework),
  em etapas com aprovação do usuário: wireframe SVG tipado → background → nav +
  cards pixel-perfect → ícones/imagens (GPT Image 2) → fontes. Use when the user
  mentions img-to-html or asks to recreate a UI mock as HTML.
disable-model-invocation: true
---

# Img → HTML

## O que é

Skill para transformar um **mock de interface** (PNG/JPG/WebP) numa **recriação HTML** fiel, passo a passo.

**Entrada:** uma imagem de referência (anexada no chat, path, ou URL). Se faltar, peça.

**Saída:** pasta `design-systems/<slug>/` com a referência copiada, o wireframe, o **`index.html`** e uma pasta **`assets/`** com o CSS, o JS e as mídias geradas.

`<slug>` = nome curto do mock em kebab-case (ex.: `chatgpt-glass-dash`). Se o usuário não indicar, derive do nome do arquivo ou pergunte.

## Por que em etapas

Recriar a tela inteira de uma vez falha (cores, glass, ícones e fontes misturam erros). O fluxo é **bottom-up**: cada camada só começa depois da anterior **aprovada** pelo usuário. O wireframe define *o que* existe; o HTML implementa *como* fica.

## Pipeline

```
1. reference → wireframe.svg           → [usuário aprova]
2. index.html + styles.css: só o bg    → [usuário aprova]
3. nav + cards (pixel-perfect)         → [usuário aprova]
4. ícones / imagens / gifs (gpt2)      → [usuário aprova]
5. fontes (família + peso)             → [usuário aprova]
```

## Gate de aprovação (vale para todas as etapas)

Ao terminar uma etapa:

1. Mostre o resultado (path + `open` no macOS e/ou screenshot no browser).
2. Pergunte se está correto / se mudaria algo.
3. **Pare.** Não inicie a etapa seguinte.

Só avance com confirmação explícita ("aprovado", "pode seguir", "ok"). Se o usuário pedir correção: edite, mostre de novo, aguarde nova aprovação.

## Layout da pasta

```
design-systems/<slug>/
  reference.[ext]      # cópia da imagem de entrada
  wireframe.svg        # planta tipada (etapa 1)
  index.html           # markup — só estrutura, sem <style>/<script> inline
  assets/
    styles.css         # todo o CSS
    app.js             # todo o JS (só se o mock precisar de comportamento)
    crops/             # recortes da reference
    *.png / *.mp4 …    # imagens, ícones, vídeos gerados
```

### Stack: HTML + CSS + JS separados

**Sem build, sem bundler, sem framework, sem `node_modules`, sem dev server** — abre com `open index.html` e funciona.

- `index.html` carrega os outros dois: `<link rel="stylesheet" href="assets/styles.css">` no `<head>` e `<script src="assets/app.js" defer></script>`.
- **Nada de `<style>` ou `<script>` inline** no HTML, e nada de `style="…"` nos elementos. Todo CSS vive em `assets/styles.css`.
- Um `styles.css` só. Se ele passar de ~1500 linhas, aí sim quebre por região (`assets/nav.css`, `assets/cards.css`) e adicione os `<link>` correspondentes — mas o default é um arquivo.
- `assets/` é a única pasta auxiliar: CSS, JS, imagens, ícones, vídeos e os crops moram todos lá.
- Sem Tailwind, sem CDN de framework. CSS puro, com **custom properties** no `:root` para o design system (cores, radius, sombras, tipografia).
- Cada região do wireframe vira uma **classe CSS** (`.nav`, `.hero`, `.card`, `.card2`, …) e cada tag tipada vira uma classe utilitária (`.h1`, `.t2`, `.btn`, `.lnk`, …). Mesmo id no wireframe = mesma classe.
- Conteúdo repetido (lista de cards, itens de nav) é escrito direto no HTML. Só crie `app.js` se o mock exigir comportamento real; não gere markup por loop de JS.
- Paths sempre relativos: `assets/{id}.png`.

Se o usuário pedir React/Vite explicitamente, aí sim mude a stack.

---

## Etapa 1 — Wireframe SVG tipado

Objetivo: a **planta estrutural** da tela — quais regiões existem e que texto tem dentro delas. Nada além disso.

O wireframe é o **contrato** com o HTML: cada região e cada tag tipada vira depois uma **classe CSS** (mesmo id = mesmo visual). O que importa aqui é **completude**, não fidelidade geométrica — omissão vira bloco faltando; caixa 20px fora do lugar não custa nada.

### Rápido e leve (regra da etapa)

- **Entregue rápido.** Uma passada escrevendo o SVG olhando a referência, **uma** revisão, e mostre ao usuário.
- **Não meça.** Nada de crop, OCR, eyedropper, sample de pixel, régua ou cálculo de coordenada. Posições e tamanhos são estimados no olho.
- **Não desenhe.** Sem ícones vetorizados, sem gráfico simulado, sem sombra/gradiente/curva. Só `rect` + `text`.
- Se estiver hesitando entre dois valores de `x`/`y`/`width`, escolha um e siga.

### Revisão única (antes do gate)

Uma varredura da referência, região por região, checando só isto:
  
1. Toda superfície visível virou **caixa com label de região**?
2. Todo texto/controle visível está dentro de uma **tag**?
3. Cards com superfície própria dentro de outro card estão **aninhados** (não achatados em texto solto)?
4. Item de nav **ativo** está como `[btn:]`, não `[lnk:]`?

Corrigiu o que faltava → abre o SVG → **gate**. Não faça uma terceira passada por conta própria; iterações extras vêm do feedback do usuário.

### Estilo do SVG

- `viewBox` proporcional ao canvas da referência (ex.: `0 0 1440 900` ou o aspect da imagem).
- Só wireframe: cinza, stroke, labels. Sem cores de produto, sem tipografia premium, sem fills decorativos.
- Caixas = regiões; label da região na borda superior (canto esquerdo).
- Texto do mock = o essencial do que há ali, dentro de **tags tipadas**. Texto **ilegível** → `[t2: …]` — **não inventar** latin falso.
- Nos labels do SVG, use letras/números básicos. Encoding errado quebra o XML no browser.
- Ar leve entre seções; não esmagar conteúdo dentro das caixas.
- Sem prosa, NOTES ou legendas longas fora das tags.

### Regra de componente (obrigatória)

Tudo que for virar um bloco com classe própria no HTML **precisa de marcação própria**:

1. **Caixa com label de região** (`nav`, `card`, `card4`, `media`, …) na borda superior.
2. **Conteúdo tipado** dentro dela (`[h3:]`, `[btn:]`, `[chart:]`, …) — nada de texto solto.
3. Caixa desenhada **sem** label de região = erro (ex.: painel de gráfico sem nome `card5`).
4. Estado visual distinto = tipo distinto (nav ativo ≠ link; KPI card ≠ item de lista ≠ painel de chart).

### Regiões (caixas)

| Região | Uso |
|--------|-----|
| `nav` | chrome superior / sidebar de navegação |
| `hero` | bloco principal |
| `media` | coluna/área só de arte |
| `card` / `card2` / `card3`… | mesmo visual = mesmo tipo; variante visual = próximo id (`card2`, `card3`…) |
| `quote` | balão / depoimento |
| `form` | formulário |
| `rail` | coluna lateral de métricas |
| `section` | faixa genérica (ex.: wrapper de analytics) |

**Aninhamento:** regiões podem conter regiões. Cards dentro de cards são obrigatórios quando o mock mostra itens com superfície própria (ex.: `card2` = "Today Schedule"; cada job HVAC/Plumbing = `card4` com caixa + label próprios). Tooltip flutuante, dock de ícones, painel de chart — se parecerem componente, ganham caixa + tipo.

### Tags de elemento (vocabulário fechado)

Todo texto/controle visível entra **dentro** de uma tag. Nada solto. **Mesmo id de tag = mesma classe CSS** (tipografia, botão, etc.).

| Tag | Significado |
|-----|-------------|
| `[h1:`…`]` `[h2:`…`]` `[h3:`…`]` | Títulos |
| `[t1:`…`]` `[t2:`…`]` `[t3:`…`]` | Corpo / meta / micro |
| `[btn:`…`]` `[btn2:`…`]` `[btn3:`…`]` | Botões — **mesmo id = mesmo estilo**. Nav ativo (pill) ≠ CTA largo ≠ ghost/ícone → `btn` / `btn2` / `btn3` |
| `[lnk:`…`]` | Link de nav **inativo** (sem pill / estado ativo) |
| `[in:`…`]` | Placeholder / texto de input |
| `[ico:`…`]` | Ícone |
| `[img:`…`]` | Raster / 3D |
| `[av:`…`]` | Avatar |
| `[chart:`…`]` | Gráfico |

Botão com ícone: `[btn: [ico:plus] View Star Map]`.
Nav: item **ativo** → `[btn: [ico:grid] Overview]`; demais → `[lnk: …]`.

Uma frase por linha visual — headline em 3 linhas = 3 tags `[h1:]`, não uma concatenada.

**Referência canônica** (densidade, aninhamento, btn ativo, card5 de charts): [`references/wireframe.example.svg`](references/wireframe.example.svg) — ServiceFlow ops dashboard. Espelhe esse nível de marcação.

### Fluxo etapa 1

1. Criar `design-systems/<slug>/` e copiar a imagem para `reference.[ext]`.
2. Ler a imagem → escrever `wireframe.svg` de uma vez (example acima como régua de completude).
3. Revisão única (checklist acima).
4. Abrir o SVG → **gate**.

---

## Etapa 2 — Background

Pré-requisito: wireframe aprovado.

1. Criar `index.html` (esqueleto mínimo com o `<link>` para `assets/styles.css` e `<body>` vazio) e `assets/styles.css` (reset curto + `:root` com as custom properties que já der para definir).
2. Recriar **somente** o fundo da tela (gradiente, texture, blobs, cor sólida — o que a `reference` tiver).
3. Sem navbar, sem cards, sem conteúdo.
4. Abrir o arquivo no browser (`open index.html`), comparar com a referência.
5. **Gate.**

---

## Etapa 3 — Nav + cards (pixel-perfect)

Aqui entra todo o conteúdo do wireframe (markup no `index.html`, estilo no `assets/styles.css`): primeiro o chrome (`nav` — top bar e/ou sidebar), depois cada tipo de card (`card`, `card2`, …). Um gate só, no fim.

Meta: cada superfície **indistinguível** da referência. Iterar medindo, não chutando:

- cores (eyedropper / sample de pixels na `reference`)
- gradientes (ângulo + stops)
- transparência (glass vs opaco)
- bordas / rim light (direção, soft vs hairline)
- glow / sombra externa e inset
- radius, padding, espaçamento entre elementos
- tipografia **provisória** (família/peso finais = etapa 5)

Fluxo por superfície (nav primeiro, depois card a card):

1. Crop da referência (ou lab side-by-side no browser).
2. Amostrar pixels (fill, rim TL/BR, texto, meta).
3. Escrever o markup no `index.html` e a classe em `assets/styles.css`; valores reutilizados viram custom property no `:root`.
4. Screenshot recreate vs crop; ajustar até bater.

Ícones e imagens continuam placeholder até a etapa 4. Com nav e todos os cards batendo → **gate**.

---

## Etapa 4 — Imagens, ícones, gifs

Para cada `[ico:]` / `[img:]` / `[av:]` (e arte relevante) marcado no wireframe:

1. Crop na `reference` → `assets/crops/{id}.png`.
2. Regenerar com **GPT Image 2** via OpenRouter (`gpt2`), PNG com **fundo transparente**:

```bash
uv run ~/.agents/skills/openrouter-img/scripts/generate_image.py \
  --prompt "Recreate this UI icon/asset exactly. Flat, clean edges. Transparent background. No extra padding, no mockup frame." \
  --input-image design-systems/<slug>/assets/crops/{id}.png \
  --filename design-systems/<slug>/assets/{id}.png \
  --model gpt2 --resolution 1K --aspect-ratio 1:1
```

Rodar a partir do cwd do repo de skills (ou paths absolutos). Ajustar `--aspect-ratio` ao crop. Requer `OPENROUTER_API_KEY` (`.env` do projeto ou `~/.env`).

3. Encaixar no HTML via `<img src="assets/{id}.png">` (ou `background-image`); comparar com a ref.
4. Se falhou: novo prompt / nova geração até o agente julgar que acertou.
5. Conjunto pronto → **Gate.**

---

## Etapa 5 — Fontes

1. Para cada tag tipado distinto (`h1`…`t3`, `btn`, `lnk`, …), detectar **família + peso**:
   - preferir a skill/API local `find-font` (crop de **uma linha**, parâmetro `text=` case-sensitive com o glyph exato); **ou**
   - julgamento visual + Google Font mais próximo.
2. Aplicar: `<link>` do Google Fonts no `index.html` (ou `@font-face` no topo do `styles.css`) + `font-family` / `font-weight` na classe de cada tag.
3. Mesmo id de tag = mesma tipografia.
4. Screenshot → **Gate.**

---

## Não fazer

- Pular gates ou "adiantar" várias etapas num único turno.
- Na etapa 1: medir, croppar, fazer OCR, desenhar arte, ou refinar o wireframe além da revisão única.
- Inventar textos ilegíveis no wireframe.
- Desenhar caixa de componente sem label de região, ou achatar cards-filho em texto solto dentro do pai.
- Marcar nav ativo como `[lnk:]` (use `[btn:]` / variante).
- Tratar ícones/imagens com Lucide/placeholder "parecido" quando a etapa 4 pede asset gerado da ref.
- Escrever CSS inline (`<style>` no HTML ou `style="…"` no elemento) — todo estilo vai para `assets/styles.css`.
- Criar `package.json`, bundler, framework ou espalhar arquivos fora de `assets/`.
