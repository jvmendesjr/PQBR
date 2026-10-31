> ⛔ **PESQUISA / REFERÊNCIA DE PRÉ-CONSTRUÇÃO: AGENTES NÃO CONSULTAM SEM APROVAÇÃO EXPLÍCITA DO JOSÉ (t287).** Pode conter premissas superadas que, mal interpretadas, iriam parar em produção. As regras válidas estão em `docs/REGRAS.md`.

> Nota: a parte sobre templates do Paperclip perde peso com a t282 (Paperclip só como painel).

# Pesquisa: agente de comunidade (@prod-comunidade) — templates Paperclip, skills e boas práticas

> Data: 08/10/2026, ~23:10 PT (Fortaleza). Pesquisa somente leitura (GitHub API/raw, API de busca do skills.sh). Nenhum host remoto tocado, nenhum segredo lido.
> **VERIFICADO** = visto no arquivo real (caminho citado). **HIPÓTESE** = inferência minha ou fonte não conferida.
> Complementa `PESQUISA-comentarios-boas-praticas.md` (regras da API, moderação, respostas automáticas §8), que **não** é repetido aqui.

## 0. Resposta curta
- **Não existe, em nenhum template Paperclip, um agente de comentários/moderação de YouTube.** (VERIFICADO: varredura de todos os caminhos de `paperclipai/companies` e de `packages/teams-catalog` do `paperclipai/paperclip`.)
- O mais próximo **no formato Paperclip, com conteúdo próprio (não stub)** é `donchitos-game-studio/agents/community-manager` (Donchitos Game Studio). (VERIFICADO)
- Na Agency Agents (base escolhida), os candidatos são `support-support-responder`, `marketing-social-media-strategist`, `product-feedback-synthesizer` e os de plataforma (`marketing-reddit-community-builder`, `marketing-twitter-engager`). Nenhum cobre YouTube nem moderação de comentário com classificador. (VERIFICADO)
- No upstream `msitarzewski/agency-agents` existem 3 papéis **mais novos que o snapshot do Paperclip** e mais aderentes: `specialized/customer-service.md`, `marketing/marketing-developer-community-builder.md`, `specialized/customer-success-manager.md`. (VERIFICADO: estão no upstream e **não** em `paperclipai/companies/agency-agents/agents/`.)
- **Recomendação:** persona própria em pt-BR no formato do `community-manager` da Donchitos (O que faz / De onde vem o trabalho / Com quem coordena / O que produz / O que NÃO faz), com regras de escalonamento e tom do upstream `customer-service.md`, regras de moderação do `marketing-developer-community-builder.md` e o método de temas do `product-feedback-synthesizer`. Não importar nenhum como está.

## 1. Templates

### 1.1 Contexto do catálogo (VERIFICADO)
- `paperclipai/companies`: último commit `514503bf4f` em 23/03/2026 17:44 PT. Pastas de empresa: aeon-intelligence, agency-agents, agentsys-engineering, clawteam-capital, clawteam-engineering, clawteam-research-lab, default, donchitos-game-studio, fullstack-forge, gstack, kdense-science-lab, minimax-studio, product-compass-consulting, redoak-review, superpowers, taches-creative, trail-of-bits-security.
- `agency-agents`: 167 `AGENTS.md`, 10 times (design, engineering, game-development, marketing, operations, product, quality-assurance, sales, spatial-computing, specialized-ops). Cada AGENTS.md é stub que aponta para o upstream fixado no commit `6254154899` (15/03/2026 18:37 PT).
- Upstream `msitarzewski/agency-agents`: 158.347★, MIT, último push 07/10/2026 13:45 PT.
- Varredura por `support|community|social|feedback|moderat|customer|comment|engag|reply|respond` em **todas** as empresas fora da agency-agents: só `donchitos-game-studio/agents/community-manager/AGENTS.md`. (As outras ocorrências são skills de outro assunto: `clinical-decision-support`, `customer-journey-map`, `ideal-customer-profile`.)
- Paperclip **teams-catalog** (`paperclipai/paperclip`, master `9b624a110e`, 08/10/2026 19:58 PT): times `core-exec-team` (ceo, cto, qa), `product-design` (ux-designer), `product-engineering` (cto, qa, senior-coder), opcional `content-machine` (content-lead + skill `content-calendar`). **Nenhum agente de comunidade/suporte.**

### 1.2 Candidatos (agency-agents no Paperclip → upstream)
Caminho Paperclip: `paperclipai/companies/agency-agents/agents/<slug>/AGENTS.md`. Upstream: `https://github.com/msitarzewski/agency-agents/blob/main/<arquivo>`.

| Slug (Paperclip) | Upstream | Resumo (do arquivo real) | Encaixe PQBR |
|---|---|---|---|
| `support-support-responder` (reportsTo `vp-operations`) | `support/support-support-responder.md` (601 linhas) | Especialista de suporte multicanal (e-mail, chat, telefone, social, in-app), "empático, focado em solução". Traz YAML de canais com SLA (social: resposta em 1 h, `escalation_to_private: true`), tiers e critérios de escalonamento, template de interação. | **Médio.** A estrutura de triagem, SLA e escalonamento é útil; o resto é SaaS/call center (telefone, tiers, FCR 85%). Muito longo e genérico. |
| `marketing-social-media-strategist` (reportsTo `cmo`) | `marketing/marketing-social-media-strategist.md` (125) | Estrategista cross-platform focado em **LinkedIn/Twitter e B2B**: campanhas, thought leadership, employee advocacy. Cita "community management and professional group moderation" e escala para Legal Compliance Checker e Brand Guardian. | **Baixo.** É estratégia de publicação B2B, não atendimento de comentário. Só o bloco "Workflow Integration" (handoff/escalates to) serve de modelo. |
| `product-feedback-synthesizer` | `product/product-feedback-synthesizer.md` (118) | Coleta e sintetiza feedback multicanal; análise de sentimento, categorização por tema, priorização (RICE, MoSCoW, Kano), "Voice of Customer" com citação literal. | **Médio, só para a parte "sugestão de tema → grade".** Não modera nem responde. |
| `marketing-reddit-community-builder` | `marketing/marketing-reddit-community-builder.md` (122) | Reddit "relationship-first", regra 90/10 valor/promoção, monitorar menções e responder com autenticidade. | **Baixo.** Específico de Reddit; a ideia "sem promoção na resposta" serve. |
| `marketing-twitter-engager` | `marketing/marketing-twitter-engager.md` (125) | Engajamento em tempo real no X; resposta a menções < 2 h em horário comercial, crise < 30 min. | **Baixo.** Só referência de SLA. |
| `marketing-tiktok-strategist` | `marketing/marketing-tiktok-strategist.md` (124) | Viralização no TikTok, adaptação para Reels/Shorts, "community building". | **Baixo** para comentários (é de conteúdo). |
| `support-analytics-reporter` | `support/support-analytics-reporter.md` (377) | Analista de dados: dashboards, KPIs, relatórios. | Já previsto para o analista; não para comunidade. |
| `design-brand-guardian` | (não lido) | Guardião da marca (pelo nome). | HIPÓTESE: útil só como fonte do guia de tom. |

### 1.3 Só no upstream (não estão no snapshot do Paperclip)
| Arquivo upstream | Resumo (do arquivo real) | Encaixe PQBR |
|---|---|---|
| `specialized/customer-service.md` (398) | Atendente de qualquer setor: "empatia antes de tudo", "nunca prometa o que não pode cumprir", "escale antes da frustração chegar ao pico". **Gatilhos de escalonamento** IMEDIATO (segurança, ameaça jurídica, ameaça de exposição por conta grande, fora da autoridade) e URGENTE (repetiu o problema, muito irritado); técnicas de desescalada; estilo: linguagem simples, frases curtas sob pressão. | **Alto para regras de tom e escalonamento.** Mas presume conversa 1:1 e texto livre; na PQBR o texto vem de template e o Jev não escreve. |
| `marketing/marketing-developer-community-builder.md` (285) | Gestor de comunidade "caloroso sem ser artificialmente animado". Regras: "Moderate consistently", "Don't fake grassroots", "Measure health, not just size", "Never weaponize the community". Política com SLA (#help 24 h), spam: aviso e remoção sem exposição pública; playbook de crise escrito **antes**. | **Alto para regras de moderação e saúde.** Público é dev/Discord, adaptar. |
| `specialized/customer-success-manager.md` (460) | CSM de SaaS: onboarding, health score, renovação, churn. | **Nulo** para a PQBR. |
| `marketing/marketing-x-twitter-intelligence-analyst.md` | Inteligência no X, depende do serviço Xquik. | Nulo. |

### 1.4 Fora da agency-agents: `donchitos-game-studio/agents/community-manager` (VERIFICADO)
- Caminho: `paperclipai/companies/donchitos-game-studio/agents/community-manager/AGENTS.md`; `reportsTo: producer`; texto **completo no próprio arquivo** (não é stub); empresa MIT, autor "Donchitos".
- Persona: dono da comunicação com jogadores; monitora canais (sentimento, bugs, pedidos), sintetiza feedback em relatório categorizado (sentimento, frequência, gravidade), modera, cuida de crise.
- Regras que servem direto: toda comunicação pública aprovada pelo produtor; nunca prometer recurso/data; reconhecer problema rápido; **não discutir com membro, desescalar ou sair**; "não ignore feedback negativo, é dado"; não tomar decisão de produto, só repassar.
- Encaixe: **o melhor esqueleto** (seções e limites) para o `AGENTS.md` do @prod-comunidade. Tirar patch notes, blog, eventos.

## 2. Skills

### 2.1 Top 3 recomendadas (installs = skills.sh em 08/10/2026; ★ = GitHub)
| # | Skill | Repo | Sinal | O que reaproveitar |
|---|---|---|---|---|
| 1 | `support-ticket-triage` | `composio-community/awesome-codex-skills` (`support-ticket-triage/SKILL.md`) | 543 installs; repo 16.812★ | Saída fixa por item (categoria, prioridade com justificativa, próxima ação); "sinal fraco → 2–3 categorias prováveis e o que desempata"; mascarar PII; nunca prometer prazo. Encaixa no JSON do Jev. Curta (26 linhas). |
| 2 | `developer-community-moderation` | `samber/developer-relations-skills` (`skills/developer-community-moderation/SKILL.md`, MIT) | 3.256 installs; repo **2★** (desproporção: tratar installs com cautela) | Escada de aplicação de regra, runbook de incidente separado da política, "regra que não pode ser aplicada é pior que nenhuma", controles da plataforma primeiro (filtros, limites) antes de trabalho manual. Base para a política de retenção. |
| 3 | `youtube-comments-to-ideas` | `ravsau/youtuber-skills` (`skills/youtube-comments-to-ideas/SKILL.md`, MIT) | 14 installs; 5★ (adoção baixa) | Exatamente o fluxo "sugestão de tema → grade": descartar elogio/spam/respostas entre espectadores, agrupar por pergunta, **contar**, citar o comentário literal, "1 comentário é 1, não arredondar", ideia sem comentário-prova é palpite. |

### 2.2 Complementares
| Skill | Repo | Sinal | Uso |
|---|---|---|---|
| `mine-youtube-comments` | `manifoldmcp/marketing-skills` | 3 installs | Regras de julgamento boas: likes pesam como concordância; ler respostas antes de dizer que pergunta está sem resposta; **nunca nomear o comentarista em texto público**; "never reply, post or contact". Depende do MCP Manifold (não usar o conector; só as regras). |
| `community-marketing` | `coreyhaines31/marketingskills` (MIT) | 82.024 installs; 53.778★ | Métricas de saúde (taxa de resposta, concentração em poucos membros), "fechar o ciclo": quando um comentário vira vídeo, creditar publicamente. Foco Discord/Slack. |
| `social` | `coreyhaines31/marketingskills` | 73.839 installs | Seção "Engagement Strategy": responder a todos os comentários; comentário de qualidade ≠ "ótimo post!". Mais publicação que atendimento. |
| `brand-voice-enforcement` | `anthropics/knowledge-work-plugins` (`partner-built/brand-voice/...`) | 3.508 installs | Padrão de guia de voz em arquivo + nível de rigor (strict/balanced/flexible). Útil para validar o **banco de templates** antes da aprovação do José. |
| `sentiment-analysis` | `phuryn/pm-skills` | 2.902 installs; 26.840★ | Referência de categorias de sentimento (não lida a fundo; HIPÓTESE de utilidade). |
| `developer-community-health` | `samber/developer-relations-skills` | 3.196 installs | Métricas de saúde de comunidade (não lida a fundo). |

### 2.3 Descartadas / alertas
- Skills de "auto-reply" em plataformas chinesas e LinkedIn (`xiaohongshu-comment-reply` 26, `douyin-comment-auto-reply` 6, `linkedin-comment-reply-manager` 8): adoção mínima, outra plataforma.
- `community-manager` de `eddiebe147/claude-settings` (45) e `alterlab-nmc-community-manager` (44): adoção baixa, não lidas.
- Família `*/superpowers/twitter-automation` com centenas de milhares de installs em forks quase iguais: padrão de contagem inflada já apontado no dossiê. **Não usar.**
- Scrapers de comentário (`apidojo-io/*scraping-youtube-comments*`, `browser-act/youtube-comments-api-skill`): leitura por raspagem contraria a decisão (API oficial apenas).
- **Hermes:** no `NousResearch/hermes-agent` só há `skills/media/youtube-content` (transcrição → resumo), `social-media/xurl`, `optional-skills/social-media/reddit-reading` e `creative/social-media-content-calendar`. Nenhuma de comentários. (VERIFICADO)
- **Hermes `rede` local:** o inventário do dossiê (§e) não lista skill de comentários; o único ponto é "o plugin do Paperclip grava o corpo inteiro dos comentários (autoRetain)", que é sobre issues do Paperclip, não YouTube. Não reli o host `pc` (regra de não tocar host remoto). (VERIFICADO no dossiê; HIPÓTESE de que nada mudou no host.)

## 3. Boas práticas para o papel (síntese aplicada à PQBR)
Fontes: arquivos acima (VERIFICADO) + `PESQUISA-comentarios-boas-praticas.md`. Adaptação é minha (HIPÓTESE até validar em dev).

**Escopo (faz)**
- Ler comentários via API (ritmo t243), mandar ao Jev, gravar no Supabase com o código do vídeo.
- Reter sozinho golpe, contato externo, imitação do canal, dado pessoal, ofensa a terceiro (aprovado pelo José; `heldForReview`, reversível).
- Responder não críticos com frase do banco aprovado, escolhida por código (regras §8.4 da pesquisa anterior).
- Agrupar sugestões e perguntas por autores distintos e entregar à grade com citação literal e contagem (padrão `youtube-comments-to-ideas`).
- Resumo diário e relatório de saúde (volume, % respondido, retidos, críticos, temas).

**Fora do escopo (não faz)** — padrão Donchitos/customer-service
- Não escreve texto livre, não promete tema/data, não discute com espectador, não responde pergunta factual, crítica nem tema sensível.
- Não torna vídeo privado por conta própria: sinaliza; a ação é da regra do item 5 (executor único definido no blueprint).
- Não rejeita/exclui comentário (só o José), não bane autor, não comenta fora do próprio canal, não lê pelo Camofox.
- Não decide conteúdo nem métrica: repassa ao ideador/analista.

**Handoffs**
- Entrada: leitor da API (próprio agente) e eventos de publicação (código do vídeo, estado).
- Saída: `@prod-ideador`/grade (temas com contagem), analista (agregados), executor do item 5 (sinal de problema no vídeo), José via Telegram (críticos e resumo).
- Formato: JSON validado (Pydantic) e template de relatório; sem prosa do modelo.

**Escalonamento para o José** (adaptado de `customer-service.md` + regras já aprovadas)
- IMEDIATO: sinal de problema no vídeo (erro factual, direitos, marca/pessoa), ameaça jurídica, conta grande/imprensa, possível criança, pico de comentários (> 3× média), resposta automática sumida.
- NO RESUMO: pergunta, crítica, reclamação, ironia possível, divergência entre as 2 rodadas do Jev, sugestão repetida.
- Regra "escale antes da frustração chegar ao pico": autor que volta com a mesma queixa vai direto ao José.

**Guia de tom (para o banco de templates)**
- Caloroso sem ser forçado; frases curtas; sem nome do autor, sem citar o comentário, sem link, sem "inscreva-se", sem promessa; 0 ou 1 emoji.
- Arquivo `guia-tom-comunidade.md` versionado; validação do banco no estilo `brand-voice-enforcement` (rigor "strict").

**SLAs (referências e proposta)**
- Referências vistas: social 1 h (support-responder), menção < 2 h e crise < 30 min (twitter-engager), #help 24 h (developer-community-builder). São de marca/SaaS, não de Shorts.
- Proposta PQBR: leitura a cada 30 min nas primeiras 48 h; resposta automática com atraso aleatório 15–120 min, só 08:00–22:00 PT; crítico ao José em ≤ 30 min após a leitura; resumo diário fixo.

**Saúde e consistência** (developer-community-builder / samber)
- Moderar sempre igual: a mesma classe gera a mesma ação; registrar cada decisão (precedente).
- Medir saúde, não só volume; "fechar o ciclo": quando um tema sugerido vira vídeo, o José pode fixar um comentário de crédito (sem nome, se preferir).
- Playbook de crise escrito antes de ligar (brigada, golpe em massa, vídeo polêmico) + kill switch `/pausar_respostas`.

## 4. Persona recomendada para @prod-comunidade
1. **Esqueleto:** `paperclipai/companies/donchitos-game-studio/agents/community-manager/AGENTS.md` (formato Paperclip nativo, seções e "Must NOT do").
2. **Escalonamento e tom:** upstream `msitarzewski/agency-agents/specialized/customer-service.md` (MIT; parafrasear, não copiar).
3. **Moderação e saúde:** upstream `marketing/marketing-developer-community-builder.md`.
4. **Temas para a grade:** `product/product-feedback-synthesizer.md` + skill `youtube-comments-to-ideas`.
5. **Skills internas a escrever:** `pqbr-comentarios-triagem` (de `support-ticket-triage` + esquema do Jev), `pqbr-comentarios-moderacao` (de `developer-community-moderation` + regras da API), `pqbr-comentarios-temas` (de `youtube-comments-to-ideas`), `pqbr-guia-tom` (banco de templates).
- Se a core-eng quiser importar algo para comparar: `support-support-responder` é o único da agency-agents com escalonamento estruturado, mas é stub em inglês e genérico. HIPÓTESE: escrever a persona do zero sai mais barato que adaptar.
