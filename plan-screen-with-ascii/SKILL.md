---
name: plan-screen-with-ascii
description: >-
  Ajuda o usuário a esclarecer o objetivo de uma tela de app e, após aprovação,
  gera o PNG da tela em mocks/.
disable-model-invocation: true
---

# Plan Screen With ASCII

Auxilie o usuário a planejar uma tela para um aplicativo que está desenvolvendo e que seja visualmente atrativa.


## Background

O usuário é criador de conteúdo para redes sociais e dono de uma escola de programação e precisa da sua ajuda para planejar um app e uma tela para um aplicativo que está desenvolvendo. Você deve ajudá-lo a criar uma **tela funcional** para seu app e que seja a mais impactante visualmente possível, com animações, componentes UIs fora da caixa, gráficos, tabelas, elementos distoantes, tecnológicos, tipografia única, etc.

Ao desenvolvermos a ideia da tela, devemos buscar um dos dois pilares abaixo:

1. **Impacto visual** — cores, animações, efeitos, transições, 3ds, backgrounds lindos, tipografia com presença, cards/superfícies com identidade — elementos que chamam muito a atenção para o aplicativo quando visto em redes sociais.
2. **Funcionalidade fora da caixa** — uma forma diferente de resolver o problema proposto, seja por conta de algum algoritmo ou IA nova embutida no projeto.


## Regras Gerais

- Sempre que precisar perguntar algo para o usuário, faça uma pergunta aberta, onde ele pode escrever sua resposta. Não use questionários com respostas de marcar. Isso limita o usuário.
- Faça uma pergunta por vez.
- Seja sucinto em suas colocações e perguntas - pouco verboso.


## Fluxo

### 1. Conversa e briefing

Em primeiro lugar você deve compreender o que o usuário deseja fazer. 
Qual o objetivo do app? Está claro a ideia dessa tela? Existe alguma ideia interessante que poderia aparecer ali que ele está deixando passar?

O usuário também pode te fornecer uma página HTML, pasta, screenshot ou link de referência contendo designs que ele gostaria de incluir no seu app.
Se isso ocorrer: 
1. Abra e estude o layout (cores, componentes, o que chama atenção, background), 
2. Garanta que está claro qual elemento chamou a atenção do usuário ali e que ele não abre mão de incluir no aplicativo. Se não estiver: pergunte a ele.
3. Tire um screenshot da tela (se não tiver sido lhe passado) e guarde o caminho do arquivo — essa referência volta na etapa 3 como base visual da imagem que geraremos do app.

Converse até fechar:
Se o objetivo ainda não estiver 100% claro para você, pergunte ao usuário até entender bem.


### 2. Duas propostas de tela (texto)

Escreva **três propostas** da tela do app que deseja montar, cada uma com uma direção distinta. O objetivo é dar ao usuário variações de ideias de como implementar esse app.
Para cada proposta, descreva:

- Uma pequena frase descrevendo o que torna essa tela única.
- Bullet points contendo os elementos que aparecerão na tela.
- Que eleimage.pngmentos de design especiais estarão na tela (animações? elementos 3d? gráficos, componentes UI, cards? CTAs? Transições?, Background?)
- Um desenho em ASCII da tela representando o layout do app apenas (não cores). No ASCII, represente a posição de elementos e o que haverá lá (apenas uma descriçao breve, não precisa de uma descrição literal). 

Envie ao usuário e peça sua opinião. Avance para a próxima etapa só quando ele aprovar.
Se ele não aprovar, refaça as propostas e repita o ciclo.


### 3. Gerar a imagem

Com a proposta aprovada, verifique com o usuário quantas telas deve gerar por proposta. Use sua skill de OpenRouter Image API para gerá-las. Default: modelo `gpt2` (GPT Image 2), `1K`, `16:9`.

No prompt, deixe explícito que é um **aplicativo** (função do app) e que a tela precisa de funcionalidade + visual absurdo. Cada versão recebe um prompt próprio, mesma ideia de produto, visual diferente. Solicite ao modelo que capriche em todas elas.

Olhe `mocks/` e use o próximo `{n}` livre (ou o que o usuário indicar). Dispare as 3 chamadas **em paralelo** (ou a quantidade que o usuário mandar), no cwd do usuário, com `OPENROUTER_API_KEY` (`.env` do projeto ou `~/.env`):

```bash
uv run ~/.agents/skills/openrouter-img/scripts/generate_image.py \
  --prompt "..." --filename "mocks/{n}-a.png" \
  --model gpt2 --resolution 1K --aspect-ratio 16:9 &

wait
```

Se o usuário passou referência visual na etapa 1, acrescente `--input-image` com o path dela nas três chamadas e diga no prompt o que reaproveitar. Se for HTML ou link, tire um screenshot antes. Suba a resolução só se o usuário pedir.

#### Output

Mostre os paths (`{n}-a.png`, `{n}-b.png`, `{n}-c.png`) e pare.
