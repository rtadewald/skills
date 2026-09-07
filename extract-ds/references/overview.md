# Overview

<<<<<<< ours
Leia este arquivo somente ao criar a seção **Overview** de `design-system.html`.

## Papel

O Overview deve permitir que uma pessoa ou outra IA entenda a personalidade do sistema antes de abrir Foundations, Components ou Layouts. Ele é uma leitura de orientação, não uma segunda documentação dos tokens, componentes e arranjos.

Use `data-ds-section="overview"` e exponha, em texto curto e visual:

- identificação do design system e tipo da fonte (`HTML` ou `image`);
- evidência disponível e confiança geral;
- personalidade visual sustentada pela fonte: por exemplo `dark`, `editorial`, `glass`, `spatial`, `soft`, `brutalist`, `high contrast` ou `playful`;
- sinais que formam essa personalidade: superfícies, contraste, densidade, tipografia, bordas, iluminação, gradientes, textura, 3D ou motion;
- cobertura real: foundations, componentes, layouts e assets incorporados incluídos; itens observados porém não reutilizáveis; e categorias não observadas.

Não escreva uma lista de adjetivos vazia. Cada descrição deve ser confirmada pelo preview ou por uma descoberta do inventário. Diferencie no texto e em `data-status` aquilo que é `observed`, `inferred` e `suggested`.

## Showcase

Quando a fonte tiver um layout característico, coloque uma pequena showcase próxima ao Overview: normalmente hero, bloco de dashboard ou seção de destaque. Ela deve usar os mesmos componentes, classes, Foundations e assets exibidos no catálogo. Não crie uma versão cenográfica só para a introdução.

Em uma fonte pequena, um único preview pode bastar. Em uma fonte rica, mostre no máximo dois ou três Layouts que expliquem a linguagem; não transforme o Overview numa cópia da aplicação inteira.

## Separar o catálogo da fonte

A barra superior, labels, containers, busca, controles de copiar código e demais elementos de navegação de `design-system.html` pertencem à **UI de documentação**. Não os registre como componentes extraídos, salvo se a mesma peça existir comprovadamente na fonte.

Mantenha essa separação compreensível por estrutura e classes. A documentação deve ser legível e utilizável em viewport razoável, mas sua responsividade não prova que a referência original tinha o mesmo comportamento.
=======
Leia este arquivo logo depois de criar a casca de `design-system.html`.

## O Overview é a hero do `index.html`

Use a hero principal do HTML de origem como primeira seção do catálogo. O objetivo é causar o mesmo impacto visual e mostrar imediatamente a personalidade do Design System em funcionamento.

Preserve da hero original:

- estrutura HTML e hierarquia;
- classes e layout;
- componentes e variantes;
- background e camadas decorativas;
- imagens, SVGs, vídeo, Canvas, 3D ou WebGL;
- gradients, glass, glow, masks, borders e iluminação;
- ambient motion e interaction motion;
- responsividade e comportamento em runtime.

Altere somente a copy necessária para apresentar o catálogo como Design System. Mantenha aproximadamente o mesmo volume, número de linhas e hierarquia do texto original para não quebrar composição, espaçamento ou animações.

A nova copy deve explicar de forma curta que a página documenta a linguagem visual extraída e permite consultar Typography, Colors, Spacing, Components e Layouts. Evite texto técnico longo dentro da hero.

Se `index.html` não possuir um elemento chamado `hero`, identifique a primeira dobra ou seção de maior impacto que exerce essa função e use-a como Overview. Não invente uma hero completamente nova enquanto existir uma composição principal aproveitável.

## Implementação

Use `data-ds-section="overview"` sem substituir as classes originais da hero. O preview deve usar os assets, CSS, JS e dependências reais. Não simplifique efeitos para tornar a documentação mais neutra.

A barra superior do catálogo pertence à UI de documentação e fica acima do Overview. Ela não substitui automaticamente a navegação que já faça parte da hero; preserve a navegação original quando ela for necessária para manter a composição e o impacto visual.

Depois que Foundations, Components e Layouts forem implementados, revise a hero para confirmar que continua usando as mesmas fontes, tokens, componentes e assets registrados nas demais seções.

## Verificação

Confirme que:

- o Overview é reconhecível como a hero original;
- somente a copy foi adaptada;
- efeitos e animações continuam funcionando;
- o texto apresenta o Design System sem alterar a densidade da composição; e
- a hero demonstra o sistema real, sem uma implementação paralela.
>>>>>>> theirs
