---
name: to-img
description: >-
  Gera imagens em paralelo via OpenRouter a partir de um pedido simples ou de
  um batch com prompts e filenames definidos. Usa gpt2 em 1K por padrão. Use
  when the user mentions to-img or asks to generate image variants via OpenRouter.
disable-model-invocation: true
---

# To Img

Gere imagens via OpenRouter e salve-as em `mocks/`. Aceite um pedido simples ou uma lista de jobs independentes.

Defaults: `model=gpt2` (GPT Image 2), `resolution=1K` e `aspect-ratio=16:9`. Altere-os somente quando o usuário ou a skill chamadora fornecer outros valores.

## Entrada

### Pedido simples

Receba:

- o pedido ou `prompt`;
- `count`, opcional e igual a `3` quando ausente;
- `input-image`, opcional;
- `aspect-ratio`, opcional.

Se for uma tela de app, deixe explícito no prompt que a imagem representa um aplicativo usável.

Encontre o maior número já usado em `mocks/`, adote o próximo como `{cycle}` e nomeie as variantes:

```text
mocks/{cycle}-a.png
mocks/{cycle}-b.png
mocks/{cycle}-c.png
```

Não use `count` como número do ciclo. Variações podem explorar interpretações diferentes da mesma ideia quando o usuário não tiver definido prompts exatos.

### Batch

Aceite uma lista de jobs. Cada job contém:

- `prompt`, obrigatório;
- `filename`, obrigatório;
- `input-image`, opcional;
- `aspect-ratio`, opcional.

Exemplo:

```text
Use $to-img com estes jobs:

- filename=mocks/12-dashboard-a.png
  prompt="Dashboard operacional do produto..."
  aspect-ratio=16:9

- filename=mocks/12-detail-a.png
  prompt="Tela de detalhe do mesmo produto..."
  aspect-ratio=16:9
  input-image=references/style.png
```

Quando um job fornecer `filename`, use o path exatamente como recebido. Não procure outro ciclo, não renomeie o arquivo e não combine prompts de jobs distintos.

## Geração

1. Confirme que cada job possui prompt e destino válidos.
2. Crie `mocks/` ou os diretórios de destino necessários.
3. Use `OPENROUTER_API_KEY` disponível no `.env` do projeto ou em `~/.env`.
4. Execute todas as chamadas independentes em paralelo no cwd do usuário.
5. Aguarde todas e confirme que cada arquivo esperado foi criado.

Para cada job, use:

```bash
uv run ~/.agents/skills/openrouter-img/scripts/generate_image.py \
  --prompt "..." \
  --filename "mocks/{cycle}-a.png" \
  --model gpt2 \
  --resolution 1K \
  --aspect-ratio 16:9
```

Inclua `--input-image` quando fornecido. Preserve diferenças de prompt, filename, referência e proporção entre jobs. Faça o escaping seguro de prompts e paths ao construir os comandos.

Se algum job falhar, identifique-o pelo filename e preserve os resultados concluídos. Ao terminar, mostre todos os paths gerados e pare.
