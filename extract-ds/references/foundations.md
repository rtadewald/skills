# Foundations

Leia este arquivo somente na etapa **Foundations**, antes de criar Components ou Layouts.

## Definição

Foundations são os **átomos do Design System**: os elementos visuais primários usados para construir todo o restante. Nesta arquitetura, existem apenas três famílias de átomos:

```text
Foundations
├── Colors
├── Typography
└── Spacing
```

Cores determinam a matéria visual; tipografia determina a voz e a hierarquia; spacing determina o ritmo e a relação entre elementos. Components combinam esses átomos com forma, acabamento, assets, estados e movimento. Layouts organizam os Components em interfaces.

Radius, borders, shadows, elevation, gradients, blur, glow, assets e motion **não pertencem a Foundations nesta skill**. Eles só ganham significado quando materializados em um Component ou Layout e devem ser documentados nessas etapas.

Use `data-ds-section="foundation"`, IDs claros e `data-status` quando algo for `inferred` ou `suggested`. O preview deve tornar cada átomo visível sem antecipar cards, botões ou layouts.

## Colors

Extraia cores por papel semântico e pelo uso real observado:

- background principal e backgrounds secundários;
- surface e surface elevated como papéis de cor, quando existirem;
- texto primário, secundário, muted, link e texto sobre accent;
- accent principal e variações cromáticas observadas;
- cores de border, divider, overlay e estados semânticos.

A cor-base do catálogo já deve ter sido capturada conforme `catalog-shell.md`: por leitura de pixels/conta-gotas na imagem ou diretamente do HTML. Reutilize esse mesmo valor na Foundation; não crie outra interpretação para o swatch.

Mostre cada cor com nome, valor exato, status e exemplo sobre o fundo correto. Preserve alpha. Gradients, glows e efeitos compostos aparecem depois no Component ou Layout que os usa; aqui entram somente as cores que os alimentam.

Crie CSS custom properties apenas para papéis úteis e recorrentes:

```css
:root {
  --color-background: #0b0d10;
  --color-surface: #15181d;
  --color-text: #ffffff;
  --color-text-muted: #a7adb7;
  --color-accent: #725cff;
  --color-border: rgb(255 255 255 / 12%);
}
```

Não fabrique escalas de 50 a 950 nem dezenas de tons que a referência não utiliza.

## Typography

Construa uma escala visual somente com estilos presentes ou necessários para reproduzir a fonte. Para cada estilo, demonstre:

- família e fallback;
- função: display, heading, body, label, caption ou meta;
- weight, size, line-height e letter-spacing;
- text transform e comportamento de quebra quando característicos.

Renderize texto real com as classes reais. O usuário deve perceber hierarquia, ritmo e contraste tipográfico olhando a seção, sem depender apenas de uma tabela `size / line-height`.

Em HTML, reutilize `@font-face`, imports, variáveis e arquivos existentes. Em imagem, não afirme uma família sem evidência: preserve proporção, peso, tracking e caráter visual; marque qualquer aproximação como `inferred`.

## Spacing

Spacing é o conjunto de distâncias que cria ritmo entre os elementos. Identifique padrões recorrentes de:

- gap entre itens relacionados;
- padding interno;
- distância entre grupos;
- respiro vertical de seções; e
- afastamento das bordas do viewport ou container.

Tokenize apenas distâncias que reaparecem. Não force uma escala de 4 ou 8 pixels se a fonte não a sustenta. Mostre cada valor numa régua ou relação visual simples e indique onde ele foi observado.

```css
:root {
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 32px;
}
```

O exemplo é estrutural; os valores finais precisam vir da referência.

## Antes do gate de Foundations

Confirme que:

- a seção contém somente Colors, Typography e Spacing;
- a cor de background é exatamente a capturada na casca;
- todo token tem uso e evidência;
- tipografia e spacing preservam a personalidade da fonte; e
- nenhum acabamento, asset, motion ou layout foi antecipado.

Mostre somente Foundations e aguarde aprovação antes de ler `components.md`.
