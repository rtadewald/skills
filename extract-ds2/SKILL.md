---
name: extract-ds2
description: >-
  Extrai de uma pasta de site HTML autocontido ou projeto local um design system
  em HTML, fiel ao original, com Overview, Components (incluindo foundations) e
  Layouts. Entrega navegação e Components juntos, depois Overview e Layouts,
  com aprovação entre entregas e foco desktop. Use quando o usuário pedir
  extract-ds2 ou este fluxo de extração.
---

# Extract DS 2

Transforme o site fornecido em um catálogo HTML autocontido. A referência visual
é o próprio site de entrada. Extraia sua implementação e apresente seus elementos
sem redesenhar a identidade. Construa por etapas e espere aprovação para avançar.

## Entrada e fonte de verdade

Aceite uma pasta local com HTML, CSS, JS e assets, um HTML com suas dependências,
ou um projeto local executável. Use o caminho indicado pelo usuário; não exija
uma sintaxe de parâmetros. Preserve a origem e gere em uma pasta separada.
Se o destino não foi indicado, use `design-systems/<slug>/` no projeto de trabalho.


## Regra central: nenhuma invenção

NUNCA invente ou estime fontes, pesos, tamanhos, cores, gradientes, textos,
espaçamentos, ícones, imagens, componentes, variantes, estados ou animações.
Toda decisão visual extraída precisa de evidência no HTML/DOM, CSS, JS, assets
ou comportamento renderizado do original. Não use memória, gosto ou convenções
de outros design systems para preencher ausências.

- Registre a origem de cada item junto da implementação, em comentário ou
  `data-source`: arquivo e seletor, componente ou asset. Registre também o estado
  e viewport desktop quando o valor depende deles. Não crie um manifesto duplicado.
- Preserve os textos reais nos exemplos, inclusive títulos, parágrafos e CTAs.
  Não escreva slogans para a Overview, lorem ipsum, estatísticas ou benefícios.
  Para adaptar a copy à apresentação do DS, peça o texto ou autorização específica.
- Texto de apoio tem tanta fidelidade quanto o título: confira família, arquivo
  de fonte carregado, peso, tamanho, entrelinha, tracking, cor e largura do bloco
  na viewport desktop de referência.
- Um asset ou classe disponível, mas não usado na página analisada, não comprova
  uso. Distinga variantes efetivamente encontradas de arquivos legados.
- Derivar um valor de uma expressão CSS comprovada é permitido; inventar uma
  escala ou atribuir significado semântico não demonstrado não é. Preserve os
  nomes existentes ou use rótulos descritivos do que foi observado.
- Se a evidência falta, procure na origem. Persistindo a ausência, omita o item
  e relate a lacuna; peça informação quando ela impedir a etapa. Não preencha
  com uma aproximação. Uma solicitação posterior de criação deve ser identificada
  como extensão autorizada, nunca como extração.

## Inspeção antes de construir

1. Leia as instruções locais. Identifique a página principal e as variantes que
   realmente pertencem ao escopo. Confira código ativo; comentários podem estar antigos.
2. Abra o original no navegador, diretamente ou pelo servidor local necessário.
   Observe uma viewport desktop de referência e os estados existentes. Se não conseguir renderizar,
   explicite a limitação: leitura de código não equivale a validação visual.
3. Inspecione estilos computados, fontes carregadas, custom properties,
   pseudo-elementos, breakpoints, SVG, imagens, vídeos, canvas/WebGL e interações.
   Prefira adaptar o markup/CSS/JS existente a recriá-lo por aparência.
4. Monte um inventário curto com origem: foundations em uso, peças reutilizáveis,
   dobras reais e dependências. Categorias ausentes não viram exemplos fictícios.
5. Apresente os achados principais junto da primeira etapa implementada. Não
   transforme a inspeção em uma aprovação extra antes de produzir algo revisável.

## Organização do catálogo

A navbar tem três destinos: **Overview · Components · Layouts**. Foundations
integram o início de Components, sem uma quarta página ou aba superior.

Use um shell integrado de até 1440px, centralizado, com navbar no fluxo e sidebar
estrutural à esquerda. Sem menus flutuantes. Overview ocupa a área principal sem
sidebar. Components e Layouts têm sidebar com somente os nomes dos itens:
sem busca, apresentação institucional, rodapé promocional ou instruções redundantes.

Os links laterais trocam o conteúdo central: um painel por vez, nunca âncoras para
uma pilha de seções. Preserve link direto por hash, seleção ativa e voltar/avançar.
Um painel pode rolar se necessário; não desenhe uma barra fixa decorativa de rolagem.
O escopo é desktop. Não crie nem valide versões mobile, menus hamburger ou
breakpoints adicionais. CSS responsivo já existente pode ser preservado sem
trabalho específico de adaptação; não o remova apenas para simplificar a extração.

A navegação do catálogo é uma adaptação estrutural solicitada, não um componente
extraído. Seus rótulos funcionais e indicadores de estado são texto documental
permitido. Reaproveite tipografia, materiais e estados da navegação/controles
observados. Se não houver referência suficiente, apresente essa lacuna para decisão
na entrega de Components; não crie silenciosamente uma nova linguagem visual.

## Estrutura de saída e assets

Use esta estrutura final. Crie arquivos e subpastas opcionais somente quando
houver conteúdo extraído que os justifique:

```text
<destino>/
  index.html                  # Overview: somente a hero de apresentação
  components.html             # Foundations primeiro, depois peças completas
  layouts.html                # Dobras reais, uma por seleção
  assets/
    css/
      foundations.css         # Fontes, tokens e regras atômicas observadas
      components.css          # Aparência, variantes e estados das peças
      layouts.css             # Composições da Overview e das dobras
      catalog.css             # Navbar, sidebar e estrutura documental
    js/
      catalog.js              # Seleção de painel, hash e histórico
      interactions.js         # Comportamentos extraídos, quando existirem
    fonts/                    # Arquivos locais usados e suas licenças
    icons/                    # SVGs e sprites de ícones
    images/                   # Marca, fotos, screenshots e texturas em imagem
    media/                    # Vídeos e áudios
    scenes/                   # Cenas, modelos 3D, shaders e dados de efeitos
    vendor/                   # Runtimes/SDKs necessários e suas licenças
```

Os nomes acima definem responsabilidades; preserve módulos CSS/JS adicionais
do original quando isso evitar reescrita ou quebra. Não precisa concatenar tudo.
`scenes/` pode conter JSON como asset real do efeito, não como documentação
paralela. SVG inline e shaders embutidos podem continuar no markup/script original.

O pacote deve funcionar após mover apenas `<destino>` para outro diretório:

- Copie do original todas as dependências necessárias aos elementos selecionados,
  inclusive as indiretas: `@import`, `url()`, `srcset`, posters, máscaras, texturas,
  fontes/pesos em uso, cenas e recursos carregados dinamicamente pelo runtime.
- Tudo além dos HTMLs de entrada fica em `assets/`, no tipo correspondente.
  Preserve subárvores de um SDK quando ele depender de caminhos internos fixos.
- Reescreva caminhos para relativos à saída. Não use symlinks, caminhos absolutos,
  referências à pasta original/DS anterior, CDN ou projeto remoto como dependência.
- Não copie `node_modules` inteiro, builds antigos ou assets que não participem
  dos elementos extraídos. Preserve bytes e licenças; evite recompressão sem necessidade.
- Se um recurso exigido não estiver no original local, relate a ausência. Um
  link externo não é uma cópia autocontida. Não invente substituto nem declare o
  pacote completo; explicite o recurso pendente e obtenha-o apenas se autorizado.
- Prefira HTML que abra diretamente em `file://`. Se uma capacidade original
  exigir HTTP, mantenha todas as dependências locais e informe o comando mínimo
  para servir a pasta; não exija o framework ou servidor do projeto de origem.

## Conteúdo de cada parte

Esta lista orienta a busca e a classificação; não obriga criar categorias sem
evidência. Dentro de Components, foundations e peças compartilham a mesma sidebar.

| Parte | O que apresentar, quando observado |
|---|---|
| Foundations / Tipografia | Famílias realmente usadas, arquivos/pesos, assinaturas de títulos, apoio, corpo, labels e metadados; aplicação original e escala de tamanho em três larguras; exemplos com copy e efeitos originais. |
| Foundations / Cores | Paletas e tokens originais, cores de texto/fundo/ação e suas aplicações comprovadas; transparências e variações de tema existentes. |
| Foundations / Espaçamento | Distâncias recorrentes, paddings, gaps, larguras de container, colunas e alinhamentos; valores observados, sem completar uma escala imaginária. |
| Foundations / Superfícies e efeitos | Raios, bordas, sombras, transparências e gradientes compartilhados; vidro, blur e glow apenas onde existirem. |
| Foundations / Ícones e movimento | Ícones usados com seus tamanhos/traços; durações, easing e keyframes compartilhados. O efeito completo permanece no componente que o demonstra. |
| Components / Ações e navegação | Botões, links, controles, tabs, menus e outros elementos reais, incluindo variantes e estados encontrados. |
| Components / Texto e conteúdo | Composições de eyebrow, título, apoio e CTA; badges, listas, prova social e grupos de conteúdo existentes. |
| Components / Cards e superfícies | Cards reais de conteúdo, preço ou benefício; materiais, bordas, halos, ícones e efeitos do componente completo. |
| Components / Entrada, feedback e dados | Inputs, seletores, validação, accordion, dialog, avisos, tabelas ou gráficos somente se presentes. Não incluir por convenção. |
| Components / Mídia e fundos | Imagens em seus frames, players, avatares, carrosséis e backgrounds reutilizáveis; camadas, assets e interações completos. |
| Overview | Uma única hero baseada na original, com tipografia, apoio, botões, mídia e fundo extraídos. Sem resumo documental, catálogo de amostras ou rodapé inventado. |
| Layouts | Dobras efetivamente presentes: hero, apresentação, grade de conteúdo, benefícios, mídia, preços, FAQ etc. Preserve a composição e a hierarquia de cada dobra; não invente outras páginas. |

Cada foundation apresenta valor + uso observado; cada componente, implementação
renderizada + variantes/estados comprovados; cada layout, composição real das
peças. Registre a origem no código, sem encher a interface de detalhes técnicos.
Use os mesmos estilos, scripts e assets compartilhados nas três páginas.

## Etapas e aprovações

Execute somente a etapa atual. Ao terminar, valide, entregue um link/arquivo
revisável e peça aprovação específica antes de implementar a próxima. Correções
mantêm a mesma etapa. Aprovação prévia explícita continua válida; não a peça de novo.
Na retomada, confira os arquivos e as decisões já aprovadas, sem reiniciar o processo.

### 1. Components completo, com navegação e fundo

Esta é uma única entrega: shell → foundations → peças completas. Faça os três
passos abaixo sem pedir aprovação intermediária. A primeira aprovação acontece
com `components.html` navegável e seus exemplos reais.

#### 1a. Shell: navbar, sidebar e fundo

Construa a estrutura do catálogo e o fundo observado, incluindo seus assets e
efeitos. Mostre na sidebar apenas itens confirmados pelo inventário. Destinos
ainda não implementados ficam claramente indisponíveis, sem links quebrados ou
conteúdo fictício. Não fabrique a hero nesta etapa. Continue direto para foundations.

#### 1b. Foundations primeiro

Comece a página Components pelas regras atômicas efetivamente encontradas:
tipografia, cores, espaçamento/containers, bordas/raios/sombras, gradientes,
iconografia e parâmetros de movimento, somente quando houver evidência de uso.
Não force todas essas categorias em toda extração.

Renderize as assinaturas tipográficas com trechos reais do site. Mostre valores
reais e suas origens. Não invente níveis H1–H6, cores de erro/sucesso, escalas de
espaçamento ou famílias de ícones ausentes. Efeitos exclusivos permanecem junto
do componente proprietário; apenas regras compartilhadas entram como foundations.
Continue para as peças completas, sem aprovação isolada de foundations.

##### Formato obrigatório da seção Tipografia

Apresente as assinaturas tipográficas em uma lista vertical, com uma linha por
estilo observado e divisórias discretas entre as linhas. Não envolva cada estilo
em um card. Ordene da maior hierarquia visual para a menor e mantenha papéis de
interface, metadados e labels depois dos títulos e textos principais.

Cada linha possui três áreas:

1. **Identificação, à esquerda:** mostre o papel do estilo, como `Heading 1`,
   `Heading 2`, `Text 1`, `Button`, `Meta` ou `Label`. Derive o papel da tag,
   classe e uso real; não crie níveis ausentes. Logo abaixo, mostre somente a
   família e o peso observados, por exemplo `Inter · peso 500`.
2. **Aplicação, no centro:** renderize um trecho real usando o HTML interno e os
   estilos do original. Preserve spans, ênfases, gradientes de texto, cores,
   tracking, transformações e outros efeitos aplicáveis; não reduza o exemplo a
   texto plano. Respeite a largura necessária para demonstrar a quebra original.
3. **Escala, à direita:** mostre apenas os três `font-size` medidos do maior para
   o menor viewport, separados por barras verticais, como
   `64px | 64px | 44px`. Não escreva `Desktop`, `iPad`, `Tablet`, `Mobile` nem
   cabeçalhos equivalentes: a ordem já comunica a escala. Não misture entrelinha
   nessa coluna.

Meça os três tamanhos no site original renderizado, em uma largura ampla, uma
intermediária e uma estreita. Use `1440px`, `1024px` e `390px` quando o projeto
não indicar viewports de referência mais apropriados. Se o tamanho não mudar,
repita o valor medido; nunca fabrique uma progressão. Essa leitura estreita serve
somente para documentar a escala tipográfica e não amplia o escopo para construir
ou fazer QA da interface mobile.

Os demais dados comprovados — entrelinha, tracking, cor, seletor, arquivo e
viewports de medição — permanecem aplicados ao exemplo ou registrados na origem
do código (`data-source`/comentário), sem tornar a interface da tabela verbosa.

#### 1c. Peças completas

Acrescente as peças observadas após os foundations: botões, links, grupos de texto,
cards, navegação, mídia, formulários e outras que existam. Preserve variantes e
estados comprovados, texto, ícones, camadas, efeitos e comportamento.

Exiba os componentes sobre o fundo apropriado, sem envelopar cada exemplo em um
card genérico. Um grupo de título + apoio + CTA pode ser um componente quando
essa composição existe na origem. Backgrounds implementados como peças reutilizáveis
podem ter seu próprio item. **Entregue navbar, sidebar, fundo e Components juntos
e peça aprovação antes de compor a Overview.**

### 2. Overview

Monte somente uma hero de apresentação com os elementos já extraídos e aprovados,
baseada na composição da hero original. Preserve proporções, hierarquia, títulos,
textos de apoio, botões e mídia existentes. Impacto vem da identidade observada;
não aumente arbitrariamente a tipografia nem acrescente estrelas, selos, linhas,
slogans, rodapés ou estatísticas.

Mantenha a copy original até o usuário fornecer/aprovar uma adaptação para o DS.
Se um CTA apontar para uma seção extraída, adapte apenas seu destino para o painel
correspondente; não simule checkout/envio ou deixe ações quebradas. Informe as
limitações de demonstração. **Peça aprovação da Overview.**

### 3. Layouts

Apresente dobras reais do site, com os componentes extraídos aplicados às suas
composições originais. A sidebar seleciona uma dobra por vez. Cada dobra ocupa
toda a área central disponível, sem thumbnail, moldura de navegador ou card
externo que comprima o layout. Não invente dashboard, workspace ou outra aplicação.
Preserve o arranjo desktop da origem. **Peça aprovação de Layouts.**

## Como acelerar sem perder fidelidade

- Faça uma inspeção inicial por página relevante: capture em lote estilos
  computados de elementos representativos, pseudo-elementos, fontes, assets e
  estados. Percorra a página para revelar conteúdo lazy e efeitos antes de fechar
  o inventário. Evite reabrir a origem para cada propriedade ou ler arquivos enormes
  inteiros quando busca por seletor/import resolve.
- Agrupe itens pela mesma implementação/classe e assinatura visual. Extraia um
  representante por família e suas variantes reais; não trate cada card repetido
  como componente novo. Não expanda a análise a todas as rotas de um projeto quando
  elas não acrescentarem variantes ao escopo solicitado.
- Reaproveite DOM renderizado, CSS, SVG e JS do original. Prefira exportar/adaptar
  o componente existente a reconstruí-lo manualmente ou redesenhar a partir de uma
  screenshot. Capture também os estilos herdados necessários e o contexto de fundo.
- Resolva a cadeia de dependências e copie os assets em lote. Use hashes para
  deduplicar quando necessário e mantenha os nomes originais sempre que possível.
- Mantenha um único servidor original e uma sessão de navegador durante a inspeção.
  Faça leituras e verificações independentes em paralelo quando as ferramentas
  permitirem, sem exigir subagentes para uma extração simples.
- Valide uma viewport desktop consistente, estados distintivos e recursos locais
  por entrega. Repita apenas o que foi alterado ou falhou. Sem QA mobile, pipeline
  de screenshots em massa, build de toda a aplicação ou testes extensivos sem motivo.
- Use scripts curtos de extração ou geração quando reduzirem trabalho repetitivo.
  Se forem necessários para editar/regenerar a saída, inclua-os em `assets/js/tools/`;
  o consumo dos HTMLs continua independente deles. Não crie ferramentas genéricas
  complexas antes de entregar a extração pedida.

Velocidade vem de copiar implementações comprovadas e eliminar trabalho repetido,
nunca de omitir dependências, usar placeholders ou estimar valores visuais.

## Entrega e conferência por etapa

Use HTML/CSS/JS e assets locais, sem exigir o framework original para consumir o
resultado, seguindo a estrutura acima. Crie cada página quando chegar sua etapa;
na primeira entrega, abra `components.html`. Reserve `index.html` para a Overview,
sem criar páginas vazias. Preserve licenças dos assets copiados.

Compare cada etapa com a origem na mesma viewport desktop. Confira fontes e
valores computados além da imagem; confirme assets carregados, estados, teclado,
movimento reduzido e ausência de overflow/cortes. Teste seleção de painel e histórico
quando disponíveis. Não afirme fidelidade visual com base apenas em ler o CSS.
Na conferência de portabilidade, abra uma cópia da pasta de saída fora do projeto
original, bloqueie requisições externas e verifique assets, efeitos e navegação.
Verifique também caminhos em CSS/JS e recursos lazy usados pelos exemplos; a
ausência de erros no primeiro frame não comprova que o pacote está autocontido.

Não reative tracking, checkout ou envios reais ao transportar interações. Preserve
efeitos visuais locais; declare uma dependência indisponível em vez de substituí-la
por outro efeito. Se o navegador/asset necessário estiver inacessível, relate o
que foi e não foi verificado na entrega da etapa.

No pedido de aprovação, indique a etapa concluída, o acesso ao resultado, as
limitações concretas e qual etapa vem depois. Não avance automaticamente.
