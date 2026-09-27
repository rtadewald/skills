# Extract DS

Transforma um site local finalizado em um design system navegável, preservando a
identidade visual, o código existente, as interações e as principais animações.

![Demonstração da Extract DS com Sonic.Link e Asimov](assets/extract-ds-demo.webp)

[Assistir à demonstração em alta qualidade (MP4)](assets/extract-ds-demo.mp4)

O fluxo é **copy-first**: a skill copia e adapta o projeto original em vez de
redesenhar ou reconstruir a interface. A entrega acontece em duas etapas, cada
uma com aprovação explícita do usuário.

## O que ela faz

1. Analisa rapidamente como o projeto roda: `file://` ou servidor local.
2. Copia o projeto completo para `<marca>-design-system/`.
3. Cria o **Overview**, preservando layout, navbar, efeitos e animações.
4. Adapta a hero para apresentar o design system e troca a copy editorial por
   Lorem Ipsum.
5. Entrega o Overview para validação do usuário e aguarda aprovação.
6. Extrai o catálogo de **Components** diretamente do Overview aprovado.
7. Entrega Components para uma segunda validação.

O catálogo reaproveita HTML, classes, CSS, assets e estados reais. A página de
Components usa a principal animação do Overview como fundo e inclui os
backgrounds observados como espécimes vivos — sem screenshots ou recriações.

### Decisão de runtime

- Se o projeto já funciona por `file://`, a skill segue pelo caminho rápido.
- Se exige servidor, ela pergunta se deve preservar o runtime atual ou fazer a
  conversão mais demorada para `file://`.
- A validação visual fica com o usuário. A skill não abre Chrome, Playwright ou
  ferramentas de screenshot automaticamente.

## Instalação

Clone este repositório:

```bash
git clone https://github.com/rtadewald/skills.git
```

Copie a pasta `extract-ds` para o diretório de skills usado pelo seu agente.

Exemplo para o diretório compartilhado de agents:

```bash
mkdir -p ~/.agents/skills
cp -R skills/extract-ds ~/.agents/skills/
```

Exemplo para Claude Code:

```bash
mkdir -p ~/.claude/skills
cp -R skills/extract-ds ~/.claude/skills/
```

Se você já clonou o repositório dentro do diretório de skills, não precisa fazer
a cópia novamente.

## Como usar

Passe o caminho absoluto do site finalizado:

```text
Use $extract-ds no projeto "/caminho/absoluto/para/o-site".
```

Em clientes que expõem skills como comandos:

```text
/extract-ds "/caminho/absoluto/para/o-site"
```

Caminhos com espaços ou parênteses devem permanecer entre aspas.

### Fluxo esperado

```text
site original
    ↓ cópia fiel
<marca>-design-system/
    ↓
Overview → aprovação do usuário
    ↓
Components → aprovação final
```

A saída principal fica em:

```text
<marca>-design-system/design-system.html
```

Abra esse arquivo diretamente quando o runtime escolhido for `file://`. Se o
projeto preservar um servidor local, use o comando original informado pela
skill.

## Estrutura da entrega

```text
<marca>-design-system/
├── design-system.html
└── assets/
    └── overview/
        └── ...cópia funcional do projeto original
```

O resultado final mantém Overview e Components no mesmo catálogo, com navegação
por hash e uma única navbar adaptada à identidade visual do projeto.
