# Foundations

Leia este arquivo somente na etapa **Foundations**, antes de criar Components ou Layouts.

## Definição

<<<<<<< ours
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
=======
Foundations são os **átomos do Design System**: os elementos visuais primários usados para construir todo o restante.

```text
Foundations
├── Typography
├── Colors
└── Spacing
```

Tipografia determina voz e hierarquia; cores determinam a matéria visual; spacing determina ritmo e relações. Components combinam esses átomos com forma, acabamento, assets, estados e movimento. Layouts organizam os Components em interfaces.

Radius, borders, shadows, elevation, gradients, blur, glow, assets e motion não pertencem a Foundations nesta skill. Eles devem aparecer materializados no Component ou Layout correspondente.

Use `data-ds-section="foundation"`, IDs claros e `data-status="observed|inferred"` quando necessário. Não antecipe Components ou Layouts.

## Typography

Use o HTML renderizado como índice tipográfico. Percorra todos os elementos textuais e agrupe somente aqueles com a mesma assinatura computada. Uma assinatura inclui:

- `font-family` efetivamente renderizada;
- `font-weight`;
- `font-size`;
- `line-height`;
- `letter-spacing`;
- `text-transform`; e
- estilo, decoração ou tratamento tipográfico relevante.

Analise cada assinatura única uma vez, mesmo quando aparece em vários elementos. Famílias iguais com pesos ou métricas diferentes continuam sendo estilos distintos; estilos equivalentes podem compartilhar o mesmo registro.

### Identificar e registrar as fontes

Para cada assinatura, localize um elemento representativo e examine estilo computado, selector/classe de origem, regra CSS, `@font-face`, import, arquivo carregado e fallback. Registre no catálogo:

- nome semântico do estilo e função observada;
- selector ou classe de origem;
- família renderizada e fallback;
- origem e forma de carregamento da fonte;
- weight, size, line-height, letter-spacing e transformação; e
- evidência usada para o registro.

Não reduza tudo a “fonte principal” quando o HTML utiliza mais de uma família. Se o browser não carregar a família declarada, registre a fonte realmente renderizada e corrija a dependência antes de continuar.

### Construir o catálogo com as fontes extraídas

Reutilize os `@font-face`, imports e arquivos do projeto. Copie fontes para `assets/fonts/` apenas quando isso for necessário para tornar o catálogo funcional e permitido pela origem. Crie variáveis semânticas quando ajudarem:

```css
:root {
  --font-display: "Fonte observada", sans-serif;
  --font-body: "Fonte observada", sans-serif;
  --font-ui: "Fonte observada", sans-serif;
}
```

Aplique as fontes registradas às classes tipográficas correspondentes e ao próprio `design-system.html`. A UI de documentação usa a fonte de corpo observada como base e a fonte de display nos títulos quando esse for seu papel. Cada preview mantém a assinatura exata do elemento original.

Confira no browser se não houve fallback silencioso antes de ajustar quebras, largura ou spacing. Uma fonte listada, mas não carregada e utilizada, não está implementada.

Mostre uma escala viva com todas as assinaturas relevantes e seus exemplos reais. Não adicione headings ou estilos convencionais ausentes do HTML.

## Colors

Extraia do CSS declarado e computado os papéis cromáticos realmente usados:

- background principal e backgrounds secundários;
- surface e surface elevated como papéis de cor;
- texto primário, secundário, muted, link e texto sobre accent;
- accent e variações observadas;
- border, divider, overlay e estados semânticos.

A cor-base do catálogo já foi extraída do HTML durante a criação da casca. Registre exatamente o mesmo valor na seção Colors. Mostre cada cor com nome, valor, origem e exemplo sobre o fundo correto. Preserve alpha.

Gradients, glows e efeitos compostos aparecem depois no Component ou Layout que os usa; aqui entram apenas as cores que os alimentam.

Crie custom properties somente para papéis úteis e recorrentes. Não fabrique escalas de 50 a 950 nem tons ausentes da implementação.

## Spacing

Extraia dos estilos e do layout computado distâncias recorrentes de:
>>>>>>> theirs

- gap entre itens relacionados;
- padding interno;
- distância entre grupos;
- respiro vertical de seções; e
<<<<<<< ours
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
=======
- afastamento de containers e viewport.

Tokenize apenas valores que reaparecem ou definem o ritmo do HTML. Não force escala de 4 ou 8 pixels quando a implementação não a sustenta. Mostre cada valor numa relação visual simples e indique selectors ou regiões onde foi observado.

## Verificação de Foundations

Confirme que:

- a seção contém somente Typography, Colors e Spacing, nessa ordem;
- todas as famílias e assinaturas tipográficas únicas relevantes foram registradas;
- fontes estão carregadas e aplicadas aos previews e à UI do catálogo;
- a cor de background coincide com o HTML de origem;
- todo token possui uso e evidência; e
- nenhum acabamento, asset, motion ou layout foi antecipado.

Depois da verificação, continue diretamente para `components.md`.
>>>>>>> theirs
