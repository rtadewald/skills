---
name: to-wireframe
description: >-
  Analisa uma tela de app em imagem e grava ao lado um wireframe SVG tipado,
  completo e aninhado, compatível com o fluxo img-to-html. Use when the user
  mentions to-wireframe or asks for a typed UI wireframe from an image.
disable-model-invocation: true
---

# To Wireframe

Leia uma imagem de tela de aplicativo e crie um wireframe SVG tipado que descreve sua estrutura, componentes e conteúdo visível. Use como referência canônica de densidade e marcação [`references/wireframe.example.svg`](references/wireframe.example.svg).

## Entrada e saída

1. Use a imagem cujo path o usuário passou, ou a imagem anexada à conversa. Se não houver uma imagem acessível, peça o path.
2. Grave o SVG no mesmo diretório da imagem, com o mesmo nome-base e a extensão `.wireframe.svg`.

```
mocks/dashboard.png  →  mocks/dashboard.wireframe.svg
foo/hero.webp        →  foo/hero.wireframe.svg
```

3. Mostre o path resultante e abra o SVG quando fizer sentido. Não inicie implementação HTML/CSS, plano de etapas, geração de assets ou aprovação em gates; esta skill termina ao entregar o wireframe.

## O que o wireframe representa

O SVG é uma planta estrutural: registra o que existe e o que aparece dentro de cada região. Não é uma recriação visual pixel-perfect.

- Cada superfície ou componente com estilo próprio recebe uma caixa com label de região na borda superior esquerda: `nav`, `hero`, `media`, `card`, `card2`, `card3`, `form`, `rail`, `quote` ou `section`.
- Mesmo visual usa o mesmo id. Variação visual recebe o próximo id: `card`, `card2`, `card3`.
- Regiões aninham quando a tela mostra superfícies próprias dentro de outra, como cards de lista dentro de um card, tooltip flutuante, dock de controles ou painel de gráfico.
- Toda caixa desenhada precisa de label. Não achate um componente em texto solto no pai.

## Tags tipadas

Todo texto e controle visível entra em uma tag; não deixe conteúdo solto. Use este vocabulário fechado:

| Tag | Uso |
|---|---|
| `[h1:]`, `[h2:]`, `[h3:]` | Títulos |
| `[t1:]`, `[t2:]`, `[t3:]` | Corpo, meta e microtexto |
| `[btn:]`, `[btn2:]`, `[btn3:]` | Botões com estilos distintos |
| `[lnk:]` | Link de navegação inativo |
| `[in:]` | Placeholder ou texto de input |
| `[ico:]` | Ícone |
| `[img:]` | Imagem, raster ou 3D |
| `[av:]` | Avatar |
| `[chart:]` | Gráfico |

Um mesmo id de tag representa o mesmo estilo. Botões visualmente diferentes usam ids diferentes. Nav ativo é `[btn:]`; nav inativo é `[lnk:]`. Um botão com ícone pode ser `[btn: [ico:plus] Add project]`. Escreva uma tag por linha visual: uma headline em três linhas vira três tags `[h1:]`.

Use o texto essencial que estiver legível. Quando não der para ler com segurança, escreva `[t2: ...]`; não invente texto de preenchimento.

## Execução rápida

1. Leia a imagem e estime seu canvas para definir um `viewBox` proporcional.
2. Em uma única passada, desenhe apenas `rect` e `text`: as caixas de região e as tags tipadas. Use cinza, strokes e labels simples.
3. Faça uma única revisão, região por região:
   - toda superfície visível virou região rotulada;
   - todo texto e controle ficou em tag tipada;
   - cards e elementos com superfície própria foram aninhados;
   - o item de nav ativo está marcado como botão;
   - ids de regiões e tags refletem diferenças visuais reais.
4. Grave e abra o arquivo.

## Limites visuais

- Não meça pixels, faça OCR, crop, eyedropper, cálculo de coordenadas ou comparação pixel a pixel.
- Estime posições e tamanhos; se houver dúvida entre valores, escolha um e continue.
- Não desenhe ícones, gráficos, sombras, gradientes, curvas ou imagens simuladas. Descreva-os pelas tags `[ico:]`, `[chart:]`, `[img:]` e `[av:]`.
- Use `<?xml version="1.0" encoding="UTF-8"?>` e labels com letras/números básicos para evitar XML inválido.
- Não inclua texto explicativo, notas extensas, cores do produto ou labels de etapas de implementação. O SVG contém apenas o wireframe.
