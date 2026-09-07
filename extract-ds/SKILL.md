---
name: extract-ds
description: >-
  Extrai de uma página ou projeto HTML existente um catálogo HTML-first de design
  system com Overview, Foundations, Components e Layouts. Use when
  the user mentions extract-ds or asks to derive a design system from HTML.
disable-model-invocation: true
---

# Extract DS

Extraia do HTML existente uma linguagem visual reutilizável e fiel. O design system é composto por `design-system.html`, seu CSS, seu JavaScript quando houver comportamento, e `assets/`; não crie JSON, manifestos ou documentação paralela que possa se desalinhar da implementação.

## Entrada

Aceite somente `html=<path>`: um arquivo HTML local ou o entrypoint de um projeto já funcional, com seus CSS, JavaScript, fontes e assets associados.

Esta skill não analisa imagens e não cria wireframes. Quando a origem for uma imagem, ela deve ser transformada em HTML antes, por exemplo com `$img-to-html`; use o HTML resultante como entrada desta skill.

`<slug>` é um nome curto em kebab-case derivado do projeto ou indicado pelo usuário.

## Resultado

```text
design-systems/<slug>/
  reference.html       # cópia do HTML de entrada, quando for um arquivo isolado
  design-system.html   # catálogo navegável e fonte de documentação
  styles.css           # Foundations, aparência e layouts
  interactions.js      # somente quando houver comportamento ou motion
  assets/              # fontes, imagens, ícones, SVG, 3D e recursos de runtime
```

Preserve o projeto de origem intacto. Copie para o output somente dependências necessárias para o catálogo ou referencie arquivos estáveis do projeto com paths válidos.

O catálogo usa uma barra de navegação **superior e horizontal** para `Overview`, `Foundations`, `Components` e `Layouts`. Ela pode permanecer sticky ou flutuar no topo, mas não deve virar uma sidebar vertical. Assets não são uma categoria: ficam dentro do Component ou Layout que os utiliza e fisicamente em `assets/`.

## Arquitetura canônica

```text
Foundations
├── Typography
├── Colors
└── Spacing

Components
├── Appearance
├── Variants
├── States
├── Assets
├── Ambient motion
└── Interaction motion

Layouts
├── Components
├── Layout-level assets
└── Responsive arrangement
```

Foundations fornecem os átomos. Components materializam esses átomos em peças completas, com acabamento e comportamento. Layouts organizam as peças no espaço e controlam os assets e a responsividade do arranjo. Use essa árvore para classificar a fonte, implementar as seções e revisar o resultado.

## Preparação — inspecionar o HTML

1. Abra ou hospede o HTML com seus CSS, scripts, fontes e assets carregados.
2. Inspecione DOM, stylesheets, CSS custom properties, estilos computados, pseudo-elementos, breakpoints, estados, `@font-face`, imports, imagens, SVG, Canvas, WebGL, Three.js e dependências externas.
3. Observe a página em runtime para encontrar transitions, `@keyframes`, listeners, estados interativos e animações ambientais.
4. Crie um inventário interno mínimo de Foundations, Components e Layouts. Associe cada asset ao Component ou Layout proprietário.
5. Em Typography, enumere todas as famílias e assinaturas tipográficas únicas realmente usadas no DOM: selector/classe, família, peso, tamanho, line-height, letter-spacing e transformação.

Use a implementação como evidência. `observed` é algo comprovado pelo DOM, CSS, JS, asset ou runtime; `inferred` pode descrever apenas função, agrupamento ou nome semântico deduzido da implementação. Não invente componentes, estados ou comportamentos ausentes.

## Construir o catálogo sem interrupções

Gere o `design-system.html` completo em uma única execução, sem gates ou pedidos de aprovação intermediários. Antes de cada passo, leia somente a referência indicada; não carregue as demais por antecipação.

| Momento | Referência a ler | Resultado |
|---|---|---|
| Arquivo inicial, background e navegação | [catalog-shell.md](references/catalog-shell.md) | Casca do catálogo |
| Hero adaptada do `index.html` | [overview.md](references/overview.md) | Overview |
| Átomos reutilizáveis | [foundations.md](references/foundations.md) | Foundations |
| Peças e comportamentos | [components.md](references/components.md) | Components |
| Arranjos reutilizáveis | [layouts.md](references/layouts.md) | Layouts |

### 1. Casca, background e Overview

Leia `catalog-shell.md`. Crie `design-system.html`, `styles.css`, a barra superior e o background real do HTML. Reutilize imediatamente efeitos globais, background animado, vídeo, Canvas, WebGL ou movimento presentes na fonte.

Em seguida, leia `overview.md` e crie o Overview como uma adaptação direta da hero de `index.html`: mantenha estrutura, componentes, assets, efeitos, animações e impacto visual; altere somente a copy para apresentar o Design System.

### 2. Foundations

Leia `foundations.md` e implemente, nesta ordem, Typography → Colors → Spacing. Identifique e registre todas as famílias e assinaturas tipográficas únicas encontradas no HTML e aplique essas fontes em todo o catálogo.

### 3. Components

Depois de Foundations, leia `components.md` e implemente os componentes completos sobre os átomos extraídos. Radius, borders, shadows, elevation, gradients, assets e motion pertencem a esta etapa.

### 4. Layouts

Depois de Components, leia `layouts.md` e implemente os layouts com as peças extraídas, incluindo assets do arranjo.

### 5. Revisão final

Abra `design-system.html` e verifique navegação, hero, fontes, background, componentes, layouts, estados, animações, responsividade, imports, assets e erros de console. Corrija os problemas encontrados e só então mostre o catálogo e seus paths ao usuário.

## Princípios de implementação

- `design-system.html` importa `styles.css` e, se necessário, `interactions.js`; não use CSS ou JS inline.
- Use HTML semântico e metadados leves: `data-ds-section`, `data-component`, `data-variant` e `data-status`.
- Concentre em custom properties somente Typography, Colors e Spacing compartilhados. Acabamentos permanecem nos Components ou Layouts que os materializam.
- Cada preview usa o markup, classes, CSS, JS e assets reais do design system.
- Reutilize a implementação original quando ela já funciona; remova apenas conteúdo de negócio e lógica sem relação com a linguagem visual.
- Se uma Foundation mudar, revise os Components e Layouts dependentes.

## Não fazer

- Aceitar imagem ou gerar screenshot/wireframe como etapa de extração.
- Criar componentes, estados, responsividade ou motion sem evidência no HTML.
- Parar para aprovação entre Overview, Foundations, Components e Layouts.
- Manter tokens, manifestos ou documentação em JSON como fonte paralela.
- Criar uma aba de Assets; documente cada recurso dentro do Component ou Layout que o usa.
- Substituir classes, assets ou efeitos distintivos por aproximações genéricas quando a implementação original está disponível.
