# PLANO da PQBR (fases, portões e rollback)

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
| 4 | Migração do notebooklm-py | **G4** a cada passo | voltar ao pipx 0.8.2 e ao crontab salvo |
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
