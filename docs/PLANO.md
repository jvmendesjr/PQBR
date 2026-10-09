# PLANO de construção da PQBR (SDD)

> Autoridade: abaixo de `docs/REGRAS.md` e de `docs/ARQUITETURA.md`. Adaptado em 09/10/2026 do plano SDD anterior (premissa de "org Paperclip com 12 agentes", superada pelas t281–t286).
> Não consultar `docs/arquivo/`, `docs/pesquisas/` nem `docs/DECISOES-LOG.md` sem aprovação explícita do José (t287).
> Legenda: [APROVADO] · [VERIFICADO] · [HIPÓTESE] · [PROPOSTA] · EM CONSTRUÇÃO — aguardando José.

## 0. Premissas

- **Quem constrói:** agentes de desenvolvimento, conduzidos pelo jr; **sem core-eng** (t284). O José aprova cada portão e cada merge.
- A espinha é **código + motor de workflow** (Temporal primeiro, DBOS plano B; t283). O Paperclip é **painel desde o início** (t282). O Telegram fica com o Hermes `pqbr` (t281).
- Mudanças durante a construção são **tarefas de desenvolvimento** (D), nunca tickets; cada uma com autorização, critério de aceite e rollback (t187; item 7).
- Nada que depende de hipótese é construído antes de ela virar VERIFICADO (item 7).
- Fases do produto: construção → **validação (7 itens; prioridade 1, 2 e 3)** → produção.
- Cada entregável vai numa branch própria (`sdd/fase-N-...`) e entra na `main` com aprovação do José. **Nada de push sem autorização.**
- Segredos nunca no repositório, em tickets, no Supabase, no Hindsight ou em logs (item 6).

Formato de cada fase: **Objetivo · Entregáveis · Aceite · Portão do José · Rollback · Dependências.**

---

## Fase 0: especificação e rastreabilidade
- **Objetivo:** transformar o `REGRAS.md` em especificação executável e rastreável antes de qualquer código.
- **Entregáveis:** `docs/sdd/01-especificacao.md` (requisitos RF/RNF com status e tNNN); `docs/sdd/02-rastreabilidade.md` (tNNN → requisito → tarefa D → teste). A "constituição" do plano anterior é o próprio `REGRAS.md`.
- **Aceite:** toda regra do REGRAS.md aparece na especificação com a origem; nenhuma regra sem origem, exceto as marcadas [PROPOSTA].
- **Portão G0 (José):** aprova a especificação e a ordem deste plano.
- **Rollback:** reverter o commit; só documentos.
- **Dependências:** nenhuma.

## Fase 0.5: spike de 1 dia do motor de orquestração (t283)
- **Objetivo:** escolher o motor com dados do servidor real.
- **Entregáveis:** `docs/sdd/adr-001-orquestrador.md` com a medição; compose isolado do Temporal só com Postgres local dedicado (sem Elasticsearch, separado do `mp32-postgres`); `EpisodioWorkflow` de brinquedo com timer, sinal de aprovação vindo do Telegram (Hermes `pqbr`) e uma Activity que falha; simulação de Supabase fora com outbox; demonstração de como o painel Paperclip é alimentado.
- **Aceite:** RAM total abaixo do limite combinado com o José; retomada após `kill -9` no worker e após reboot; aprovação por sinal funcionando.
- **Se reprovar:** mesmo teste com o **DBOS** (plano B).
- **Portão G0.5 (José):** escolhe o motor; confirma no teste: (a) os dois bancos (Postgres do Temporal só para estado; Supabase para dados de negócio); (b) retentativas duráveis + outbox no lugar da fila em arquivo da t242; (c) a forma de alimentar o painel Paperclip, demonstrada no teste [t324–t326].
- **Rollback:** `docker compose down -v` do spike; nada de produção é tocado.
- **Dependências:** G0. Hipóteses H-ORQ1, H-ORQ2.

## Fase 1: painel Paperclip (t282)
- **Objetivo:** o José ver o estado da construção e, depois, da produção, desde o início, sem o Paperclip ser dono do fluxo.
- **Entregáveis:** forma de alimentar o painel conforme a ADR-002; nenhum agente com efeito; heartbeats desligados.
- **EM CONSTRUÇÃO — aguardando José (a demonstrar no teste da Fase 0.5) [t324–t326]:** pacote `company/` com agentes pausados ou só issues/projetos gravados por código; destino de `company/` e `tasks/`. Se houver pacote, seguir o formato agentcompanies/v1 (`COMPANY.md` com `schema`, `agents/<slug>/AGENTS.md` com as instruções no corpo, `.paperclip.yaml` com `schema: paperclip/v1`, segredos só como `inputs.env` `kind: secret`).
- **Aceite:** o painel mostra as tarefas D e os portões; nenhum heartbeat ligado.
- **Portão G1 (José):** aprova a forma do painel.
- **Rollback:** arquivar o projeto ou a org no Paperclip (exclusão só pelo José).
- **Dependências:** G0. Riscos #6596 e `--yolo` (ADR-002).

## Fase 3: fundações (D3 + D14)
- **D3, contratos Pydantic únicos** (`src/pqbr/schemas/`): `RoteiroShort` de 15 s a 3 min, alvo de ~50 s (t271), palavras dimensionadas a ~2,3 palavras/s [t324–t326]; estados aprovado → enviando → enviado(video_id) → agendado → publicado; comentário multirrótulo; saídas fechadas de `decide()`; auditoria com veredito/motivo/ID da cena. **`canal_id` em todo o schema** e `config/canais/pqbr.yaml` [PROPOSTA]. Migração `db/migrations/0001_base.sql`; carga de `db/seeds/temas-publicados.csv` na tabela de temas (R10).
- **D14, verificador de segredos/PII:** regex/scanner primeiro, Jev como segunda camada; hook antes de gravar no Hindsight (inclusive memórias de código), tickets, Supabase e logs; pre-commit no repo.
- **Aceite:** testes de esquema passam; o scanner bloqueia o segredo de teste.
- **Portão G3:** José aprova os esquemas.
- **Rollback:** migrações com `down`.
- **Dependências:** G0.5 (para o desenho multi-canal). H13.

## Fase 4: D1, migração do notebooklm-py (t187–t191)
- **Entregáveis:** venv da PQBR com 0.8.4 fixada, `NOTEBOOKLM_HOME` próprio, perfil `pqbr`; serviço único dono da sessão como Activity na fila `notebooklm` (concorrência 1) [PROPOSTA]; `usage --json` no Supabase; MP32 com instalação própria em 0.8.2; skills do `rede` aposentadas ou apontadas para o serviço, sem cópia de cookies; pipx global removido por último (`~/.notebooklm` mantido 7 dias; backup do crontab). **Antes do login novo, deslogar a sessão antiga** (t191).
- **Aceite:** smoke test em caderno clonado; consumo gravado (ou contagem própria se H6 falhar); MP32 funcionando; rollback ensaiado.
- **Portão G4:** José autoriza **cada passo**, em especial o logout e a interrupção da produção atual.
- **Rollback:** voltar ao pipx 0.8.2 global e ao crontab salvo.
- **Dependências:** G0 (pode correr em paralelo com a Fase 3). H6, H15.

## Fase 5: D5, estabilidade
- **Entregáveis:** grade por código a partir da data; 3 barreiras de repetição (barreira 2 via `decide()`); R10; máquina de estados = `EpisodioWorkflow` com checkpoint; horários fixos + vigia de prazo como **Schedules e timers duráveis do motor** [PROPOSTA; substitui os timers do SO do plano anterior]; coleta de tendências + caderno diário + Deep Research + pontuação de polêmica.
- **Aceite:** vários dias seguidos sem falha em paralelo **antes do corte do fluxo antigo**; teste que reproduz o incidente de 08/10 passa.
- **Portão G5:** início do teste paralelo; **G5b:** corte do fluxo antigo (o `rede` passa a rodar só sob demanda).
- **Rollback:** pausar os Schedules; o fluxo antigo continua até G5b.
- **Dependências:** D3, D1.

## Fase 6: D6, resiliência
- **Entregáveis:** guardião de sessão como Schedule (~20 min com variação; checagem extra ~30 min antes de publicar; escada t272); teste de resposta; escada 30 s → 2 min → 8 min como `RetryPolicy` + lógica no workflow; `NETWORK_WAITING` sem gastar tentativa; retentativas duráveis + outbox para o Supabase no lugar da fila em arquivo da t242 (conforme G0.5); fallback do Jev.
- **Aceite:** simulação de cada degrau, de rede fora e de Supabase fora; nenhuma cópia de cookies sem OK.
- **Portão G6:** José aprova o relatório de simulação.
- **Rollback:** pausar o guardião.
- **Dependências:** D5. H7, H9.

## Fase 7: D11 + D4, editorial e auditor
- **D11:** `docs/CONTRATO-EDITORIAL.md` v1 → **v2** sem os trechos SUPERADOS (t262–t265, t271); RUNBOOK do auditor revisado; steering/SOP em `templates/sop/`.
- **D4:** `src/pqbr/pipeline/auditor/` (`decide.py` e prompts com o critério t264/t265; quadros por cena + Whisper; Gemini sim/não em 2 rodadas; Jev nas checagens de texto; relatório por template; detector de pedido de comentário; direitos de áudio bloqueantes acima de 60 s). Gabarito: `labels.json` e `decide.py` do teste de 08/10 vão para `tests/auditor/` e `src/pqbr/pipeline/auditor/`.
- **Aceite:** contrato v2 e RUNBOOK aprovados; falso aprovado e falso reprovado medidos.
- **Portão G7:** José aprova. Fecha os itens 1 e 3 da validação.
- **Rollback:** v1 e auditor v3 seguem como referência até a aprovação.
- **Dependências:** D3. H10.

## Fase 8: D7 + D13, publicação e armazenamento
- **D7:** `PublicacaoWorkflow` com ID idempotente; `videos.insert` com agendamento; até H1, sobe privado e o Camofox agenda (fila `camofox`, concorrência 1); sem duplicidade (REGRAS §15); `Item5Workflow` (REGRAS §16).
- **D13:** Drive t267; ciclo de upload com hash (t268); limpeza noturna na rotina do @prod-director (t270).
- **Aceite:** upload interrompido sem duplicata; 1 agendamento por via; item 5 testado em vídeo privado; duplicata de teste movida, nada excluído.
- **Portão G8:** José aprova o primeiro upload real. Fecha os itens 4, 5 e 6.
- **Rollback:** pausar a publicação; vídeos de teste ficam privados.
- **Dependências:** D6, D4. H1, H2, H14.

## Fase 9: D12, monitores e relatório diário
- **Entregáveis:** monitor de atualizações (semanal; nunca atualiza sozinho; com OK do José vira ticket ou tarefa para qualquer agente de dev, t286); monitor de consumo (NotebookLM, Jev); relatório diário por template; custo por canal; UI do motor como painel técnico.
- **Aceite:** relatório no Telegram por vários dias.
- **Portão G9:** José valida o relatório; os dados alimentam o **teto de orçamento** (EM CONSTRUÇÃO — aguardando José).
- **Dependências:** D7. H6, H8, H12.

## Fase 10: D8 + D9 + D10, comunidade
- **D9:** banco de 60 frases rascunhado pelo NotebookLM e aprovado pelo José (t249).
- **D10:** registrar no `DECISOES-LOG.md` a regra do item 5 e a regra completa de respostas como instrução expressa do dono (política da API III.I.2, III.E.3).
- **D8:** `src/pqbr/community/` conforme REGRAS §19, com o kill switch como sinal do motor [PROPOSTA]; 1 resposta real de teste antes do automático (H3).
- **Aceite:** 3 dias de sombra ou ~30 respostas simuladas aprovadas sem correção (t248).
- **Portão G10:** José liga respostas e corações.
- **Dependências:** D3, D6, D7. H3, H4, H7, H8, H16.

## Fase 11: D15, estratégia para 2 personagens (não bloqueia, t264)
- Testes de preservação das fichas e alternativa (narração do NotebookLM + quadros de outra ferramenta montados em código). Fecha o item 2. **G11:** decisão do José com evidência.

## Fase 12: validação final e liberação da produção
- **Entregáveis:** `docs/sdd/validacao-7-itens.md`; ordem de ativação dos Schedules do canal, um a um.
- **Portão G12 (José):** libera a produção.
- **Rollback:** pausar os Schedules; HOLD da fila.
- **Dependências:** todas; orçamento definido.

**Ordem resumida:** G0 → G0.5 → Fase 1 (painel) → Fase 3 ∥ Fase 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12.
_Fase 2 do plano anterior (import da org Paperclip com 12 agentes) foi removida pela t282/t284._

---

## Tarefas de desenvolvimento (D1–D15)

| # | Tarefa | Fase | Critério de pronto |
|---|---|---|---|
| D1 | Migração do notebooklm-py | 4 | Smoke test; consumo gravado; MP32 ok; rollback |
| D2 | Ajuste do perfil Hermes `pqbr` (já criado): env mínimo, toolsets, budgets; sem `--yolo`/sudo | 1 | Perfil revisado pelo José |
| D3 | Contratos Pydantic + migração base multi-canal | 3 | Testes de esquema |
| D4 | Auditor t264/t265, duração t271, CTA, direitos de áudio | 7 | Gabarito ampliado medido |
| D5 | Grade, barreiras, estados, Schedules | 5 | Dias sem falha antes do corte |
| D6 | Guardião, escadas, buffer t242, fallback do Jev | 6 | Simulação de cada degrau |
| D7 | Publicação API + Camofox; item 5 | 8 | Sem duplicata; 1 agendamento por via |
| D8 | @prod-comunidade | 10 | Sombra de 3 dias / ~30 respostas |
| D9 | Banco de 60 frases | 10 | Aprovado pelo José |
| D10 | Registro da regra do item 5 e das respostas | 10 | Entrada no DECISOES-LOG |
| D11 | Contrato editorial v2 + RUNBOOK + SOP | 7 | Aprovados pelo José |
| D12 | Monitores + relatório diário | 9 | Relatório no Telegram |
| D13 | Drive: estrutura, upload com hash, limpeza | 8 | Duplicata movida, nada excluído |
| D14 | Verificador de segredos/PII | 3 | Bloqueia segredo de teste |
| D15 | 2 personagens | 11 | Decisão do José |

Hipóteses H1–H16, H-ORQ1–3 e H-SDD1–3: ver `docs/ARQUITETURA.md` §7.

## Pendências que precisam do José (EM CONSTRUÇÃO — aguardando José)

1. Teto de orçamento mensal (após os primeiros dias de testes; t268/decisão 10).
2. ~~Horários das janelas~~ RESOLVIDO [t324–t326]: 11:40, 14:40, 18:35, 21:15.
3. ~~@prod-director: LLM ou rotina~~ RESOLVIDO [t324–t326]: rotina fixa executa; agente propõe (Pydantic v2) e o José aprova.
4. Persona do @prod-compliance e do @pqbr-assistente.
5. Motor: Temporal × DBOS (G0.5). A substituição da fila t242 por retentativas + outbox e a manutenção do Supabase estão decididas [t324–t326], a confirmar no teste.
6. Forma do painel Paperclip (pacote `company/` ou não): a demonstrar no teste da Fase 0.5.
7. ~~Tickets e bank Hindsight~~ RESOLVIDO [t324–t326]: 2 aprovações (abertura com correções + merge); bank único por organização.
8. Aprovação das 60 frases (D9) e do contrato v2 (D11).
9. Configuração única do Studio (moderação, links, palavras bloqueadas): sem resposta registrada.
10. Definição de sucesso do piloto (metas só depois da API; recalibrar em 2–4 semanas).
11. Papel do `rede` depois da PQBR existir; migração do `yt_production`.
12. Juiz visual em produção: Gemini web via Camofox × Gemini API (a chave é decisão do José; H10).
13. Rotações: senha do `paperclip_app`, root do Contabo, token do OpenCode.
14. Política de cota da API para vários canais (um projeto GCP ou auditoria).

## Riscos

| Risco | Efeito | Mitigação |
|---|---|---|
| `hermes_local` força `--yolo` | Agente executa sem confirmação | Painel sem agentes com efeito; perfil `pqbr` sem sudo sem senha; H-SDD1 |
| Repetir a deriva da COR-1 | Retrabalho | REGRAS como autoridade; rastreabilidade tNNN; t287 |
| RAM/swap do `pc` com o motor | Lentidão, quedas | Spike G0.5; DBOS como plano B |
| Determinismo e versionamento de workflows | Falha no replay | Testes de replay no CI; workflows curtos |
| Recovery storm do Paperclip sem internet (#6596) | Carga e ruído | Heartbeats desligados |
| Sessão do NotebookLM com dois donos | Bloqueio da conta | Logout antes do login novo (t191) |
| Quedas da sessão do Studio (H9) | Publicação parada | Guardião + escada t272 |
| Auditoria do app do GCP demora (H1) | Sem upload público pela API | Privado + Camofox agenda (t273) |
| Cotas da Data API e limites do NotebookLM | Falha no lote | Monitor de consumo; espaçar acima de 80% |
| Desmonetização por conteúdo inautêntico (pior ao escalar canais) | Saída do YPP | Compliance + HOLD + variedade; R10 |
| Respostas parecendo robô | Dano ao canal | Banco aprovado, limites t274, sombra, kill switch |
| Segredo vazado em ticket, memória de código ou repo | Credencial exposta | D14 primeiro; pre-commit |
| Supabase fora | Estado perdido | Retentativas duráveis do Temporal + outbox; nada agendado/público sem estado gravado |
| Métricas divergentes (30 × 46 Shorts) | Metas erradas | Só pela Analytics API (H12) |
| Disco do servidor | Falta de espaço | Ciclo t267/t268; `runtime/` limpo |
