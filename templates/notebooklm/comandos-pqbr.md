# PQBR — comandos e prompts do caderno efêmero (pacote canônico, t459)

Fonte de verdade: Postgres `pqbr.pacote_canonico` (hash). Este arquivo é um item do pacote; mudar aqui = nova versão.

## Comandos fechados (notebooklm-py 0.8.4, perfil pqbr, `workflows/notebooklm.py`)
1. `create "Short - <PQBR-EPxxxx> - <slug>"` → id registrado em `pqbr.cadernos_episodio`.
2. `configure --persona` (persona-pqbr.txt) antes de qualquer outra coisa.
3. `source add --type file` do pacote canônico ("PQBR pacote <hash12>") e depois do roteiro.
4. `ask` sem `--new` para roteiro, compliance, SEO e o JSON do storyboard. Não existe `generate video` (t130u). O storyboard sai da activity `storyboard_criar`.
5. No máximo 3 chats por caderno; pesquisa web com `source add-research` (fast ou deep) + `--import-all`.
6. Arquivar (`metadata`, `source fulltext`, `history`) → Drive + Postgres. Sem vídeo do caderno.
7. `delete -n <UUID completo> -y` só via `ApagarCadernoWorkflow` (D+2 após publicação, allowlist, nunca mestre, nunca por título).

## Prompts
- **Roteiro:** "Escreva o roteiro do Short sobre <tema> seguindo o contrato editorial e o bloco visual §16.7 do pacote: gancho até 3 s com a imagem literal da expressão, versão mais aceita + 'mas tem quem diga', ≥ 2 fontes, loop na última cena."
- **SEO:** "Gere título (≤ 100), descrição (≤ 5000) e 3–15 hashtags pt-BR para o roteiro, sem pedir comentário; categoria 27 Educação."
- **Storyboard:** o chat devolve só o JSON da ficha (contrato Storyboard 1.2.0). Imagem e vídeo não saem deste caderno. A cadeia visual é Flow → Vids → Vibes, fora desta etapa. No JSON, `inicio` é a foto parada do começo da ação e vira o `prompt_imagem`, com a frase-trava da ficha, sem redesenhar a roupa. `prompt_animacao` descreve o corpo saindo desse frame até o `fim`, com "lips closed". A referência é o recorte de um boneco (`ASSET_*`), não a folha inteira. Isso veio dos materiais de 28/10 e cabe neste contrato (t141u). O caderno não chama Claude, Vsub nem outro gerador.
