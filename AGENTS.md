# AGENTS

## Estrutura de escrita das skills

Ao criar ou reescrever uma skill que descreve um processo, comece o corpo do
`SKILL.md` nesta ordem:

1. **Quem você é** — defina claramente o papel do agente.
2. **Seu objetivo** — explique o resultado final e os princípios que devem ser
   preservados.
3. **Processo em alto nível** — apresente o fluxo completo, do início à entrega,
   sem detalhes de implementação.

Somente depois desse mapa inicial entre em regras, exceções, ferramentas e
instruções operacionais. Não comprima os três blocos em um parágrafo genérico e
não desça para o baixo nível antes de o processo completo estar claro.

## Clareza, concisão e exemplos

Antes de explicar **como** uma skill funciona, diga em poucas palavras:

1. o que ela permite fazer;
2. qual é seu principal benefício; e
3. qual resultado o usuário recebe.

Avance sempre do geral para o específico: **valor → resultado → processo →
regras e ferramentas**. Use frases curtas e precisas. Elimine contexto,
repetições e justificativas que não mudem uma decisão.

Sempre inclua ao menos um exemplo curto para tornar a instrução concreta.

Exemplo de abertura:

> Extract DS é uma Skill que te permite gerar Design Systems completos a partir
> de uma simples página HTML local. Isso permite criar novas interfaces usando
> referências visuais de alta qualidade, já implementadas e validadas.

Somente depois desse benefício explique detalhes como tipografia, cores,
componentes, runtime ou ferramentas.

## README

Sempre que houver qualquer alteração no **nome** de uma skill (renomear pasta, criar skill nova, apagar skill, ou mudar o `name` no frontmatter), atualize também o [`README.md`](./README.md) para refletir a mudança.

## OpenAI agent metadata

Toda skill neste repositório deve ter o arquivo `agents/openai.yaml`, no padrão:

```yaml
interface:
  display_name: "Nome amigável"
  short_description: "Uma linha do que faz"
  default_prompt: "Use $nome-da-skill: …"
policy:
  allow_implicit_invocation: false
```

Ao **criar** ou **renomear** uma skill, crie ou atualize esse arquivo junto (o `$nome-da-skill` no `default_prompt` deve bater com a pasta / `name` do `SKILL.md`).
