---
name: to-ascii
description: >-
  Analisa uma imagem de mock de app e grava a planta em ASCII no mesmo diretório,
  com o mesmo nome e extensão .txt. Use when the user mentions to-ascii.
disable-model-invocation: true
---

# To ASCII

Olhe a imagem do mock de app, desenhe a tela em ASCII e grave ao lado.

## Fluxo

1. Use o path da imagem que o usuário passou (ou a imagem da conversa). Se faltar, peça.
2. Leia a imagem e identifique regiões, hierarquia, textos visíveis e o momento da UI.
3. Desenhe a planta em ASCII: janela com borda (`┌─┐│└─┘`), cada área com nome no topo, o essencial do que há ali (sem copiar pixel a pixel).
4. Grave no **mesmo diretório** da imagem, **mesmo nome**, extensão `.txt`.

```
mocks/1-a.png  →  mocks/1-a.txt
foo/hero.png   →  foo/hero.txt
```

5. Mostre o path e pare.
