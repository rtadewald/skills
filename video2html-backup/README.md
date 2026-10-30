# Vídeo → HTML vivo

Skill que transforma o vídeo de uma interface (gravação de tela, mock animado ou vídeo gerado por IA) num **HTML vivo e
interativo**: a página se mexe como o vídeo e, além disso, responde ao cursor, aos cliques e às ações do usuário.

## O problema

Pedir "anima essa tela" direto para um modelo de código dá o de sempre: fade-in e hover que escurece. Modelos de vídeo imaginam
movimento muito melhor (o núcleo que respira, a luz que corre até um item, a névoa que rola), mas o vídeo não é código:

- ele inventa coisas (rótulos que mudam, textos que derretem) que não podem ir para a tela;
- usado como camada, mata a interatividade;
- "parece com o vídeo" não se verifica a olho.

## A ideia

O vídeo é **inspiração de movimento**; o conteúdo vem da imagem de referência (ou do quadro mais nítido do vídeo).

1. **Ler o vídeo com dois leitores:** um mapa de movimento por pixel (onde, quanto, quando: exato e de graça) e um modelo
   multimodal (o quê e como, em palavras: centavos). Juntos, viram o **mapa de vida**: cada elemento com o que faz no vídeo, a
   interação que vamos criar e a técnica.
2. **Construir a tela parada em camadas:** fiel à referência, com tudo que vai se mexer separado (o personagem recortado, a
   arte isolada da placa de fundo, os traços em SVG).
3. **Animar em código,** pela técnica mais simples que convence: CSS/SVG → Canvas 2D → WebGL (Three.js), com GSAP na
   coreografia. Vídeo nunca vira asset.
4. **Ir além do vídeo:** cada movimento vira uma função que o estado ocioso chama e que as interações também chamam.
5. **Provar:** grava a página no Chrome e compara o movimento com o vídeo, região por região. Um modo `?estatico` congela a
   página no estado da referência para medir a fidelidade.

## Passo a passo

```
1. preparar a pasta (vídeo + referência)
2. ler o vídeo → vida.md                         ✋ aprovar o mapa de vida
3. tela parada em camadas + ?estatico            ✋ aprovar a foto × referência
4. dar vida (ocioso + interações)
5. verificar (gravar, comparar com o vídeo, demo das interações)
6. entregar (README)                             ✋
```

Os ✋ são pontos de parada para o usuário aprovar. No **modo autônomo**, a skill segue direto e registra as decisões.

## Arquivos

- [`SKILL.md`](./SKILL.md): o passo a passo, as regras e as ferramentas.
- [`references/tecnicas.md`](./references/tecnicas.md): receitas por tipo de problema (personagem, arte fina luminosa, fundo
  claro, objeto 3D, cena inteira em código…).
- [`references/armadilhas.md`](./references/armadilhas.md): erros conhecidos de Three.js, GSAP e gravação.
- [`references/vida.exemplo.md`](./references/vida.exemplo.md): um mapa de vida de exemplo.
- `scripts/`: as ferramentas.

## Scripts

Rodam com `uv run` (dependências declaradas no próprio arquivo) e usam o Google Chrome instalado:

| Script | Para quê |
|---|---|
| `mapa_movimento.py` | regiões que se mexem, curvas de atividade, picos, período, quadros-chave |
| `analisar_video.py` | descrição do movimento por um modelo multimodal; `--comparar` compara referência e página |
| `gravar.py` | foto ou vídeo da página, com `--antes` para rodar um roteiro (cursor, cliques) |
| `comparar_quadro.py` | tela parada: diferença por região entre a referência e a página |
| `comparar_movimento.py` | movimento: regiões vivas do vídeo que ficaram paradas na página, lado a lado |
| `isolar_camada.py` | separa a arte de uma placa de fundo (clara, ou clara e escura para fundos claros) |
| `caminhos.py` | esqueleto dos traços → caminhos para sinais andarem pelo desenho |

**Requisitos:** `uv`, `ffmpeg`, Google Chrome e `OPENROUTER_API_KEY` (no ambiente, num `.env` ou em `~/.env`). Opcional:
`rembg` via `uvx` para recortes (o modelo tem ~1 GB na primeira vez) e um gerador de imagens para placas e mapas de profundidade.
