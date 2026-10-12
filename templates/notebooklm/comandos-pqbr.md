# PQBR — comandos e prompts do caderno efêmero (pacote canônico, t459)

Fonte de verdade: Postgres `pqbr.pacote_canonico` (hash). Este arquivo é um item do pacote; mudar aqui = nova versão.

## Comandos fechados (notebooklm-py 0.8.4, perfil pqbr, `workflows/notebooklm.py`)
1. `create "Short - <PQBR-EPxxxx> - <slug>"` → id registrado em `pqbr.cadernos_episodio`.
2. `configure --persona` (persona-pqbr.txt) antes de qualquer outra coisa.
3. `source add --type file` do pacote canônico ("PQBR pacote <hash12>") e depois do roteiro.
4. `generate video --format short --language pt_BR --no-wait "<steering>"` (steering = bloco visual 2D do roteiro + reforços fixos: sem texto escrito na imagem; mesmo personagem em todas as cenas; t462); acompanhar com `artifact list`; nunca regerar se já há vídeo.
5. `ask` sem `--new`; no máximo 3 chats por caderno; pesquisa web com `source add-research` (fast ou deep) + `--import-all`.
6. Arquivar (`metadata`, `source fulltext`, `history`, vídeo) → Drive + Postgres.
7. `delete -n <UUID completo> -y` só via `ApagarCadernoWorkflow` (D+2 após publicação, allowlist, nunca mestre, nunca por título).

## Prompts
- **Roteiro:** "Escreva o roteiro do Short sobre <tema> seguindo o contrato editorial e o bloco visual §16.7 do pacote: gancho até 3 s com a imagem literal da expressão, versão mais aceita + 'mas tem quem diga', ≥ 2 fontes, loop na última cena."
- **SEO:** "Gere título (≤ 100), descrição (≤ 5000) e 3–15 hashtags pt-BR para o roteiro, sem pedir comentário; categoria 27 Educação."
- **Vídeo:** a fonte do roteiro já leva o bloco [ESTILO]/[PERSONAGEM]/[AMBIENTE]/[CENAS] preenchido; o Short não tem seletor de estilo.
