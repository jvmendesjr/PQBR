# ADR-001 (parcial): orquestrador — Temporal self-hosted (Fase 0.5)

> Status: **PARCIAL**. TZ-01 a TZ-03 aprovados em 09/10/2026; o soak de 24 h está em andamento; TZ-04 a TZ-06 aguardam a autorização do José para escrever no Paperclip (t333). A decisão final (TZ-07) sai depois do soak e dos TZ-04 a TZ-06.
> Autoridade: abaixo de `docs/REGRAS.md`, `docs/SPEC.md` e `docs/ARQUITETURA.md` (ADR-002). Origem: t329, t333.

## Instalação (F05-01)

- `infra/temporal/docker-compose.yml`, projeto `pqbr-temporal`, rede `pqbr-temporal`:
  - Temporal Server 1.32.1, Postgres 16 dedicado e UI 2.49.1;
  - sem Elasticsearch, com visibilidade no próprio Postgres;
  - `NUM_HISTORY_SHARDS=4`, escolhido uma vez;
  - namespace `pqbr`.
- Portas só em `127.0.0.1`: gRPC `7233` e UI `8233`; o Postgres não tem porta publicada. O acesso remoto à UI é por túnel SSH (`ssh -L 8233:127.0.0.1:8233 pc`).
- Limites de memória rígidos do Docker, com `memswap_limit` igual ao limite, então sem swap:

  | Serviço | Limite |
  |---|---|
  | postgres | 400M |
  | temporal | 750M |
  | ui | 200M |
  | **Total** | **1350M**, abaixo do teto de 1,5 GB (t329) |

- Senha do Postgres em `infra/temporal/.env`, gerada no servidor, `chmod 600` e fora do git. O modelo está em `.env.example`.
- Worker: `src/pqbr/workflows/` (temporalio 1.34.0, Pydantic v2.14, conversor Pydantic), venv `.venv/` (fora do git). Serviço de usuário systemd `pqbr-temporal-worker` com `Restart=always` e `MemoryMax=256M`. Cópias das units em `infra/temporal/systemd/`.

## Resultados

| ID | Resultado | Evidência (09/10/2026, horário de Fortaleza) |
|---|---|---|
| TZ-01 | **Aprovado** | RAM em repouso ≈ 218–285 MiB (temporal 100–135, postgres 110–140, ui 7). Carga de 100 workflows concorrentes em 9 s: pico de 307 MiB no compose, pico de 58 MiB no worker, sem OOM. `pg_dump` e restauração num banco temporário com contagens iguais (executions 5/5, history_node 58/58); o banco temporário foi apagado. |
| TZ-02 | **Aprovado, exceto o reboot** | `kill -9` no worker durante os retries e durante o timer, e restart do container do Temporal durante a espera do sinal: o workflow retomou do ponto certo (roteiro na tentativa 4, depois de 3 falhas simuladas) e o efeito do outbox rodou 1 vez. O reboot do servidor não foi feito (fora da autorização). |
| TZ-03 | **Aprovado** | "Supabase" (stub em arquivo) fora antes do outbox, com `kill -9` no worker no meio: o estado ficou `aguardando_outbox` (nada concluído sem estado) e as retentativas foram duráveis. Na volta gravou 1 vez (tentativa 7). Em 103 efeitos, 0 duplicados. |
| TZ-04 | **Pendente** | Só a parte do motor: o sinal `proposta_agente` aceita proposta válida e rejeita a inválida (Pydantic v2), e nada é aplicado sem o sinal de aprovação. O Paperclip foi só lido: `/api/health` ok, commit `8f8a0ab`, modo `authenticated`/`private`. Abrir issue no Paperclip precisa de autorização. |
| TZ-05 | **Pendente** | Precisa de agente de teste no Paperclip (H-SDD1 `--yolo`). |
| TZ-06 | **Pendente (parte do motor ok)** | Sinal de remetente diferente de `jose` é ignorado (`sinais_ignorados=1`). Falta a ponte do Telegram (Hermes `pqbr`). |
| TZ-07 | **Parcial** | Este documento. Até agora o Temporal não reprovou nenhum TZ; o DBOS não foi necessário. |

## Integração proposta com o Paperclip (TZ-04) [PROPOSTA, sem escrita feita]

1. Uma Activity `abrir_issue_paperclip` (API REST do Paperclip, token de serviço fora do git, chave de idempotência = `workflow_id`) cria ou atualiza a issue num projeto de teste.
2. O agente responde na issue com JSON de `PropostaAgente`.
3. Um webhook ou consulta periódica (Activity) lê a resposta e envia o sinal `proposta_agente`. O workflow valida em Pydantic v2.
4. A aprovação do José (painel ou Telegram) vira o sinal `aprovacao_jose`.
5. O agente nunca recebe credenciais do Postgres do Temporal.

## Soak de 24 h (09/10 ~15:36 → 10/10 ~15:40, horário de Fortaleza)

- Schedule `pqbr-soak-24h`: um `EpisodioWorkflow` a cada 10 min, com 1 falha simulada, timer de 60 s, aprovação automática e outbox (stub). Sobreposição: SKIP.
- Amostra de RAM a cada 5 min (timer de usuário `pqbr-temporal-ram.timer`), gravada em `runtime/tz/ram.log`, fora do git.
- Conferir: `sh scripts/tz/soak_check.sh`. O soak aprova com:
  - pico do compose ≤ 1536 MiB;
  - 0 amostras acima do teto;
  - cerca de 144 execuções concluídas;
  - 0 falhas;
  - 0 duplicados.

## Operação e rollback

- Subir: `cd infra/temporal && docker compose up -d`.
- Parar o soak:
  ```
  systemctl --user disable --now pqbr-temporal-ram.timer
  docker run --rm --network pqbr-temporal temporalio/admin-tools:1.32.1 temporal --address temporal:7233 -n pqbr schedule delete --schedule-id pqbr-soak-24h
  ```
- Rollback total:
  ```
  systemctl --user disable --now pqbr-temporal-worker pqbr-temporal-ram.timer
  rm ~/.config/systemd/user/pqbr-temporal-*
  systemctl --user daemon-reload
  cd infra/temporal && docker compose down -v
  rm -rf ../../.venv ../../runtime/tz
  ```
  Remove containers, volume e rede. Não afeta outros serviços.
