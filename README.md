# Skills

Biblioteca pessoal de skills para agentes de IA (Cursor / Claude / Codex).

Cada pasta é uma skill (`SKILL.md` + scripts/assets se precisar). Não é um app — são fluxos e ferramentas.

---

## Planejamento de telas

Inventar e fechar a direção de uma tela de app (conversa → proposta → imagem).

| Skill | O que faz |
|-------|-----------|
| `plan-screen-with-svg` | Briefing + 3 propostas com **wireframe SVG** → gera PNGs em `mocks/` |
| `plan-screen-with-ascii` | Mesmo fluxo, mas propostas com **planta ASCII** |

## Design system

Extrair / materializar a linguagem visual de uma referência.

| Skill | O que faz |
|-------|-----------|
| `img-to-ds` | Mock (imagem) → `design-systems/<slug>/` com `design-system.html` + CSS |
| `extract-design-system` | HTML monolítico → `design-system.html` limpo + assets separados |

## Imagem

Gerar ou converter artefatos visuais.

| Skill | O que faz |
|-------|-----------|
| `to-img` | Qualquer pedido → **n** PNGs em paralelo (OpenRouter, default gpt2 @ 1K) em `mocks/` |
| `to-ascii` | Mock PNG → planta ASCII (`.txt` ao lado) |
| `to-svg` | Mock PNG → wireframe SVG (`.svg` ao lado) |
| `openrouter-img` | CLI/API OpenRouter (vários modelos de imagem) |
| `nano-banana-pro` | Gerar/editar imagem via Nano Banana Pro (Gemini) |

## Motion e mídia

| Skill | O que faz |
|-------|-----------|
| `animate` | Decidir e implementar animação/transição com critério |
| `mediabunny` | Áudio/vídeo com a lib Mediabunny |

## Planejamento e entrega

| Skill | O que faz |
|-------|-----------|
| `grill-me` | Entrevista dura para afiar plano ou design |
| `to-tickets` | Quebra plano/spec em tickets com dependências |
| `handoff` | Compacta a conversa num documento para outro agente continuar |

## Utilitários

| Skill | O que faz |
|-------|-----------|
| `context7-mcp` | Docs atuais de libs/frameworks via Context7 (em vez de chutar pela memória) |
