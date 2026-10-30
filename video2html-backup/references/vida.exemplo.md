# Painel do assistente — mapa de vida

**Referência:** `reference.png` (1536×864) · **Vídeo:** `analise/video-ref.mp4` (6 s)
**Leituras:** `analise/movimento.png` + `analise/regioes.json` (mapa de movimento) · `analise/gemini.md` (modelo multimodal)

## Ritmo geral

Calmo, com pontuações rápidas. O núcleo do assistente respira o tempo todo; a cada ~1 s uma luz sai dele e acende um item da
lista; a sequência termina no microfone. Movimentos curtos, com ease-out, e brilho que decai devagar.

## Elementos

| Elemento | O que faz no vídeo | Interação que vamos criar | Técnica |
|---|---|---|---|
| **Núcleo** (r05) | brilho de 70 % → 100 % → 70 % em ~2,4 s | segue o cursor alguns graus; acende quando um item é chamado | Three.js 2.5D (recorte + mapa de profundidade) e bloom |
| **Anel em volta** (r07, r08, r11–r20) | o brilho acompanha o núcleo | gira devagar, sempre; acelera um instante quando uma luz sai | SVG (círculos tracejados) |
| **Luz até o item 1** (r03) | percorre o conector de 1,1 a 1,8 s, com ease-out | passar o mouse num item dispara a luz até ele | SVG (`stroke-dasharray`) + GSAP |
| **Item 1** | flare quando a luz chega (1,8 s); fica ativo em 2,2 s | hover acende um halo; clique o seleciona | SVG/CSS |
| **Luz até o item 2** (r02) | 2,2 → 2,8 s; o item fica ativo em 3,0 s | idem | idem |
| **Microfone** (r04) | pulso de luz de 5,1 a 5,7 s | clique: modo "ouvindo" (anéis pulsando + onda) | CSS + Canvas 2D |
| **Gráficos laterais** (r06, r10) | micro-oscilação (r10 com período de 2,6 s) | os gráficos rolam e os números variam | SVG atualizado por JS |
| **Partículas** | quase paradas | derivam devagar e desviam do cursor | Canvas 2D |
| **Relógio** | parado | hora real | JS |
| **Chat** | parado | Enter envia; o assistente responde e a luz vai até o item citado | HTML + JS |

## Linha do tempo do ocioso (loop de 9 s)

```
0.0  núcleo respira (contínuo, 2,4 s) · anel gira (contínuo)
1.1  luz → item 1 ········ 1.8 flare ··· 2.2 assenta
2.2  luz → item 2 ········ 2.8 flare ··· 3.0 item 2 fica ativo
5.1  microfone pulsa ····· 5.7
6.5  item 2 volta ao estado inicial · 9.0 recomeça
```

Interagir (mouse num item, digitar no chat, clicar no microfone) pausa o ocioso, que volta sozinho 6 s depois.

## Fora

- No fim do vídeo, o rótulo do item 3 muda de texto (artefato do modelo de vídeo): os rótulos ficam fixos.
- O relógio deforma nos últimos quadros: vira hora real.
