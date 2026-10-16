# ADR-001 (parcial): orquestrador — Temporal self-hosted (Fase 0.5)
> **Snapshot histórico:** o status abaixo registra a avaliação de 09/10/2026; não é o estado operacional atual. Consulte `docs/ROADMAP.md` e `docs/TESTES.md` para os gates e resultados atuais.

> Status: **PARCIAL**. Em 09/10/2026: TZ-01 a TZ-04 aprovados (TZ-02 sem reboot, dispensado em t334); TZ-05 **bloqueado** (`--yolo` incondicional no `hermes_local`); TZ-06 pendente (Telegram); soak de 24 h em andamento. A decisão final (TZ-07) sai depois do soak.
> Autoridade: abaixo de `docs/REGRAS.md`, `docs/SPEC.md` e `docs/ARQUITETURA.md` (ADR-002). Origem: t329, t333, t334.

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
| TZ-02 | **Aprovado** (reboot dispensado pelo José em t334; o restart do motor cobre o caso) | `kill -9` no worker durante os retries e durante o timer, e restart do container do Temporal durante a espera do sinal: o workflow retomou do ponto certo (roteiro na tentativa 4, depois de 3 falhas simuladas) e o efeito do outbox rodou 1 vez. O reboot do servidor não foi feito. |
| TZ-03 | **Aprovado** | "Supabase" (stub em arquivo) fora antes do outbox, com `kill -9` no worker no meio: o estado ficou `aguardando_outbox` (nada concluído sem estado) e as retentativas foram duráveis. Na volta gravou 1 vez (tentativa 7). Em 103 efeitos, 0 duplicados. |
| TZ-04 | **Aprovado** | Ponte de ponta a ponta no Paperclip de teste (empresa `PQBR-TESTE`), workflow `tz04-ponte-04` / issue PQB-4. O Temporal abre a issue e acorda o agente com `--resume`. O agente (adaptador `process`, sem LLM) comenta uma proposta inválida e uma válida dentro do próprio run. A proposta inválida foi rejeitada pela validação Pydantic v2, com comentário do Temporal na issue. A válida ficou aguardando o José. O sinal de outro remetente foi ignorado. O sinal `jose` aplicou a proposta (stub, 1 linha) e concluiu a issue. Nada foi aplicado antes da aprovação. O agente não tem rota nem credencial para o Postgres do Temporal (sem porta publicada; senha só em `infra/temporal/.env`). |
| TZ-05 | **Bloqueado** | O `@paperclipai/hermes-paperclip-adapter` 2026.1001.0 (`dist/server/execute.js`, linha 391) faz `args.push("--yolo")` **sempre**, sem opção de configuração. Por isso nenhum agente `hermes_local` foi criado nem executado. Heartbeats: o agente de teste foi criado com `heartbeat.enabled=false` e ficou pausado fora dos runs do teste. O conserto da #3833 não foi conferido. Alternativas para o José decidir (H-SDD1): (a) PR/patch upstream com opção para desligar o `--yolo`; (b) agente com adaptador `process` chamando o Hermes `pqbr` com aprovação própria; (c) outro adaptador. |
| TZ-06 | **Pendente (parte do motor ok)** | Sinal de remetente diferente de `jose` é ignorado (`sinais_ignorados=1`). Falta a ponte do Telegram (Hermes `pqbr`). |
| TZ-07 | **Parcial** | Este documento. Até agora o Temporal não reprovou nenhum TZ; o DBOS não foi necessário. |

## Integração Temporal ↔ Paperclip (TZ-04) [VERIFICADO no teste t334]

1. Código: `src/pqbr/workflows/paperclip.py` e `PonteTemporalPaperclipWorkflow`. A Activity `abrir_issue_paperclip` usa o CLI oficial `paperclipai` com o contexto de board do servidor (nenhum token no código). A idempotência vem do marcador `[wf:<id>]` no título.
2. A Activity `comentar_paperclip` com `--resume` acorda o agente responsável **com o contexto da issue**. Sem isso, o Paperclip recusa o comentário do agente (403, `cross_issue_influence_run_context_required`).
3. O agente responde dentro do próprio run com um bloco ```json``` de `PropostaAgente` (`scripts/tz/agente_processo.sh`).
4. `ler_propostas_paperclip` consulta periodicamente, em ordem cronológica. O workflow valida em Pydantic v2: a inválida recebe comentário de rejeição; a válida segue para aprovação.
5. A aprovação do José vira o sinal `aprovacao_jose`. No teste foi um stub pelo `scripts/tz/tz.py`; a origem pelo Telegram é o TZ-06. Depois do sinal: `aplicar_proposta_stub`, comentário na issue e `done`.
6. O agente nunca recebe credenciais do Postgres do Temporal.
7. Achados:
   - Agente pausado com issue `in_progress` faz a recuperação automática do Paperclip marcar a issue `blocked`. Na produção, concluir a issue antes de pausar ou não pausar no meio do fluxo.
   - O `PAPERCLIP_API_URL` injetado no run usa o hostname local, que não escuta; o script usa o `apiBase` do contexto do CLI.

## Criado no Paperclip (teste t334) e limpeza

Nada foi alterado em Core Engineering, tutibom ou rede_midia.

| Item | ID |
|---|---|
| Empresa `PQBR-TESTE` (prefixo PQB) | `d9fa962a-6ee6-42c7-93aa-59a86313a658` |
| Projeto `TZ-04 ponte Temporal` | `4f25a797-7910-4a83-ae3e-e77cdfbac497` |
| Agente `tz-proponente` (process, pausado, heartbeat off) | `98cdf54a-b0a6-41d6-9b00-364a8b745536` |
| Issues PQB-1 (cancelada) | `0b42107a-a135-4e28-a240-e5d7f7436978` |
| Issues PQB-2 (cancelada) | `4dd351b7-0595-4cbb-9d45-4eda5f98ec2c` |
| Issues PQB-3 (done) | `e7486416-0d2e-40b9-9478-375ca0af1975` |
| Issues PQB-4 (done) | `f4348170-7bc0-4ab0-a960-d29abac99085` |
| Chaves de agente (criadas para uma tentativa manual, recusada pelo Paperclip) | `5fcd3096-…` e `ee5a3f40-9c2a-4443-9a71-af9adbf78075`, **ambas revogadas**; arquivo apagado |
| Runs de heartbeat (2 falharam nos ajustes) | `e965c831-…`, `2b616340-…`, `02d4cad5-…` e o run do teste final |

Limpeza (no `pc`):

```
P="$HOME/.hermes/node/bin/node $HOME/.paperclip/cli/current/node_modules/paperclipai/dist/index.js"
$P agent delete 98cdf54a-b0a6-41d6-9b00-364a8b745536
$P project delete 4f25a797-7910-4a83-ae3e-e77cdfbac497
$P company archive d9fa962a-6ee6-42c7-93aa-59a86313a658   # reversível
$P company delete d9fa962a-6ee6-42c7-93aa-59a86313a658    # definitivo; apaga issues e comentários
```

Também `rm runtime/tz/propostas_aplicadas.jsonl`. Os workflows `tz04-ponte-*` saem com a retenção do namespace ou com `docker compose down -v`.

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

## Resultado (t374, 10/10/2026)
- Soak encerrado às 11:57: 122 execuções em ~20 h, 0 falhas/expiradas, 0 perdidas, 0 duplicatas no outbox; pico do compose 340 MiB, worker 53 MiB, nenhuma amostra acima de 1536 MiB.
- **Decisão: motor = Temporal. DBOS dispensado.**
