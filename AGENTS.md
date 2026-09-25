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
