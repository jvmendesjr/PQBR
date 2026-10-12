# ARQUITETURA da PQBR

> Autoridade: abaixo de `docs/REGRAS.md` e `docs/SPEC.md`; acima de `docs/TESTES.md`, `docs/ROADMAP.md` e `docs/PLANO.md`. Requisitos citados como RF/RNF (SPEC). Este arquivo diz **como** as regras são executadas hoje; ele se adapta às regras, nunca o contrário (t285). Em conflito, vale o REGRAS.md.
> Não consultar `docs/arquivo/`, `docs/pesquisas/` nem `docs/DECISOES-LOG.md` sem aprovação explícita do José (t287).
> Legenda: [APROVADO] · [VERIFICADO] · [HIPÓTESE] · [PROPOSTA] (sugestão ainda sem aprovação) · EM CONSTRUÇÃO — aguardando José.

---

## 1. Decisões de arquitetura (ADRs)

### ADR-001: motor de orquestração (Temporal primeiro, DBOS como plano B)
- **Resultado [APROVADO t374, 10/10]:** o **Temporal** foi aprovado no teste (TZ-01..TZ-04 e TZ-07; soak de 122 execuções em ~20 h, sem falha, perda ou duplicata, pico de 340 MiB). **Motor = Temporal; DBOS dispensado.**
- **Decisão [APROVADO t283]:** a espinha do fluxo é **código + motor de workflow durável**, numa arquitetura híbrida pensada para vários canais. O **Temporal** é testado primeiro; o **DBOS** é o plano B.
- **Como decidir [PROPOSTA, ROADMAP F05-01..F05-07; TESTES TZ-01..TZ-07]:** spike de 1 dia. Temporal self-hosted só com Postgres local e dedicado no `pc` (sem Elasticsearch; separado do `mp32-postgres`; ~0,9 GiB estimado) e um `EpisodioWorkflow` de brinquedo com timer, sinal de aprovação e uma Activity que falha. Aceite: RAM dentro do limite combinado; retomada após `kill -9` no worker e após reboot; aprovação por sinal. Se reprovar, repetir o teste com o DBOS. O José escolhe no portão G0.5.
- **Forma-alvo [PROPOSTA]:**
  - Schedules: grade da madrugada, lote da manhã, guardião de sessão, leitura de comentários, limpeza do Drive, relatório diário, monitores. Eles substituem os timers do SO; a **regra** de horários fixos + vigia de prazo (REGRAS §3) não muda.
  - `EpisodioWorkflow(ep)`: pauta → NotebookLM → FFmpeg → auditor → upload privado → agendar → confirmar.
  - `Item5Workflow`: qualquer problema → privado na hora + Telegram (REGRAS §16).
  - Workers Python (`src/pqbr`) com filas por recurso: `notebooklm` (concorrência 1), `camofox` (concorrência 1), `render`, `default`.
  - Activities sem LLM: NotebookLM CLI 0.8.4, FFmpeg, juiz Gemini, `decide()` (Jev via Pydantic), YouTube API, Drive, banco do app.
  - **Escopo [t327]:** só o canal Porquê BR. Multi-canal (`canal_id`, config e orçamento por canal, R10 por canal) fica **adiado** para depois dos aprendizados.
- **Dois bancos com papéis distintos [t324–t326]:**
  - **Postgres próprio do Temporal:** só estado dos workflows. **Nunca é consultado diretamente** por agentes, painel ou relatórios.
  - **Banco do app (Postgres local, t343):** dados de negócio: temas/R10, vídeos e códigos PQBR-EP, comentários, métricas, relatórios, base do painel e do analista. Mantido [recomendação aprovada; confirmar no teste de 1 dia do Temporal].
- **Banco do app fora [t324–t326]:** retentativas duráveis do Temporal + **outbox** para o banco do app na volta. Substitui a fila em arquivo da t242 (confirmar no teste). A regra (REGRAS §18) não muda.
- **Teto de RAM [APROVADO t329]:** Temporal + Postgres dedicado ≤ 1,5 GB no `pc`; acima disso no TZ-01, considerar o DBOS (plano B).
- **Cautelas:** RAM e swap do `pc` (H-ORQ1); determinismo e versionamento dos workflows; `NUM_HISTORY_SHARDS` escolhido uma vez; backup diário do Postgres do motor (sem segredos); nenhum agente autônomo dentro de Activity com efeito colateral.

### ADR-002: Paperclip = camada de agentes + painel, ligado ao Temporal
- **Decisão [APROVADO t282, t327]:** o **Temporal** executa o fluxo determinístico; o **Paperclip** é a **camada de agentes e o painel**. **Os agentes vivem no Paperclip** (org PQBR, pacote `company/` no formato agentcompanies/v1). Pelo padrão dos agentes pensantes (t324–t326), eles observam e propõem (saída Pydantic v2), e nada se aplica sem o José; o Paperclip **não é dono do fluxo**.
- Abre só dentro da tailnet, por HTTPS; a porta 443 fica livre [VERIFICADO/APROVADO t280].
- Verificação de fichas: status/issue no painel e botões no Telegram, sincronizados pela mesma tabela (REGRAS §6).
- **Ligação Temporal ↔ Paperclip [PROPOSTA, a validar na Fase 0.5]:** o Temporal grava eventos e estado de negócio no banco do app (outbox) e abre/atualiza issues no Paperclip; os agentes leem banco do app/issues e devolvem propostas estruturadas; a aprovação do José vira **sinal** para o Temporal. Nunca leem o Postgres do Temporal.
- Riscos conhecidos: o adapter `hermes_local` força `--yolo` (PR #3850), mas o perfil `pqbr` não pode herdar `--yolo` (REGRAS §23): resolver H-SDD1 antes de ligar qualquer agente Hermes; recovery storm sem internet (issue #6596); injeção do AGENTS.md (issue #3833, corrigida pela PR #8543). Heartbeats desligados até a Fase 0.5 provar a ligação.
- `company/` continua (pacote dos agentes). `tasks/`: as rotinas viram Schedules do Temporal, então `tasks/` é candidato a exclusão depois da Fase 0.5 [PROPOSTA].

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
- Durante a construção não há tickets: mudanças são tarefas do ROADMAP (REGRAS §24).

### ADR-005: org core-eng abortada
- **Decisão [APROVADO t284]:** a core-eng está abortada por enquanto e a saída do CTO (COR-1) não é usada. Ela foi arquivada fora do git (Drive `PQBR/_arquivo-docs-2026-10-09/cor1-cto-2026-10-09.tar.gz`). Onde os documentos antigos dizem "core-eng", leia "agente de desenvolvimento".

---

### ADR-006: construção no Paperclip pelo jr; agentes via 9router [APROVADO t390–t394]
- Sem entrega à core-eng; o jr monta a empresa PQBR no Paperclip (t394). 14 agentes; desenho em `AGENTES.md`.
- Adapters: `process` (script do kit → 9router → Pydantic) e `opencode_local` (9router como provider OpenAI-compatível; ferramentas nativas negadas, salvo os Devs em container). Plano B: `http`. `hermes_local` não é usado. O único perfil Hermes é o `pqbr` (ADR-003).
- Dev Revisor usa outro modelo do 9router, de família diferente do Corretor.

### ADR-007: exceção controlada do `--yolo` / auto-aprovação de ferramentas [APROVADO t390, renumerada t395]
- `--yolo` (ou o equivalente do OpenCode, auto-aprovar permissões) só quando necessário. Perfis mínimos sem terminal, arquivos ou sudo; exceção só para o Dev Corretor e o Dev Revisor, em container isolado (worktree, sem rede de produção nem segredos; o Revisor não escreve no repo principal). O `pqbr` nunca usa `--yolo`. Com a ADR-006, o H-SDD1 deixa de bloquear.

### ADR-008: Camofox PQBR 24/7 com reautenticação autônoma [APROVADO t395]
- `pqbr-camofox` sempre ligado, com a sessão permanente na mesma tela; reinicia só se cair (`Restart=always` + guardião). A sessão caiu: renovar → sincronizar cookies do Chrome → outro caminho; log + Telegram em cada passo; o José só no fim (noVNC/2FA).

## 2. Componentes

| Componente | Papel | Status |
|---|---|---|
| **NotebookLM** (notebooklm-py) | Primário para ideação, roteiro, SEO, pesquisa e vídeo. Caderno **efêmero por episódio**; nunca o raiz. Adicionar o roteiro como fonte antes de gerar; em timeout, listar artefatos e não regerar; nunca `ask --new`. | [APROVADO] / hábitos [VERIFICADO no `rede`] |
| | Instalação exclusiva da PQBR (D1): venv com 0.8.4 fixada, `NOTEBOOKLM_HOME` próprio, perfil `pqbr`, serviço único dono da sessão. Hoje há uma instalação global 0.8.2 compartilhada com o MP32. | [APROVADO em princípio] / estado atual [VERIFICADO] |
| | Duração de 15 s a 3 min com alvo de ~50 s. Verticais até ~67 s já saíram bem; até 180 s ainda não testado (H5). Com 2 personagens, o Short ignorou as imagens de elenco (5 de 5); com 1 funcionou. | [VERIFICADO até ~67 s] |
| **Gemini web** | Reserva do NotebookLM e **juiz visual** do auditor (3.8 Flash, modo normal; o "Flash Estendido" recusa as pranchas), via Camofox. **Sem Gemini API** [t327]. | [APROVADO] |
| **Jev** (TypeSafe) | `decide()` com provedor trocável; só decisão estruturada (REGRAS §7). Fallback: Jev via OpenRouter → modelo OpenAI (H7). | [APROVADO] |
| **Camofox** (camofox-browser sobre Camoufox, perfil `porquebr`) | Toda automação de navegador; único dono do login do Studio; reserva da publicação e agendamento enquanto H1 não fecha; corações. Telemetria de crash vem ligada: verificar e desligar (H9). | [APROVADO] |
| | Dicas do Studio [VERIFICADO no `rede`]: ir direto a `/videos/upload?d=ud`; `execCommand('insertText')`; COPPA "não é para crianças"; paginar 30 por vez; desafio de passkey → humano; upload só de `~/.camofox/uploads/`. | |
| **YouTube Data API** | Grade, comentários (`commentThreads.list` = 1 unidade), respostas (`comments.insert` = 50), retenção (`setModerationStatus` = 50), `videos.update` = 50, upload (`videos.insert`). Cota 10.000/dia, reset à meia-noite do Pacífico (~04:00–05:00 em Fortaleza); `search.list` e `videos.insert` com balde próprio de 100/dia. Sem endpoint de coração. | [VERIFICADO na doc] |
| **YouTube Analytics API** | Coleta diária do analista (OAuth só leitura; app do GCP em produção, uso interno). | [APROVADO] / números [HIPÓTESE] |
| **Motor de workflow** (Temporal / DBOS) | Estado durável dos fluxos, Schedules, retentativas, sinais (ADR-001). Postgres próprio, só estado de workflow, nunca consultado diretamente. | [APROVADO t283] / escolha no G0.5 |
| **Banco do app** (Postgres 17 local, `infra/pqbr-db`) | Dados de negócio (base do painel e do analista; recebe por outbox): grade, temas (R10), episódios, `visual_assets`/`episode_assets`, comentários, ações (motivo/quem/quando), consumo, kill switch, relatórios. Plano Pro não confirmado (H13). | [APROVADO] |
| **Google Drive** | Armazenamento definitivo, estrutura t267 (REGRAS §21). | [APROVADO] |
| **Hermes `pqbr`** | @pqbr-assistente no Telegram (ADR-003). | [APROVADO t281] |
| **Paperclip** | Camada de agentes + painel, ligado ao Temporal (ADR-002). | [APROVADO t282, t327] |
| **Hindsight** (local, armazenamento próprio: Postgres embutido pg0; t349–t350) | Aprendizados (analista, lições do item 5) e memórias de código para os agentes de dev (ADR-004), num **bank único por organização**. Sem segredos nem PII. | [APROVADO t324–t326] |
| **Whisper / FFmpeg** | Transcrição com tempos (o Whisper ouve "Porquê BR" como "por KBR"; aceitar variantes). Pós: corte do end card só se detectado + logo com zoom suave curto. | [VERIFICADO] |

### Camofox: estado e isolamento [VERIFICADO 09/10, t354]
- Hoje: um servidor compartilhado (`camofox-browser`, `*:9377`, **todas as interfaces, sem chave**), um processo para 14 perfis em `~/.camofox/profiles` (pastas pelo hash sha256 do `userId`). Usado por `rede` (`porquebr`), MP32 (`tutibom10`), Hermes `mp3`/`pet`/`gpu` e o keepalive do runway (conta pessoal). Sem trava entre projetos.
- **Feito em 10/10 (t375):** F4C-01..03 no ar: `pqbr-camofox` em 127.0.0.1:9387 com chave, Camoufox e pastas próprios, e worker da fila `camofox-pqbr` (concorrência 1). Ainda sem perfil logado: o login é a F4C-04, com o José.
- Alvo: instância da PQBR (`pqbr-camofox`, `127.0.0.1:9387`, chave, `/home/pc/.pqbr/camofox`, `MAX_SESSIONS=1`, `MemoryMax=900M`), acessada só pelas Activities da fila `camofox-pqbr` (concorrência 1). A fila `camofox` do §2 passa a ser essa. Passos no ROADMAP F4C; regra no REGRAS §11.

### Correção autônoma mediada pelo Temporal [t355; PROPOSTA]
- Quando um passo de script falha com erro corrigível (`SiteMudou`, `SaidaForaDoEsquema`, transitório após a escada), o workflow chama o filho `CorrecaoAutonomaWorkflow(ferramenta, sessao, passo, contexto)` na fila da ferramenta (`camofox-pqbr`, `notebooklm`, …), com concorrência 1 por sessão.
- **Etapas [t356]:** (1) **triagem pelo Jev** (`TriagemCorrecao`: corrigível / sensível / fora de escopo; ação sensível encerra como `Sensivel` sem chamar o agente); (2) **intervenção pelo agente com LLM** (Activity na fila da sessão, tentativas e tempo limitados); (3) **verificação pelo Jev** quando couber (o passo voltou a funcionar? a saída bate com o esquema? nada fora da allowlist foi feito?); (4) **log + aprendizado**: cada ação no banco do app pelo Temporal (outbox) e o aprendizado no bank Hindsight da PQBR, sanitizado; (5) **proposta de ajuste do script** (tarefa ou ticket) quando corrigiu.
- A Activity do agente recebe só as ferramentas daquela fila (o Camofox restrito à instância `pqbr-camofox` e a uma allowlist de ações: navegar, ler, clicar, digitar, colar, upload; sem login, cookies ou exclusão). O Jev entra nas decisões estruturadas. Cada ação vai para o registro (`pqbr.acoes`, `jsonb`; tabela própria só se faltar campo, EM CONSTRUÇÃO).
- Resultado: `Corrigido(passos, proposta_script)`, `Esgotado(tentativas)` ou `Sensivel(motivo)`. Corrigido retoma o workflow e abre a proposta de ajuste (tarefa ou ticket); os outros dois avisam o José. Quem executa é um agente com LLM (t356) **rodando no Paperclip** (t357); limites: 3 tentativas, 5–15 min sorteados no Camofox; na sessão do Camofox, antes de agir, confere conta e sessão (divergência = `Sensivel`). Consumo de cada chamada vai para `pqbr.consumo_modelos`. Modelo de cada agente: definido na F1 (REGRAS §3.1).

### Consumo por modelo [t357 h]
- Tabela `pqbr.consumo_modelos` (migração 0010): uma linha por chamada ou lote, com provedor, modelo, `tipo_acao` (ideação, roteiro, auditor visual/texto/desempate, triagem/classificação/decisão/verificação do Jev, correção autônoma, comunidade, compliance, analista, assistente, publicação, teste de resposta…), ferramenta, episódio, workflow/run/activity do Temporal, tentativa, chamadas, tokens (entrada, saída, cache, raciocínio), unidades não-token, duração, sucesso, classe do erro e custo estimado (micro-USD). Sem prompt, resposta ou dado pessoal. View `consumo_diario` (fuso de Fortaleza) alimenta o relatório diário. Sem teto: só monitoramento.

## 3. Papéis

> **SUPERADO em parte (t384–t395):** a equipe vigente e o mapa @prod-* → 14 agentes estão em `AGENTES.md` §11. O "só propõe, José aprova" foi relaxado (REGRAS §0).

> t363: o `pqbr` já fala com o Paperclip (empresa de teste) por chave de agente escopada; ver §10. A restrição de acesso ainda **não** está na configuração do perfil (incidente do teste, §10).

### @pqbr-assistente (Hermes `pqbr`) — especificação [t357]
- **Papel:** assistente do José; entende a alma do negócio (CONTRATO-EDITORIAL, REGRAS). **Não executa:** sabe pedir. Os agentes rodam no **Paperclip**, que é o sistema principal de jobs.
- **Capacidades:** (1) avisos pelo Telegram (allowlist, botões); (2) acionar agentes do Paperclip (abrir issue, comentar, acordar o responsável) e abrir tickets pré-estruturados; (3) orientar o José: qual agente, comando e caminho certos; (4) buscar arquivos, resultados e estados (banco do app com `pqbr_leitura`, relatórios, Drive só leitura); (5) pedir detalhes aos agentes especialistas; (6) consultar o Jev para esclarecer ou classificar.
- **Acesso restrito:** só esses toolsets; sem shell livre, sem escrita no banco, no Drive, no Studio, no repositório nem nas configurações do Paperclip; sem `--yolo` e sem sudo (§5, REGRAS §23). Ordem só do ID do José.
- **Persona:** séria e direta (t327). Rascunho do SOUL: `docs/hermes-pqbr/SOUL-rascunho.md` (instalar no perfil só com OK do José; `~/.hermes/profiles/pqbr` não foi alterado).
 (ex-"agentes")

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

Personas [APROVADO como fonte]: pt-BR, parafraseadas da Agency Agents (MIT). Comunidade: donchitos `community-manager`, `customer-service.md`, `developer-community-builder`, `feedback-synthesizer`. **Compliance e assistente: sérios e diretos, sem rodeios [t327].** Todos os agentes vivem no Paperclip (ADR-002); o assistente roda pelo Hermes `pqbr`.

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

- `docs/`: README, REGRAS, CONTRATO-EDITORIAL, SPEC, ARQUITETURA, AGENTES, TESTES, ROADMAP (com o PLANO), RASTREABILIDADE, DECISOES-LOG; `hermes-pqbr/` (config viva do perfil `pqbr`); `pesquisas/`, `arquivo/` (estes quatro sob a t287); `docs/sdd/` para relatórios de fase (ex.: ADR-001 do teste).
- `src/pqbr/{schemas,pipeline,integrations,community,guardian,storage}`: código. [PROPOSTA] `src/pqbr/workflows/` depois da ADR-001.
- `db/migrations/` (schema do banco do app), `db/seeds/` (`temas-publicados.csv`: lista de temas já publicados, base da R10).
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
| H10 | ~~Juiz visual: Gemini web × Gemini API~~ RESOLVIDO (t327): Gemini web via Camofox. Resta verificar a automação estável em produção | dev | Auditor rodando via Camofox por N dias |
| H11 | Termos de uso comercial do NotebookLM/Gemini; selo de IA desnecessário para stickman | dev (registro) + José | Leitura dos termos registrada; compliance acompanha |
| H12 | Métricas do canal (30 vs. 46 Shorts; bases de retenção diferentes) | @prod-analista/dev | Números fixados pela Analytics API |
| H13 | `hermes_local` + Hindsight num heartbeat real (armazenamento do Hindsight verificado em 09/10, §8; Supabase Pro superado por t343) | dev | Confirmação pelo MCP + 1 heartbeat real |
| H14 | App do GCP em produção (uso interno) sem expiração do token | dev | Token válido além de 7 dias |
| H15 | Limites do Pro do NotebookLM (5 h/semanal; 20 vídeos/dia) | dev | Monitor de consumo da 1ª semana |
| H16 | Corações pelo Camofox (até 10/dia) sem desafio de login | dev | 3 dias de sombra sem incidente de sessão |
| H-ORQ1 | A RAM do `pc` comporta o motor escolhido dentro do teto de 1,5 GB (t329; o `pc` já usa swap) | dev | Medição no spike da Fase 0.5 |
| H-ORQ2 | Postgres local dedicado ao motor + backup diário | dev | Restauração testada |
| H-ORQ3 | A versão do Paperclip/adapter Hermes inclui a correção da #3833 | dev | Versão conferida |
| H-SDD1 | O `hermes_local` roda sem `--yolo` (ou há adapter alternativo que respeite o perfil `pqbr`) | dev | Teste na Fase 0.5; **bloqueia ligar agentes Hermes no Paperclip** |
| H-SDD2 | Sintaxe do `paperclipai company import … --dry-run` e criação de agentes pausados | dev | Dry-run limpo |
| H-SDD3 | Ponte Temporal ↔ Paperclip (issues/eventos; adapter `process` se útil) | dev | Demonstrada na Fase 0.5 |

## 8. Modelo de dados (banco do app) [APROVADO t343; aplicado 09/10]

- **Banco [APROVADO t343]:** **Postgres 17 local** no `pc`, em `infra/pqbr-db/docker-compose.yml` (projeto `pqbr-db`).
  - Separado do Postgres do Temporal.
  - Porta só em `127.0.0.1:55433`; `pg_hba` sem `trust` no localhost.
  - Limite de 320 MB (sem swap).
  - Senhas geradas no servidor em `infra/pqbr-db/.env` (600, fora do git).
  - **[t412] Supabase não é usado.** Texto histórico: Supabase ficava como opção futura (o projeto Supabase dedicado custaria US$ 10/mês, t337–t338). O projeto Supabase `paperclip` não é usado nem tocado.
- **Esquema `pqbr`:** migrações `db/migrations/0001..0009` (aplicadas por `infra/pqbr-db/aplicar.sh`, registro em `public.pqbr_migracoes`), com rollback em `db/migrations/rollback/`.
  - Testes descartáveis: `db/test_migrations.sh`. Verificação do banco real: `infra/pqbr-db/verificar.sh`.
  - RLS ligado e forçado em todas as tabelas, com políticas só para os papéis abaixo.
  - `canal_id` em todas as tabelas de negócio.
- **Papéis (t341–t343):**
  - `pqbr_app`: escritor, usado só pelo worker do Temporal. Sem DELETE em ações, histórico de estados, auditorias e outbox.
  - `pqbr_leitura`: só-leitura, sem o texto bruto de comentário.
  - Nenhum dos dois é superusuário nem tem BYPASSRLS; sem CREATE em `public`.
  - **Agentes do Paperclip nunca escrevem no banco do app.** Eles propõem; o Temporal valida e aplica após a aprovação. Leitura de agente só pelo contexto do fluxo ou pelo `pqbr_leitura`. O Paperclip mantém o banco próprio.
- **Diretriz de arquitetura [APROVADO t346]:**
  - Modelo genérico **canal / plataforma / publicações**: `pqbr.plataformas`, `pqbr.canal_plataformas`, `pqbr.publicacoes` (uma por episódio por plataforma) e `plataforma_id` em comentários, respostas, métricas, ações, relatórios e compliance. Campos específicos de cada rede vão em jsonb (`detalhes`/`extra`).
  - **Rede nova = linhas novas, não tabelas novas.** Não construir funcionalidade ainda indefinida; isso evita tabelas duplicadas e refatorações complexas.
  - Escopo atual: só YouTube no catálogo. **Outras redes (TikTok, Kwai, Instagram, Facebook) = sugestão futura, fora do escopo atual** (t343–t344).
  - Reaproveitamento de conteúdo entre plataformas: **EM CONSTRUÇÃO — aguardando José** (t345). Sem esquema além do vínculo `episodios → publicacoes`.
- **Três armazenamentos separados [APROVADO t349–t350]:** cada um com backup e restauração independentes.
  - Banco do app: `pqbr-db`.
  - Postgres do Temporal: `pqbr-temporal`, só estado de workflow.
  - **Hindsight:** armazenamento próprio. Um único bank por organização (PQBR).
- **Hindsight [VERIFICADO 09/10, só leitura]:**
  - Serviço de usuário `hindsight-api` (Restart=always), que roda a partir de `~/Workspace/core-engineering/memory`. API em `127.0.0.1:8890` (`/health` ok).
  - Dashboard: serviço `hindsight-control-plane` na porta 9999 da tailnet.
  - Backend: **PostgreSQL 18.1 embutido (pg0)**.
    - Dados em `~/.pg0/instances/hindsight/data` (~68 MB), porta `127.0.0.1:5432`, banco e usuário `hindsight`.
    - Credenciais no `instance.json` do pg0; não foram lidas.
  - Modelos: LLM pelo 9router, embeddings `qwen3-embedding:0.6b` pelo Ollama local.
  - Banks hoje: só o `core-engineering-bank` (46 fatos); **o bank do PQBR ainda não existe**.
  - **Não há backup do Hindsight** (sem timer, cron nem arquivos de dump). Tarefas F3-03 e F3-04 no ROADMAP.
- **Backup:** `infra/pqbr-db/backup.sh` (pg_dump `-Fc -Z9`), timer de usuário `pqbr-db-backup.timer` diário às 03:30 (Fortaleza).
  - Rotação de 7 em `~/Backups/pqbr-db` (700/600, fora do git).
  - Restauração testada com `testar_restauracao.sh`.
  - Drive ativo (12/10): pasta `PQBR` id `1RKEE2kn2WDrH6SK__1SA5QkFkxwpqzya` + 7 subpastas (REGRAS §21); IDs em `config/drive_pastas.json` e `PQBR_DRIVE_PASTA_ID` no worker.env; privada (só dono).
- **Achado:** o CSV de temas tem 2 repetições históricas (`repete_n`), anteriores à R10, aceitas pelo José (t337–t338). Elas ficam registradas, mas fora do índice único da R10.
- **Histórico:** o Supabase `paperclip` foi só lido em 09/10. O `public` dele (banco do Paperclip, 214 tabelas) está com RLS desligado; o alerta foi levado ao José, sem nenhuma alteração.

Só dados de negócio. O Postgres do Temporal guarda só estado de workflow e **nunca** é consultado diretamente (t324–t326). Sem segredos nem PII em nenhuma tabela (autores de comentário só como hash).

| Tabela | Conteúdo principal | Req |
|---|---|---|
| `temas` | tema normalizado, origem (perene/em alta), status, `video_id`, data; carga inicial de `db/seeds/temas-publicados.csv` | RF-02 |
| `grade` | data, janela, tema, pontuação, fonte, status | RF-01, RF-03, RF-05 |
| `episodios` | código `PQBR-EPxxxx`, tema, estado (aprovado → enviando → enviado → agendado → publicado/privado), `video_id`, janela, hashes dos arquivos | RF-15, RF-16 |
| `visual_assets`, `episode_assets` | fichas (origem: ferramenta, conta, data, prompt, versão; status de verificação) e uso por episódio | RF-08, RNF-08 |
| `auditorias` | veredito, motivo, ID da cena, respostas sim/não por rodada | RF-11..RF-14 |
| `comentarios` | id, vídeo, autor (hash), rótulos, ação; texto bruto apagado em até 30 dias | RF-22, RF-23 |
| `respostas` | frase usada, comentário, horário, conferência de 60 min | RF-24 |
| `frases` | banco de 60 frases aprovado | RF-24 |
| `acoes` | motivo, quem, quando (item 5, retenções, compliance) | RF-20 |
| `propostas` | propostas dos agentes (JSON Pydantic v2), status de aprovação | RF-33 |
| `tickets` | ticket de manutenção pré-estruturado, aprovações 1 e 2 | RF-35 |
| `revisao_humana` | item, caminhos já tentados, determinação do José | RF-36 |
| `consumo` | uso do NotebookLM, tokens do Jev, cota das APIs, custo estimado | RF-10, RF-32 |
| `compliance_eventos` | origem, gravidade, prazo de recurso | RF-28 |
| `metricas` | Analytics API por vídeo e dia | RF-30 |
| `config_flags` | kill switch das respostas, HOLD da fila | RF-26, RF-28 |

Escrita no banco do app sempre por Activity com **outbox** (idempotente por chave).

### Retenção do consumo por modelo [t358, t369; APROVADO, não aplicado]
- **Prazos [t369]:** linhas brutas **90 dias**; resumo diário **25 meses** (depois disso o resumo também é apagado pelo mesmo job).
- **Job:** `RetencaoConsumoWorkflow`, disparado por um **Schedule do Temporal** diário às **~04:15** (Fortaleza), depois dos backups das 03:30/03:45 e fora das janelas de publicação.
- **Ordem:** (1) agrega os dias que vão sair num **resumo diário** permanente (`pqbr.consumo_resumo_diario`, mesmas colunas de `consumo_diario`: dia, provedor, modelo, tipo de ação, somas), com upsert por chave natural; (2) confere se as somas do resumo batem com as linhas brutas daqueles dias; (3) só então apaga as linhas brutas mais antigas que o prazo, em lotes.
- **Papel dedicado:** `pqbr_manutencao` (nologin até ser usado; senha só no `.env`), com `SELECT` e `DELETE` só em `consumo_modelos` e `INSERT`/`UPDATE` só no resumo. O `pqbr_app` continua sem `DELETE`.
- **Idempotente:** rodar duas vezes no mesmo dia não duplica o resumo nem apaga nada além do prazo; se a conferência falhar, não apaga e avisa.
- **Registro:** cada execução vai para `pqbr.acoes` (`tipo='retencao_consumo'`: dias agregados, linhas apagadas, resultado). O backup diário do banco roda antes, então o bruto apagado ainda fica nos 7 dumps.
- **A fazer (migração futura, ainda não escrita nem aplicada):** tabela do resumo e papel `pqbr_manutencao`, com rollback.

### Banco do Paperclip [t367; PLANO, não executado]
- **[FEITO t412, 11/10]** O Paperclip usa Postgres 17 local dedicado (`infra/paperclip-db`, 127.0.0.1:55434, banco/role `paperclip`, backup 04:00; rollback no README até 18/10). Antes usava o **Supabase** (projeto `paperclip`). Plano: migrar para um **Postgres local próprio no `pc`**, num container dedicado ao lado dos bancos do app, do Temporal e do Hindsight (cada um separado), em 127.0.0.1 com limite de memória, backup diário e Supabase mantido como rollback por N dias. Com o banco local, a pendência de RLS do Supabase deixa de valer (a confirmar ao fim). Passos e portão: ROADMAP L-01. Exige reiniciar o **serviço do Paperclip** (não o Hermes) numa janela curta.

## 9. Workflows do Temporal [PROPOSTA; validados a partir da Fase 0.5]

| Workflow | Disparo | Passos | Req |
|---|---|---|---|
| `GradeDiariaWorkflow` | Schedule de madrugada | coleta → caderno diário → Deep Research → filtros/barreiras/polêmica → grava grade | RF-01..RF-05 |
| `EpisodioWorkflow(ep)` | grade do dia | roteiro (NotebookLM) → fichas → render → pós FFmpeg → auditor → Drive → aprovado | RF-06..RF-14, RF-40 |
| `PublicacaoWorkflow(ep)` | episódio aprovado | busca do código → `videos.insert` privado → agendar (API ou Camofox) → conferir | RF-15..RF-18 |
| `Item5Workflow(video)` | sinal de problema | privado na hora → Telegram → aguarda sinal do José | RF-19..RF-21 |
| `ComentariosWorkflow` | Schedules 30 min / 6 h / diário | ler → pré-filtro → Jev → reter/responder/sinalizar | RF-22..RF-27 |
| `ComplianceWorkflow` | Schedule + antes de cada janela | coleta → gravidade → HOLD se crítico | RF-28, RF-29 |
| `GuardiaoSessaoWorkflow` | Schedule ~20 min com variação | testa Studio, Gemini, NotebookLM → escada t272 | RF-37 |
| `AnalistaWorkflow` | Schedule diário/semanal | coleta → agente analisa → `PropostaAgente` | RF-30, RF-33 |
| `RelatorioDiarioWorkflow` | Schedule noturno | junta dados → template → Telegram | RF-31, RF-32 |
| `LimpezaDriveWorkflow` | rotina noturna do @prod-director | duplicatas/órfãos → `_duplicados` → lista ao José | RF-41 |
| `MonitorAtualizacoesWorkflow` | Schedule semanal | lê releases → Jev → pede autorização | RF-42 |
| `RevisaoHumanaWorkflow(item)` | item que falhou em todos os caminhos | guarda → avisa → aguarda determinação | RF-36 |

- **Filas:** `notebooklm` (concorrência 1), `camofox` (concorrência 1), `render`, `default`.
- **Sinais:** `aprovacao_jose` (proposta, ticket, volta a público), `pausar_respostas` / `retomar_respostas`, `determinacao_revisao` (excluir/corrigir/reaproveitar/arquivar), `hold_fila`.
- **Retentativas:** `RetryPolicy` 30 s → 2 min → 8 min; espera de rede sem gastar tentativa; 2 falhas da mesma ação → José; 5 idênticas → parada (REGRAS §18).
- **Janelas:** 11:40, 14:40, 18:35, 21:15 (America/Fortaleza).

## 10. Integração com o Paperclip [PROPOSTA; demonstrada em F05-04]

### Hermes `pqbr` ↔ Paperclip [t363; conectado na empresa de teste]
- **Identidade:** agente `pqbr-assistente` (`7d18350e…`) na empresa **PQBR-TESTE** (`d9fa962a…`), adaptador `process` com `/bin/true`, heartbeat desligado, orçamento 0, permissões `canAssignTasks` sim, `canCreateAgents`/`canCreateSkills` não. **Chave de agente** `hermes-pqbr` (id `58b8794a…`), escopada à empresa (outra empresa → 403), guardada só em `~/.hermes/profiles/pqbr/.env` (`PAPERCLIP_PQBR_API_KEY`, 600).
- **Acesso:** contexto CLI próprio `~/.hermes/profiles/pqbr/paperclip/context.json` (600, persona agent, a URL da tailnet na porta 3100 (`<ip-tailnet>:3100`), porque o Paperclip só escuta na tailnet, não em 127.0.0.1) + wrapper `paperclip/pqbr-paperclip` com allowlist (issue list/get/comments/create/comment/update; agent list/get/me/heartbeat:invoke; project, activity, dashboard) e escopo fixo + skill `skills/productivity/paperclip-pqbr`. Cópias no repo: `docs/hermes-pqbr/perfil/`.
- **Acesso desde t372:** o perfil **não tem terminal, arquivos, código, web, navegador, delegação nem cron** (desligados em `cli` e `telegram`); ficam skills, memória, busca de sessões, perguntas e o **servidor MCP `paperclip-pqbr`** (`paperclip/mcp_paperclip.py`, só stdlib, ferramentas fixas: listar/ver issues e comentários, criar issue, comentar, listar e acordar agentes). A chave é lida pelo MCP e nunca volta ao modelo. O wrapper `pqbr-paperclip` fica só para uso manual. Busca de arquivos só leitura em `docs/`: o Hermes não oferece escopo por pasta no toolset `file`, então ficou desligada (EM CONSTRUÇÃO: ferramenta MCP de leitura em `docs/`, se o José quiser).
- **Escrita:** comentar ou atualizar issue com chave de agente exige o contexto de um heartbeat (`Cross-issue writes need a run`); a leitura funciona direto. O comentário de teste na PQB-4 só saiu com o `--run-id` de um heartbeat do próprio `pqbr-assistente`. Desde t372 o MCP faz isso sozinho: heartbeat do próprio agente com `payload.issueId` e o run id na escrita.
- **Reapontar na F1-02:** criar o mesmo agente na org PQBR real, nova chave, trocar `companyId`/`agentId` no contexto e revogar a chave de teste.
- **Incidente no teste (09/10 ~19:20):** o Hermes `pqbr` tem terminal e arquivos sem restrição. No teste, além do wrapper, ele leu `/proc/<pid>/environ` do processo do Paperclip e expôs o `DATABASE_URL` do Paperclip ao modelo e ao histórico do perfil. **Conferido em t372:** o Hermes mascarou a senha (`***`) antes de guardar; foram expostos usuário e host do Supabase, não a senha. A mensagem foi apagada do `state.db` (com backup) e o banco foi compactado; também escreveu `cache/scratch/invoke_run.js`, que lê a chave do `.env` e chama a API direto. **O "acesso restrito" do SOUL não está garantido pela configuração.** Antes de ligar o `pqbr` no Telegram: restringir os toolsets do perfil (sem terminal livre; só o wrapper e as skills) e rodar de novo o teste ponta a ponta.


- O Temporal publica eventos de negócio (via outbox) no banco do app e abre/atualiza **issues** no Paperclip (episódio, revisão, ticket, proposta).
- Os agentes no Paperclip (director, analista, comunidade, compliance, assistente, dev) leem o banco do app (só pelo contexto do fluxo ou `pqbr_leitura`) e issues e devolvem **`PropostaAgente`** validada; nunca executam efeito externo.
- A aprovação do José (Telegram pelo Hermes `pqbr` ou painel) vira sinal `aprovacao_jose` no workflow; só então a rotina aplica.
- Heartbeats desligados até a liberação; nenhum agente com `--yolo` (H-SDD1).

## 11. Interfaces: contratos Pydantic v2 [PROPOSTA; fixados em F3-01]

| Modelo | Campos principais | Usado em |
|---|---|---|
| `RoteiroShort` | falas, duração estimada (15–180 s, alvo ~50 s, ~2,3 palavras/s), CTA = "Segue o Porquê BR", entidades da cena, sem nomes | RF-07 |
| `DecisaoRepeticao` | repetido: bool, tema_parecido, confiança | RF-02 |
| `PontuacaoPolemica` | valor 0–100, componentes, bloqueio_absoluto: bool | RF-05 |
| `VereditoAuditor` | veredito (aprova/ressalva/revisão/reprova), motivos[], id_cena, rodadas | RF-12..RF-14 |
| `DecisaoPublicacao` | ação (refazer/trocar/chamar_jose), confere_agendado: bool | RF-18 |
| `ClassificacaoComentario` | rótulos[], alvo, ironia_possivel, grave: bool, pede_acao: bool | RF-23 |
| `SinalItem5` | origem, motivo, gravidade, video_id | RF-19, RF-21 |
| `PropostaAgente` | agente, tipo, alvo (parâmetro/regra/tema), valor_atual, valor_proposto, justificativa curta, evidências | RF-33 |
| `TicketManutencao` | localização (arquivo/módulo/workflow), falha observada (evidência, horário, episódio), correções sugeridas, aprovações 1 e 2 | RF-35 |
| `DeterminacaoRevisao` | item, decisão (excluir/corrigir/reaproveitar/arquivar), observação | RF-36 |
| `decide()` | interface única do Jev: entrada tipada, saída de um dos modelos acima; fallback devolve o mesmo modelo | RNF-02 |


## Revisão por modelo distinto (t419)
Combo do 9router `core-revisao` (família distinta dos combos de produção) para correções/revisões de saídas dos outros combos core: aplicados (t419/t421): Dev Revisor, desempate da 3ª rodada do Auditor, 2ª tentativa após saída inválida, dupla checagem do Guardião antes de bloquear/pausar (`segunda_opiniao` no `pqbr-kit`), revisão do Diretor sobre correções de playbook e segunda leitura do Compliance em roteiro sensível. Falha do combo (2×) → regra conservadora. Detalhe em `docs/AGENTES.md` §7.
