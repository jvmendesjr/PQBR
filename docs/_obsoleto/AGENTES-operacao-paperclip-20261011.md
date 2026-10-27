# AGENTES — corpo antigo, para análise (t129u)

Movido de `docs/AGENTES.md`. Mistura a equipe vigente com contratação, issues e rotinas do Paperclip. A versão curta vigente voltou para `docs/AGENTES.md`. Não usar este arquivo como instrução.

# AGENTES da PQBR (canônico; agentes PydanticAI no Temporal, ADR-011; origem: PROPOSTA v4.3, t384–t394)

**v4.3 (t393):** incorporado, sem mudar o texto, o observador de risco da conta já especificado (Observador de Conformidade, t192/t198, e guardião de sessão, t195). Divisão na §2.2. v4.2 guardada em `PROPOSTA-agentes-paperclip-v4.2.bak.md`.

> **Atualização 23/10/2026 (t474, ADR-011):** o Paperclip está sendo retirado. Os agentes deste roster passam a ser **PydanticAI (Pydantic v2) dentro de activities do Temporal**; as personas em `company/agents/*/AGENTS.md` e os playbooks continuam valendo. Canal do José: Telegram (Hermes `pqbr`) + sinais do Temporal; painel: Temporal UI. Trechos sobre org/issues/rotinas/contratação do Paperclip abaixo são históricos até a reescrita.

**v4.4 (t464, canal REVOGADO por t474):** (1) **Perfis Hermes não são usados pelos agentes.** ~~Discord nativo~~ (revogado: o canal é o Telegram/Hermes `pqbr`). Modelos vêm do **9router** (roteador principal); o Hermes é só ponte para modelos que não se alcançam de outra forma. Ferramentas dos agentes = **kit PQBR** (Temporal, Camofox, NotebookLM py, Pydantic v2) + ~~API do Paperclip~~. (2) **Sem teto de agentes** e sem 1/semana. (3) Rotinas acordam agentes inclusive para produção (agora via Schedules do Temporal). (4) Orçamento **warn-only**. (5) Novo agente **Guardião de Segurança** (§2.1) → 14 agentes.
**v4.5 (t465):** NotebookLM é o motor intelectual canônico; agentes orquestram, sem pesquisa/criação editorial independente, salvo complemento de relatório ou indisponibilidade documentada. Flow primário; Vids fallback; Gemini Web terceiro; Vibes posterior. Instruções técnicas em inglês e conteúdo final em pt-BR.

**v4.1 (11/10, validação contra docs oficiais do Paperclip):** ajustes na §10 (rotinas em vez de heartbeats, `toolsets` explícitos, modelo por perfil Hermes, orçamento warn-only, limites de contratação via instruções). v4 guardada em `PROPOSTA-agentes-paperclip-v4.bak.md`.

**v4 (t390):** (1) aprovações relaxadas ao nível v3 (ADR-004, REGRAS §2/§3/§8/§18/§20); José só para regras canônicas, segredos, infra e a lista "ainda exige o José" da §3. (2) **Dev Revisor contratado já** → 13 agentes (quem corrige ≠ quem revisa). (3) `--yolo` permitido quando necessário sob as regras da §7 (ADR de exceção). Camofox 5–15 min / 3 tentativas confirmado (t357). Fonte de verdade = Postgres local (não Supabase). v3 guardada em `PROPOSTA-agentes-paperclip-v3.bak.md`.

Muda em relação à v2 (t384–t387): equipe toda **já contratada** desde a criação; especialistas acordam por gatilho ou agenda; entra o **Observador**; papéis sobrepostos foram fundidos; princípio de **PROATIVIDADE/autonomia** (semanas/meses sem humano). Só documento: nada mudou no Paperclip, no Hermes nem no servidor. v2 guardada em `PROPOSTA-agentes-paperclip-v2.bak.md`.

Fontes revisadas (servidor `pc` fora da tailnet; usadas cópias locais): espelho dos docs do repo em `/tmp/t343/docs` (09/10 17:54: REGRAS, ARQUITETURA, DECISOES-LOG, ROADMAP, SPEC, PLANO, TESTES) e `/workspace/d336/docs` (09/10 17:12, inclui CONTRATO-EDITORIAL); `prep/decisoes-jose-2026-10-07/08.md`, ENTREGA, PLANO-SDD, SOUL-pqbr-rascunho, PESQUISA-orquestracao. **Não verificado no servidor:** qualquer edição posterior a 09/10 17:54 (ex.: migração do banco do Paperclip, decisões de 10–11/10) e o `hermes-pqbr/SOUL.md` final (só o rascunho t357).

## 1. Princípio novo: PROATIVIDADE
- A PQBR funciona como empresa com o presidente ausente: opera **semanas ou meses sem intervenção humana**.
- Cada agente age antes do problema (loops de verificação), corrige sozinho pelos **playbooks de correção** pré-definidos e **pode escolher o caminho** entre os previstos no playbook.
- Piloto com **risco aceito não baixo**. A segurança vem de limites de tentativa, rollback e do Temporal como único executor de efeito externo, não de pedir OK.

## 2. Equipe (t512, 24/10/2026: 8 papéis-agente)
> **Vigente:** Diretor · Líder Editorial (monta pedidos ao MotorIntelectual e valida respostas) · Pesquisador de Origem · Auditor · Compliance (`lider-compliance`) · Guardião de Segurança · Observador · **Dev** (fusão Corretor+Revisor; só indica problemas e propõe, nunca aplica). Roteirista, SEO e Caçador Sazonal = **etapas de workflow** que chamam o MotorIntelectual (NotebookLM hoje); Comunidade adiada; Diretor de Arte 2D aposentado (vídeo = GeradorVideo). Personas aposentadas: `docs/_obsoleto/company/agents/`. Habilidades por papel: proposta em `docs/sdd/PROPOSTA-papeis-skills.md`. A equipe anterior de 14 agentes está em `docs/_obsoleto/agentes-equipe-14-t395.md`.

### 2.1 Guardião de Segurança (separado do Observador)
Observador mede saúde/custo/resultado; Guardião protege. Quem vigia segurança não corrige (correção vai ao Dev Corretor) nem opera produção.
- **Varre:** segredos em repo, `company/`, tickets, logs, Hindsight (substitui/estende o scanner D14); permissões e escopo de ferramentas por agente (lista fechada do MCP `pqbr-kit` vs. o declarado no pacote); idade e rotação de chaves (Paperclip, 9router, Google, YouTube); uso anômalo (chamadas, tokens, horários, ações fora da trilha); auditoria das ações (log de atividade do Paperclip + histórico do Temporal); **prompt injection** em conteúdo externo (comentários, páginas web, transcrições) antes de chegar a outro agente: marca como dado, isola ou descarta.
- **Poderes autônomos:** pausar um agente (`pause`, reversível); bloquear uma ação/proposta (sinal ao Temporal para não executar a `PropostaAgente`); pôr conteúdo em quarentena; revogar/suspender chave comprometida e abrir ticket de rotação. Avisa Diretor e José pelo canal privado ativo (Telegram/Hermes `pqbr`; t474).
- **Não pode:** excluir nada, mudar regra canônica, criar/rotacionar segredo pago, despausar a si mesmo; não pode ser pausado por outro agente além do Diretor (e o Diretor deve justificar no relatório). Despausar agente que ele pausou: Diretor, após ticket resolvido.
- Ferramentas: só leitura do kit + API Paperclip (pause/comentário/issue) + sinal de bloqueio no Temporal. Modelo do 9router distinto dos agentes que audita.

### 2.2 Observador de risco da conta (spec existente, incorporado sem mudança)
Fontes: `prep/decisoes-jose-2026-10-08.md` §"OBSERVADOR DE CONFORMIDADE — @prod-compliance (t192 ponto 1, aprovado t198)" e §"SESSÃO DO YOUTUBE STUDIO" (t194–t196); REGRAS §11 (l.100–112, cópia /tmp/t343); ENTREGA l.45 e l.130.
- **Risco:** desmonetização por "conteúdo inautêntico" (repetitivo/templated, "mesma situação, mesmo desfecho"; IA dando conselho especializado). Rito: aviso no Studio → 7 dias para recurso → saída do YPP, reaplicação após 90 dias. Diretrizes: aviso único → strikes (3 em 90 dias = encerramento).
- **Coleta por código (Temporal), o agente só analisa:** e-mail da conta do canal (juniormoedavirtual), com os e-mails do YouTube classificados pelo Jev (info / atenção / crítico); Studio via Camofox **só leitura, ritmo humano** (Restrições/Avisos, Status e recursos, Monetização, notificações, incluindo o rótulo de IA automático); Data API (rejeitado, bloqueado, privado forçado, restrição regional).
- **Gravidade:** informativo → relatório diário; atenção (claim, anúncio limitado) → canal privado ativo (Telegram/Hermes `pqbr`; t474) + lição para roteiros; crítico (aviso/strike, inautêntico, remoção) → HOLD automático da fila + canal privado ativo + ticket + prazo de recurso monitorado. O agente prepara rascunho; José envia; nunca recorre, apaga ou altera.
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
2. Escada de falhas do REGRAS §18 mantida (30 s → 2 min → 8 min, rede fora não gasta tentativa, cada tentativa com outra estratégia; 5 idênticas = parada). Na 2ª falha da mesma ação, entra o playbook (até 3 tentativas de correção); Camofox com 5–15 min. Esgotou → Diretor → canal privado ativo (Telegram/Hermes `pqbr`; t474).
3. Rollback: toda mudança de parâmetro é versionada e reversível; mudança de código entra com flag e volta sozinha se o smoke/ping falhar.
4. Freio automático: >3 falhas iguais em 24 h → Diretor pausa a trilha e abre ticket.
5. Sem segredos/PII em Hindsight, tickets, Supabase ou logs (scanner D14).
6. Orçamento sem teto (REGRAS §22): política por agente **warn-only** (`hardStopEnabled: false`, `warnPercent: 80`) só para gerar alerta; nada pausa por custo. **Aprovado t392**; limite de segurança será reavaliado após os primeiros dias de relatórios. Observador alerta anomalia >30% semana a semana. (Com `budgetMonthlyCents = 0` não há política nem alerta.)

**O que ainda exige o José (mínimo):**
- Excluir qualquer coisa (vídeo, comentário, arquivo do Drive, agente, org); rejeitar comentário ou banir autor.
- Voltar a público vídeo que o item 5 tornou privado; recurso ao YouTube.
- Gastar dinheiro / assinar plano / criar chave paga.
- Login manual pelo noVNC/2FA só após esgotar reautenticação autônoma (renovar → cookies do Chrome → outro caminho; log + aviso pelo canal privado ativo: Telegram/Hermes `pqbr`).
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
| Monitor de atualizações: José autoriza no canal privado ativo (Telegram/Hermes `pqbr`; t474) |
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
Agente externo de manutenção: só pelo `pqbr-mcp` (tailnet), **exclusivo do papel `mantenedor`** (t114u); os papéis internos não entram por ele (`docs/operacao/onboarding-agente-externo.md`). Checkout atômico (409 → pega outra); projeto + etiqueta por trilha; MCP `pqbr-kit` com lista fechada por papel; filas Temporal (Camofox e NotebookLM concorrência 1); autor ≠ auditor; quem mede ≠ quem corrige; Comunidade não redige texto livre; tickets **pré-estruturados e agnósticos** (local, falha observada, correções sugeridas), executáveis por qualquer dev/agente.

## 7. Runtime (ADR-011, t510: PydanticAI dentro de activities do Temporal)
1. **Agente = persona + combo + contrato.** Persona: `company/agents/<papel>/AGENTS.md`; combo: `config/modelos_9router.json`; saída: modelo Pydantic v2 em `src/pqbr/contratos`. Fábrica/registro: `src/pqbr/agents/` (detalhes em ARQUITETURA §10).
2. **Só gera e valida.** O agente roda numa activity; escrita em banco, Telegram, Drive e publicação são activities separadas. Nenhum agente tem ferramenta de efeito externo.
3. **Agentes com ferramenta** (Diretor, Pesquisador, Observador, Guardião, Devs): migram depois, com ferramentas PydanticAI explícitas e restritas; até lá seguem no estado anterior (ver `docs/_obsoleto/paperclip-trechos-t510.md`).
4. **Dev Revisor ≠ Dev Corretor:** combos diferentes (`core-revisao` × `core-alto`).
5. **Migrados:** Líder Editorial (reposição da grade, `ReposicaoTemasWorkflow`, 23/10).

6. **Modelos (t414): só combos core do 9router.** Nenhum id direto (`ag/*`, `cu/*`) em agente.

| Combo | Agentes |
|---|---|
| `core-alto` | Diretor, Roteirista, Auditor, Dev Corretor |
| `core-revisao` | Dev Revisor; desempate da 3ª rodada do Auditor (t419) |
| `core-medio` | Pesquisador de Origem, Líder Editorial, Líder Compliance, Guardião de Segurança |
| `core-baixo` | Observador, Especialista SEO, Caçador Sazonal, Comunidade, Diretor de Arte 2D (pausado), Canal José (pqbr) |

Composição no 9router (11/10): `core-alto` = gemini-3.8-flash-high → claude-opus-4-6-thinking; `core-medio` = gemini-3.8-flash-medium → claude-sonnet-4-6 (round-robin); `core-baixo` = gemini-3-flash. Nenhum combo core passa por `cu/*`. `core-revisao` (t416/t419) = claude-sonnet-4-6 → cu/claude-sonnet-5-5-medium (round-robin). **Regra Revisor ≠ Corretor reativada (t419):** Corretor em `core-alto` (Gemini primário), Revisor em `core-revisao` (Claude). Ressalvas: `core-alto` tem Opus como fallback (mesma família Claude em ~metade das chamadas por round-robin) e `core-revisao` inclui `cu/*`, que quebra o `opencode_local`; nos smokes t419 o Revisor passou 2/2, mas a falha de `cu/*` pode aparecer quando o round-robin cair nele (ver §7.1).

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

## 10. Orquestração (ADR-011)
Temporal é o orquestrador e o agendador (Schedules); organograma, posse de tarefa e aprovações viram estado de workflow e sinais (Telegram → `aprovacao_jose`). Painel: Temporal UI. A tabela de alinhamento com o Paperclip ficou em `docs/_obsoleto/paperclip-trechos-t510.md`.

## 11. Mapa antigo (@prod-* → 14 agentes, t395)
Histórico em `docs/_obsoleto/agentes-equipe-14-t395.md`.

## Hindsight — manutenção e qualidade (HS-01, decidido pelo José em 12/10)
- **Dev Corretor** é o dono da manutenção do bank `pqbr`: reindexação/consolidação diária, deduplicação, poda de memórias obsoletas, sem segredos/PII (achou, remove e abre ticket para o Guardião); nada de apagar em massa sem o backup do dia.
- **Observador** mede a qualidade nos relatórios: taxa de acerto (hit rate), defasagem (staleness), duplicatas, tamanho/crescimento; se a manutenção não rodou, abre ticket para o Dev Corretor. Quem mede não corrige.
