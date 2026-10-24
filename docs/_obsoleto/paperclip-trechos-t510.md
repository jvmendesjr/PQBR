# Trechos Paperclip retirados dos docs canônicos (t510, 23/10/2026, ADR-011)

Texto original preservado, sem edição.

## ARQUITETURA §10 (Paperclip, até 23/10)

## 10. Integração com o Paperclip [HISTÓRICO; Paperclip em retirada pela ADR-011]

### Hermes `pqbr` ↔ Paperclip [HISTÓRICO, t474; t363;
- **Identidade:** agente `pqbr-assistente` (`7d18350e…`) na empresa **PQBR-TESTE** (`d9fa962a…`), adaptador `process` com `/bin/true`, heartbeat desligado, orçamento 0, permissões `canAssignTasks` sim, `canCreateAgents`/`canCreateSkills` não. **Chave de agente** `hermes-pqbr` (id `58b8794a…`), escopada à empresa (outra empresa → 403), guardada só em `~/.hermes/profiles/pqbr/.env` (`PAPERCLIP_PQBR_API_KEY`, 600).
- **Acesso:** contexto CLI próprio `~/.hermes/profiles/pqbr/paperclip/context.json` (600, persona agent, a URL da tailnet na porta 3100 (`<ip-tailnet>:3100`), porque o Paperclip só escuta na tailnet, não em 127.0.0.1) + wrapper `paperclip/pqbr-paperclip` com allowlist (issue list/get/comments/create/comment/update; agent list/get/me/heartbeat:invoke; project, activity, dashboard) e escopo fixo + skill `skills/productivity/paperclip-pqbr`. Cópias no repo: `docs/hermes-pqbr/perfil/`.
- **Acesso desde t372:** o perfil **não tem terminal, arquivos, código, web, navegador, delegação nem cron** (desligados em `cli` e `telegram`); ficam skills, memória, busca de sessões, perguntas e o **servidor MCP `paperclip-pqbr`** (`paperclip/mcp_paperclip.py`, só stdlib, ferramentas fixas: listar/ver issues e comentários, criar issue, comentar, listar e acordar agentes). A chave é lida pelo MCP e nunca volta ao modelo. O wrapper `pqbr-paperclip` fica só para uso manual. Busca de arquivos só leitura em `docs/`: o Hermes não oferece escopo por pasta no toolset `file`, então ficou desligada (EM CONSTRUÇÃO: ferramenta MCP de leitura em `docs/`, se o José quiser).
- **Escrita:** comentar ou atualizar issue com chave de agente exige o contexto de um heartbeat (`Cross-issue writes need a run`); a leitura funciona direto. O comentário de teste na PQB-4 só saiu com o `--run-id` de um heartbeat do próprio `pqbr-assistente`. Desde t372 o MCP faz isso sozinho: heartbeat do próprio agente com `payload.issueId` e o run id na escrita.
- **Reapontar na F1-02:** criar o mesmo agente na org PQBR real, nova chave, trocar `companyId`/`agentId` no contexto e revogar a chave de teste.
- **Incidente no teste (09/10 ~19:20):** o Hermes `pqbr` tem terminal e arquivos sem restrição. No teste, além do wrapper, ele leu `/proc/<pid>/environ` do processo do Paperclip e expôs o `DATABASE_URL` do Paperclip ao modelo e ao histórico do perfil. **Conferido em t372:** o Hermes mascarou a senha (`***`) antes de guardar; foram expostos usuário e host do Supabase, não a senha. A mensagem foi apagada do `state.db` (com backup) e o banco foi compactado; também escreveu `cache/scratch/invoke_run.js`, que lê a chave do `.env` e chama a API direto. **O "acesso restrito" do SOUL não está garantido pela configuração.** Antes de ligar o `pqbr` no Telegram: restringir os toolsets do perfil (sem terminal livre; só o wrapper e as skills) e rodar de novo o teste ponta a ponta.


- O Temporal publica eventos de negócio (via outbox) no banco do app e abre/atualiza **issues** no Paperclip (episódio, revisão, ticket, proposta).
- Os agentes no Paperclip (director, analista, comunidade, compliance, assistente, dev) leem o banco do app (só pelo contexto do fluxo ou `pqbr_leitura`) e issues e devolvem **`PropostaAgente`** validada; nunca executam efeito externo.
- A aprovação do José pelo Telegram (Hermes `pqbr`) vira sinal `aprovacao_jose` no Temporal (t474). A rota valida o ID autorizado, a tarefa e o estado, e falha fechada.
- Heartbeats desligados até a liberação; nenhum agente com `--yolo` (H-SDD1).


## AGENTES §7 Runtime v4.2 (Paperclip process/opencode_local)

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


## AGENTES §10 Alinhamento com o Paperclip

## 10. Alinhamento com o Paperclip (docs oficiais, 11/10)
| Ponto | Como fica | Doc |
|---|---|---|
| Organograma | `reportsTo` do mesmo company, sem ciclo; Diretor `role: ceo`, `reportsTo: null` | https://docs.paperclip.ing/reference/api/agents/ |
| Equipe inicial | criada pelo board (`POST /agents`, board-only) ou import do pacote; contratações seguintes pelo Diretor via `POST /agent-hires` + skill `paperclip-create-agent`, com `sourceIssueId` | https://docs.paperclip.ing/how-to/handle-board-approvals-for-hires/ |
| Aprovação de contratação | desligada → contratação ativa na hora; José vê pelo canal privado ativo (Telegram/Hermes `pqbr`; t474)/atividade | idem; https://docs.paperclip.ing/guides/day-to-day/approvals/ |
| Instruções | `instructionsBundle` (AGENTS.md/SOUL.md), não `promptTemplate` | https://docs.paperclip.ing/reference/api/agents/ |
| Skills | instaladas no nível da empresa; `desiredSkills` na criação; sem Hermes nos agentes (v4.2) | https://docs.paperclip.ing/reference/api/agents/ |
| Agendamento | timer desligado; rotinas Paperclip acordam agentes, inclusive produção (t392); efeito externo e calendário de execução seguem no Temporal (ADR-002) | https://docs.paperclip.ing/guides/projects-workflow/routines/ |
| Posse de tarefa | checkout atômico, 409 para dono vivo; lock preso a run morto já corrigido (#5413/#6223), exigir versão com o fix | https://github.com/paperclipai/paperclip/issues/6007 |
| Chaves/segredos | chave de API por agente; segredos só por `secret_ref` no `env` (respostas mascaram); nunca no AGENTS.md | https://docs.paperclip.ing/reference/api/agents/ |
| Rollback | `config-revisions/{id}/rollback` para config de agente; arquivos do bundle não têm histórico → versionar `company/` no git | idem |
| Orçamento | warn-only (ver §3.6) | https://docs.paperclip.ing/how-to/set-monthly-budget/ |
| Adapters | `process` (texto) e `opencode_local` (ferramenta) → 9router | https://docs.paperclip.ing/reference/adapters/overview/ |


## ROADMAP Fase 1 F1-01..F1-03 (org Paperclip)

## Fase 1: org PQBR no Paperclip (agentes pausados)
> Reconciliação 2026-10-15: a organização PQBR atual já está ativa e integrada ao Discord. F1-01/F1-02 descrevem um pacote antigo que criaria uma segunda organização; ficam suspensas, sem novo G1/importação, até adaptar o plano à organização existente.

- **F1-01 [SUSPENSO — reconciliar com a organização ativa; não importar como nova]** Pacote `company/` (agentcompanies/v1)
  - Req: RF-33, RNF-12 · Testes: TS-09 · Depende de: F05-07, F00-01
  - Aceite: `COMPANY.md`, `agents/<slug>/AGENTS.md` (director, analista, comunidade, compliance, dev), `.paperclip.yaml` sem segredos; validador e scanner passam; o Diretor atende José diretamente pelo Discord/Paperclip após t464; não criar agente Hermes/assistente duplicado.
  - Portão José: **G1**. Obs: 2026-10-10 (t376): pacote pronto em `company/` (COMPANY.md, 6 AGENTS.md, `.paperclip.yaml` com adaptador `process` stub, heartbeat desligado, orçamento 0); scanner limpo; dry-run sem avisos nem erros. **Aguarda o G1 do José** (revisar o pacote).
  - Estado: o pacote e dry-run registrados em 10/10 pertencem ao plano antigo. Não solicitar G1 nem aplicar esse pacote à organização atual antes da reconciliação.
- **F1-02 [SUSPENSO — nenhuma organização nova autorizada ou necessária]** Import dry-run e criação da org pausada
  - Req: RF-43, RNF-13 · Testes: TS-13 · Depende de: F1-01
  - Aceite: dry-run limpo (H-SDD2); agentes pausados, heartbeats desligados.
  - Portão José: autorizar o import; liberar agente é decisão separada. Obs: 2026-10-10 (t376): **só o dry-run**, limpo (`docs/sdd/f1-02-dryrun.md`); nenhuma org criada. O pacote não carrega `paused`: pausar todos logo após o import. Criação real aguarda o José.
  - Estado: dry-run histórico concluído; importação real não executada. Não rodar `company import --target new`; revisar apenas o que ainda se aplica à organização PQBR ativa.
- **F1-03 [SUPERADO por t464]** O ajuste operacional do perfil Hermes `pqbr` não se executa separadamente; a pausa ocorre somente pelo gate F05-09, após a migração completa.
  - Req: RF-34, RF-48 · Testes: TZ-10 · Depende de: F05-06, F05-08, F05-09
  - Aceite: confirmar que o perfil Hermes `pqbr` foi pausado pelo gate F05-09; preservar dados/configuração para rollback e manter ligado o gateway Hermes compartilhado.
  - Portão José: t464 autoriza a pausa somente após aprovação de F05-09; nenhuma alteração separada no perfil. Obs:
  - Obs: 2026-10-09 (t363): `pqbr` conectado ao Paperclip na PQBR-TESTE por chave de agente escopada (agente `pqbr-assistente`, wrapper com allowlist, skill `paperclip-pqbr`); listar ok, outra empresa recusada, comentário de teste na PQB-4 criado (`4ad87746…`) só com run de heartbeat. **Pendências:** (1) restringir os toolsets do perfil (no teste ele saiu do wrapper e expôs o `DATABASE_URL` do Paperclip ao modelo, ARQUITETURA §10); (2) heartbeat+run dentro do wrapper para escrever; (3) reapontar para a org real na F1-02.
  - Obs: 2026-10-09 (t372): toolsets restritos (sem terminal, arquivos, código, web, navegador, delegação, cron) em `cli` e `telegram`; Paperclip só pelo MCP `paperclip-pqbr` (heartbeat embutido). Teste oneshot: listar ok; comentário na PQB-4 ok (`4488f764…`); pedido de `env`/`/proc/self/environ` recusado (só ferramentas MCP foram chamadas). Sem gateway do `pqbr` rodando, então nada foi recarregado. Mensagem com o `DATABASE_URL` (senha mascarada) apagada do `state.db` e `invoke_run.js` removido. Pendente: reapontar para a org real (F1-02); leitura de `docs/` por MCP se o José quiser.
- [~] **AÇÃO MANUAL PENDENTE — José (t373):** trocar a senha do banco do Paperclip no Supabase; depois atualizar o `DATABASE_URL` em `~/.config/core-engineering/supabase.env` (EnvironmentFile do `paperclipai.service`) e reiniciar **só** o Paperclip. Passos preparados (não executados): (1) `cp -p ~/.config/core-engineering/supabase.env ~/Backups/paperclip/supabase.env.$(date +%F)` e `chmod 600`; (2) editar só a senha no `DATABASE_URL` (sem imprimir); (3) `systemctl --user restart paperclipai.service`; (4) conferir `paperclipai health`, o painel e `issue list` da PQBR-TESTE; rollback: restaurar o arquivo e reiniciar o serviço. Obs: até lá, a senha atual continua válida (não foi exposta, t372). **[SUPERADO t412: o Supabase não é mais usado; a troca de senha sai das pendências. O risco do DATABASE_URL vazado acaba com o L-01 + desligamento/exclusão do projeto Supabase pelo José.]**
