# Animate — Especificação

## Visão

Animate é uma skill e um catálogo local de componentes animados e backgrounds
reutilizáveis para sites. A galeria permite avaliar exemplos ao vivo e copiar o
caminho absoluto de uma implementação para uso por outro agente.

## Responsabilidades

- iniciar, reutilizar e manter o servidor local;
- abrir o catálogo quando invocada sem outro pedido;
- adicionar, refinar, classificar e validar itens;
- preservar IDs e caminhos publicados;
- fornecer o caminho absoluto de qualquer implementação.

## Tipos

O catálogo possui apenas:

1. **Componentes** (#components) — elementos aplicados à interface: carrosséis,
   sliders, parallax, cards, botões, menus, mídia, objetos 3D e controles;
2. **Backgrounds** (#backgrounds) — atmosferas aplicadas ao fundo de páginas,
   seções, banners, cards e outras superfícies.

Animações exclusivamente de entrada, reveal inicial ou entrada na viewport não
fazem parte do catálogo.

## Navegação e filtros

- A primeira navbar contém ANIMATE, Componentes e Backgrounds.
- A segunda navbar contém filtros do tipo ativo.
- Todos exibe a grade completa; os demais filtros reduzem a mesma grade.
- Categorias descrevem onde ou como o item é aplicado, não sua tecnologia.
- Filtros vazios não são criados.

Vocabulário inicial para Componentes:

- Carrosséis e sliders;
- Cards;
- Botões e CTAs;
- Navegação;
- Mídia e marca;
- Objetos 3D;
- Seções com parallax.

Vocabulário inicial para Backgrounds:

- Página e seções;
- Hero e banners;
- Overlays de superfície;
- Bordas de seção.

## Layout

- Fundo branco e duas navbars compactas alinhadas à esquerda.
- Tipografia Archivo.
- Cards com borda suave, preview 16:9 e rodapé com nome, ID e COPY PATH.
- Componentes: quatro colunas no desktop.
- Backgrounds: três colunas no desktop.
- Mobile: uma coluna e navbars horizontalmente roláveis.

## IDs

| Tipo | Prefixo novo | Observação |
| --- | --- | --- |
| Componentes | CMP- | IDL- e INT- permanecem como IDs legados |
| Backgrounds | BG- | preservado |

IDs publicados nunca são renumerados ou reutilizados. TRN- está aposentado e não
deve ser criado.

## Estrutura

~~~text
animate/
├── SKILL.md
├── SPECS.md
├── index.html
├── agents/openai.yaml
├── assets/
│   ├── animations/<id>-<slug>/
│   │   ├── meta.json
│   │   ├── demo.html
│   │   ├── styles.css
│   │   ├── script.js
│   │   └── assets/
│   ├── css/
│   ├── js/
│   └── runtime/
└── scripts/
    ├── server.py
    └── validate.py
~~~

O runtime usa HTML, CSS e JavaScript puros. HTTP local é necessário para módulos,
fetch, Canvas e WebGL.

## Servidor

- Endereço padrão: 127.0.0.1:4173.
- Reutilizar o servidor ativo.
- Se a porta estiver ocupada, usar a próxima livre.
- Não expor na rede local.
- Manter ativo até pedido explícito de encerramento.
- Registrar estado em /tmp/animate-server.json.

## Pacote

Exemplo:

~~~json
{
  "id": "CMP-01",
  "name": "Inertial carousel",
  "mode": "components",
  "category": "Carrosséis e sliders",
  "entry": "demo.html",
  "files": ["demo.html", "styles.css", "script.js"],
  "dependencies": [],
  "source": { "name": "Implementação local", "url": "", "license": "Revisar" },
  "accessibility": { "reducedMotion": true }
}
~~~

COPY PATH copia a pasta absoluta, não código nem uma instrução composta.

## Conteúdo ativo

- 6 Componentes com IDs legados preservados;
- 12 Backgrounds.

Novos Componentes usam CMP-. Os antigos exemplos de entrada foram removidos da
biblioteca ativa.

## Performance e acessibilidade

- Respeitar prefers-reduced-motion.
- Pausar efeitos quando a aba estiver oculta.
- Efeitos pesados podem pausar fora da viewport.
- Recursos gráficos, listeners, timers e RAFs devem possuir cleanup.
- Dependências remotas precisam de fallback local quando possível.

## Fluxos

### Abrir

1. Consultar o servidor.
2. Reutilizar ou iniciar.
3. Abrir o catálogo.

### Adicionar

1. Escolher Componentes ou Backgrounds.
2. Escolher a categoria por uso.
3. Alocar o próximo ID.
4. Criar pacote e registrar.
5. Validar pacote, filtro e rota.

### Refinar

1. Resolver o ID.
2. Editar o pacote.
3. Preservar ID e caminho.
4. Validar catálogo e demo isolado.

### Compartilhar

1. Localizar o card.
2. Clicar em COPY PATH.
3. Colar o caminho para o agente de integração.
