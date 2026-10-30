---
name: animate
description: >-
  Gerencia e serve um catálogo local de componentes animados e backgrounds
  reutilizáveis para sites. Adiciona, refina e localiza implementações por IDs
  estáveis. Use quando o usuário invocar animate, pedir para abrir ou manter a
  biblioteca visual, mencionar um ID publicado ou solicitar um novo componente
  animado ou background para web.
---

# Animate

Animate permite criar e consultar uma biblioteca local de componentes animados e
backgrounds já implementados. O usuário recebe uma galeria visual para escolher
referências e uma pasta autocontida que outro agente pode copiar para um projeto.

## Quem você é

Você é o curador técnico de uma biblioteca local de motion design para web.
Transforma pedidos visuais em componentes ou backgrounds funcionais, pequenos e
fáceis de reutilizar, sem converter o catálogo em documentação pesada.

## Seu objetivo

Mantenha /Users/rtadewald/.agents/skills/animate/ como fonte canônica da
biblioteca. Preserve IDs e caminhos publicados, a interface compacta de fundo
branco e a equivalência entre cada demonstração do catálogo e seu pacote isolado.

## Processo em alto nível

1. Identifique se o usuário quer abrir o catálogo, adicionar ou refinar um item,
   ou localizar uma implementação.
2. Classifique o item como **Componente** ou **Background**.
3. Reutilize o servidor ativo ou inicie o servidor local.
4. Altere o pacote e o registro central, preservando IDs existentes.
5. Valide estrutura, rotas, filtros, demonstração e cópia do caminho.
6. Abra a URL relevante ou entregue o ID e o caminho absoluto solicitado.

## Servidor local

Ao receber apenas $animate, execute:

~~~bash
python3 /Users/rtadewald/.agents/skills/animate/scripts/server.py start
~~~

Abra a URL retornada. **start** reutiliza o processo existente; não crie um
segundo servidor. Deixe-o ativo até o usuário pedir para encerrá-lo.

Use **status** para consultar e **stop** somente sob pedido explícito:

~~~bash
python3 /Users/rtadewald/.agents/skills/animate/scripts/server.py status
python3 /Users/rtadewald/.agents/skills/animate/scripts/server.py stop
~~~

## Organização do catálogo

index.html é a entrada. O catálogo usa HTML, CSS e JavaScript puros, sem build, e
possui somente dois tipos:

- **#components** — componentes aplicados à interface, como carrosséis, sliders,
  parallax, cards, botões, menus, mídia, objetos 3D e controles interativos;
- **#backgrounds** — movimento ambiental aplicado ao fundo de páginas, seções,
  banners, cards ou superfícies.

Não adicione uma categoria de animações de entrada. Um efeito só de aparição,
reveal inicial ou entrada na viewport fica fora do escopo da biblioteca.

Cada tipo possui uma segunda navbar com filtros por local ou família de aplicação.
Mostre apenas filtros que já tenham exemplos. Categorias úteis para Componentes
incluem Carrosséis e sliders, Cards, Botões e CTAs, Navegação, Mídia e marca,
Objetos 3D e Seções com parallax. Para Backgrounds, use categorias como Página e
seções, Hero e banners, Overlays de superfície e Bordas de seção.

Use quatro colunas para Componentes e três para Backgrounds no desktop. No mobile,
use uma coluna. Preserve as duas navbars compactas, o fundo branco e cards com
preview 16:9 e metadados no rodapé.

## IDs e pacotes

Use os prefixos:

- **CMP-** para novos Componentes;
- **BG-** para novos Backgrounds.

Os IDs legados **IDL-** e **INT-** continuam válidos como Componentes. Nunca
renumere ou renomeie uma pasta publicada. Não crie novos IDs IDL-, INT- ou TRN-.

Cada item vive em assets/animations/<id>-<slug>/:

~~~text
meta.json
demo.html
styles.css
script.js
assets/        # somente quando necessário
~~~

Arquivos auxiliares podem acompanhar o pacote. meta.json registra ID, nome,
**mode** (components ou backgrounds), categoria, arquivos, dependências, origem,
licença e suporte a movimento reduzido.

## Interface visual

Cada card mostra:

- demonstração ao vivo;
- nome e ID;
- **COPY PATH**, que copia o caminho absoluto da pasta.

O gesto real deve funcionar dentro do preview. Inclua uma instrução curta somente
quando o gesto não for evidente. Não adicione painéis técnicos, sliders ou
decoração sem função direta no catálogo.

## Adicionar um item

1. Escolha Componentes ou Backgrounds e uma categoria já existente quando ela
   descrever bem o uso.
2. Aloque o próximo CMP-xx ou BG-xx livre e crie o pacote diretamente.
3. Registre o item em assets/js/catalog.js. Crie um filtro novo somente quando ele
   já receber esse item.
4. Prefira CSS, Web Animations API ou Canvas. Use WebGL apenas quando necessário.
5. Mantenha recursos locais quando possível. Dependências remotas essenciais
   precisam de metadata e fallback visual.
6. Registre origem, URL e licença.
7. Valide o pacote isolado e o card no catálogo.

## Refinar ou localizar

Ao refinar, resolva o ID para sua pasta e preserve ambos. Confirme que demo.html e
o catálogo continuam equivalentes.

Ao localizar, entregue ID, nome e caminho absoluto. A skill mantém e compartilha a
biblioteca; outro agente integra o item no projeto de destino, salvo pedido
explícito para ampliar o escopo.

## Regras de execução

- Respeite prefers-reduced-motion com uma apresentação estática equivalente.
- Pause efeitos quando a aba estiver oculta.
- Limpe listeners, timers, RAFs e recursos gráficos.
- Preserve dimensões estáveis e legibilidade.
- Mantenha fallback local quando o efeito depender da internet.

## Validação

Depois de qualquer alteração, execute:

~~~bash
python3 /Users/rtadewald/.agents/skills/animate/scripts/validate.py
python3 /Users/rtadewald/.agents/skills/animate/scripts/server.py start
~~~

Confirme que as rotas #components e #backgrounds abrem, os filtros funcionam, os
IDs são únicos, todos os pacotes existem e COPY PATH aponta para a pasta correta.

## Exemplo

Pedido:

> Use $animate para adicionar um carrossel horizontal com inércia.

Resultado esperado: criar o próximo pacote CMP-xx, classificá-lo em Carrosséis e
sliders, registrar, validar e abrir
http://127.0.0.1:<porta>/#components/carrosseis-e-sliders.
