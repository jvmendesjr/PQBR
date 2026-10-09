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

---

## Fase 0.5: teste de 1 dia do Temporal ligado ao Paperclip ← PRIMEIRO PASSO ABERTO

- [ ] **F05-01** Subir o Temporal com Postgres próprio e medir recursos
  - Req: RNF-09 · Testes: TZ-01 · Depende de: R-005
  - Aceite: Temporal em compose isolado, Postgres dedicado (sem Elasticsearch, separado do `mp32-postgres`); RAM/CPU dentro do limite (H-ORQ1); dump e restauração testados (H-ORQ2).
  - Portão José: autorizar a instalação e combinar o limite de RAM (EM CONSTRUÇÃO — aguardando José).
  - Obs:
- [ ] **F05-02** `EpisodioWorkflow` de brinquedo
  - Req: RNF-05 · Testes: TZ-02 · Depende de: F05-01
  - Aceite: timer + Activity que falha e retenta; retoma após `kill -9` no worker e após reboot.
  - Portão José: autorizar o reboot, se for o do servidor.
  - Obs:
- [ ] **F05-03** Outbox para o Supabase e simulação de Supabase fora
  - Req: RF-39, RNF-06 · Testes: TZ-03 · Depende de: F05-02
  - Aceite: com o Supabase de desenvolvimento fora, nada se perde e nada fica "agendado/público" sem estado; na volta, grava uma vez só.
  - Portão José: nenhum. Obs:
- [ ] **F05-04** Ponte Temporal ↔ Paperclip
  - Req: RF-33, RF-43, RNF-06 · Testes: TZ-04 · Depende de: F05-02
  - Aceite: o Temporal abre/atualiza issue; agente de teste devolve proposta Pydantic v2 válida; aprovação vira sinal; o agente nunca lê o Postgres do Temporal; heartbeats desligados.
  - Portão José: autorizar projeto/org de teste no Paperclip.
  - Obs:
- [ ] **F05-05** Agente Hermes no Paperclip sem `--yolo`; versão do Paperclip
  - Req: RNF-13 · Testes: TZ-05 · Depende de: F05-04
  - Aceite: H-SDD1 resolvida (ou alternativa documentada que respeite o perfil `pqbr`); H-ORQ3 conferida.
  - Portão José: decidir a alternativa se não houver caminho sem `--yolo`. Obs:
- [ ] **F05-06** Aprovação pelo Telegram (Hermes `pqbr`) como sinal
  - Req: RF-34 · Testes: TZ-06 · Depende de: F05-04
  - Aceite: aprovar/negar funciona; outro ID é ignorado.
  - Portão José: nenhum. Obs:
- [ ] **F05-07** Relatório do teste e escolha do motor
  - Req: RNF-01, RNF-05, RNF-09 · Testes: TZ-07 · Depende de: F05-01..F05-06
  - Aceite: `docs/sdd/adr-001-orquestrador.md`; ARQUITETURA atualizada. Se o Temporal reprovar, repetir F05-01..F05-04 com o DBOS.
  - Portão José: **G0.5** (motor; dois bancos; outbox; ponte com o Paperclip). Obs:

## Fase 0: revisão da especificação (paralela à 0.5)

- [ ] **F00-01** Revisar SPEC, TESTES e RASTREABILIDADE com o José
  - Req: todos · Testes: — · Depende de: R-005
  - Aceite: toda seção do REGRAS coberta por RF/RNF; matriz sem lacunas não marcadas.
  - Portão José: **G0**. Obs:

## Fase 1: org PQBR no Paperclip (agentes pausados)

- [ ] **F1-01** Pacote `company/` (agentcompanies/v1)
  - Req: RF-33, RNF-12 · Testes: TS-09 · Depende de: F05-07, F00-01
  - Aceite: `COMPANY.md`, `agents/<slug>/AGENTS.md` (director, analista, comunidade, compliance, assistente, dev), `.paperclip.yaml` sem segredos; validador e scanner passam; personas de compliance e assistente sérias e diretas.
  - Portão José: **G1**. Obs:
- [ ] **F1-02** Import dry-run e criação da org pausada
  - Req: RF-43, RNF-13 · Testes: TS-13 · Depende de: F1-01
  - Aceite: dry-run limpo (H-SDD2); agentes pausados, heartbeats desligados.
  - Portão José: autorizar o import; liberar agente é decisão separada. Obs:
- [ ] **F1-03** (D2) Ajuste do perfil Hermes `pqbr`
  - Req: RF-34, RNF-13 · Testes: TZ-06 · Depende de: F05-05
  - Aceite: env mínimo, toolsets restritos, budgets; segredos só no `.env`.
  - Portão José: revisar o perfil. Obs:
- [ ] **F1-04** Fluxo de tickets de manutenção agnósticos
  - Req: RF-35 · Testes: TS-09 · Depende de: F1-02, F3-02
  - Aceite: ticket pré-estruturado (localização, falha, correções); aprovação 1 (abertura, com pedido de correção) e 2 (merge); memórias de código no bank Hindsight único, sem segredos.
  - Portão José: aprovar o fluxo. Obs:

## Fase 3: fundações

- [ ] **F3-01** (D3) Contratos Pydantic v2 e migração base
  - Req: RF-02, RF-07, RNF-02 · Testes: TS-01, TS-02 · Depende de: F05-07
  - Aceite: modelos da ARQUITETURA §11; `db/migrations/0001_base.sql` (ARQUITETURA §8); carga de `temas-publicados.csv`; testes de contrato passam.
  - Portão José: **G3**. Obs:
- [ ] **F3-02** (D14) Verificador de segredos/PII
  - Req: RNF-03 · Testes: TS-SEC · Depende de: —
  - Aceite: bloqueia segredo de teste antes de Hindsight, tickets, Supabase, logs e commit.
  - Portão José: nenhum. Obs:

## Fase 4: migração do notebooklm-py (D1) — cada passo com portão G4

- [ ] **F4-01** venv PQBR 0.8.4, `NOTEBOOKLM_HOME` próprio, perfil `pqbr` — Req: RF-10 · Testes: TS-02 · Depende de: F3-01 · Aceite: smoke test em caderno clonado · Portão: G4 · Obs:
- [ ] **F4-02** Deslogar a sessão antiga e login novo (t191) — Req: RF-10 · Depende de: F4-01 · Aceite: um só dispositivo · Portão: G4 + autorizar interrupção da produção atual · Obs:
- [ ] **F4-03** Serviço único dono da sessão (Activity, fila `notebooklm`, concorrência 1; consumo no Supabase) — Req: RF-10, RF-32 · Testes: TS-02, V7 · Depende de: F4-02 · Aceite: consumo gravado (H6) · Portão: G4 · Obs:
- [ ] **F4-04** MP32 com instalação própria 0.8.2; skills do `rede` sem cópia de cookies — Req: RF-10 · Depende de: F4-03 · Aceite: MP32 funcionando · Portão: G4 · Obs:
- [ ] **F4-05** Remover o pipx global (manter `~/.notebooklm` 7 dias; backup do crontab) — Req: RF-10 · Depende de: F4-04 · Aceite: rollback ensaiado · Portão: G4 · Obs:

## Fase 5: estabilidade e produção (D5)

- [ ] **F5-01** Grade, coleta, 3 barreiras, R10, polêmica — Req: RF-01..RF-05 · Testes: TS-01, V4 · Depende de: F3-01 · Aceite: teste do incidente de 08/10 passa · Portão: nenhum · Obs:
- [ ] **F5-02** `EpisodioWorkflow` real + Schedules (janelas 11:40, 14:40, 18:35, 21:15) + vigia de prazo — Req: RF-06, RF-17, RNF-10 · Testes: TS-02, TS-04 · Depende de: F5-01, F4-03 · Aceite: ciclo completo em paralelo · Portão: **G5** · Obs:
- [ ] **F5-03** Dias em paralelo sem falha; corte do fluxo antigo; **pausa do perfil `rede`** — Req: RF-01, RNF-05 · Testes: TS-REPLAY · Depende de: F5-02, F5-04, F5-05 · Aceite: N dias sem falha · Portão: **G5b** · Obs:
- [ ] **F5-04** Fichas: resolvedor sem LLM, criação sob demanda, verificação Telegram/painel, proveniência — Req: RF-08, RNF-08 · Testes: TS-02, V2, V6 · Depende de: F3-01 · Aceite: ficha nova sem bloqueio; "Não Aprovado" abre ticket · Portão: nenhum · Obs:
- [ ] **F5-05** Render e pós FFmpeg — Req: RF-09 · Testes: TS-02 · Depende de: F4-03 · Aceite: end card cortado só se detectado; logo com zoom · Portão: nenhum · Obs:

## Fase 6: resiliência (D6)

- [ ] **F6-01** Guardião de sessão (escada t272), teste de resposta, escada de falhas, NETWORK_WAITING, outbox, fallback do Jev, fila Camofox — Req: RF-37..RF-39, RNF-02, RNF-04 · Testes: TS-10 · Depende de: F5-02 · Aceite: simulação de cada degrau; nenhuma cópia de cookies sem OK · Portão: **G6** · Obs:

## Fase 7: editorial e auditor

- [ ] **F7-01** (D11) Contrato v2 sem superados; decidir R1–R6, R8, R9; RUNBOOK; SOP — Req: RF-07 · Testes: V1 · Depende de: R-005 · Aceite: aprovado pelo José · Portão: **G7** · Obs: R1–R9 EM CONSTRUÇÃO — aguardando José.
- [ ] **F7-02** (D4) Auditor (Gemini web via Camofox, Jev no texto, código decide; imagem×fala não reprova) — Req: RF-11..RF-14 · Testes: TS-03, V3 · Depende de: F3-01, F7-01 · Aceite: falso aprovado/reprovado medidos · Portão: G7 · Obs:

## Fase 8: publicação, armazenamento e revisão humana

- [ ] **F8-01** (D7) `PublicacaoWorkflow` + `Item5Workflow` — Req: RF-15..RF-21 · Testes: TS-04, TS-05, V4, V5 · Depende de: F6-01, F7-02 · Aceite: sem duplicata; 1 agendamento por via; item 5 em vídeo privado · Portão: **G8** · Obs:
- [ ] **F8-02** (D13) Drive t267, upload com hash, limpeza noturna — Req: RF-40, RF-41 · Testes: TS-11, V6 · Depende de: F5-02 · Aceite: duplicata movida, nada excluído · Portão: G8 · Obs:
- [ ] **F8-03** Revisão humana como último recurso — Req: RF-36 · Testes: TS-09 · Depende de: F8-01 · Aceite: item vai ao local de revisão, José avisado, determinação registrada · Portão: aprovar o local · Obs: [PROPOSTA] Supabase + `04_Privados_Revisao`.

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

- [ ] **L-01** Rotação de senhas e tokens (`paperclip_app`, root do Contabo, token do OpenCode) — Portão: José · Obs: adiado (t327).
- [ ] **L-02** Estudo de outros canais e cota da API para vários canais — Portão: José · Obs: adiado (t327).
- [ ] **L-03** Excluir `tasks/` se as rotinas ficarem só como Schedules — Depende de: F05-07 · Portão: José · Obs:
