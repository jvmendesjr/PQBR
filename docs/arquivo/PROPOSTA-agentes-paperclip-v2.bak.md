> ⛔ **ARQUIVO — não consultar sem aprovação do José.** Superado pelos docs canônicos (README).

# PROPOSTA v2 — Agentes PQBR no Paperclip (2026-10-11, rascunho)

Base: ARQUITETURA ADR-002 (Temporal executa; Paperclip = camada de agentes + painel; agentes propõem `PropostaAgente` Pydantic v2; nunca escrevem no banco do app nem executam efeito externo), ADR-004 (dev: 2 aprovações do José, abertura e merge), REGRAS §23/H-SDD1.
Orçamento: **sem teto; só monitoramento por agente** (regra do José). `budgetMonthlyCents = 0` em todos; o consumo vai para a tabela de consumo (por modelo, ação e **agente**).

## 1. O que o Paperclip já oferece (nativo)
| Recurso | Como funciona | Fonte |
|---|---|---|
| Organograma | árvore estrita, `reportsTo` único, sem ciclos; delegação e escalonamento pela cadeia | https://docs.paperclip.ing/guides/org/org-structure/ · https://github.com/getpaperclipai/paperclip/blob/master/docs/guides/board-operator/org-structure.md |
| Contratação por agente | `POST /api/companies/{id}/agent-hires`; com `requireBoardApprovalForNewAgents` ligado, nasce `pending_approval` + aprovação `hire_agent` (sem heartbeat, chave nem skills até aprovar). Skill pronta `paperclip-create-agent` | https://paperclip.inc/docs/paperclip/how-to/handle-board-approvals-for-hires/ · https://paperclip.inc/docs/paperclip/guides/org/agents/ |
| Orçamento por agente | aba Budget; parada dura opcional; subordinado só propõe aumento | mesma página de Agents |
| Posse da tarefa | checkout atômico `POST /api/issues/:id/checkout` com `expectedStatuses`; 409 se outro dono; nunca mudar para `in_progress` à mão | https://paperclipai-paperclip.mintlify.app/concepts/tasks |
| Trabalho fora da linha | agente pode receber tarefa de fora da sua linha, mas não cancela (devolve ao gestor) | org-structure.md |
| Pacote portátil | agentcompanies/v1 (COMPANY/TEAM/AGENTS/SKILL) | https://github.com/paperclipai/paperclip/blob/master/docs/companies/companies-spec.md |

## 2. Organograma (núcleo de 9 + contratáveis)
```
José (board)
└─ Diretor (CEO)
   ├─ Líder Editorial ── Pesquisador de Origem · Roteirista · [Caçador Sazonal] · [Checador de Fatos]
   ├─ Líder Visual/Áudio ── Diretor de Arte 2D · [Capista] · [QA de Narração]
   ├─ Líder Distribuição ── Especialista SEO · [Programador de Publicação]
   ├─ Líder Qualidade/Compliance ── Auditor · [Direitos Autorais]
   ├─ Líder Comunidade/Dados ── [Triagem de Comentários] · [Redator de Respostas] · [Vigia de Custo]
   └─ Líder Operações ── [Guardião de Sessão] · Dev Corretor · [Dev Revisor]
```
`[ ]` = contratar sob demanda. `pqbr` (Hermes, Telegram) fica fora do organograma: abre tarefas para o Diretor e consulta, não executa.

Para não inflar: os líderes do núcleo **acumulam a função dos especialistas ainda não contratados** dentro da própria trilha. Sem líder para Comunidade/Dados e Operações no início: Diretor assume até a 1ª contratação? → ver Decisão 2. Núcleo real = Diretor, Líder Editorial, Pesquisador de Origem, Roteirista, Diretor de Arte 2D, SEO, Auditor, Líder Compliance, Dev Corretor.

## 3. Posse (RACI simplificado): 1 dono por tarefa
| Tarefa | Dono (R/A) | Pode pedir/consultar | Não toca |
|---|---|---|---|
| Grade de temas 80/20 | Líder Editorial | Analista/Vigia (dados), Diretor | Roteirista, SEO, Arte |
| Origem de expressão + fontes | Pesquisador de Origem | Checador de Fatos | Roteirista (não inventa fonte) |
| Tendência sazonal (≤20%) | Caçador Sazonal (até contratar: Líder Editorial) | Analista | demais |
| Roteiro (NotebookLM) | Roteirista | Pesquisador, Líder Editorial | SEO, Arte, Auditor |
| Fichas/prompts 2D | Diretor de Arte 2D | Roteirista (contexto) | Roteirista não muda estilo |
| Capa/thumbnail | Capista (até contratar: Arte 2D) | SEO (texto da capa) | — |
| Narração/áudio QA | QA de Narração (até: Líder Visual/Áudio) | Roteirista | — |
| Render FFmpeg, upload, privar | **Temporal** (Activity) | qualquer agente lê status | **nenhum agente** |
| Título/descrição/tags | Especialista SEO | Roteirista | Roteirista não edita metadado |
| Data/hora de publicação | Programador (até: Líder Distribuição) propõe; Temporal executa | Analista | — |
| Auditoria final (+3ª rodada) | Auditor | — | autor da peça não audita a própria |
| Políticas YouTube / item 5 | Líder Compliance | Auditor | — |
| Direitos autorais (imagem, música, citação) | Direitos Autorais (até: Líder Compliance) | Arte 2D | — |
| Triagem de comentários | Triagem (até: Jev + rotina) | — | Redator |
| Texto de resposta (banco 60 frases) | Redator de Respostas | Triagem | Triagem não responde |
| Relatório diário / métricas | Analista (Líder Comunidade/Dados) | todos leem | — |
| Consumo por agente | Vigia de Custo (até: Analista) | Diretor | ninguém altera a tabela |
| Sessão Camofox/Studio/NotebookLM | Guardião de Sessão (até: Temporal + Dev Corretor) | — | demais não abrem navegador |
| Ticket e correção | Dev Corretor | Líderes pré-estruturam ticket | não faz merge |
| Revisão de PR | Dev Revisor (até: José) | — | o autor não revisa |
| Prioridades, desbloqueio, contratação | Diretor | líderes propõem | especialistas não contratam |

### Antiinterferência
1. **Checkout atômico** obrigatório em toda tarefa (skill `pqbr-contrato`); 409 → pega outra.
2. **Projeto por trilha** (Editorial, Visual/Áudio, Distribuição, Qualidade, Comunidade, Operações) + **etiqueta de trilha**; agente só faz checkout no seu projeto. Tarefa de outra trilha = comentar e devolver ao gestor.
3. **Escopo de MCP por agente**: servidor `pqbr-kit` com lista fechada de ferramentas por papel (chave própria por agente); nenhuma ferramenta de efeito externo.
4. **Filas do Temporal** como único executor: Camofox concorrência 1, NotebookLM isolado; agentes só enfileiram pedido.
5. **Separação de funções**: autor ≠ auditor; triagem ≠ redator; corretor ≠ revisor.
6. Saída só em `PropostaAgente`/contrato da trilha; Temporal valida e rejeita campo fora do papel.

## 4. Plano de contratação
- `requireBoardApprovalForNewAgents = ligado`: todo pedido vira `hire_agent` para o José.
- Só Diretor e líderes contratam, usando a skill `paperclip-create-agent` + modelo de agente do pacote (`company/agents/_modelos/`), já com skills, MCP e trilha. Nada de agente fora do modelo.
- Gatilhos (o líder anexa a evidência ao pedido):
  | Especialista | Gatilho |
  |---|---|
  | Caçador Sazonal | 30 dias antes de Natal/Carnaval/Junina, ou >20% da grade sazonal |
  | Checador de Fatos | ≥2 reprovações do Auditor por fato/fonte em 14 dias |
  | Capista | capa custom aprovada pelo José, ou CTR abaixo da meta por 2 semanas |
  | QA de Narração | ≥2 defeitos de áudio em 14 dias |
  | Programador de Publicação | >1 vídeo/dia ou teste de horários |
  | Direitos Autorais | 1º alerta de direitos/Content ID ou uso de material de terceiros |
  | Triagem / Redator | fim dos 3 dias em sombra e >50 comentários/dia |
  | Vigia de Custo | variação >30% de consumo semana a semana |
  | Guardião de Sessão | ≥2 quedas de sessão em 7 dias |
  | Dev Revisor | >3 PRs/semana à espera do José |
  | Líderes Comunidade/Dados, Operações | 1º especialista da trilha contratado |
- Demissão/pausa: proposta do líder com motivo; José aprova; nada é apagado (agente fica pausado).

## 5. Fichas do núcleo
Comum a todos: skill `pqbr-contrato` (checkout, trilha, `PropostaAgente`, 3 tentativas, sem apagar, sem segredos, escalonar pela cadeia); sem terminal/arquivos/código; heartbeat desligado (acordam por tarefa aberta pelo Temporal); runtime `hermes_local` com perfil Hermes mínimo por agente — **bloqueado por H-SDD1** (REGRAS §23 proíbe herdar `--yolo`); alternativa para agentes só-texto: adapter `process` chamando script fixo do kit que faz uma única chamada de LLM.

| Agente | Missão | Persona | Skills obrigatórias | Extras úteis | Ferramentas MCP | Gatilho | Runtime / modelo |
|---|---|---|---|---|---|---|---|
| Diretor | prioriza, desbloqueia, contrata, consolida ao José | editor-chefe seco | `priorizacao`, `paperclip-create-agent` | rotina semanal de resumo | tarefas Paperclip, `kit.status`, `kit.roadmap_ler` | semanal + escalonamento | hermes_local / médio |
| Líder Editorial | grade de temas 80/20, anti-repetição | curador de curiosidades | `grade-80-20`, `anti-repeticao` | knowledge: temas já publicados; memória Hindsight (leitura) | `kit.temas_grade`, `kit.dedup` | grade 1:00 AM | process / baixo |
| Pesquisador de Origem | origem de expressões com fontes citáveis | etimólogo cético | `origem-expressao`, `fonte-citavel` | checklist de fonte (≥2, data) | `kit.notebooklm_consulta` (fila), busca web | tema aprovado | hermes_local / médio |
| Roteirista | roteiro ≤60 s, gancho 2 s, autossátira | humorista do cotidiano | `roteiro-short`, `contrato-editorial-v2` | evals: ~20 roteiros de ouro | `kit.notebooklm_roteiro`, `kit.validar_roteiro` | pesquisa concluída | process / forte |
| Diretor de Arte 2D | fichas e prompts 2D por cena (estilo livre, Decisão 4) | ilustrador | `estilo-2d`, `ficha-visual` | knowledge: guia de estilo | `kit.prompt_imagem`, `kit.gemini_fila` | roteiro aprovado | hermes_local / médio |
| Especialista SEO | título, descrição, 5–8 tags, legenda | otimizador de busca | `seo-shorts` | checklist de metadados | `kit.validar_metadados`, `kit.analytics_ler` | roteiro aprovado | process / baixo |
| Auditor | auditoria final; 3ª rodada em divergência | revisor rigoroso | `checklist-auditoria`, `fatos-fonte` | evals de reprovação | `kit.audit_rodada`, `kit.diff_contrato` | pré-publicação | process / forte |
| Líder Compliance | políticas YouTube, item 5, direitos (até contratar) | jurista direto | `politicas-yt`, `item5` | knowledge: políticas fixadas por data | `kit.compliance_check`, `kit.studio_ler` | pré-publicação + diário | process / baixo |
| Dev Corretor | corrige tickets em branch com testes | SRE metódico | `triagem-falhas`, `pr-pequeno` | memória de código Hindsight (ADR-004) | tickets, git branch/PR, logs (leitura) | ticket aprovado pelo José | hermes_local (perfil dev) / forte |

Analista (existente) entra como **Líder Comunidade/Dados** quando a trilha abrir; até lá o `AnalistaWorkflow` roda por Schedule e as propostas vão ao Diretor. Comunidade (existente) segue nos 3 dias em sombra, como rotina + Jev, até a contratação da Triagem/Redator.

## 6. Mudanças em relação ao pacote atual
- Sai `assistente` (duplica o `pqbr`). `director`, `compliance` e `dev` mudam de escopo; `analista` e `comunidade` viram trilha/contratação.
- Novos no núcleo: Líder Editorial, Pesquisador de Origem, Roteirista, Diretor de Arte 2D, SEO, Auditor.
- Em todos os agentes: budget 0 + consumo por agente.

## 7. Decisões para o José
1. Aprovar o núcleo de 9 e o organograma por trilhas?
2. Até a 1ª contratação, o Diretor acumula as trilhas Comunidade/Dados e Operações (e o José revisa os PRs)?
3. Runtime: H-SDD1 (REGRAS §23) proíbe `--yolo`, e o `hermes_local` força. Usar `process` (script fixo + 1 chamada de LLM) nos agentes só-texto e manter os 3 que precisam de ferramentas (Pesquisador, Arte 2D, Dev) parados até H-SDD1 ser resolvido?
4. Estilo 2D livre já vale para o Diretor de Arte, ou ele fica no stickman até a discussão de conteúdo?
5. Os gatilhos de contratação da §4 servem como estão?
