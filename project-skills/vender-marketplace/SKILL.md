---
name: vender-marketplace
description: Transforma fotos de coisas paradas em casa em anúncios prontos e publicados no Facebook Marketplace e na OLX — identifica cada item, melhora a foto com um modelo de imagem barato (OpenRouter), pesquisa o preço justo de usado, escreve título e descrição e publica pelo Chrome do usuário (extensão Claude in Chrome, já logado). Use quando o usuário mandar fotos de itens e pedir para vender, anunciar ou precificar.
---

# Vender no Marketplace e na OLX

## 1. Olhe cada foto
Para cada foto em `fotos/` (ou as que o usuário mandar): diga o que é o item (marca, modelo, tamanho), o estado (o
desgaste, os defeitos que aparecem) e o que falta saber (pergunte só o que muda o preço: ano, voltagem, acessórios).

## 2. Melhore as fotos (modelo de imagem barato)
```bash
uv run .claude/skills/vender-marketplace/scripts/editar_foto.py fotos/<foto>.jpg anuncios/<item>/<n>.png "<pedido>"
```
- Pedido típico: "tire da foto tudo que não é o item (a base, a mesa, o fundo bagunçado) e deixe um fundo liso e claro;
  luz mais uniforme". Uma foto por pedido; confira cada resultado olhando a imagem.
- **Nunca esconda defeito** nem troque o item: compare com a original. Se o modelo mudou o item, refaça ou use a original.
- Padrão: `google/gemini-2.5-flash-image` (centavos por foto). A chave: `OPENROUTER_API_KEY` no `.env`.
- Além da foto limpa, use a original e recortes de detalhe (a marca, o estado do cabo, a etiqueta): comprador confia em
  foto real.

## 3. Preço justo
Pesquise anúncios do mesmo item **usado** no Facebook Marketplace, na OLX e no Mercado Livre da região do usuário
(navegando pelo Chrome dele). Anote 5 a 10 preços, descarte os extremos e proponha:
- o preço de anúncio (a mediana, um pouco acima para ter margem de negociação);
- o mínimo que vale aceitar.

## 4. O anúncio
Para cada item, em `anuncios/<item>/anuncio.md`: título (marca + modelo + o atributo que mais vende, até 60
caracteres), descrição (o que é, o estado com honestidade, o que acompanha, retirada/entrega), categoria e preço.

## 5. Publique pelo Chrome
Com a extensão Claude in Chrome (o usuário já logado no Facebook e na OLX):
1. Facebook: `facebook.com/marketplace/create/item` → fotos, título, preço, categoria, condição, descrição.
2. OLX: `olx.com.br` → Anunciar → mesma coisa.
3. **Mostre ao usuário o anúncio preenchido e só clique em Publicar depois do "ok" dele.**
4. Poucos anúncios por vez, com calma: publicar tudo de uma vez faz a plataforma achar que é robô e travar a conta.

## 6. Depois (opcional)
Uma tarefa agendada a cada 24 h pode ler as mensagens dos compradores e sugerir respostas; negociar e combinar entrega
só com o usuário aprovando.
