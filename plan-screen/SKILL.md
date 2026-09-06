---
name: plan-screen
description: >-
  Ajuda a planejar uma tela isolada ou um fluxo de telas de app: fecha o briefing,
  propõe direções, cria wireframes ASCII tipados por padrão e, após aprovação,
  gera PNGs em mocks/. Use SVG apenas quando o usuário pedir.
disable-model-invocation: true
---

# Plan Screen

Ajude o usuário a planejar uma tela isolada ou um fluxo de telas para um aplicativo. O resultado deve equilibrar impacto visual e uma ideia funcional que resolva algo de modo interessante.

## Formato do wireframe

Use **ASCII** por padrão. Se o usuário pedir SVG, use **SVG**. Defina o formato no início do trabalho e mantenha-o em todo o ciclo de propostas e telas:

| Escolha | Chamada a `$to-wireframe` | Arquivo |
|---------|----------------------------|---------|
| Padrão | `format=ascii` | `.txt` |
| Pedido explícito do usuário | `format=svg` | `.svg` |

Não escolha SVG apenas porque facilita a visualização. O wireframe é a planta estrutural; a imagem final é o PNG gerado depois da aprovação.

## Conversa

- Faça uma pergunta aberta por vez e seja sucinto.
- Descubra o objetivo do produto, quem usa, o resultado que cada tela precisa produzir e o que torna a experiência memorável.
- Defina cedo o escopo: uma tela focal ou um fluxo com várias telas. Para fluxos, descubra as telas mínimas, a ordem e a ação que liga cada uma à próxima. Não acrescente telas por hábito.
- Se o usuário trouxer HTML, pasta, screenshot ou link, estude a referência. Confirme o que deve ser reaproveitado e guarde ou crie uma screenshot para orientar a geração de imagens.

## Fluxo

### 1. Briefing e mapa de telas

Converse até entender o produto e o escopo. Se houver mais de uma tela, apresente um mapa curto antes das propostas:

| Tela | Objetivo | Entrada / saída |
|---|---|---|
| `onboarding` | Definir preferências | Abre `dashboard` |
| `dashboard` | Acompanhar o estado principal | Abre `detail` |
| `detail` | Tomar a ação central | Retorna ao `dashboard` |

O mapa descreve somente telas necessárias ao fluxo aprovado. Uma tela única não precisa de mapa.

### 2. Três direções de produto

Apresente três direções visuais e funcionais distintas. Cada direção inclui:

- uma frase sobre o que a torna única;
- elementos e comportamento que aparecerão;
- motion, 3D, gráficos, superfícies, CTAs e background relevantes;
- quando houver fluxo, um mapa curto de telas e transições;
- um wireframe tipado da tela mais importante do fluxo. Para uma única tela, ela é a própria tela proposta.

Para cada direção, invoque **`$to-wireframe`** com o formato escolhido, passando no `brief` a função da tela, os elementos, estados e hierarquia. Grave os três arquivos no mesmo ciclo `{n}` em `mocks/`:

```text
mocks/{n}-proposal-a-wire.txt
mocks/{n}-proposal-b-wire.txt
mocks/{n}-proposal-c-wire.txt
```

Use `.svg` no lugar de `.txt` se o usuário escolheu SVG. Encontre o maior `{n}` já usado em `mocks/` e use o próximo. No SVG, abra o arquivo ou mostre o path; no ASCII, mostre seu conteúdo no chat junto do path.

`$to-wireframe` é a fonte única para regiões, tags tipadas, estados, aninhamento e revisão estrutural. Não crie uma gramática local nem altere o resultado manualmente.

Não desenhe todas as telas de todas as direções: isso torna a escolha lenta. O usuário aprova uma direção e seu mapa de telas antes da próxima etapa. Se não aprovar, revise as direções e repita este ciclo.

### 3. Wireframes do fluxo aprovado

Com a direção e o mapa aprovados, crie um wireframe para cada tela. Se o usuário aprovou uma tela única, gere somente um. Para cada tela, invoque `$to-wireframe` com o mesmo formato escolhido e grave:

```text
mocks/{n}-{screen-slug}-wire.txt
```

Use `.svg` quando SVG foi solicitado. Mostre todos os wireframes, identificados pelo slug da tela, e aguarde aprovação antes de gerar imagens.

### 4. Gerar imagens

Depois que os wireframes forem aprovados, pergunte quantas variações visuais gerar **por tela**. O padrão é uma variação de cada tela aprovada. Gere uma imagem por tela e variante, em paralelo, com GPT Image 2 (`gpt2`), 1K e proporção adequada ao wireframe; use `16:9` se nada indicar outro formato.

Use o mesmo `{n}` do ciclo aprovado, o slug da tela e uma letra de variante:

```text
mocks/{n}-dashboard-a.png
mocks/{n}-detail-a.png
mocks/{n}-detail-b.png
```

No prompt de cada imagem, descreva a função do aplicativo, a tela específica, a transição de onde ela vem e para onde vai, e a direção aprovada. O wireframe é um mapa de regiões: traduza sua intenção para o prompt, sem pedir uma cópia literal dos caracteres ou do SVG.

Rode a geração no cwd do usuário com `OPENROUTER_API_KEY` disponível em `.env` do projeto ou `~/.env`. Dispare os requests independentes em paralelo e aguarde todos antes de apresentar os resultados:

```bash
uv run ~/.agents/skills/openrouter-img/scripts/generate_image.py \
  --prompt "..." --filename "mocks/{n}-{screen-slug}-{variant}.png" \
  --model gpt2 --resolution 1K --aspect-ratio 16:9 &

wait
```

Se houver referência visual, inclua `--input-image` e especifique no prompt quais qualidades reaproveitar. Ao terminar, mostre todos os paths e pare.

## Não fazer

- Gerar imagens antes da aprovação da direção, do mapa de telas quando houver e dos wireframes.
- Transformar uma proposta em um conjunto grande de telas sem necessidade de produto.
- Criar tipos, tags ou ids paralelos aos de `$to-wireframe`.
- Tratar cards, tooltips, docks ou painéis internos como texto solto dentro do componente pai.
- Inventar textos ilegíveis, cores ou detalhes visuais no wireframe.
