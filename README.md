# Skills

Skills que uso nos agentes (Cursor / Claude / Codex). Cada pasta tem um `SKILL.md`.

---

## Telas

Pra inventar e fechar a cara de um app antes de gerar mock.

- [`plan-screen-with-svg`](./plan-screen-with-svg): conversa, 3 propostas com wireframe SVG, depois PNG em `mocks/`
- [`plan-screen-with-ascii`](./plan-screen-with-ascii): o mesmo fluxo, mas a planta vai em ASCII

## Design system

Quando quero tirar a linguagem visual de uma referência e deixar pronta pra implementar. Prefixo: `ds-from-…` / `ds-cards-…`

- [`ds-from-html`](./ds-from-html): HTML monolítico → `design-system.html` limpo + assets
- [`ds-from-img`](./ds-from-img): mock (imagem) → `design-systems/<slug>/` com HTML + CSS
- [`ds-from-svg`](./ds-from-svg): wireframe/mock SVG → `design-systems/<slug>/` com HTML + CSS
- [`ds-cards-from-img`](./ds-cards-from-img): mock → cards com máscara + `sample_cards.py` (mais preciso)
- [`ds-cards-from-img-2`](./ds-cards-from-img-2): o mesmo, fluxo **rápido** (bbox + PIL na original, sem crops/script)
- [`img-to-html`](./img-to-html): mock → `measure.py` + vocab fechado → `index.html` + render/diff 2–3× (assets via OpenRouter)

## Imagem

Gerar, converter, brincar com PNG.

- [`to-img`](./to-img): qualquer pedido → n PNGs em paralelo (OpenRouter, gpt2 @ 1K) em `mocks/`
- [`to-ascii`](./to-ascii): mock PNG → planta ASCII (`.txt` ao lado)
- [`to-svg`](./to-svg): mock PNG → wireframe SVG (`.svg` ao lado)
- [`openrouter-img`](./openrouter-img): CLI dos modelos de imagem do OpenRouter
- [`nano-banana-pro`](./nano-banana-pro): gerar/editar imagem com Nano Banana Pro (Gemini)

## Motion e mídia

Mexer em animação, áudio e vídeo.

- [`animate`](./animate): decide e implementa motion com critério (não só “coloca um fade”)
- [`mediabunny`](./mediabunny): áudio/vídeo com a lib Mediabunny

## Planejamento e entrega

Afiando ideia, quebrando em tickets, passando o bastão.

- [`grill-me`](./grill-me): entrevista dura pra afiar plano ou design
- [`to-tickets`](./to-tickets): plano/spec/conversa → tickets com dependências
- [`handoff`](./handoff): compacta a conversa pra outro agente continuar

## Utilitários

Coisas soltas que salvam tempo.

- [`context7-mcp`](./context7-mcp): puxa docs atuais de libs via Context7 (em vez de chutar de memória)
