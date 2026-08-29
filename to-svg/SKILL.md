---
name: to-svg
description: >-
  Analisa uma imagem de mock de app e grava um wireframe SVG no mesmo diretório,
  com o mesmo nome e extensão .svg. Use when the user mentions to-svg.
disable-model-invocation: true
---

# To SVG

Olhe a imagem do mock de app, desenhe um **wireframe SVG** da tela e grave ao lado.

## Fluxo

1. Use o path da imagem que o usuário passou (ou a imagem da conversa). Se faltar, peça.
2. Leia a imagem e identifique regiões, hierarquia, textos visíveis e o momento da UI.
3. Desenhe um wireframe SVG: estrutura + intenção — cinza, stroke, labels. Caixas = regiões; texto = o essencial do que há ali (sem copiar pixel a pixel, sem cores de produto, sem tipografia premium).
4. Grave no **mesmo diretório** da imagem, **mesmo nome**, extensão `.svg`.

```
mocks/1-a.png  →  mocks/1-a.svg
foo/hero.png   →  foo/hero.svg
```

**Formato do SVG:**
- Comece com `<?xml version="1.0" encoding="UTF-8"?>`.
- `viewBox` 16:9 (ex.: `0 0 1440 810`).
- Destaque a região ativa com stroke mais grosso / fill um pouco mais escuro.
- Elementos fora da janela (ex.: personagem 3D) em linha tracejada.
- Nos labels, use so letras/numeros basicos (sem simbolos raros). Encoding errado quebra o XML no browser.

5. Mostre o path (e, no macOS, `open` o arquivo se fizer sentido) e pare.
