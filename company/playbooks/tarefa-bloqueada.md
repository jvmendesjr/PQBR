# Tarefa bloqueada → nova tarefa (t397; teste t396: `blocked` → `todo` volta a `blocked` sozinho)
Run morto deixa a issue `blocked` com locks limpos; reabrir a mesma issue não funciona.
1. Observador: a cada relatório, listar issues `blocked` há > 30 min cujo último run está `failed`.
2. Erro transitório (rede, 9router, timeout): **abrir nova issue** com o mesmo título + " (retomada N/3)", a descrição original e o link da antiga, atribuída ao mesmo dono (a atribuição acorda o agente). Cancelar a antiga com comentário apontando a nova.
3. Mesmo erro 2×: o Diretor abre a nova issue para outro agente da trilha (se houver) ou para o dono com `--force-fresh-session`.
4. 3ª falha: label `tipo:incidente`, ticket ao Dev Corretor com as evidências das 3 issues; Telegram via Diretor.
