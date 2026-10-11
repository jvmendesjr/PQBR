# ROADMAP da PQBR (tarefas granulares, para qualquer agente retomar)

> **Como retomar (qualquer agente, qualquer sessão):**
> 1. Leia **só**, nesta ordem: `docs/REGRAS.md` → `docs/SPEC.md` → `docs/ARQUITETURA.md` → `docs/TESTES.md` → este `docs/ROADMAP.md`. Em conflito, vale o primeiro.
> 2. ⛔ **Nunca consulte** `docs/arquivo/`, `docs/pesquisas/`, `docs/DECISOES-LOG.md`, `docs/CONTRATO-EDITORIAL.md` nem qualquer rascunho ou material legado **sem aprovação explícita do José** (t287).
> 3. Pegue a **primeira tarefa `- [ ]` cujas dependências estejam todas `- [x]`**. Não pule portões do José.
> 4. Dúvida ou conflito que as regras aprovadas não resolvem com certeza: **não adivinhe**. Escreva "EM CONSTRUÇÃO — aguardando José" no `Obs:` e avise (t323).
> 5. Mudanças durante a construção são tarefas deste roteiro, nunca tickets (REGRAS §24). Nada de push sem autorização do José.
>
> **Como marcar concluída:** troque `- [ ]` por `- [x]` e acrescente na mesma linha `— AAAA-MM-DD — commit <hash curto>`; no `Obs:`, registre o que foi feito, as evidências (IDs de teste do TESTES.md) e os desvios. Parcial continua `- [ ]`, com o estado no `Obs:`.
> **Atualize este arquivo a cada tarefa concluída**, no mesmo commit do trabalho (ou no seguinte, se precisar do hash).
> Campos: **Req** = IDs do `SPEC.md`; **Testes** = IDs do `TESTES.md`; **Dn** = numeração antiga das tarefas de desenvolvimento. Fases, portões e rollback: `docs/PLANO.md`.

---

## Concluído

- [x] **R-000** Estrutura do repositório — 2026-10-09 — commit ade0ebb
  - Obs: `/home/pc/Workspace/PQBR` (GitHub `jvmendesjr/PQBR`, privado), pastas só com README.
- [x] **R-001** Perfil Hermes `pqbr` criado — 2026-10-09 — sem commit (config do servidor)
  - Obs: sem `--yolo` e sem sudo sem senha; ajuste fino em F1-03.
- [x] **R-002** Saída do CTO (COR-1) e levantamento de vídeos arquivados no Drive — 2026-10-09 — sem commit
  - Obs: Drive `PQBR/_arquivo-docs-2026-10-09/`; sha256 conferido antes de apagar do servidor.
- [x] **R-003** Sanitização dos documentos — 2026-10-09 — commit 66aacb2
  - Obs: REGRAS/ARQUITETURA/PLANO/CONTRATO/DECISOES-LOG, `pesquisas/`, `arquivo/`, `db/seeds/temas-publicados.csv`; t287.
- [x] **R-004** Decisões t324–t326 registradas — 2026-10-09 — commit 1598d8e
- [x] **R-005** Decisões t327–t328 registradas; conjunto SDD criado (SPEC, TESTES, RASTREABILIDADE, ROADMAP) — 2026-10-09 — commit 7ef5f39
  - Obs: Temporal + Paperclip (agentes no Paperclip); sem teto de orçamento; imagem×fala não reprova; revisão humana como último recurso; escopo só PQBR.
- [x] **R-006** Decisões t329–t332: teto de RAM 1,5 GB; escopo do escalonamento; Studio/Visualização sem pendência — 2026-10-09 — commit: ver `git log -1 -- docs/ROADMAP.md`
  - Obs: —

---

## Fase 0.5: teste de 1 dia do Temporal ligado ao Paperclip ← PRIMEIRO PASSO ABERTO

- [x] **F05-01** Subir o Temporal com Postgres próprio e medir recursos
  - Req: RNF-09 · Testes: TZ-01 · Depende de: R-005
  - Aceite: Temporal em compose isolado, Postgres dedicado (sem Elasticsearch, separado do `mp32-postgres`); RAM ≤ 1,5 GB para Temporal + Postgres dedicado (t329; H-ORQ1); dump e restauração testados (H-ORQ2).
  - Portão José: autorizar a instalação.
  - Obs: 2026-10-09, commit: ver `git log -1 -- docs/sdd/adr-001-orquestrador.md`. Temporal 1.32.1 + Postgres 16 em `infra/temporal` (só 127.0.0.1; limites 400M/750M/200M). Repouso ≈ 220–285 MiB; pico com 100 workflows 307 MiB; dump e restauração ok. Soak de 24 h até 10/10 ~15:40 (`sh scripts/tz/soak_check.sh`). Ver `docs/sdd/adr-001-orquestrador.md`.
- [x] **F05-02** `EpisodioWorkflow` de brinquedo
  - Req: RNF-05 · Testes: TZ-02 · Depende de: F05-01
  - Aceite: timer + Activity que falha e retenta; retoma após `kill -9` no worker e após reboot.
  - Portão José: autorizar o reboot, se for o do servidor.
  - Obs: 2026-10-09: retries, timer, sinal, `kill -9` no worker e restart do motor ok; 0 duplicados. Reboot do servidor dispensado pelo José (t334); o restart do motor cobre o caso.
- [x] **F05-03** Outbox para o banco do app e simulação de banco do app fora
  - Req: RF-39, RNF-06 · Testes: TZ-03 · Depende de: F05-02
  - Aceite: com o banco do app de teste fora, nada se perde e nada fica "agendado/público" sem estado; na volta, grava uma vez só.
  - Portão José: nenhum. Obs: 2026-10-09 (stub em arquivo, sem banco do app real): estado `aguardando_outbox` durante a queda e com `kill -9`; gravou 1 vez na volta. Teste contra o banco do app de teste fica para a F3.
- [x] **F05-04** Ponte Temporal ↔ Paperclip
  - Req: RF-33, RF-43, RNF-06 · Testes: TZ-04 · Depende de: F05-02
  - Aceite: o Temporal abre/atualiza issue; agente de teste devolve proposta Pydantic v2 válida; aprovação vira sinal; o agente nunca lê o Postgres do Temporal; heartbeats desligados.
  - Portão José: autorizar projeto/org de teste no Paperclip.
  - Obs: 2026-10-09 (t334): ponte verificada no Paperclip de teste `PQBR-TESTE` (PQB-4, workflow `tz04-ponte-04`). Inválida rejeitada, válida aplicada (stub) só depois do sinal do José. IDs e limpeza em `docs/sdd/adr-001-orquestrador.md`.
- [ ] **F05-05** Agente Hermes no Paperclip sem `--yolo`; versão do Paperclip
  - Req: RNF-13 · Testes: TZ-05 · Depende de: F05-04
  - Aceite: H-SDD1 resolvida (ou alternativa documentada que respeite o perfil `pqbr`); H-ORQ3 conferida.
  - Portão José: decidir a alternativa se não houver caminho sem `--yolo`. Obs: 2026-10-09: BLOQUEADO e pendente. `hermes_local` 2026.1001.0 força `--yolo` sem opção; nenhum agente Hermes criado nem executado. José (t334): não mexer no código do Paperclip; o adaptador fica como está.
- [ ] **F05-06** Aprovação pelo Telegram (Hermes `pqbr`) como sinal
  - Req: RF-34 · Testes: TZ-06 · Depende de: F05-04
  - Aceite: aprovar/negar funciona; outro ID é ignorado.
  - Portão José: nenhum. Obs: Lado do motor ok (remetente diferente do José ignorado). Falta a ponte do Telegram.
- [x] **F05-07** Relatório do teste e escolha do motor
  - Req: RNF-01, RNF-05, RNF-09 · Testes: TZ-07 · Depende de: F05-01..F05-06
  - Aceite: `docs/sdd/adr-001-orquestrador.md`; ARQUITETURA atualizada. Se o Temporal reprovar, repetir F05-01..F05-04 com o DBOS.
  - Portão José: **G0.5** (motor; dois bancos; outbox; ponte com o Paperclip). Obs: 2026-10-10 (t374): Soak encerrado em 10/10 11:57 (t374, sem esperar as 24 h): **122 execuções em ~20 h** (a cada 10 min), 0 falhas ou expiradas, 0 perdidas (`MissedCatchupWindow` 0), 0 duplicatas no outbox; pico do compose 340 MiB, worker 53 MiB, nenhuma amostra acima de 1536 MiB. **Motor = Temporal**; o DBOS não é necessário. Schedule `pqbr-soak-24h` pausado e timer `pqbr-temporal-ram` desligado (logs mantidos em `runtime/tz/`); stack do Temporal e worker seguem rodando. TZ-05 (`--yolo`) e TZ-06 (Telegram) continuam pendentes fora do motor.

## Fase 0: revisão da especificação (paralela à 0.5)

- [ ] **F00-01** Revisar SPEC, TESTES e RASTREABILIDADE com o José
  - Req: todos · Testes: — · Depende de: R-005
  - Aceite: toda seção do REGRAS coberta por RF/RNF; matriz sem lacunas não marcadas.
  - Portão José: **G0**. Obs:

## Fase 1: org PQBR no Paperclip (agentes pausados)

- [ ] **F1-01** Pacote `company/` (agentcompanies/v1)
  - Req: RF-33, RNF-12 · Testes: TS-09 · Depende de: F05-07, F00-01
  - Aceite: `COMPANY.md`, `agents/<slug>/AGENTS.md` (director, analista, comunidade, compliance, assistente, dev), `.paperclip.yaml` sem segredos; validador e scanner passam; personas de compliance e assistente sérias e diretas.
  - Portão José: **G1**. Obs: 2026-10-10 (t376): pacote pronto em `company/` (COMPANY.md, 6 AGENTS.md, `.paperclip.yaml` com adaptador `process` stub, heartbeat desligado, orçamento 0); scanner limpo; dry-run sem avisos nem erros. **Aguarda o G1 do José** (revisar o pacote).
- [ ] **F1-02** Import dry-run e criação da org pausada
  - Req: RF-43, RNF-13 · Testes: TS-13 · Depende de: F1-01
  - Aceite: dry-run limpo (H-SDD2); agentes pausados, heartbeats desligados.
  - Portão José: autorizar o import; liberar agente é decisão separada. Obs: 2026-10-10 (t376): **só o dry-run**, limpo (`docs/sdd/f1-02-dryrun.md`); nenhuma org criada. O pacote não carrega `paused`: pausar todos logo após o import. Criação real aguarda o José.
- [ ] **F1-03** (D2) Ajuste do perfil Hermes `pqbr`
  - Req: RF-34, RNF-13 · Testes: TZ-06 · Depende de: F05-05
  - Aceite: env mínimo, toolsets restritos, budgets; segredos só no `.env`.
  - Portão José: revisar o perfil. Obs:
  - Obs: 2026-10-09 (t363): `pqbr` conectado ao Paperclip na PQBR-TESTE por chave de agente escopada (agente `pqbr-assistente`, wrapper com allowlist, skill `paperclip-pqbr`); listar ok, outra empresa recusada, comentário de teste na PQB-4 criado (`4ad87746…`) só com run de heartbeat. **Pendências:** (1) restringir os toolsets do perfil (no teste ele saiu do wrapper e expôs o `DATABASE_URL` do Paperclip ao modelo, ARQUITETURA §10); (2) heartbeat+run dentro do wrapper para escrever; (3) reapontar para a org real na F1-02.
  - Obs: 2026-10-09 (t372): toolsets restritos (sem terminal, arquivos, código, web, navegador, delegação, cron) em `cli` e `telegram`; Paperclip só pelo MCP `paperclip-pqbr` (heartbeat embutido). Teste oneshot: listar ok; comentário na PQB-4 ok (`4488f764…`); pedido de `env`/`/proc/self/environ` recusado (só ferramentas MCP foram chamadas). Sem gateway do `pqbr` rodando, então nada foi recarregado. Mensagem com o `DATABASE_URL` (senha mascarada) apagada do `state.db` e `invoke_run.js` removido. Pendente: reapontar para a org real (F1-02); leitura de `docs/` por MCP se o José quiser.
- [ ] **AÇÃO MANUAL PENDENTE — José (t373):** trocar a senha do banco do Paperclip no Supabase; depois atualizar o `DATABASE_URL` em `~/.config/core-engineering/supabase.env` (EnvironmentFile do `paperclipai.service`) e reiniciar **só** o Paperclip. Passos preparados (não executados): (1) `cp -p ~/.config/core-engineering/supabase.env ~/Backups/paperclip/supabase.env.$(date +%F)` e `chmod 600`; (2) editar só a senha no `DATABASE_URL` (sem imprimir); (3) `systemctl --user restart paperclipai.service`; (4) conferir `paperclipai health`, o painel e `issue list` da PQBR-TESTE; rollback: restaurar o arquivo e reiniciar o serviço. Obs: até lá, a senha atual continua válida (não foi exposta, t372).
- [ ] **F1-04** Fluxo de tickets de manutenção agnósticos
  - Req: RF-35 · Testes: TS-09 · Depende de: F1-02, F3-02
  - Aceite: ticket pré-estruturado (localização, falha, correções); aprovação 1 (abertura, com pedido de correção) e 2 (merge); memórias de código no bank Hindsight único, sem segredos.
  - Portão José: aprovar o fluxo. Obs:

## Fase 3: fundações

- [ ] **F3-01** (D3) Contratos Pydantic v2 e migração base
  - Req: RF-02, RF-07, RNF-02 · Testes: TS-01, TS-02 · Depende de: F05-07
  - Aceite: modelos da ARQUITETURA §11; `db/migrations/0001_base.sql` (ARQUITETURA §8); carga de `temas-publicados.csv`; testes de contrato passam.
  - Portão José: **G3**. Obs: 2026-10-09 (t336–t346): Banco do app = **Postgres 17 local** (`infra/pqbr-db`, 127.0.0.1:55433, 320 MB), esquema `pqbr` com migrações 0001–0009 **aplicadas** (24 tabelas, 60 temas; só YouTube no catálogo). RLS ligado e forçado; papéis `pqbr_app` (escritor do Temporal) e `pqbr_leitura`; verificação pelo host ok. Backup diário 03:30 com rotação 7 (`~/Backups/pqbr-db`), restauração testada. Upload ao Drive pendente (sem credencial no servidor). Faltam os contratos Pydantic da §11 e ligar o worker ao banco. 2026-10-10 (t376): contratos da §11 em `src/pqbr/contratos/` (RoteiroShort com CTA, sem nomes, sem pedir comentário e 15–180 s a 2,3 palavras/s; DecisaoRepeticao; PontuacaoPolemica; VereditoAuditor; DecisaoPublicacao; ClassificacaoComentario; SinalItem5; PropostaAgente; TicketManutencao; DeterminacaoRevisao; Triagem/Resultado da correção; RegistroConsumo; GradeDiaria), `extra=forbid`; `tests/unit/test_contratos.py` 10/10. A migração base e a carga já estavam feitas. Falta só o G3 do José.

- [ ] **F3-02** (D14) Verificador de segredos/PII
  - Req: RNF-03 · Testes: TS-SEC · Depende de: —
  - Aceite: bloqueia segredo de teste antes de Hindsight, tickets, banco do app, logs e commit.
  - Portão José: nenhum. Obs: 2026-10-09 (t336): `src/pqbr/seguranca/segredos.py` + `scripts/seguranca/verificar_segredos.py` + hook `.githooks/pre-commit` instalado (`core.hooksPath`); repositório inteiro limpo; commit com segredo falso bloqueado. Falta ligar Hindsight/tickets/banco do app/logs (quando existirem).
- [x] **F3-03** Backup do Hindsight (inexistente hoje), alinhado ao backup das 03:30
  - Req: RNF-03 · Testes: TS-DB (restauração) · Depende de: —
  - Aceite: `pg_dump -Fc` do banco `hindsight` do pg0 (sem parar nem reiniciar o Hindsight), timer de usuário às 03:30, rotação de 7 em `~/Backups/hindsight`, restauração testada em banco descartável, credencial lida só na hora do dump e nunca no git. Criar o bank único da organização PQBR quando a F1 pedir.
  - Portão José: nenhum (só leitura do Hindsight). Obs: 2026-10-09: verificado que não há backup (t349–t350). 2026-10-09 (t351): feito. `infra/hindsight-backup/backup.sh` (pg_dump -Fc com o binário do próprio pg0 18.1; senha lida do `instance.json` na hora, sem imprimir); timer `hindsight-backup.timer` às 03:45 (+até 5 min; app às 03:30); 7 dumps em `~/Backups/hindsight` (chmod 600). 1º dump 420 KB; restauração em container `pgvector/pgvector:pg18` sem rede com contagens iguais (25 tabelas, 1 bank, 46/7/84) e container apagado; Hindsight não parou (`/health` ok).
- [ ] **F3-04** Backup fora do servidor no Drive via rclone no `pc`
  - Req: RNF-03 · Testes: restauração a partir do Drive · Depende de: F3-03
  - Aceite: rclone instalado em escopo de usuário; remote do Google Drive com escopo mínimo, autorizado uma vez pelo José; destino `PQBR/backups-db`; envio diário dos dumps do banco do app e do Hindsight depois das 03:30; retenção no Drive definida; nenhum token no git.
  - Portão José: **login Google único** e escolha da retenção. Obs: PENDENTE José (t349–t350).

- [ ] **F3-05** `CorrecaoAutonomaWorkflow` (t355) — filho chamado na falha corrigível, por fila de ferramenta e concorrência 1 por sessão; limites (t357: 3 tentativas; 5–15 min sorteados no Camofox; conferir conta e sessão antes de agir; agente rodando no Paperclip); resultados `Corrigido`/`Esgotado`/`Sensivel`; travas duras em código (lista do REGRAS §3.1); triagem e verificação pelo Jev, intervenção por agente com LLM, aprendizado no Hindsight da PQBR (t356); registro em `pqbr.acoes`; proposta de ajuste do script como tarefa ou ticket · Req: RF-44, RF-46 · Testes: TS-11 · Depende de: F3-01 · Aceite: TS-11 verde · Portão: G4 · Obs: casos a–h resolvidos em t357. Obs: 2026-10-10 (t376): `src/pqbr/workflows/correcao.py` — triagem (trava dura de passos sensíveis antes do Jev) → até 3 tentativas do agente (5–15 min sorteados no Camofox; conta divergente = `sensivel`) → verificação → registro (com barreira). Backends reais do Jev e do agente no Paperclip **EM CONSTRUÇÃO**: sem simulação a Activity falha sem repetir. TS-11: 6/6 no ambiente de teste do Temporal. Registrado no worker.

- [x] **F3-06** Consumo por modelo (t357 h) — migração `0010_pqbr_consumo_modelos.sql` + view `consumo_diario`; toda Activity que chama modelo grava uma linha; seção "Consumo" do relatório diário por template (por modelo, por tipo de ação, falhas, custo estimado, variação vs. 7 dias) · Req: RF-47 · Testes: TS-DB, TS-08 · Aceite: migração testada e aplicada; relatório mostra os números sem teto · Portão: nenhum (sem teto, só monitoramento) · Obs: Obs: 2026-10-10 (t376): Activity `registrar_consumo` (pqbr_app, com barreira) e `secao_consumo()` do relatório diário (por modelo, por tipo, falhas, custo, variação vs. 7 dias); testado; 1 linha de verificação (`modelo=verificacao-t376`) gravada no banco real. Falta ligar cada Activity que chama modelo quando os backends existirem.
- [x] **F3-07** Retenção do consumo por modelo (t358) — migração (resumo diário + papel `pqbr_manutencao`, com rollback), `RetencaoConsumoWorkflow` num Schedule do Temporal, agrega → confere → apaga em lotes, idempotente e registrado · Req: RF-49 · Testes: TS-12 · Depende de: F3-06 · Aceite: TS-12 verde · Portão: G4 (prazos definidos) · Obs: t369: brutos 90 dias, resumo 25 meses, Schedule ~04:15; desbloqueado, ainda não executado. (D1) — runbook, cada passo com portão G4 Obs: 2026-10-10 (t376): migração `0011` (resumo diário, função `pqbr.reter_consumo`, papel `pqbr_manutencao` com rollback) testada em banco descartável (agrega 2/3/1/15, apaga 3 brutas, 2ª execução não muda nada, `pqbr_app` não executa) e **aplicada** no banco local; `RetencaoConsumoWorkflow` + Schedule `pqbr-retencao-consumo` **ativo** às 04:15 (Fortaleza); execução manual real ok (nada a apagar ainda). senhas do worker em `~/.pqbr/worker.env` (600), worker da PQBR reiniciado (só ele).

Estado em 09/10 (lido só leitura): pipx global `notebooklm-py` 0.8.2 (Python 3.13, sem extras) em `~/.local/bin/notebooklm`; `~/.notebooklm` (332 KB, perfil `default`) é a **sessão pessoal do José** (confirmado em t355): fica intacta e **fora da migração**, inclusive o cron `*/15 … notebooklm auth refresh -q` (linha 1 do crontab) que **já está falhando** ("CSRF token not found"). O MP32 usa `NOTEBOOKLM_HOME=/home/pc/.mp32/notebooklm` (perfis `tutibom10`, `juniormoedavirtual`), cron `*/20` `mp32/scripts/notebooklm-keepalive.sh` e **o mesmo binário global** (`NB=/home/pc/.local/bin/notebooklm`; `ops/notebooklm.py` cai nele via `shutil.which`). Por isso o MP32 precisa ganhar a própria 0.8.2 **antes** de remover o pipx. Existe `~/.pqbr`? Não. PyPI: 0.8.4 é a última, Python ≥3.10. Regras: §10 das REGRAS. Variáveis: `V=/home/pc/.pqbr/venvs/notebooklm-0.8.4`, `H=/home/pc/.pqbr/notebooklm`, `B=~/Backups/notebooklm-migracao`.

- [x] **F4-00** Retrato e backups (nada muda) — Comando: `mkdir -p $B && crontab -l > $B/crontab-$(date +%F).txt && tar czf $B/dot-notebooklm-$(date +%F).tgz -C ~ .notebooklm && tar czf $B/mp32-notebooklm-$(date +%F).tgz -C ~/.mp32 notebooklm && chmod -R go-rwx $B && pipx list > $B/pipx.txt` · Aceite: 4 arquivos em `$B`, `chmod 600` · Portão: nenhum (só leitura/cópia) · Rollback: `rm -rf $B` · Obs: 2026-10-09 (t354): feito. 4 arquivos em `~/Backups/notebooklm-migracao` (crontab, tgz de `~/.notebooklm` e de `~/.mp32/notebooklm`, `pipx list`), pasta 700 e arquivos 600; cookies não lidos.
- [x] **F4-01** venv da PQBR com 0.8.4 fixada — Req: RF-10 · Comando: `uv venv --python 3.13 $V && uv pip install --python $V/bin/python 'notebooklm-py==0.8.4'` (extras só se o login pedir) · Aceite: `$V/bin/notebooklm --version` = 0.8.4; `~/.local/bin/notebooklm --version` continua 0.8.2 · Portão: G4 (instalar) · Rollback: `rm -rf $V` · Obs: 2026-10-09 (t354): feito. `/home/pc/.pqbr/venvs/notebooklm-0.8.4` (uv, Python 3.13): `--version` = 0.8.4 (bff7c66e); global continua 0.8.2.
- [ ] **F4-02** MP32 com a própria 0.8.2 (antes de qualquer remoção) — Comando: `uv venv --python 3.13 ~/.mp32/venvs/notebooklm-0.8.2 && uv pip install --python ~/.mp32/venvs/notebooklm-0.8.2/bin/python 'notebooklm-py==0.8.2'`; trocar `NB=` no `notebooklm-keepalive.sh` e pôr `~/.mp32/venvs/notebooklm-0.8.2/bin` no PATH de `activate-mp32-env.sh`/units `mp32-worker`; **mudança no repositório MP32** · Aceite: keepalive registra `ok` para `tutibom10`; `preflight-notebooklm.sh` passa; `mp32-worker` roda um estágio NotebookLM · Portão: **G4 + José (mexe no MP32; reinício do `mp32-worker` precisa de OK)** · Rollback: voltar `NB=`/PATH para `~/.local/bin/notebooklm` (o binário global continua lá) · Obs:
- [x] **F4-03** Ambiente PQBR isolado — Comando: `mkdir -m 700 -p $H` e wrapper `~/.pqbr/bin/pqbr-notebooklm` com `export NOTEBOOKLM_HOME=$H; exec $V/bin/notebooklm -p pqbr "$@"`; skills do `rede` passam a chamar só o wrapper (sem cópia de cookies) · Aceite: `pqbr-notebooklm auth check` falha "sem sessão" sem tocar `~/.notebooklm` · Portão: G4 · Rollback: `rm -rf ~/.pqbr/bin $H` · Obs: 2026-10-09 (t354): feito. Wrapper `~/.pqbr/bin/pqbr-notebooklm` (700) imprime 0.8.4; `auth check` sem sessão, como esperado; `~/.pqbr/notebooklm` (700) só com `profiles/` vazio e `.migration.lock`. Skills do `rede` ainda não apontam para ele (vai junto do F4-05).
- [ ] **F4-04** Deslogar a sessão antiga (t191; conta = conta de produção, t352) — Verificado em 09/10 (t353): o MP32 tem uma cópia antiga dessa conta em `~/.mp32/notebooklm/profiles/<conta de produção>` (de 27/09), que a documentação do MP32 dá como obsoleta e proibida (o preflight bloqueia). O keepalive só usa `tutibom10`. O logout pode invalidar essa cópia, mas o MP32 não usa; `tutibom10` é outra conta e não é afetada. Antes do logout, confirmar de novo com `rg -n` que nada do MP32 passou a usar o perfil. — **Não toca em `~/.notebooklm` nem na linha 1 do crontab (sessão pessoal, t355).** Onde está a sessão antiga do Porquê BR usada pelo `rede` (pasta e cron): EM CONSTRUÇÃO, conferir só leitura antes deste passo — Comando: pausar o agente `rede` e o refresh dessa sessão; José sai da sessão antiga em myaccount.google.com → Segurança → Seus dispositivos (conta do Porquê BR) · Aceite: nada da PQBR/`rede` usa a sessão antiga; `~/.notebooklm` e a linha 1 do crontab inalterados; conta com um dispositivo a menos · Portão: **José (logout na conta Google + autoriza interromper a produção atual)** · Rollback: restaurar `$B/crontab-*.txt` e despausar o `rede` (a sessão antiga só volta com relogin) · Obs:
- [ ] **F4-05** Login novo no perfil `pqbr` (na conta de produção, t352) — Comando: `pqbr-notebooklm login` (abre navegador; feito pelo José no desktop remoto/noVNC do `pc`, ou `login --browser-cookies chrome --account <conta PQBR>` se a conta estiver logada no Chrome do `pc`) · Aceite: `pqbr-notebooklm auth check --test` ok; `storage_state.json` em `$H/profiles/pqbr` `chmod 600`; um só dispositivo · Portão: **José (login Google único, 2FA)** · Rollback: `rm -rf $H/profiles/pqbr`, voltar ao F4-04 rollback · Obs:
- [ ] **F4-06** Caderno clonado e smoke test — José indica o caderno raiz; o agente cria um caderno **cópia** (fontes reimportadas) e grava o id como `NOTEBOOKLM_NOTEBOOK_ID_TESTE`; nunca produz no raiz · Comando: `pqbr-notebooklm list --json`, `pqbr-notebooklm usage --json`, gerar um artefato pequeno só no clone · Aceite: TS-02 verde; raiz sem alteração (contagem de fontes/artefatos igual antes/depois) · Portão: **José (escolher o raiz e o nome do clone)** · Rollback: apagar o caderno clone · Obs: clonagem nativa pela CLI EM CONSTRUÇÃO (sem confirmação; plano B = criar caderno e reimportar fontes)
- [ ] **F4-07** Serviço único dono da sessão — unit de usuário `pqbr-notebooklm-refresh.timer` (refresh a cada 15 min só do perfil `pqbr`) + Activity Temporal na fila `notebooklm` com concorrência 1; `usage --json` gravado em `pqbr.consumo` · Req: RF-10, RF-32 · Testes: TS-02, V7 · Aceite: 24 h sem queda; consumo gravado (H6); nenhum outro processo chama o perfil `pqbr` · Portão: G4 · Rollback: `systemctl --user disable --now pqbr-notebooklm-refresh.timer`, remover a fila do worker · Obs:
- [ ] **F4-08** Remover o pipx global (por último) — **EM CONSTRUÇÃO — aguardando José (t355):** a sessão pessoal (`~/.notebooklm` e o cron da linha 1) usa o binário global; remover o pipx quebra esse refresh. Opções: manter o pipx global só para o uso pessoal, ou dar ao uso pessoal uma venv própria e trocar o caminho no cron (isso mexe no crontab e precisa do José). Pré: F4-02 aceito · Portão: **José** · Rollback: `pipx install 'notebooklm-py==0.8.2'` · Obs:
- [x] **F4-09** ~~Limpeza de `~/.notebooklm` após 7 dias~~ — **CANCELADO (t355):** é a sessão pessoal do José e fica intacta. Obs: 2026-10-09: o tgz de F4-00 continua em `~/Backups/notebooklm-migracao` só como cópia.

Precisam do José: F4-02 (mexer/reiniciar MP32), F4-04 (logout Google + interromper produção), F4-05 (login novo), F4-06 (escolher caderno raiz), F4-08 (pipx × sessão pessoal). F4-09 cancelado (t355). Os demais só pedem o portão G4.

## Fase 4C: isolamento do Camofox da PQBR (t354) — cada passo com portão G4

Estado em 09/10 (lido só leitura):
- Um único servidor compartilhado: serviço de usuário `camofox-browser` (`~/camofox-browser`, v1.6.0, commit 2c0036a de 10/09, `node server.js`, Restart=on-failure, ~116 MB RSS). Sem `Environment` na unit, então tudo está no padrão.
- **Porta 9377 escutando em todas as interfaces (`*:9377`), inclusive LAN e tailnet, sem chave de API** (`CAMOFOX_API_KEY`/`CAMOFOX_ACCESS_KEY` não definidas). noVNC desligado.
- Perfis em `~/.camofox/profiles/<sha256(userId)[:32]>` (291 MB, 14 pastas), todos no mesmo processo e no mesmo `~/.camofox`. Identificados pelo hash, sem abrir cookies: `porquebr` (PQBR/`rede`, usado hoje), `tutibom10` e a conta do MP32 por e-mail (MP32/Gemini/Flow/Studio), `mp3_isolated_worker` (Hermes `mp3`), a conta pessoal do José (`~/Workspace/runway_keepalive.py`, usado hoje). Outras 9 pastas sem dono identificado (por exemplo `me`, das skills `pet`/`gpu`).
- Clientes: `rede` (skills do Porquê BR), MP32 (`src/mp32/web/camofox.py`), Hermes `mp3`, `pet` e `gpu`, `runway_keepalive.py`.
- Controle de concorrência: só os limites padrão do servidor (`MAX_SESSIONS`, `MAX_CONCURRENT_PER_USER`, `MAX_TABS_*` não ajustados). Não existe trava entre projetos. Uma queda ou reinício por memória (`BROWSER_RSS_RESTART_THRESHOLD_MB`) derruba todos ao mesmo tempo.

Conflitos: (1) reinício, atualização ou travamento do servidor de outro projeto derruba o Studio da PQBR; (2) dois clientes podem usar o mesmo `userId` ao mesmo tempo (nada impede que outro projeto use `porquebr`); (3) a exposição em LAN/tailnet sem chave deixa qualquer cliente da rede abrir a sessão do Studio; (4) a atualização do código é única para todos.

Plano. Variáveis: `C=/home/pc/.pqbr/camofox`, porta `9387`, unit `pqbr-camofox.service`.
- [x] **F4C-01** Checkout próprio fixado — Comando: `git clone ~/camofox-browser $C/app && git -C $C/app checkout 2c0036a && (cd $C/app && npm ci --omit=dev)`, com Camoufox próprio via `CAMOFOX_EXECUTABLE_PATH` se o download não for compartilhável · Aceite: `node $C/app/server.js --help` roda; nada muda em `~/camofox-browser` · Portão: G4 · Rollback: `rm -rf $C/app` · Obs: 2026-10-10 (t375): feito. `/home/pc/.pqbr/camofox/app` no commit 2c0036a (`npm ci --omit=dev`); Camoufox próprio em `/home/pc/.pqbr/camofox/cache/camoufox` (1,3 GB, `CAMOUFOX_EXECUTABLE_PATH`; conferido que os processos usam essa cópia).
- [x] **F4C-02** Serviço próprio, só localhost, com chave — `.env` 600 em `$C` com `CAMOFOX_PORT=9387`, `CAMOFOX_BIND_HOST=127.0.0.1`, `CAMOFOX_PROFILE_DIR=$C/profiles`, `CAMOFOX_COOKIES_DIR`/`UPLOADS_DIR`/`TRACES_DIR` em `$C`, `CAMOFOX_API_KEY` gerada, `MAX_SESSIONS=1`, `MAX_CONCURRENT_PER_USER=1`, `CAMOFOX_CRASH_REPORT_ENABLED=false`; unit `pqbr-camofox.service` com `MemoryMax=900M` · Aceite: `ss -ltn` mostra só `127.0.0.1:9387`; `/health` ok; sem a chave dá 401; `:9377` intacto · Portão: G4 · Rollback: `systemctl --user disable --now pqbr-camofox` e remover a unit · Obs: 2026-10-10 (t375): feito. `pqbr-camofox.service` ativo, escuta só em `127.0.0.1:9387`; `/health` ok; sem chave ou com chave errada = 401, com chave = 200; `.env` 600 com chaves de API, acesso e admin, `NODE_ENV=production`, pastas próprias, `MAX_SESSIONS=1`, VNC desligado; MemoryMax 900M (≈350 MB em uso). O 9377 compartilhado não foi tocado (mesmo PID 1334). Arquivos: `infra/pqbr-camofox/`.
- [x] **F4C-03** Fila `camofox-pqbr` no Temporal, concorrência 1 por sessão — o worker usa `max_concurrent_activities=1` por fila e por perfil; só as Activities chamam a porta 9387 (scripts e a Activity de agente do F4C-08); ninguém fala direto com o Camofox · Testes: TS-02, V7 · Aceite: duas tarefas simultâneas executam em série (log) · Portão: G4 · Rollback: voltar para a fila `camofox` antiga · Obs: 2026-10-10 (t375): feito. `src/pqbr/workflows/camofox.py` (Activity `camofox_saude` com health e chamada autenticada, stub `camofox_acao_stub`, `CamofoxSaudeWorkflow`) e worker próprio `pqbr-camofox-worker.service` na fila `camofox-pqbr` com `max_concurrent_activities=1` (o worker principal não foi reiniciado). `scripts/camofox/verificar.sh`: saudável, autenticado, 2 execuções em série.
- [ ] **F4C-04** Login novo do Studio/Gemini no perfil `pqbr` (conta de produção) pelo noVNC próprio (`ENABLE_VNC` só durante o login, preso a 127.0.0.1 com senha e acesso por túnel) · Aceite: Studio, Gemini Web e NotebookLM respondem no guardião; um dispositivo novo na conta · Portão: **José (login Google/2FA; autorizar a parada curta do Studio no `rede`)** · Rollback: o perfil `porquebr` no 9377 continua lá até o F4C-06 · Obs: mover (não copiar) o `porquebr` antigo só com OK do José; cópia de cookies segue proibida (REGRAS §11)
- [ ] **F4C-05** Trocar os clientes da PQBR — skills do `rede` e o guardião (§11) apontam para a Activity, não para `:9377`; o `rede` deixa de usar `porquebr` · Aceite: `grep -rn 9377` nas skills do `rede` só em histórico; 3 dias de sombra sem queda (H16) · Portão: **José (mudar o `rede` em produção)** · Rollback: reverter as skills (backup da pasta antes) · Obs:
- [ ] **F4C-06** Desligar o perfil `porquebr` antigo — sair da sessão antiga no Google (dispositivos) e arquivar a pasta `ffa8f2ea…` em `~/Backups` (tgz 600) por 7 dias · Aceite: nenhum cliente usa `porquebr` no 9377 · Portão: **José (logout na conta + apagar depois de 7 dias)** · Rollback: restaurar o tgz · Obs:
- [ ] **F4C-07** (Fora da PQBR, só recomendação) Fechar o 9377 compartilhado: `CAMOFOX_BIND_HOST=127.0.0.1` + chave de API, o que exige reiniciar o `camofox-browser` e afeta MP32, `mp3`, `pet`, `gpu` e o runway · Portão: **José (outros projetos e reinício)** · Rollback: tirar o env e reiniciar · Obs:

- [ ] **F4C-08** Activity de agente no Camofox (t355) — ferramenta Camofox para o agente com allowlist (navegar, ler, clicar, digitar, colar, upload), só em `127.0.0.1:9387` com a chave, sem login, cookies ou exclusão; cada ação registrada · Req: RF-45 · Testes: TS-11 · Depende de: F4C-03, F3-05 · Aceite: seletor quebrado de propósito numa página de teste é corrigido pelo agente e vira proposta de script · Portão: G4 · Rollback: desligar a Activity (só scripts) · Obs:

Precisam do José: F4C-04, F4C-05, F4C-06, F4C-07. F4C-01..03 só pedem o portão G4.

## Fase 5: estabilidade e produção (D5)

- [x] **F5-01** Grade, coleta, 3 barreiras, R10, polêmica — Req: RF-01..RF-05 · Testes: TS-01, V4 · Depende de: F3-01 · Aceite: teste do incidente de 08/10 passa · Portão: nenhum · Obs: Obs: 2026-10-10 (t376): `src/pqbr/pipeline/grade.py` — 3 barreiras (exata, variação por núcleo de palavras, índice do banco), R10 também para sugestão do José, bloqueio absoluto por categoria, polêmica por componentes (pesos e limiar **PROPOSTA**, recalibrar), mistura configurável (`fracao_perene`, t378). Teste do incidente de 08/10 passa; no histórico só os 2 repetidos legados são pegos. 7/7. **Depende de t378 (escopo editorial, EM CONSTRUÇÃO — discutir com José).**
- [ ] **F5-02** `EpisodioWorkflow` real + Schedules (janelas 11:40, 14:40, 18:35, 21:15) + vigia de prazo — Req: RF-06, RF-17, RNF-10 · Testes: TS-02, TS-04 · Depende de: F5-01, F4-03 · Aceite: ciclo completo em paralelo · Portão: **G5** · Obs: Obs: 2026-10-10 (t376): **só código e testes**: `src/pqbr/workflows/producao.py` (GradeDiaria, EpisodioProducao com vigia de prazo: sem reserva cancela, com reserva usa; reprovado nunca publica; polêmica > 75 espera o José). NotebookLM/auditor/publicação reais desligados (falham sem simulação). Schedules `pqbr-grade-diaria` 01:00 e `pqbr-lote-producao` 05:00 criados **PAUSADOS** (horários PROPOSTA). 6/6. Liberar = **G5**.
- [ ] **F5-03** Dias em paralelo sem falha; corte do fluxo antigo; **pausa do perfil `rede`** — Req: RF-01, RNF-05 · Testes: TS-REPLAY · Depende de: F5-02, F5-04, F5-05 · Aceite: N dias sem falha · Portão: **G5b** · Obs:
- [ ] **F5-04** Fichas: resolvedor sem LLM, criação sob demanda, verificação Telegram/painel, proveniência — Req: RF-08, RNF-08 · Testes: TS-02, V2, V6 · Depende de: F3-01 · Aceite: ficha nova sem bloqueio; "Não Aprovado" abre ticket · Portão: nenhum · Obs:
- [ ] **F5-05** Render e pós FFmpeg — Req: RF-09 · Testes: TS-02 · Depende de: F4-03 · Aceite: end card cortado só se detectado; logo com zoom · Portão: nenhum · Obs:

## Fase 6: resiliência (D6)

- [ ] **F6-01** Guardião de sessão (escada t272), teste de resposta, escada de falhas, NETWORK_WAITING, outbox, fallback do Jev, fila Camofox — Req: RF-37..RF-39, RNF-02, RNF-04 · Testes: TS-10 · Depende de: F5-02 · Aceite: simulação de cada degrau; nenhuma cópia de cookies sem OK · Portão: **G6** · Obs:

## Fase 7: editorial e auditor

- [ ] **F7-00** (t378) Reformular o escopo editorial — **EM CONSTRUÇÃO — discutir com José** na próxima fase de conteúdo; regras atuais **não** mudam ainda. Proposta: ≥ 80% de "curiosidades inúteis que prendem a atenção" (ex.: origem de expressões antigas do dia a dia ainda em uso; "por que dizemos podre de rico" foi bem); menos pesquisa de assuntos em alta; tendências só para contextualizar datas sazonais (Natal, Carnaval, festas brasileiras). Afeta F5-01 (mistura e barreiras; o código já aceita a fração configurável) e F7-01 · Portão: José.

- [ ] **F7-01** (D11) Contrato v2 sem superados; decidir R1–R6, R8, R9; RUNBOOK; SOP — Req: RF-07 · Testes: V1 · Depende de: R-005 · Aceite: aprovado pelo José · Portão: **G7** · Obs: R1–R9 EM CONSTRUÇÃO — aguardando José.
- [ ] **F7-02** (D4) Auditor (Gemini web via Camofox, Jev no texto, código decide; imagem×fala não reprova) — Req: RF-11..RF-14 · Testes: TS-03, V3 · Depende de: F3-01, F7-01 · Aceite: falso aprovado/reprovado medidos · Portão: G7 · Obs:

## Fase 8: publicação, armazenamento e revisão humana

- [ ] **F8-01** (D7) `PublicacaoWorkflow` + `Item5Workflow` — Req: RF-15..RF-21 · Testes: TS-04, TS-05, V4, V5 · Depende de: F6-01, F7-02 · Aceite: sem duplicata; 1 agendamento por via; item 5 em vídeo privado · Portão: **G8** · Obs:
- [ ] **F8-02** (D13) Drive t267, upload com hash, limpeza noturna — Req: RF-40, RF-41 · Testes: TS-11, V6 · Depende de: F5-02 · Aceite: duplicata movida, nada excluído · Portão: G8 · Obs:
- [ ] **F8-03** Revisão humana como último recurso — Req: RF-36 · Testes: TS-09 · Depende de: F8-01 · Aceite: item vai ao local de revisão, José avisado, determinação registrada · Portão: aprovar o local · Obs: [PROPOSTA] Banco do app + `04_Privados_Revisao`.

## Fase 9: monitores, compliance e analista

- [ ] **F9-01** (D12) Monitor de atualizações, consumo, levantamento de custos, relatório diário — Req: RF-31, RF-32, RF-42, RNF-07 · Testes: TS-08, TS-12 · Depende de: F8-01 · Aceite: relatório no Telegram por vários dias · Portão: **G9** · Obs:
- [ ] **F9-02** @prod-compliance (coleta, gravidade, HOLD, rascunho de recurso) — Req: RF-28, RF-29 · Testes: TS-07 · Depende de: F8-01, F1-02 · Aceite: simulação de crítico gera HOLD · Portão: G9 · Obs:
- [ ] **F9-03** @prod-analista (Analytics API diária, propostas Pydantic v2) — Req: RF-30, RF-33 · Testes: TS-08 · Depende de: F1-02, F3-01 · Aceite: coleta diária gravada; H14 · Portão: G9 · Obs:

## Fase 10: comunidade

- [ ] **F10-01** (D9) Banco de 60 frases — Req: RF-24 · Testes: TS-06 · Depende de: F7-01 · Aceite: aprovado · Portão: **G10** · Obs:
- [ ] **F10-02** (D10) Registrar no DECISOES-LOG o item 5 e as respostas como instrução expressa do dono — Req: RF-19, RF-24 · Depende de: F10-01 · Aceite: entrada registrada · Portão: aprovar o texto · Obs:
- [ ] **F10-03** (D8) @prod-comunidade completo — Req: RF-21..RF-27 · Testes: TS-06 · Depende de: F10-01, F8-01 · Aceite: H3 + sombra de 3 dias ou ~30 respostas · Portão: **G10** · Obs:

## Fase 11: dois personagens (não bloqueia)

- [ ] **F11-01** (D15) Estratégia para 2 personagens — Req: RF-08 · Testes: V2 · Depende de: F4-03, F7-02 · Portão: **G11** · Obs:

## Fase 12: validação final e liberação

- [ ] **F12-01** Evidência V1–V7; metas do piloto; ativar Schedules um a um — Req: todos · Testes: V1–V7 · Depende de: todas · Portão: **G12** · Obs: metas do piloto EM CONSTRUÇÃO — aguardando José (t327).

## Segundo momento (fora do caminho crítico)

- [ ] **L-01** Migrar o banco do Paperclip do Supabase para Postgres local próprio no `pc` (container dedicado, ao lado de app/Temporal/Hindsight) (t367) — Passos: (1) inventariar só leitura onde o `DATABASE_URL` do Paperclip é usado (serviço, `.env`, CLI, backups); (2) `pg_dump` do Supabase (versão do cliente ≥ servidor); (3) container `paperclip-db` em 127.0.0.1 com `mem_limit`, senha só no `.env` 600; (4) restaurar e conferir contagens por tabela contra a origem; (5) trocar o `DATABASE_URL` do Paperclip numa janela curta de manutenção (**reinício do serviço do Paperclip**, não do Hermes) e conferir painel, issues e heartbeats; (6) timer de backup diário com rotação; (7) manter o Supabase como rollback por N dias (N a definir); (8) depois, decidir que a pendência de RLS do Supabase deixou de valer · Aceite: contagens iguais, painel e TZ-04 ok no banco novo, backup e restauração testados · Portão: **José (OK antes de executar; janela de reinício do Paperclip)** · Rollback: voltar o `DATABASE_URL` para o Supabase e reiniciar o serviço do Paperclip · Obs: não executado.

- [ ] **L-01** Rotação de senhas e tokens (`paperclip_app`, root do Contabo, token do OpenCode) — Portão: José · Obs: adiado (t327).
- [ ] **L-02** Estudo de outros canais e cota da API para vários canais — Portão: José · Obs: adiado (t327).
- [ ] **L-03** Excluir `tasks/` se as rotinas ficarem só como Schedules — Depende de: F05-07 · Portão: José · Obs:

---

## Anexo: fases e portões (ex-PLANO.md, incorporado em 11/10, t394)
### PLANO da PQBR (fases, portões e rollback)

> Autoridade: o último da ordem (REGRAS > SPEC > ARQUITETURA > TESTES > ROADMAP > PLANO). **As tarefas, o estado e o próximo passo ficam só em `docs/ROADMAP.md`**; este arquivo resume as fases, os portões do José, o rollback, as pendências e os riscos, sem repetir tarefas.
> Não consultar material restrito (t287).

## 0. Premissas

- Quem constrói: agentes de desenvolvimento, sem core-eng (t284). O José aprova cada portão e cada merge.
- Espinha: **Temporal** (fluxo determinístico; DBOS plano B) ligado ao **Paperclip** (camada de agentes e painel). Os agentes vivem no Paperclip e só propõem (t324–t327). Telegram pelo Hermes `pqbr` (t281).
- Escopo: só o canal Porquê BR (t327).
- Mudanças na construção são tarefas do ROADMAP, nunca tickets. Nada que depende de hipótese é construído antes de ela virar VERIFICADO (item 7).
- Branch por tarefa e merge com aprovação do José; nada de push sem autorização.
- Produto: construção → validação (V1–V7, `docs/TESTES.md` §3) → produção.

## 1. Fases

| Fase | Objetivo | Portão do José | Rollback |
|---|---|---|---|
| 0.5 | Teste de 1 dia do Temporal ligado ao Paperclip (motor, dois bancos, outbox, ponte) | **G0.5** escolhe o motor | `docker compose down -v`; nada de produção tocado |
| 0 | Revisão de SPEC/TESTES/RASTREABILIDADE | **G0** | reverter o commit |
| 1 | Org PQBR no Paperclip, agentes pausados; perfil `pqbr`; fluxo de tickets | **G1** | arquivar a org (exclusão só pelo José); restaurar backup do perfil |
| 3 | Contratos Pydantic v2, migração base, scanner de segredos | **G3** | migrações com `down` |
| 4 | Migração do notebooklm-py (runbook F4-00..F4-09) | **G4** a cada passo; José em F4-02/04/05/06/08/09 | voltar ao pipx 0.8.2 e ao crontab salvo |
| 5 | Grade, barreiras, `EpisodioWorkflow`, Schedules, fichas, render | **G5** (paralelo) e **G5b** (corte do fluxo antigo + pausa do `rede`) | pausar Schedules; fluxo antigo segue até G5b |
| 6 | Resiliência | **G6** | pausar o guardião |
| 7 | Contrato v2 e auditor | **G7** | v1 e auditor v3 como referência |
| 8 | Publicação, item 5, Drive, revisão humana | **G8** | pausar publicação; vídeos de teste privados |
| 9 | Monitores, compliance, analista, relatório | **G9** | pausar rotinas |
| 10 | Comunidade | **G10** | kill switch; retenções reversíveis |
| 11 | Dois personagens (não bloqueia) | **G11** | — |
| 12 | Validação final e liberação | **G12** | pausar Schedules; HOLD da fila |

Ordem: 0.5 ∥ 0 → 1 → 3 ∥ 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12.

## 2. Pendências do José

- **EM CONSTRUÇÃO — aguardando José:** regras de roteiro R1–R6, R8, R9 (contrato v2).
- **EM CONSTRUÇÃO — aguardando José:** metas do piloto (definidas depois, t327).
- Aprovar: banco de 60 frases (F10-01); local da revisão humana (F8-03); texto dos AGENTS.md (G1).
- Segundo momento (t327): rotações de senhas/tokens; outros canais e cota multi-canal.

## 3. Riscos

| Risco | Mitigação |
|---|---|
| `hermes_local` força `--yolo`, mas o perfil `pqbr` não pode herdá-lo | F05-05 antes de ligar agentes Hermes; heartbeats desligados |
| Repetir a deriva da COR-1 | REGRAS como autoridade; SPEC e matriz de rastreabilidade; t287 |
| RAM/swap do servidor com o motor | TZ-01; DBOS como plano B |
| Determinismo e versionamento de workflows | TS-REPLAY; workflows curtos |
| Recovery storm do Paperclip sem internet (#6596) | heartbeats desligados; agentes sem efeito |
| Sessão do NotebookLM com dois donos | logout antes do login novo (t191) |
| Quedas da sessão do Studio (H9) | guardião + escada t272 |
| Auditoria do app do GCP (H1) | privado + Camofox agenda (t273) |
| Cotas da Data API e limites do NotebookLM | monitor de consumo; espaçar acima de 80% |
| Desmonetização por conteúdo inautêntico | compliance + HOLD + variedade; R10 |
| Respostas parecendo robô | banco aprovado, limites, sombra, desligamento em casos graves |
| Segredo vazado | scanner (F3-02) primeiro; pre-commit |
| Banco do app fora | retentativas + outbox (TZ-03) |
| Métricas divergentes | só pela Analytics API (H12); relatórios avisam falta de significância |
| Disco do servidor | ciclo t267/t268; `runtime/` limpo |
