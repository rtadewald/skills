# Layouts

<<<<<<< ours
Leia este arquivo somente depois da aprovação de Components.
=======
Leia este arquivo somente depois de implementar e verificar Components.
>>>>>>> theirs

## Definição

Layouts são arranjos reutilizáveis que organizam Components no espaço para formar partes completas de uma interface. Eles definem hierarquia, alinhamento, densidade, largura, grid, colunas, ritmo entre regiões e comportamento responsivo.

Exemplos possíveis incluem hero, feature grid, pricing, login, dashboard shell, dashboard header, settings, navigation layout, profile e empty state. Extraia somente arranjos presentes ou necessários para preservar a identidade da fonte.

Um card ou navbar isolado é Component. Navbar + headline + CTA + mídia + background formando uma hero é Layout. Uma linha casual com dois botões não precisa virar Layout se não tiver valor reutilizável.

## Construção

<<<<<<< ours
Use `data-ds-section="layout"`. Cada Layout deve utilizar os Components, classes, Foundations, motions e assets reais já aprovados. Não duplique um componente com markup alternativo apenas para fazê-lo caber no exemplo.
=======
Use `data-ds-section="layout"`. Cada Layout deve utilizar os Components, classes, Foundations, motions e assets reais já extraídos. Não duplique um componente com markup alternativo apenas para fazê-lo caber no exemplo.
>>>>>>> theirs

Para cada Layout, torne claros:

- finalidade e contexto de uso;
- Components e variantes usados;
- grid, containers, colunas, gaps e alinhamentos;
- assets que pertencem ao arranjo completo;
- comportamento responsivo observado; e
<<<<<<< ours
- partes `inferred` ou `suggested`.
=======
- relações ou nomes semânticos marcados como `inferred` quando não forem explícitos no código.
>>>>>>> theirs

## Assets do layout

Backgrounds, ilustrações amplas, personagens 3D, WebGL, shaders, Canvas e texturas pertencem ao Layout quando servem à composição inteira. Os arquivos continuam em `assets/`, mas sua documentação e demonstração ficam dentro do Layout.

Um fundo global já copiado na casca pode ser reutilizado. Efeitos específicos de uma hero ou dashboard devem rodar apenas no preview correspondente. Para recursos complexos, use fallback estático quando ele trouxer benefício real; não crie uma versão paralela sem necessidade.

## Responsividade e fidelidade

<<<<<<< ours
Em HTML, preserve breakpoints e mudanças de arranjo observadas. Uma imagem de desktop não comprova comportamento mobile; qualquer reflow criado deve ser `suggested`. O catálogo em si deve continuar utilizável em viewport razoável, independentemente da responsividade extraída.

Preserve o que torna o arranjo reconhecível: hierarquia, ritmo, densidade, iluminação, background, mídia, 3D e relação entre componentes. Prefira poucos Layouts representativos a reconstruir todas as páginas da aplicação.

## Antes do gate de Layouts

Confirme que:

- todos os Layouts usam Components já aprovados;
=======
Preserve os breakpoints, media queries e mudanças de arranjo implementadas no HTML. Não invente reflow ou comportamento mobile ausente. O catálogo em si deve continuar utilizável em viewport razoável, independentemente da responsividade extraída.

Preserve o que torna o arranjo reconhecível: hierarquia, ritmo, densidade, iluminação, background, mídia, 3D e relação entre componentes. Prefira poucos Layouts representativos a reconstruir todas as páginas da aplicação.

## Verificação de Layouts

Confirme que:

- todos os Layouts usam Components já extraídos;
>>>>>>> theirs
- assets amplos aparecem no Layout proprietário;
- nenhuma responsividade foi apresentada como observada sem evidência;
- background e efeitos executam sem erros; e
- os exemplos ensinam como criar novas interfaces coerentes.

<<<<<<< ours
Depois, construa o Overview final, mostre o catálogo integrado e aguarde aprovação.
=======
Depois, revise o Overview contra as seções concluídas e faça a revisão final do catálogo.
>>>>>>> theirs
