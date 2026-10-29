# ARQUITETURA da PQBR

> Autoridade: abaixo de `docs/REGRAS.md` e `docs/SPEC.md`; acima de `docs/TESTES.md`, `docs/ROADMAP.md` (incluindo o anexo ex-PLANO). Requisitos citados como RF/RNF (SPEC). Este arquivo diz **como** as regras são executadas hoje; ele se adapta às regras, nunca o contrário (t285). Em conflito, vale o REGRAS.md.
> Não consultar `docs/arquivo/`, `docs/pesquisas/` nem `docs/DECISOES-LOG.md` sem aprovação explícita do José (t287). **Exceção (t530, José):** `docs/pesquisas/PESQUISA-extensoes-geracao-em-serie.md` pode ser lido por qualquer agente, **somente leitura** (referência da Fase 4V). **t536:** a restrição vale para os agentes especialistas; o agente PQBR (auxiliar do José) lê todos os docs.
> Legenda: [APROVADO] · [VERIFICADO] · [HIPÓTESE] · [PROPOSTA] (sugestão ainda sem aprovação) · EM CONSTRUÇÃO — aguardando José.

---

## 1. Decisões de arquitetura (ADRs)

### ADR-013: processo canônico de criação por plataforma [APROVADO t160u / José t149u]
- **Documento:** `docs/processos/CRIACAO-README.md` (v1.0.0) + `flow.md` / stubs Vids·Vibes.
- **Ordem:** projeto por episódio → fichas do `banco-fichas/` → refs faltantes pelo agente da plataforma → storyboard → stills → revisão → 1 clipe/cena → HOLD se cota/esgotamento.
- **Temporal:** activity `processo_criacao_conferir` no `EpisodioWorkflow` (versão+hash fail-closed). Ativação em runtime exige reinício do `pqbr-episodio-worker` (OK José).
- **Cadeia:** `CADEIA_VIDEO` = flow → google_vids → meta_vibes → HOLD.


### ADR-001: motor de orquestração (Temporal primeiro, DBOS como plano B)
- **Resultado [APROVADO t374, 10/10]:** o **Temporal** foi aprovado no teste (TZ-01..TZ-04 e TZ-07; soak de 122 execuções em ~20 h, sem falha, perda ou duplicata, pico de 340 MiB). **Motor = Temporal; DBOS dispensado.**
- **Decisão [APROVADO t283]:** a espinha do fluxo é **código + motor de workflow durável**, numa arquitetura híbrida pensada para vários canais. O **Temporal** é testado primeiro; o **DBOS** é o plano B.
- **Como decidir [PROPOSTA, ROADMAP F05-01..F05-07; TESTES TZ-01..TZ-07]:** spike de 1 dia. Temporal self-hosted só com Postgres local e dedicado no `pc` (sem Elasticsearch; separado do `mp32-postgres`; ~0,9 GiB estimado) e um `EpisodioWorkflow` de brinquedo com timer, sinal de aprovação e uma Activity que falha. Aceite: RAM dentro do limite combinado; retomada após `kill -9` no worker e após reboot; aprovação por sinal. Se reprovar, repetir o teste com o DBOS. O José escolhe no portão G0.5.
- **Forma-alvo [PROPOSTA]:**
  - Schedules: grade da madrugada, lote da manhã, guardião de sessão, leitura de comentários, limpeza do Drive, relatório diário, monitores. Eles substituem os timers do SO; a **regra** de horários fixos + vigia de prazo (REGRAS §3) não muda.
  - `EpisodioWorkflow(ep)`: pauta → NotebookLM → FFmpeg → auditor → upload privado → agendar → confirmar.
  - `Item5Workflow`: qualquer problema → vídeo privado na hora + aviso pelo canal ativo (Telegram/Hermes `pqbr`; t474) (REGRAS §16).
  - Workers Python (`src/pqbr`) com filas por recurso: `notebooklm` (concorrência 1), `camofox` (concorrência 1), `render`, `default`.
  - Activities sem LLM: NotebookLM CLI 0.8.4, FFmpeg, juiz Gemini, YouTube API, Drive, banco do app. `decide()` (Jev) está desenhado e **ainda não existe no código** (JEV-EF, t137u).
  - **Escopo [t327]:** só o canal Porquê BR. Multi-canal (`canal_id`, config e orçamento por canal, R10 por canal) fica **adiado** para depois dos aprendizados.
- **Dois bancos com papéis distintos [t324–t326]:**
  - **Postgres próprio do Temporal:** só estado dos workflows. **Nunca é consultado diretamente** por agentes, painel ou relatórios.
  - **Banco do app (Postgres local, t343):** dados de negócio: temas/R10, vídeos e códigos PQBR-EP, comentários, métricas, relatórios, base do painel e do analista. Mantido [recomendação aprovada; confirmar no teste de 1 dia do Temporal].
- **Banco do app fora [t324–t326]:** retentativas duráveis do Temporal + **outbox** para o banco do app na volta. Substitui a fila em arquivo da t242 (confirmar no teste). A regra (REGRAS §18) não muda.
- **Teto de RAM [APROVADO t329]:** Temporal + Postgres dedicado ≤ 1,5 GB no `pc`; acima disso no TZ-01, considerar o DBOS (plano B).
- **Cautelas:** RAM e swap do `pc` (H-ORQ1); determinismo e versionamento dos workflows; `NUM_HISTORY_SHARDS` escolhido uma vez; backup diário do Postgres do motor (sem segredos); nenhum agente autônomo dentro de Activity com efeito colateral.

### ADR-002: Paperclip = camada de agentes + painel, ligado ao Temporal [SUBSTITUÍDA pela ADR-011 em 23/10/2026; histórico]
> O Paperclip está sendo retirado. Agentes: PydanticAI em activities do Temporal (ADR-011). Painel: Temporal UI; canal: Telegram (t471/t474). O texto abaixo é histórico.
- **Decisão [APROVADO t282, t327]:** o **Temporal** executa o fluxo determinístico; o **Paperclip** é a **camada de agentes e o painel**. **Os agentes vivem no Paperclip** (org PQBR, pacote `company/` no formato agentcompanies/v1). Pelo padrão dos agentes pensantes (t324–t326), eles observam e propõem (saída Pydantic v2), e nada se aplica sem o José; o Paperclip **não é dono do fluxo**.
- Abre só dentro da tailnet, por HTTPS; a porta 443 fica livre [VERIFICADO/APROVADO t280].
- Verificação de fichas: status/issue no painel e botões no canal ativo, sincronizados pela mesma tabela (Telegram/Hermes `pqbr`; t474) (REGRAS §6).
- **Ligação Temporal ↔ Paperclip [PROPOSTA, a validar na Fase 0.5]:** o Temporal grava eventos e estado de negócio no banco do app (outbox) e abre/atualiza issues no Paperclip; os agentes leem banco do app/issues e devolvem propostas estruturadas; a aprovação do José vira **sinal** para o Temporal. Nunca leem o Postgres do Temporal.
- Riscos conhecidos: o adapter `hermes_local` força `--yolo` (PR #3850), mas o perfil `pqbr` não pode herdar `--yolo` (REGRAS §23): resolver H-SDD1 antes de ligar qualquer agente Hermes; recovery storm sem internet (issue #6596); injeção do AGENTS.md (issue #3833, corrigida pela PR #8543). Heartbeats desligados até a Fase 0.5 provar a ligação.
- `company/` continua (pacote dos agentes). `tasks/`: as rotinas viram Schedules do Temporal, então `tasks/` é candidato a exclusão depois da Fase 0.5 [PROPOSTA].

### ADR-003: Telegram com o Hermes `pqbr` [VIGENTE: restabelecida por t474, que revogou ADR-009/t464]
- **Decisão [t281; reafirmada t474]:** o canal do José é o Telegram, pelo perfil Hermes `pqbr`: avisos, pedidos e aprovações (as aprovações viram sinais do Temporal). Painel: Temporal UI (t471). Preservar o gateway Hermes compartilhado e os outros perfis. Pendente: token de bot próprio do perfil `pqbr` (decisão do José).
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
> Categoria YouTube: **27 Educação** (José 12/10); `containsSyntheticMedia=false` (stickman, não realista; t133u).
> Referência viva da sessão Google: [`REFERENCIA-sessao-google.md`](REFERENCIA-sessao-google.md) (Camofox única fonte e único renovador; NotebookLM só lê; 12/10).
- **Instância e perfil únicos (José, 12/10):** a conta Google de produção vive em **um** processo `pqbr-camofox` (127.0.0.1:9387) e **um** perfil persistente: `userId=pqbr` → `~/.pqbr/camofox/profiles/66e057673effe4afdd963a2bd6a45a2a/` (SHA-256 do userId, plugin de persistência). Regras: todo cliente usa `userId=pqbr` (o `sessionKey` é só o grupo de abas, no mesmo contexto); `MAX_SESSIONS=1`; nada de userId novo, perfil efêmero, `--fresh` ou segundo processo; reinícios restauram o mesmo `storage-state.json`. Auditado em 12/10: keepalive, `camofox.py` (fila camofox-pqbr), `sync_cookies_chrome.py`, `mcp_kit` e playbooks usam só `pqbr`; o auditor Gemini ainda não tem código e deve seguir a mesma regra. Outro processo `node server.js` no `pc` (PID do 9377) é de outro projeto, não da PQBR.
- **NotebookLM gerenciado pelo `notebooklm-py`; autenticação Google única:** toda a gestão do serviço Google NotebookLM é feita pela CLI `notebooklm-py`, que gerencia a sessão lógica NotebookLM e seu armazenamento local no perfil lógico `pqbr`; isso não significa outra conta, perfil de navegador ou renovador. O Camofox é a fonte única de autenticação/renovação da mesma conta Google de produção usada por NotebookLM, Flow e Vids, no perfil persistente único `userId=pqbr` da instância `pqbr-camofox`. O consumidor NotebookLM lê o estado sincronizado pelo mecanismo existente `NOTEBOOKLM_REFRESH_CMD`/`nlm-sync.sh`; a referência viva registra `NOTEBOOKLM_HEADLESS_REAUTH=0` e `NOTEBOOKLM_DISABLE_KEEPALIVE_POKE=1`, sem Chromium/login paralelo ou renovação concorrente. Base: `REFERENCIA-sessao-google.md` §3/§5, REGRAS §10–§11 e blueprint do módulo de vídeo §9; esclarecimento do proprietário em 17/10/2026. Esta precisão documental não altera configuração, comprova operação atual nem fecha F4-07 ou F00-01/G0.
- `pqbr-camofox` sempre ligado, com a sessão permanente na mesma tela; reinicia só se cair (`Restart=always` + guardião). A sessão caiu: renovar → sincronizar cookies do Chrome → outro caminho; log + aviso pelo canal privado ativo (Telegram/Hermes `pqbr`; t474); o José só no fim (noVNC/2FA).

- **Comportamento humano obrigatório (REGRAS §11, José 12/10):** toda automação de navegador (Camofox/Camoufox) simula humano: Camoufox com `humanize: true` (cursor humano, fixo no `server.js` do camofox 1.6.0); clique só por `/click`; texto curto digitado com cadência variável e texto longo colado (`fill`) após clique no campo; pausas sorteadas entre ações; keepalive com jitter. Essas cadências não se confundem com os 5–15 min de pacing entre intervenções de REGRAS §3.1; não implicam garantia anti-detecção. Código: `src/pqbr/workflows/camofox_humano.py` (único caminho para clicar/digitar). Sessão Google: Camofox é a única fonte e o único renovador; o NotebookLM só lê (`NOTEBOOKLM_REFRESH_CMD`).

### ADR-009: Discord nativo do Paperclip como canal PQBR [REVOGADA por t474 em 23/10/2026; histórico]
- Conectar o conector Discord diretamente ao Diretor ativo; não criar agente “Canal PQBR” redundante.
- O conector experimental fica restrito a servidor/canal privado e à identidade Paperclip ativa do José; “Allow unlinked people” desligado. Não abrir ingresso HTTPS público; confirmar que o Gateway de saída funciona na instância real.
- Migrar conversa, aprovação Temporal e todos os avisos operacionais antes do corte. Entrega proativa de notificações precisa ser comprovada; respostas em threads, sozinhas, não bastam.
- Hermes `pqbr` e emissores Telegram PQBR permanecem como rollback durante o piloto; após todos os gates, pausar somente o perfil `pqbr` e rotinas PQBR. Preservar gateway Hermes compartilhado, outros perfis, histórico e credenciais.
- Aprovações Temporal usam principal autenticado em metadado server-side, vínculo com tarefa e estado válido; falha fechada, idempotência persistente, até três tentativas e ticket de manutenção após esgotamento. Nenhum sinal de workflow de produção no piloto.


### ADR-010: NotebookLM como fonte intelectual; provedores Google para vídeo [APROVADO t465]
- NotebookLM conduz pesquisa profunda, cultura brasileira/expressões, propostas semanais de temas, ideação, roteiro e SEO. O caderno canônico é temporário para os documentos/pacote iniciais e recriável após persistir fontes e resultados; cadernos por episódio são efêmeros e copiam a mesma persona-base.
- Agentes Paperclip orquestram, encaminham insumos, extraem saídas estruturadas e validam. Não fazem pesquisa, tema, roteiro ou SEO independentes, exceto complemento de relatório ou fallback documentado por indisponibilidade central.
- NotebookLM não gera vídeo. Temporal chama a rota visual pelo Camofox: Flow primário, depois Google Vids, depois Meta Vibes quando Flow e Vids falham ou esgotam cota (t517); tudo pelo navegador, sem APIs. Medir cotas reais; dois Shorts/dia não é quota prometida. Instruções técnicas em inglês; conteúdo final em pt-BR. Identidade visual aprovada: stickmen/fichas; implementação pendente.

### ADR-011: agentes PydanticAI em activities do Temporal [APROVADO t474, 23/10/2026; substitui ADR-002]
- **Decisão:** o Paperclip sai da arquitetura (em retirada; o código dele não é alterado até o desligamento). O **Temporal** continua dono do fluxo; os agentes passam a ser **PydanticAI com Pydantic v2**, executados **dentro de activities do Temporal**. O **Jev** continua como classificador/decisor estruturado.
- **Regra de efeitos:** o agente só gera e valida (saída tipada Pydantic v2). Efeitos externos (Drive, YouTube, Camofox, banco) ficam em activities determinísticas separadas. Retentativa, timeout e idempotência são do Temporal.
- **Modelos:** via 9router (combos reais do projeto). Personas: `company/agents/<slug>/AGENTS.md`; playbooks: `company/playbooks/`. Memória: Hindsight por adaptador.
- **Interface do José:** Telegram (Hermes `pqbr`) para avisos, pedidos e aprovações; aprovação = sinal do Temporal (ID autorizado, estado válido, fail-closed, idempotente). Painel: Temporal UI; painel próprio depois (t471).
- **Agente-first:** contratos pequenos e fechados, um módulo por agente, testes unitários sem rede, para que agentes de programação construam e mantenham.
- **Pendências:** reescrever as partes de §3/§10 e do roster (`docs/AGENTES.md`) que ainda descrevem org/issues/heartbeats do Paperclip; definir o primeiro workflow migrado (proposta: `ReposicaoTemasWorkflow`). Detalhe: `docs/sdd/adr-011-agentes-pydanticai-temporal.md`.

- **Princípios t512–t514 (José, 24/10/2026):**
  1. **Temporal = sistema nervoso** (t514): a peça mais rígida; trocável em tese, mas a última a mudar, pela consistência. Toda decisão que exigiria um humano e roda sozinha é **determinística e passa pelo Temporal** (durável, registrada, reexecutável/replay, com retentativas e sinais). O Temporal **não** é escondido atrás de camadas extras: workflows e activities usam o SDK direto.
  2. **NotebookLM = centro nervoso editorial e motor do canal** (t512): decisões, temas, roteiros e direção do canal; a produção segue os caminhos que ele norteia. A **geração de vídeo saiu do NotebookLM** por determinismo (Flow é a rota primária).
  3. **Sistema modular** (t513): cada motor é peça trocável atrás de um contrato (interface Pydantic + adaptador), escolhida por config (`config/motores.json`; portas em `src/pqbr/motores/`): `MotorIntelectual` (hoje NotebookLM), `GeradorVideo` (hoje Flow; cadeia Flow (primário) → Google Vids pelo navegador → Meta Vibes quando os dois falham ou esgotam a cota; tudo pelo navegador nas cotas já pagas, **sem APIs** (t517); NotebookLM vídeo só como alternativa). Agentes e motores giram em volta do Temporal.
  4. **9 papéis-agente** (t512, t145u): Diretor, Líder Editorial (monta pedidos ao motor e valida respostas), Pesquisador de Origem, Auditor, Compliance, Guardião, Observador, Dev (diagnostica e propõe; nunca aplica; José aplica com agentes externos), Motion (monta o bloco de motion graphics do catálogo; não julga). Roteirista, SEO e Caçador Sazonal viram etapas de workflow que chamam o MotorIntelectual; Comunidade adiada.
  5. **Contratos Pydantic v2 = peça central do determinismo, junto com o Temporal** (t515): todo dado que cruza agente, motor ou serviço web passa por contrato. Ficam **num lugar só** (`src/pqbr/contratos/`, inclusive os das portas de motor), cada um **versionado em SemVer** (`contratos.VERSOES`; MAJOR = quebra, MINOR = campo opcional/regra mais frouxa, PATCH = doc; teste obriga). **Revisão contínua**, porque regras e fluxos dos serviços web mudam: testes de contrato por adaptador (respostas reais gravadas como fixtures), canários periódicos por adaptador web em Schedule do Temporal que detectam deriva, e Observador/Dev sinalizando quebras (proposta, não aplicada, em `docs/_obsoleto/sdd/PROPOSTA-papeis-skills.md` §Revisão de contratos).

### ADR-012: Camofox — uma instalação, uma instância por conta crítica, atrás de `NavegadorIdentidade` [APROVADO José 24/10/2026; NÃO implementado]
- **Decisão:** uma única instalação do Camofox (app + binário Camoufox, versão travada) e uma instância systemd por conta crítica (`camofox@<conta>`), cada uma com porta e perfil próprios, **um único renovador**, backup diário do perfil com teste de restauração e canário diário (Schedule do Temporal). Até ~3 contas simultâneas. Workflows falam só com o adaptador `NavegadorIdentidade` (contrato Pydantic), nunca com a porta direto.
- **Diagnóstico 24/10 (somente leitura):** a 9387 (PQBR) é **instalação duplicada**: clone git do global em `~/.pqbr/camofox/app` (v1.15.0) + cópia própria do Camoufox 152.0.4-beta.30 em `~/.pqbr/camofox/cache` (1,3 GB). O global (9377) foi atualizado para v1.18.1 em 24/10 (mesmo camoufox-js 0.11.5 e mesmo binário). Ver `docs/REFERENCIA-sessao-google.md` §9 e `docs/mapa/08-identidade-camofox.mmd`.
- **Migração:** por proposta, com OK do José a cada passo (plano em REFERENCIA §9). A 9387 não muda até lá.

**Atualização t526 (24/10/2026):** PQBR permanece na instalação individual (9387) por decisão do José. Kit pronto no repo (`deploy/camofox/`, `config/camofox_instancias.json`, `motores/navegador.py`); próxima instância reservada `proxima`:9397 (não instalada). Gatilho: próxima integração de projeto. Procedimento: `docs/RUNBOOK-nova-instancia-camofox.md`.

## 2. Componentes

| Componente | Papel | Status |
|---|---|---|
| **NotebookLM** (notebooklm-py) | Fonte intelectual primária para pesquisa, propostas de temas, ideação, roteiro e SEO; não gera vídeo. A geração visual cabe ao Flow primário, Vids fallback adicional, Gemini Web terceira rota e Meta Vibes posterior (REGRAS §9; ADR-010), sem declarar integração ou ativação. Caderno **efêmero por episódio**; nunca o raiz. **Sem caderno mestre (t459, ADR-003):** pacote canônico (persona, comandos/prompts, contrato, bloco §16.7) versionado por hash em `pqbr.pacote_canonico` (Postgres, fonte de verdade) e espelhado no Drive `00_Biblia_Visual`; injetado em cada caderno do episódio (casado pelo id registrado em `pqbr.cadernos_episodio`); fontes/respostas/artefatos intelectuais arquivados em Drive + `pqbr.arquivo_caderno`; caderno apagado pelo id em D+2 após a publicação (allowlist, nunca mestre, nunca por título). Adicionar o roteiro como fonte antes de gerar artefatos intelectuais; em timeout, listar artefatos e não regerar; nunca `ask --new`. | [APROVADO] / hábitos [VERIFICADO no `rede`] |
| | Instalação exclusiva da PQBR (D1): venv com 0.8.4 fixada, `NOTEBOOKLM_HOME` próprio, perfil `pqbr`, serviço único dono da sessão. Hoje há uma instalação global 0.8.2 compartilhada com o MP32. | [APROVADO em princípio] / estado atual [VERIFICADO] |
| | Histórico de geração de vídeo anterior à ADR-010 (rota NotebookLM desativada): duração de 15 s a 3 min com alvo de ~50 s. Verticais até ~67 s já saíram bem; até 180 s ainda não testado (H5). Com 2 personagens, o Short ignorou as imagens de elenco (5 de 5); com 1 funcionou. | [VERIFICADO até ~67 s] |
| **Gemini web** | Reserva do NotebookLM e **juiz visual** do auditor (3.8 Flash, modo normal; o "Flash Estendido" recusa as pranchas), via Camofox. **Sem Gemini API** [t327]. | [APROVADO] |
| **Jev** (TypeSafe) | `decide()` com provedor trocável; só decisão estruturada (REGRAS §7). Fallback: Jev via OpenRouter → modelo OpenAI (H7). | [APROVADO] |
| **Camofox** (camofox-browser sobre Camoufox, perfil `porquebr`) | Toda automação de navegador; único dono do login do Studio; reserva da publicação e agendamento enquanto H1 não fecha; corações. Telemetria de crash vem ligada: verificar e desligar (H9). | [APROVADO] |
| | Dicas do Studio [VERIFICADO no `rede`]: ir direto a `/videos/upload?d=ud`; `execCommand('insertText')`; COPPA "não é para crianças"; paginar 30 por vez; desafio de passkey → humano; upload só de `~/.camofox/uploads/`. | |
| **YouTube Data API** | Grade, comentários (`commentThreads.list` = 1 unidade), respostas (`comments.insert` = 50), retenção (`setModerationStatus` = 50), `videos.update` = 50, upload (`videos.insert`). Cota 10.000/dia, reset à meia-noite do Pacífico (~04:00–05:00 em Fortaleza); `search.list` e `videos.insert` com balde próprio de 100/dia. Sem endpoint de coração. | [VERIFICADO na doc] |
| **YouTube Analytics API** | Coleta diária do analista (OAuth só leitura; app do GCP em produção, uso interno). | [APROVADO] / números [HIPÓTESE] |
| **Motor de workflow** (Temporal) | Estado durável dos fluxos, Schedules, retentativas, sinais (ADR-001). Postgres próprio, só estado de workflow, nunca consultado diretamente. | [APROVADO t374] / Temporal escolhido no G0.5; DBOS dispensado |
| **Banco do app** (Postgres 17 local, `infra/pqbr-db`) | Dados de negócio (base do painel e do analista; recebe por outbox): grade, temas (R10), episódios, `visual_assets`/`episode_assets`, comentários, ações (motivo/quem/quando), consumo, kill switch, relatórios. Plano Pro não confirmado (H13). | [APROVADO] |
| **Google Drive** | Armazenamento definitivo da mesma conta Google (Flow, Studio, NotebookLM). Estrutura t267 (REGRAS §21). Leitura 27/10: pastas no lugar; fichas de imagem ainda não estavam em `00_Biblia_Visual` (t133u). | [APROVADO] |
| **Hermes `pqbr`** | Canal Telegram do José: avisos, pedidos e aprovações (sinais do Temporal); não desligar o gateway compartilhado. | [APROVADO t281/t474] |
| **Paperclip** | Em retirada (ADR-011). Era camada de agentes + painel (ADR-002). | [EM RETIRADA t474] |
| **Temporal UI** | Painel do José: estado, histórico, erros, runs travados (t471). | [APROVADO t471] |
| **PydanticAI** | Agentes tipados (Pydantic v2) dentro de activities do Temporal (ADR-011). | [APROVADO t474] |
| **Hindsight** (local, armazenamento próprio: Postgres embutido pg0; t349–t350) | Aprendizados (analista, lições do item 5) e memórias de código para os agentes de dev (ADR-004), num **bank único por organização**. Sem segredos nem PII. | [APROVADO t324–t326] |
| **Whisper / FFmpeg** | Transcrição com tempos (o Whisper ouve "Porquê BR" como "por KBR"; aceitar variantes). Pós: corte do end card só se detectado + logo com zoom suave curto. | [VERIFICADO] |

### Camofox: estado e isolamento [VERIFICADO 09/10, t354]
- Hoje: um servidor compartilhado (`camofox-browser`, `*:9377`, **todas as interfaces, sem chave**), um processo para 14 perfis em `~/.camofox/profiles` (pastas pelo hash sha256 do `userId`). Usado por `rede` (`porquebr`), MP32 (`tutibom10`), Hermes `mp3`/`pet`/`gpu` e o keepalive do runway (conta pessoal). Sem trava entre projetos.
- **Feito em 10/10 (t375):** F4C-01..03 no ar: `pqbr-camofox` em 127.0.0.1:9387 com chave, Camoufox e pastas próprios, e worker da fila `camofox-pqbr` (concorrência 1). O login do perfil `pqbr` foi feito em 11/10 (F4C-04, t405). O parágrafo de 09/10 acima é a leitura de antes desse isolamento; `src/mp32/web/camofox.py` não é arquivo deste repositório.
- Alvo: instância da PQBR (`pqbr-camofox`, `127.0.0.1:9387`, chave, `/home/pc/.pqbr/camofox`, `MAX_SESSIONS=1`, `MemoryMax=900M`), acessada só pelas Activities da fila `camofox-pqbr` (concorrência 1). A fila `camofox` do §2 passa a ser essa. Passos no ROADMAP F4C; regra no REGRAS §11.

### Correção autônoma mediada pelo Temporal [t355; PROPOSTA]
- Quando um passo de script falha com erro corrigível (`SiteMudou`, `SaidaForaDoEsquema`, transitório após a escada), o workflow chama o filho `CorrecaoAutonomaWorkflow(ferramenta, sessao, passo, contexto)` na fila da ferramenta (`camofox-pqbr`, `notebooklm`, …), com concorrência 1 por sessão.
- **Etapas [t356]:** (1) **triagem pelo Jev** (`TriagemCorrecao`: corrigível / sensível / fora de escopo; ação sensível encerra como `Sensivel` sem chamar o agente); (2) **intervenção pelo agente com LLM** (Activity na fila da sessão, tentativas e tempo limitados); (3) **verificação pelo Jev** quando couber (o passo voltou a funcionar? a saída bate com o esquema? nada fora da allowlist foi feito?); (4) **log + aprendizado**: cada ação no banco do app pelo Temporal (outbox) e o aprendizado no bank Hindsight da PQBR, sanitizado; (5) **proposta de ajuste do script** (tarefa ou ticket) quando corrigiu.
- A Activity do agente recebe só as ferramentas daquela fila (o Camofox restrito à instância `pqbr-camofox` e a uma allowlist de ações: navegar, ler, clicar, digitar, colar, upload; sem login, cookies ou exclusão). O Jev entra nas decisões estruturadas. Cada ação vai para o registro (`pqbr.acoes`, `jsonb`; tabela própria só se faltar campo, EM CONSTRUÇÃO).
- Resultado: `Corrigido(passos, proposta_script)`, `Esgotado(tentativas)` ou `Sensivel(motivo)`. Corrigido retoma o workflow e abre a proposta de ajuste (tarefa ou ticket); os outros dois avisam o José. Quem executa é um agente com LLM (t356) dentro de activity do Temporal (ADR-011; a frase de t357 dizia Paperclip e está superada); limites: até 3 tentativas, salvo parada imediata; no Camofox, 5–15 min sorteados do término de uma intervenção ao início da próxima na mesma sessão, não duração ou timeout da Activity; na sessão do Camofox, antes de agir, confere conta e sessão (divergência = `Sensivel`). Consumo de cada chamada vai para `pqbr.consumo_modelos`. Modelo de cada agente: definido na F1 (REGRAS §3.1).

**Contrato temporal e de falha (precisão documental de 17/10/2026; não afirma implementação):** sincronizar ações por condição de prontidão observável com timeout controlado; o pacing local não substitui waits de UI. O próximo início deve respeitar tanto o intervalo sorteado quanto a espera do provedor (`Retry-After` maior prevalece). Desafio/CAPTCHA, bloqueio ou consentimento necessário interrompem e seguem para avaliação humana, sem bypass. A exceção técnica na intervenção permanece terminal, sem retry/fallback automático nem reexecução da operação falha; os limites acima não alteram essa precedência. Base pública e distinção entre comportamento do cursor e pacing: REGRAS §3.1. Casos adicionais apenas especificados em TESTES §4/TS-11.

### Consumo por modelo [t357 h]
- Tabela `pqbr.consumo_modelos` (migração 0010): uma linha por chamada ou lote, com provedor, modelo, `tipo_acao` (ideação, roteiro, auditor visual/texto/desempate, triagem/classificação/decisão/verificação do Jev, correção autônoma, comunidade, compliance, analista, assistente, publicação, teste de resposta…), ferramenta, episódio, workflow/run/activity do Temporal, tentativa, chamadas, tokens (entrada, saída, cache, raciocínio), unidades não-token, duração, sucesso, classe do erro e custo estimado (micro-USD). Sem prompt, resposta ou dado pessoal. View `consumo_diario` (fuso de Fortaleza) alimenta o relatório diário. Sem teto: só monitoramento.

## 3. Papéis

> **Equipe vigente (t512, t129u, t145u):** 9 papéis em `docs/AGENTES.md`. O mapa de 14 agentes e o `@prod-*` estão em `docs/_obsoleto/agentes-equipe-14-t395.md`. O "só propõe, José aprova" foi relaxado (REGRAS §0).

> t363, histórico: o `pqbr` falava com o Paperclip de teste. Isso não é o canal atual. Canal e painel estão no bloco seguinte.

### Canal do José: Telegram (Hermes `pqbr`) + sinais do Temporal [t474; revoga t464]
- **Papel:** o perfil Hermes `pqbr` é a conversa do José com a PQBR: responde perguntas, consulta estado e resultados (Postgres do app e Temporal, só leitura), avisa e coleta aprovações, que viram sinais do Temporal.
- **Acesso restrito:** sem shell livre, acesso ao banco do Temporal, segredos, Studio ou repositório; só o ID autorizado do José dá ordem.
- **Persona:** séria e direta (t327). O rascunho de SOUL não foi instalado e foi para `docs/_obsoleto/hermes-pqbr/SOUL-rascunho.md` (t129u). Painel: Temporal UI (t471). Canal de aprovação: bot próprio (t538).
 (ex-"agentes")

**Padrão dos agentes pensantes [APROVADO t324–t326]:** uma rotina fixa executa tudo; @prod-director, @prod-analista e @prod-comunidade só observam e propõem mudanças como saída estruturada validada por Pydantic v2; nada se aplica sem a aprovação do José.

Princípio [APROVADO t184, precisado t465]: ideação, roteiro, SEO e pesquisa ficam com o NotebookLM; os papéis orquestram, extraem por código, validam com Pydantic e conferem com o Jev. Com o motor de workflow, os papéis sem LLM viram **Activities/workflows** e só alguns continuam como agentes LLM [PROPOSTA, PESQ-orquestração §9]. NotebookLM é fonte intelectual; agentes apenas orquestram/validam, sem pesquisa/roteiro autoral independente, salvo complemento de relatório ou fallback documentado se a ferramenta central faltar. Vídeo fora do NotebookLM; Flow primário e Vids fallback (ADR-010).

| Papel | Natureza [PROPOSTA salvo indicação] | Faz | Não faz |
|---|---|---|---|
| @prod-director | Rotina fixa executa; agente observa e propõe (Pydantic v2), aplica só com aprovação do José [APROVADO t324–t326] | Cadência, rotinas, parâmetros operacionais; recebe propostas do analista e do assistente; limpeza noturna do Drive por script (t270) | Não altera regra canônica; não aplica mudança sem o José; não exclui |
| @prod-ideador | Workflow que chama o NotebookLM | Workflow que encaminha tendências/fontes ao NotebookLM, recebe propostas e aplica filtros determinísticos | Não pesquisa nem escolhe tema fora do NotebookLM e das barreiras determinísticas |
| @prod-roteirista | Workflow que chama o NotebookLM | Workflow que pede pesquisa/plano/roteiro ao NotebookLM; lista entidades e valida `RoteiroShort` | Não pesquisa nem redige por conta própria; sem nomes |
| @prod-render | Activity (sem LLM; Temporal/Camofox) | Geração visual pelo Google Flow (primário), Vids (fallback) e pós-processamento aprovado | Nunca gera vídeo no NotebookLM; não julga qualidade |
| @prod-auditor | Código decide; Gemini sim/não; Jev nas checagens de texto | Auditoria pré-publicação + item de conformidade | LLM não dá gravidade nem escreve laudo |
| @prod-seo | Workflow que chama o NotebookLM | Workflow que pede metadados SEO ao NotebookLM e valida `PacoteSEO` | Não redige SEO independentemente nem pede comentário (t263) |
| @prod-publisher | Activity (sem LLM) | `videos.insert` com agendamento; confere ID e código; executa o item 5 em código | Não decide sozinho; não reenvia sem consultar; não exclui; não volta vídeo a público |
| @prod-analista [APROVADO] | Coleta por rotina fixa; agente analisa e propõe (Pydantic v2), aplica só com aprovação do José [t324–t326] | Analytics API; análise semanal ou por anomalia; propostas ao director; Hindsight | Não muda parâmetro sozinho |
| @prod-compliance [APROVADO t198] | Coleta por código + Jev + análise | E-mail do canal, Studio só leitura, Data API; gravidade; HOLD; rascunho de recurso | Nunca recorre, apaga ou altera sem dupla confirmação |
| @prod-comunidade [APROVADO t245] | Rotina fixa + Jev executam; agente faz resumo e propõe (Pydantic v2), aplica só com aprovação do José [t324–t326] | Lê, classifica, retém, responde pelo banco, corações, agrupa temas | Não torna vídeo privado (t250); não escreve texto livre |
| Canal do José (sem agente separado) | Telegram/Hermes `pqbr` + sinais do Temporal (t474) | Consulta, estado/resultados, avisos e aprovações com acesso restrito | Não executa livremente |
| Agentes de dev | LLM (qualquer um) | Tickets de manutenção na produção; tarefas D na construção (ADR-004) | Não faz merge (só o José) |

Personas [APROVADO como fonte]: pt-BR, parafraseadas da Agency Agents (MIT). Comunidade: donchitos `community-manager`, `customer-service.md`, `developer-community-builder`, `feedback-synthesizer`. **Compliance e assistente: sérios e diretos, sem rodeios [t327].** Os agentes passam a ser PydanticAI em activities do Temporal (ADR-011; Paperclip em retirada); o José fala pelo Telegram/Hermes `pqbr` (t474).

## 4. Skills

- **Do Hermes `rede`, viram skills internas (não persona):** `rotina-producao-porqu-br` (máquina de estados, deduplicação, COPPA, fuso UTC×Fortaleza, polling tolerante, "nunca escolher pelo mp4"), `durable-orchestration`, `gemini-web-video-auditor` (só como padrão; vetos visuais obsoletos pela t265), `ecossistema-ponte-multitenant`. Nome da skill nova do fluxo: `rotina-producao-porque-br` (07/10).
- **⚠ Antes de portar qualquer skill do `rede`:** ela destrava o GNOME Keyring com senha por comando (risco); cita CDP 9225 (banido); `produ-o-short-b1` prefere papercut e horário fixo das 19h30 (obsoletos).
- **Da comunidade (com commit fixado):** coreyhaines `copywriting`/`video`, kostja94 `youtube-seo`, supabase/agent-skills, notebooklm-py (oficial), digitalsamba `ffmpeg`, `building-pydantic-ai-agents`. **Não usar:** superpowers/* nem `claude-office-skills/youtube-automation` (aviso do Snyk).
- **Escrever do zero:** `skill-short-form-copy`, `skill-youtube-metadata-seo`, `skill-research-curation`, `pqbr-comentarios-triagem`, `pqbr-comentarios-moderacao`, `pqbr-comentarios-temas`, `pqbr-guia-tom`.

## 5. Ambiente (nomes lógicos; valores reais só na config local)

- Servidor `pc` (casa, acessado pela tailnet). Repositório oficial em `/home/pc/Workspace/PQBR`, GitHub `jvmendesjr/PQBR` (privado, `main`) [VERIFICADO].
- Paperclip só dentro da tailnet, por HTTPS; 443 livre [VERIFICADO t280].
- Dependências globais [VERIFICADO 09/10]: Camofox (REST, saudável), Node, Python/uv, FFmpeg, Docker, gh, NotebookLM CLI 0.8.2 global, Hindsight, GitNexus [t84u–t86u]. As dependências da PQBR são tarefas do roadmap canônico (`docs/ROADMAP.md`).
- Endereços (IP/host da tailnet), IDs de canais/tópicos, tokens e segredos de Telegram ou Discord não entram no Git (REGRAS §17).

## 6. Estrutura do repositório

- `docs/`: README, REGRAS, CONTRATO-EDITORIAL, SPEC, ARQUITETURA, AGENTES, TESTES, ROADMAP (com o PLANO), RASTREABILIDADE, DECISOES-LOG; `hermes-pqbr/` (config viva do perfil `pqbr`); `pesquisas/`, `arquivo/` (estes quatro sob a t287); `docs/sdd/` para relatórios de fase (ex.: ADR-001 do teste).
- `src/pqbr/{schemas,pipeline,integrations,community,guardian,storage}`: código. [PROPOSTA] `src/pqbr/workflows/` depois da ADR-001.
- `db/migrations/` (schema do banco do app), `db/seeds/` (`temas-publicados.csv`: lista de temas já publicados, base da R10).
- `templates/` (relatórios, mensagens fixas, banco de frases), `config/` (só exemplos sem segredo), `tests/`, `scripts/`, `skills/`.
- `company/`, `tasks/`: pendentes da ADR-002.
- `runtime/`: temporário, fora do git.

**Governança transversal (RNF-11/12):** ADR-001 mantém somente o canal Porquê BR; o modelo genérico de dados não libera multi-canal. A cobertura documental é revisada na cadeia canônica e matriz (TS-GOV-01, F00-01). A restrição de leitura de REGRAS §0 deve ser verificada por caso negativo apenas onde existir controle técnico testável, usando fixtures sintéticas isoladas sem ler material real restrito (TS-GOV-02). Nenhum novo mecanismo de bloqueio é declarado implantado; se não houver controle seguro verificável, registrar essa lacuna para o aceite de F00-01/G0.

## 7. Hipóteses

Nada que depende de uma hipótese é construído antes de ela virar VERIFICADO (REGRAS §14). Dono padrão: agente de dev da tarefa D correspondente.

| # | Hipótese | Dono | Critério de pronto |
|---|---|---|---|
| H1 | Auditoria do app do GCP para upload público pela API (t273). Até lá, vídeo sobe privado e o Camofox agenda pelo Studio. Inclui o custo real de cota. | dev | Auditoria concedida e 1 upload público de teste; até lá, fluxo "privado + agendamento pelo Camofox" testado |
| H2 | Agendamento via `publishAt` depois da auditoria | dev | 1 agendamento de teste confirmado pela API |
| H3 | `comments.insert` (`youtube.force-ssl`) funciona sem auditoria | dev | 1 resposta real de teste publicada e conferida |
| H4 | Leitura do canal inteiro via `allThreadsRelatedToChannelId` inclui os Shorts; leitura de `heldForReview`/`likelySpam` com o escopo previsto | dev | Comparar com a leitura por vídeo |
| H5 | [SUPERADA t465] Hipótese histórica de geração de Short vertical até 180 s pelo NotebookLM; geração de vídeo nessa rota desativada (REGRAS §9; ADR-010). | dev | Não executar o ensaio histórico; validar os provedores visuais vigentes no módulo de vídeo, sem presumir integração ou gate aprovado. |
| H6 | `notebooklm usage --json` funciona na conta (medição ativa) | dev | Saída válida gravada; senão, contagem própria |
| H7 | Nome do modelo OpenAI do fallback e paridade com o esquema do Jev | dev | Conjunto de avaliação roda com o mesmo formato |
| H8 | Preço e saldo do Jev; média de gasto | dev | Média dos primeiros dias no relatório |
| H9 | Causa das quedas do Studio (cookies do Chrome vs. identidade do aparelho do Camofox); telemetria do camofox-browser desligada | dev | Sessão estável por N dias com a escada t272, sem cópia de cookies |
| H10 | ~~Juiz visual: Gemini web × Gemini API~~ RESOLVIDO (t327): Gemini web via Camofox. Resta verificar a automação estável em produção | dev | Auditor rodando via Camofox por N dias |
| H11 | Termos de uso comercial do NotebookLM/Gemini; selo de IA desnecessário para stickman | dev (registro) + José | Leitura dos termos registrada; compliance acompanha |
| H12 | Métricas do canal (30 vs. 46 Shorts; bases de retenção diferentes) | @prod-analista/dev | Números fixados pela Analytics API |
| H13 | `hermes_local` + Hindsight num heartbeat real (armazenamento do Hindsight verificado em 09/10, §8; Supabase Pro superado por t343) | dev | Confirmação pelo MCP + 1 heartbeat real |
| H14 | App do GCP em produção (uso interno) sem expiração do token | dev | Token válido além de 7 dias |
| H15 | Cotas reais do NotebookLM na conta (janelas/limites medidos; sem assumir números históricos) | dev | Monitor de consumo da 1ª semana e validação na interface oficial |
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

### Catálogo de erros de produção [José 25/10/2026; APLICADO 0019]
`pqbr.catalogo_erros` guarda os erros já vistos na produção, cada um com a sua prevenção (instrução para o prompt ou a checagem), a severidade e os papéis interessados. Os agentes internos só leem (`catalogo_erros_para_papel` / activity `catalogo_erros_consultar`, contrato `ErroCatalogo` v1.0.0) antes de gerar. Quem cadastra é o agente externo (t538-P). RLS: `pqbr_app` grava e `pqbr_leitura` lê. Detalhes: `docs/CATALOGO-ERROS.md`; mapa: `docs/mapa/10-catalogo-erros.mmd`.

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
| `EpisodioWorkflow(ep)` | grade do dia | pacote canônico → caderno do episódio (id) → roteiro (NotebookLM) → fichas → render → pós FFmpeg → auditor → arquivar caderno → Drive → aprovado → `ApagarCadernoWorkflow` D+2 | RF-06..RF-14, RF-40 |
| `PublicacaoWorkflow(ep)` | episódio aprovado | busca do código → `videos.insert` privado → agendar (API ou Camofox) → conferir | RF-15..RF-18 |
| `Item5Workflow(video)` | sinal de problema | privado na hora → canal ativo (Telegram/Hermes `pqbr`; t474) → aguarda sinal do José | RF-19..RF-21 |
| `ComentariosWorkflow` | Schedules 30 min / 6 h / diário | ler → pré-filtro → Jev → reter/responder/sinalizar | RF-22..RF-27 |
| `ComplianceWorkflow` | Schedule + antes de cada janela | coleta → gravidade → HOLD se crítico | RF-28, RF-29 |
| `GuardiaoSessaoWorkflow` | Schedule ~20 min com variação | testa Studio, Gemini, NotebookLM → escada t272 | RF-37 |
| `AnalistaWorkflow` | Schedule diário/semanal | coleta → agente analisa → `PropostaAgente` | RF-30, RF-33 |
| `RelatorioDiarioWorkflow` | Schedule noturno | junta dados → template → canal ativo (Telegram/Hermes `pqbr`; t474) | RF-31, RF-32 |
| `LimpezaDriveWorkflow` | rotina noturna do @prod-director | duplicatas/órfãos → `_duplicados` → lista ao José | RF-41 |
| `MonitorAtualizacoesWorkflow` | Schedule semanal | lê releases → Jev → pede autorização | RF-42 |
| `RevisaoHumanaWorkflow(item)` | item que falhou em todos os caminhos | guarda → avisa → aguarda determinação | RF-36 |

- **Filas:** `notebooklm` (concorrência 1), `camofox` (concorrência 1), `render`, `default`.
- **Sinais:** `aprovacao_jose` (proposta, ticket, volta a público), `pausar_respostas` / `retomar_respostas`, `determinacao_revisao` (excluir/corrigir/reaproveitar/arquivar), `hold_fila`.
- **Retentativas:** `RetryPolicy` 30 s → 2 min → 8 min; espera de rede sem gastar tentativa; 2 falhas da mesma ação → correção autônoma limitada a até 3 tentativas, com verificação do auditor/Jev; esgotamento → José, preservadas as chamadas imediatas por ação sensível ou demais travas de REGRAS §3.1; 5 idênticas → parada (REGRAS §18).
- **Janelas:** 11:40, 14:40, 18:35, 21:15 (America/Fortaleza).

## 10. Agentes PydanticAI no Temporal (ADR-011, t510)

- **Padrão:** agente = persona (`company/agents/<papel>/AGENTS.md`, sem frontmatter) + combo do 9router (`config/modelos_9router.json`) + contrato de saída Pydantic v2 (`src/pqbr/contratos`). Fábrica e registro em `src/pqbr/agents/` (`criar_agente`, `rodar`, `REGISTRO`).
- **Modelo:** `OpenAIChatModel(<combo>, provider=OpenAIProvider(base_url=<PQBR_9ROUTER_URL>, api_key=<NINEROUTER_API_KEY>))`; URL padrão `http://127.0.0.1:20130/v1` (20128 também responde, mas resolve os combos para outros modelos; mantido 20130, que já era o do kit). Fallback opcional por papel (`FallbackModel`, ex.: Líder Editorial `core-medio` → `core-baixo`). Chave só pelo `EnvironmentFile` 600 do worker; nunca logada.
- **Regra:** o agente roda dentro de uma activity e **só gera e valida** (`result.output` já é o contrato). Efeitos (Postgres, Telegram, Drive, publicação) ficam em activities separadas, com retry do Temporal.
- **Ferramentas do agente [PROPOSTA t134u; NÃO aplicada]:** catálogo só leitura em `src/pqbr/agents/ferramentas.py`, liberado por papel pela `config/politica_papeis.json`, como ferramenta nativa do PydanticAI no processo da activity, com limite de chamadas. MCP não entra aqui: ele fica só na fronteira com agentes externos (`pqbr-mcp`).
- **Acompanhamento de mudanças [PROPOSTA t135u; NÃO aplicada]:** sem agente novo (t136u). Vigias como Schedule do Temporal, só leitura: canário de interface no Camofox (sítios do `mapa_cliques.json`; o NotebookLM fica fora, é CLI), vigia de fallbacks, deriva de contrato por fixture, `dev_diagnosticar` no fim e aviso com `aprovacao_jose`.
- **Jev [JEV-EF, t137u; NÃO ligado]:** oráculo de pergunta fechada. O código pergunta, o Jev devolve contrato Pydantic, o código valida e age. Porta `src/pqbr/motores/decisao.py` ainda não existe.
- **Registro:** cada execução devolve `meta` (papel, combo, combos, modelo que respondeu, fallback, tokens), gravado no histórico do Temporal (resultado do workflow) e no journal do worker (`pqbr.agents`). Limite: o 9router devolve o modelo real, não o combo; fallback interno do 9router não aparece como `fallback=true`.
- **Primeira migração:** `ReposicaoTemasWorkflow` (t512/t513): `temas_situacao` → `pedido_temas` (Líder Editorial monta o pedido) → `motor_consultar` (porta MotorIntelectual, fila `notebooklm-pqbr`, caderno efêmero semanal `Short - grade-temas-<ano>w<semana>`, nunca mestre) → `temas_validar_agente` (parse JSON; PydanticAI só se preciso) → `temas_inserir` (filtros determinísticos + escrita).
- **Aprovação do José:** Telegram (Hermes `pqbr`) → sinal `aprovacao_jose` no Temporal; rota valida ID autorizado, tarefa e estado e falha fechada.
- **Run preso:** `scripts/temporal/runs_presos.py` (timer `pqbr-runs-presos`, de hora em hora; > 6 h → WARNING no journal). Alerta por Telegram fica para quando o bot `pqbr` tiver token de entrega.
- Texto anterior (integração Paperclip/Hermes): `docs/_obsoleto/paperclip-trechos-t510.md`.

## 11. Interfaces: contratos Pydantic v2 [PROPOSTA; fixados em F3-01]

| Modelo | Campos principais | Usado em |
|---|---|---|
| `RoteiroShort` | falas, `tipo_cta` (`trocadilho_tema`/`convite_seguir`/`fallback`), duração estimada (15–180 s, alvo ~50 s, ~2,3 palavras/s), entidades da cena, sem nomes | RF-07 |
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

## Modelos 9router por papel (José 12/10 14:02)
Toda chamada ao 9router de worker ou script usa `pqbr.kit.router9.combo(papel)` / `chat_papel`, lendo **`config/modelos_9router.json`** (fonte única, mesmo mapeamento dos agentes Paperclip): core-alto = Diretor, Roteirista, Auditor, Devs; core-medio = Pesquisador de Origem, Líder Editorial, Compliance, Guardião; core-baixo = Observador, SEO, Caçador Sazonal, Comunidade, Diretor de Arte, pqbr; core-revisao = revisões e segundas opiniões. Proibido nome de combo fixo no código.


## 12. Conhecimento por papel: Hindsight + GitNexus (t84u–t86u, 26/10/2026)
- **Pré-requisitos de instalação (fail-closed):** Camofox (`scripts/camofox/verificar.sh`), Hindsight (bank `pqbr`, `scripts/hindsight/`) e **GitNexus** (`scripts/gitnexus/verificar.sh`: binário, versão ≥ 1.6.12 e índice da PQBR registrado). Realocou o app ⇒ instalar o GitNexus global antes.
- **GitNexus é global do servidor**, compartilhado com outros apps e fora do repo: Node 22 em `~/.local/opt/node22`, `gitnexus` no prefixo npm dele, wrapper `~/.local/bin/gitnexus`, registry em `~/.gitnexus/`. A PQBR só registra o índice dela (`.gitnexus/` no repo, ignorado pelo git) com `analyze --index-only` (sem AGENTS.md, skills ou hooks do GitNexus no repo). Reindexa em segundo plano no `post-commit` (`scripts/gitnexus/hook-post-commit.sh`). Interface: CLI e MCP **stdio**; `--http` proibido (nada na rede ou tailnet).
- **Política por papel:** `config/politica_papeis.json` (contrato `pqbr.contratos.politica`). Para cada papel (8 PydanticAI + `mantenedor` externo + `indexador` de serviço): tags que lê, tags que escreve, prefixos de código visíveis no GitNexus e ferramentas. Aplicada em `storage/hindsight.py` (`reter` exige `papel`+`tags`; `recuperar` filtra no pedido e na volta) e em `integrations/gitnexus.py` (filtra resultados por caminho; só `query|context|impact`). Papel desconhecido ⇒ negado.
- **Licença:** GitNexus é PolyForm Noncommercial 1.0.0. **Aceita pelo José em t90u (26/10/2026):** a PQBR é de uso pessoal, sem revenda nem inclusão em produto vendido.
- **Servidor MCP da PQBR (t89u):** dentro da aplicação (`src/pqbr/mcp/`), unit `pqbr-mcp` (systemd de usuário, `infra/mcp/pqbr-mcp.service`), bind 127.0.0.1:8791 e exposto **só na tailnet** por `tailscale serve` (HTTPS 8791, sem Funnel). Transporte Streamable HTTP (POST `/mcp`, JSON; sem SSE). Identidade por token Bearer por cliente, **exclusivo do papel `mantenedor`** (t114u, 0.4.0; política 1.4.0: lê todas as tags, vê o repo todo): só o sha256 em `~/.pqbr/secrets/mcp_clientes.json` (600; permissão aberta ⇒ nada aceito); token criado por `scripts/mcp/novo_cliente.py`. Ferramentas **só leitura**, liberadas pela política: `onboarding`, `buscar_memoria` (`memoria_buscar`), `codigo` (`gitnexus_consultar`), `estado` (`estado_ler`). `AGENTS.md` é gerado do onboarding (`scripts/mcp/gerar_agents_md.py`); a base manual ficou em `docs/operacao/AGENTS-base.md`.
- **Memórias sem tag (t89u):** a recuperação filtra por tags no servidor (`tags` no recall funciona no Hindsight 0.10.2). Memórias anteriores a t84u não têm tag e ficam invisíveis à política até serem reclassificadas.
- **Regra única de tags (t90u/t90s398):** `pqbr.storage.hindsight_tags` dá as tags de conteúdo (origem + palavras-chave, filtradas pela política) ao indexador e à reclassificação; o legado foi reclassificado e as obsoletas apagadas com backup (`docs/operacao/hindsight-descarte-candidatos.md`).
- **Escrita pelo MCP (t95u/t96u):** `registrar_memoria`/`registrar_alteracao` (`pqbr.contratos.memoria_mcp`), só para papel com `memoria_registrar`; tags ⊆ escrita do papel; autor `autor:<cliente>` vem do token; commit verificado no repo.
- **Mantenedor e persistência (t112u–t117u):** o MCP externo só aceita `mantenedor` (token de outro papel ⇒ 401; `X-PQBR-Papel` diferente ⇒ 403). Ele constrói e liga módulos (contrato → porta/adaptador por config → worker Temporal → testes → docs/mapa → `registrar_alteracao`); reinício/migração com OK do José. Persistência: `pqbr-mcp` e `hindsight-api` são user units enabled (linger=yes), containers DB/Temporal `unless-stopped`; checagem em `docs/operacao/onboarding-agente-externo.md`.
- **Handoff (t98u/t99u):** `docs/ESTADO-ATUAL.md` é a fonte única de onde estamos; 1ª seção do onboarding/AGENTS.md. O pre-commit (`scripts/seguranca/verificar_estado_atual.py`) o exige quando ROADMAP/LACUNAS/DECISOES-LOG/CHANGELOG mudam; `registrar_alteracao` com `tipo` correcao/pendencia_resolvida o exige no commit e grava um handoff (tag `estado`, política 1.3.0, lida por todos). Diagrama: `docs/mapa/13-memoria-mcp-handoff.mmd`.
