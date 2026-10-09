# Entrega à core-eng: blueprint da org PQBR (Porquê BR)

> **Para:** @eng-cto (org core-eng, Paperclip) · **Dono:** José Vieira · **Data:** 09/10/2026 (horário de Fortaleza)
> **Pedido:** escrever e construir o blueprint da nova org Paperclip **PQBR**, que opera o canal de YouTube Shorts **"Porquê BR"** (vídeos de stickman com sátira leve sobre hábitos brasileiros).
> **Fontes (são a verdade):** `prep/decisoes-jose-2026-10-08.md` (vence em conflito; a entrada mais nova vale mais que a antiga), `prep/dossie-preparacao-pqbr.md`, `prep/contrato-editorial-pqbr-rascunho.md`, `testes/2026-10-08/auditor/PESQUISA-comentarios-boas-praticas.md`, `PESQUISA-agente-comunidade.md`, `PESQUISA-auditoria-av-comunidade.md`, `auditor/v3/RUNBOOK.md`, `auditor/v3/resultados/RESUMO.md`, `final-round/v2-r3/RELATORIO-v2-r3.md`. Os códigos "tNNN" remetem às entradas do registro de decisões. **Revisão de 09/10 (10:23):** incorpora t271–t274 e resolve as contradições que existiam entre as fontes; as regras resolvidas estão marcadas como [APROVADO]. Os documentos antigos que ainda divergem (contrato v1, RUNBOOK v3b, RELATORIO-v2-r3) são atualizados pela tarefa D11.
> **Legenda (item 7, regra do blueprint):** **[VERIFICADO]** = testado ou visto na fonte real · **[HIPÓTESE]** = a confirmar pela core-eng antes de construir o que depende dela · **[APROVADO]** = decisão do José. Uma decisão aprovada não prova que a ferramenta consegue executá-la.
> **Regra de trabalho:** antes de dar um papel a um componente, conferir a ficha dele neste documento (t230). Mudanças durante a construção voltam ao blueprint como **tarefas de desenvolvimento**. Tickets ficam só para a produção (t187, item 7).

---

## 1. Objetivo e fronteiras

- **Objetivo [APROVADO]:** produzir, auditar e agendar até 4 Shorts por dia no "Porquê BR", com autonomia máxima e intervenção humana mínima. Determinismo vem antes de LLM: início automático, grade correta do dia, nenhum tema repetido e "publicado" só com ID confirmado (decisão ESTABILIDADE).
- **Nome [APROVADO]:** a org se chama **PQBR**. Os documentos explicam a sigla (Porquê BR). O canal usa "porquê" por extenso. Os documentos antigos que falam em "porquebr-production" ou "PorqueBR Production" devem ser ajustados.
- **Promessa (rascunho do contrato):** "O Porquê BR pega uma mania que todo brasileiro tem, ri dela junto com você e mostra por que a gente faz isso."
- **Fases [APROVADO]:** construção → **validação** (7 itens, com prioridade para 1, 2 e 3) → produção. A core-eng só libera a produção quando cada item cumpre o seu critério de aceite.
- **Quem pode o quê [APROVADO]:**
  - José altera as regras canônicas, aprova merges e é a autoridade final.
  - @prod-director altera parâmetros operacionais.
  - core-eng altera código e infraestrutura, por ticket na produção ou por tarefa de dev na construção.
  - Os demais agentes só propõem.
- **Fora do escopo:**
  - comentar em outros canais;
  - excluir vídeos ou comentários, rejeitar comentários ou banir autores (só José);
  - republicar um vídeo corrigido;
  - atualizar dependências sem autorização;
  - publicar vídeo reprovado para bater a meta.
- **Base de template [APROVADO no dossiê como recomendação; o formato final cabe à core-eng]:** pacote próprio `pqbr-company/` no formato Agent Companies (COMPANY.md, TEAM.md, AGENTS.md, SKILL.md, TASK.md, `.paperclip.yaml`), com as personas em pt-BR adaptadas da Agency Agents (MIT, parafraseadas). Importar primeiro com `--dry-run` e fixar `--ref <commit>`, porque o repositório `paperclipai/companies` está parado desde 23/03/2026 [VERIFICADO]. Os agentes importados chegam com heartbeat desligado [VERIFICADO na doc do Paperclip].
- **Perfil Hermes dedicado `pqbr` [APROVADO]:** o @pqbr-assistente roda nele. Env mínimo, toolsets restritos e budgets antes de ligar os heartbeats. O perfil **não** herda o `--yolo` nem o sudo sem senha do `rede` (risco apontado no dossiê §f.5).

## 2. Agentes

Princípio [APROVADO, t184]: **ideação, roteiro, SEO e pesquisa ficam com o NotebookLM.** Os agentes orquestram: entregam o conhecimento, reforçam com pesquisa própria, extraem a saída por código, validam com Pydantic, conferem com o Jev e acompanham com observabilidade. Os módulos determinísticos (preflight, render, publisher, backup) não usam LLM (blueprint v3.3, segundo o dossiê).

| Agente | Papel / o que faz | NÃO faz | Ferramentas | Fonte de persona |
|---|---|---|---|---|
| **@prod-director** | Coordena a cadência, as rotinas e os parâmetros operacionais. Recebe as propostas de ajuste do analista e do assistente. Roda a **limpeza noturna do Drive** por script (t270). | Não altera regras canônicas. Não exclui nada. | Rotinas TASK.md, Supabase, Telegram (via assistente) | `project-management-studio-producer` / `agents-orchestrator` (Agency) + o padrão "CEO pausado" do GStack. LLM ou rotina determinística: **decisão em aberto** (dossiê g.10) |
| **@prod-ideador** | Orquestra a grade: entrega a coleta e as fontes ao caderno de tendências e recebe os temas filtrados. | Não escolhe tema sem passar pelas barreiras de repetição. Não libera tema bloqueado. | NotebookLM (Deep Research), YouTube Data API, Supabase | `product-trend-researcher`, `academic-historian/anthropologist`, `specialized-cultural-intelligence-strategist` |
| **@prod-roteirista** | Orquestra o roteiro no NotebookLM, lista as entidades da cena (fichas) e valida o `RoteiroShort`. | Não redige fora do NotebookLM/Gemini web. Não usa nomes de personagens no vídeo. | NotebookLM, Pydantic, resolvedor de fichas (sem LLM) | `marketing-content-creator`, `narrative-designer` |
| **@prod-render** | Executor determinístico: gera o vídeo no NotebookLM e faz a pós (FFmpeg: corte do end card, logo). | Não julga qualidade. | notebooklm-py (serviço PQBR), FFmpeg | sem persona (script); `marketing-short-video-editing-coach` só como "olho" |
| **@prod-auditor** | Auditoria pré-publicação (§6): o código extrai quadros e transcrição, o Gemini responde sim/não, o Jev cuida das checagens de texto e o código decide. Também cuida do item de conformidade (variedade, tom de especialista, direitos de áudio). | Não deixa o LLM dar a gravidade nem escrever o laudo. | Whisper, PySceneDetect, OCR, Gemini (visual), Jev, `decide.py` | `testing-reality-checker`, `testing-evidence-collector`, `qa-director` |
| **@prod-seo** | Orquestra título e descrição (NotebookLM) e coloca o código PQBR-EPxxxx na descrição e na etiqueta. | Não pede comentário na descrição (t263). | NotebookLM, Pydantic, Jev (marca/pessoa/obra de terceiros) | `marketing-seo-specialist` + `youtube-seo` (kostja94) |
| **@prod-publisher** (o "agente do Studio" das decisões) | Executor determinístico: envia pela API (`videos.insert` com agendamento) [APROVADO t273], agenda e confere o ID e o código. Executa a **regra do item 5 em código** que torna o vídeo privado [APROVADO t250]. | Não decide sozinho tornar privado: quem decide é a regra em código. Não reenvia sem consultar o Supabase e o canal. Não exclui. Não volta vídeo a público sem o toque do José. | YouTube Data API (primária); Studio via Camofox (reserva e, até a auditoria do app, agendamento dos vídeos enviados como privados; H1) | sem persona (script) |
| **@prod-analista** [APROVADO] | Coleta diária por código pela Analytics API. Análise semanal ou quando há anomalia. Propõe ajustes ao director e grava os aprendizados no Hindsight. **Só observa até ~30 Shorts / 90 dias.** Entrega relatórios pedidos pelo assistente. | Não muda parâmetro sozinho. | YouTube Analytics API (OAuth, só leitura); Camofox no Studio só como reserva | `support-analytics-reporter`, `testing-test-results-analyzer` |
| **@prod-compliance** [APROVADO t198] | Observa a conformidade. A coleta é por código (e-mail do canal, Studio só leitura, Data API) e o Jev classifica a gravidade. Prepara o rascunho de recurso. | Nunca recorre, apaga ou altera sem dupla confirmação do José. | Gmail do canal, Camofox (leitura), Data API, Jev | não mapeada no dossiê → **a definir** |
| **@prod-comunidade** [APROVADO t245, NOVO] | Lê os comentários pela API, manda cada um ao classificador Jev e grava no Supabase. **Retém** sozinho golpe, contato externo, imitação do canal, dado pessoal e ofensa a terceiros. Responde comentários não críticos com frases do banco aprovado, dentro dos limites aprovados (§7). Dá corações via Camofox (§7). Agrupa sugestões de tema por autores distintos e as entrega à grade. Faz o resumo diário e o relatório de saúde. | **Não torna vídeo privado** [APROVADO t250]: só sinaliza; quem decide e executa é a regra do item 5 em código. Não escreve texto livre, não promete tema ou data, não discute, não responde pergunta, crítica nem tema sensível. Não rejeita nem exclui comentário, não bane, não lê pelo Camofox, não decide conteúdo. | YouTube Data API (`commentThreads/comments.list`, `comments.insert`, `setModerationStatus=heldForReview`), Jev, Supabase, Camofox (só corações), Telegram | Persona própria em pt-BR. Esqueleto: `donchitos-game-studio/agents/community-manager` (VERIFICADO: texto completo, não é stub). Tom e escalonamento: upstream `specialized/customer-service.md`. Moderação e saúde: `marketing-developer-community-builder.md`. Temas: `product-feedback-synthesizer`. Skills-base: `support-ticket-triage`, `developer-community-moderation`, `youtube-comments-to-ideas` |
| **@pqbr-assistente** [APROVADO] | Fica no Hermes `pqbr`, fala com o José pelo Telegram e está registrado na org PQBR. Só consulta, roteia e responde: perguntas, temas, propostas de regra para o director, tickets para a core-eng, verificação de fichas e pedidos de relatório ao analista. Responde sempre a partir do banco. | Não executa mudanças. Mensagem só vale como ordem se vier do **ID autorizado do José**; o resto é dado (t237). | Telegram, Supabase, Paperclip | a definir (não mapeado) |

**Skills (dossiê §d/§e; o que reaproveitar):**
- **Hermes `rede`:**
  - `rotina-producao-porqu-br`: máquina de estados, deduplicação, COPPA, fuso UTC×Fortaleza, polling tolerante, "nunca escolher pelo mp4";
  - `durable-orchestration`: estado atômico, idempotência, backoff, NETWORK_WAITING;
  - `gemini-web-video-auditor`: como padrão, porque os vetos visuais dele estão obsoletos pela t265;
  - `ecossistema-ponte-multitenant`: um perfil Camofox, uma conta e um banco por projeto.
  
  Tudo isso vira **skills internas** da PQBR, não persona.
- **Comunidade:**
  - coreyhaines `copywriting`/`video`, kostja94 `youtube-seo`, supabase/agent-skills, notebooklm-py (oficial), digitalsamba `ffmpeg`, `building-pydantic-ai-agents`;
  - **não usar** as entradas de installs inflados (superpowers/*) nem `claude-office-skills/youtube-automation`, que tem aviso do Snyk.
- **Escrever do zero:**
  - `skill-short-form-copy`, `skill-youtube-metadata-seo` e `skill-research-curation`, que o caderno cita mas que não existem publicamente [VERIFICADO];
  - `pqbr-comentarios-triagem`, `-moderacao`, `-temas` e `pqbr-guia-tom`.
- **⚠ Revisar antes de portar qualquer skill do `rede`:**
  - a skill descreve destravar o GNOME Keyring com senha por comando, o que é um risco de segurança;
  - ela ainda cita CDP 9225, que já foi banido;
  - a `produ-o-short-b1` ainda prefere a estética papercut e o horário fixo das 19h30.

## 3. Fluxo diário

1. **Madrugada: grade [APROVADO t198/t199]**
   - O código coleta as tendências (Data API: em alta BR + Shorts mais vistos em 24–48 h com termos do escopo).
   - Junta o resumo diário de comentários (≤ ~300).
   - Tudo vai para o **caderno diário de tendências**, separado do raiz e limpo todo dia.
   - NotebookLM Deep Research (1 das 20 diárias) filtra para a sátira stickman.
   - Os filtros em código aplicam as 3 barreiras de repetição, a variedade do compliance, as exclusões sensíveis e a pontuação de polêmica.
   - A grade vai para o Supabase com pontuação e fonte. A grade é gerada **por código a partir da data**.
   - **Mistura: ~70% em alta / ~30% perenes.**
2. **Manhã: produção, pós e auditor [APROVADO item 4]**
   - Teste de resposta antes do lote (§5).
   - Pausas em ritmo humano e limites de uso por modelo/ferramenta calculados para o dia.
   - `notebooklm usage --json` antes e depois de cada geração: acima de 80% numa janela, o agendador espaça as produções.
   - Há um prazo de corte.
   - Falhas: refazer ou trocar pela reserva durante a manhã. O que ficar pendente vai para o José **antes da primeira janela**.
   - Referência histórica do `rede`: lote das 06:00 às 09:30 com jitter de 12–18 min [HIPÓTESE de horário].
3. **Agendamento nas janelas [APROVADO]**
   - Os aprovados ficam **AGENDADOS** nas janelas definidas. Via [APROVADO t273]: YouTube Data API (`videos.insert` com agendamento, `publishAt`). Até a auditoria do app (H1), o vídeo sobe **privado** e o Camofox agenda pelo Studio. O Studio via Camofox também é a reserva quando a API falha.
   - A **última janela** do dia sai, de preferência, dos 30% perenes.
   - Checagem extra da sessão ~30 min antes de cada publicação. Antes de cada horário, confirmar que não há advertência ativa (compliance).
   - **Horários das janelas: pendentes** (§11).
4. **Reserva [APROVADO]:** **≥ 2 vídeos aprovados** em estoque. Horário perdido: entra um vídeo da reserva; sem reserva, o horário é cancelado. Atraso de até 1 h é só plano B.
5. **Teto [APROVADO]:** **4 por dia, sem mínimo.** Qualidade vem antes da cota.
6. **Estados [APROVADO]:** aprovado → enviando → enviado (video_id) → agendado → publicado. Cada passo tem checkpoint. "Publicado" só com o ID confirmado.
7. **Noite:** limpeza do Drive (§9) e relatório diário (produção, consumo NotebookLM/Jev, compliance, comunidade).
8. **Monitor de atualizações [APROVADO t186/t196], semanal:**
   - Cobre notebooklm-py, Camofox/camofox-browser, Camoufox, Paperclip, Hermes, FFmpeg, Whisper, Pydantic, Supabase CLI e Jev SDK.
   - O Jev julga a relevância e o José autoriza no Telegram.
   - Depois vem a tarefa ou o ticket: worktree, smoke test isolado, versão fixada e rollback.
   - **Nunca atualiza sozinho.**

## 4. Componentes e papéis

| Componente | Papel | Status |
|---|---|---|
| **NotebookLM** (notebooklm-py) | **Primário** para ideação, roteiro, SEO, pesquisa e geração de vídeo. Usa caderno **efêmero por episódio** (o caderno mestre foi banido por contaminação). Adicionar o roteiro como fonte antes de gerar. Timeout: listar artefatos, não regerar. Nunca usar `ask --new`. | [APROVADO] / hábitos [VERIFICADO no rede] |
| | Instalação **exclusiva da PQBR**: venv com **0.8.4 fixada**, `NOTEBOOKLM_HOME=/home/pc/.pqbr/notebooklm`, perfil `pqbr`, um serviço único dono da sessão (refresh por timer, fila de uma tarefa). Hoje existe uma instalação global 0.8.2 compartilhada com o MP32 [VERIFICADO]. | [APROVADO em princípio] |
| | Limites do Pro: janela de 5 h + teto semanal; 500 chats/dia, 20 vídeos/dia, 300 fontes/caderno, 500 cadernos. `notebooklm usage --json` na 0.8.4 depende de a conta ter medição ativa; se não tiver, usar contagem própria + `retry_after_seconds`. | [HIPÓTESE] |
| | Duração [APROVADO t271]: de 15 s a 3 min, **alvo de ~50 s**. Shorts verticais acima de 60 s já saíram bem (finais de 61,9–63,0 s depois do corte, e 63,9–67 s em rodadas anteriores). | [VERIFICADO até ~67 s]; até 180 s [HIPÓTESE] |
| | Com 2 personagens, o Short ignora as imagens de elenco (5 de 5 gerações falharam); 1 personagem funcionou (V1). O "estilo próprio" não é aceito no formato Short. | [VERIFICADO] |
| **Gemini web** | **Reserva** do NotebookLM (ideação/roteiro) e **juiz visual** do auditor: 3.8 Flash no modo normal, conta jvmendesjr nos testes. O "Flash Estendido" recusa as pranchas. | [APROVADO] / recusa [VERIFICADO] |
| | Operação automatizada do Gemini web em produção (via Camofox) vs. Gemini API (free tier: dados usados para treino; criar a chave é decisão do José, ainda não feita). | [HIPÓTESE / em aberto] |
| **Jev** (TypeSafe) | Interface única `decide()`, com provedor trocável. Devolve **só decisões estruturadas** (sim/não, classe, JSON). **Nunca redige texto.** Faz: repetição (barreira 2), roteamento do assistente, correspondência de fichas, checagens de texto do auditor, gravidade de tickets e e-mails, classificação de comentários e mensagens, segunda camada de PII/segredo, marca/pessoa/obra de terceiros, refazer/trocar/chamar José, conferência agendado × aprovado. **Não cabe:** imagem/vídeo/áudio, texto, julgamento jurídico, barreira única de segredo, exclusão. | [APROVADO] |
| | **Fallback, nesta ordem:** (1) o mesmo Jev via OpenRouter; (2) modelo OpenAI, direto ou via OpenRouter. O nome do modelo é HIPÓTESE. Mesma validação Pydantic, formato inalterado. Fallback ainda não avaliado: só alerta, sem ação automática. | [APROVADO] / modelo [HIPÓTESE] |
| | Preço informado pelo José: US$ 0,042/1M tokens; saldo > US$ 4 de US$ 5 grátis. Sem monitor em tempo real: média de gasto calculada pelos tokens por chamada nos primeiros dias. Limiares de confiança calibrados com casos reais; confiança baixa vai para um LLM ou para o José. | [HIPÓTESE] / [APROVADO] |
| **Camofox** (jo-inc/camofox-browser sobre o Camoufox, :9377, perfil `porquebr`) | **Obrigatório (inegociável)** para toda automação de navegador: mouse humano, colar texto longo, digitar texto curto com cadência humana. O ritmo é da camada do Camofox. O Jev só responde perguntas pontuais sobre o texto/DOM. **Único dono do login do Studio.** Login inicial manual pelo noVNC do próprio Camofox (preso ao localhost/Tailscale, com senha, desligado fora do login). Sem Camoufox separado. | [APROVADO] |
| | Papel na publicação [APROVADO t273]: **reserva** da API; até a auditoria do app, agenda os vídeos que a API enviou como privados. | [APROVADO] |
| | Telemetria de crash do camofox-browser vem ligada por padrão: verificar e desligar. A causa das quedas do Studio (cookies do Chrome copiados e/ou identidade do aparelho mudando entre reinícios) ainda está sem prova. Risco de ToS ("automated means") registrado no dossiê. | [HIPÓTESE] |
| | Dicas do Studio [VERIFICADO no rede]: ir direto a `/videos/upload?d=ud`; `execCommand('insertText')`; marcar o rádio COPPA "não é para crianças"; paginar 30 por vez; challenge de passkey → humano; upload só de `~/.camofox/uploads/`. | |
| **YouTube Data API** | Grade (em alta), comentários (`commentThreads.list` = 1 unidade/página de 100), respostas (`comments.insert` = 50), retenção (`setModerationStatus` = 50), `videos.update` = 50, status por vídeo. Cota de 10.000/dia com reset à meia-noite do Pacífico (~04:00–05:00 em Fortaleza). `search.list` e `videos.insert` têm balde próprio de 100/dia. Não há endpoint de coração/like. | [VERIFICADO na doc] |
| | Publicação [APROVADO t273]: `videos.insert` com agendamento é a via primária. Ainda a confirmar: auditoria do app para upload público (H1), `publishAt` (H2), custo real e `comments.insert` sem auditoria (H3). | [APROVADO] / detalhes [HIPÓTESE] |
| **YouTube Analytics API** | Coleta diária do analista. OAuth só leitura, app do GCP publicado em produção (uso interno) para o token não expirar. As definições de métrica são fixadas pela API, porque as duas fontes do rede divergem. | [APROVADO] / números [HIPÓTESE] |
| **Supabase** | Estado e verdade: grade, temas (R10), máquina de estados, `visual_assets`/`episode_assets`, comentários (rótulos), ações (motivo/quem/quando), uso do NotebookLM/Jev, flag do kill switch. Plano Pro não confirmado pelo MCP. Migração do `yt_production` local e local do schema Hindsight: em aberto (dossiê g.3/g.4). | [APROVADO] / plano [HIPÓTESE] |
| **Google Drive** | Armazenamento definitivo (§9). Conta Pro de 5 TB, sem restrição de cota. | [APROVADO t266/t267] |
| **Telegram** (via @pqbr-assistente) | Avisos, botões de verificação de fichas ("Verificado" / "Não Aprovado" + observação, sincronizados com o Paperclip pela mesma tabela), toques de aprovação, `/pausar_respostas`, `/retomar_respostas`. | [APROVADO] |
| **Hindsight** | Aprendizados (analista, lições do item 5). Sem segredos nem PII. O caminho `hermes_local` num heartbeat real ainda não foi testado. | [HIPÓTESE] |
| **Whisper / FFmpeg** | Transcrição com tempos (o Whisper ouve "Porquê BR" como "por KBR"; a checagem aceita as variantes). Pós: corte do end card **só se detectado** (end card de 3,1 s detectado e cortado nas 3 tentativas da V2-r3) + logo com zoom suave curto sobre a última fala. | [VERIFICADO] |

## 5. Regras de falha e saúde

- **Guardião determinístico da sessão [APROVADO t195]:**
  - Código, com timer de ~20 min com variação. Testa Studio, Gemini Web e NotebookLM. Checagem extra ~30 min antes de cada publicação.
  - **Escada de recuperação [APROVADO t272]:** (1) o Camofox renova a sessão; (2) login manual pelo noVNC, com aviso no Telegram. A cópia de cookies do Chrome é **só o último recurso e exige o OK do José** (os cookies copiados são a causa provável das quedas, t194).
  - A publicação fica em espera e retoma sozinha.
  - Renovação que falha: Telegram + ticket automático.
  - O agente só observa e só age com roteiro pronto quando a escada esgota.
- **Teste de resposta (ping) [APROVADO t241]:** antes do lote da manhã e antes de cada ação crítica (agendar, tornar privado), o código faz uma chamada mínima a cada modelo e ferramenta (Jev, Gemini, NotebookLM, Supabase). Sem resposta no prazo ou com resposta inválida, entra a escada.
- **Escada de falhas [APROVADO; aplica-se a modelos, Supabase e 9router]:**
  - backoff 30 s → 2 min → 8 min;
  - rede fora = `NETWORK_WAITING`, sem gastar tentativa;
  - cada nova tentativa usa **outra estratégia** (outro provedor ou combo);
  - a mesma ação falhando **2×** vai para o José;
  - **5 chamadas idênticas** = parada;
  - idempotência antes de cada passo e varredura de recuperação no reboot;
  - `quotaExceeded` = espera o reset, sem nova tentativa.
- **Supabase fora [APROVADO t242]:** buffer local (fila em arquivo, gravação atômica). Nada é agendado nem tornado público sem gravar o estado. A sincronização acontece quando o Supabase volta.
- **Publicação sem duplicidade [APROVADO item 4]:**
  - Código único PQBR-EPxxxx na descrição e numa etiqueta.
  - Antes de enviar, procurar o código no Supabase **e no canal**, incluindo privados e **agendados**.
  - Envio sem confirmação: procurar o código, tentar 1×; se a dúvida continuar, parar e avisar o José.
  - Nunca escolher o que publicar pela simples existência do mp4.
- **Estabilidade [APROVADO]:**
  - agendador do SO com horários fixos + vigia de prazo;
  - tema repetido barrado em 3 barreiras;
  - agente responde sempre pelo banco;
  - relatório diário;
  - o corte do sistema antigo só acontece depois de vários dias sem falha.
  - Origem: o incidente de 08/10 (fluxo não iniciou; grade do dia 7 reaproveitada; 3 de 4 temas repetidos).
- **HOLD de conformidade [APROVADO]:**
  - Gatilho: evento crítico (aviso/strike, aviso de conteúdo inautêntico, remoção).
  - Efeito: HOLD da fila + vídeos já agendados viram privados + Telegram + ticket + prazo de recurso monitorado.
  - Eventos de atenção (claim, anúncio limitado) vão para o Telegram e viram lição para os roteiros.
- **Correção pós-publicação [APROVADO item 5, t239, t245]:**
  - **Qualquer** problema detectado torna o vídeo **privado na hora**, automaticamente, com Telegram e motivo.
  - Sem substituição e sem republicação.
  - Volta a público só com o toque do José (mesmo link).
  - Correção de título, descrição ou fixado: o agente propõe e o José aprova com um toque.
  - Toda ação é registrada e vira lição.
- **Saúde do NotebookLM:** consumo gravado desde o dia 1; acima de 80% numa janela, a produção é espaçada.

## 6. Regras editoriais e do auditor

**Editorial (contrato v1 + decisões mais novas):**
- **Tom [APROVADO t212/t213]:**
  - "nós, brasileiros" + uma explicação lógica, com o **humor predominando**;
  - sátira leve ("sorrisinho no canto da boca"), sentimento "a gente é assim mesmo";
  - o final pousa no reconhecimento caloroso;
  - satiriza o comportamento, nunca a pessoa ou o grupo; satiriza, nunca incentiva.
- **Bloqueio absoluto [APROVADO t200]:** política partidária, tragédias, religião, grupos protegidos, conselho de saúde, finanças ou direito, incentivo a ato ilegal ou perigoso, tema que só existe para gerar briga.
- **Pontuação de polêmica:** faixa-alvo 50–75; acima de 75 aguarda o José. **Engajamento não é medida de segurança.**
- **Revisão humana antes da grade (rascunho):** trânsito com risco (régua: o sinal amarelo), eletricidade/fogo, dinheiro/preço, hierarquia social.
- **R10 [APROVADO]:** um tema, um vídeo, inclusive para variações próximas. Tema repetido é recusado mesmo que o José sugira (avisa ou abre ticket).
- **Roteiro (rascunho, R1–R9):**
  - o gancho é a cena do hábito nos 2 primeiros segundos;
  - a pergunta vem sem resposta;
  - o conflito aparece em até 4 s;
  - termo técnico só com imagem;
  - o "porquê" real funciona como payoff;
  - priorizar situações de casa e de família.
- **Elenco [APROVADO t264]:** até 2 personagens é o padrão desejado; mais que isso **não reprova**.
- **Sem nomes falados ou escritos [APROVADO].** Narrador único, sem rótulos "Nome:".
- **CTA [APROVADO t262/t263]:**
  - a última fala é **apenas "Segue o Porquê BR"**, curta e colada ao gancho para fechar o loop, nos últimos ~8 s;
  - **nunca pedir comentário** (nem na narração, nem na descrição, nem no fixado).
- **Loop:** a última fala emenda na primeira cena, sem cauda, sem tela parada, sem fade.
- **Duração [APROVADO t271]:** de **15 s a 3 min**, com **alvo de ~50 s** (≈150 palavras a ~3 palavras/s [VERIFICADO na rodada final]). O contrato do roteiro e o auditor seguem essa faixa. Acima de 60 s, a checagem de direitos de áudio vira **bloqueante**, porque um claim do Content ID bloqueia o Short.
- **Dinamismo:** troca de plano a cada ~3–5 s, imagem que acompanha cada fala, personagem que age em cena.
- **Proveniência:** nada de terceiros (personagens, marcas, imagens); áudio só da narração gerada.

**Auditor [VERIFICADO em 4 vídeos, 4/4 com os motivos certos (RESUMO.md); revalidar com o restante do labels.json e com vídeos novos no dev]:**
- O código extrai 1 quadro por cena + a transcrição (Whisper).
- O Gemini 3.8 Flash (modo normal) responde só **sim/não por traço**, em **2 rodadas**, cada uma num chat novo.
- O Jev ou o código faz as checagens de texto (loop, fala cortada, tom, nomes).
- O código aplica a tabela e decide.
- O relatório sai de template (veredito, motivo, ID da cena), sem prosa de LLM.
- Divergência entre as rodadas → `revisao_jose`. Ordem: reprova > revisão > aprova com ressalva > aprova.
- Duração, silêncio e resposta estruturada são indícios, não prova.

**Critério visual [APROVADO t264/t265; substitui a tabela LEVE/GRAVE do RUNBOOK e as §11/§14 do contrato; atualização dos dois na D11]:**
- **Nenhum critério visual de estilo reprova.** Pele ou roupa colorida, troca ou variação de personagem, mais de 2 personagens, 3D ou realista (nunca pedidos, mas aceitos se vierem): nada disso reprova.
- A aderência ao elenco vira **métrica** registrada, não trava. A consistência continua sendo buscada pelos prompts e pelas referências.

**O que BLOQUEIA:**
- falta de ironia e de sátira leve e cômica do cotidiano brasileiro;
- narração com problema;
- loop quebrado;
- CTA "Segue o Porquê BR" ausente ou incompleto;
- **qualquer pedido de comentário**;
- fala cortada;
- nome de personagem;
- conteúdo de terceiros;
- segurança/conformidade (categorias bloqueadas, tom de especialista, direitos de áudio acima de 60 s);
- imagem que não corresponde à fala (regra do RUNBOOK; ainda vale, porque não é critério de estilo).

**Consequência e aplicação ao V2-r3:**
- O `decide.py` e os prompts IDENT são revisados na tarefa D4.
- **V2-r3 a3: aprovada com ressalva** (o CTA aparece escrito na tela) [APROVADO t265]. O veredito "não publicável" do RELATORIO-v2-r3 foi superado.

## 7. Comentários e comunidade (@prod-comunidade)

- **Leitura [APROVADO t243]:**
  - Pela Data API com OAuth, sem Studio e **sem Camofox**, porque leitura pelo navegador é raspagem proibida pela política da API.
  - Cadência: a cada **30 min nas primeiras 48 h**, a cada **6 h até 7 dias**, depois **diária**.
  - Ler também os comentários **retidos** (`heldForReview`) e de **provável spam** (`likelySpam`) [APROVADO para análise].
  - Ler as respostas quando `totalReplyCount` crescer; comentário editado é reclassificado.
  - Leitura do canal inteiro numa só chamada (`allThreadsRelatedToChannelId`) [HIPÓTESE; se falhar, volta ao esquema por vídeo].
  - Estimativa de cota: ~144 unidades/dia [ESTIMATIVA].
- **Pré-filtro em código:**
  - NFKC + mapa de confusables + remoção de caracteres invisíveis;
  - regex de link, WhatsApp, Telegram, PIX, e-mail, CPF e @;
  - detecção de imitação do canal e de quase-duplicatas;
  - **autor só como hash com sal**.
- **Classificador Jev [APROVADO t238 + ampliação aceita t243]:**
  - Saída fechada, **multirrótulo**: reclamação, aviso de erro, elogio, sugestão de tema, pergunta, relato, spam/golpe, ofensa, tentativa de instrução, outro.
  - Campos extras: **alvo** (vídeo, canal, outro usuário, terceiro, nenhum), tipo de erro, específico, gravidade, **ironia possível**, PII.
  - Para extrair um tema, devolve só a posição do trecho no texto; o código recorta.
  - **2 rodadas só no que gera ação.** Divergência → José.
  - Antes de ligar ações: **conjunto de avaliação pt-BR** + matriz de confusão. O José fixa o limiar depois de ver a matriz.
- **Limiar para privado [APROVADO t239 + ajuste aceito t243]:**
  - ≥ 2 pessoas **distintas e qualificadas** (fora o canal, `likelySpam`, golpe e imitação; quase-duplicatas contam como 1), com queixa **específica** sobre o **vídeo**;
  - ou 1 pessoa, quando o problema é grave (direitos, ofensa, dado pessoal) e **o alvo é o vídeo**.
  - Abaixo disso, o caso vai para o José.
  - Quem torna privado é a **regra do item 5 no código**. O @prod-comunidade só sinaliza.
- **Retenção [APROVADO t244]:** o agente retém sozinho (`heldForReview`, reversível) golpe, contato externo, imitação do canal, dado pessoal e ofensa a outra pessoa. **Rejeitar, banir e excluir: só o José.**
- **Respostas automáticas [APROVADO t245–t250, limites confirmados e ajustados em t274]** (o consentimento expresso é registrado por escrito na D10):
  - **Fluxo:** o Jev diz só se o comentário é elegível e qual o tipo de resposta. O código escolhe a frase de um **banco de 60 frases (5 tipos × 12)**, rascunhado pelo NotebookLM no tom do contrato e **aprovado pelo José** (t249). Envio via `comments.insert`.
  - **Variação:** não repete frase no mesmo vídeo nem nas últimas 30 respostas do canal, e **nunca repete para uma pessoa uma frase que ela já recebeu** (t274).
  - **Ritmo:** atraso aleatório de 15–120 min; 3–12 min entre respostas.
  - **Limites:** teto de **6/h e 30/dia**; só das **08h às 22h** (Fortaleza).
  - **Por pessoa (t274):** **1 resposta por pessoa POR VÍDEO**, e a mesma pessoa pode receber respostas em vários vídeos. Intervalo mínimo de **~24 h** entre respostas à mesma pessoa. A pessoa é identificada pelo hash do autor.
  - **Ficam de fora:** reclamação, erro, **pergunta**, golpe/spam/ofensa, PII ou link, ironia possível, tema sensível, possível criança, comentário retido, comentário com mais de 7 dias.
  - **Conferência:** 60 min depois, verificar se a resposta continua lá; se sumiu, **parar tudo** e avisar o José.
  - **Kill switch:**
    - manual: `/pausar_respostas`, só do ID do José;
    - automático: resposta sumida, 403/quota, HOLD ou vídeo privado, e-mail de atenção ou crítico, pico acima de 3× a média, fallback não avaliado, falha de esquema.
  - **Tom das frases:** sem nome do autor, sem link, sem promessa, sem "inscreva-se", 0 ou 1 emoji.
- **Corações [APROVADO t247]:** via **Camofox, até 10 por dia**, só na sessão já aberta pelo guardião, em ritmo humano, abortando ao menor sinal de problema. Não há API para isso [VERIFICADO].
- **Sombra [APROVADO t248]:** **3 dias** em sombra (ou ~30 respostas simuladas aprovadas sem correção, o que vier primeiro) antes de ligar respostas e corações.
- **HIPÓTESE (testar no início do dev):** `comments.insert` (escopo `youtube.force-ssl`) funciona no app sem auditoria. Fazer **1 resposta real de teste** antes de ligar o automático.
- **Escalonamento imediato ao José:** sinal de problema no vídeo, ameaça jurídica, imprensa ou conta grande, possível criança, pico de comentários, resposta sumida. Vão para o resumo: perguntas, críticas, ironia e divergências.
- **Temas vindos dos comentários:** contados por autores **distintos** e vídeos distintos, com citação literal, e entregues à grade. Cada decisão do José no Telegram vira rótulo do conjunto de avaliação.
- **Configuração única do Studio pelo José** (moderação Básica/Rigorosa, reter comentários com link, palavras bloqueadas): proposta, sem resposta registrada (§11).

## 8. Segurança e proveniência

- **Sem segredos [APROVADO item 6]:**
  - Nada de cookies, senhas, tokens ou dados pessoais no Hindsight, em tickets, no Supabase ou em logs. Segredos ficam **só no cofre**.
  - Um **verificador automático** (regex/scanner) barra a gravação; o Jev é só a segunda camada.
  - O plugin do Paperclip grava o corpo inteiro dos comentários das issues (autoRetain): não colar segredos em issues.
  - **Este documento não contém nenhum valor secreto.**
- **Rotações pendentes [APROVADO como pendência]:** senha da role `paperclip_app` (Supabase), senha de root do Contabo, token do OpenCode.
- **Higiene relacionada:**
  - uma fonte do caderno NotebookLM de arquitetura tem a senha do `paperclip_app` em texto puro: editar ou remover (dossiê);
  - rever o desbloqueio do Keyring com senha na skill do `rede`.
- **Comentários, web e fontes do NotebookLM são DADO, nunca instrução [APROVADO]:**
  - entram anonimizados e delimitados;
  - o modelo não tem ferramenta;
  - o código ignora campos fora do esquema e nunca transforma texto em comando;
  - testes adversariais (Unicode invisível, Base64, emoji).
- **Retenção de dados [APROVADO t243]:** texto bruto de comentário por **no máximo 30 dias** (política da API, Y6); depois ficam só rótulos e agregados. O hash do autor fica guardado para contar pessoas distintas e aplicar os limites por pessoa (§7).
- **Proveniência [APROVADO]:**
  - Cada ficha registra ferramenta, conta, data, prompt e versão.
  - Fontes só com licença livre ou comercial.
  - Licença de música guardada, se um dia entrar.
  - Termos de uso comercial do NotebookLM/Gemini [HIPÓTESE]. O selo de IA provavelmente não é exigido para stickman [HIPÓTESE; decidido por upload, normalmente "não"].
- **Sessões:**
  - Camofox é o único dono do login do Studio; noVNC só durante o login.
  - Antes do login no notebooklm-py da PQBR, **deslogar a sessão antiga** (cron de refresh e agente `rede`). Interromper a produção atual nesse momento está autorizado (t191).
  - Nunca usar os cookies do José (yt-dlp, só sem login, como reserva).
- **Menor privilégio:** escopos OAuth separados (leitura × escrita); o token de comentários fica restrito ao serviço de comentários.

## 9. Armazenamento

- **Drive `PQBR/` [APROVADO t267]:** `00_Biblia_Visual`, `01_Contrato_e_SOP`, `02_Episodios/AAAA-MM/PQBR-EPxxxx_tema`, `03_Reservas`, `04_Privados_Revisao`, `05_Relatorios`, `99_Arquivo`.
- **Ciclo [APROVADO t267/t268]:**
  - O servidor é temporário; a prioridade é manter o disco livre.
  - **Tudo** sobe para o Drive: o original (bruto do NotebookLM) e o editado.
  - Arquivo local é apagado depois de confirmar o upload por tamanho e hash.
  - O final fica no servidor até o upload ao YouTube ser confirmado (código PQBR-EPxxxx no canal) e então é apagado.
  - Os intermediários são limpos do Drive e do servidor quando a cópia final estiver pronta.
- **Fichas visuais [APROVADO]:**
  - Ficam no Drive (`00_Biblia_Visual`), com catálogo no Supabase (`visual_assets`, `episode_assets`) e wiki gerada da tabela.
  - Um resolvedor sem LLM injeta só as fichas necessárias. Ficha que falta é criada na hora, **sem aprovação bloqueante** (o José só recebe um aviso).
  - "Não Aprovado" abre ticket e a ficha é refeita para os próximos vídeos.
  - Bíblia visual v002 aprovada.
- **Limpeza noturna [APROVADO t269/t270]:**
  - Script **determinístico** na rotina noturna do @prod-director.
  - Detecta duplicatas (mesmo hash/tamanho ou mesmo código PQBR-EP) e órfãos, move para `99_Arquivo/_duplicados` e lista para o José no relatório diário e no Telegram.
  - **Exclusão definitiva: só o José**, depois de confirmar.

## 10. Tarefas de desenvolvimento e hipóteses

**Tarefas de desenvolvimento** (fase de dev, não são tickets; cada uma com autorização, critério de aceite e rollback):

| # | Tarefa | Critério de pronto |
|---|---|---|
| D1 | **Migração do notebooklm-py** (t187–t191), passos 1–5: venv da PQBR 0.8.4; serviço único dono da sessão; MP32 com instalação própria em 0.8.2; skills do `rede` aposentadas ou apontadas para o serviço, sem cópia de cookies; remover o pipx global por último (manter `~/.notebooklm` por 7 dias, backup do crontab). | Smoke test em caderno clonado; `usage --json` gravando no Supabase; MP32 funcionando; rollback documentado |
| D2 | Pacote `pqbr-company/` + import `--dry-run` + perfil Hermes `pqbr` com env mínimo | Dry-run limpo; heartbeats desligados até os budgets |
| D3 | Contratos Pydantic únicos (`pqbr_contracts`). `RoteiroShort` de **15 s a 3 min, com alvo de ~50 s** (t271) e palavras proporcionais (hoje 40–60 s). Os modelos devem espelhar o schema real. | Testes de esquema passam |
| D4 | Auditor: `decide.py` e prompts com o **critério t264/t265** (estilo vira métrica); checagem de duração de 15 s a 3 min, com alvo de ~50 s (t271; hoje 15–60 s); CTA = "Segue o Porquê BR" + detector de pedido de comentário; direitos de áudio bloqueantes acima de 60 s; revalidar com o restante do labels.json e com vídeos novos | Gabarito ampliado: falso aprovado e falso reprovado medidos |
| D5 | Grade por código + 3 barreiras de repetição + máquina de estados com checkpoint + agendador do SO + vigia de prazo | Vários dias seguidos sem falha antes do corte do fluxo antigo |
| D6 | Guardião de sessão + escada t272 (Camofox renova → noVNC + Telegram; cookies do Chrome só com o OK do José) + pings + escada de falhas + buffer local do Supabase | Simulação de cada degrau e de Supabase fora; nenhuma cópia de cookies sem o OK |
| D7 | Publicação pela API (`videos.insert` com agendamento) e reserva pelo Studio via Camofox (t273). Até a auditoria: sobe privado e o Camofox agenda. Sem duplicidade (código PQBR-EP, busca em privados/agendados, 1 tentativa sem confirmação). | Teste de upload interrompido sem duplicata; 1 agendamento por cada via |
| D8 | @prod-comunidade: leitura, pré-filtro, Jev, tabela de decisão, retenção, respostas com os limites t274 (por vídeo, ~24 h e sem frase repetida por pessoa), corações, kill switch, conjunto de avaliação pt-BR | 3 dias de sombra ou ~30 respostas simuladas aprovadas sem correção (t248); matriz aceita pelo José |
| D9 | Banco de 60 frases rascunhado pelo NotebookLM + aprovação do José (t249); `guia-tom-comunidade.md` | 60 frases aprovadas |
| D10 | Registrar por escrito a regra do item 5 e a regra completa de respostas como **instrução/consentimento expresso** do dono (política da API III.I.2, III.E.3) | Registro no arquivo de decisões |
| D11 | Atualizar o **contrato editorial** (v1 → v2), o **RUNBOOK do auditor** (v3b) e o steering/SOP para as regras aprovadas: CTA só "Segue o Porquê BR", sem pedido de comentário (t262/t263; contrato §11.1, §12 e R7); nenhum critério visual de estilo reprova, só a falta de ironia e sátira leve + as travas de texto, áudio e segurança (t264/t265; contrato §11 regra 1 e §14, tabela GRAVE do RUNBOOK); duração de 15 s a 3 min com alvo de ~50 s (t271); V2-r3 a3 aprovada com ressalva no gabarito | Contrato v2 e RUNBOOK revisado aprovados pelo José; `decide.py` coerente com eles |
| D12 | Monitor de atualizações + monitor de consumo (NotebookLM/Jev) + relatório diário | Relatório no Telegram |
| D13 | Script de limpeza do Drive + ciclo de upload com hash | Duplicata de teste movida, nada excluído |
| D14 | Verificador de segredos/PII nas gravações (Hindsight, tickets, Supabase, logs) | Bloqueia segredo de teste |
| D15 | Estratégia para 2 personagens (item 2): preservação das fichas no NotebookLM; alternativa a validar (narração do NotebookLM + quadros de outra ferramenta montados em código) | Decisão do José com evidência; pelo t264 isso não bloqueia a produção |

**HIPÓTESES** (dono padrão: core-eng/@eng-cto; nada que depende delas é construído antes de virarem VERIFICADO):

| # | Hipótese | Dono | Critério de pronto |
|---|---|---|---|
| H1 | Auditoria do app do GCP para upload público pela API (t273). Até lá, vídeo sobe privado e o Camofox agenda pelo Studio. Inclui o custo real de cota. | core-eng | Auditoria concedida e 1 upload público de teste; até lá, fluxo "privado + agendamento pelo Camofox" testado |
| H2 | Agendamento via `publishAt` depois da auditoria | core-eng | 1 agendamento de teste confirmado pela API |
| H3 | `comments.insert` (`youtube.force-ssl`) funciona sem auditoria | core-eng | 1 resposta real de teste publicada e conferida |
| H4 | Leitura do canal inteiro via `allThreadsRelatedToChannelId` inclui os Shorts; leitura de `heldForReview`/`likelySpam` com o escopo previsto | core-eng | Comparar com a leitura por vídeo |
| H5 | NotebookLM gera Short vertical bom até 180 s | core-eng | Gerações de ~90 s e ~170 s verificadas |
| H6 | `notebooklm usage --json` funciona na conta (medição ativa) | core-eng | Saída válida gravada; senão, contagem própria |
| H7 | Nome do modelo OpenAI do fallback e paridade com o esquema do Jev | core-eng | Conjunto de avaliação roda com o mesmo formato |
| H8 | Preço e saldo do Jev; média de gasto | core-eng (jr) | Média dos primeiros dias no relatório |
| H9 | Causa das quedas do Studio (cookies do Chrome vs. identidade do aparelho do Camofox); telemetria do camofox-browser desligada | core-eng | Sessão estável por N dias com a escada t272, sem cópia de cookies |
| H10 | Juiz visual em produção: Gemini web automatizado via Camofox vs. Gemini API (a chave é decisão do José) | core-eng + José | Teste comparativo (RUNBOOK) + decisão |
| H11 | Termos de uso comercial do NotebookLM/Gemini; selo de IA desnecessário para stickman | core-eng (registro) + José | Leitura dos termos registrada; compliance acompanha |
| H12 | Métricas do canal (30 vs. 46 Shorts; bases de retenção diferentes) | @prod-analista/core-eng | Números fixados pela Analytics API |
| H13 | Supabase Pro ativo; local do schema Hindsight; `hermes_local` + Hindsight num heartbeat real | core-eng | Confirmação pelo MCP + 1 heartbeat real |
| H14 | App do GCP em produção (uso interno) sem expiração do token | core-eng | Token válido além de 7 dias |
| H15 | Limites do Pro do NotebookLM (5 h/semanal; 20 vídeos/dia) | core-eng | Monitor de consumo da 1ª semana |
| H16 | Corações pelo Camofox (até 10/dia) sem desafio de login | core-eng | 3 dias de sombra sem incidente de sessão |

## 11. Pendências

1. **Teto de orçamento [APROVADO como regra; valor pendente]:** definido com os dados do monitor depois dos primeiros dias ou da primeira semana de testes (t268 / decisão 10).
2. Horários das janelas de publicação (os documentos citam 11:40/14:40/18:35/21:00 e 11:40/18:35/21:15; o pico de audiência fica fora do contrato).
3. Aprovação das 60 frases (D9) e do contrato editorial v2 (D11).
4. Configuração única do Studio pelo José (moderação, links, palavras bloqueadas): sem resposta registrada.
5. Definição de sucesso do piloto: as faixas do rascunho viram metas só depois da verificação pela API; recalibrar em 2–4 semanas.
6. Roteiros de referência a pedir ao `rede` (TV, sinal amarelo, controle remoto/fita, tomada do chuveiro).
7. Decisões em aberto do dossiê (g): @prod-director como LLM ou rotina; memória (Hindsight vs. OpenViking no `rede`); papel do `rede` depois da org existir; migração do `yt_production`.
8. Futuro: plugin do Paperclip (sem mexer no código-fonte) ou painel próprio para as verificações; área de mensagens para pedir feedback (nunca automática sem regra do José).
9. Rotações de credenciais (§8).

---

## Ambiente (atualizado em 09/10/2026)
- **APROVADO/VERIFICADO:** a pasta `/home/pc/Workspace/PQBR` no servidor `pc` é o repositório oficial da aplicação, ligada ao GitHub `jvmendesjr/PQBR` (privado, branch `main`). A documentação está em `docs/`, e o `README.md` define a ordem de autoridade.
- **VERIFICADO:** o GitHub está conectado à core-eng pelo conector do Paperclip.
- **VERIFICADO:** o Paperclip abre só dentro da tailnet, em `https://pc.taildfb7d7.ts.net:3100`. A porta 443 fica livre por decisão do José.
- **APROVADO:** a core-eng não usa perfis do Hermes. O José interage pelo chat do próprio Paperclip quando for preciso.
- **VERIFICADO:** dependências globais no servidor: Camofox (REST 9377, saudável), Node, Python/uv, FFmpeg, Docker, gh, NotebookLM CLI 0.8.2 e Hindsight. As dependências locais da PQBR são tarefas do roteiro.
