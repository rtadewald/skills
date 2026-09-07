# Components

<<<<<<< ours
Leia este arquivo somente depois da aprovação de Foundations.

## Definição

Components são as **peças completas do Design System**. Eles combinam os átomos aprovados — Colors, Typography e Spacing — com estrutura, acabamento, assets, estados e comportamento. É aqui que a linguagem deixa de ser matéria-prima e passa a assumir forma concreta.

Inclua somente componentes existentes na fonte ou indispensáveis para reproduzir os Layouts aprovados: botões, cards, inputs, badges, navegação, tabelas, tabs, modais e equivalentes. Uma referência com navbar, botões e cards não precisa ganhar uma coleção genérica de controles.
=======
Leia este arquivo somente depois de implementar e verificar Foundations.

## Definição

Components são as **peças completas do Design System**. Eles combinam os átomos extraídos — Colors, Typography e Spacing — com estrutura, acabamento, assets, estados e comportamento. É aqui que a linguagem deixa de ser matéria-prima e passa a assumir forma concreta.

Inclua somente componentes existentes na fonte ou indispensáveis para reproduzir os Layouts extraídos: botões, cards, inputs, badges, navegação, tabelas, tabs, modais e equivalentes. Uma referência com navbar, botões e cards não precisa ganhar uma coleção genérica de controles.
>>>>>>> theirs

Use `data-ds-section="component"`, `data-component`, `data-variant` e `data-status`. Variações que compartilham a mesma estrutura devem permanecer no mesmo componente, como `card--default`, `card--glass` e `card--interactive`.

## Aparência completa

Documente cada componente com o acabamento que o torna reconhecível:

- radius e formato;
- borders, dividers, rim lights e opacidade;
- shadows, elevation e glow;
- backgrounds, gradients, glass, blur, texture, noise, masks e blend modes;
- iconografia, imagens, ilustrações e outros assets próprios; e
- estados visuais e comportamento.

Essas propriedades não viram Foundations. Um glass card deve demonstrar diretamente sua combinação de background, transparência, border, backdrop blur, shadow, radius e hover.

## Assets dentro do componente

<<<<<<< ours
Ícones, SVGs, imagens, texturas, objetos 3D ou efeitos procedurais pertencem ao componente quando fazem parte dele. Mantenha os arquivos em `assets/`, mas demonstre e explique seu uso dentro do preview do componente. Preserve arquivos e código do HTML original; numa entrada por imagem, marque a reconstrução como `inferred` ou `suggested`.
=======
Ícones, SVGs, imagens, texturas, objetos 3D ou efeitos procedurais pertencem ao componente quando fazem parte dele. Mantenha os arquivos em `assets/`, mas demonstre e explique seu uso dentro do preview. Preserve os arquivos, classes, código e dependências do HTML original.
>>>>>>> theirs

Escolha a implementação mais simples capaz de preservar o resultado:

```text
CSS → SVG → imagem → Canvas → WebGL / Three.js
```

Não transforme um glow simples em shader nem descarte um asset distintivo para substituí-lo por placeholder.

## Variantes e estados

<<<<<<< ours
Mostre variantes e estados observados: default, hover, active, focus, disabled, loading, erro ou sucesso. Um estado necessário mas invisível numa screenshot pode ser criado como `suggested`; nunca o apresente como extraído.
=======
Mostre variantes e estados existentes no HTML ou em seu CSS: default, hover, active, focus, disabled, loading, erro ou sucesso. Inspecione selectors e scripts mesmo quando o estado não estiver ativo ao abrir a página. Não crie estados ausentes.
>>>>>>> theirs

Cada preview deve usar o HTML, as classes, o CSS, o JS e os assets reais. A documentação e a implementação são a mesma coisa.

## Motion do componente

O catálogo representa dois tipos de motion:

### Ambient motion

Animações que continuam acontecendo sem interação: floating, rotação lenta, partículas, glow pulsante, gradiente em movimento, noise, mesh, blobs, background animado ou idle 3D.

### Interaction motion

Animações disparadas por ação ou mudança de estado: hover, press, click, focus, accordion, tabs, dropdown, abertura e fechamento de modal, drag, tilt, pointer tracking ou cursor interaction.

<<<<<<< ours
Toda motion documentada deve executar no próprio preview, com duração, easing e gatilho quando conhecidos. Em HTML, reutilize CSS animations, `@keyframes`, transitions, listeners, Canvas, WebGL, Three.js e dependências existentes. Em imagem, não há evidência de movimento: qualquer ambient ou interaction motion criada deve receber `data-status="suggested"`.

Não implemente agora transições entre páginas, rotas, telas ou grandes contextos. Elas pertencem a uma evolução futura do sistema. Abrir um modal ou alternar uma tab continua sendo Interaction motion porque responde a uma ação local.

## Antes do gate de Components

Confirme que:

- cada componente combina Foundations já aprovadas;
- acabamento e assets aparecem no componente proprietário;
- variantes compartilham uma estrutura coerente;
- motions estão classificadas somente como Ambient ou Interaction;
- movimentos observados rodam no catálogo e sugestões estão identificadas; e
- não foram criadas transições entre telas.

Mostre Components e aguarde aprovação antes de ler `layouts.md`.
=======
Toda motion documentada deve executar no próprio preview, com sua duração, easing e gatilho. Reutilize CSS animations, `@keyframes`, transitions, listeners, Canvas, WebGL, Three.js e dependências existentes. Não invente movimento que não esteja implementado no HTML.

Não implemente agora transições entre páginas, rotas, telas ou grandes contextos. Elas pertencem a uma evolução futura do sistema. Abrir um modal ou alternar uma tab continua sendo Interaction motion porque responde a uma ação local.

## Verificação de Components

Confirme que:

- cada componente combina Foundations já extraídas;
- acabamento e assets aparecem no componente proprietário;
- variantes compartilham uma estrutura coerente;
- motions estão classificadas somente como Ambient ou Interaction;
- movimentos observados rodam no catálogo; e
- não foram criadas transições entre telas.

Depois da verificação, continue diretamente para `layouts.md`.
>>>>>>> theirs
