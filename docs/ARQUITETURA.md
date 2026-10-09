# ARQUITETURA da PQBR

> Autoridade: abaixo de `docs/REGRAS.md` e acima de `docs/PLANO.md`. Este arquivo diz **como** as regras são executadas hoje; ele se adapta às regras, nunca o contrário (t285). Em conflito, vale o REGRAS.md.
> Não consultar `docs/arquivo/`, `docs/pesquisas/` nem `docs/DECISOES-LOG.md` sem aprovação explícita do José (t287).
> Legenda: [APROVADO] · [VERIFICADO] · [HIPÓTESE] · [PROPOSTA] (sugestão ainda sem aprovação) · EM CONSTRUÇÃO — aguardando José.

---

## 1. Decisões de arquitetura (ADRs)

### ADR-001: motor de orquestração (Temporal primeiro, DBOS como plano B)
- **Decisão [APROVADO t283]:** a espinha do fluxo é **código + motor de workflow durável**, numa arquitetura híbrida pensada para vários canais. O **Temporal** é testado primeiro; o **DBOS** é o plano B.
- **Como decidir [PROPOSTA, PLANO Fase 0.5]:** spike de 1 dia. Temporal self-hosted só com Postgres local e dedicado no `pc` (sem Elasticsearch; separado do `mp32-postgres`; ~0,9 GiB estimado) e um `EpisodioWorkflow` de brinquedo com timer, sinal de aprovação e uma Activity que falha. Aceite: RAM dentro do limite combinado; retomada após `kill -9` no worker e após reboot; aprovação por sinal. Se reprovar, repetir o teste com o DBOS. O José escolhe no portão G0.5.
- **Forma-alvo [PROPOSTA]:**
  - Schedules por canal: grade da madrugada, lote da manhã, guardião de sessão, leitura de comentários, limpeza do Drive, relatório diário, monitores. Eles substituem os timers do SO; a **regra** de horários fixos + vigia de prazo (REGRAS §3) não muda.
  - `EpisodioWorkflow(canal, ep)`: pauta → NotebookLM → FFmpeg → auditor → upload privado → agendar → confirmar.
  - `Item5Workflow`: qualquer problema → privado na hora + Telegram (REGRAS §16).
  - Workers Python (`src/pqbr`) com filas por recurso: `notebooklm` (concorrência 1), `camofox` (concorrência 1), `render`, `default`.
  - Activities sem LLM: NotebookLM CLI 0.8.4, FFmpeg, juiz Gemini, `decide()` (Jev via Pydantic), YouTube API, Drive, Supabase.
  - Multi-canal: `canal_id` em todo o schema, `config/canais/pqbr.yaml`, orçamento por canal.
  - R10 por canal: [PROPOSTA]; hoje a regra vale para o canal Porquê BR.
- **Dois bancos com papéis distintos [t324–t326]:**
  - **Postgres próprio do Temporal:** só estado dos workflows. **Nunca é consultado diretamente** por agentes, painel ou relatórios.
  - **Supabase:** dados de negócio: temas/R10, vídeos e códigos PQBR-EP, comentários, métricas, relatórios, base do painel e do analista. Mantido [recomendação aprovada; confirmar no teste de 1 dia do Temporal].
- **Supabase fora [t324–t326]:** retentativas duráveis do Temporal + **outbox** para o Supabase na volta. Substitui a fila em arquivo da t242 (confirmar no teste). A regra (REGRAS §18) não muda.
- **Cautelas:** RAM e swap do `pc` (H-ORQ1); determinismo e versionamento dos workflows; `NUM_HISTORY_SHARDS` escolhido uma vez; backup diário do Postgres do motor (sem segredos); nenhum agente autônomo dentro de Activity com efeito colateral.

### ADR-002: Paperclip como painel desde o início
- **Decisão [APROVADO t282]:** o Paperclip é **painel** desde o começo. Mostra estado, issues e verificações; **não é dono do fluxo** e nenhum agente dele executa efeito.
- Abre só dentro da tailnet, por HTTPS; a porta 443 fica livre [VERIFICADO/APROVADO t280].
- Verificação de fichas: status/issue no painel e botões no Telegram, sincronizados pela mesma tabela (REGRAS §6).
- Riscos conhecidos: o adapter `hermes_local` força `--yolo` (PR #3850); recovery storm sem internet (issue #6596); injeção do AGENTS.md (issue #3833, corrigida pela PR #8543). Por isso: heartbeats desligados e nenhum agente com efeito.
- **EM CONSTRUÇÃO — aguardando José:** como o painel é alimentado (pacote `company/` com agentes pausados vs. só issues/projetos gravados por código) e se a pasta `company/` continua. **Será demonstrado no teste de 1 dia do Temporal** (Fase 0.5) [t324–t326]. Até lá, `company/README.md` e `tasks/README.md` ficam como estão.

### ADR-003: Telegram com o Hermes `pqbr`
- **Decisão [APROVADO t281]:** o Telegram fica com o perfil Hermes `pqbr`; o @pqbr-assistente roda lá. Ele só consulta, roteia e responde, lendo o banco (REGRAS §2).
- Perfil já criado [VERIFICADO 09/10]: não herda `--yolo` nem sudo sem senha; segredos só no `.env` do perfil. Rota: tópico do grupo do José, pelo roteador de bot único (o perfil não tem token próprio). IDs de chat e tópico ficam só na config local, nunca no git.
- Uso no servidor: `hermes -p pqbr chat` (interativo) ou `hermes -p pqbr chat --query-file - --oneshot -Q` (sem interação).
- Aprovações do José (botões e dupla confirmação) chegam ao motor como **sinal** [PROPOSTA]; a ponte exata é definida na Fase 0.5.

### ADR-004: tickets de manutenção agnósticos + memória de código no Hindsight
- **Decisão [APROVADO t286]:** na produção, qualquer agente de desenvolvimento pode pegar um ticket de manutenção, acessar o código e corrigir. O conhecimento vem das **memórias de código no Hindsight**, sem segredos (REGRAS §17).
- Os agentes especializados da PQBR (auditor, compliance, comunidade, guardião, analista) **pré-estruturam cada ticket**: localização (arquivo/módulo/workflow), falha observada (evidência, horário, ID do episódio) e correções sugeridas.
- Fluxo: o ticket é aberto pelo código ou pelo assistente, já pré-estruturado → **1ª aprovação do José na abertura** (ele pode pedir correções no próprio ticket) → um agente de dev trabalha em branch/worktree → testes → **2ª aprovação do José no merge** [t324–t326].
- Memórias de código no **bank Hindsight único da organização** [t324–t326].
- Durante a construção não há tickets: mudanças são tarefas de desenvolvimento do PLANO (REGRAS §24).

### ADR-005: org core-eng abortada
- **Decisão [APROVADO t284]:** a core-eng está abortada por enquanto e a saída do CTO (COR-1) não é usada. Ela foi arquivada fora do git (Drive `PQBR/_arquivo-docs-2026-10-09/cor1-cto-2026-10-09.tar.gz`). Onde os documentos antigos dizem "core-eng", leia "agente de desenvolvimento".

---

## 2. Componentes

| Componente | Papel | Status |
|---|---|---|
| **NotebookLM** (notebooklm-py) | Primário para ideação, roteiro, SEO, pesquisa e vídeo. Caderno **efêmero por episódio**; nunca o raiz. Adicionar o roteiro como fonte antes de gerar; em timeout, listar artefatos e não regerar; nunca `ask --new`. | [APROVADO] / hábitos [VERIFICADO no `rede`] |
| | Instalação exclusiva da PQBR (D1): venv com 0.8.4 fixada, `NOTEBOOKLM_HOME` próprio, perfil `pqbr`, serviço único dono da sessão. Hoje há uma instalação global 0.8.2 compartilhada com o MP32. | [APROVADO em princípio] / estado atual [VERIFICADO] |
| | Duração de 15 s a 3 min com alvo de ~50 s. Verticais até ~67 s já saíram bem; até 180 s ainda não testado (H5). Com 2 personagens, o Short ignorou as imagens de elenco (5 de 5); com 1 funcionou. | [VERIFICADO até ~67 s] |
| **Gemini web** | Reserva do NotebookLM e juiz visual do auditor (3.8 Flash, modo normal; o "Flash Estendido" recusa as pranchas). Produção via Camofox vs. Gemini API: H10. | [APROVADO] / [HIPÓTESE] |
| **Jev** (TypeSafe) | `decide()` com provedor trocável; só decisão estruturada (REGRAS §7). Fallback: Jev via OpenRouter → modelo OpenAI (H7). | [APROVADO] |
| **Camofox** (camofox-browser sobre Camoufox, perfil `porquebr`) | Toda automação de navegador; único dono do login do Studio; reserva da publicação e agendamento enquanto H1 não fecha; corações. Telemetria de crash vem ligada: verificar e desligar (H9). | [APROVADO] |
| | Dicas do Studio [VERIFICADO no `rede`]: ir direto a `/videos/upload?d=ud`; `execCommand('insertText')`; COPPA "não é para crianças"; paginar 30 por vez; desafio de passkey → humano; upload só de `~/.camofox/uploads/`. | |
| **YouTube Data API** | Grade, comentários (`commentThreads.list` = 1 unidade), respostas (`comments.insert` = 50), retenção (`setModerationStatus` = 50), `videos.update` = 50, upload (`videos.insert`). Cota 10.000/dia, reset à meia-noite do Pacífico (~04:00–05:00 em Fortaleza); `search.list` e `videos.insert` com balde próprio de 100/dia. Sem endpoint de coração. | [VERIFICADO na doc] |
| **YouTube Analytics API** | Coleta diária do analista (OAuth só leitura; app do GCP em produção, uso interno). | [APROVADO] / números [HIPÓTESE] |
| **Motor de workflow** (Temporal / DBOS) | Estado durável dos fluxos, Schedules, retentativas, sinais (ADR-001). Postgres próprio, só estado de workflow, nunca consultado diretamente. | [APROVADO t283] / escolha no G0.5 |
| **Supabase** | Dados de negócio (base do painel e do analista; recebe por outbox): grade, temas (R10), episódios, `visual_assets`/`episode_assets`, comentários, ações (motivo/quem/quando), consumo, kill switch, relatórios. Plano Pro não confirmado (H13). | [APROVADO] |
| **Google Drive** | Armazenamento definitivo, estrutura t267 (REGRAS §21). | [APROVADO] |
| **Hermes `pqbr`** | @pqbr-assistente no Telegram (ADR-003). | [APROVADO t281] |
| **Paperclip** | Painel (ADR-002). | [APROVADO t282] |
| **Hindsight** (local, backup diário) | Aprendizados (analista, lições do item 5) e memórias de código para os agentes de dev (ADR-004), num **bank único por organização**. Sem segredos nem PII. | [APROVADO t324–t326] |
| **Whisper / FFmpeg** | Transcrição com tempos (o Whisper ouve "Porquê BR" como "por KBR"; aceitar variantes). Pós: corte do end card só se detectado + logo com zoom suave curto. | [VERIFICADO] |

## 3. Papéis (ex-"agentes")

**Padrão dos agentes pensantes [APROVADO t324–t326]:** uma rotina fixa executa tudo; @prod-director, @prod-analista e @prod-comunidade só observam e propõem mudanças como saída estruturada validada por Pydantic v2; nada se aplica sem a aprovação do José.

Princípio [APROVADO t184]: ideação, roteiro, SEO e pesquisa ficam com o NotebookLM; os papéis orquestram, extraem por código, validam com Pydantic e conferem com o Jev. Com o motor de workflow, os papéis sem LLM viram **Activities/workflows** e só alguns continuam como agentes LLM [PROPOSTA, PESQ-orquestração §9].

| Papel | Natureza [PROPOSTA salvo indicação] | Faz | Não faz |
|---|---|---|---|
| @prod-director | Rotina fixa executa; agente observa e propõe (Pydantic v2), aplica só com aprovação do José [APROVADO t324–t326] | Cadência, rotinas, parâmetros operacionais; recebe propostas do analista e do assistente; limpeza noturna do Drive por script (t270) | Não altera regra canônica; não aplica mudança sem o José; não exclui |
| @prod-ideador | Workflow que chama o NotebookLM | Entrega coleta e fontes ao caderno de tendências; recebe os temas filtrados | Não escolhe tema sem as 3 barreiras |
| @prod-roteirista | Workflow que chama o NotebookLM | Roteiro no NotebookLM; lista as entidades da cena; valida `RoteiroShort` | Não redige fora do NotebookLM/Gemini; sem nomes |
| @prod-render | Activity (sem LLM) | Geração no NotebookLM + pós FFmpeg | Não julga qualidade |
| @prod-auditor | Código decide; Gemini sim/não; Jev nas checagens de texto | Auditoria pré-publicação + item de conformidade | LLM não dá gravidade nem escreve laudo |
| @prod-seo | Workflow que chama o NotebookLM | Título, descrição, código PQBR-EPxxxx | Não pede comentário (t263) |
| @prod-publisher | Activity (sem LLM) | `videos.insert` com agendamento; confere ID e código; executa o item 5 em código | Não decide sozinho; não reenvia sem consultar; não exclui; não volta vídeo a público |
| @prod-analista [APROVADO] | Coleta por rotina fixa; agente analisa e propõe (Pydantic v2), aplica só com aprovação do José [t324–t326] | Analytics API; análise semanal ou por anomalia; propostas ao director; Hindsight | Não muda parâmetro sozinho |
| @prod-compliance [APROVADO t198] | Coleta por código + Jev + análise | E-mail do canal, Studio só leitura, Data API; gravidade; HOLD; rascunho de recurso | Nunca recorre, apaga ou altera sem dupla confirmação |
| @prod-comunidade [APROVADO t245] | Rotina fixa + Jev executam; agente faz resumo e propõe (Pydantic v2), aplica só com aprovação do José [t324–t326] | Lê, classifica, retém, responde pelo banco, corações, agrupa temas | Não torna vídeo privado (t250); não escreve texto livre |
| @pqbr-assistente [APROVADO] | LLM no Hermes `pqbr` (t281) | Consulta, roteia, responde pelo banco | Não executa mudanças |
| Agentes de dev | LLM (qualquer um) | Tickets de manutenção na produção; tarefas D na construção (ADR-004) | Não faz merge (só o José) |

Personas [APROVADO como fonte]: pt-BR, parafraseadas da Agency Agents (MIT). Comunidade: donchitos `community-manager`, `customer-service.md`, `developer-community-builder`, `feedback-synthesizer`. Compliance e assistente: **a definir**.

## 4. Skills

- **Do Hermes `rede`, viram skills internas (não persona):** `rotina-producao-porqu-br` (máquina de estados, deduplicação, COPPA, fuso UTC×Fortaleza, polling tolerante, "nunca escolher pelo mp4"), `durable-orchestration`, `gemini-web-video-auditor` (só como padrão; vetos visuais obsoletos pela t265), `ecossistema-ponte-multitenant`. Nome da skill nova do fluxo: `rotina-producao-porque-br` (07/10).
- **⚠ Antes de portar qualquer skill do `rede`:** ela destrava o GNOME Keyring com senha por comando (risco); cita CDP 9225 (banido); `produ-o-short-b1` prefere papercut e horário fixo das 19h30 (obsoletos).
- **Da comunidade (com commit fixado):** coreyhaines `copywriting`/`video`, kostja94 `youtube-seo`, supabase/agent-skills, notebooklm-py (oficial), digitalsamba `ffmpeg`, `building-pydantic-ai-agents`. **Não usar:** superpowers/* nem `claude-office-skills/youtube-automation` (aviso do Snyk).
- **Escrever do zero:** `skill-short-form-copy`, `skill-youtube-metadata-seo`, `skill-research-curation`, `pqbr-comentarios-triagem`, `pqbr-comentarios-moderacao`, `pqbr-comentarios-temas`, `pqbr-guia-tom`.

## 5. Ambiente (nomes lógicos; valores reais só na config local)

- Servidor `pc` (casa, acessado pela tailnet). Repositório oficial em `/home/pc/Workspace/PQBR`, GitHub `jvmendesjr/PQBR` (privado, `main`) [VERIFICADO].
- Paperclip só dentro da tailnet, por HTTPS; 443 livre [VERIFICADO t280].
- Dependências globais [VERIFICADO 09/10]: Camofox (REST, saudável), Node, Python/uv, FFmpeg, Docker, gh, NotebookLM CLI 0.8.2 global, Hindsight. As dependências da PQBR são tarefas do PLANO.
- Endereços (IP/host da tailnet), IDs de chat/tópico do Telegram e segredos **não entram no git** (REGRAS §17).

## 6. Estrutura do repositório

- `docs/`: REGRAS, ARQUITETURA, PLANO, CONTRATO-EDITORIAL (rascunho), DECISOES-LOG, `pesquisas/`, `arquivo/` (os quatro últimos sob a t287).
- `src/pqbr/{schemas,pipeline,integrations,community,guardian,storage}`: código. [PROPOSTA] `src/pqbr/workflows/` depois da ADR-001.
- `db/migrations/` (schema do Supabase), `db/seeds/` (`temas-publicados.csv`: lista de temas já publicados, base da R10).
- `templates/` (relatórios, mensagens fixas, banco de frases), `config/` (só exemplos sem segredo), `tests/`, `scripts/`, `skills/`.
- `company/`, `tasks/`: pendentes da ADR-002.
- `runtime/`: temporário, fora do git.

## 7. Hipóteses

Nada que depende de uma hipótese é construído antes de ela virar VERIFICADO (REGRAS §14). Dono padrão: agente de dev da tarefa D correspondente.

| # | Hipótese | Dono | Critério de pronto |
|---|---|---|---|
| H1 | Auditoria do app do GCP para upload público pela API (t273). Até lá, vídeo sobe privado e o Camofox agenda pelo Studio. Inclui o custo real de cota. | dev | Auditoria concedida e 1 upload público de teste; até lá, fluxo "privado + agendamento pelo Camofox" testado |
| H2 | Agendamento via `publishAt` depois da auditoria | dev | 1 agendamento de teste confirmado pela API |
| H3 | `comments.insert` (`youtube.force-ssl`) funciona sem auditoria | dev | 1 resposta real de teste publicada e conferida |
| H4 | Leitura do canal inteiro via `allThreadsRelatedToChannelId` inclui os Shorts; leitura de `heldForReview`/`likelySpam` com o escopo previsto | dev | Comparar com a leitura por vídeo |
| H5 | NotebookLM gera Short vertical bom até 180 s | dev | Gerações de ~90 s e ~170 s verificadas |
| H6 | `notebooklm usage --json` funciona na conta (medição ativa) | dev | Saída válida gravada; senão, contagem própria |
| H7 | Nome do modelo OpenAI do fallback e paridade com o esquema do Jev | dev | Conjunto de avaliação roda com o mesmo formato |
| H8 | Preço e saldo do Jev; média de gasto | dev | Média dos primeiros dias no relatório |
| H9 | Causa das quedas do Studio (cookies do Chrome vs. identidade do aparelho do Camofox); telemetria do camofox-browser desligada | dev | Sessão estável por N dias com a escada t272, sem cópia de cookies |
| H10 | Juiz visual em produção: Gemini web automatizado via Camofox vs. Gemini API (a chave é decisão do José) | dev + José | Teste comparativo (RUNBOOK) + decisão |
| H11 | Termos de uso comercial do NotebookLM/Gemini; selo de IA desnecessário para stickman | dev (registro) + José | Leitura dos termos registrada; compliance acompanha |
| H12 | Métricas do canal (30 vs. 46 Shorts; bases de retenção diferentes) | @prod-analista/dev | Números fixados pela Analytics API |
| H13 | Supabase Pro ativo; local do schema Hindsight; `hermes_local` + Hindsight num heartbeat real | dev | Confirmação pelo MCP + 1 heartbeat real |
| H14 | App do GCP em produção (uso interno) sem expiração do token | dev | Token válido além de 7 dias |
| H15 | Limites do Pro do NotebookLM (5 h/semanal; 20 vídeos/dia) | dev | Monitor de consumo da 1ª semana |
| H16 | Corações pelo Camofox (até 10/dia) sem desafio de login | dev | 3 dias de sombra sem incidente de sessão |
| H-ORQ1 | A RAM do `pc` comporta o motor escolhido (o `pc` já usa swap) | dev | Medição no spike da Fase 0.5 |
| H-ORQ2 | Postgres local dedicado ao motor + backup diário | dev | Restauração testada |
| H-ORQ3 | A versão do Paperclip/adapter Hermes inclui a correção da #3833 | dev | Versão conferida |
| H-SDD1 | O `hermes_local` roda sem `--yolo` (ou há adapter alternativo) | dev | Teste; perde urgência se nenhum agente do painel executar efeito |
| H-SDD2 | Sintaxe do `paperclipai company import … --dry-run` e criação de agentes pausados | dev | Só se a ADR-002 usar pacote |
| H-SDD3 | O adapter `process` serve como ponte opcional painel → motor | dev | Só se a ADR-002 usar pacote |
