> ⛔ **ARQUIVO — não consultar sem aprovação do José.** Superado pelos docs canônicos (README).

> ⛔ **SUPERADO — ARQUIVO DE PRÉ-CONSTRUÇÃO. NÃO USAR PARA DECIDIR. AGENTES NÃO CONSULTAM SEM APROVAÇÃO EXPLÍCITA DO JOSÉ (t287).**
> Original: `docs/99-historico/dossie-preparacao-pqbr.md`. Motivo: dossiê de preparação para a core-eng (abortada, t284). E-mail pessoal e IP da tailnet removidos em 09/10. As regras válidas estão em `docs/REGRAS.md`.

# Dossiê de preparação: PorqueBR Production (pqbr)

> **Este documento não é o blueprint.** Ele reúne a pesquisa feita antes de desenhar a organização `porquebr-production` no Paperclip, que depois será delegada à org `core-engineering` (agente `core-engenheiro` / @eng-cto).
> Data: 07/10/2026 (horário de Fortaleza). Métricas de popularidade coletadas nesse dia pela API do GitHub e de skills.sh. Os textos de terceiros estão resumidos aqui, nunca copiados.
> Convenção: **[NB: título]** indica a fonte do caderno NotebookLM `f3b90c97…` ("Arquitetura de Confiabilidade, Automação e Dev com PaperClip…"). **[HERMES-rede]** indica leitura somente-leitura de `~/.hermes/profiles/rede/skills` no host `pc` (<IP da tailnet removido>). **⚠ confirmar com Hermes atual** indica algo possivelmente desatualizado ou contraditório.

---

## 0. Resumo executivo

1. **Já existe um blueprint pqbr v3.3/v3.4 no caderno**, com 7 agentes (@prod-director, ideador, roteirista, render, auditor, seo, publisher), Hindsight `porquebr-production-bank`, contratos Pydantic v2 e o runbook de provisionamento pela core-eng. O próximo blueprint deve **partir dele e corrigir as inconsistências** listadas na §5.3, em vez de começar do zero. [NB: 📘 Blueprint … PorqueBR v3.3.md] [NB: Blueprint de Produção e Agentes]
2. **Não existe template "de marketing" pronto para Shorts em companies.sh.** O catálogo tem 16 empresas, todas de `paperclipai/companies`. A única com divisão de marketing é a **Agency Agents** (167 agentes, 0 skills próprias, e cada agente é só um stub que aponta para o repo upstream `msitarzewski/agency-agents`). Parte do que o caderno afirma sobre os rosters da Agency Agents e da TÂCHES Creative **não confere com o repositório** (§3.2).
3. **Recomendação de template:** montar um **pacote Agent Companies próprio** (`pqbr-company/`, com COMPANY.md, TEAM.md, AGENTS.md, SKILL.md, TASK.md e `.paperclip.yaml`), usando cerca de 6 a 8 papéis da Agency Agents como fonte de texto de persona e a governança do GStack como referência. A importação seria com `paperclipai company import ./pqbr-company --target new --dry-run`. Importar a Agency Agents inteira traria 160 agentes inúteis.
4. **Publicação é o maior risco.** A esteira atual publica pelo YouTube Studio via **Camofox** (jo-inc/camofox-browser + Camoufox), o que entra em conflito direto com a cláusula de "automated means" dos Termos do YouTube. A **YouTube Data API** ficou muito mais barata em 2026: `videos.insert` custa 1 unidade num balde próprio de 100 uploads por dia. Porém, sem auditoria de conformidade, os vídeos ficam travados como privados. O usuário já tem OAuth em modo dry-run e o MCP `youtube-shorts-agent` conectado.
5. **O Hindsight funciona com Supabase.** Com `HINDSIGHT_API_DATABASE_URL` e `HINDSIGHT_API_DATABASE_SCHEMA=hindsight` ele usa pgvector, que já vem no Supabase. Hoje a core-eng roda Hindsight 0.10.2 com pg0 embutido em 127.0.0.1:8890. O perfil Hermes `rede` **ainda usa OpenViking** como memória (⚠ confirmar com Hermes atual).
6. **O conhecimento operacional real está no Hermes `rede`.** A skill `rotina-producao-porqu-br` (v2) é a principal fonte de "o que quebra": seletores Polymer, COPPA, challenge de passkey, deduplicação, timezone UTC×BRT, fuga de metadados do NotebookLM e polling falso. Isso deve virar skills internas da pqbr, não persona.
7. **Skills da comunidade com tração** (installs em skills.sh): coreyhaines31/marketingskills (`copywriting` 218k, `content-strategy` 152k, `video` 77k, `social-content` 67k), heygen-com/hyperframes (~0,7 a 0,85M por skill), remotion-best-practices (581k), supabase/agent-skills (`supabase-postgres-best-practices` 434k), higgsfield-youtube-thumbnail (78k), teng-lin/notebooklm-py (9,5k), kostja94 `youtube-seo` (3,1k), digitalsamba `ffmpeg` (10k).

---

## (a) Avaliação de cada fonte indicada pelo José

| Fonte | O que é | Mantenedor / licença | Sinais (07/10/2026) | Maturidade |
|---|---|---|---|---|
| skills.sh › claude-office-skills/youtube-automation | SKILL.md genérico de "automação de canal" | claude-office-skills / MIT | repo com 499★, último push em 31/01/2026, 4.650 installs; skills.sh mostra "Gen Agent Trust Hub: Pass / **Snyk: Warn**" | Baixa |
| companies.sh | Diretório/CLI de "Agent Companies" para Paperclip | Paperclip | 16 empresas; mais instaladas: GStack 682, Agency Agents 268, Superpowers 207 | Média |
| github.com/paperclipai/companies | Repo-fonte das 16 empresas | paperclipai / MIT (badge; a API não detecta) | 909★, **último commit em 23/03/2026** (sem atualização há cerca de 6 meses) | Média, mas parada |
| davidmosiah/youtube-shorts-agent | CLI + servidor MCP para upload de Shorts pela YouTube Data API, com dry-run | davidmosiah (Delx) / MIT | **1★**, v0.1.9 em 29/08/2026 | Inicial, porém útil |
| poseljacob/agentic-video-editor | Editor agêntico (Gemini via ADK + FFmpeg) que monta anúncios a partir de footage e brief | poseljacob / MIT | 496★, criado e parado em 14/04/2026 | Protótipo |
| HKUDS/VideoAgent | Framework de pesquisa (EMNLP) para entender, editar e "refazer" vídeo | HKU Data Science Lab / MIT | 1.924★, push em 22/07/2026, sem releases | Pesquisa acadêmica |
| kostja94/marketing-skills | Biblioteca de cerca de 170 skills de marketing/SEO | kostja94 / MIT | 1.019★, push em 06/10/2026, v1.0.0 (03/2026); `youtube-seo` com 3.121 installs | Boa, viés web/SEO |

### a.1 claude-office-skills/youtube-automation
- **Conteúdo:** fluxo genérico (upload → metadados → thumbnail → agendamento), checklists de SEO, tags, analytics, calendário, comentários e playlists. Depende de um MCP hipotético `youtube-mcp`, os modelos listados estão desatualizados (Claude 3 / GPT-4) e os idiomas são en/zh.
- **Reuso para a pqbr:** pouco. No máximo serve de checklist para o @prod-seo (estrutura de descrição, tags) e para um futuro agente de comentários.
- **Riscos:** foca em vídeos longos e em inglês, tem alerta do Snyk e nenhuma lógica específica de Shorts (loop, 0–3s, COPPA, disclosure de IA). **Não instalar como está.**

### a.2 companies.sh + paperclipai/companies
- **Como funciona:** cada empresa é um pacote no formato Agent Companies (`COMPANY.md`, `teams/*/TEAM.md`, `agents/*/AGENTS.md`, `skills/*/SKILL.md`, `.paperclip.yaml`). Há dois jeitos de instalar: `npx companies.sh add paperclipai/companies/<slug>`, ou `paperclipai company import <fonte> --target new --new-company-name … --agents a,b,c --dry-run`. Agentes importados chegam **com heartbeat desligado** e, por padrão no app, com rotinas pausadas. [docs Paperclip: importing-and-exporting.md]
- **Precedente do José:** a core-eng foi criada com `paperclipai company import paperclipai/companies/gstack --target new --include company,agents --agents all`, porque o `companies.sh add` não permite nomear a empresa. [NB: BLUEPRINT_CORE_ENGINEERING.md §7]
- **Empresas relevantes para conteúdo:**
  - **Agency Agents** (de msitarzewski/agency-agents, 158k★ no upstream): 10 times. O time **marketing** tem o `cmo` como gestor e cerca de 34 agentes, como `marketing-content-creator`, `marketing-seo-specialist`, `marketing-short-video-editing-coach`, `marketing-tiktok-strategist`, `marketing-social-media-strategist`, `marketing-growth-hacker` e vários voltados a plataformas chinesas. Fora do marketing há outros úteis: `creative-director`, `narrative-designer`, `product-trend-researcher`, `academic-historian` e `academic-anthropologist` (bons para o ângulo "por que o Brasil é assim"), `specialized-cultural-intelligence-strategist`, `testing-reality-checker`, `testing-evidence-collector`, `qa-director`, `support-analytics-reporter`, `project-management-studio-producer` e `agents-orchestrator`.
    - **Atenção:** os AGENTS.md são **stubs com `usage: referenced`**. A persona real fica no arquivo upstream fixado por commit. Quem importa recebe só o ponteiro, ou precisa "vendorizar" o conteúdo.
  - **TÂCHES Creative:** os agentes reais são `ceo, quality-auditor, research-lead, skills-architect, strategy-director, workflow-designer`. É um time de **estratégia e meta-prompting**, não de produção de mídia. As 35 skills são do tipo "consider-*", "research-*" e "create-*". Como base de produção, serve pouco.
  - **MiniMax Studio:** a única skill de mídia é `gif-sticker-maker`. Irrelevante.
  - **Paperclip teams-catalog** (dentro do repo do Paperclip): o time opcional `content-machine` (ContentLead + projeto `content-operations` + rotina `weekly-content-review` + skill `content-calendar`) é um bom **exemplo mínimo de rotina via TASK.md**.
- **Riscos/lacunas:** repo de templates parado desde março, nenhum template de vídeo ou Shorts, e personas em inglês e genéricas.

### a.3 davidmosiah/youtube-shorts-agent
- **O que oferece:** ferramentas MCP `youtube_connection_status`, `youtube_privacy_audit`, `youtube_oauth_authorize_url` (PKCE local), `youtube_upload_short` (com `containsSyntheticMedia`), `youtube_list_recent_videos` e `youtube_agent_manifest`. O **dry-run vem ligado por padrão** (`YOUTUBE_DRY_RUN`).
- **Contexto do José:** esse MCP **já está conectado** na conta do José como `user-youtube-shorts`, e `/workspace/yt-llm-bot/youtube-auth/` já tem OAuth configurado em modo dry-run.
- **Reuso:** é o candidato natural para o **@prod-publisher pela via oficial** e para a checagem pós-publicação (listar os vídeos recentes e confirmar o ID).
- **Riscos:** só 1★ e um único mantenedor. Não resolve a auditoria da API (sem ela, o vídeo fica privado). Convém fixar a versão e revisar o código antes de passar o token de produção.

### a.4 poseljacob/agentic-video-editor
- **Padrão útil:** um **pipeline em YAML** com as etapas Director → Trim Refiner → Editor (FFmpeg) → Reviewer, em que o Reviewer dá nota de 0 a 1 em 5 dimensões e devolve feedback ao Director até 2 vezes. Os style templates em YAML definem duração de segmentos, pacing e overlays.
- **Reuso:** o **conceito** de "reviewer com limiar e feedback dirigido" para o @prod-auditor/JEV, e de "style YAML" para codificar a bíblia Stickman (beats de 1,5 a 2,0 s, loop, CTA). Não faz sentido usar o código: ele parte de footage real e foi feito para anúncios DTC, enquanto a pqbr gera o vídeo no NotebookLM.
- **Riscos:** projeto de um fim de semana, parado desde abril, e a UI está em WIP.

### a.5 HKUDS/VideoAgent
- **Padrão útil:** análise de intenção → grafo de ferramentas → auto-avaliação em dois passos, além de um "Storyboard Agent" que transforma o pedido em consultas visuais.
- **Reuso:** apenas ideias (por exemplo, decompor a pauta em sub-intenções visuais para o steering do NotebookLM). Não recomendo como dependência.
- **Riscos:** código acadêmico pesado (muitos modelos), sem releases e sem foco em produção estável.

### a.6 kostja94/marketing-skills
- **Skills relevantes:** `platforms/youtube` (nome `youtube-seo`: título com menos de 60 caracteres, palavra-chave no começo, descrição com as 2 ou 3 primeiras frases ricas, tags como sinal secundário, coerência entre título, descrição e thumbnail), `content/video` (estrutura de short-form, os 3 primeiros segundos, ganchos por plataforma), `seo/content/keyword-research`, `content-strategy`, `competitor-research`, `analytics/*` e `content/translation`.
- **Reuso:** base para o @prod-seo e o @prod-ideador. Requer adaptação para PT-BR, porque as skills esperam um `contextus.md` e o equivalente na pqbr seria a bíblia do canal.
- **Riscos:** o foco é SEO de sites, e as estatísticas citadas nas skills não têm fonte verificável (tratar como heurística).

---

## (b) Recomendações da comunidade por área

| Área | O que a comunidade usa ou recomenda | Sinal | Leitura para a pqbr |
|---|---|---|---|
| Geração end-to-end de Shorts | MoneyPrinterTurbo (129k★, ativo), MoneyPrinter (14k★), ShortGPT (8k★, parado desde 02/2025), short-video-maker MCP (1,4k★, parado) | estrelas | Todos usam o fluxo TTS + stock + legendas, sem identidade própria. A pqbr já é mais sofisticada (NotebookLM + Stickman). Vale como referência de legendas e montagem, não como base. |
| Render programático | **HyperFrames** (heygen-com, 58k★, Apache-2.0, "HTML → vídeo, feito para agentes") e **Remotion** (62k★, licença própria e paga para empresas acima de certo porte) | installs de 0,6 a 0,85M | Para overlays, legendas animadas e stings, o HyperFrames encaixa melhor em agentes. O FFmpeg VAAPI continua no corte, logo e loudness. |
| FFmpeg via skill | `digitalsamba/claude-code-video-toolkit/ffmpeg` (10k installs, repo com 2,2k★), `affaan-m/ecc/video-editing` (12k) | installs | Bom material para uma skill interna "fpmp-ffmpeg-vaapi". |
| Copy, roteiro e ganchos | coreyhaines31/marketingskills (53,6k★, v2.11.19 publicada hoje): `copywriting`, `video`, `social-content`, `marketing-psychology` | 67k a 218k installs | É a biblioteca de marketing mais adotada. Adaptar ao formato "Mas/Então", microbeats e loop. |
| Pesquisa e tendências | `mvanhorn/last30days` (44,8k installs), `agent-reach` (já existe no Hermes rede), NotebookLM Deep Research | installs | Serve ao @prod-ideador (tendências BR) com deduplicação por `theme_hash`. |
| Thumbnail e capa | `higgsfield-ai/skills/higgsfield-youtube-thumbnail` (78k) e a skill local `capa-canal-porqu-br` | installs | Em Shorts, thumbnail personalizada tem uso limitado. O foco certo é a **capa/frame dos 0 a 3 s** (critério A9 do gate local). |
| Memória de agentes | **Hindsight** (vectorize-io, 46,8k★, MIT, v0.10.2 em 29/09) com plugin oficial para Paperclip e provider para Hermes | estrelas, integrações oficiais | É a escolha já feita na core-eng. Ver §(f). |
| Estado e filas | Postgres com `FOR UPDATE SKIP LOCKED` (já em uso), **pgmq** / Supabase Queues (5,3k★), DBOS Transact (1,6k★, workflows duráveis sobre Postgres) | estrelas | O `durable_runner.py` caseiro funciona. DBOS e pgmq são alternativas a avaliar se ele crescer. |
| Contratos tipados | Pydantic v2 (29k★) + **PydanticAI** (20,5k★, `retries` com auto-correção); skill `pydantic/skills/building-pydantic-ai-agents` | estrelas | Já é o padrão no `schemas/shorts.py`. Manter. |
| Supabase com agentes | `supabase/agent-skills` (`supabase-postgres-best-practices` 434k, `supabase` 312k) e o MCP Supabase (já conectado) | installs | Instalar no agente da core-eng que vai migrar o `yt_production`. |
| NotebookLM | teng-lin/notebooklm-py (19,6k★, MIT, v0.8.4 em 02/10; o box está na 0.8.2) + skill oficial (9,5k installs) | estrelas | Seguir o modo recomendado pelo próprio projeto: **auth com master token** para uso headless, `--json` e IDs explícitos. |
| Navegador anti-detect | daijro/camoufox (12,4k★, MPL-2.0, beta v156.0.1-beta.36) e jo-inc/camofox-browser (11,5k★, MIT, v1.18.1 em 05/10, REST na porta :9377) | estrelas | É o que o Hermes rede usa. Risco de ToS, ver §(f). |
| Publicação | YouTube Data API (`videos.insert`), youtube-shorts-agent (MCP), porjo/youtubeuploader (885★, Go, ativo) | docs oficiais | Via oficial: barata desde 06/2026, mas exige **auditoria** para publicar como público. |
| Observabilidade de LLM | pydantic/logfire (4,5k★) | estrelas | Opcional, integra nativamente com PydanticAI. |

**Política do YouTube a considerar:** as diretrizes de monetização tratam conteúdo produzido em massa ou repetitivo como "inauthentic content", e o YouTube exige divulgação de conteúdo sintético realista (na API, o campo `containsSyntheticMedia`). O gate editorial local (B1 a B10, com "GenAI disclosure") já prevê isso.

---

## (c) Estratégia de template

**Conclusão:** sim, vale usar template como a core-eng fez, mas **não como importação crua**. A Agency Agents não tem nenhum agente executor de mídia, e o pacote só traz ponteiros.

**Caminho recomendado:**
1. A core-eng cria um **pacote próprio** `pqbr-company/`, versionado em git, seguindo a especificação Agent Companies:
   - `COMPANY.md`: goal, fronteiras e canal.
   - `teams/producao/TEAM.md` com o @prod-director como manager.
   - `agents/<slug>/AGENTS.md`: persona em PT-BR, com a seção "sources" atribuindo o texto adaptado da Agency Agents (MIT).
   - `skills/`: as skills internas descritas na §(e).
   - `tasks/`: as rotinas (preflight 06:00, refresh do NotebookLM a cada 15 min, janelas de publicação, revisão semanal).
   - `.paperclip.yaml`: adapter `hermes_local` com o perfil dedicado, entradas de env e budgets.
2. Antes de importar de verdade, rodar `paperclipai company import ./pqbr-company --target new --new-company-name "PorqueBR Production" --dry-run`.
3. Uma alternativa mais rápida para comparar: `paperclipai company import paperclipai/companies/agency-agents --target new --agents cmo,creative-director,marketing-content-creator,marketing-seo-specialist,marketing-short-video-editing-coach,product-trend-researcher,testing-reality-checker,support-analytics-reporter --dry-run`, renomeando depois. O ponto fraco é que as personas continuam como ponteiros upstream em inglês.

**Mapeamento de papéis da pqbr para as fontes de template:**

| Agente pqbr (blueprint v3.3) | Natureza | Fonte de persona sugerida | Skills-base (comunidade + locais) |
|---|---|---|---|
| @prod-director | coordenação e cadência | `project-management-studio-producer` / `agents-orchestrator` (Agency) + padrão "CEO pausado" do GStack | rotinas em TASK.md; `durable-orchestration` [HERMES-rede] |
| @prod-ideador | pesquisa e pauta | `product-trend-researcher`, `academic-historian`, `academic-anthropologist`, `specialized-cultural-intelligence-strategist` | `last30days`, `content-strategy` (coreyhaines), `keyword-research` (kostja94), `agent-reach` [HERMES-rede], NotebookLM research |
| @prod-roteirista | roteiro Stickman | `marketing-content-creator`, `narrative-designer` | `copywriting` + `video` (coreyhaines), `content/video` (kostja94), `humanizer` [HERMES-rede], Fábrica/SOP no NotebookLM [local] |
| @prod-render | executor determinístico | `marketing-short-video-editing-coach` (só como "olho" editorial) | notebooklm-py, `p-s-short-porqu-br` [local], FFmpeg VAAPI, HyperFrames (opcional) |
| @prod-auditor | QA multimodal | `testing-reality-checker`, `testing-evidence-collector`, `qa-director` | `gate-pr-publish-porqu-br` [local], `gemini-web-video-auditor` [HERMES-rede], padrão Reviewer do agentic-video-editor |
| @prod-seo | metadados | `marketing-seo-specialist` | `youtube-seo` (kostja94), `seo-audit`/`ai-seo` (coreyhaines), `ops/seo-pack-template-short.md` [local] |
| @prod-publisher | executor determinístico | (sem persona: script) | youtube-shorts-agent (API) **ou** Camofox; trava anti-duplicação |
| **@prod-analista** (lacuna) | telemetria e aprendizado | `support-analytics-reporter`, `testing-test-results-analyzer` | `analytics` (coreyhaines), YouTube Analytics API, retain no Hindsight dos ganchos que funcionaram |

> O blueprint v3.3 diz que o Hindsight guarda "estruturas e ganchos com maior retenção comprovada na telemetria", mas **não há nenhum agente que leia analytics**. Ou se adiciona o @prod-analista, ou essa tarefa vai para o @prod-director.

---

## (d) Skills candidatas da comunidade por capacidade

| Capacidade | Skill / repo | Popularidade | Observação |
|---|---|---|---|
| Copy e roteiro curto | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) `copywriting`, `video`, `social-content`, `marketing-psychology` | 53,6k★; 218k / 77k / 67k / 154k installs | Adaptar para PT-BR e para a fórmula Mas/Então |
| SEO YouTube | [kostja94/marketing-skills](https://github.com/kostja94/marketing-skills) `youtube-seo`, `keyword-research`, `content/video` | 1k★; 3,1k installs (youtube-seo) | Heurísticas de título e descrição |
| Tendências | [mvanhorn/last30days-skill](https://skills.sh) `last30days` | 44,8k installs | Avaliar se a cobertura de fontes BR é suficiente |
| Render e overlays | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) (`hyperframes`, `-cli`, `-animation`) | 58,5k★; ~0,7 a 0,85M installs | Apache-2.0; alternativa ao Remotion |
| Render (alternativa) | [remotion-dev/skills](https://github.com/remotion-dev/remotion) `remotion-best-practices` | 62k★; 581k installs | Atenção à licença |
| FFmpeg | [digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) `ffmpeg` | 2,2k★; 10k installs | Base para a skill VAAPI interna |
| Thumbnail e capa | `higgsfield-ai/skills/higgsfield-youtube-thumbnail` | 78k installs | Útil para a capa do canal; em Shorts o foco é o frame dos 0 a 3 s |
| NotebookLM | [teng-lin/notebooklm-py](https://github.com/teng-lin/notebooklm-py) skill `notebooklm` | 19,6k★; 9,5k installs | Já espelhada no Hermes (v0.8.2) |
| Supabase | [supabase/agent-skills](https://github.com/supabase/agent-skills) | 2,7k★; 434k / 312k installs | Para a core-eng (migração e RLS) |
| PydanticAI | `pydantic/skills/building-pydantic-ai-agents` | 5,2k installs | Contratos e retries |
| Paperclip | `paperclipai/paperclip/paperclip`, `paperclip-create-agent`, `paperclip-create-plugin` | 3 a 3,7k installs | Para o agente da core-eng que vai provisionar |
| Camofox | `yelban/camofox-browser-skills`, `redf0x1/camofox-browser` | 387 / 242 installs | Pouca adoção; as skills internas do rede são mais completas |
| Publicação via API | [davidmosiah/youtube-shorts-agent](https://github.com/davidmosiah/youtube-shorts-agent) (MCP) | 1★ | Já conectado; revisar o código |

**Alerta de confiabilidade:** skills.sh lista entradas como `101-skills/superpowers/ai-video-generation` com centenas de milhares de installs e vários forks quase idênticos. É um padrão típico de contagem inflada, então **não usar** essas entradas como sinal de qualidade. Prefira mantenedores reconhecidos (coreyhaines31, heygen-com, remotion-dev, supabase, pydantic, teng-lin).

**Divergência com o caderno:** o "Blueprint v3.4" do caderno cita as skills `skill-short-form-copy`, `skill-youtube-metadata-seo` e `skill-research-curation` como "skills da comunidade". **Não encontrei skills públicas com esses nomes.** Elas precisam ser **escritas** (sugestão: derivadas de coreyhaines `copywriting`/`video`, kostja94 `youtube-seo` e `last30days`). [NB: Blueprint de Produção e Agentes]

---

## (e) Inventário do Hermes `rede` e skills locais

### e.1 Como o acesso foi feito
- **Caderno NotebookLM** (perfil `jv`, somente leitura): listei as 78 fontes, li o texto integral de cerca de 30 fontes-chave e fiz **uma** pergunta focada no chat do caderno. Nada foi criado, apagado ou renomeado. A pergunta e a resposta ficaram no histórico de chat do caderno.
- **Host `pc`** (Tailscale <IP da tailnet removido>, onde o Hermes roda): acesso SSH somente leitura a partir do notebook do José (BOOK-9H2JJD2OTF). Perfis existentes: `core, gpu, mp3, pet, rede`. **Não li** `.env`, `auth.json`, tokens nem o `config.yaml` completo.
- **VPS `vmi3460009`:** o SSH como root foi recusado (publickey). Para inventariar a VPS seria preciso uma chave ou usuário autorizado, ou que o José rode `ls ~/.hermes/profiles` lá. Como o host `pc` respondeu, isso não foi necessário.

### e.2 Persona e ambiente do `rede`
O SOUL.md define o perfil como gestor operacional do canal Porquê BR / Tutibom Story:
- Esteira canônica em `/workspace/yt-llm-bot`, conta operacional `<conta operacional do canal (e-mail removido)>`, Camofox :9377 com perfil `porquebr`.
- A memória é o **OpenViking** (`memory.provider: openviking`).
- Plugins: `hermes-handoff` e `hermes-jev`.
- **⚠ confirmar com Hermes atual:** o blueprint diz que o Hindsight substituiu o OpenViking, mas isso valeu só para a core-eng.

### e.3 Skills específicas do canal (as que importam)

| Skill [HERMES-rede] | Para que serve | Dicas que devem ir para a pqbr |
|---|---|---|
| `rotina-producao-porqu-br` (v2, 206 linhas) | Pipeline completo pesquisa → roteiro → vídeo → pós → gate → publicação, persistido no Postgres `yt_production` | Ver lista detalhada abaixo |
| `gemini-web-video-auditor` | QA quadro a quadro via Gemini Web com "prompt vivo", saída em tabela por timestamp | Caderno do auditor **isolado** do de produção. Hard vetos: desvio temático/metalinguagem, CTA ausente, fala ou legenda truncada, Stickman ausente por mais de 2 s ou menos de 80% em cena, falta de humor, loop falso, **contaminação papercut**, dessincronia acima de 1 s, colisão com a UI, split-screen acima de 4 s. Resultado padrão: `AGUARDANDO_REVISAO_HUMANA` |
| `durable-orchestration` | Padrão de execução durável | Estado atômico (arquivo tmp + rename), job ID determinístico, idempotência antes de cada passo, anti-duplicação consultando a plataforma, backoff 30 s → 2 min → 8 min, estado `NETWORK_WAITING` que não gasta tentativa, varredura de recuperação no reboot, checklist diário, **delegação em duas fases (blueprint → autorização)**, validação em duas camadas (LLM observa, JEV pontua de 0 a 10) |
| `ecossistema-ponte-multitenant` | Camada "Ponte" com adapters compartilhados (camofox_client, notebooklm, ffmpeg_stamper) e registro de projetos | Um perfil Camofox, uma conta e um banco por projeto; contratos Pydantic separados por projeto |
| `produ-o-short-b1-notebooklm`, `p-s-short-porqu-br`, `gate-pr-publish-porqu-br`, `capa-canal-porqu-br`, `documentar-decis-es-de-projeto` | Mesmas skills que existem no box (ver e.4) | |
| `notebooklm` (v0.8.2) | Skill oficial do notebooklm-py | Preferir **master token** em uso headless. Validar com `auth check --test --json` |
| `self-hosted-agent-memory`, `hermes-external-memory` | OpenViking + Ollama | qwen3-embedding 0.6B (1024 dimensões) é a melhor opção para PT-BR. O mesmo modelo já é usado no Hindsight da core-eng |
| Outras gerais | `agent-reach`, `humanizer`, `youtube-content`, `browser-cookie-auth`, `blocked-page-recovery`, `planning-with-files`, `sdlc-review`, `telegram-router`, `vps-access`, além das categorias creative, productivity, research e software-development | `agent-reach` serve ao ideador; `humanizer` serve ao roteirista (é em inglês, adaptar) |

**Lições da `rotina-producao-porqu-br`** (resumo próprio):
- **Máquina de estados durável no Postgres:** `CRIADA → … → PUBLICADA`, ou os marcadores `ideated → scheduled → scripted → produced → ready_to_publish → published | blocked_human_required`.
- **Tabelas obrigatórias:** `channels`, `production_plans`, `pautas` (com `theme_hash`), `scripts`, `media_assets` (com sha256), `publication_queue` (com SKIP LOCKED), `publications` (com nomes de colunas canônicos) e `bot_action_logs` (com colunas fixas).
- **Roteamento por tier via 9router:** Flash low para SEO, combo 9-jr para pesquisa, Flash high ou Sonnet para roteiro e auditoria. O Jev cuida da deduplicação e da escolha de tier.
- **Recuperação de falhas:** cada tentativa precisa usar uma estratégia diferente. Se a mesma ação falhar 2 vezes, passa direto para o humano. Cinco chamadas idênticas disparam um halt. Toda chamada de ferramenta deve vir seguida de síntese.
- **Gates antes do upload:** (1) arquivos presentes; (2) regex anti-placeholder com `#shorts` e menção ao canal; (3) validador semântico pauta × SEO.
- **NotebookLM:**
  - Usar **cadernos efêmeros, um por episódio**. O caderno mestre compartilhado foi banido por contaminação.
  - Adicionar o roteiro como fonte antes de gerar, senão aparece o erro `rpc_code=3`.
  - Se o polling der timeout, **não regerar**: consultar `artifact list` e baixar.
  - Filtrar as linhas de metadado ("Continuing conversation…").
- **YouTube Studio (via Camofox):**
  - Navegar direto para `/videos/upload?d=ud`.
  - Fazer polling do input de arquivo.
  - Preencher com `execCommand('insertText')`, porque atribuir `innerText` não aciona o Polymer.
  - Marcar o rádio COPPA "não é para crianças", senão o vídeo fica como rascunho.
  - Paginar a lista de Shorts (30 por página) antes de auditar.
  - Selecionar o canal no switcher quando aparecer "Ops! Algo deu errado".
  - Diante de challenge de passkey: parar e passar para o humano.
  - Fazer upload só a partir de `~/.camofox/uploads/`; o corpo da requisição exige `userId` e `sessionKey`.
- **Agenda:** lote matinal das 06:00 às 09:30 com jitter de 12 a 18 min entre gerações. Upload em T-5 min de cada janela, com no mínimo 60 a 90 s entre uploads.
- **Pitfalls de infraestrutura:**
  - Comparar datas com `AT TIME ZONE 'America/Fortaleza'`, porque a janela das 21:00 cai no dia seguinte em UTC.
  - No cron, usar caminhos absolutos.
  - Não fazer `kill -9` em loop em processo supervisionado pelo systemd.
  - Nunca escolher o que publicar pela simples existência do mp4; checar `06-publicacao.json` e o Studio.
  - **Nunca apagar nem reenviar vídeos** (o reenvio é detectado por hash-match).
- **Lacunas declaradas na própria skill:** não há alerta automático de falha, e o watchdog não reseta jobs que ficaram `IN_PROGRESS` depois de uma queda.

**Pontos da skill que precisam de confirmação (⚠ confirmar com Hermes atual):**
- Ela ainda menciona CDP 9225 e `sync_auth_notebooklm_to_cdp.py` apesar de declarar o CDP banido.
- O "Episodes tracking" indica 39 Shorts publicados e 84 pautas (plano 2026-W39).
- Ela descreve o uso de uma senha para destravar o GNOME Keyring via comando. Isso é um risco de segurança e precisa ser revisto antes de levar qualquer coisa para a pqbr.

### e.4 Skills e material local no box
- **`produ-o-short-b1-notebooklm`:** roteiro de um Short via NotebookLM (cadernos Produção, Channel Clone, Episódio e Reserva; prompts 4.1 a 4.3 da Fábrica; áudio PT-BR; Pacote Short; trim e logo; limpeza do chat). **⚠ desatualizada:** ainda prefere a estética "papercut/kraft", que o auditor atual veta, e ancora a publicação às 19h30.
- **`p-s-short-porqu-br`:** trim de 2,5 s + logo bug v2 (canto superior direito, cerca de 45% de opacidade) + máscara no canto inferior direito, via `scripts/post-short.sh`, mantendo o dry-run. **⚠ confirmar:** o rede hoje corta em "fim da fala + 0,35 s".
- **`gate-pr-publish-porqu-br`:** gate fail-closed com probe técnico (9:16, até 180 s, áudio), QA visual (critérios A4 a A9, incluindo o frame-capa dos 0 a 3 s), revisão editorial B1 a B10 (fonte, não-conselho, título honesto, não feito para crianças, divulgação de IA) e relatório PASS / FAIL / P1_HOLD. Publicação ao vivo só com `KILL_PUBLISH=false` e autorização explícita.
- **`capa-canal-porqu-br`:** banner 2560×1440 com safe zone de cerca de 1546×423, kraft + teal `#0D9488`, sem faces e sem o amarelo do Vox.
- **`/workspace/yt-llm-bot`:** clone ou snapshot do repo privado `jvmendesjr/porque-br`. Contém o BOOTSTRAP-AGENTE (instala só com autorização), playbook de decisões, roadmap B1, branding, cerca de 25 SOPs em `ops/` (overlay, stickman, CTA, SEO pack, hooks, durações, kill-switches) e scripts `post-short.sh` e `prepublish-gate.sh`. Também tem `youtube-auth/` (OAuth do YouTube; arquivos sensíveis que não foram abertos).

### e.5 O que o caderno registra (fontes NB)
- **Arquitetura em duas organizações** (produção × engenharia) ligadas por tickets inter-org. O payload do ticket (`CodeDelegationTaskRequest`) leva módulo, gravidade, traceback e o comando de teste. [NB: Arquitetura Paperclip por Organizações] [NB: Fluxo de Tickets - Paperclip Org]
- **core-eng v3.2:**
  - GStack com 5 agentes e 27 skills; CEO pausado; heartbeats desligados.
  - Adapter `hermes_local` com o perfil `core` (só `NINEROUTER_API_KEY`) e modelo 9-jr. O adapter sempre passa `--yolo`.
  - Hindsight local em :8890 (bank `core-engineering-bank`, embedding qwen3 de 1024 dimensões, regra "não guardar código").
  - Plugin configurado **por empresa**.
  - O banco do Paperclip foi restaurado no Supabase (215 tabelas idênticas), mas a troca de `DATABASE_URL` aparece como **pendente**.
  - A org `rede_midia` usa o **Hindsight Cloud** como grupo de comparação.
  - [NB: BLUEPRINT_CORE_ENGINEERING.md]
- **pqbr v3.3 e v3.4:**
  - CWD `/home/pc/Workspace/porquebr/episodios`, prefixo `PQBR`.
  - Matriz que separa agentes cognitivos de módulos determinísticos (preflight, render, publisher e backup não usam LLM).
  - Contrato `RoteiroShort`: 50 a 220 palavras, 40 a 60 s, CTA obrigatório, sem placeholders.
  - `durable_runner.py` com quarentena `HOLD_HUMAN_REVIEW`.
  - Rotinas: 06:00, refresh a cada 15 min, janelas de publicação.
  - A v3.4 adota a Agency Agents como template.
  - [NB: 📘 Blueprint … PorqueBR v3.3.md] [NB: Blueprint de Produção e Agentes]
- **Esteira e retenção:**
  - Quadro zero com ação e 2 a 4 palavras na tela, microbeats de 1,5 a 2,0 s, loop sem emenda, -14 LUFS.
  - Teto de 20 gerações por dia (16 para estoque, 4 reservadas para oportunidades virais até as 16h).
  - Não apagar nem reenviar vídeos.
  - Catálogo de falhas FLH-01 a 08.
  - [NB: Especificação Arquitetural da Esteira…] [NB: 04-blueprint-arquitetural-esteira-shorts.md] [NB: 00-fonte-da-verdade-shorts-youtube.md] [NB: 06-catalogo-falhas-auditoria-shorts.md] [NB: 02/03-pesquisa…]
- **Modelos:** há oscilação entre o adapter `hermes_local` com 9-jr, os combos `core-alto` e `core-medio`, e chamadas diretas. [NB: Configuração do Combo Core-Alto] [NB: Escolha do Fluxo de Agentes]

---

## (f) Notas de stack e riscos

### f.1 Supabase Pro + Hindsight
- **Estado atual:** o Paperclip tem um projeto Supabase (`paperclip`, sa-east-1, Postgres 17.11), com a role `paperclip_app` e Data API sem permissões para anon/authenticated. A troca de `DATABASE_URL` aparece **pendente** no blueprint da core-eng, embora o cabeçalho da seção diga "operando" (⚠ confirmar). A esteira atual usa o Postgres **local** `yt_production` (contêiner mp32-postgres:55432), segundo o [HERMES-rede].
- **Hindsight no Supabase:** é suportado oficialmente. Basta `HINDSIGHT_API_DATABASE_URL` (conexão direta ou session pooler), `HINDSIGHT_API_MIGRATION_DATABASE_URL` (conexão direta, quando houver pooler transacional) e `HINDSIGHT_API_DATABASE_SCHEMA=hindsight`. O pgvector já vem no Supabase. Opções:
  - **(a)** schema `hindsight` no mesmo projeto do Paperclip: mais barato, menos isolado;
  - **(b)** projeto Supabase separado para memória: custo de compute próprio;
  - **(c)** manter o pg0 local: é o estado atual, sem backup gerenciado.
- **Cuidados:**
  - A dimensão do embedding fica fixa enquanto o banco tiver dados.
  - O plugin do Paperclip grava **o corpo inteiro dos comentários** (autoRetain). Não colar segredos em issues.
  - A memória é indexada por companyId + agentId, ou fica estática com `bankId`.
  - A documentação lista os adapters Claude, Codex, Cursor, HTTP e Process como compatíveis. O caminho completo **via `hermes_local` ainda não foi testado num heartbeat real** (pendente na core-eng).
- **Hermes:** o Hindsight é hoje um provider do catálogo de plugins (`hermes plugins install hindsight`, depois `hermes memory setup`), com modos cloud, local_embedded ou local_external. Isso permitiria apontar o perfil rede, ou um novo perfil `pqbr`, para o mesmo servidor :8890 e abandonar o OpenViking.
- **Supabase Pro:** projetos pagos não pausam por inatividade, e a franquia é de 8 GB de disco por projeto [NB: BLUEPRINT_CORE_ENGINEERING.md §8]. O plano Pro **não foi confirmado** pelo MCP.

### f.2 Pydantic v2
- Já é o padrão (`schemas/shorts.py`, PydanticAI com `retries=3`).
- Recomendo um **pacote único de contratos** (por exemplo `pqbr_contracts`) consumido tanto pelos agentes quanto pelos scripts, com modelos `Pauta`, `RoteiroShort`/`MicroBeat`, `LaudoAuditoria` (com notas JEV), `SeoPack`, `PublicationRecord` e `CodeDelegationTaskRequest`. Gerar JSON Schema a partir deles serve aos prompts e às ferramentas MCP.
- **Ajuste necessário:** o rede depende do nome exato das colunas de `publications` e `bot_action_logs`. Os modelos devem espelhar o schema real.

### f.3 notebooklm-py
- **API não oficial,** baseada em RPC do Google, e pode quebrar sem aviso. Fixar a versão (box na 0.8.2, upstream na 0.8.4).
- **Autenticação:** o próprio projeto recomenda **master token** em uso headless. O rede ainda copia cookies Camofox → `storage_state.json` com refresh a cada 15 min, o que é mais frágil.
- **Contas:** produção em `juniormoedavirtual`; o caderno de arquitetura está em `jvmendesjr` (perfil `jv` no box). Manter perfis separados com `NOTEBOOKLM_PROFILE`.
- **Hábitos do rede que devem continuar:** cadernos efêmeros por episódio, fonte única por episódio, nunca usar `ask --new` (apaga a conversa), polling tolerante e respeito ao limite de cerca de 20 gerações por dia.

### f.4 Camofox / Camoufox no YouTube Studio
- **Projetos:** o daemon `:9377` é o **jo-inc/camofox-browser** (MIT, REST com `userId`/`sessionKey`, uploads restritos a um diretório, login via VNC). Ele roda sobre o **daijro/camoufox** (MPL-2.0, Firefox com spoofing de fingerprint em C++, ainda beta).
- **Telemetria:** o camofox-browser envia, por padrão, telemetria anônima de crash e travamento como issues no GitHub. Verificar e desligar antes de usar com o Studio.
- **Risco de ToS:** os Termos do YouTube proíbem acessar o serviço "por meios automatizados" sem permissão escrita, e proíbem contornar mecanismos de segurança. Isso é anti-detect aplicado à conta do canal. O risco vai de challenge de passkey e logout silencioso até **restrição ou encerramento do canal**. O histórico do rede (CDP rejeitado, "navegador não seguro", passkey) mostra que o Google já detecta o padrão.
- **Fragilidade:** seletores Polymer mudam, e cada mudança vira um ticket para a core-eng.
- **Alternativa oficial:**
  - **YouTube Data API:** `videos.insert` passou a custar 1 unidade num balde próprio de 100 uploads por dia (mudança de 01/06/2026).
  - **Porém** vídeos de projetos não verificados (criados depois de 28/07/2020) ficam travados como privados até a **auditoria de conformidade**, que é diferente da verificação OAuth. O formulário de auditoria exige demonstrar "valor independente".
  - A API cobre agendamento (`publishAt`), `containsSyntheticMedia`, `selfDeclaredMadeForKids` e a listagem dos vídeos para deduplicar.
- **Arquitetura sugerida:** API como caminho primário (depois da auditoria); Camofox apenas para leitura e verificação, ou como fallback manual assistido; publicação sempre passando por gate e kill-switch.

### f.5 Outros riscos
- **Execução sem confirmação:** o adapter `hermes_local` sempre passa `--yolo`, e o SOUL do rede menciona sudo sem senha. Agentes da pqbr **não** devem herdar isso. A recomendação é um perfil Hermes dedicado (`pqbr`, análogo ao `core`) com env mínimo, toolsets restritos e budgets definidos antes de ligar os heartbeats.
- **Template parado:** o repo `paperclipai/companies` não muda desde 03/2026. Fixar a importação com `--ref <commit>`.
- **Auditor via Gemini Web dentro do Camofox:** tem o mesmo risco de ToS e a mesma fragilidade. Avaliar a Gemini API (o próprio rede a lista como fallback).
- **Alucinações nas fontes do caderno:** os rosters dos templates e os nomes de skills (§3.2, §d) e o "Stickman 2D Papercut" do v3.3 entram em conflito com a regra anti-papercut do auditor. Verificar antes de copiar para o blueprint.

---

## (g) Decisões em aberto para o José (antes do blueprint)

1. **Publicação:** Camofox no Studio (como hoje), YouTube Data API depois da auditoria, ou híbrido (API publica, Camofox só verifica)?
2. **Template:** pacote próprio `pqbr-company` com personas adaptadas (recomendado), ou importar a Agency Agents com `--agents` selecionados?
3. **Estado da esteira:** migrar `yt_production` para o Supabase? Se sim, schema no projeto do Paperclip ou projeto separado? E o Hindsight vai para o Supabase (schema `hindsight`) ou fica no pg0 local?
4. **Memória:** um bank único `porquebr-production-bank` ou um por agente? O perfil Hermes rede deixa o OpenViking e passa para o Hindsight?
5. **Perfil e adapter:** criar um perfil Hermes `pqbr` dedicado (como o `core`) ou reaproveitar o `rede`? Qual o papel do `rede` depois que a org existir: aposentar, virar operador humano-assistido ou ficar só como fallback?
6. **Cadência:** 3 ou 4 Shorts por dia, e em quais horários? Os documentos citam 11:40/14:40/18:35/21:00 e 11:40/18:35/21:15.
7. **Identidade visual:** Stickman 2D puro (o auditor veta papercut) ou "Stickman papercut" (como no v3.3 e na skill local)?
8. **Auditor:** continuar com o Gemini Web via Camofox ou ir para a Gemini API? O JEV entra já na v1?
9. **Agente de analytics:** criar o @prod-analista para fechar o ciclo de retenção → Hindsight?
10. **Governança:** @prod-director como agente LLM ou como rotina determinística (com CEO pausado, como na core-eng)? Quais budgets mensais por agente?

---

## Anexos de trabalho (nesta pasta)
- `nlm-sources.json`: lista das 78 fontes do caderno (metadados).
- `nlm/*.md`: texto integral de cerca de 30 fontes-chave, extraído em modo somente leitura (material do próprio José, para consulta da core-eng).
- `ask1.json`: a resposta da única pergunta feita ao chat do caderno, com as 71 citações.

> **Alerta de segurança:** a fonte [NB: Escolha do Fluxo de Agentes] contém, em texto puro, a senha da role `paperclip_app` do Supabase do Paperclip (em comandos `PGPASSWORD=…`). Nas cópias locais desta pasta a senha foi substituída por [REDACTED]. Recomendo **rotacionar a senha** (o próprio blueprint da core-eng já pede isso) e remover ou editar essa fonte no caderno.
