# Armadilhas conhecidas

Erros que já custaram tempo. Leia antes de usar WebGL ou de gravar a verificação.

## Three.js e shaders

- **Espaço de cor:** `ShaderMaterial` não converte cores. Para os pixels saírem iguais aos da imagem, use a textura com
  `colorSpace = NoColorSpace` e `renderer.outputColorSpace = LinearSRGBColorSpace`.
- **Recorte com transparência:** devolva a cor **pré-multiplicada** (`gl_FragColor = vec4(rgb * a, a)`). Sem isso, o fundo do
  recorte aparece como um retângulo.
- **Bloom descarta o alfa:** o `UnrealBloomPass` deixa o canvas opaco. Renderize o objeto num canvas transparente e o brilho
  num **segundo canvas** (só as partes claras, sobre preto), sobreposto com `mix-blend-mode: screen` e uma máscara radial.
  Sem `OutputPass` nessa camada, senão tudo clareia.
- **Números no GLSL:** ao montar shaders com template strings, `${x}.0` vira `616.5.0` quando `x` já tem casa decimal. Use
  `const f = (v) => (Number.isInteger(v) ? v + '.0' : String(v))`.
- **Pontos que não aparecem:** um `THREE.Points` cujo vertex shader não lê o atributo `position` pode não desenhar nada
  (Chrome/ANGLE). Some `position.xy` à posição, mesmo que seja zero.
- **Cursor empurrando partículas:** um deslocamento que não vai a zero no centro do cursor abre um buraco nítido. Use uma queda
  que é zero no centro e na borda (ex.: `x·(1−x)²`), ou gire as partículas em volta do cursor em vez de afastá-las. O mesmo
  vale para distorções do fundo em shader.
- **Cache:** se o servidor manda o JS com cache longo, o navegador roda a versão velha. Sirva código sem cache.

## GSAP e SVG

- Não ponha `transform-box` ou `transform-origin` no CSS de elementos SVG que o GSAP escala: ele passa a escalar a partir de
  (0, 0). Para círculos, prefira animar `attr: { r }`.
- A linha do tempo do ocioso precisa **reiniciar o estado no tempo 0**: o que ela ativou no meio, ela desativa.
- Cada disparo encerra o anterior do mesmo elemento (`gsap.killTweensOf`), senão as animações se acumulam.

## Gravação e verificação

- `page.evaluate` que devolve um objeto do GSAP trava o Playwright. O `gravar.py --antes` já embrulha o JS para evitar isso.
- Um erro de JavaScript faz o `window.vida` não existir e o `--antes` falhar. Abra a página e leia o console antes de gravar.
- Movimento "global" no vídeo (a tela inteira acende de uma vez) aparece no comparador como muitas regiões paradas. Ele só some
  quando a camada inteira participa (uma onda de cor, o brilho da camada no pico), não só os detalhes.
- O modelo multimodal erra eventos curtos e às vezes afirma que algo não acontece. Confira nos quadros antes de mudar a página
  por causa dele.
