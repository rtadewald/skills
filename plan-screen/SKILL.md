---
name: plan-screen
description: >-
  Ajuda a transformar uma ideia de tela ou fluxo de aplicativo em uma direção
  aprovada, wireframes estruturais e mocks visuais. Usa ASCII por padrão e SVG
  quando solicitado. Use when the user mentions plan-screen or asks to plan an
  app screen or interface flow.
disable-model-invocation: true
---

# Plan Screen

Ajude o usuário a planejar telas ou fluxos de aplicativos visualmente impactantes e chegar a mocks aprovados. Conduza a ideia desde a definição do problema até imagens que representem com clareza o produto imaginado.

Ao final do trabalho, o usuário deve ter:

- o escopo e o fluxo do produto definidos;
- uma direção funcional e visual aprovada;
- um wireframe aprovado para cada tela necessária;
- os mocks visuais dessas telas em `mocks/`.

## Como o trabalho acontece

Conduza o processo em quatro etapas:

1. **Entender o produto:** descubra o objetivo, o público, a ação principal e se o usuário precisa de uma tela ou de um fluxo.
2. **Explorar direções:** apresente três maneiras diferentes de resolver o mesmo problema e mostre o wireframe da tela principal de cada uma.
3. **Detalhar a escolhida:** depois da aprovação, crie o wireframe de todas as telas que fazem parte da direção escolhida.
4. **Gerar os mocks:** depois da aprovação dos wireframes, envie todas as imagens necessárias para `$to-img` e apresente os resultados.

Existem dois momentos de aprovação. O primeiro acontece após as três direções; o segundo, após os wireframes completos. Não gere os mocks antes dessas duas aprovações.

## Antes de começar

O usuário é criador de conteúdo e precisa conseguir entender, comparar e apresentar as propostas com facilidade. Não presuma que ele conhece termos de design ou desenvolvimento. Explique as escolhas em linguagem clara e mostre como cada decisão afeta o impacto visual e a experiência. Evite apresentar o processo como uma lista de termos técnicos.

Neste fluxo:

- uma **direção** é uma proposta coerente de produto, composição, aparência e comportamento;
- um **wireframe** é a planta estrutural da interface, usada para validar regiões, hierarquia, conteúdo e estados;
- um **mock** é a imagem visual final produzida a partir da direção e do wireframe aprovados.

Use ASCII nos wireframes por padrão. Use SVG somente quando o usuário pedir. Passe `format=ascii` ou `format=svg` em toda chamada a `$to-wireframe` e mantenha o formato escolhido até o fim.

Salve todos os artefatos em `mocks/`. Encontre o maior número já usado nessa pasta, use o próximo como `{cycle}` e mantenha esse número em todos os arquivos do mesmo trabalho.

Quando o usuário fornecer HTML, imagens, pastas ou links como referência, examine o material antes das propostas. Identifique o que deve ser preservado e o que pode ser reinterpretado.

`$to-wireframe` é responsável por desenhar os wireframes. `$to-img` é responsável por gerar as imagens via OpenRouter. A `$plan-screen` coordena o produto, as decisões, as aprovações e as informações entregues a essas duas skills.

## Etapa 1 — Entender o produto

Descubra as informações que determinam a solução:

- quem usará o produto;
- que problema ou necessidade ele atende;
- qual resultado a experiência precisa produzir;
- qual é a ação principal do usuário;
- quais restrições ou referências precisam ser consideradas;
- se o escopo é uma tela isolada ou um fluxo de telas.

Pergunte somente o que estiver faltando e puder mudar materialmente a proposta. Se o pedido já tiver contexto suficiente, prossiga sem transformar o briefing em uma entrevista longa.

Para um fluxo, defina apenas as telas necessárias e mostre um mapa simples:

| Tela | Objetivo | Ação principal | Próximo destino |
|---|---|---|---|

O mapa explica a jornada que as três direções deverão resolver. Uma tela isolada não precisa dele.

## Etapa 2 — Explorar três direções

Apresente três direções claramente diferentes para o mesmo objetivo e, quando houver fluxo, para o mesmo mapa de telas. As diferenças devem resultar em experiências reconhecíveis, e não apenas em trocas superficiais de estilo.

Explique em cada direção:

- a ideia central;
- o que ela faz de maneira diferente;
- como organiza a informação e a ação principal;
- qual linguagem visual sustenta a proposta;
- que interações ou movimentos contribuem para a experiência, quando forem úteis.

Não trate gráficos, 3D, animações ou efeitos como uma checklist. Use-os quando ajudarem a comunicar, orientar ou tornar a experiência memorável.

Crie o wireframe da tela mais importante de cada direção. Para isso, invoque `$to-wireframe` passando a função da tela, seu conteúdo, suas regiões, a hierarquia e os estados necessários:

```text
Use $to-wireframe:
format=<ascii|svg>
brief="<descrição estrutural da tela principal>"
output=mocks/{cycle}-proposal-<a|b|c>-wire.<txt|svg>
```

Os arquivos devem seguir este padrão:

```text
mocks/{cycle}-proposal-a-wire.txt
mocks/{cycle}-proposal-b-wire.txt
mocks/{cycle}-proposal-c-wire.txt
```

Use `.svg` no lugar de `.txt` quando SVG tiver sido solicitado. Mostre o conteúdo dos wireframes ASCII junto de seus paths. Para SVG, abra os arquivos quando possível ou apresente os paths.

Compare brevemente as três direções e peça ao usuário que escolha uma. Quando houver fluxo, confirme também o mapa de telas. Não desenhe todas as telas de cada direção antes dessa escolha.

Se nenhuma direção for aprovada, entenda os pontos rejeitados e apresente um novo ciclo de propostas.

## Etapa 3 — Detalhar a direção aprovada

Depois da escolha, crie um wireframe para cada tela aprovada. Uma proposta de tela isolada gera apenas um wireframe.

Para cada tela, informe a `$to-wireframe`:

- a direção escolhida;
- a função da tela dentro do produto;
- de onde o usuário veio e para onde poderá seguir;
- a ação principal;
- o conteúdo, as regiões e a hierarquia;
- os estados necessários.

Grave os arquivos mantendo o mesmo `{cycle}`:

```text
mocks/{cycle}-{screen-slug}-wire.txt
```

Use `.svg` quando esse for o formato escolhido. `$to-wireframe` é a fonte única para regiões, tags, aninhamento e revisão estrutural; não crie outra gramática nem altere seu resultado manualmente.

Mostre todos os wireframes, identificados pelo slug da tela, e aguarde a segunda aprovação.

## Etapa 4 — Gerar os mocks

Depois da aprovação dos wireframes, prepare as solicitações de imagem. Se o usuário não indicar uma quantidade, gere uma variante de cada tela.

Crie uma solicitação para cada combinação de tela e variante. Cada uma deve conter:

- `filename=mocks/{cycle}-{screen-slug}-{variant}.png`;
- um prompt que explique o produto, a direção aprovada e a função da tela;
- a relação da tela com o restante do fluxo;
- a estrutura e os estados definidos no wireframe;
- a proporção adequada à interface;
- a referência visual, quando houver, e o que deve ser aproveitado dela.

O wireframe orienta a composição. Traduza suas regiões e hierarquia para uma interface visual; não peça ao gerador que copie literalmente os caracteres ASCII ou as formas do SVG.

Invoque `$to-img` uma única vez com todas as solicitações. Ela cuidará do modelo, da resolução, do OpenRouter, da execução paralela e da verificação dos arquivos.

Quando a geração terminar, apresente todos os mocks e seus paths.

## Regras gerais

- Não aumente o número de telas sem necessidade funcional.
- Não repita ou altere o mapa do fluxo em cada direção.
- Não reduza direções diferentes a simples mudanças de cor ou acabamento.
- Não crie tags, regiões ou ids paralelos aos definidos por `$to-wireframe`.
- Não transforme cards, tooltips, docks ou painéis internos em texto solto dentro do elemento pai.
- Não use textos ilegíveis ou detalhes visuais inventados no wireframe.
