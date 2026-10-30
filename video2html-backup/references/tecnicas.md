# Técnicas por tipo de problema

Receitas para o passo 3 (separar em camadas) e o passo 4 (dar vida). Cada seção diz **quando usar**, **como fazer** e
**o que observar**.

## Medir

**Quando:** sempre, antes de posicionar qualquer coisa.

- **Geometria:** extraia da referência com análise de imagem em vez de estimar a olho. Um arco ou anel: pegue os pontos claros
  dele e ajuste centro e raio por mínimos quadrados. Nós e ícones: ache os blobs claros e use os centros.
- **Texto:** compare a caixa de tinta do texto na referência com a da página (posição e largura) e ajuste fonte, tamanho e
  espaçamento até ficar a ±2 px.
- **Itens repetidos:** guarde as coordenadas num lugar só (uma lista no JS ou um script que gera o HTML). Mudar um item não
  pode exigir caçar cópias.

## Placa de fundo

**Quando:** o fundo tem elementos que vão se mexer (personagem, objeto, arte) e precisa existir sem eles.

- Peça a um modelo de imagem a referência **sem** os elementos vivos ("remove the robot, keep everything else
  pixel-identical"). Use uma proporção suportada pelo modelo; se a referência tiver outra, gere numa próxima e recorte.
- Uma máscara radial suave na placa esconde o que o modelo deixou "vazar" em volta do objeto removido.
- Tramas decorativas que não se mexem (grades, marcas, glifos) ficam na placa. Por cima, em SVG, só o que vive.

## Personagem ou objeto recortado

**Quando:** há uma figura central (robô, mascote, produto) que precisa se mexer separada do fundo.

- Recorte pixel a pixel com
  `uvx --python 3.12 --from "rembg[cpu,cli]" rembg i -m birefnet-general recorte.png saida.png`. Roda local; o modelo tem
  ~1 GB na primeira vez.
- Camada 2D com efeitos (brilho, flutuação, inclinação leve) resolve a maioria dos casos.
- Para reagir em volume (virar para o cursor), use **2.5D**, abaixo.

## 2.5D com mapa de profundidade

**Quando:** a figura precisa girar alguns graus e parecer ter volume.

- Gere o mapa de profundidade do recorte com um modelo de imagem: "depth map aligned pixel-for-pixel, white = closest, black =
  farthest, smooth, no details".
- Em Three.js: um `PlaneGeometry` bem subdividido com a textura do recorte e um `ShaderMaterial` que desloca o z de cada
  vértice pelo mapa.
- Gire em torno de um pivô no "pescoço", não no centro da imagem.
- **Limite:** ~14° para os lados e ~9° para cima e para baixo. Mais que isso, a silhueta deforma.
- **Olhar para o cursor:** calcule a direção do olho da figura até o cursor (em px da tela, com uma distância virtual de
  ~500 px) e converta em ângulos. Para o olhar ficar convincente, desloque também a íris alguns px na mesma direção: no shader,
  distorça só a região do olho, com uma queda suave até a borda do soquete.

## Arte fina luminosa

**Quando:** filamentos, circuitos, neurônios, molduras finas e brilhantes, que uma segmentação comum não recorta bem.

1. Gere a placa sem a arte.
2. `uv run scripts/isolar_camada.py reference.png placa.png assets/arte.png --excluir "x,y,w,h;…"` isola a arte clara. Exclua
   só o que vai virar HTML/SVG (textos, anéis, gráficos).
3. Use a camada com `mix-blend-mode: screen` sobre a placa: placa + camada = a referência.
4. Para sinais que **andam pelo desenho** (faíscas, pulsos): `uv run scripts/caminhos.py assets/arte-mascara.png
   assets/caminhos.json --centro x,y`. Antes, corte da máscara o chão, as réguas e as molduras. Anime ao longo das polilinhas
   do JSON.
5. **Onda de cor que se espalha:** uma segunda cópia da camada, tingida (`sepia + saturate + hue-rotate`), revelada por uma
   máscara radial que cresce. `mix-blend-mode: saturation` sobre a camada tira a cor de um trecho.

## Fundo claro (tinta sobre papel)

**Quando:** a arte é escura sobre fundo claro, com pontos de luz.

- `isolar_camada.py --modo duplo --limiar 0` gera `-escura.png` (use com `multiply`) e `-clara.png` (use com `screen`).
  Placa × escura + clara reproduz o fundo inteiro.
- Para dividir a camada escura em partes (objeto, reflexo, resto), use **máscaras binárias complementares**. Bordas suaves nas
  duas máscaras criam um anel claro na emenda.

## Objeto redondo vivo (esfera, planeta, orbe)

**Quando:** um objeto esférico da referência precisa girar ou respirar.

- `SphereGeometry` com **projeção frontal** da textura: o uv de cada vértice é a posição dele no plano da imagem, fixado no
  vértice, então o desenho gira junto.
- Câmera **ortográfica**: a perspectiva amplia o centro (~14 %) e a esfera parada deixa de bater com a referência.
- Desloque a câmera meio pixel, para cada pixel cair no centro de um texel: parado, fica nítido.
- Estenda a textura além da borda com a cor da borda: girar nunca revela branco.
- Linhas ou objetos que cruzam a esfera e não giram precisam sair da textura (clone a área em volta), senão giram junto.

## Cena inteira em código

**Quando:** o pedido é "construa no código" em vez de "anime a imagem", ou o objetivo é um fundo vivo no nível de páginas como
as de design systems em WebGL.

- Um canvas WebGL em tela cheia, câmera ortográfica em px da referência.
- A imagem vira só **placa** e **distribuição**: sorteie pontos pela escuridão (ou pelo brilho) da arte e anime cada um no
  vertex shader. Dá para salvar os pontos num `.bin` (Float32: x, y, intensidade).
- Peças que funcionam:
  - um corpo esférico traçado por pixel num quad (normal + rotação), com manchas em fbm que giram junto;
  - uma nuvem de pontos com o raio deformado por ruído simplex;
  - um fundo em fbm com domain warp;
  - fios de partículas até os elementos ativos;
  - uma onda que sai do centro a cada evento.
- **Fundo claro em WebGL:** a tinta escurece (blending `dst × cor`: `blendSrc: ZeroFactor`, `blendDst: SrcColorFactor`, saída
  `mix(1, cor, a)`) e a luz soma (aditivo). Uma cor viva sobre papel precisa de duas passadas: uma tinge, a outra soma o
  núcleo.

## Tremor e água em arte estática

**Quando:** a arte é uma imagem, mas o vídeo mostra ela tremendo, ondulando ou escorrendo.

- Filtro SVG `feTurbulence` + `feDisplacementMap` (escala de 2 a 8 px), com `seed` e `baseFrequency` mudando por JS.
- Desligue no `?estatico`.

## Conectores e feixes de luz

**Quando:** linhas que ligam elementos e uma luz que corre por elas.

- Em repouso, a linha fica **fraca**. Se ela já brilha, a luz passando não se lê.
- A luz "enche" a linha (`stroke-dasharray` animado), segura acesa ~1,5 s e decai. Funciona melhor que um cometa curto.
- O elemento de destino reage quando a luz chega (flare, anel que acende).
