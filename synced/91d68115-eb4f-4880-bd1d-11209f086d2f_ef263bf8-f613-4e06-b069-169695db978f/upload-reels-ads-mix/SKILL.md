---
name: upload-reels-ads-mix
description: Processo de upload e catalogação de Reels, Ads e Mix (Tipos 1-3) — criar pastas no Google Drive e cards no Notion a partir de arquivos brutos de vídeo na pasta Filmes. Use quando Rodrigo apontar uma pasta com vídeos brutos de reels/ads/mix (prefixos R_, ADLP_/ADVSL_, M_) para processar.
---

# Upload + catalogação — Reels, Ads, Mix (Tipos 1 a 3)

As regras 🚫 REGRA ABSOLUTA e ⚠️ REGRA DE OURO do `CLAUDE.md` da pasta valem integralmente aqui — releia se precisar. As Referências fixas (Notion e Google Drive) também estão no `CLAUDE.md` central.

## Processo geral de upload — Tipos 1 a 3 (visão macro)

1. Rodrigo aponta uma pasta dentro de `Filmes` (esta pasta) com arquivos brutos de um tipo de conteúdo.
2. Identifique os grupos de arquivos que pertencem à mesma peça de conteúdo (mesmo nome-base, prefixos/sufixos diferentes — ver cada tipo abaixo).
3. Para cada grupo, monte o plano (nome da pasta no Drive, template do Notion, valores dos campos) e peça autorização.
4. Após aprovação:
   - Crie a pasta no Drive com a nomenclatura correta.
   - Faça upload dos arquivos do grupo para essa pasta.
   - Crie o card no Notion com o template correto, preenchendo os campos.
   - Cole o link da pasta do Drive no campo **"Link da Pasta"** do Notion.
5. Atualize esta skill (ou o `CLAUDE.md` central, se for cross-cutting) sempre que aprender algo novo sobre o processo (nova convenção, correção de um campo, novo tipo de tarefa, etc.).

## Tipo 1 — Reels

- **Arquivo de origem** (nesta pasta `Filmes`): nome começa com `R_` (ex: `R_Claude1.mp4`).
- **Agrupamento**: arquivos com o mesmo nome-base pertencem ao mesmo reels e vão para a mesma pasta/card (ex: `R_Claude1.mp4` + `R_Claude1_instrucoes.mp4` → mesmo reels "Claude1").
- **Pasta no Drive**: criar dentro da pasta raiz de Reels/Mix, no padrão `n_nome_do_reels` (número simples, sem zero-padding, = maior número existente + 1). Ex: se o maior é `40_strix`, o próximo é `41_claude1`.
- **Card no Notion**: template **Reels**, campos:
  - Responsável pela gravação: Rodrigo Tadewald
  - Link da Pasta: link da pasta criada no Drive
  - Copywriter: Rodrigo Tadewald
  - Editor: Matheus Bittencourt

## Tipo 2 — Ads

- **Arquivo de origem**: nome começa com `ADLP_` (funil = LP) ou `ADVSL_` (funil = VSL), seguido do nome do ad.
- **Agrupamento**: mesma lógica dos Reels (mesmo nome-base = mesma pasta/card).
- **Pasta no Drive**: criar dentro da pasta raiz de Ads, no padrão **`NNN [PROD FUNIL] Nome do ad`** (sem hífen entre o colchete e o nome — confirmado por Rodrigo), onde:
  - `NNN` = número sequencial, sem zero-padding, = maior número já usado na pasta + 1 (ver aviso de paginação no `CLAUDE.md` central).
  - `PROD` = produto, default **FIA** salvo Rodrigo indicar outro.
  - `FUNIL` = `LP` ou `VSL`, identificado pelo prefixo do arquivo de origem (`ADLP_` / `ADVSL_`).
- **Card no Notion**: template **Criativo**, mesma lógica de preenchimento de campos dos Reels (Responsável pela gravação, Link da Pasta, Copywriter, Editor), **mais o campo `Perfil` = `["Rodrigo"]`** (multi_select) e **o campo `Produto` = `🤖 FIA`** (com o emoji, salvo Rodrigo indicar outro produto) — sempre preencher os dois, nunca deixar em branco.

## Tipo 3 — Mix

- **Arquivo de origem**: nome começa com `M_` (ex: `M_NomeDoMix.mp4`).
- **Agrupamento**: mesma lógica dos Reels.
- **Pasta no Drive**: mesma pasta raiz dos Reels ("Rodrigo"), mesma sequência numérica compartilhada, padrão `n_nome_do_mix`.
- **Card no Notion**: template **Mix de saídas**, mesma lógica de preenchimento de campos dos Reels.

## Pendências / Futuro

- **Roteiros no Obsidian**: Rodrigo guarda os roteiros dos ads/reels em `/Users/rtadewald/Obsidian Notes/1 Copies/1 Priorizar` (fora da pasta `Filmes`, vault Obsidian separado). Pasta confirmada existente via listagem skeleton em 21/08, mas o acesso completo (`device_request_folder_access`) ainda **não foi concedido** — a primeira tentativa expirou sem resposta do Rodrigo. Objetivo futuro (pedido por Rodrigo em 21/08, ainda não confirmado como ativo): ao processar Tipo 1/2 (upload de reels/ads), buscar o roteiro correspondente nessa pasta do Obsidian e colar dentro do card do Notion, numa seção de "roteiro". **Ainda não implementado** — pedir acesso à pasta de novo na próxima vez que for relevante, e só then tratar como parte padrão do processo.

## Aprendizados / ajustes (manter atualizado)

- **Variantes numeradas no nome do arquivo de origem (`_2`, `2` no fim) = mesmo conteúdo, mesma pasta/card** — confirmado como regra geral por Rodrigo (ex: `ADLP_Prontidão_Aplicações_AI_Python.MP4` + `...Python2.MP4` viraram uma pasta/card só; `ADSVSL_Gemini.MP4` + `...Gemini2.MP4` idem). Só tratar como itens separados se o nome-base for realmente diferente (ex: `Gemini_e_Kimi` é outro ad, não variante do `Gemini`).
- **Separador do prefixo pode ser espaço em vez de underscore**: em 17/08 os arquivos vieram como `ADVSL CTA Jarvis.MP4` e `ADVSL Claude Arquiteto VSL.MP4`. Mesmo significado de `ADVSL_` — tratar igual, sem perguntar.
- **"VSL"/"LP" repetido no fim do nome do ad é redundância, remover** (confirmado por Rodrigo em 17/08): `ADVSL Claude Arquiteto VSL.MP4` → pasta `870 [FIA VSL] Claude Arquiteto`, não "Claude Arquiteto VSL". O funil já aparece no colchete.
- **Uma pasta de data pode ser de Ads, não de aulas**: `2026_08_17/` só tinha `ADVSL ...` — é Tipo 2, não Tipo 4. **Olhar o conteúdo antes de assumir o tipo da tarefa** só porque a pasta tem nome de data; o prefixo dos arquivos é que decide.
- **Prefixo `ADSVSL_`** já apareceu nos arquivos de origem — é **erro de digitação de `ADVSL_`** (funil VSL), confirmado por Rodrigo. Se aparecer de novo, tratar como VSL sem perguntar de novo, a menos que o padrão mude.
- **Convenção de nome das pastas de Ads**: `NNN [PROD FUNIL] Nome do ad`, **sem hífen** antes do nome (confirmado por Rodrigo). O histórico da pasta é inconsistente (várias entradas antigas têm hífen, ordem invertida `[VSL FIA]`, etc.) — não seguir o histórico como referência, seguir sempre esse padrão para pastas novas. PRODs vistos além de FIA: `N8N`, `HOME`, `FID`, `AxA`, `WORK`.
- **Reels/Mix**: numeração e pasta raiz são compartilhadas entre os dois tipos (mesma sequência, mesma pasta "Rodrigo").
- **Erro real cometido (10/08)**: criei as pastas de Ads 782–786 sem paginar toda a listagem da pasta raiz, colidindo com números já usados por outras pastas (782–786 já existiam, criadas por outra pessoa em 05/08). Corrigido recriando como 812–816 (número real+1, formato sem hífen) e atualizando o campo "Link da Pasta" dos cards já criados no Notion via `notion-update-page` (`command: "update_properties"`). As pastas erradas 782–786 (vazias) ficaram para Rodrigo apagar manualmente — sem ferramenta de delete no MCP do Drive.
- **Ads com "Asimov Work" no nome usam PROD `WORK`**, não o default FIA (confirmado por Rodrigo em 12/08: `ADLP_Asimov_work.MP4` → `835 [WORK LP] Asimov Work`). Se o nome do ad referenciar um produto explicitamente, ele ganha do default.
- **Campo `Perfil`** (multi_select, "Em qual perfil essa mídia será publicada?") deve ser preenchido como `["Rodrigo"]` em todo card de Ads (Tipo 2 e Tipo 5) — correção pedida por Rodrigo em 17/08 depois de eu ter deixado o campo vazio em 6 cards criados no dia.
- **Método confiável para achar o maior número da pasta de Ads**: `search_files` com `parentId = '<raiz>' and createdTime > '<hoje -1 ou -2 dias>'`. Retorna poucos itens, sem paginação, e o maior número aparece direto — bem melhor que paginar a listagem inteira.
