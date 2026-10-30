---
name: organizar-aulas
description: Pareamento de gravações de tela (OBS) com gravações de câmera para aulas/projetos (Tipo 4) — tarefa local no Mac, sem Drive nem Notion. Use quando Rodrigo apontar uma pasta de trabalho com vídeos de câmera crus (ex. MVI_XXXX.MP4) para parear com as telas já nomeadas na raiz de Movies.
---

# Tipo 4 — Organização de aulas (pareamento tela ↔ câmera)

Tarefa **puramente local** (não envolve Drive nem Notion): parear as gravações de tela (OBS) com as gravações de câmera de aulas/projetos gravados para a plataforma.

As regras 🚫 REGRA ABSOLUTA e ⚠️ REGRA DE OURO do `CLAUDE.md` da pasta valem integralmente aqui — releia se precisar.

## Cenário de entrada

- **Na raiz de `Movies`**: os vídeos de **tela**, gravados no OBS e **já nomeados corretamente** com o nome final da aula (ex: `1.3. Primeiros passos trabalhando com LLMs.mp4`, `2.4 A Classe Agent.mp4`). São a fonte da verdade dos nomes.
- **Numa pasta de trabalho que Rodrigo aponta** (ex: `2026_08_13/`): os vídeos **crus da câmera**, com nome genérico da câmera (ex: `MVI_0631.MP4`).
- **Sempre há mais vídeos de câmera do que de tela**: durante a gravação Rodrigo erra, refaz e apaga a gravação de tela ruim, mas **não** apaga a de câmera correspondente. Essas câmeras sobrando são takes descartados.

## Regra de pareamento — dois critérios

**1. Duração** (critério de partida): o par tela↔câmera tem praticamente a mesma duração — **tolerância de ±10 segundos**.

**2. Horário de início** (critério de confirmação, e o mais forte dos dois — ver abaixo): o instante em que cada gravação começou.

- **Tela (OBS)**: não tem tag `creation_time`. Use o `birth` do arquivo = **início** da gravação, e o `mtime` = **fim**. (`birth + duração ≈ mtime`, confere.)
- **Câmera (Canon `MVI_*`)**: tem tag `creation_time` no container, **em UTC** e correspondente ao **início** da gravação. Converter para o horário local (**UTC−3**) antes de comparar. Não usar o `birth`/`mtime` das câmeras: eles refletem a hora da **cópia do cartão SD**, feita em lotes, e não a gravação.
- **O relógio da câmera não é o mesmo do Mac.** No lote de 13/08 a câmera estava **+3min11s adiantada**. O que importa não é o offset ser zero, e sim ele ser **constante**: no dia inteiro variou só entre +3:10 e +3:14 (4s de amplitude em 11 pares).

**Como usar na prática**: calcule `offset = início_câmera − início_tela` para todos os pares propostos. O offset correto forma um **cluster apertado** (poucos segundos de amplitude); qualquer par com offset fora do cluster é pareamento errado. Não presuma o valor do offset — ele muda conforme o relógio da câmera; **descubra-o a partir do próprio lote** (mediana dos offsets dos pares de duração mais óbvia, os com Δ < 1s) e depois valide os demais contra ele.

Comandos:
```
ffprobe -v error -show_entries format=duration -of csv=p=0 "arquivo.mp4"
ffprobe -v error -show_entries format_tags=creation_time -of csv=p=0 "MVI_0637.MP4"   # UTC, início
stat -f '%SB|%Sm' -t '%H:%M:%S' "tela.mp4"                                            # birth=início | mtime=fim
```

## Passo a passo

1. **Confirmar a pasta de trabalho** com Rodrigo e listar os dois lados (telas na raiz, câmeras na pasta).
2. **Medir duração E horário de início de todos os vídeos** (dos dois lados) com `ffprobe`/`stat` (o `ffprobe` já está em `/opt/homebrew/bin/ffprobe`) — operações somente leitura, pode rodar à vontade. Ver os comandos na seção de regra de pareamento acima.
3. **Calcular o pareamento** (ver algoritmo abaixo) e montar a tabela: tela → câmera, com as duas durações, o delta em segundos **e o offset de horário de início**.
4. **Apresentar o plano completo a Rodrigo e esperar autorização explícita** (vale a REGRA DE OURO também aqui). O plano deve mostrar: cada par proposto com o delta, quais câmeras ficaram sem par, e os nomes finais exatos.
5. **Só após o "sim"**, executar nesta ordem:
   - **Mover** os vídeos de tela da raiz de `Movies` para a pasta de trabalho.
   - **Renomear apenas os vídeos de câmera** pareados, para o nome da aula + sufixo `_cam` (ex: `1.3. Primeiros passos trabalhando com LLMs_cam.MP4`). Manter a extensão original (`.MP4` da câmera continua `.MP4`).
   - **Os vídeos de tela NUNCA são renomeados** — o nome deles já é o correto e é a referência.
   - Criar a subpasta `não encontrados/` dentro da pasta de trabalho e **mover para lá as câmeras sem par**.
6. **Verificar e reportar**: conferir a contagem final (nenhum arquivo perdido — total de arquivos antes = total depois) e mostrar o resultado.

## Algoritmo de pareamento (detalhes que importam)

- Para cada vídeo de tela, os candidatos são todas as câmeras com `|duração_câmera − duração_tela| ≤ 10s`.
- **Não usar guloso ingênuo por ordem de arquivo.** Gerar todos os pares candidatos, ordenar por `|delta|` crescente e ir fixando os pares do menor delta para o maior, descartando os candidatos cujo tela ou câmera já foi usado. Isso evita que uma tela "roube" a câmera de outra.
- **Validação por offset de horário (a mais forte)**: depois de montar os pares por duração, calcule o offset de início de cada um. Todos devem cair no mesmo cluster de poucos segundos. Um par com offset destoante (minutos ou horas) está errado, por mais que a duração case.
- **Validação de ordem cronológica**: os dois lados são cronológicos (as telas pela numeração da aula `1.2, 1.3, …`; as câmeras pelo número sequencial `MVI_0631, 0632, …`). O pareamento correto **preserva essa ordem** — se o resultado cruzar (aula posterior pareada com câmera anterior), quase certamente há um erro de pareamento.
- **Ambiguidade**: se uma tela tiver mais de uma câmera dentro da tolerância de duração com deltas parecidos, **resolva pelo offset de horário** — na prática ele desempata sozinho, porque takes descartados ficam a minutos ou horas de distância. Só pergunte a Rodrigo se o offset também não separar os candidatos.
- **Tela sem par** não deveria acontecer (sempre sobra câmera, nunca falta). Se acontecer, **não mova nem renomeie nada dessa tela** — reporte como anomalia e pergunte.
- **Nem toda câmera órfã é take descartado**: aulas do tipo "Apresentação"/intro costumam ser **só câmera, sem gravação de tela**, então nunca terão par. Elas caem em `não encontrados/` pelo algoritmo, mas o certo é renomeá-las com o nome da aula e deixá-las na pasta principal. Ao reportar as órfãs, sinalizar as candidatas a esse caso (duração "de aula", no início do dia de gravação, ordem cronológica coerente) e perguntar a Rodrigo.
- Colisão de nome: se duas aulas gerarem o mesmo nome de destino, pare e reporte. Nunca sobrescrever (ver REGRA ABSOLUTA).

## Cuidados operacionais

- **Nada é deletado, em nenhum momento** — o processo inteiro é só `mv` (mover/renomear) e `mkdir`. Câmeras descartadas vão para `não encontrados/`, nunca para a lixeira.
- Sempre citar paths entre aspas (nomes têm espaços, acentos, emojis e `=`).
- Verificar que o destino não existe antes de cada `mv`; nunca usar `-f`.
- Alguns arquivos de tela têm extensão dupla (`... .mp4.mp4`) por erro do OBS. Isso é só cosmético — se Rodrigo pedir, dá para corrigir com renomeação; não corrigir por conta própria.
- A pasta de trabalho pode ter arquivos que não são vídeo (`.DS_Store` etc.) — ignorar.

## Aprendizados / ajustes (manter atualizado)

- **Primeira execução do Tipo 4 (14/08, pasta `2026_08_13`)**: 11 telas na raiz × 20 câmeras → 11 pares, todos com Δ ≤ 6,2s (a maioria < 1s), 9 câmeras para `não encontrados/`. O **pareamento saiu perfeitamente monotônico** (aulas `1.2→2.4` ↔ câmeras `0637→0650`, sem cruzamento). As duas ambiguidades dentro da tolerância (`1.4`: 0632 vs 0639; `1.7`/`2.2` disputando 0643 e 0648) se resolveram sozinhas.
- **Lição da 1ª execução — usar o horário de início desde o começo, não só a duração** (levantado por Rodrigo 14/08, depois da execução): na conferência posterior, o offset início-câmera − início-tela ficou entre **+3:10 e +3:14 nos 11 pares** (4s de amplitude no dia inteiro), confirmando cada par de forma independente e fechando as duas ambiguidades com folga de mais de 1h. **O horário separa melhor que a duração** — takes descartados podem ter duração quase idêntica, mas nunca o mesmo horário. Na 1ª execução isso ficou de fora do plano; nas próximas, medir e apresentar o offset junto com o delta de duração.
- **`MVI_0632` era a câmera da aula "1.1. Apresentação"**, não um take descartado — foi para `não encontrados/` e Rodrigo o renomeou/moveu manualmente depois. Pelo horário, `MVI_0631` (191s) foi o take falso que terminou 14:03:12 e `0632` começou 14:03:13 — a retomada da mesma apresentação. Origem do aprendizado sobre aulas só-câmera documentado acima.
- **Tipo 4 — armadilhas técnicas já encontradas**:
  - **Vídeos alheios na raiz**: a raiz de `Movies` tem vídeos que não são do lote (ex: `igor_adapta.mp4`, de julho). Um deles chegou a ficar a 3,9s de uma câmera do lote — se entrasse na conta, poderia sujar o pareamento. **Filtrar as telas pelo padrão de nome de aula** (`1.2.`, `2.3.` …) e não pegar tudo que é `.mp4` da raiz.
  - **`zsh` sem `nullglob`**: `for f in *.mp4 *.MP4` falha com "no matches found" se um dos globs não casar. Usar `find … -print0 | while IFS= read -r -d ''`.
  - **Normalização unicode do macOS (NFD)**: não hardcodar nomes com acento no script (`memória`, `não`). Indexar os arquivos reais com `os.listdir` e casar por **prefixo ASCII** (`1.4`) ou basename da câmera (`MVI_0639`), derivando o nome final do nome que está no disco.
  - **Extensão dupla `.mp4.mp4`** (bug do OBS, apareceu em `1.2` e `2.1`): ao montar o nome da câmera, remover todos os `.mp4` do fim antes de acrescentar `_cam`. As telas ficaram com a extensão dupla mesmo — não corrigi por conta própria.
  - Rodar o `ffprobe` de novo dentro do script como **assert** de que cada par está dentro dos 10s, e conferir contagem antes/depois (31 → 31), antes e depois de mexer.
