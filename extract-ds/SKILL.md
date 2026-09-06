---
name: extract-ds
description: >-
  Extrai de HTML ou imagem uma linguagem visual reutilizável e cria um catálogo
  HTML-first de design system: wireframe e inventário → foundations → components
  → layouts, com aprovação a cada camada. Use when the user mentions
  extract-ds or asks to derive a design system from a UI reference.
disable-model-invocation: true
---

# Extract DS

Crie um design system HTML-first, reutilizável e fiel à fonte. Ele é composto pelo catálogo `design-system.html`, seu CSS, seu JS quando houver comportamento, e `assets/`; não crie JSON, manifestos ou uma documentação paralela que possa se desalinhar da implementação.

Aceite uma única fonte de entrada:

- `html=<path>`: uma página HTML local, com seu CSS, JS e assets associados;
- `image=<path>` ou imagem anexada: uma tela, mock ou screenshot.

Se a fonte não estiver clara, peça uma única fonte. `<slug>` é um nome curto em kebab-case derivado da fonte ou indicado pelo usuário.

## Resultado

```text
design-systems/<slug>/
  reference.html | reference.[ext]  # cópia da fonte fornecida
  wireframe.txt                    # contrato estrutural da etapa 1
  design-system.html               # catálogo navegável e fonte de documentação
  styles.css                       # tokens, linguagem visual e componentes
  interactions.js                  # somente se houver comportamento ou motion
  assets/                          # imagens, ícones, SVG, modelos 3D e códigos visuais
```

O catálogo usa uma barra de navegação **superior e horizontal** para `Overview`, `Foundations`, `Components` e `Layouts`. Ela pode permanecer sticky ou flutuar no topo, mas não deve virar uma sidebar vertical. Assets não são uma categoria: ficam dentro do Component ou Layout que os utiliza e fisicamente em `assets/`.

## Arquitetura canônica

Organize todo design system criado por esta skill segundo esta hierarquia e preserve a responsabilidade de cada camada:

```text
Foundations
├── Colors
├── Typography
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

Foundations fornecem os átomos. Components materializam esses átomos em peças completas, com acabamento e comportamento. Layouts organizam as peças no espaço e controlam os assets e a responsividade do arranjo. Use essa árvore como contrato para classificar o inventário, implementar as seções e revisar o resultado.

## Gates de aprovação

O catálogo cresce em complexidade e tem quatro gates, nesta ordem:

1. decomposição tipada e inventário;
2. Foundations;
3. Components;
4. Layouts e Overview final.

Em cada gate, abra ou mostre `design-system.html`, destaque somente a seção concluída, informe o path e **pare**. Só avance com aprovação explícita. Uma correção repete a camada atual; não comece a seguinte enquanto ela não estiver aprovada.

## Etapa 1 — Decomposição tipada

Objetivo: registrar quais regiões e peças a fonte realmente mostra antes de criar o catálogo.

1. Crie `design-systems/<slug>/` e copie a fonte para `reference.html` ou `reference.[ext]`.
2. Para HTML, abra a página e analise seus estilos e scripts; tire uma screenshot representativa em `design-systems/<slug>/reference.png`. Para imagem, use a cópia fornecida diretamente.
3. Invoque [`$to-wireframe`](../to-wireframe/SKILL.md) com `format=ascii`, a screenshot/imagem em `image=`, e `output=design-systems/<slug>/wireframe.txt`.
4. Leia o wireframe e a fonte, quando for HTML. Faça um inventário curto que associe cada região a uma categoria: foundation, component ou layout. Registre assets dentro do component ou layout proprietário. Marque cada descoberta como `observed`, `inferred` ou `suggested`.
5. Liste também elementos não observados que portanto não entrarão no catálogo, como formulários, tabelas, modais ou motion.
6. Mostre `wireframe.txt` e o inventário → **gate da etapa 1**.

O `$to-wireframe` é a fonte única para regiões, tags tipadas e aninhamento. Não edite manualmente o ASCII e não o trate como especificação de cores, medidas ou efeitos.

### Evidência e confiança

- `observed`: aparece na imagem, ou existe em HTML/CSS/JS/asset da fonte.
- `inferred`: é uma regra visual provável, usada com moderação para tornar os elementos observados coerentes.
- `suggested`: comportamento ou estado útil que não é comprovado pela fonte, como focus, hover ou motion em uma entrada por imagem.

Não apresente inferências ou sugestões como extrações. Para HTML, examine classes, custom properties, CSS, `@keyframes`, transições, scripts e assets antes de classificar uma propriedade como observada.

## Etapa 2 — Construir o catálogo incrementalmente

Objetivo: implementar uma página navegável cujos exemplos usam o código real do design system. Siga rigorosamente: casca e background → Foundations → Components → Layouts.

Antes de trabalhar uma categoria, leia somente a referência indicada abaixo; não carregue as outras por antecipação.

| Momento | Referência a ler | Seção no catálogo |
|---|---|---|
| Criação do arquivo, background e navegação superior | [catalog-shell.md](references/catalog-shell.md) | Casca do catálogo |
| Tokens e regras reutilizáveis | [foundations.md](references/foundations.md) | Foundations |
| Peças de interface e seus estados | [components.md](references/components.md) | Components |
| Arranjos reutilizáveis e showcase | [layouts.md](references/layouts.md) | Layouts |
| Resumo da linguagem visual e cobertura, após as outras seções | [overview.md](references/overview.md) | Overview |

Preserve somente os elementos do inventário aprovado e execute cada camada abaixo antes da seguinte.

### 2.0 Casca e background

Leia `catalog-shell.md`. Crie `design-system.html`, `styles.css`, a barra superior e o background fiel à fonte. Para imagem, obtenha a cor por amostragem/conta-gotas; para HTML, leia o valor e as camadas reais. Reutilize imediatamente efeitos globais, background animado, Canvas, WebGL ou movimento presentes no HTML. Esta passagem prepara a atmosfera do catálogo, sem implementar Components ou Layouts.

### 2.1 Foundations

Leia `foundations.md` e implemente somente Colors, Typography e Spacing. Não implemente previews de Components ou Layouts nesta passagem. Verifique a seção no catálogo e apresente-a → **gate de Foundations**.

### 2.2 Components

Depois da aprovação de Foundations, leia `components.md` e implemente os componentes completos sobre os átomos já validados. Radius, borders, shadows, elevation, gradients, assets e motion pertencem a esta etapa. Verifique variantes, estados, imports, assets e as animações demonstráveis e apresente a seção → **gate de Components**.

### 2.3 Layouts e Overview

Depois da aprovação de Components, leia `layouts.md` e implemente os layouts com as peças já aprovadas, incluindo assets que pertencem ao arranjo completo. Por fim, leia `overview.md` e construa o resumo e a showcase a partir do sistema agora completo. Verifique a integração entre todas as seções e apresente o catálogo → **gate de Layouts**.

O output deve cumprir estes princípios:

- `design-system.html` importa `styles.css` e, se necessário, `interactions.js`; não use CSS ou JS inline.
- Use HTML semântico e metadados leves no markup: `data-ds-section`, `data-component`, `data-variant` e `data-status` (`observed`, `inferred`, `suggested`).
- Concentre em CSS custom properties somente cores, tipografia e spacing compartilhados. Acabamentos e efeitos permanecem nos Components ou Layouts que os materializam.
- O preview é sempre o componente real e suas classes reais. Não crie uma demonstração separada da implementação.
- HTML de origem permite reutilizar classes, CSS, assets, animações e interações existentes. Imagem permite apenas reconstruir visualmente, marcando as partes não comprovadas.
- Preserve textos e controles como HTML; não converta a tela em uma única imagem.

Se uma correção posterior mudar uma foundation, revise os Components e Layouts que dependem dela antes de apresentar novamente a camada afetada. Abra `design-system.html`, verifique links da navegação, background, estados visíveis, carregamento de assets e a relação entre cada exemplo e sua fonte.

## Não fazer

- Pular o wireframe, o inventário ou qualquer gate.
- Criar um design system universal com componentes ausentes da fonte.
- Manter tokens, manifestos ou documentação em JSON como fonte paralela.
- Chamar de extraído um modelo 3D, fundo ou animação reconstruído a partir de imagem.
- Criar uma aba de Assets; documente cada recurso dentro do Component ou Layout que o usa.
- Usar placeholders genéricos para substituir elementos distintivos da referência.
