# Casca e background do catálogo

<<<<<<< ours
Leia este arquivo imediatamente antes de criar `design-system.html`. Esta passagem estabelece a atmosfera visual e a navegação do catálogo; ainda não implemente Foundations, Components ou Layouts.

## Background fiel à fonte

O background de `design-system.html` deve vir da referência, nunca de uma escolha genérica da UI de documentação.

### Entrada por imagem

Obtenha a cor real com um algoritmo de amostragem, conta-gotas ou leitura de pixels. Inspecione áreas livres de conteúdo e mais de um ponto — como cantos e faixas externas — para não confundir card, glow, compressão ou overlay com a cor do canvas. Determine a cor-base dominante, registre o valor exato em CSS e confira visualmente contra a imagem.

```css
:root {
  --color-background: /* valor medido */;
}
```

Não estime a cor apenas olhando a screenshot. Se o fundo combinar uma cor-base com imagem, gradiente ou efeito, preserve a cor medida como fallback e trate as demais camadas no Component ou Layout responsável.

### Entrada por HTML

Leia o CSS e o estilo computado de `html`, `body` e do root visual da página. Preserve a cor, imagem, gradiente, pseudo-elementos, blend, overlay e demais camadas que realmente formam o background. Reaproveite valores, classes e assets existentes sempre que possível.

Se o HTML tiver uma atmosfera global animada — CSS animation, Canvas, partículas, vídeo, WebGL, Three.js, shader ou outro movimento de fundo — copie sua implementação e dependências já nesta passagem. Inicialize-a em `interactions.js` ou num arquivo dedicado quando a complexidade justificar. O catálogo deve nascer com o mesmo ambiente visual da fonte; não deixe esse efeito para o final.

Efeitos particulares de um card ou de um layout permanecem para suas respectivas etapas.
=======
Leia este arquivo imediatamente antes de criar `design-system.html`. Esta passagem estabelece a atmosfera visual e a navegação; ainda não implemente Foundations, Components ou Layouts.

## Background fiel ao HTML

O background do catálogo deve vir da implementação de origem, nunca de uma escolha genérica da UI de documentação.

Leia o CSS e o estilo computado de `html`, `body` e do root visual. Preserve cor, imagem, gradiente, pseudo-elementos, blend, overlay e todas as camadas que formam o fundo. Reutilize valores, classes e assets existentes sempre que possível.

Se o HTML tiver atmosfera global animada — CSS animation, vídeo, Canvas, partículas, WebGL, Three.js, shader ou outro movimento de fundo — copie sua implementação e dependências já nesta passagem. Inicialize-a em `interactions.js` ou num arquivo dedicado quando a complexidade justificar. O catálogo deve nascer com o mesmo ambiente visual da fonte.

Efeitos particulares de um Component ou Layout permanecem para suas respectivas etapas.
>>>>>>> theirs

## Navegação superior

Crie uma barra horizontal no topo com links para `Overview`, `Foundations`, `Components` e `Layouts`. Ela pode ser sticky ou flutuante na parte superior, com overflow horizontal em viewports estreitos. Não use sidebar nem barra vertical flutuante.

<<<<<<< ours
A barra pertence à UI de documentação. Use classes próprias da casca, sem registrá-la automaticamente como Component extraído. Ela deve permitir navegar por âncoras, indicar a seção ativa quando isso puder ser feito de forma simples e continuar legível sobre o background capturado.
=======
A barra pertence à UI de documentação. Use classes próprias da casca, sem registrá-la automaticamente como Component extraído. Ela deve navegar por âncoras, indicar a seção ativa quando isso puder ser feito de forma simples e continuar legível sobre o background extraído.

A tipografia inicial da casca é provisória. Assim que Typography for implementada, substitua-a pelas famílias e assinaturas tipográficas encontradas no HTML. O catálogo final não deve manter uma fonte de documentação desconectada do sistema extraído.
>>>>>>> theirs

## Verificação inicial

Antes de iniciar Foundations, confirme que:

<<<<<<< ours
- o background-base foi medido na imagem ou lido do HTML;
- efeitos globais do HTML foram preservados e executam sem erros;
- a navegação superior alcança todas as seções previstas; e
- a casca não introduz uma linguagem visual que concorra com a referência.
=======
- o background-base e suas camadas foram lidos do HTML;
- efeitos globais foram preservados e executam sem erros;
- a navegação superior alcança todas as seções previstas; e
- a casca não introduz uma linguagem visual que concorra com a fonte.
>>>>>>> theirs
