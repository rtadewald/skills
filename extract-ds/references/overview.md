# Overview

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
