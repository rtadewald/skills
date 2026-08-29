# AGENTS

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
