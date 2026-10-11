# Tarefa bloqueada → todo (teste t396: run morto vira `blocked`, locks limpos, ninguém reacorda)
1. Observador: a cada relatório, listar issues `blocked` há > 30 min com último run `failed`.
2. Ler o erro do run. Transitório (rede, 9router, timeout): voltar para `todo` mantendo o dono; comentar "retomada automática (1/3)".
3. Mesmo erro 2×: Diretor reatribui a outro agente da mesma trilha (se houver) ou ao dono com `--force-fresh-session`; comentar.
4. 3ª falha: label `tipo:incidente`, ticket ao Dev Corretor com evidências; Telegram via Diretor.
