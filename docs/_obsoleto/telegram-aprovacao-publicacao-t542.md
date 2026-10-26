# Obsoleto (t542, 25/10/2026) — Telegram como aprovação de publicação

Movido sem apagar: José decidiu que o Telegram é manutenção/relatórios/observabilidade, não aprovação de publicação. Publicação automática pelo gate (F8-01, `workflows/publicacao.py`).

## De `docs/ROADMAP.md`

  - **Escopo novo (t510, ADR-011):** activity de pedido de aprovação → mensagem Telegram pelo Hermes `pqbr` → sinal `aprovacao_jose` no workflow; ID autorizado, tarefa, estado e idempotência persistente no Postgres; falha fechada. Os registros Discord/Paperclip abaixo são históricos.

## De `docs/sdd/PLANO-ponte-telegram-duravel.md`

- Ligados: `EpisodioWorkflow` e `PonteTemporalPaperclipWorkflow` (antes de esperar `aprovacao_jose`; soak automático não chama) e `AcessosWorkflow` (avisos/pedidos ao fim de cada rodada).
