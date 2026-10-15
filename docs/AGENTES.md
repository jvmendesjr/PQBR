# AGENTES da PQBR no Paperclip (canônico; origem: PROPOSTA v4.3, t384–t394)

**v4.3 (t393):** incorporado, sem mudar o texto, o observador de risco da conta já especificado (Observador de Conformidade, t192/t198, e guardião de sessão, t195). Divisão na §2.2. v4.2 guardada em `PROPOSTA-agentes-paperclip-v4.2.bak.md`.

**v4.4 (t464):** (1) **Perfis Hermes não são usados pelos agentes.** O perfil Hermes `pqbr` permanece como fallback Telegram até o gate t464; após o piloto, Discord nativo conecta diretamente ao Diretor ativo e Hermes `pqbr` é pausado. Não criar agente de canal duplicado. Modelos vêm do **9router** (roteador principal); o Hermes é só ponte para modelos que não se alcançam de outra forma. Ferramentas dos agentes = **kit PQBR** (Temporal, Camofox, NotebookLM py, Pydantic v2) + API do Paperclip. As referências Telegram nos playbooks são transitórias até a migração completa; depois do piloto, o Diretor usa Discord/Paperclip. Runtime refeito na §7. (2) **Sem teto de agentes** e sem 1/semana; contratação pelas regras do Paperclip, só por sugestão do Diretor, do dono da trilha ou do José. (3) Rotinas do Paperclip podem acordar agentes **inclusive para produção**. (4) Orçamento **warn-only**; limite de segurança revisto após os primeiros dias de relatório. (5) Novo agente **Guardião de Segurança** (§2.1) → 14 agentes. v4.1 guardada em `PROPOSTA-agentes-paperclip-v4.1.bak.md`.

**v4.1 (11/10, validação contra docs oficiais do Paperclip):** ajustes na §10 (rotinas em vez de heartbeats, `toolsets` explícitos, modelo por perfil Hermes, orçamento warn-only, limites de contratação via instruções). v4 guardada em `PROPOSTA-agentes-paperclip-v4.bak.md`.

**v4 (t390):** (1) aprovações relaxadas ao nível v3 (ADR-004, REGRAS §2/§3/§8/§18/§20); José só para regras canônicas, segredos, infra e a lista "ainda exige o José" da §3. (2) **Dev Revisor contratado já** → 13 agentes (quem corrige ≠ quem revisa). (3) `--yolo` permitido quando necessário sob as regras da §7 (ADR de exceção). Camofox 5–15 min / 3 tentativas confirmado (t357). Fonte de verdade = Postgres local (não Supabase). v3 guardada em `PROPOSTA-agentes-paperclip-v3.bak.md`.

Muda em relação à v2 (t384–t387): equipe toda **já contratada** desde a criação; especialistas acordam por gatilho ou agenda; entra o **Observador**; papéis sobrepostos foram fundidos; princípio de **PROATIVIDADE/autonomia** (semanas/meses sem humano). Só documento: nada mudou no Paperclip, no Hermes nem no servidor. v2 guardada em `PROPOSTA-agentes-paperclip-v2.bak.md`.

Fontes revisadas (servidor `pc` fora da tailnet; usadas cópias locais): espelho dos docs do repo em `/tmp/t343/docs` (09/10 17:54: REGRAS, ARQUITETURA, DECISOES-LOG, ROADMAP, SPEC, PLANO, TESTES) e `/workspace/d336/docs` (09/10 17:12, inclui CONTRATO-EDITORIAL); `prep/decisoes-jose-2026-10-07/08.md`, ENTREGA, PLANO-SDD, SOUL-pqbr-rascunho, PESQUISA-orquestracao. **Não verificado no servidor:** qualquer edição posterior a 09/10 17:54 (ex.: migração do banco do Paperclip, decisões de 10–11/10) e o `hermes-pqbr/SOUL.md` final (só o rascunho t357).

## 1. Princípio novo: PROATIVIDADE
- A PQBR funciona como empresa com o presidente ausente: opera **semanas ou meses sem intervenção humana**.
- Cada agente age antes do problema (loops de verificação), corrige sozinho pelos **playbooks de correção** pré-definidos e **pode escolher o caminho** entre os previstos no playbook.
- Piloto com **risco aceito não baixo**. A segurança vem de limites de tentativa, rollback e do Temporal como único executor de efeito externo, não de pedir OK.

## 2. Equipe final (14 agentes, todos contratados na criação)
```
José (board, ausente por padrão)
└─ Diretor (CEO)
   ├─ Líder Editorial ── Pesquisador de Origem · Roteirista · Caçador Sazonal
   ├─ Diretor de Arte 2D (PAUSADO, t400)
   ├─ Especialista SEO
   ├─ Auditor
   ├─ Líder Compliance
   ├─ Comunidade
   ├─ Observador
   ├─ Guardião de Segurança
   ├─ Dev Corretor
   └─ Dev Revisor
```
`pqbr` (perfil Hermes/Telegram temporário até t464; depois pausado; Discord nativo → Diretor)

| Agente | Responsabilidade única | Acorda por | Absorveu |
|---|---|---|---|
| Diretor (CEO) | prioriza, desbloqueia, contrata/pausa, resumo semanal; parâmetros operacionais e limpeza noturna do Drive por script (t270) | escalonamento + semanal | Programador de Publicação (propõe janelas; Temporal executa) |
| Líder Editorial | grade 80/20, anti-repetição R10 | grade 1:00 | — |
| Pesquisador de Origem | origem das expressões com ≥2 fontes | tema aprovado | Checador de Fatos (fonte) |
| Roteirista | orquestra no NotebookLM (caderno **efêmero por episódio**, nunca o mestre; roteiro como fonte antes de gerar; nunca `ask --new`) pesquisa, plano, roteiro e Short com os comandos/prompts canônicos; escreve o **bloco visual** (estilo 2D + personagem + ambiente + cenas, CONTRATO §16); respeita **limite diário** de uso (contagem própria; Pro: 500 chats/dia, 20 vídeos/dia) para poupar tokens; 15 s–3 min, alvo ~50 s (t271) | pesquisa pronta | descrição de estilo/personagem do Diretor de Arte 2D (t400) |
| Caçador Sazonal | tendências sazonais (≤20% da grade) | rotina Paperclip (cron) 30 dias antes de Carnaval, Junina, Natal etc. + issue do Líder Editorial | — |
| Diretor de Arte 2D | **PAUSADO (t400)** junto com as fichas; reativar só em arquitetura não-NotebookLM | — | — |
| Especialista SEO | título, descrição, tags, código PQBR-EP; nunca pede comentário (t263) | roteiro aprovado | — |
| Auditor | auditoria pré-publicação: código extrai quadros/transcrição; **juiz visual** = Gemini web via Camofox (3.8 Flash modo normal, nunca "Flash Estendido"; chat novo por pedido), **2 pedidos distintos**: (1) **VISUAL** — anexos = 1 quadro por cena (pranchas) + fala de cada cena; sim/não por traço visual e `imagem_corresponde_a_fala`; rodado **2×** e falha só se as duas rodadas concordam (divergência → 3ª rodada do agente); (2) **LOOP** — só texto (primeiras e últimas frases da transcrição): `ultima_continua_na_primeira` e `fala_final_cortada_no_meio` (pode migrar para o Jev). Prompts-base: `IDENT_<V>.txt` e `LOOP_todos.txt` (teste v3b); os traços do VISUAL precisam ser refeitos para o 2D sem fichas (F7-02) (RUNBOOK-auditor-v3b; decisoes-jose-2026-10-08 l.103; ENTREGA §2); Jev no texto; código decide; checagens visuais sem fichas (CONTRATO §16.6) e gate A9 (capa/frame) | pré-publicação | QA de Narração; auditoria de imagem/vídeo e capa do Diretor de Arte 2D (t400) |
| Líder Compliance | políticas YT, item 5, direitos autorais | pré-publicação + diário | Direitos Autorais |
| Comunidade | resumo e saúde dos comentários; triagem e respostas são código + Jev + banco de 60 frases (t245) | ciclo 30 min / 6 h / diário | Triagem + Redator (o "redator" é código; separação mantida porque o agente não escreve texto livre) |
| **Observador** (novo) | loop constante: conexões, auth/reauth, saldos, limites, consumo de tokens por agente/modelo/ação, tentativas e quais falham mais; reprovações do Auditor; reações/resultados dos vídeos (Analytics) para enriquecer relatórios | Temporal faz os pings a cada ~20 min (código) e abre issue no Paperclip em anomalia; agente acorda por essa issue + rotina diária e semanal | Vigia de Custo, Guardião de Sessão (observação), Checador de Reprovações, Capista-monitor, **@prod-analista** |
| Dev Corretor | corrige tickets em branch/worktree com testes; dono do **registro de aprendizado de falhas** (§5) | ticket aberto | — |
| **Guardião de Segurança** (v4.2) | segurança e guardrails (§2.1) | Temporal (varreduras de código) abre issue + rotina diária + gatilho em conteúdo externo novo | parte de segurança que estava diluída no Observador/scanner D14 |
| **Dev Revisor** (v4) | revisa todo PR do Dev Corretor (CI verde + testes + leitura do diff, **modelo do 9router de família diferente** do Corretor); aprova merge automático ou devolve; nunca escreve correção | PR aberto | revisão automática da v3 |

Removidos: `assistente` (duplica o `pqbr`), Capista, QA de Narração, Programador, Direitos Autorais, Triagem, Redator, Vigia de Custo, Guardião de Sessão, Checador, Líderes Visual/Distribuição/Comunidade/Operações (sem filhos, só inflavam). `@prod-publisher` continua **código no Temporal**, não agente.

### 2.1 Guardião de Segurança (separado do Observador)
Observador mede saúde/custo/resultado; Guardião protege. Quem vigia segurança não corrige (correção vai ao Dev Corretor) nem opera produção.
- **Varre:** segredos em repo, `company/`, tickets, logs, Hindsight (substitui/estende o scanner D14); permissões e escopo de ferramentas por agente (lista fechada do MCP `pqbr-kit` vs. o declarado no pacote); idade e rotação de chaves (Paperclip, 9router, Google, YouTube); uso anômalo (chamadas, tokens, horários, ações fora da trilha); auditoria das ações (log de atividade do Paperclip + histórico do Temporal); **prompt injection** em conteúdo externo (comentários, páginas web, transcrições) antes de chegar a outro agente: marca como dado, isola ou descarta.
- **Poderes autônomos:** pausar um agente (`pause`, reversível); bloquear uma ação/proposta (sinal ao Temporal para não executar a `PropostaAgente`); pôr conteúdo em quarentena; revogar/suspender chave comprometida e abrir ticket de rotação. Avisa Diretor e José pelo canal privado ativo (Telegram durante a migração; Discord/Paperclip após t464).
- **Não pode:** excluir nada, mudar regra canônica, criar/rotacionar segredo pago, despausar a si mesmo; não pode ser pausado por outro agente além do Diretor (e o Diretor deve justificar no relatório). Despausar agente que ele pausou: Diretor, após ticket resolvido.
- Ferramentas: só leitura do kit + API Paperclip (pause/comentário/issue) + sinal de bloqueio no Temporal. Modelo do 9router distinto dos agentes que audita.

### 2.2 Observador de risco da conta (spec existente, incorporado sem mudança)
Fontes: `prep/decisoes-jose-2026-10-08.md` §"OBSERVADOR DE CONFORMIDADE — @prod-compliance (t192 ponto 1, aprovado t198)" e §"SESSÃO DO YOUTUBE STUDIO" (t194–t196); REGRAS §11 (l.100–112, cópia /tmp/t343); ENTREGA l.45 e l.130.
- **Risco:** desmonetização por "conteúdo inautêntico" (repetitivo/templated, "mesma situação, mesmo desfecho"; IA dando conselho especializado). Rito: aviso no Studio → 7 dias para recurso → saída do YPP, reaplicação após 90 dias. Diretrizes: aviso único → strikes (3 em 90 dias = encerramento).
- **Coleta por código (Temporal), o agente só analisa:** e-mail da conta do canal (juniormoedavirtual), com os e-mails do YouTube classificados pelo Jev (info / atenção / crítico); Studio via Camofox **só leitura, ritmo humano** (Restrições/Avisos, Status e recursos, Monetização, notificações, incluindo o rótulo de IA automático); Data API (rejeitado, bloqueado, privado forçado, restrição regional).
- **Gravidade:** informativo → relatório diário; atenção (claim, anúncio limitado) → canal privado ativo (Telegram durante a migração; Discord/Paperclip após t464) + lição para roteiros; crítico (aviso/strike, inautêntico, remoção) → HOLD automático da fila + canal privado ativo + ticket + prazo de recurso monitorado. O agente prepara rascunho; José envia; nunca recorre, apaga ou altera.
- **Prevenção:** item de conformidade no Auditor; checagem de advertência ativa antes de cada horário de publicação; relatório semanal de variedade.

**Divisão sem sobreposição:**
| Parte | Dono | Por quê |
|---|---|---|
| Conteúdo e conformidade da conta (e-mails do YouTube, avisos/strikes/monetização no Studio, status da Data API, HOLD, rascunho de recurso, relatório de variedade) | **Líder Compliance** (é o @prod-compliance da spec) | a spec dá esse papel ao compliance; não muda |
| Saúde da sessão/login do Camofox (guardião de ~20 min, Studio/Gemini Web/NotebookLM, checagem ~30 min antes de publicar, escada t272, contagem de falhas de renovação) | **Observador** | é o "Guardião de Sessão" que o Observador já absorveu |
| Sinal de comprometimento da conta (login de lugar estranho, e-mail de segurança do Google, cookie/sessão adulterados, ação fora do roteiro no Studio) | **Guardião de Segurança** | segurança, não conformidade; pode bloquear a ação/pausar o agente (§2.1) |
Os e-mails do YouTube passam por uma única coleta e um único classificador (Jev). O roteamento por tipo decide o dono: política/monetização → Compliance; segurança da conta → Guardião; falha de sessão → Observador. Nenhum dos três lê o Studio por conta própria: toda leitura sai da coleta do Temporal pelo Camofox, com concorrência 1.

## 3. Regras de autonomia
**Contratação:** `requireBoardApprovalForNewAgents = desligado` após a criação (contratação via `POST /agent-hires` ativa na hora, conforme docs). **Sem teto de agentes**: tantos quantos forem precisos para eficiência, controle e distribuição. Só se contrata por **sugestão do Diretor, do dono da trilha ou do José**; quem executa a contratação é o Diretor (único com `canCreateAgents`), a partir de modelo do pacote (`company/agents/_modelos/`), com `sourceIssueId` da sugestão, aviso no Telegram e relatório. Pausar agente: Diretor (e Guardião, §2.1); `DELETE` de agente é só José.

**Playbooks de correção** (`company/playbooks/<falha>.md`): cada falha conhecida tem passos ordenados; o agente escolhe entre eles; cada execução grava resultado.

**Guardrails:**
1. Efeito externo (render, upload, agendar, privar, responder, reter, coração) **só pelo Temporal**; agentes entregam `PropostaAgente` (Pydantic v2) validada.
2. Escada de falhas do REGRAS §18 mantida (30 s → 2 min → 8 min, rede fora não gasta tentativa, cada tentativa com outra estratégia; 5 idênticas = parada). Na 2ª falha da mesma ação, entra o playbook (até 3 tentativas de correção); Camofox com 5–15 min. Esgotou → Diretor → canal privado ativo (Telegram durante a migração; Discord/Paperclip após t464).
3. Rollback: toda mudança de parâmetro é versionada e reversível; mudança de código entra com flag e volta sozinha se o smoke/ping falhar.
4. Freio automático: >3 falhas iguais em 24 h → Diretor pausa a trilha e abre ticket.
5. Sem segredos/PII em Hindsight, tickets, Supabase ou logs (scanner D14).
6. Orçamento sem teto (REGRAS §22): política por agente **warn-only** (`hardStopEnabled: false`, `warnPercent: 80`) só para gerar alerta; nada pausa por custo. **Aprovado t392**; limite de segurança será reavaliado após os primeiros dias de relatórios. Observador alerta anomalia >30% semana a semana. (Com `budgetMonthlyCents = 0` não há política nem alerta.)

**O que ainda exige o José (mínimo):**
- Excluir qualquer coisa (vídeo, comentário, arquivo do Drive, agente, org); rejeitar comentário ou banir autor.
- Voltar a público vídeo que o item 5 tornou privado; recurso ao YouTube.
- Gastar dinheiro / assinar plano / criar chave paga.
- Login manual pelo noVNC/2FA só após esgotar reautenticação autônoma (renovar → cookies do Chrome → outro caminho; log + aviso pelo canal privado ativo: Telegram durante a migração, Discord/Paperclip após t464).
- Mudança nas regras canônicas (constituição, contrato editorial, item 5).

## 4. Regras anteriores recalibradas
| Regra anterior | Fonte | Agora (v3) |
|---|---|---|
| Agentes pensantes só propõem; nenhuma mudança sem aprovação do José | REGRAS §3 (t324–t326) | **Relaxada:** aplicam sozinhos dentro de faixas pré-definidas e playbooks; José vê no relatório |
| Diretor altera parâmetros operacionais só com aprovação do José | REGRAS §2 | **Relaxada:** Diretor aplica dentro das faixas; regra canônica segue só José |
| Mesma ação falhando 2× vai ao José | REGRAS §18 | **Relaxada:** vai ao playbook; José só após esgotar playbook e Diretor |
| Divergência entre as 2 rodadas do auditor vai ao José | REGRAS §8 | **Relaxada:** 3ª rodada (chat novo) desempata; persistindo, vídeo vai para reserva, não para o José |
| Analista aplica ajuste só com OK do José | REGRAS §20 | **Relaxada** (via Observador/Diretor, faixas) |
| Atualizar dependência só com autorização | REGRAS §2, §12 | **Relaxada** (linha do monitor abaixo) |
| Contratação só com OK do José (`hire_agent`) | v2 §4 | Equipe pré-contratada; novas pelo Diretor sob sugestão (Diretor/dono da trilha/José), sem teto (t392) |
| Ticket com 2 aprovações do José (abertura e merge) | ADR-004, SOUL t357 | **Relaxada:** abertura automática; merge automático se CI + testes + **aprovação do Dev Revisor** passam e mudança não toca regra canônica/segredos/infra; José só vê no relatório. **Aprovado t390** |
| Monitor de atualizações: José autoriza no canal privado ativo (Telegram durante a migração; Discord/Paperclip após t464) |
| Heartbeats desligados (#6596) | PESQUISA §5 | **Mantida:** timer desligado em todos (padrão do Paperclip). Agentes acordam por issue/comentário ou **rotina** (cron) do Paperclip, **inclusive para trabalho de produção (t392)**; efeito externo continua só pelo Temporal; checagens de 20 min ficam no Temporal |
| Analista só observa até ~30 Shorts/90 dias | t—, ENTREGA | Mantida para *mudar parâmetro editorial*; depois disso o Diretor aplica ajustes propostos dentro de faixas pré-definidas |
| Diretor: LLM ou rotina? (pendente g.10) | PLANO | LLM, com rotinas fixas por script |
| Comunidade não torna privado (só sinaliza, t250) | PLANO | Mantida; item 5 em código executa |
| Retenção sozinha de golpe/contato/imitação/PII/ofensa (t244) | ENTREGA | Mantida; rejeitar/banir/excluir seguem só José |
| R10: tema repetido recusado mesmo se José sugerir | ENTREGA | Mantida |
| Agentes heartbeat-off, acordam só por tarefa | v2 §5 | Ver linha de heartbeats |

## 5. Onde fica o registro de aprendizado de falhas
**Dev Corretor.** Motivo: o registro só evita repetição quando vira ação — playbook novo, teste de regressão ou correção de código, que é trabalho do Dev. O Observador **detecta e conta** (fonte de dados: tentativas, falhas mais comuns), mas não muda nada; dar a ele a escrita de lições misturaria quem mede com quem corrige (separação de funções). Fluxo: Observador abre ticket com evidência → Dev corrige, grava a lição no Hindsight (banco único da org, sem PII) e atualiza o playbook + teste → Observador confirma que a falha sumiu em 7 dias e fecha.

## 6. Posse e antiinterferência (mantidos da v2)
Checkout atômico (409 → pega outra); projeto + etiqueta por trilha; MCP `pqbr-kit` com lista fechada por papel; filas Temporal (Camofox e NotebookLM concorrência 1); autor ≠ auditor; quem mede ≠ quem corrige; Comunidade não redige texto livre; tickets **pré-estruturados e agnósticos** (local, falha observada, correções sugeridas), executáveis por qualquer dev/agente.

## 7. Runtime (v4.2: 9router, sem perfis Hermes)
Princípio: agente = instruções (`instructionsBundle`) + modelo do 9router + kit PQBR via MCP `pqbr-kit`. Nada de skills/ferramentas do Hermes.
1. **Agentes só-texto** (Líder Editorial, Roteirista, SEO, Auditor, Compliance, Comunidade, Caçador): adapter **`process`** → script fixo do kit (Python): checkout → 1 chamada ao endpoint OpenAI-compatível do 9router (modelo por agente em `env`) → saída Pydantic v2 → comentário/status pela API. Só API/import (não aparece no menu). Doc: https://docs.paperclip.ing/reference/adapters/overview/
2. **Agentes com ferramenta** (Diretor, Pesquisador, Arte 2D, Observador, Guardião, Dev Corretor, Dev Revisor): adapter **`opencode_local`**, com o 9router declarado como provider OpenAI-compatível no `opencode.json` e `model: "9router/<modelo>"` por agente (Paperclip faz preflight do modelo e aceita ids fora do catálogo após refresh). Ferramentas nativas do OpenCode **negadas** por permissão (bash/edit/webfetch = deny), exceto nos Devs; só MCP `pqbr-kit` + API Paperclip. Doc: https://docs.paperclip.ing/reference/adapters/opencode/ · https://docs.paperclip.ing/guides/org/agent-adapters/
3. Alternativa avaliada: **`http`** (serviço próprio do kit que fala com o 9router) — mais controle, mas mais código; fica como plano B se o `opencode_local` não respeitar as permissões. Hermes como runtime de agente: descartado.
4. **Ponte Hermes:** só para modelos que o 9router não alcança; o 9router aponta para o Hermes como upstream (agentes não sabem disso). Não há perfis por agente.
5. **Dev Revisor ≠ Dev Corretor:** basta `model` diferente no 9router (famílias diferentes, ex.: um OpenAI, outro Anthropic/Google); não precisa de perfil.
7. **Pontos de revisão / segunda opinião → `core-revisao` (t419).** Aplicados: Dev Revisor (todo PR do Corretor); desempate da 3ª rodada do Auditor (`agente_texto` troca para `PQBR_MODELO_REVISAO` quando a issue cita `terceira_rodada`/`desempate`). Aplicados também (t421): (a) 2ª tentativa após saída inválida (Pydantic) no `agente_texto` vai ao `core-revisao`; (b) Guardião chama `segunda_opiniao` antes de pausar agente/bloquear publicação (DISCORDO → não aplica, escala ao Diretor; exceção: segredo exposto confirmado bloqueia na hora); (c) Diretor chama `segunda_opiniao` antes de aplicar correção de playbook (DISCORDO → devolve); (d) Compliance: roteiro **sensível** recebe segunda leitura automática (`PQBR_SEGUNDA_LEITURA`) anexada ao comentário; DISCORDO → não aprova. Se o `core-revisao` falhar 2×, a regra é conservadora (não aplica/escala). SEO/Comunidade: sem segunda opinião (baixo risco).

6. **Modelos (t414): só combos core do 9router.** Nenhum id direto (`ag/*`, `cu/*`) em agente.

| Combo | Agentes |
|---|---|
| `core-alto` | Diretor, Roteirista, Auditor, Dev Corretor |
| `core-revisao` | Dev Revisor; desempate da 3ª rodada do Auditor (t419) |
| `core-medio` | Pesquisador de Origem, Líder Editorial, Líder Compliance, Guardião de Segurança |
| `core-baixo` | Observador, Especialista SEO, Caçador Sazonal, Comunidade, Diretor de Arte 2D (pausado), Canal José (pqbr) |

Composição no 9router (11/10): `core-alto` = gemini-3.8-flash-high → claude-opus-4-6-thinking; `core-medio` = gemini-3.8-flash-medium → claude-sonnet-4-6 (round-robin); `core-baixo` = gemini-3-flash. Nenhum combo core passa por `cu/*`. `core-revisao` (t416/t419) = claude-sonnet-4-6 → cu/claude-sonnet-5-5-medium (round-robin). **Regra Revisor ≠ Corretor reativada (t419):** Corretor em `core-alto` (Gemini primário), Revisor em `core-revisao` (Claude). Ressalvas: `core-alto` tem Opus como fallback (mesma família Claude em ~metade das chamadas por round-robin) e `core-revisao` inclui `cu/*`, que quebra o `opencode_local`; nos smokes t419 o Revisor passou 2/2, mas a falha de `cu/*` pode aparecer quando o round-robin cair nele (ver §7.1).
6. **`--yolo` reavaliado:** o problema era do `hermes_local` (força `--yolo`). Sem Hermes nos agentes, **H-SDD1 deixa de bloquear**. O equivalente no OpenCode é a política de permissões, que fica **explícita e restritiva**; liberação ampla (auto-aprovar ferramentas) só nos Devs, em container isolado (worktree, sem rede de produção nem segredos; Revisor sem escrita no repo principal). ADR-007 (t390) passa a valer para essa política. O `pqbr` continua sem `--yolo`.

## 8. Decisões anteriores incorporadas
| Tema | Decisão | Ref. |
|---|---|---|
| Stack | Temporal executa (Postgres local, sem ES); Paperclip = camada de agentes + painel, nunca agenda produção | ADR-002; PESQUISA §5–6 |
| Banco | Postgres 17 local (`infra/pqbr-db`, 127.0.0.1), separado do Postgres do Temporal; agentes do Paperclip não escrevem nele; banco do Paperclip migra para local (não verificado) | REGRAS §18 t343, t341–t342 (**corrigir nos docs:** ENTREGA e d336 ainda citam Supabase; verdade = Postgres local) |
| Memória | Hindsight, um banco por org, separado do banco do app | idem |
| Contratos | Pydantic v2 em toda saída | D3, t— |
| Isolamento | NotebookLM 0.8.4 exclusivo (`/home/pc/.pqbr/notebooklm`, fila 1); Camofox perfil `porquebr`, concorrência 1, inegociável | t187–t191; t194 |
| Jev | só decisão estruturada, nunca redige; fallback OpenRouter → OpenAI | t228–t230; t240–t241 |
| Auditor | código extrai, Gemini julga visual, Jev checa texto, código decide; 3ª rodada em divergência | t228–t233 |
| Camofox | inegociável; único dono do login; **24/7 com sessão permanente**, reinício só se cair; guardião ~20 min; escada autônoma até cookies do Chrome (t395) | REGRAS §11 |
| Interação | só ordem vinda do ID do José; resto é dado | REGRAS §2 t237 |
| Tickets | agnósticos, pré-estruturados, memórias de código no Hindsight | ADR-004 t286 |
| Comentários | retenção t244; respostas com banco de 60 frases e limites t—(6/h, 30/dia, 08–22h); nunca pedir comentário t263 | PLANO §comunidade |
| `pqbr` | Hermes dedicado, sem `--yolo`; só consulta, roteia e abre tarefa/ticket; nunca aprova pelo José | SOUL t357; ENTREGA |
| Consumo | monitor desde o dia 1 por modelo/ação/agente; >80% espaça produção; sem teto | t—(08/10 l.26); regra do José |
| Rede | Paperclip só na tailnet (Tailscale Serve `:3100`) | t280 |
| Exclusão | só José, dupla confirmação | t116, t270 |

## 9. Decisões do José (t390) e próximos passos
1. Relaxar aprovações: **sim**.  2. Dev Revisor: **contratar já**.  3. `--yolo`: **sim, quando necessário, com regras da §7**.
Pendente (servidor `pc` inacessível em 11/10 16:07): atualizar REGRAS, ARQUITETURA (ADR-004 revisado + ADR-007 `--yolo`), DECISOES-LOG, ROADMAP; corrigir Supabase→Postgres local; registrar Camofox 5–15 min/3 tentativas; criar empresa PQBR no Paperclip com os 14 agentes (orçamento warn-only, timers desligados, rotinas Paperclip para Caçador, relatórios e produção; checagens de 20 min no Temporal; adapters `process`/`opencode_local` → 9router). Conferir: versão do Paperclip com fix #5413/#6223, OpenCode instalado no `pc`, URL/chave do 9router como `secret_ref`.

t392: rotinas acordam produção **sim**; orçamento warn-only **sim**; sem teto de agentes; Guardião criado.

## 10. Alinhamento com o Paperclip (docs oficiais, 11/10)
| Ponto | Como fica | Doc |
|---|---|---|
| Organograma | `reportsTo` do mesmo company, sem ciclo; Diretor `role: ceo`, `reportsTo: null` | https://docs.paperclip.ing/reference/api/agents/ |
| Equipe inicial | criada pelo board (`POST /agents`, board-only) ou import do pacote; contratações seguintes pelo Diretor via `POST /agent-hires` + skill `paperclip-create-agent`, com `sourceIssueId` | https://docs.paperclip.ing/how-to/handle-board-approvals-for-hires/ |
| Aprovação de contratação | desligada → contratação ativa na hora; José vê pelo canal privado ativo (Telegram durante a migração; Discord/Paperclip após t464)/atividade | idem; https://docs.paperclip.ing/guides/day-to-day/approvals/ |
| Instruções | `instructionsBundle` (AGENTS.md/SOUL.md), não `promptTemplate` | https://docs.paperclip.ing/reference/api/agents/ |
| Skills | instaladas no nível da empresa; `desiredSkills` na criação; sem Hermes nos agentes (v4.2) | https://docs.paperclip.ing/reference/api/agents/ |
| Agendamento | timer desligado; rotinas Paperclip acordam agentes, inclusive produção (t392); efeito externo e calendário de execução seguem no Temporal (ADR-002) | https://docs.paperclip.ing/guides/projects-workflow/routines/ |
| Posse de tarefa | checkout atômico, 409 para dono vivo; lock preso a run morto já corrigido (#5413/#6223), exigir versão com o fix | https://github.com/paperclipai/paperclip/issues/6007 |
| Chaves/segredos | chave de API por agente; segredos só por `secret_ref` no `env` (respostas mascaram); nunca no AGENTS.md | https://docs.paperclip.ing/reference/api/agents/ |
| Rollback | `config-revisions/{id}/rollback` para config de agente; arquivos do bundle não têm histórico → versionar `company/` no git | idem |
| Orçamento | warn-only (ver §3.6) | https://docs.paperclip.ing/how-to/set-monthly-budget/ |
| Adapters | `process` (texto) e `opencode_local` (ferramenta) → 9router | https://docs.paperclip.ing/reference/adapters/overview/ |

## 11. Mapa @prod-* (papéis antigos) → 14 agentes (t395)
| Papel antigo | Agora | Natureza |
|---|---|---|
| @prod-director | **Diretor** | agente (`opencode_local`) |
| @prod-ideador | **Líder Editorial** + **Caçador Sazonal** | agentes (`process`); coleta e NotebookLM são Activities |
| @prod-roteirista | **Roteirista** (+ **Pesquisador de Origem** antes) | agente `process` orquestra o NotebookLM |
| @prod-render | — | Activity do Temporal (sem LLM) |
| @prod-auditor | **Auditor** | código decide; agente `process` desempata (3ª rodada) |
| @prod-seo | **Especialista SEO** | agente `process` |
| (arte/fichas) | **Diretor de Arte 2D — PAUSADO (t400)**; descrição visual → Roteirista; auditoria e capa → Auditor | agente `opencode_local` pausado |
| @prod-publisher | — | Activity do Temporal (único executor de efeito externo) |
| @prod-analista | **Observador** (resultados/Analytics) | agente; coleta por código |
| @prod-compliance | **Líder Compliance** (inclui o observador de risco da conta, §2.2) | agente `process`; coleta por código |
| @prod-comunidade | **Comunidade** | agente `process`; triagem e respostas por código + Jev |
| guardião de sessão (t195) | **Observador** (análise) + watchdog em código | — |
| scanner D14 / segurança | **Guardião de Segurança** | agente `opencode_local` |
| agentes de dev | **Dev Corretor** + **Dev Revisor** | `opencode_local` em container |
| Canal do José | Hermes `pqbr` apenas como fallback de transição; após o piloto, Discord nativo do Paperclip diretamente ao Diretor |

## Hindsight — manutenção e qualidade (HS-01, decidido pelo José em 12/10)
- **Dev Corretor** é o dono da manutenção do bank `pqbr`: reindexação/consolidação diária, deduplicação, poda de memórias obsoletas, sem segredos/PII (achou, remove e abre ticket para o Guardião); nada de apagar em massa sem o backup do dia.
- **Observador** mede a qualidade nos relatórios: taxa de acerto (hit rate), defasagem (staleness), duplicatas, tamanho/crescimento; se a manutenção não rodou, abre ticket para o Dev Corretor. Quem mede não corrige.
