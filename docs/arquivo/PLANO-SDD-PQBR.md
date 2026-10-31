> ⛔ **ARQUIVO — não consultar sem aprovação do José.** Superado pelos docs canônicos (README).

# Plano SDD (Spec-Driven Development) da org PQBR

> **Dono do desenvolvimento:** jr · **Autoridade final:** José · **Data:** 09/10/2026 (horário de Fortaleza)
> **Repositório:** `/home/pc/Workspace/PQBR` (GitHub `jvmendesjr/PQBR`, privado, branch `main`) [VERIFICADO]
> **Fontes da verdade, nesta ordem (README.md):** (1) `docs/00-entrega/decisoes-jose-2026-10-08.md` (entrada mais nova vence); (2) `docs/00-entrega/ENTREGA-core-eng-PQBR.md`; (3) `docs/01-editorial/` (contrato v1 DESATUALIZADO em CTA e identidade visual, ver t262–t265); (4) `docs/02-pesquisas/`; (5) `docs/03-auditor/`; (6) `docs/04-canal/` (só referência); (7) `docs/99-historico/` (não usar para decidir).
> **Legenda:** **[APROVADO]** decisão do José · **[VERIFICADO]** testado/visto na fonte · **[HIPÓTESE]** a confirmar antes de construir o que depende dela · **[PROPOSTA]** sugestão do jr, ainda sem aprovação · **[PENDENTE-JOSÉ]** decisão em aberto.
> Os códigos "tNNN", "item N", "Dn" e "Hn" remetem ao registro de decisões e à ENTREGA.

---

## 0. Mudança de rumo e premissas deste plano

- **Quem constrói:** o jr conduz o desenvolvimento e cria uma org Paperclip **nova, chamada "PQBR"**, separada da core-eng. [instrução atual do José/jr; substitui a delegação da COR-1 à core-eng]
- **Nome [APROVADO]:** org "PQBR"; os documentos explicam a sigla (Porquê BR); o canal usa "porquê" por extenso.
- **Tudo pausado:** o CEO e todos os agentes da PQBR são criados **pausados**, com heartbeats desligados, até o José liberar. Os agentes importados já chegam com heartbeat desligado [VERIFICADO na doc do Paperclip, ENTREGA §1].
- **Mudanças durante a construção** voltam ao blueprint como **tarefas de desenvolvimento**, nunca como ticket; tickets são só da produção [APROVADO t187/item 7]. Cada tarefa tem autorização, critério de aceite e rollback [APROVADO t187].
- **Nada que dependa de uma hipótese é construído antes de ela virar VERIFICADO** [APROVADO item 7].
- **Fases do produto [APROVADO]:** construção → **validação (7 itens; prioridade 1, 2 e 3)** → produção. A produção só é liberada quando cada item cumpre o seu critério de aceite.
- **Regra de trabalho [APROVADO t230]:** antes de dar um papel a um componente, conferir a ficha dele na ENTREGA §4.
- **Segredos [APROVADO item 6]:** nada de senhas, tokens, cookies ou dados pessoais no repositório, em tickets, no Supabase, no Hindsight ou em logs. Segredos só no cofre/`.env` do servidor.

### 0.1 O que fazer com os arquivos não commitados do CTO (COR-1)

Arquivos: `docs/BLUEPRINT_PQBR.md`, `docs/INSTRUCOES_AGENTES_PQBR.md`, `company/.paperclip.yaml`, `company/COMPANY.md`, `company/agents/*/INSTRUCTIONS.md` (11), `company/teams/*/TEAM.md` (3). Pela revisão de 09/10, eles descrevem outro canal (divulgação científica, 3 atos, fontes primárias), omitem item 5, Jev, escadas de falha, Supabase, NotebookLM 0.8.4 e Drive t267, inventam pastas, modelos, orçamentos e equipes e não seguem o formato agentcompanies/v1.

- **[PROPOSTA, aguarda OK do José]:** mover sem apagar para `docs/99-historico/cor1-cto-2026-10-09/` (mantendo a árvore `company/` dentro dela), com um `LEIA-ME.md` de uma linha: "Entrega da COR-1 (core-eng) não aprovada; ver revisão de 09/10. Não usar para decidir."
- Commit separado: `chore(historico): arquiva entrega COR-1 não aprovada`.
- **Rollback:** `git revert` desse commit (ou mover de volta).
- Não aproveitar o conteúdo, exceto como checagem cruzada: as regras de comentários (limites t274, sombra de 3 dias, 10 corações/dia, `heldForReview`) estavam corretas e já constam da ENTREGA §7.
- A seção "Atualização do ambiente: perfil Hermes `pqbr` JÁ CRIADO", hoje sem commit no fim da ENTREGA, entra num commit próprio (`docs(entrega): perfil pqbr já criado`) **[PROPOSTA]**.
- **COR-1 no Paperclip da core-eng:** fica como está. Comentar ou reabrir só com OK do José.

---

## 1. Elenco de agentes (como aprovado)

Princípio [APROVADO t184]: ideação, roteiro, SEO e pesquisa ficam com o **NotebookLM** (Gemini web como reserva). Os agentes **orquestram**: entregam o conhecimento, extraem a saída por código, validam com Pydantic, conferem com o Jev e acompanham com observabilidade. Preflight, render, publisher e backup **não usam LLM** (ENTREGA §2).

| Slug | Natureza | Papel aprovado (resumo) | Não faz | Estado inicial |
|---|---|---|---|---|
| **ceo** | Raiz da org Paperclip | Padrão "CEO pausado" (GStack, citado na ENTREGA §2 como referência do director). Não opera o fluxo. | Nada até o José liberar | **Pausado** |
| **prod-director** | **[PENDENTE-JOSÉ]** LLM ou rotina determinística (dossiê g.10) | Cadência, rotinas e **parâmetros operacionais**; recebe propostas do analista e do assistente; roda a **limpeza noturna do Drive por script** (t270) | Não altera regra canônica; não exclui; não é autoridade final | Pausado |
| **prod-ideador** | Orquestrador LLM + código | Entrega coleta e fontes ao caderno de tendências; recebe temas filtrados | Não escolhe tema sem as 3 barreiras; não libera tema bloqueado | Pausado |
| **prod-roteirista** | Orquestrador LLM + código | Orquestra o roteiro no NotebookLM, lista as entidades da cena, valida `RoteiroShort` | Não redige fora do NotebookLM/Gemini web; sem nomes de personagens | Pausado |
| **prod-render** | **Executor determinístico (script, sem persona)** | Gera no NotebookLM (serviço PQBR) e faz a pós FFmpeg: corte do end card só se detectado + logo com zoom suave | Não julga qualidade | Pausado |
| **prod-auditor** | **Código decide**; Gemini (sim/não por traço) + Jev (texto) | Auditoria pré-publicação e item de conformidade; relatório por template | LLM não dá gravidade nem escreve laudo | Pausado |
| **prod-seo** | Orquestrador LLM + código | Título/descrição via NotebookLM; código PQBR-EPxxxx na descrição e na etiqueta | Não pede comentário (t263) | Pausado |
| **prod-publisher** ("agente do Studio") | **Executor determinístico (script, sem persona)** | `videos.insert` com agendamento (t273); confere ID e código; executa em código a regra do item 5 (tornar privado) | Não decide sozinho tornar privado; não reenvia sem consultar Supabase e canal; não exclui; não volta vídeo a público sem o toque do José | Pausado |
| **prod-analista** | Coleta por código + análise LLM | Analytics API diária; análise semanal ou por anomalia; propõe ao director; aprendizados no Hindsight; **só observa até ~30 Shorts/90 dias** | Não muda parâmetro sozinho | Pausado |
| **prod-compliance** | Coleta por código + Jev classifica + agente analisa | E-mail do canal, Studio (leitura), Data API; gravidade; HOLD em caso crítico; rascunho de recurso | Nunca recorre, apaga ou altera sem dupla confirmação do José | Pausado |
| **prod-comunidade** | Código + Jev; agente faz resumo e saúde | Lê pela API, classifica, retém, responde com o banco de 60 frases, dá corações via Camofox, agrupa temas | **Não torna vídeo privado** (só sinaliza, t250); não escreve texto livre; não rejeita, exclui ou bane | Pausado (+ 3 dias de sombra, t248) |
| **pqbr-assistente** | LLM no **Hermes `pqbr`**, pelo Telegram | Só consulta, roteia e responde: perguntas, temas, propostas de regra ao director, tickets à engenharia, verificação de fichas, pedidos de relatório ao analista; responde pelo banco | Não executa mudanças; ordem só vale do **ID autorizado do José** (t237) | Pausado |

- **Equipes (`teams/`) [PROPOSTA]:** a ENTREGA não define equipes. Proposta mínima: nenhuma equipe no início, todos reportando ao `prod-director`, e o `prod-director` ao `ceo`. Equipes só se o José pedir.
- **Personas [APROVADO como fonte, ENTREGA §2]:** pt-BR, parafraseadas da Agency Agents (MIT); comunidade a partir de donchitos `community-manager`, `customer-service.md`, `developer-community-builder` e `feedback-synthesizer`. Compliance e assistente: **a definir**.
- **Adapters [HIPÓTESE/PROPOSTA]:** o `hermes_local` sempre passa `--yolo` [VERIFICADO no dossiê §f.5], e o perfil `pqbr` **não** pode herdar `--yolo` nem sudo sem senha [APROVADO]. Antes de definir o adapter de cada agente, verificar se o `hermes_local` aceita desligar o `--yolo` (H-SDD1). Para os executores determinísticos, avaliar o adapter `process`, que roda script e dispensa LLM [PROPOSTA].

---

## 2. Formato do pacote (agentcompanies/v1 + extensão Paperclip)

Base: especificação `paperclipai/paperclip/docs/companies/companies-spec.md` [VERIFICADO em 09/10].

```
company/
├── COMPANY.md                  # frontmatter: name, description, slug: pqbr, schema: agentcompanies/v1
├── agents/<slug>/AGENTS.md     # frontmatter: name, title, reportsTo, skills; CORPO = instruções canônicas
├── teams/<slug>/TEAM.md        # só se aprovado: manager: ../../agents/<slug>/AGENTS.md, includes: [...]
├── skills/<slug>/SKILL.md      # Agent Skills; extensões só em metadata.paperclip / metadata.sources
├── tasks/<slug>/TASK.md        # assignee: <slug>; recurring: true para rotinas
└── .paperclip.yaml             # schema: paperclip/v1; agents.<slug>.adapter{type,config}; inputs.env (kind: secret|plain, requirement); routines.<slug>.triggers (cron + timezone America/Fortaleza); budgets
```

Regras da especificação a cumprir:
- Instruções no corpo do `AGENTS.md`, nunca no `.paperclip.yaml` e nunca em arquivos à parte.
- Config de adapter e runtime só no `.paperclip.yaml`.
- Sem segredos, caminhos absolutos ou IDs de banco no pacote; segredos só como `inputs.env.<VAR>: {kind: secret, requirement: required|optional}`, sem valor.
- Skills referenciadas por shortname; skills de terceiros com `sources` fixados por `commit` (e `sha256`).
- Omitir campos vazios ou com valor padrão.

---

## 3. Fases

Formato de cada fase: **Objetivo · Entregáveis · Critério de aceite · Portão do José · Rollback · Dependências.**
Todo entregável é commitado em branch própria (`sdd/fase-N-...`) e entra na `main` por PR aprovado pelo José [APROVADO: José aprova merges].

### Fase 0: especificação, constituição e roteiro

- **Objetivo:** transformar a ENTREGA + decisões em especificação executável e rastreável antes de qualquer código.
- **Entregáveis:**
  - `docs/sdd/00-constituicao.md`: princípios inegociáveis com a tNNN de origem: determinismo antes de LLM; Jev só decisão estruturada; relatórios por template; item 5; sem segredos; Camofox inegociável; NotebookLM primário; sem pedido de comentário; CTA só "Segue o Porquê BR"; estilo visual não reprova; exclusões só pelo José; nunca atualizar dependência sozinho.
  - `docs/sdd/01-especificacao.md`: requisitos numerados (RF/RNF), cada um com status APROVADO/VERIFICADO/HIPÓTESE e tNNN.
  - `docs/sdd/02-rastreabilidade.md`: matriz tNNN → requisito → tarefa D → teste.
  - `docs/sdd/03-roteiro.md`: ordem das fases e tarefas deste plano (cópia viva).
  - `docs/sdd/04-hipoteses.md`: H1–H16 da ENTREGA + H-SDD1… (dono, critério de pronto, o que depende).
  - `docs/sdd/05-pendencias-jose.md` (§5 deste plano).
  - Arquivamento da §0.1 (só com OK).
- **Aceite:** toda regra das §1–§9 da ENTREGA aparece na especificação com a origem; nenhuma regra sem origem, exceto as marcadas [PROPOSTA]; revisão cruzada sem contradição com o registro de decisões.
- **Portão G0 (José):** aprova a constituição, a ordem do roteiro e o destino dos arquivos do CTO.
- **Rollback:** documentos só em `docs/sdd/`; reverter o PR.
- **Dependências:** nenhuma.

### Fase 1: pacote da org (`company/`)

- **Objetivo:** pacote agentcompanies/v1 fiel ao elenco aprovado, importável, sem segredos.
- **Entregáveis:**
  - `company/COMPANY.md`: frontmatter `name: PQBR`, `slug: pqbr`, `schema: agentcompanies/v1` e `description` de sátira leve de stickman sobre manias brasileiras (promessa do contrato); `requirements.secrets` só com nomes.
  - `company/agents/{ceo,prod-director,prod-ideador,prod-roteirista,prod-render,prod-auditor,prod-seo,prod-publisher,prod-analista,prod-compliance,prod-comunidade,pqbr-assistente}/AGENTS.md`: frontmatter `name`, `title`, `reportsTo`, `skills`; corpo em pt-BR com Papel, NÃO faz, Ferramentas e Regras citando tNNN (tabela da §1).
  - `company/skills/`: esqueletos das skills a escrever do zero, com `SKILL.md` e status "a implementar": `pqbr-comentarios-triagem`, `pqbr-comentarios-moderacao`, `pqbr-comentarios-temas`, `pqbr-guia-tom`, `skill-short-form-copy`, `skill-youtube-metadata-seo`, `skill-research-curation`.
  - Skills internas portadas do `rede` só depois da revisão de segurança (Keyring com senha, CDP 9225 banido, papercut/19h30 obsoletos): `rotina-producao-porqu-br`, `durable-orchestration`, `gemini-web-video-auditor` (vetos visuais obsoletos pela t265), `ecossistema-ponte-multitenant`.
  - Skills da comunidade, referenciadas com commit fixado: coreyhaines `copywriting`/`video`, kostja94 `youtube-seo`, supabase/agent-skills, notebooklm-py (oficial), digitalsamba `ffmpeg`, `building-pydantic-ai-agents`. **Não usar** superpowers/* nem `claude-office-skills/youtube-automation`.
  - `company/tasks/<rotina>/TASK.md` (`recurring: true`), uma por rotina aprovada: grade da madrugada, lote da manhã, guardião de sessão (~20 min com variação), checagem pré-publicação, leitura de comentários (30 min / 6 h / diária), limpeza noturna do Drive, relatório diário, monitor de atualizações (semanal), monitor de consumo. **Horários das janelas: [PENDENTE-JOSÉ].**
  - `company/.paperclip.yaml`: `schema: paperclip/v1`; `agents.<slug>.adapter{type,config}`; `inputs.env` só declarações (`kind: secret`); `routines` com `timezone: America/Fortaleza`. Budgets em branco ou mínimos até o teto ser definido [PENDENTE-JOSÉ].
  - `scripts/validar_pacote.py`: checa frontmatter, slugs, `reportsTo` válidos, skills resolvidas, ausência de segredos e de caminhos absolutos.
- **Aceite:** o validador passa; o scanner de segredos não acha nada; os 12 slugs batem com a §1; cada `AGENTS.md` cita as regras-chave do papel (item 5, t250, t263, t237 etc.); nenhum agente determinístico tem modelo LLM.
- **Portão G1 (José):** aprova o texto dos 12 `AGENTS.md` e o `.paperclip.yaml` (sem budgets definitivos).
- **Rollback:** reverter o PR; nada foi importado ainda.
- **Dependências:** G0.

### Fase 2: import em dry-run e criação da org PQBR (pausada)

- **Objetivo:** criar a org PQBR nova, separada da core-eng, com tudo pausado.
- **Entregáveis:**
  - `docs/sdd/fase2-dry-run.md`: saída do `paperclipai company import ./company --target new --new-company-name "PQBR" --dry-run` (sintaxe do dossiê; conferir na versão instalada [HIPÓTESE]), com avisos e correções.
  - Import real fixado no commit aprovado da `main`.
  - `docs/sdd/fase2-estado-org.md`: lista de agentes com status (todos pausados, heartbeats off), sem IDs secretos.
  - Verificação do perfil `pqbr` (já existe [VERIFICADO]): `~/.hermes/profiles/pqbr/config.yaml` com env mínimo, toolsets restritos, budgets, **sem `--yolo` e sem sudo sem senha** (ajuste da D2). Segredos só em `~/.hermes/profiles/pqbr/.env`.
- **Aceite:** dry-run limpo; org "PQBR" criada como empresa nova; CEO e 11 agentes **pausados**; nenhum heartbeat ligado; core-eng intocada; H-SDD1 (adapter sem `--yolo`) resolvida, ou agentes LLM sem adapter ativo até resolver.
- **Portão G2 (José):** autoriza o import real depois de ver o dry-run. **Liberar qualquer agente ou heartbeat é decisão separada do José**, uma a uma.
- **Rollback:** arquivar ou excluir a org PQBR **só pelo José** (exclusão é do José); restaurar o `config.yaml` do perfil a partir de backup feito antes.
- **Dependências:** G1.

### Fase 3 em diante: tarefas D1–D15 em ordem de dependência

Ordem **[PROPOSTA]**, montada a partir das dependências técnicas da ENTREGA §10. Todas são tarefas de desenvolvimento (não tickets), cada uma com autorização, aceite e rollback. Código em `src/pqbr/…`, testes em `tests/…`, migrações em `db/migrations/…`, modelos de texto em `templates/…`, exemplos de configuração em `config/` (só `.env.example`).

#### Fase 3: fundações (D3 + D14)
- **D3, contratos Pydantic únicos.**
  - Entregáveis: `src/pqbr/schemas/` (pacote `pqbr_contracts`): `RoteiroShort` de **15 s a 3 min, alvo de ~50 s** (t271), palavras proporcionais (~3 palavras/s); estados `aprovado → enviando → enviado(video_id) → agendado → publicado`; comentário multirrótulo (t238/t243); `decide()` com saídas fechadas; auditoria com veredito/motivo/ID da cena.
  - Migração: `db/migrations/0001_base.sql` (grade, temas R10, episódios, `visual_assets`, `episode_assets`, comentários, ações com motivo/quem/quando, consumo, kill switch).
  - Testes: `tests/schemas/`.
  - Aceite: testes de esquema passam; os modelos espelham o schema real do Supabase.
- **D14, verificador de segredos/PII.**
  - Entregáveis: `src/pqbr/storage/scanner.py` (regex/scanner primeiro, Jev só como segunda camada), hook antes de gravar no Hindsight, tickets, Supabase e logs; `tests/scanner/`; hook de pre-commit no repo.
  - Aceite: bloqueia o segredo de teste.
- **Portão G3:** José aprova os esquemas (sobretudo a faixa de duração e os rótulos de comentário).
- **Rollback:** reverter as migrações com `down` correspondente; pacote versionado.
- **Dependências:** G2. H13 (Supabase Pro; local do schema Hindsight) deve estar verificada antes de gravar no banco de produção; até lá, usar banco de desenvolvimento [PROPOSTA].

#### Fase 4: D1, migração do notebooklm-py (passos 1–5, t187–t191)
- **Entregáveis:**
  - venv da PQBR com **0.8.4 fixada**, `NOTEBOOKLM_HOME=/home/pc/.pqbr/notebooklm`, perfil `pqbr`.
  - `src/pqbr/integrations/notebooklm_service.py`: serviço único dono da sessão, refresh por timer, fila de uma tarefa, `notebooklm usage --json` gravado no Supabase.
  - `scripts/migracao_notebooklm/` com o passo a passo e o rollback.
  - MP32 com instalação própria em 0.8.2; skills do `rede` aposentadas ou apontadas para o serviço, **sem cópia de cookies**; pipx global removido por último, `~/.notebooklm` mantido por 7 dias e backup do crontab.
  - **Antes do login novo, deslogar a sessão antiga do Porquê BR** (cron de refresh + agente `rede`); interromper a produção atual nesse momento está autorizado (t191).
- **Aceite:** smoke test em caderno clonado; `usage --json` gravando (ou contagem própria se H6 falhar); MP32 funcionando; rollback documentado e ensaiado.
- **Portão G4:** José autoriza **cada passo** (1 a 5), em especial o logout da sessão antiga e a interrupção da produção atual.
- **Rollback:** voltar ao pipx 0.8.2 global e ao crontab salvo; MP32 continua com a instalação anterior.
- **Dependências:** G2 (pode correr em paralelo com a Fase 3); H6, H15.

#### Fase 5: D5, estabilidade (grade, barreiras e máquina de estados)
- **Entregáveis:**
  - `src/pqbr/pipeline/grade.py`: grade gerada **por código a partir da data**, gravada no banco; mistura ~70% em alta / ~30% perenes; última janela preferencialmente dos perenes.
  - Barreiras: `src/pqbr/pipeline/barreiras.py` (3 barreiras; barreira 2 via `decide()`/Jev; R10 recusa tema repetido mesmo se o José sugerir, com aviso ou ticket).
  - Estados: `src/pqbr/pipeline/estado.py` (checkpoint; "publicado" só com ID confirmado; idempotência; varredura no reboot).
  - Agendador do SO (timers systemd do usuário `pc`) + vigia de prazo: `scripts/systemd/`.
  - Coleta de tendências: Data API + resumo de comentários + caderno diário + Deep Research (1 das 20) + filtros em código + pontuação de polêmica (50–75; acima de 75 aguarda o José; bloqueio absoluto).
- **Aceite:** vários dias seguidos sem falha em ambiente paralelo **antes do corte do fluxo antigo**; testes reproduzindo o incidente de 08/10 (grade do dia 7, 3 de 4 temas repetidos) passam.
- **Portão G5:** José aprova o início do teste paralelo; o **corte do fluxo antigo** é um portão separado (G5b).
- **Rollback:** desligar os timers da PQBR; o fluxo antigo continua até G5b.
- **Dependências:** D3, D1.

#### Fase 6: D6, resiliência
- **Entregáveis:**
  - `src/pqbr/guardian/sessao.py`: timer de ~20 min com variação; testa Studio, Gemini Web e NotebookLM; checagem extra ~30 min antes de cada publicação; **escada t272**: Camofox renova → login manual pelo noVNC (aviso no Telegram) → cópia de cookies do Chrome **só como último recurso e com OK do José**. Publicação em espera e retomada automática; renovação que falha gera Telegram + ticket.
  - `src/pqbr/guardian/ping.py`: teste de resposta antes do lote e antes de cada ação crítica.
  - `src/pqbr/guardian/escada.py`: 30 s → 2 min → 8 min; `NETWORK_WAITING` sem gastar tentativa; outra estratégia a cada tentativa; 2 falhas da mesma ação vão para o José; 5 chamadas idênticas param tudo; `quotaExceeded` espera o reset.
  - `src/pqbr/storage/buffer_local.py`: Supabase fora → fila em arquivo com gravação atômica; nada agendado nem tornado público sem gravar o estado; sincroniza quando o banco volta (t242).
  - Fallback do Jev em `decide()`: (1) Jev via OpenRouter; (2) modelo OpenAI (nome em H7); mesma validação Pydantic; fallback não avaliado só alerta, sem ação automática.
- **Aceite:** simulação de cada degrau e de Supabase fora; nenhuma cópia de cookies sem OK.
- **Portão G6:** José aprova o relatório de simulação.
- **Rollback:** desligar o guardião (timer); sem efeito em sessão existente.
- **Dependências:** D5; H9, H7.

#### Fase 7: D11 + D4, editorial e auditor
- **D11:** contrato editorial v1 → **v2** em `docs/01-editorial/contrato-editorial-pqbr-v2.md`; RUNBOOK do auditor revisado em `docs/03-auditor/RUNBOOK-v4.md` [PROPOSTA de nome]; steering/SOP em `templates/sop/`. Conteúdo: CTA **apenas "Segue o Porquê BR"**, colado ao gancho (t262); **nunca pedir comentário** (t263); nenhum critério visual de estilo reprova (t264/t265); 15 s a 3 min, alvo ~50 s (t271); V2-r3 a3 aprovada com ressalva no gabarito.
- **D4:** `src/pqbr/pipeline/auditor/` (`decide.py`, prompts IDENT com o critério t264/t265; quadros por cena + Whisper; Gemini 3.8 Flash no modo normal, sim/não por traço, 2 rodadas em chats novos; Jev ou código nas checagens de texto; relatório por `templates/relatorios/auditor.md`). Detector de pedido de comentário; direitos de áudio bloqueantes acima de 60 s. Testes em `tests/auditor/` com o labels.json completo + vídeos novos.
- **Aceite:** contrato v2 e RUNBOOK aprovados pelo José; `decide.py` coerente com eles; falso aprovado e falso reprovado medidos no gabarito ampliado.
- **Portão G7:** José aprova o contrato v2, o RUNBOOK e a matriz do auditor. Fecha os **itens 1 e 3 da validação**.
- **Rollback:** manter o v1 e o auditor v3 marcados como vigentes até a aprovação.
- **Dependências:** D3; H10 (juiz visual em produção).

#### Fase 8: D7 + D13, publicação e armazenamento
- **D7:** `src/pqbr/integrations/youtube_publish.py`: `videos.insert` com agendamento (t273); **até a auditoria do app (H1), sobe privado e o Camofox agenda pelo Studio**; o Studio via Camofox também é a reserva. Sem duplicidade: código PQBR-EPxxxx na descrição e numa etiqueta; busca no Supabase **e no canal**, incluindo privados e agendados; 1 tentativa sem confirmação, depois para e avisa o José. Reserva de ≥ 2 aprovados; sem reserva, o horário é cancelado; teto de 4/dia sem mínimo; vídeo reprovado nunca é publicado. Jev confere se o agendado bate com o aprovado.
  - Regra do item 5 em código, `src/pqbr/pipeline/item5.py`: **qualquer** problema → privado na hora + Telegram com motivo; **sem substituição nem republicação**; volta a público só com o toque do José (mesmo link); exclusão só pelo José com dupla confirmação; limiar de comentários t239/t243; HOLD de conformidade torna privados os já agendados; toda ação registrada no Supabase e vira lição.
  - Aceite: teste de upload interrompido sem duplicata; 1 agendamento por via; teste do item 5 num vídeo de teste privado.
- **D13:** `src/pqbr/storage/drive.py` + `scripts/limpeza_drive.py`. Estrutura `PQBR/` (t267): `00_Biblia_Visual`, `01_Contrato_e_SOP`, `02_Episodios/AAAA-MM/PQBR-EPxxxx_tema`, `03_Reservas`, `04_Privados_Revisao`, `05_Relatorios`, `99_Arquivo`. Tudo sobe (original bruto + editado); local apagado após conferir tamanho e hash; o **final fica no servidor até o upload ao YouTube ser confirmado** (t268). Limpeza noturna determinística **na rotina do @prod-director** (t270): duplicatas e órfãos vão para `99_Arquivo/_duplicados` e a lista vai ao José no relatório e no Telegram; exclusão só pelo José.
  - Aceite: duplicata de teste movida, nada excluído.
- **Portão G8:** José aprova o fluxo "privado + agendamento pelo Camofox" e o primeiro upload real. Fecha os **itens 4, 5 e 6 da validação**.
- **Rollback:** desligar o publisher (voltar ao fluxo antigo enquanto ele existir); vídeos de teste ficam privados.
- **Dependências:** D6, D4; H1, H2, H14.

#### Fase 9: D12, monitores e relatório diário
- **Entregáveis:** `src/pqbr/pipeline/monitor_atualizacoes.py` (semanal; notebooklm-py, Camofox/camofox-browser, Camoufox, Paperclip, Hermes, FFmpeg, Whisper, Pydantic, Supabase CLI, Jev SDK; o Jev julga relevância, o José autoriza no Telegram, depois worktree, smoke test, versão fixada e rollback; **nunca atualiza sozinho**); `monitor_consumo.py` (`usage --json` antes e depois de cada geração; acima de 80% numa janela, espaça as produções; tokens por chamada do Jev → média de gasto); `templates/relatorios/diario.md` (produção, consumo NotebookLM/Jev, compliance, comunidade, limpeza do Drive).
- **Aceite:** relatório chega ao Telegram por vários dias.
- **Portão G9:** José valida o formato do relatório. Os dados da primeira semana alimentam o **teto de orçamento** [PENDENTE-JOSÉ].
- **Rollback:** desligar as rotinas.
- **Dependências:** D7; H6, H8, H12.

#### Fase 10: D8 + D9 + D10, comunidade
- **D9:** banco de 60 frases (5 tipos × 12) rascunhado pelo NotebookLM no tom do contrato, em `templates/frases/banco-60.yaml`; `docs/01-editorial/guia-tom-comunidade.md`. Aceite: 60 frases aprovadas pelo José.
- **D10:** registro por escrito da regra do item 5 e da regra completa de respostas como instrução/consentimento expresso do dono (política da API III.I.2, III.E.3), em nova entrada de `docs/00-entrega/decisoes-jose-2026-10-08.md` ou arquivo de decisões sucessor. Aceite: entrada registrada.
- **D8:** `src/pqbr/community/`:
  - Leitura pela API (sem Camofox), cadência 30 min / 6 h / diária, inclusive `heldForReview` e `likelySpam`.
  - Pré-filtro: NFKC, confusables, links/WhatsApp/Telegram/PIX/e-mail/CPF/@, autor como hash com sal.
  - Jev multirrótulo, 2 rodadas só no que gera ação; retenção t244.
  - Respostas: elegibilidade pelo Jev, frase escolhida por código; não repete no vídeo, nas últimas 30 nem para a mesma pessoa; atraso 15–120 min; 3–12 min entre respostas; 6/h e 30/dia; 08h–22h; **1 por pessoa por vídeo** com ~24 h entre respostas à mesma pessoa (t274); exclusões da ENTREGA §7; conferência em 60 min.
  - Kill switch: `/pausar_respostas` só do ID do José, mais os gatilhos automáticos.
  - Corações via Camofox até 10/dia, só na sessão do guardião.
  - Conjunto de avaliação pt-BR em `tests/comentarios/` + matriz de confusão; texto bruto apagado em até 30 dias.
  - **1 resposta real de teste antes do automático (H3).**
- **Aceite:** 3 dias de sombra ou ~30 respostas simuladas aprovadas sem correção (t248); matriz aceita pelo José, que fixa o limiar.
- **Portão G10:** José liga respostas e corações automáticos.
- **Rollback:** kill switch e flag no banco; retenções são reversíveis.
- **Dependências:** D3, D6, D7 (item 5); H3, H4, H7, H8, H16.

#### Fase 11: D15, estratégia para 2 personagens (não bloqueia, t264)
- **Entregáveis:** `docs/sdd/d15-dois-personagens.md` com testes de preservação das fichas no NotebookLM e uma alternativa (narração do NotebookLM + quadros de outra ferramenta montados em código). Fecha o **item 2 da validação** (3 vídeos reaproveitáveis com os mesmos personagens).
- **Aceite e portão G11:** decisão do José com evidência.
- **Dependências:** D1, D4.

#### Fase 12: validação final e liberação da produção
- **Objetivo:** os 7 itens da validação com critério cumprido; definição de sucesso do piloto; liberação gradual.
- **Entregáveis:** `docs/sdd/validacao-7-itens.md` (evidência por item); `docs/sdd/liberacao.md` (ordem de despausar agentes e ligar heartbeats).
- **Portão G12 (José):** libera a produção e **despausa** os agentes, um a um; o CEO continua pausado salvo decisão contrária.
- **Rollback:** pausar os agentes; HOLD da fila.
- **Dependências:** todas as anteriores; budgets definidos.

---

## 4. Hipóteses que travam fases

H1–H16 conforme a ENTREGA §10 (dono, critério de pronto). Acréscimos **[PROPOSTA]**:
- **H-SDD1:** o adapter `hermes_local` pode rodar sem `--yolo` (ou existe um adapter alternativo que respeite o perfil `pqbr`). Trava a Fase 2 para agentes LLM.
- **H-SDD2:** sintaxe atual do `paperclipai company import … --target new --dry-run` e suporte a criar agentes já pausados. Trava a Fase 2.
- **H-SDD3:** o adapter `process` (ou equivalente) serve aos executores determinísticos sem LLM.

---

## 5. Pendências que precisam do José

1. **Teto de orçamento mensal:** definido com os dados dos primeiros dias ou da primeira semana de testes (t268 / decisão 10). Até lá, budgets do `.paperclip.yaml` mínimos e agentes pausados.
2. **Horários das janelas de publicação:** os documentos citam 11:40/14:40/18:35/21:00 e 11:40/18:35/21:15.
3. **@prod-director: LLM ou rotina determinística** (dossiê g.10).
4. **Persona do @prod-compliance e do @pqbr-assistente:** a definir.
5. **Equipes no pacote** [PROPOSTA: nenhuma no início] e **papel do CEO** (raiz pausada acima do director) [PROPOSTA].
6. **Destino dos arquivos do CTO** [PROPOSTA: arquivar em `docs/99-historico/cor1-cto-2026-10-09/`] e o que fazer com a COR-1 na core-eng.
7. **Aprovação das 60 frases (D9)** e do **contrato editorial v2 (D11)**.
8. **Configuração única do Studio** (moderação Básica/Rigorosa, reter comentários com link, palavras bloqueadas): sem resposta registrada.
9. **Definição de sucesso do piloto:** metas só depois da verificação pela API; recalibrar em 2–4 semanas.
10. **Roteiros de referência** a pedir ao `rede` (TV, sinal amarelo, controle remoto/fita, tomada do chuveiro).
11. **Decisões em aberto do dossiê (g):** memória (Hindsight vs. OpenViking no `rede`); papel do `rede` depois da org existir; migração do `yt_production`.
12. **3D/realista:** nunca pedido, aceito se vier (t265), já resolvido. **Juiz visual em produção:** Gemini web via Camofox vs. Gemini API, com a chave como decisão do José (H10).
13. **Rotações de credenciais:** senha do `paperclip_app`, root do Contabo, token do OpenCode; remover a senha do `paperclip_app` da fonte do caderno de arquitetura.
14. **Telegram do perfil `pqbr`:** a rota do tópico 5756 está com o José; ela bloqueia o @pqbr-assistente na liberação (G12), não o desenvolvimento.

---

## 6. Riscos

| Risco | Efeito | Mitigação |
|---|---|---|
| `hermes_local` força `--yolo` [VERIFICADO no dossiê] | Agente executa sem confirmação | H-SDD1 antes de despausar; executores determinísticos fora de LLM; perfil `pqbr` sem sudo sem senha |
| Repetir a deriva da COR-1 (outro canal) | Retrabalho | Constituição + matriz de rastreabilidade; todo `AGENTS.md` cita tNNN; revisão contra as decisões em cada PR |
| Sessão do NotebookLM com dois donos durante a migração | Bloqueio da conta / perda da produção atual | Logout da sessão antiga antes do login novo (t191); passo a passo autorizado; rollback ensaiado |
| Quedas da sessão do Studio (H9) | Publicação parada | Guardião + escada t272; publicação em espera; Camofox único dono do login |
| Auditoria do app do GCP demora (H1) | Sem upload público pela API | Sobe privado e o Camofox agenda (t273) |
| Cotas: Data API 10.000/dia; `search.list` e `videos.insert` com balde próprio de 100/dia; limites do Pro do NotebookLM | Falha no lote | Monitor de consumo; espaçar acima de 80%; `quotaExceeded` espera o reset |
| Desmonetização por "conteúdo inautêntico" / strikes | Saída do YPP | Compliance + HOLD + variedade no auditor; R10 |
| Respostas automáticas parecendo robô / remoção pelo YouTube | Dano ao canal | Banco aprovado, limites t274, sombra de 3 dias, conferência em 60 min, kill switch |
| Segredo vazado em issue (o plugin grava o corpo inteiro, autoRetain) ou no repo | Credencial exposta | D14 primeiro; pre-commit; nunca colar segredo em issue |
| Supabase fora | Estado perdido / publicação duplicada | Buffer local atômico; nada agendado ou público sem estado gravado (t242) |
| Dados do canal divergentes (30 vs. 46 Shorts) | Metas erradas | Métricas só pela Analytics API (H12); analista só observa até ~30 Shorts |
| ToS do Studio ("automated means") e termos comerciais do NotebookLM/Gemini (H11) | Risco de conta | Camofox em ritmo humano; leitura de comentários só pela API; registro dos termos |
| Disco do servidor (temporário) | Falta de espaço | Ciclo t267/t268; `runtime/` fora do git e limpo a cada ciclo |
| Template `paperclipai/companies` parado desde 23/03/2026 [VERIFICADO] | Formato desatualizado | Pacote próprio validado pela especificação atual; skills com commit fixado |
