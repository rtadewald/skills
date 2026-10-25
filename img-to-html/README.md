# Img → HTML

Skill que ataca o problema **image → code**: transformar um mock/screenshot de UI em HTML + CSS + JS estático, **sem framework**, com bem mais fidelidade do que pedir “recria essa tela” de uma vez.

**Entrada:** imagem de referência (anexo, path ou URL).  
**Saída:** `design-systems/<slug>/` com `reference`, `wireframe.txt`, `index.html` e `assets/`.

---

## O problema

Hoje existem dois problemas quando você usa IA para criar interfaces.

### 1. AI slop (`prompt → código`)

As IAs modernas já desenham bem — mas são viciadas em padrões. Sem guia, saem da caixa as mesmas manias: degradê genérico, botão arredondado, três cards lado a lado, fonte serifada em tudo. Cada modelo tem as suas.

Isso acontece porque você pede para ela resolver **tudo de uma vez**: layout, HTML, CSS, responsividade, componentes e identidade visual no mesmo passo. O código engessa a criatividade. Sobrou pouca capacidade para composição, contraste e referência fora do padrão.

A saída é começar pela imagem:

```
prompt → imagem → código
```

Na geração de imagem a IA não está presa às regras do HTML. Ela explora hierarquia, contraste e ideias ousadas. Aí você transforma aquilo numa aplicação funcional.

### 2. Image → code ainda é loteria

Só que os modelos ainda erram bastante ao ir de uma imagem pronta para código — não porque sejam ruins, mas porque tentam interpretar layout, textos, espaçamento, componentes, imagens, fontes, fundos e responsividade **ao mesmo tempo**. Sem estratégia de decomposição, o resultado oscila: às vezes acerta, às vezes fica longe da referência e queima token/tempo.

`img-to-html` existe para fechar esse segundo elo: **qualquer modelo** (inclusive os inconsistentes) decompõe a referência em camadas controladas, com aprovação humana entre elas — menos tentativa, menos retrabalho, sem a cara genérica de IA.

---

## A ideia da skill

Em vez de `imagem → código mágico`, o fluxo vira uma sequência:

1. **Ler** a tela (wireframe ASCII tipado + plano) e **aprovar** antes de qualquer linha de código  
2. **Construir camada por camada** — fundo → estrutura/componentes + fontes → assets restantes → revisão integrada  
3. Em cada etapa: mostrar, corrigir se precisar, só então avançar

Você não torce para a IA acertar de primeira. Você dirige a construção.

---

## Pipeline

```
1. wireframe ASCII tipado + plano  → [aprova]
2. fundo completo (CSS e/ou imagens) → [aprova]
3. estrutura, componentes + fontes   → [aprova]
4. assets restantes (ícones etc.)    → [aprova, se houver]
5. revisão final integrada           → [aprova]
```

Em cada gate: mostra o resultado, pergunta, **para**. Só avança com “aprovado” / “pode seguir” / “ok”.

| # | O que faz | Gate |
|---|-----------|------|
| 1 | `$to-wireframe format=ascii` + plano por região (etapa + técnica) | estrutura + sequência |
| 2 | Fundo completo (CSS, imagem ou camadas) | fundo vs referência |
| 3 | Chrome → cards → resto; fontes antes do ajuste fino | superfícies + tipografia |
| 4 | Ícones, imagens de conteúdo, avatares (omitir se o plano disser) | assets na composição |
| 5 | Screenshot tela cheia vs referência; integração | entrega final |

Assets de fundo vão na etapa 2 ou 3 (pela função). Independentes geram em lote paralelo via `openrouter-img` (`gpt2`, 1K).

---

## Layout

```
design-systems/<slug>/
  reference.[ext]
  wireframe.txt
  index.html
  assets/
    styles.css
    app.js          # só se precisar de comportamento
    crops/
    *.png / …
```

Stack: HTML + CSS + JS separados. Sem build, bundler, Tailwind ou CDN. Abre `index.html` direto no browser.

- Todo CSS em `assets/styles.css` (nada de `<style>` / `style="…"`)
- Custom properties no `:root`
- Mesmo id do wireframe = mesma classe CSS
- Paths relativos: `assets/{id}.png`

---

## Skills vizinhas

- [`to-wireframe`](../to-wireframe) — planta ASCII tipada (etapa 1)
- [`openrouter-img`](../openrouter-img) — regenerar crops/ícones
- [`find-font`](../find-font) — família/peso a partir de crop de texto (opcional na etapa 3)
- [`img-to-html2`](../img-to-html2) / [`img-to-html3`](../img-to-html3) — variantes do fluxo

Detalhe operacional (gates, não-fazer, prompts de asset): [`SKILL.md`](./SKILL.md).
