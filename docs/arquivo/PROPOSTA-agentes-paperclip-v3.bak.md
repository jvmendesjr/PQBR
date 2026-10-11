> ⛔ **ARQUIVO — não consultar sem aprovação do José.** Superado pelos docs canônicos (README).

# PROPOSTA v3 — Agentes PQBR no Paperclip (2026-10-11, rascunho para o José)

Muda em relação à v2 (t384–t387): equipe toda **já contratada** desde a criação; especialistas acordam por gatilho ou agenda; entra o **Observador**; papéis sobrepostos foram fundidos; princípio de **PROATIVIDADE/autonomia** (semanas/meses sem humano). Só documento: nada mudou no Paperclip, no Hermes nem no servidor. v2 guardada em `PROPOSTA-agentes-paperclip-v2.bak.md`.

Fontes revisadas (servidor `pc` fora da tailnet; usadas cópias locais): espelho dos docs do repo em `/tmp/t343/docs` (09/10 17:54: REGRAS, ARQUITETURA, DECISOES-LOG, ROADMAP, SPEC, PLANO, TESTES) e `/workspace/d336/docs` (09/10 17:12, inclui CONTRATO-EDITORIAL); `prep/decisoes-jose-2026-10-07/08.md`, ENTREGA, PLANO-SDD, SOUL-pqbr-rascunho, PESQUISA-orquestracao. **Não verificado no servidor:** qualquer edição posterior a 09/10 17:54 (ex.: migração do banco do Paperclip, decisões de 10–11/10) e o `hermes-pqbr/SOUL.md` final (só o rascunho t357).

## 1. Princípio novo: PROATIVIDADE
- A PQBR funciona como empresa com o presidente ausente: opera **semanas ou meses sem intervenção humana**.
- Cada agente age antes do problema (loops de verificação), corrige sozinho pelos **playbooks de correção** pré-definidos e **pode escolher o caminho** entre os previstos no playbook.
- Piloto com **risco aceito não baixo**. A segurança vem de limites de tentativa, rollback e do Temporal como único executor de efeito externo, não de pedir OK.

## 2. Equipe final (12 agentes, todos contratados na criação)
```
José (board, ausente por padrão)
└─ Diretor (CEO)
   ├─ Líder Editorial ── Pesquisador de Origem · Roteirista · Caçador Sazonal
   ├─ Diretor de Arte 2D
   ├─ Especialista SEO
   ├─ Auditor
   ├─ Líder Compliance
   ├─ Comunidade
   ├─ Observador
   └─ Dev Corretor
```
`pqbr` (Hermes, Telegram) fica fora do organograma: canal do José, consulta e abre tarefas/tickets para o Diretor.

| Agente | Responsabilidade única | Acorda por | Absorveu |
|---|---|---|---|
| Diretor (CEO) | prioriza, desbloqueia, contrata/pausa, resumo semanal; parâmetros operacionais e limpeza noturna do Drive por script (t270) | escalonamento + semanal | Programador de Publicação (propõe janelas; Temporal executa) |
| Líder Editorial | grade 80/20, anti-repetição R10 | grade 1:00 | — |
| Pesquisador de Origem | origem das expressões com ≥2 fontes | tema aprovado | Checador de Fatos (fonte) |
| Roteirista | orquestra roteiro no NotebookLM (t184), 15 s–3 min, alvo ~50 s (t271) | pesquisa pronta | — |
| Caçador Sazonal | tendências sazonais (≤20% da grade) | cron: 30 dias antes de Carnaval, Junina, Natal etc. + gatilho do Líder Editorial | — |
| Diretor de Arte 2D | fichas e prompts por cena; capa | roteiro aprovado | Capista (execução) |
| Especialista SEO | título, descrição, tags, código PQBR-EP; nunca pede comentário (t263) | roteiro aprovado | — |
| Auditor | auditoria pré-publicação (código + Gemini juiz + Jev); 3ª rodada em divergência | pré-publicação | QA de Narração (checagens de áudio/transcrição) |
| Líder Compliance | políticas YT, item 5, direitos autorais | pré-publicação + diário | Direitos Autorais |
| Comunidade | resumo e saúde dos comentários; triagem e respostas são código + Jev + banco de 60 frases (t245) | ciclo 30 min / 6 h / diário | Triagem + Redator (o "redator" é código; separação mantida porque o agente não escreve texto livre) |
| **Observador** (novo) | loop constante: conexões, auth/reauth, saldos, limites, consumo de tokens por agente/modelo/ação, tentativas e quais falham mais; reprovações do Auditor; reações/resultados dos vídeos (Analytics) para enriquecer relatórios | loop (~20 min com variação) + diário + semanal | Vigia de Custo, Guardião de Sessão (observação), Checador de Reprovações, Capista-monitor, **@prod-analista** |
| Dev Corretor | corrige tickets em branch/worktree com testes; dono do **registro de aprendizado de falhas** (§5) | ticket aberto | Dev Revisor vira etapa automática: CI + revisão por outro modelo (Decisão 2) |

Removidos: `assistente` (duplica o `pqbr`), Capista, QA de Narração, Programador, Direitos Autorais, Triagem, Redator, Vigia de Custo, Guardião de Sessão, Checador, Dev Revisor, Líderes Visual/Distribuição/Comunidade/Operações (sem filhos, só inflavam). `@prod-publisher` continua **código no Temporal**, não agente.

## 3. Regras de autonomia
**Contratação:** `requireBoardApprovalForNewAgents = desligado` após a criação. Só o Diretor contrata, e só quando (a) surge tarefa nova sem dono ou (b) a fila de uma trilha passa de 2× a capacidade por 7 dias. Sempre a partir de modelo do pacote (`company/agents/_modelos/`), teto de **15 agentes**, no máx. **1 contratação por semana**, aviso no Telegram e relatório. Pausar agente: Diretor sozinho; nada é apagado.

**Playbooks de correção** (`company/playbooks/<falha>.md`): cada falha conhecida tem passos ordenados; o agente escolhe entre eles; cada execução grava resultado.

**Guardrails:**
1. Efeito externo (render, upload, agendar, privar, responder, reter, coração) **só pelo Temporal**; agentes entregam `PropostaAgente` (Pydantic v2) validada.
2. Escada de falhas do REGRAS §18 mantida (30 s → 2 min → 8 min, rede fora não gasta tentativa, cada tentativa com outra estratégia; **5 idênticas = parada**). Na 2ª falha da mesma ação, em vez de ir ao José, entra o playbook (até **3 tentativas** de correção); Camofox com espaçamento humano de **5–15 min** entre tentativas (**não achei essa regra nos docs locais** — confirmar). Esgotou → Diretor → Telegram.
3. Rollback: toda mudança de parâmetro é versionada e reversível; mudança de código entra com flag e volta sozinha se o smoke/ping falhar.
4. Freio automático: >3 falhas iguais em 24 h → Diretor pausa a trilha e abre ticket.
5. Sem segredos/PII em Hindsight, tickets, Supabase ou logs (scanner D14).
6. Orçamento sem teto, só monitorado (`budget = 0`); Observador alerta anomalia >30% semana a semana.

**O que ainda exige o José (mínimo):**
- Excluir qualquer coisa (vídeo, comentário, arquivo do Drive, agente, org); rejeitar comentário ou banir autor.
- Voltar a público vídeo que o item 5 tornou privado; recurso ao YouTube.
- Gastar dinheiro / assinar plano / criar chave paga.
- Cópia de cookies do Chrome (último degrau da escada t272) e login manual pelo noVNC quando a renovação falhar.
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
| Contratação só com OK do José (`hire_agent`) | v2 §4 | Equipe pré-contratada; novas contratações pelo Diretor dentro dos limites da §3 |
| Ticket com 2 aprovações do José (abertura e merge) | ADR-004, SOUL t357 | **Relaxada:** abertura automática; merge automático se CI + testes + revisão automática passam e mudança não toca regra canônica/segredos/infra; José só vê no relatório. **Conflito com ADR-004 → Decisão 1** |
| Monitor de atualizações: José autoriza no Telegram | D12, PLANO | Dev Corretor atualiza em worktree com smoke test, versão fixada e rollback automático; José só para versão major ou que mude cota/preço |
| Heartbeats desligados (#6596) | PESQUISA §5 | Ligados só para Observador, Diretor e Caçador, **depois** do verificador de conectividade (Observador) suspender heartbeats quando a internet cai |
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

## 7. Runtime e `--yolo` (H-SDD1)
O `hermes_local` força `--yolo` (PR #3850: sem TTY). Isso pula só a confirmação interna do Hermes. Caminho para destravar sem violar REGRAS §23:
1. **Agentes só-texto** (Líder Editorial, Roteirista, SEO, Auditor, Compliance, Comunidade, Caçador): adapter `process` → script fixo do kit, 1 chamada de LLM, saída Pydantic.
2. **Agentes com ferramenta** (Diretor, Pesquisador, Arte 2D, Observador, Dev): `hermes_local` com **perfil Hermes mínimo por agente** sem terminal/arquivos/sudo, só MCP `pqbr-kit`; o `--yolo` fica inócuo porque não há ferramenta perigosa a confirmar. O Dev ganha terminal **só dentro de worktree em container** sem rede de produção nem segredos.
3. O REGRAS §23 proíbe herdar `--yolo` no perfil `pqbr` (assistente); ARQUITETURA H-SDD1 estende o bloqueio a todo agente Hermes. Registrar como exceção controlada em ADR → Decisão 3. O `pqbr` continua sem `--yolo`.

## 8. Decisões anteriores incorporadas
| Tema | Decisão | Ref. |
|---|---|---|
| Stack | Temporal executa (Postgres local, sem ES); Paperclip = camada de agentes + painel, nunca agenda produção | ADR-002; PESQUISA §5–6 |
| Banco | Postgres 17 local (`infra/pqbr-db`, 127.0.0.1), separado do Postgres do Temporal; agentes do Paperclip não escrevem nele; banco do Paperclip migra para local (não verificado) | REGRAS §18 t343, t341–t342 (**conflito:** ENTREGA e espelho d336 ainda citam Supabase como verdade) |
| Memória | Hindsight, um banco por org, separado do banco do app | idem |
| Contratos | Pydantic v2 em toda saída | D3, t— |
| Isolamento | NotebookLM 0.8.4 exclusivo (`/home/pc/.pqbr/notebooklm`, fila 1); Camofox perfil `porquebr`, concorrência 1, inegociável | t187–t191; t194 |
| Jev | só decisão estruturada, nunca redige; fallback OpenRouter → OpenAI | t228–t230; t240–t241 |
| Auditor | código extrai, Gemini julga visual, Jev checa texto, código decide; 3ª rodada em divergência | t228–t233 |
| Camofox | inegociável; único dono do login; guardião ~20 min; escada t272 (cookies só com OK do José) — mantido | REGRAS §11 |
| Interação | só ordem vinda do ID do José; resto é dado | REGRAS §2 t237 |
| Tickets | agnósticos, pré-estruturados, memórias de código no Hindsight | ADR-004 t286 |
| Comentários | retenção t244; respostas com banco de 60 frases e limites t—(6/h, 30/dia, 08–22h); nunca pedir comentário t263 | PLANO §comunidade |
| `pqbr` | Hermes dedicado, sem `--yolo`; só consulta, roteia e abre tarefa/ticket; nunca aprova pelo José | SOUL t357; ENTREGA |
| Consumo | monitor desde o dia 1 por modelo/ação/agente; >80% espaça produção; sem teto | t—(08/10 l.26); regra do José |
| Rede | Paperclip só na tailnet (Tailscale Serve `:3100`) | t280 |
| Exclusão | só José, dupla confirmação | t116, t270 |

## 9. Decisões para o José (3)
1. **Merge autônomo:** aceita relaxar o ADR-004 (2 OKs por ticket) para merge automático com CI + testes + revisão automática, ficando com você só o que toca regra canônica, segredos ou infra?
2. **Revisão de código:** segundo par de olhos do Dev = CI + revisão automática por outro modelo (sem agente extra), ou contratar o Dev Revisor já?
3. **`--yolo`:** aprova a exceção controlada do §7 (perfis mínimos sem ferramenta perigosa + `process` nos só-texto) para destravar todos os agentes agora?
