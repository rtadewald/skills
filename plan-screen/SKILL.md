---
name: plan-screen
description: >-
  Ajuda o usuário a planejar uma tela ou fluxo de aplicativo, comparar três
  propostas com wireframes e, após aprovação, gerar mocks em paralelo. Usa
  ASCII por padrão e SVG quando solicitado. Use when the user mentions
  plan-screen or asks to plan an app screen or interface flow.
disable-model-invocation: true
---

# Plan Screen

Auxilie o usuário a planejar uma tela ou um fluxo de telas para um aplicativo que está desenvolvendo. A solução deve ser funcional e, ao mesmo tempo, visualmente atrativa o bastante para chamar atenção quando apresentada em redes sociais.

Para chegar a esse resultado, trabalhe em quatro etapas:

1. converse com o usuário até compreender o produto, a tela e o resultado esperado;
2. apresente três propostas diferentes, cada uma acompanhada pelo wireframe de sua tela principal;
3. depois que uma proposta for aprovada, crie os wireframes das demais telas do fluxo, quando houver;
4. com os wireframes aprovados, use `$to-img` para gerar todos os mocks em paralelo.

Antes de executar essas etapas, considere o contexto e os critérios criativos abaixo.

## Background

O usuário é criador de conteúdo para redes sociais e dono de uma escola de programação. Ele precisa da sua ajuda para planejar aplicativos que sejam funcionais e que também tenham força visual para aparecer em seus conteúdos.

Ao desenvolver a ideia, busque pelo menos um destes dois pilares:

1. **Impacto visual** — cores, animações, efeitos, transições, elementos 3D, backgrounds marcantes, tipografia com presença e superfícies com identidade. Esses recursos devem fazer o aplicativo chamar atenção quando visto em redes sociais.
2. **Funcionalidade fora da caixa** — uma maneira diferente de resolver o problema proposto, inclusive por meio de um algoritmo, automação ou uso interessante de IA.

Uma proposta pode combinar os dois pilares. Evite, porém, adicionar efeitos ou tecnologia apenas para preencher uma lista: cada escolha deve fortalecer a ideia do produto.

## Regras gerais

- Sempre que precisar perguntar algo, faça uma pergunta aberta para o usuário responder com as próprias palavras. Não use questionários com alternativas.
- Faça uma pergunta por vez.
- Seja sucinto nas perguntas e explicações.
- Não presuma que o usuário domina termos de design. Explique as ideias de maneira concreta.
- Use wireframes ASCII por padrão. Use SVG somente quando o usuário pedir.
- Salve wireframes e imagens em `mocks/`.

## Fluxo

### 1. Conversa e briefing

Primeiro, compreenda o que o usuário deseja criar. Descubra qual é o objetivo do aplicativo, quem irá utilizá-lo, o que essa pessoa precisa conseguir fazer e qual resultado a tela deve produzir.

Também avalie se a ideia já está clara ou se existe alguma possibilidade funcional ou visual interessante que o usuário ainda não percebeu. Sugira melhorias quando elas contribuírem diretamente para o produto.

Defina cedo se o trabalho envolve uma única tela ou um fluxo. Quando houver várias telas, identifique somente as necessárias, a ordem entre elas e a ação que leva o usuário de uma para a próxima. Apresente um mapa simples:

| Tela | Objetivo | Ação principal | Próximo destino |
|---|---|---|---|

Uma tela isolada não precisa desse mapa.

O usuário também pode fornecer uma página HTML, uma pasta, uma screenshot ou um link com designs que gostaria de aproveitar. Quando isso acontecer:

1. abra e estude o layout, incluindo cores, componentes, background e os elementos que mais chamam atenção;
2. identifique o que o usuário considera essencial preservar; se isso não estiver claro, pergunte;
3. se a referência for HTML ou um link e ainda não houver imagem, tire uma screenshot e guarde seu path para a geração dos mocks.

Continue a conversa até compreender bem o objetivo, o escopo e as referências. Se essas informações já estiverem claras, avance sem prolongar o briefing.

### 2. Três propostas de tela

Apresente três propostas distintas para resolver o mesmo problema. Quando houver um fluxo, todas devem respeitar o mesmo mapa de telas; o que muda é a direção funcional e visual.

Para cada proposta, descreva no chat:

- uma frase curta explicando o que torna a ideia única;
- os elementos que aparecerão na tela;
- a diferença funcional da proposta;
- os recursos visuais relevantes, como animações, elementos 3D, gráficos, componentes de UI, cards, CTAs, transições ou background.

Além do texto, gere um wireframe da tela mais importante de cada proposta. O wireframe é um mapa de estrutura e intenção: ele não deve tentar reproduzir as cores, os materiais ou o acabamento visual do mock.

#### Gerar os wireframes com `$to-wireframe`

Olhe o maior `{n}` já existente em `mocks/` e use o próximo. As três propostas compartilham o mesmo `{n}`.

Use `format=ascii` por padrão ou `format=svg` quando o usuário tiver pedido SVG. Para cada proposta, invoque `$to-wireframe` com um `brief` que explique a função da tela, as regiões, o conteúdo, a hierarquia e os estados relevantes:

```text
Use $to-wireframe:
format=<ascii|svg>
brief="<descrição estrutural da tela principal>"
output=mocks/{n}-wire-<a|b|c>.<txt|svg>
```

Os arquivos devem seguir este padrão:

```text
mocks/{n}-wire-a.txt
mocks/{n}-wire-b.txt
mocks/{n}-wire-c.txt
```

Use `.svg` no lugar de `.txt` quando o formato escolhido for SVG. Para ASCII, mostre o conteúdo do wireframe junto de seu path. Para SVG, abra o arquivo quando possível ou mostre o path para visualização.

`$to-wireframe` é a fonte única para regiões, tags, estados, aninhamento e revisão estrutural. Não crie uma gramática paralela nem altere manualmente o wireframe que ela produzir.

Mostre as três propostas e seus wireframes e peça a opinião do usuário. Avance somente quando ele aprovar uma direção e, quando houver fluxo, confirmar o mapa de telas. Se nenhuma proposta for aprovada, entenda o que precisa mudar e repita esta etapa.

### 3. Wireframes das demais telas

Esta etapa só é necessária quando a proposta aprovada contém mais de uma tela. O wireframe da tela principal já foi produzido na etapa anterior; crie agora um wireframe para cada tela restante.

Em cada chamada a `$to-wireframe`, use o mesmo formato e o mesmo `{n}`. Explique no `brief` a função da tela, sua posição no fluxo, a ação principal, o conteúdo, as regiões, os estados e a direção aprovada.

Grave cada arquivo como:

```text
mocks/{n}-{screen-slug}-wire.txt
```

Use `.svg` quando esse for o formato escolhido. Mostre todos os wireframes e aguarde a aprovação do conjunto antes de gerar as imagens.

Para uma tela isolada, o wireframe aprovado na etapa 2 já é suficiente e esta etapa deve ser ignorada.

### 4. Gerar as imagens

Com a proposta e os wireframes aprovados, pergunte quantas versões visuais o usuário deseja gerar por tela. Faça essa pergunta somente se a quantidade ainda não tiver sido informada.

Prepare uma solicitação de imagem para cada tela e variante. No prompt de cada uma:

- deixe explícito que se trata de um aplicativo usável e explique sua função;
- descreva a tela específica e a ação principal;
- preserve a direção funcional e visual aprovada;
- informe de onde a tela vem e para onde leva, quando fizer parte de um fluxo;
- traduza as regiões do wireframe em intenção de composição, sem pedir uma cópia literal do ASCII ou do SVG;
- peça uma execução visual especialmente cuidadosa e impactante;
- quando houver referência, explique quais qualidades devem ser reaproveitadas.

Cada variante pode ter um prompt próprio e explorar uma interpretação visual diferente, desde que mantenha a mesma ideia de produto.

Use o mesmo `{n}` do ciclo aprovado. Para uma tela isolada, nomeie as imagens como:

```text
mocks/{n}-a.png
mocks/{n}-b.png
mocks/{n}-c.png
```

Para um fluxo, inclua o slug da tela:

```text
mocks/{n}-{screen-slug}-a.png
mocks/{n}-{screen-slug}-b.png
```

Reúna todas as solicitações em um único batch e invoque `$to-img` uma vez, passando para cada item seu `prompt`, `filename`, `aspect-ratio` e, quando houver, `input-image`. `$to-img` deve disparar todas as gerações independentes em paralelo e aguardar sua conclusão.

Quando terminar, mostre todos os paths gerados e pare.
