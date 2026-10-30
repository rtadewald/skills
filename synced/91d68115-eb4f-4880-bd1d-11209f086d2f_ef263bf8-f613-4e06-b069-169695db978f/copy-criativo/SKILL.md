---
name: copy-criativo
description: Preenchimento da copy final (títulos, texto principal, campanha) num card de Ads já existente no Notion (Tipo 5) — só Notion, sem Drive nem vídeo. Use quando Rodrigo colar a copy/roteiro de um anúncio e apontar o card correspondente (Mídia = 💰 Criativo), ou pedir para duplicar um card de criativo para outra Landing Page.
---

# Tipo 5 — Copy final do Criativo (títulos, texto principal, campanha)

Tarefa **só no Notion** (não envolve Drive nem arquivo de vídeo): preencher, num card de Ads (**Mídia = 💰 Criativo**) já existente, a copy final usada pelo tráfego para subir o ad, e as propriedades de campanha associadas. É a etapa final antes do ad poder rodar.

A regra ⚠️ REGRA DE OURO do `CLAUDE.md` da pasta vale integralmente aqui — releia se precisar. As Referências fixas (Notion) também estão no `CLAUDE.md` central.

## Gatilho e entrada

- Rodrigo aponta um card do Notion (URL ou ID) na base "Edição e Publicação - 2026".
- Rodrigo cola a copy/roteiro do anúncio (o texto de referência a partir do qual os títulos e textos são gerados).
- Rodrigo informa a Landing Page (URL) e, se necessário, o destino (LP ou VSL) e o produto — ver defaults abaixo.

## O que preencher

**1. Conteúdo da página** — dentro do toggle "Copy de Descrições (Tráfego)":
- **Títulos**: gerar 3 títulos curtos (headline de anúncio) a partir da copy, como os 3 bullets já existentes no template. Estilo: frases declarativas diretas, sem emoji, sem ponto de interrogação forçado (ex: "As ferramentas que os desenvolvedores sérios estão usando.", "Os projetos de IA mais populares do momento.").
- **Texto principal 1 / 2 / 3**: gerar 3 variações do corpo do anúncio, cada uma mapeada a um comprimento — ⚠️ **CORRIGIDO em 20/08/2026: a ordem certa é a INVERSA do que este arquivo dizia antes** (confirmado por Rodrigo com exemplo real de ad, ver "Aprendizados" no fim):
  - **Texto principal 1 = o mais longo/detalhado.** Reconta a proposta de valor em prosa, com vários parágrafos curtos (uma ideia por parágrafo, sem medo de quebrar linha) — não tem limite rígido de caracteres, mas também não é o roteiro inteiro, é uma síntese bem escrita. Fecha com CTA + gatilho de urgência.
  - **Texto principal 2 = médio.** Versão condensada do texto 1, 2-3 linhas. Fecha com CTA + urgência.
  - **Texto principal 3 = o mais curto.** 1-2 linhas, direto ao ponto. CTA simples, sem urgência forte.
  - **🚫 Nunca citar a palavra "VSL" no copy voltado pro público** (nem título nem texto) — isso é jargão interno. Pro público, a oferta é sempre "a aula gratuita". CTAs de referência: "Clique no botão abaixo e assista à aula gratuita" / "Assista à aula gratuita e descubra..."; urgência (textos 1 e 2): "mas atenção, ela não fica no ar pra sempre" / "antes que saia do ar"; texto 3 não precisa de urgência, só o CTA.
  - **Exemplo real de referência** (ad "Claude Code vs OpenClaw", aprovado por Rodrigo) — usar como modelo de tom e estrutura:
    - Título: "As ferramentas que os desenvolvedores sérios estão usando."
    - Texto 1 (longo): "Claude Code e OpenClaw são os dois projetos de IA mais populares dos últimos meses, mas muita gente ainda confunde os dois — e a diferença muda tudo.\nO Claude Code roda no terminal e programa por você [...]\nO OpenClaw foi feito para outra coisa [...]\nA recomendação é usar os dois [...]\nClique no botão abaixo e assista à aula gratuita para saber mais — mas atenção, ela não fica no ar para sempre."
    - Texto 3 (curto): "Os dois projetos de IA mais populares do momento — e cada um com um propósito diferente.\nAssista à aula gratuita e descubra como aplicar os dois na prática."

**2. Propriedades** (nomes exatos no schema — confirmados via `notion-fetch` na `collection://3063ee05-7ee5-8134-a30f-000bbc36e56c`):
- **`Landing Page`** (multi_select): valor(es) que Rodrigo informar diretamente (path ou URL da LP/VSL).
- **`Campanha`** (multi_select): nome gerado no padrão **`[PRODUTO]_DESTINO_NOME`**:
  - `PRODUTO` — texto simples sem colchete/emoji (`FIA`, `N8N`, `HOME`, `FID`, `WORK`, etc.), default **FIA** salvo Rodrigo indicar outro. Mesma lógica de default do Tipo 2.
  - `DESTINO` — `LP` ou `VSL`. Inferir do prefixo do arquivo de origem se ele existir (`ADLP_`/`ADVSL_`), do path da Landing Page (se contém `/vsl/`), da copy, ou perguntar a Rodrigo se não der para saber. Funis de isca (lead magnet) que caem em página `/vsl/...` também contam como `VSL`.
  - `NOME` — slug genérico com underscores, criado a partir do nome do card (ex: card "Desperdiçando Potencial IA" → `Desperdicando_Potencial_IA`).
  - **Nenhum dos dois campos (`Landing Page`/`Campanha`) cria opção nova sozinho ao salvar um valor inédito** — ver "Cuidados" abaixo, é preciso checar o limite de 100 opções antes.

## Passo a passo

1. Ler o card com `notion-fetch` para confirmar que é um Criativo (Mídia = 💰 Criativo) e ver o que já está preenchido.
2. Gerar títulos e textos principais a partir da copy que Rodrigo colar.
3. Montar o nome de Campanha e confirmar a Landing Page.
4. **Apresentar o plano** (títulos, os 3 textos com contagem de caracteres, valor de Campanha, valor de Landing Page) e esperar confirmação de Rodrigo — vale a REGRA DE OURO também aqui.
5. Após o "sim", atualizar a página via `notion-update-page`: conteúdo (títulos + textos principais dentro do toggle existente) e as duas propriedades.

## Cuidados

- Esse card normalmente já foi criado no Tipo 2 (upload do ad) — não criar um card novo, **editar o existente**. Se checar e não existir card nenhum ligado àquela pasta do Drive (buscar por `notion-search` pelo nome do ad não basta — pode achar um card antigo homônimo de outro contexto; conferir sempre `Link da Pasta` no card encontrado bate com a pasta em questão), **criar o card do zero** (Tipo 2 + Tipo 5 juntos) com `Mídia = 💰 Criativo`, `Status = "Copy pronta"` (copy fechada, vídeo ainda não editado) e todas as propriedades normais.
- Não mexer nas outras propriedades do card (Status, Revisão, Link da Pasta, etc.) a menos que Rodrigo peça.
- `Landing Page` e `Campanha` são **multi_select**, não texto simples — passar como array de string(s) ao atualizar via API.
- **Nem `Landing Page` nem `Campanha` criam opção nova sozinhos ao salvar um valor inédito** — a API do Notion recusa (`Invalid multi_select value ... If a new multi_select option is needed, the data source must be updated to add it`). Isso é diferente da interface do Notion, que cria a opção na hora sem perguntar.
  - **Para adicionar a opção**: usar `notion-update-data-source` com `ALTER COLUMN "<Campo>" SET MULTI_SELECT(...)`, passando **a lista completa das opções já existentes (nome+cor, sem alterar nenhuma) mais a(s) nova(s)**. A API valida cor por cor — **mudar a cor de uma opção existente (mesmo sem querer) já derruba a chamada inteira** (`Cannot update color of select with name: ...`).
  - **A API também recusa `ALTER COLUMN SET` se o total de opções passar de 100** (`options.length should be ≤ 100`), mesmo que o campo já tenha mais que isso historicamente (criado pela UI, que não tem essa trava). **`Campanha` já tem 285+ opções — está permanentemente acima do limite, então nunca dá pra adicionar opção nova nele por essa via.** `Landing Page` tem ~67 — ainda cabe.
  - **Nunca reconstrua a lista de opções à mão/digitando na chamada** — extrair as opções (com cor) do schema já buscado via script (Python/Bash), gerar a string do DDL inteira por código, escrever num arquivo e reenviar o conteúdo do arquivo literalmente. Já aconteceu de digitar a cor errada de uma opção ao montar a chamada manualmente, o que derrubou a alteração.
  - **Fluxo padrão quando o campo estourou o limite (caso do `Campanha`) e o navegador está disponível**: usar o workaround via Claude in Chrome (ver "Aprendizados" abaixo) — eu mesmo crio a opção pela interface web, sem trava de 100. Só cair pro fluxo manual (pedir pro Rodrigo digitar direto num card na interface do Notion) se o Chrome não estiver acessível.
  - Se o campo ainda tem espaço (< ~90 opções, caso do `Landing Page`), pode-se também fazer o `ALTER COLUMN SET` via API normalmente.
- **Duplicar um card para mais de uma Landing Page (ex: mesmo ad rodando em duas VSLs diferentes)**: por padrão, **editar o card original** para virar a primeira variação e **criar 1 card novo** para a segunda — não criar dois cards novos preservando o original intocado, salvo Rodrigo pedir diferente. Os cards novos herdam Copywriter, Editor, Responsável pela gravação, Link da Pasta, Revisão, Status, Formato, Mídia e Prazo do original (mesmo material bruto, só muda o destino).
- **Título do card (correção 20/08, revisada de novo no mesmo dia)**: segue o padrão **`[FUNIL]_NNN_Nome_do_ad`** — funil entre colchetes, **o número da pasta do Drive** (o mesmo `NNN` da convenção de pasta), e o nome. No nosso caso o funil é sempre VSL, então na prática é `[VSL]_NNN_Nome_do_ad` (ex: `[VSL]_815_Gemini`). ⚠️ Errei a primeira versão dessa regra (achei que era só `[FUNIL]_Nome_do_ad`, sem número) — confirmado com Rodrigo depois de notar que outros cards criados por colegas no mesmo dia já seguiam `[VSL]_NNN_Nome` (ex: `[VSL]_862_Meme_Bike_Melhor_IA`) e que o print de exemplo que ele mandou também tinha o número (`[LP]_853_...`). Ao duplicar pra mais de uma Landing Page, adicionar sufixo `_v12`/`_v15` no final do nome (ex: `[VSL]_815_Gemini_v12`, `[VSL]_815_Gemini_v15`) — não usar o formato `Nome — v12` (travessão).
- **Sempre preencher o campo `Produto`** (select simples, não confundir com o texto `[PRODUTO]` da Campanha) em todo card de Ads/Criativo — valor padrão `🤖 FIA` (com o emoji, é o texto exato da opção). Rodrigo pediu pra sempre preencher junto com `Perfil` (`["Rodrigo"]`).

## Pendências

- **Campo `Campanha` sem valor em "Find Skills" e "Claude Smart"** (cards criados 17/08 para o funil isca-vsl `isc-guia-skills`): campo bloqueado pelo limite de 100 opções da API (`Campanha` já tem 286+ opções). Valores propostos, no padrão sem `[E1]`: `[FIA]_VSL_Find_Skills` e `[FIA]_VSL_Claude_Smart`. Agora que o workaround via navegador está documentado (ver Aprendizados), dá pra resolver isso diretamente sem esperar Rodrigo digitar manualmente — revisitar quando houver oportunidade.

## Aprendizados / ajustes (manter atualizado)

- **Duplicar card de Criativo pra 2 Landing Pages (20/08, card "Gemini")**: segui a regra acima — editei o card original virando `Gemini — v12` e criei 1 card novo `Gemini — v15` (nomenclatura de título revisada depois, ver "Cuidados"), herdando Copywriter/Editor/Responsável/Link da Pasta/Revisão/Status/Mídia/Prazo do original. Landing Pages confirmadas por consulta SQL no data source (`notion-query-data-sources`, filtrando `Landing Page LIKE '%v12%'/'%v15%'` em cards antigos) — formação "Engenheiro de Agentes de IA" (FIA): `/formacoes/engenheiro-de-ia/vsl/v12` e `/formacoes/engenheiro-de-ia/vsl/v15`.
- **Campo `Campanha` acima do limite de 100 opções — workaround via navegador em vez de pedir pro Rodrigo digitar**: como tenho acesso ao Claude in Chrome, em vez de pedir pra Rodrigo digitar o valor novo manualmente na interface (fluxo antigo), eu mesmo naveguei até o card no `app.notion.com`, cliquei no campo `Campanha` vazio, digitei o valor (ex: `[FIA]_VSL_Gemini_v12`) e cliquei em "Create ...". A interface web cria a opção na hora, sem a trava de 100 opções da API. Bem mais rápido que esperar o Rodrigo — usar esse caminho por padrão quando o navegador estiver disponível, só cair pro fluxo manual (pedir pro Rodrigo digitar) se o Chrome não estiver acessível. **Cuidado com o clique**: clicar uma vez no campo "Empty" às vezes só rola o campo pra tela, sem abrir/focar o input de busca — padrão confiável: clicar uma vez no campo vazio, depois clicar de novo diretamente dentro da caixa de busca já visível, só então digitar. Conferir depois (screenshot ou SQL) que nenhuma opção indesejada foi criada por clique perdido, e que o campo não ficou vazio em nenhum card do lote (já aconteceu de esquecer de preencher um dos cards duplicados).
