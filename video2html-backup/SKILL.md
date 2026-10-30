---
name: video2html-backup
description: >-
  (Backup da primeira versão da video2html.) Recria uma interface a partir de um vídeo (gravação de tela, mock animado, vídeo gerado por IA) como um HTML vivo e
  interativo: lê o movimento do vídeo, monta um mapa do que se mexe, constrói a tela parada fiel à referência e anima tudo
  em código (CSS, SVG, Canvas, Three.js, GSAP), expandindo o movimento em interações reais, e prova o resultado gravando a
  página e comparando com o vídeo. Use só quando o usuário pedir video2html-backup explicitamente; para transformar um vídeo de interface num
  HTML animado, use a video2html.
disable-model-invocation: true
---

# Vídeo → HTML vivo

Transforma o vídeo de uma interface numa página HTML que **se mexe como o vídeo e responde ao usuário**. O vídeo mostra o
movimento (o que respira, acende, gira, quando); a página reproduz esse movimento em código e vai além dele: o cursor, os
cliques e as ações também animam a tela.

## Entradas e saída

**Entradas**
- **O vídeo** da interface (obrigatório).
- **A imagem de referência** (opcional): o quadro "oficial" da tela, quando existe. Por exemplo, a imagem a partir da qual um
  modelo de vídeo gerou o vídeo. Ela é a fonte do conteúdo (textos, layout, cores). Sem ela, o passo 1 extrai o quadro mais
  nítido do vídeo.
- **A pasta de saída.** Se o usuário não disser, pergunte. Se ele preferir não escolher, use `./<nome-da-tela>/`.

**Saída** (a pasta):

```
index.html                 a página; ?estatico congela no estado da referência
assets/                    styles.css, app.js, módulos (ex.: cena.js), imagens estáticas
reference.png              a referência
vida.md                    o mapa de vida (passo 2)
analise/                   o vídeo e as leituras dele
verificacao/               gravações e comparações (passo 5)
README.md                  o que vive, como foi feito, o que ficou de fora
```

## Regras

1. **O conteúdo vem da referência; o movimento vem do vídeo.** Textos, layout e cores seguem a imagem de referência. O vídeo
   diz o que se mexe, como e quando.
2. **O que o vídeo inventou não entra.** Em vídeos gerados por IA, rótulos que mudam de letra, textos que derretem, objetos que
   aparecem e somem são artefatos: registre-os no `vida.md` como "fora".
3. **Tudo que se mexe é código.** Nunca use o vídeo (ou um GIF) como camada: isso mata a interação. Imagens estáticas
   (placas de fundo, recortes, texturas) podem.
4. **Vá além do vídeo.** O movimento do vídeo vira o estado ocioso da página. Cada movimento é uma função que o ocioso chama e
   que as interações também chamam (passar o mouse, clicar, digitar).
5. **Use a técnica mais simples que convence:** CSS/SVG → Canvas 2D → WebGL (Three.js). Veja "Escolhendo a técnica".
6. **Prove com gravação.** "Parece certo" não vale: grave a página e compare com o vídeo (passo 5).

## Passo a passo

Os passos marcados com ✋ terminam mostrando o resultado ao usuário e esperando o "ok". Se o usuário pedir **modo
autônomo**, siga direto e registre as decisões nos arquivos.

### 1. Preparar a pasta

1. Crie a pasta de saída com `analise/`, `assets/` e `verificacao/`.
2. Copie o vídeo para `analise/video-ref.mp4`.
3. Ponha a referência em `reference.png`. Sem imagem, extraia um quadro do vídeo: escolha o mais nítido e completo, olhando a
   folha de quadros do passo 2, e salve com `ffmpeg -ss <segundo> -i analise/video-ref.mp4 -frames:v 1 reference.png`.
4. Sirva a pasta por http, por exemplo com `python3 -m http.server`. Texturas de WebGL não carregam de `file://`.

### 2. Ler o vídeo e escrever o mapa de vida ✋

1. **Onde, quanto e quando:** `uv run scripts/mapa_movimento.py analise/video-ref.mp4 analise --largura-ref <largura da
   referência>`. Gera `movimento.png` (as regiões que se mexem, numeradas), `regioes.json` (caixa, picos e período de cada uma),
   `curvas.png` e `quadros/` (um quadro por região e uma folha com 9 quadros).
2. **O quê e como:** `uv run scripts/analisar_video.py analise/video-ref.mp4 analise/gemini.md`. Um modelo multimodal descreve
   cada movimento, o ritmo e os artefatos, por centavos.
3. **Junte as duas leituras olhando os quadros:**
   - agrupe as regiões em elementos (vários pedaços de um anel viram "anel");
   - confirme os tempos (o tempo fino vem do mapa de movimento, não do modelo);
   - separe os artefatos.
4. Escreva o **`vida.md`** (modelo em `references/vida.exemplo.md`):
   - o ritmo geral, em duas ou três frases;
   - uma tabela **elemento | o que faz no vídeo | interação que vamos criar | técnica**;
   - a linha do tempo do ocioso, em texto;
   - o que fica de fora.
5. ✋ Mostre o `vida.md`.

### 3. Construir a tela parada ✋

O objetivo é uma página **idêntica à referência quando parada**, com cada coisa que vai se mexer já numa camada própria.

1. Monte a estrutura em HTML/CSS: layout, textos e componentes fiéis à referência. Itens repetidos (listas, nós, cartões) saem
   de dados, não de cópias.
2. **O que o `vida.md` anima nunca fica "assado" no fundo.** Separe em camadas:
   - **fundo estático:** uma placa sem os elementos vivos (gerada por um modelo de imagem a partir da referência, ou recortada);
   - **personagens e objetos:** recortados da referência;
   - **traços, linhas, conectores:** em SVG;
   - **arte fina luminosa** (filamentos, circuitos): isolada da placa com `isolar_camada.py`.

   As receitas de cada caso estão em `references/tecnicas.md`.
3. Meça em vez de chutar: posições, raios e tamanhos de texto saem da referência (veja `references/tecnicas.md`, "Medir").
4. Crie o modo **`?estatico`**: com esse parâmetro, a página congela no estado exato da referência (animações paradas, dados
   fixos, relógio da imagem).
5. Compare: `uv run scripts/gravar.py "<url>?estatico" verificacao/foto.png --foto` e depois
   `uv run scripts/comparar_quadro.py reference.png verificacao/foto.png verificacao`. A diferença média deve ficar perto de
   5/255. Os zooms por região mostram onde corrigir.
6. ✋ Mostre a foto ao lado da referência.

### 4. Dar vida

1. Em `assets/app.js`, escreva **uma função por movimento** do `vida.md` (ex.: `pulsar(no)`, `feixe(de, ate)`, `ativar(item)`).
2. Monte a **linha do tempo do ocioso** com GSAP, em loop, chamando essas funções nos tempos do vídeo. Exponha-a em
   `window.vida = { ocioso }` para a gravação reiniciá-la. No início do loop, ela devolve tudo ao estado inicial.
3. Ligue as **interações** às mesmas funções (hover, clique, envio de mensagem, cursor). Interagir pausa o ocioso, que volta
   sozinho alguns segundos depois.
4. O que precisa de WebGL (3D, partículas densas, shaders) fica num módulo próprio (`assets/cena.js`) que conversa com o
   `app.js` por eventos (`dispatchEvent(new CustomEvent('pulso', …))`).
5. Bibliotecas por CDN com versão fixa (ex.: `three@0.170.0`, `gsap@3.13.0`).

Antes de seguir, abra a página e leia o console. Um erro de JavaScript derruba o resto.

### 5. Verificar

1. **Grave o ocioso:** `uv run scripts/gravar.py "<url>" verificacao/html.mp4 --segundos <duração do loop> --antes
   "vida.ocioso.restart()"`.
2. **Compare o movimento:** `uv run scripts/comparar_movimento.py analise/video-ref.mp4 verificacao/html.mp4 verificacao`.
   - Nenhuma região que se mexe no vídeo pode ficar `PARADO` no HTML, a não ser os artefatos.
   - `fraco` pede atenção, mas pode ser normal: a página tem vida própria e um loop diferente.
   - Abra `verificacao/lado-a-lado.mp4` e confira o ritmo.
3. **Segunda opinião:** `uv run scripts/analisar_video.py analise/video-ref.mp4 verificacao/gemini-comparacao.md --comparar
   verificacao/html.mp4`. O modelo erra eventos curtos; confira nos quadros antes de mudar algo.
4. **Grave as interações:** use `--antes` com um roteiro que dispara eventos (`PointerEvent('pointermove')` para o cursor,
   `mouseenter`, cliques) e salve em `verificacao/demo-interacao.mp4`.
5. Corrija e repita até o lado a lado convencer.

### 6. Entregar ✋

Escreva o `README.md` da pasta:
- o que vive (ocioso e interação, por elemento);
- como foi feito (as técnicas de cada camada);
- os números (diferença parada, regiões cobertas, custo das chamadas de modelo);
- o que ficou de fora e por quê.

✋ Mostre a página, o lado a lado e a demo das interações.

## Escolhendo a técnica

| O que se mexe | Técnica |
|---|---|
| brilho, pulso, rotação, cor, entrada e saída de elementos | CSS + GSAP |
| traços, arcos, conectores, luz percorrendo uma linha | SVG (`stroke-dasharray`) + GSAP |
| partículas leves, ondas, gráficos que rolam | Canvas 2D |
| arte estática que treme ou ondula (água, tinta) | filtros SVG (`feTurbulence` + `feDisplacementMap`) |
| personagem ou objeto que reage em volume (olha o cursor) | 2.5D: recorte + mapa de profundidade num plano Three.js |
| esfera, orbe, planeta, núcleo abstrato | Three.js (malha com a textura da referência ou procedural) |
| milhares de partículas, nuvens de pontos, fundos vivos | Three.js com shaders |

Para cada técnica, as receitas e os cuidados estão em `references/tecnicas.md`. Os erros já conhecidos (espaço de cor, bloom,
GSAP em SVG…) estão em `references/armadilhas.md`: leia antes de usar WebGL.

## Ferramentas

Scripts em `scripts/`. Rodam com `uv run`, com as dependências declaradas no próprio arquivo, e usam o Google Chrome instalado.

| Script | Para quê |
|---|---|
| `mapa_movimento.py <vídeo> <pasta>` | regiões que se mexem, intensidade, picos, período, quadros-chave |
| `analisar_video.py <vídeo> <saída.md>` | descrição do movimento por um modelo multimodal; `--comparar <outro.mp4>` compara dois vídeos |
| `gravar.py <url> <saída.mp4\|.png>` | grava ou fotografa a página; `--antes "<js>"` roda um roteiro antes |
| `comparar_quadro.py <ref.png> <foto.png> <pasta>` | diferença por região entre a referência e a foto da página |
| `comparar_movimento.py <ref.mp4> <html.mp4> <pasta>` | regiões vivas do vídeo que ficaram paradas no HTML + lado a lado |
| `isolar_camada.py <ref.png> <placa.png> <saída.png>` | separa a arte clara (ou clara e escura, `--modo duplo`) de uma placa de fundo |
| `caminhos.py <máscara.png> <saída.json> --centro x,y` | esqueleto dos traços → caminhos para faíscas e sinais andarem pelo desenho |

**Requisitos:** `uv`, `ffmpeg`, Google Chrome e `OPENROUTER_API_KEY` (no ambiente, num `.env` da pasta ou em `~/.env`) para o
`analisar_video.py`. Opcional: `rembg` via `uvx` para recortes, e um gerador de imagens para placas e mapas de profundidade.

## Não fazer

- Copiar o vídeo ao pé da letra, com os erros dele.
- Usar vídeo ou GIF como camada.
- Deixar no fundo algo que o `vida.md` anima.
- Pular o `?estatico` ou a gravação de verificação.
- Confiar no modelo multimodal para tempos finos (eles vêm do mapa de movimento).
