# Skills

Skills que uso nos agentes (Cursor / Claude / Codex). Cada pasta tem um `SKILL.md`.

---

## Telas

Pra inventar e fechar a cara de um app antes de gerar mock.

- [`plan-screen`](./plan-screen): conversa, uma tela ou fluxo com wireframes ASCII tipados por padrão (SVG sob pedido), depois PNGs em `mocks/`

## Design system

Quando quero tirar a linguagem visual de uma referência e deixar pronta pra implementar. Prefixo: `ds-from-…` / `ds-cards-…`

- [`ds-from-html`](./ds-from-html): HTML de referência → `design-system.html` (pattern library viva, classes/assets originais)
- [`extract-ds`](./extract-ds): `index.html` existente → catálogo direto com Overview, Foundations, Components e Layouts
- [`clean-ds-from-html`](./clean-ds-from-html): HTML → design system limpo com assets extraídos
- [`ds-from-react`](./ds-from-react): aplicação React hospedada → `design-system.html` (pattern library viva, UI e arquivos reais)
- [`ds-from-img`](./ds-from-img): mock (imagem) → `design-systems/<slug>/` com HTML + CSS
- [`ds-from-svg`](./ds-from-svg): wireframe/mock SVG → `design-systems/<slug>/` com HTML + CSS
- [`ds-cards-from-img`](./ds-cards-from-img): mock → cards com máscara + `sample_cards.py` (mais preciso)
- [`ds-cards-from-img-2`](./ds-cards-from-img-2): o mesmo, fluxo **rápido** (bbox + PIL na original, sem crops/script)
- [`img-to-html`](./img-to-html): mock → **wireframe ASCII tipado + plano** → **aprovação** → `index.html` + `assets/styles.css` (sem framework): fundo completo (CSS/imagens) → componentes com fontes → assets restantes → revisão final, cada etapa aplicável com gate
- [`img-to-html2`](./img-to-html2): wireframe ASCII tipado → **aprovação** → detect fontes (fal-ai OCR + Gemini 3.1 Pro / OpenRouter) → `typography.css` + `index.html` shell
- [`img-to-html3`](./img-to-html3): toolbox (fontes, cores pixel, PNG, SVG/ASCII) dirigida por prompt humano — sem pipeline fixo

## Imagem

Gerar, converter, brincar com PNG.

- [`to-img`](./to-img): qualquer pedido → n PNGs em paralelo (OpenRouter, gpt2 @ 1K) em `mocks/`
- [`to-wireframe`](./to-wireframe): imagem ou brief de tela → wireframe **tipado** e aninhado em SVG ou ASCII (`format=svg|ascii`)
- [`openrouter-img`](./openrouter-img): CLI dos modelos de imagem do OpenRouter
- [`nano-banana-pro`](./nano-banana-pro): gerar/editar imagem com Nano Banana Pro (Gemini)
- [`fal-ai`](./fal-ai): fal.ai Model API (auth/upload/subscribe) + Moondream detect/query/point/caption/segment

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

- [`find-font`](./find-font): crop de texto (1 linha) → TTF local + weight_css/color/overlay via API (`127.0.0.1:8000/find-font`, exige `text=`) — avulsa (não é o default do img-to-html2)
- [`context7-mcp`](./context7-mcp): puxa docs atuais de libs via Context7 (em vez de chutar de memória)
