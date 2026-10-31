# AGENTES — equipe de 14 agentes e mapa @prod-* (histórico, movido em t90u, 26/10/2026)

Substituído pelos 8 papéis da t476/t512 (`docs/AGENTES.md` §2).

### Equipe anterior (14 agentes; histórico)
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
`pqbr` (perfil Hermes/Telegram: canal do José, t474)

| Agente | Responsabilidade única | Acorda por | Absorveu |
|---|---|---|---|
| Diretor (CEO) | prioriza, desbloqueia, contrata/pausa, resumo semanal; parâmetros operacionais e limpeza noturna do Drive por script (t270) | escalonamento + semanal | Programador de Publicação (propõe janelas; Temporal executa) |
| Líder Editorial | grade 80/20, anti-repetição R10; coordena NotebookLM para pesquisa profunda e proposta de grade; não pesquisa nem cria temas independentemente | grade 1:00 | — |
| Pesquisador de Origem | organiza fontes e confere proveniência da pesquisa do NotebookLM (≥2 fontes); pesquisa independente só como complemento ou fallback documentado | tema aprovado | Checador de Fatos (fonte) |
| Roteirista | orquestra pesquisa/plano/roteiro no NotebookLM em caderno efêmero; valida `RoteiroShort` (15 s–3 min, alvo ~50 s), lista entidades e compõe bloco visual stickman/fichas para o handoff Temporal; sem pesquisa/roteiro independente, sem `ask --new`; medir quota real sem limite fixo | pesquisa pronta | referência visual aprovada no CONTRATO §17; handoff ao workflow Temporal |
| Caçador Sazonal | encaminha dados sazonais ao NotebookLM para pesquisa profunda e proposta de temas (≤20%); rotina Paperclip 30 dias antes de Carnaval, Junina, Natal etc.; sem pesquisa/ideação independente | rotina Paperclip (cron) 30 dias antes de Carnaval, Junina, Natal etc. + issue do Líder Editorial | — |
| Diretor de Arte 2D | Não ativo: papel genérico 2D superado pela identidade stickman aprovada para Flow; fichas/resolvedor pendentes. Não criar ou reativar por t465; o roadmap decide se papel dedicado é necessário | — | — |
| Especialista SEO | orquestra NotebookLM para título, descrição, tags e código PQBR-EP; valida `PacoteSEO`; não redige SEO independentemente nem pede comentário (t263) | roteiro aprovado | — |
| Auditor | auditoria pré-publicação: código extrai quadros/transcrição; **juiz visual** = Gemini web via Camofox (3.8 Flash modo normal, nunca "Flash Estendido"; chat novo por pedido), **2 pedidos distintos**: (1) **VISUAL** — anexos = 1 quadro por cena (pranchas) + fala de cada cena; sim/não por traço visual e `imagem_corresponde_a_fala`; rodado **2×** e falha só se as duas rodadas concordam (divergência → 3ª rodada do agente); (2) **LOOP** — só texto (primeiras e últimas frases da transcrição): `ultima_continua_na_primeira` e `fala_final_cortada_no_meio` (pode migrar para o Jev). Prompts-base: `IDENT_<V>.txt` e `LOOP_todos.txt` (teste v3b); os traços do VISUAL devem ser revistos para a identidade stickman e fichas aprovadas do módulo (F7-02) (RUNBOOK-auditor-v3b; decisoes-jose-2026-10-08 l.103; ENTREGA §2); Jev no texto; código decide; checagens visuais contra fichas stickman quando implementadas; identidade/consistência permanece métrica no piloto até definição de gate (CONTRATO §17) e gate A9 (capa/frame) | pré-publicação | QA de Narração; auditoria de imagem/vídeo e capa do Diretor de Arte 2D (t400) |
| Líder Compliance | políticas YT, item 5, direitos autorais | pré-publicação + diário | Direitos Autorais |
| Comunidade | resumo e saúde dos comentários; triagem e respostas são código + Jev + banco de 60 frases (t245) | ciclo 30 min / 6 h / diário | Triagem + Redator (o "redator" é código; separação mantida porque o agente não escreve texto livre) |
| **Observador** (novo) | loop constante: conexões, auth/reauth, saldos, limites, consumo de tokens por agente/modelo/ação, tentativas e quais falham mais; reprovações do Auditor; reações/resultados dos vídeos (Analytics) para enriquecer relatórios | Temporal faz os pings a cada ~20 min (código) e abre issue no Paperclip em anomalia; agente acorda por essa issue + rotina diária e semanal | Vigia de Custo, Guardião de Sessão (observação), Checador de Reprovações, Capista-monitor, **@prod-analista** |
| Dev Corretor | corrige tickets em branch/worktree com testes; dono do **registro de aprendizado de falhas** (§5) | ticket aberto | — |
| **Guardião de Segurança** (v4.2) | segurança e guardrails (§2.1) | Temporal (varreduras de código) abre issue + rotina diária + gatilho em conteúdo externo novo | parte de segurança que estava diluída no Observador/scanner D14 |
| **Dev Revisor** (v4) | revisa todo PR do Dev Corretor (CI verde + testes + leitura do diff, **modelo do 9router de família diferente** do Corretor); aprova merge automático ou devolve; nunca escreve correção | PR aberto | revisão automática da v3 |

Removidos: `assistente` (duplica o `pqbr`), Capista, QA de Narração, Programador, Direitos Autorais, Triagem, Redator, Vigia de Custo, Guardião de Sessão, Checador, Líderes Visual/Distribuição/Comunidade/Operações (sem filhos, só inflavam). `@prod-publisher` continua **código no Temporal**, não agente.


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
| Canal do José | Telegram (Hermes `pqbr`) + sinais do Temporal; painel = Temporal UI (t474) |

