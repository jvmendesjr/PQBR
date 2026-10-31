> ⛔ **PESQUISA / REFERÊNCIA DE PRÉ-CONSTRUÇÃO: AGENTES NÃO CONSULTAM SEM APROVAÇÃO EXPLÍCITA DO JOSÉ (t287).** Pode conter premissas superadas que, mal interpretadas, iriam parar em produção. As regras válidas estão em `docs/REGRAS.md`.

> Nota: base da t283. A §8 virou a ADR-001 em docs/ARQUITETURA.md; as mudanças da §9 estão no docs/PLANO.md.

# Pesquisa: orquestração da PQBR pensando em escala (vários canais e fluxos)

> **Data:** 09/10/2026, horário de Fortaleza · **Autor:** jr (pesquisa) · **Para:** José
> **Pergunta:** manter o Paperclip como base, trocar por um motor de workflow (Temporal ou alternativa) ou usar um harness de agentes (DeepSeek Harness etc.)? Como fazer isso pensando em vários canais?
> **Legenda:** **[VERIFICADO]** visto na fonte ou no servidor hoje · **[FONTE]** afirmação de terceiros, com link · **[OPINIÃO]** avaliação do jr · **[PROPOSTA]** precisa do OK do José.
> Nada foi alterado no servidor. Só leitura (`free`, `ps`, `docker ps`, versões).

---

## 1. Resposta curta

**Recomendação [OPINIÃO]: arquitetura híbrida, com espinha determinística em Temporal (self-hosted, só Postgres, sem Elasticsearch) e poucos agentes de IA chamados como passos dessa espinha. O Paperclip vira opcional: no máximo painel e casa de 3–4 agentes que pensam, nunca o agendador nem o dono do fluxo.**

- O fluxo da PQBR (grade → NotebookLM → pós FFmpeg → auditor → upload → agendamento → monitores → item 5) é um processo de negócio fixo. Isso pede **execução durável**: estados, novas tentativas, timers longos ("publicar às 18h35"), espera por aprovação humana e retomada depois de queda. É exatamente o que Temporal faz. [FONTE: docs Temporal, §3]
- Agente de IA (Paperclip, DeepSeek Harness, CrewAI etc.) como **dono** do fluxo repete o risco da COR-1: improvisa. A comunidade relata deriva e "busywork" no Paperclip (§5).
- Para **vários canais**, o canal vira **configuração** (um YAML por canal) e o mesmo código roda N vezes, com `canal_id` em tudo. Novo canal = novo arquivo de config + novo contrato editorial, não nova org de agentes.
- **Plano B leve [OPINIÃO]:** DBOS (biblioteca Python sobre Postgres, MIT). Escolher DBOS se o José priorizar RAM e manutenção mínimas acima de painel, ecossistema e maturidade. O Hatchet Lite fica em terceiro.
- **Não recomendo** n8n, Airflow, Prefect, Windmill nem harness genérico como espinha (§4 e §6).

---

## 2. Realidade do servidor `pc` [VERIFICADO hoje, 09/10]

| Item | Valor |
|---|---|
| RAM | 15 GiB total, **~9,5 GiB disponíveis**, mas **5,7 GiB de swap em uso** (sinal de pressão de memória) |
| CPU | 24 núcleos |
| Disco `/` | 452 GB, 36% usado |
| Docker | 29.8.1, já roda `mp32-postgres` (postgres:16-alpine), deskcomm (Redis + workers), waha, email/kiwify workers e tailscale-proxy |
| Já instalados | `paperclipai`, `hermes`, **`dsh` (DeepSeek Harness) 0.2.0-rc.2** e um timer `dsh-tls-renew` |
| Maiores consumidores | hermes (~480 MB e ~370 MB), node, hindsight-api, camoufox, headroom, openviking |

Implicação: um Temporal só com Postgres (medido em ~0,9 GiB parado, §3.2) **cabe**, mas o swap em uso pede duas coisas antes: (1) medir de novo com tudo rodando e (2) desligar o que sobra, por exemplo o OpenViking, que já está sendo trocado pelo Hindsight. [PROPOSTA]

---

## 3. (a) Temporal

### 3.1 O que entrega para a PQBR
- **Workflows duráveis em Python** (SDK oficial, MIT). Toda chamada externa (NotebookLM, FFmpeg, Gemini, YouTube, Drive, Supabase, Camofox) vira uma **Activity** com política de novas tentativas. O workflow guarda o estado e retoma de onde parou depois de queda. [FONTE](https://docs.temporal.io/develop/python/versioning)
- **Timers duráveis e agendas (Schedules)** com política de sobreposição (Skip, BufferOne, BufferAll, CancelOther, TerminateOther, AllowAll) e janela de recuperação (catchup) depois de uma queda. Isso substitui os timers do systemd e o "vigia de prazo". [FONTE](https://docs.temporal.io/schedule)
- **Aprovação humana (HITL)**: um Signal ou Update + `workflow.wait_condition(..., timeout=...)`. Dá para esperar horas ou dias pelo toque do José no Telegram, sem processo vivo. Há padrão oficial de aprovação. [FONTE](https://docs.temporal.io/design-patterns/approval) · [FONTE](https://docs.temporal.io/develop/python/workflows/message-passing)
- **UI web** com o histórico de cada execução (o que rodou, quando, com qual erro).
- **Integrações de IA prontas**: OpenAI Agents SDK (GA em 23/03/2026) [FONTE](https://docs.temporal.io/develop/python/integrations/openai-agents); Pydantic AI com `TemporalDurability()`, que casa com o Jev/Pydantic [FONTE](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/); e o "Temporal Agent Harness", que a própria Temporal chama de "earlier than public preview" (não usar agora). [FONTE](https://temporal.io/blog/temporal-agent-harness-durable-agent-infrastructure)
- **Maturidade [VERIFICADO no GitHub hoje]:** `temporalio/temporal`, MIT, ~23,5 mil estrelas, commits hoje; `sdk-python`, MIT.

### 3.2 Custo de recursos no servidor de casa
- Pilha mínima (Postgres + Temporal + UI, **sem Elasticsearch**): **~915 MiB parada**, medição de 15/08/2026 (Railway). O Elasticsearch sozinho usava ~1,3 GiB. [FONTE](https://railway.com/deploy/temporal-or-durable-workflows-no-elastic.md)
- Guia de VPS: "solo dev / sem ES: 2 GB / 2 vCPU"; "ferramenta interna, produção leve: 4 GB / 2 vCPU". [FONTE](https://ramnode.com/guides/temporal)
- O compose oficial vem **com** Elasticsearch, então é preciso usar a variante só com Postgres. [FONTE](https://docs.temporal.io/self-hosted-guide/deployment)
- `NUM_HISTORY_SHARDS` **não pode ser mudado depois** de criado o cluster. Mudar significa recomeçar do zero. [FONTE](https://railway.com/deploy/temporal-or-durable-workflows-no-elastic.md)
- `temporal server start-dev --db-filename temporal.db` (SQLite) persiste, mas é para desenvolvimento. [FONTE](https://docs.temporal.io/cli/command-reference/server)

### 3.3 Armadilhas (o que a comunidade avisa)
- **Determinismo:** o código do workflow não pode ler relógio, gerar aleatório, fazer rede ou ler arquivo. Isso fica nas Activities. O sandbox Python "não é completamente isolado". [FONTE](https://docs.temporal.io/develop/python/best-practices/python-sdk-sandbox)
- **Versionamento:** mudar a ordem dos passos quebra workflows em andamento. Usar `workflow.patched()`, com o código novo no topo, e depois `deprecate_patch()`, ou então Worker Versioning. [FONTE](https://docs.temporal.io/patching)
- **Peso operacional:** no HN, quem usa para automação simples gosta, e quem construiu sistema grande auto-hospedado reclama de upgrades e operação. "Determinism sucks… make everything idempotent in activities". Mesmo assim, outro relato diz: "100% would adopt again". [FONTE HN](https://news.ycombinator.com/item?id=48326802)
- **Agente autônomo dentro de uma Activity opaca** dá problema (estado local de sessão, histórico grande). Use o Temporal em volta dos turnos do agente, com checkpoints explícitos. [FONTE](https://befailproof.ai/blog/why-temporal-breaks-with-ai-agents/)

**Mitigação para a PQBR [OPINIÃO]:** workflows curtos, um por episódio (`EpisodioWorkflow`, que vive no máximo alguns dias) e um por rotina via Schedule. Assim, versão nova afeta poucos workflows em andamento. Testes de replay no CI com históricos reais. Toda Activity idempotente, com a chave = código `PQBR-EPxxxx` + passo.

---

## 4. (b) Alternativas mais leves ou diferentes

| Ferramenta | Licença [VERIFICADO no GitHub/LICENSE] | Infra | Encaixe na PQBR | Veredito [OPINIÃO] |
|---|---|---|---|---|
| **DBOS Transact** (Python) | MIT | **Biblioteca**, só Postgres (pode ser o Supabase via session pooler, nunca transaction mode) [FONTE](https://docs.dbos.dev/integrations/supabase) | Workflows/steps com decorators; `DBOS.sleep` durável; `DBOS.recv/send` para aprovação humana [FONTE](https://docs.dbos.dev/python/tutorials/workflow-communication); agendas cron persistidas [FONTE](https://docs.dbos.dev/python/tutorials/scheduled-workflows); **filas com limite de concorrência global, por worker e por tenant** (= por canal) [FONTE](https://docs.dbos.dev/explanations/comparing-temporal.md); Pydantic AI `DBOSDurability()` [FONTE](https://ai.pydantic.dev/durable_execution/dbos/) | **Plano B forte.** Menos RAM e nenhum servidor extra. Comunidade menor (~1,6 mil estrelas) e a comparação com o Temporal é feita pelo próprio fornecedor |
| **Hatchet** (Lite) | MIT | 1 container + Postgres (Postgres-only é o padrão desde a v0.55) [FONTE](https://docs.hatchet.run/self-hosting/hatchet-lite) · [FONTE](https://github.com/hatchet-dev/hatchet/issues/1737) | Durable tasks com sleep e espera de evento [FONTE](https://docs.hatchet.run/durable-execution); concorrência por chave e rate limit [FONTE](https://docs.hatchet.run/v1/concurrency); entrega "at least once" [FONTE](https://docs.hatchet.run/llms/v1/architecture-and-guarantees.md) | Terceira opção. Boa, mas mais jovem que o Temporal em workflows longos com HITL |
| **Inngest** (self-host) | **SSPL** (vira Apache-2.0 no futuro) | Binário único; SQLite em nó único, Redis + Postgres em produção [FONTE](https://www.inngest.com/docs/self-hosting) | Bom em funções orientadas a eventos; ecossistema centrado em TypeScript | Não. Licença SSPL e foco em TS |
| **Restate** | Servidor **BSL**; SDKs MIT [FONTE](https://docs.restate.dev/get-restate) | Binário único, sem banco externo [FONTE](https://docs.restate.dev/server/overview) | Execução durável com journal | Interessante, mas licença BSL e SDK Python menos testado. Não agora |
| **Prefect 3** | Apache-2.0 | Servidor + SQLite/Postgres (+ Redis com vários workers) [FONTE](https://docs.prefect.io/v3/how-to-guides/self-hosted/docker-compose) | Orquestração de **dados** (flows/tasks). Segundo relato, crash de worker pode perder trabalho em andamento sem armazenamento de resultado [FONTE](https://www.macrostack.net/run/prefect) | Não. Feito para pipelines de dados, não para espera humana longa |
| **Windmill** CE | AGPLv3 (+ partes proprietárias) | Servidor + Postgres; ~1–2 GB por worker [FONTE](https://www.windmill.dev/docs/advanced/self_host) | Plataforma de scripts com UI, flows e apps internos | Útil para painel e scripts de operação, não como espinha. Workers pesam no `pc` |
| **n8n** | Sustainable Use License (uso interno liberado, revenda não) [FONTE](https://docs.n8n.io/n8n-community-license/community-license/license-faq) | Servidor Node + banco | Visual; git só como push/pull, sem revisão estilo PR nativa [FONTE](https://docs.n8n.io/administer/use-source-control-and-environments/use-git-in-n8n) | Não como espinha: fluxo visual contraria o SDD com PR e testes. Pode servir de "cola" pontual |
| **Airflow** | Apache-2.0 | Scheduler + webserver + workers + banco | DAGs de lote de dados | Não. Pesado e ruim para eventos e aprovação humana |

**Por que Temporal e não DBOS como primeira escolha [OPINIÃO]:** o José quer vários canais e fluxos novos. O Temporal tem UI madura, Schedules ricos, Signals e Updates, versionamento formal, o maior ecossistema e integrações de IA oficiais. O custo é ~1 GiB de RAM e um serviço a mais para manter. **Se o teste de RAM (§2) mostrar aperto, ou se o José preferir zero serviço novo, DBOS** entrega o essencial (durabilidade, cron, filas por canal, HITL) dentro do próprio processo Python. As duas escolhas usam o mesmo desenho: Activities/steps idempotentes, `canal_id`, config por canal. Então a decisão não muda a especificação, só o adaptador. **Sugiro decidir com um teste de 1 dia (§9, Fase 0.5).**

---

## 5. (d) Paperclip como camada de gestão: o que se sabe

### 5.1 Pontos fortes (por que mantê-lo opcional)
- Controles reais: checkout atômico de tarefa, orçamento por agente e por empresa com parada dura, pausa de agentes, aprovações, trilha de auditoria. A ClawBlog avalia bem, mas deixa a confiabilidade "abaixo de 70" até testes independentes. [FONTE](https://clawblog.com/reviews/paperclip)
- Projeto muito ativo: MIT, ~99 mil estrelas, commits hoje [VERIFICADO no GitHub].
- **Adapter `process`**: roda um script por heartbeat, injeta `PAPERCLIP_*` e captura stdout/stderr. Hoje aparece como "Coming soon" no formulário e só é configurável via API ou import de pacote. Serve para um agente "ponte" que só dispara ou consulta o Temporal. [FONTE](https://docs.paperclip.ing/reference/adapters/process/)

### 5.2 Riscos documentados
- **Deriva e "busywork"**: "40% genuinely productive, 60% busywork… governance theater unless you anchor them to one real KPI" [FONTE Reddit](https://www.reddit.com/r/aisolobusinesses/comments/1s9gfma/is_paperclip_ai_actually_useful_or_just_another/). "Agent drift without tight skill files. Vague role definitions produce vague output"; queima de tokens com heartbeats agressivos. [FONTE](https://vibecoding.app/blog/paperclip-review)
- **`hermes_local` + instruções**: a issue #3833 (abr/2026) mostra que o adapter Hermes **não injetava o AGENTS.md/SOUL.md no prompt**. O agente recebia só o prompt genérico do heartbeat. A issue foi fechada em 22/07/2026 como resolvida pelo PR #8543. [FONTE](https://github.com/paperclipai/paperclip/issues/3833) **[HIPÓTESE]: se o Paperclip ou o adapter instalado no `pc` for anterior a essa correção, isso explicaria a COR-1 ter inventado outro canal. Conferir a versão instalada antes de culpar só as instruções.**
- **`--yolo`**: o PR #3850 explica o motivo. Hermes roda sem TTY e os prompts de aprovação expiram, então o Paperclip força `--yolo`. Isso pula a confirmação **interna do Hermes**, não as aprovações do servidor Paperclip. [FONTE](https://github.com/paperclipai/paperclip/pull/3850) (o dossiê já tinha verificado o `--yolo` sempre ligado no `pc`).
- **Tempestade de recuperação sem internet** (issue #6596, **aberta**): quando a internet cai, o watchdog cria issues "Review silent active run" e acorda agentes que também falham. O ciclo se amplifica sem limite, com milhares de issues e gasto de tokens. O único contorno é `HEARTBEAT_SCHEDULER_ENABLED=false`. [FONTE](https://github.com/paperclipai/paperclip/issues/6596) **Muito relevante para servidor doméstico**, onde a internet cai.

### 5.3 Boas práticas para usá-lo por cima (se mantido)
1. **Paperclip nunca agenda produção.** Quem agenda é o Temporal (Schedules). Rotinas do Paperclip só para o que é de gestão (resumo semanal do analista, por exemplo).
2. **Só 3–4 agentes LLM** (analista, resumo da comunidade, análise de compliance e, se o José quiser, um director). Render, publisher, preflight e backup **não são agentes**: viram Activities.
3. Agentes LLM **não executam efeitos** (publicar, tornar privado, responder). Eles **propõem** e o fluxo determinístico executa, com a aprovação do José quando a regra exige. Isso neutraliza o `--yolo` nos passos críticos.
4. Heartbeats desligados, orçamento com parada dura, versão do Paperclip fixada e um verificador de conectividade antes de ligar qualquer heartbeat (por causa da #6596).
5. Instruções verificadas **no prompt real** (a sessão salva do Hermes), não só no arquivo. É o teste que a #3833 descreve.

---

## 6. (c) Harnesses de agentes com plugins de orquestração

| Harness | Situação [VERIFICADO/FONTE] | Encaixe | Risco [OPINIÃO] |
|---|---|---|---|
| **DeepSeek Harness (dsh)** | Já instalado no `pc` (0.2.0-rc.2). Repo `deepseek-ai/deepseek-harness`, MIT, criado em 13/08/2026; **todas as releases são pré-release** (a última é 0.2.1-alpha.2, de hoje) [VERIFICADO na API do GitHub]. Subagentes nativos [FONTE](https://deepseek-harness.github.io/deepseek-harness/en/reference/tool-catalog); plugins da comunidade: `dsh-agent-teams` (capitão + tarefas com dependência) [FONTE](https://github.com/liuyizhang671-design/dsh-agent-teams), `dsh-swarm-orchestrator` (DAG com revisores) [FONTE](https://dsh.directory/plugins/linkbag/dsh-swarm-orchestrator), `deepseek-harness-orchestrate` ("not an official DeepSeek package") [FONTE](https://github.com/apheli0os/deepseek-harness-orchestrate), `dsh-goalmesh` (retry automático "Planned") [FONTE](https://github.com/Jarad-z/dsh-goalmesh) | Bom para **trabalho de engenharia** (escrever código, revisar PR) | Como espinha de produção, não: é alfa/RC, os plugins são de terceiros e o **LLM monta o DAG**, que é justamente a improvisação que queremos evitar |
| **OpenAI Agents SDK** | Integração oficial com Temporal, GA [FONTE](https://docs.temporal.io/develop/python/integrations/openai-agents) | Agente dentro de workflow durável | Bom se algum dia precisar de agente com ferramentas; hoje é desnecessário |
| **Pydantic AI** | Durabilidade via Temporal, DBOS ou Prefect [FONTE](https://pydantic.dev/docs/ai/durable-execution/) | **Melhor encaixe para o `decide()` do Jev** (saída Pydantic validada) | Baixo |
| **LangGraph** | MIT; checkpointer Postgres + `interrupt` para HITL [FONTE](https://docs.langchain.com/oss/python/langgraph/interrupts) | Grafo de agente | Ao retomar, o nó **reexecuta do início**, e efeitos colaterais podem repetir [FONTE](https://effloow.com/articles/langgraph-checkpointing-postgres-gotchas-2026). Mais uma camada sem ganho para nós |
| **Claude Agent SDK** | Sessões são subprocessos locais; transcrição retomável, mas arquivos e estado vivo não são duráveis [FONTE](https://code.claude.com/docs/en/agent-sdk/hosting) | Agente de código | Custo de API e não resolve durabilidade |

**Conclusão [OPINIÃO]:** harness é ferramenta de **construção** (pode ajudar o jr ou a core-eng a escrever código), não de **operação**. Na operação, o LLM entra só como Activity com entrada e saída tipadas (Pydantic) e validação por código.

---

## 7. Boas práticas de pipeline de conteúdo multi-canal

1. **Máquina de estados explícita por episódio**, por exemplo `pauta → roteiro → render → auditado → aprovado → enviando → enviado(video_id) → agendado → publicado → medido`, mais `privado(item5)` e `hold`. Cada passo é retentável. **Gravar a intenção antes de todo efeito irreversível** e **reconciliar antes de tentar de novo** (buscar no canal pelo código PQBR-EPxxxx, o que já está no plano D7). [FONTE](https://github.com/TomGranot/faceless-channel-factory) · [FONTE](https://dankdev.com/Blog/youtube-shorts-automation-pi)
2. **Idempotência por chave estável**: ID do workflow = `<canal>:<episodio>:<passo>`. O Temporal recusa iniciar um workflow com ID repetido enquanto o primeiro está em execução, o que vira proteção natural contra publicação duplicada. [OPINIÃO baseada no modelo de Workflow ID do Temporal]
3. **Canal como configuração**, `config/canais/<slug>.yaml` com identidade, contrato editorial, CTA, janelas, teto/dia, credenciais (só nomes de segredos), personagens e caderno NotebookLM. Mais `canal_id` em todas as tabelas, no histórico de temas (R10 é **por canal**) e nos relatórios.
4. **Recursos compartilhados com fila e limite por recurso, não por canal:**
   - **Cota da YouTube Data API é por projeto do Google Cloud**, não por canal: 10.000 unidades/dia mais baldes próprios de 100/dia para `videos.insert` e `search.list`. [FONTE](https://developers.google.com/youtube/v3/determine_quota_cost) Com vários canais, a cota é dividida. Aumento só via auditoria. [FONTE](https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits)
   - **Camofox/sessão Google**: uma conta, uma sessão, concorrência 1 (fila dedicada no Temporal ou fila DBOS com limite 1).
   - **NotebookLM Pro**: limites da conta são compartilhados entre canais. O monitor de consumo (D12) precisa ver o total, não só o da PQBR.
5. **Portões humanos como sinais duráveis** (Telegram → bot determinístico → Signal/Update), aceitos só do ID do José (t237), com prazo e ação padrão segura em caso de timeout (por exemplo, não publicar).
6. **Observabilidade**: UI do Temporal (histórico por execução), relatório diário por template, alertas no Telegram e métricas de custo por canal e por episódio (tokens do Jev, uso do NotebookLM, chamadas de API).
7. **Controle de custo**: orçamento por canal no banco e verificado **antes** de cada Activity paga; kill switch global e por canal; LLM só onde há decisão.
8. **Risco de plataforma ao escalar**: desde 15/07/2025 o YouTube renomeou "repetitious content" para **"inauthentic content"**. Conteúdo em massa, repetitivo ou de template sem contribuição original não é monetizável, e conteúdo sintético realista precisa ser declarado. [FONTE](https://techcrunch.com/2025/07/09/youtube-prepares-crackdown-on-mass-produced-and-repetitive-videos-as-concern-over-ai-slop-grows/) · [FONTE](https://support.google.com/youtube/answer/1311392?hl=en) **Escalar canais com o mesmo molde aumenta esse risco**, então cada canal precisa de uma identidade e um contrato editorial próprios, não só outro nome.

---

## 8. Recomendação adaptada à realidade do José

**Arquitetura-alvo [PROPOSTA]:**

```
Telegram (José) ──► bot determinístico (aprovar/negar, só ID do José) ──► Signals/Updates
                                                                            │
Temporal (local, Postgres próprio no pc, sem ES)                           ▼
 ├─ Schedules por canal: grade da madrugada, lote, guardião de sessão, comentários, limpeza Drive, relatório, monitores
 ├─ EpisodioWorkflow(canal, ep): pauta → NotebookLM → FFmpeg → auditor → upload privado → agendar (Camofox) → confirmar
 ├─ Item5Workflow: qualquer problema → privado na hora + Telegram (sem substituir/republicar)
 └─ Workers Python (pacote src/pqbr) com filas: "notebooklm" (conc. 1), "camofox" (conc. 1), "render", "default"
      Activities: NotebookLM CLI 0.8.4, FFmpeg, Gemini juiz, decide() Jev via Pydantic AI, YouTube API, Drive, Supabase (outbox)
Supabase: dados de negócio, painel, histórico de temas, relatórios (sincronizado por Activity)
Hermes `pqbr`: só consulta e responde (lê Supabase/Temporal), sem executar
Paperclip (opcional, depois): 3–4 agentes LLM que PROPÕEM; nada de efeito direto
```

**Dicas**
- **Postgres do Temporal local no `pc`**, não no Supabase. A orquestração não pode parar quando a internet cai, e é justamente aí que a fila local da t242 precisa funcionar. Usar uma instância separada da `mp32-postgres`.
- Comece com **1 worker Python** e filas por recurso. Não é preciso Kubernetes.
- Fixe as versões (Temporal server, SDK, NotebookLM 0.8.4) e passe-as pelo monitor de atualizações (D12).
- Testes de replay do Temporal no CI desde o primeiro workflow.

**Oportunidades**
- O **histórico do Temporal substitui boa parte da "fila local" (t242)** e do vigia de prazo: o estado do fluxo nunca depende do Supabase estar no ar. O Supabase passa a ser atualizado por uma Activity com outbox (retenta até conseguir). **Isso muda a implementação da t242, não a regra. Precisa do OK do José.**
- Novo canal = YAML + contrato + caderno, e o código é reaproveitado. Fluxos novos (outro formato, outra plataforma) viram novos workflows no mesmo motor.
- A UI do Temporal dá ao José a visão de "onde está cada vídeo" sem o Paperclip.

**Cautelas**
- RAM: o `pc` já usa swap. Medir antes e liberar memória (OpenViking).
- Determinismo e versionamento exigem disciplina. Manter os workflows curtos.
- O `NUM_HISTORY_SHARDS` é escolhido uma única vez.
- Backup do Postgres do Temporal (dump diário no Drive, sem segredos).
- Não pôr agente autônomo dentro de Activity com efeito colateral.
- Paperclip: issue #6596 aberta (tempestade sem internet). Se mantido, heartbeats desligados e versão com a correção da #3833.
- DeepSeek Harness em alfa/RC: não usar na operação.

---

## 9. Caminho de migração e mudanças no `PLANO-SDD-PQBR.md`

**O que NÃO muda:** constituição, decisões tNNN, contratos Pydantic (D3), scanner de segredos (D14), migração do NotebookLM (D1), regras do item 5, comunidade, auditor e Drive. As regras são as mesmas. Muda **quem executa** (motor de workflow em vez de agentes Paperclip) e **a ordem**.

| Plano atual | Mudança proposta [PROPOSTA] |
|---|---|
| §0 "org Paperclip PQBR nova" | A espinha passa a ser código + Temporal. A org Paperclip vira **opcional e posterior** (Fase 11b), só com agentes LLM |
| — | **Nova Fase 0.5: ADR + spike de 1 dia.** `docs/sdd/adr-001-orquestrador.md`. Subir o Temporal só com Postgres no `pc` (compose isolado), medir RAM/CPU com a carga real e rodar um `EpisodioWorkflow` de brinquedo com timer, sinal de aprovação via Telegram e uma Activity falhando. **Aceite:** RAM total < limite combinado, retomada após `kill -9` no worker e após reboot, aprovação por sinal. **Se reprovar: DBOS** com o mesmo teste. **Portão G0.5 (José):** escolhe o motor |
| §1 elenco de 12 agentes | Render, publisher, preflight e backup viram **Activities** (já eram "sem LLM"). Ideador, roteirista e SEO viram **workflows que chamam o NotebookLM** (eles já só orquestravam). Agentes LLM que restam: analista, comunidade (resumo), compliance (análise), assistente `pqbr` (Hermes) e, se o José quiser, o director |
| Fases 1–2 (pacote `company/` + import) | **Adiadas** para depois da Fase 9. Encolhem para 3–5 agentes. H-SDD1 (`--yolo`) perde urgência porque nenhum agente LLM executa efeito. H-SDD3 (adapter `process`) vira a ponte opcional Paperclip → Temporal |
| Fase 3 (D3 + D14) | Acrescentar **`canal_id` em todo o schema**, `config/canais/pqbr.yaml` e a tabela de orçamento por canal. Migração `0001_base.sql` já multi-canal |
| Fase 4 (D1 NotebookLM) | Igual. O serviço NotebookLM vira Activity na fila `notebooklm` com concorrência 1 |
| Fase 5 (D5 grade/barreiras/estados, timers systemd) | Máquina de estados = `EpisodioWorkflow`; **timers systemd → Temporal Schedules**; vigia de prazo = timer durável. A grade continua sendo código a partir da data. R10 por canal |
| Fase 6 (D6 resiliência) | Escada 30 s → 2 min → 8 min = `RetryPolicy` + lógica no workflow; `NETWORK_WAITING` = Activity de espera de rede sem gastar tentativa. **Fila local t242**: o estado vive no Postgres local do Temporal, e o Supabase recebe via outbox (OK do José). O guardião de sessão vira Schedule |
| Fase 7 (D11 + D4 auditor) | Igual. O `decide()` usa Pydantic AI com a durabilidade do motor escolhido |
| Fase 8 (D7 + D13 publicação/Drive) | `PublicacaoWorkflow` com ID idempotente; agendamento pelo Camofox na fila `camofox` (concorrência 1); `Item5Workflow` |
| Fase 9 (D12 monitores) | Schedules; custo por canal no relatório; UI do Temporal como painel técnico |
| Fase 10 (D8–D10 comunidade) | Workflows por canal; kill switch como sinal; sombra de 3 dias igual |
| — | **Nova Fase 11b (opcional): Paperclip por cima.** Agentes LLM que leem o Supabase e propõem; ponte via `process` só para consultar ou sinalizar o Temporal; heartbeats desligados até a correção da #6596 ou o teste de queda de internet |
| Fase 12 (liberação) | "Despausar agentes" passa a ser **ativar os Schedules do canal**, um a um |
| §4 hipóteses | Novas: **H-ORQ1** RAM do `pc` comporta o motor escolhido; **H-ORQ2** Postgres local dedicado + backup; **H-ORQ3** versão do Paperclip/adapter Hermes inclui a correção da #3833 (explica ou não a deriva da COR-1) |
| §5 pendências | Novas para o José: **motor (Temporal × DBOS)** depois do spike; **manter ou não o Paperclip**; **t242 via histórico do motor + outbox**; política de cota da API para vários canais (um projeto GCP ou auditoria) |
| §6 riscos | Acrescentar: determinismo/versionamento; RAM/swap; tempestade de recuperação do Paperclip; "inauthentic content" ao escalar canais |

**Ordem resumida:** G0 (constituição) → **G0.5 (spike e escolha do motor)** → Fase 3 (schemas multi-canal) ∥ Fase 4 (NotebookLM) → Fase 5 (EpisodioWorkflow + Schedules) → 6 → 7 → 8 → 9 → 10 → 11 (2 personagens) → **11b (Paperclip opcional)** → 12.

---

## 10. Fontes principais
- Temporal: [versionamento Python](https://docs.temporal.io/develop/python/versioning) · [patching](https://docs.temporal.io/patching) · [sandbox](https://docs.temporal.io/develop/python/best-practices/python-sdk-sandbox) · [schedules](https://docs.temporal.io/schedule) · [aprovação](https://docs.temporal.io/design-patterns/approval) · [deploy](https://docs.temporal.io/self-hosted-guide/deployment) · [OpenAI Agents SDK](https://docs.temporal.io/develop/python/integrations/openai-agents) · [Agent Harness](https://temporal.io/blog/temporal-agent-harness-durable-agent-infrastructure) · [Railway sem ES](https://railway.com/deploy/temporal-or-durable-workflows-no-elastic.md) · [RamNode](https://ramnode.com/guides/temporal) · [HN](https://news.ycombinator.com/item?id=48326802)
- DBOS: [vs Temporal](https://docs.dbos.dev/explanations/comparing-temporal.md) · [Supabase](https://docs.dbos.dev/integrations/supabase) · [cron](https://docs.dbos.dev/python/tutorials/scheduled-workflows) · [comunicação](https://docs.dbos.dev/python/tutorials/workflow-communication)
- Hatchet: [Lite](https://docs.hatchet.run/self-hosting/hatchet-lite) · [durable](https://docs.hatchet.run/durable-execution) · [concorrência](https://docs.hatchet.run/v1/concurrency)
- Inngest [self-host](https://www.inngest.com/docs/self-hosting) · Restate [get](https://docs.restate.dev/get-restate) · Prefect [compose](https://docs.prefect.io/v3/how-to-guides/self-hosted/docker-compose) · Windmill [self-host](https://www.windmill.dev/docs/advanced/self_host) · n8n [licença](https://docs.n8n.io/n8n-community-license/community-license/license-faq)
- Paperclip: [process adapter](https://docs.paperclip.ing/reference/adapters/process/) · [#3833](https://github.com/paperclipai/paperclip/issues/3833) · [PR #3850](https://github.com/paperclipai/paperclip/pull/3850) · [#6596](https://github.com/paperclipai/paperclip/issues/6596) · [ClawBlog](https://clawblog.com/reviews/paperclip) · [vibecoding review](https://vibecoding.app/blog/paperclip-review) · [Reddit](https://www.reddit.com/r/aisolobusinesses/comments/1s9gfma/is_paperclip_ai_actually_useful_or_just_another/) · [Reddit OpenClaw](https://www.reddit.com/r/openclaw/comments/1sdgngk/opinion_from_those_who_have_used_both_openclaw/)
- Harnesses: [DSH tools](https://deepseek-harness.github.io/deepseek-harness/en/reference/tool-catalog) · [dsh-agent-teams](https://github.com/liuyizhang671-design/dsh-agent-teams) · [Pydantic AI durable](https://pydantic.dev/docs/ai/durable-execution/) · [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) · [Claude Agent SDK hosting](https://code.claude.com/docs/en/agent-sdk/hosting)
- YouTube: [cota](https://developers.google.com/youtube/v3/determine_quota_cost) · [auditoria](https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits) · [monetização](https://support.google.com/youtube/answer/1311392?hl=en) · [TechCrunch](https://techcrunch.com/2025/07/09/youtube-prepares-crackdown-on-mass-produced-and-repetitive-videos-as-concern-over-ai-slop-grows/)

**Limites desta pesquisa:** as medições de RAM do Temporal são de terceiros (Railway, RamNode), não do `pc`. A comparação DBOS × Temporal citada é do próprio fornecedor (DBOS). Os relatos do Reddit e do HN são individuais. Não li o changelog do Paperclip instalado, então a H-ORQ3 está aberta.
