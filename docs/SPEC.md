# SPEC da PQBR (requisitos)

> Autoridade: abaixo de `docs/REGRAS.md` (cuja §0–§3 é a constituição do projeto) e acima de `docs/ARQUITETURA.md`. Cada requisito aponta para a seção do REGRAS de onde vem; nenhum requisito cria regra nova.
> Fonte única: os IDs RF/RNF são usados em `docs/ARQUITETURA.md`, `docs/TESTES.md`, `docs/ROADMAP.md` e `docs/RASTREABILIDADE.md`. Para mudar um requisito, mude a regra no REGRAS primeiro.
> Não consultar material restrito (t287). Legenda: [PROPOSTA] · [HIPÓTESE] · EM CONSTRUÇÃO — aguardando José.

## 1. Requisitos funcionais por funcionalidade

### F01. Grade e temas

**História:** Como José, quero que a grade do dia saia sozinha, correta e sem temas repetidos, para não precisar cobrar o sistema.

**Critérios de aceite da funcionalidade:**
- A grade do dia D é gerada só a partir da data D e gravada antes do lote.
- Nenhum tema publicado (ou variação próxima) entra na grade; o teste do incidente de 08/10 passa.
- Tema acima de 75 de polêmica não entra sem o José; tema do bloqueio absoluto nunca entra.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-01 | Grade diária gerada por código a partir da data e gravada no banco do app; início automático. | §3, §4 |
| RF-02 | Três barreiras de repetição + R10 (tema repetido recusado mesmo se o José sugerir; avisa ou abre ticket), usando `temas-publicados.csv` como carga inicial. | §4 |
| RF-03 | Mistura ~70% em alta / ~30% perenes; última janela preferencialmente perene. | §4 |
| RF-04 | Coleta de tendências (Data API) e de comentários de vídeos virais; resumo ≤ ~300; caderno diário de tendências separado do raiz. | §4 |
| RF-05 | Pontuação de polêmica 0–100 em código (faixa 50–75; > 75 aguarda o José) e bloqueio absoluto de temas sensíveis. | §4 |

### F02. Roteiro e produção

**História:** Como José, quero roteiros no tom do canal e vídeos prontos de manhã, para publicar nas janelas sem intervenção.

**Critérios de aceite da funcionalidade:**
- Roteiro validado pelo `RoteiroShort` (duração, CTA, sem nomes, sem pedido de comentário).
- Produção sempre em caderno efêmero; nenhuma chamada ao caderno raiz.
- Consumo do NotebookLM gravado antes e depois de cada geração.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-06 | Ideação, roteiro, SEO e pesquisa no NotebookLM em caderno efêmero; nunca no raiz; Gemini web como reserva. | §9 |
| RF-07 | `RoteiroShort`: 15 s–3 min, alvo ~50 s, ~2,3 palavras/s; CTA final só "Segue o Porquê BR"; sem pedido de comentário; sem nomes; loop; 1–2 personagens. | §5 |
| RF-08 | Resolvedor de fichas sem LLM; ficha nova criada na hora sem aprovação bloqueante; verificação "Verificado/Não Aprovado" por Telegram e painel. | §6 |
| RF-09 | Render no NotebookLM e pós FFmpeg (corte do end card só se detectado; logo com zoom suave sobre a última fala). | §5, §9 |
| RF-10 | Instalação exclusiva do notebooklm-py 0.8.4, serviço único dono da sessão, `usage --json` gravado; acima de 80% numa janela, espaçar produções. | §9, §10 |

### F03. Auditor

**História:** Como José, quero que só vídeos dentro das travas sejam publicados, com motivo claro quando algo reprova.

**Critérios de aceite da funcionalidade:**
- Veredito decidido pelo código com base em respostas sim/não e checagens de texto.
- Falso aprovado e falso reprovado medidos no gabarito ampliado.
- Estilo visual e imagem×fala nunca reprovam sozinhos.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-11 | Auditor extrai 1 quadro por cena e a transcrição (Whisper). | §8 |
| RF-12 | Juiz visual Gemini web via Camofox (sem API), sim/não por traço em 2 rodadas; divergência vai ao José; Jev nas checagens de texto; o código decide. | §7, §8 |
| RF-13 | Travas: falta de ironia/sátira; narração; loop; CTA; pedido de comentário; fala cortada; nome; terceiros; segurança; direitos de áudio > 60 s. Estilo visual e imagem×fala não reprovam. | §5, §8 |
| RF-14 | Relatório do auditor por template (veredito, motivo, ID da cena), sem prosa de LLM. | §7, §8 |

### F04. Publicação

**História:** Como José, quero os vídeos agendados nas janelas certas, sem duplicata e sem publicar reprovado.

**Critérios de aceite da funcionalidade:**
- Upload interrompido não gera duplicata.
- No máximo 4 por dia; reprovado nunca publicado; horário sem reserva cancelado.
- Agendado confere com o aprovado (título, descrição, código).

| ID | Requisito | REGRAS |
|---|---|---|
| RF-15 | Publicação por `videos.insert` com agendamento; até H1, sobe privado e o Camofox agenda; Studio como reserva. | §15 |
| RF-16 | Sem duplicata: código PQBR-EPxxxx na descrição e etiqueta; busca no banco do app e no canal (privados e agendados); 1 tentativa sem confirmação e para. | §15 |
| RF-17 | Janelas 11:40, 14:40, 18:35, 21:15; teto 4/dia sem mínimo; reserva ≥ 2; vídeo reprovado nunca publicado; horário sem reserva é cancelado. | §15 |
| RF-18 | Jev decide refazer/trocar/chamar José e confere agendado × aprovado. | §7, §15 |

### F05. Correção pós-publicação (item 5)

**História:** Como José, quero que qualquer problema torne o vídeo privado na hora e me avise, sem republicação.

**Critérios de aceite da funcionalidade:**
- Sinal de problema → privado e Telegram em minutos, com motivo.
- Nenhum vídeo volta a público nem é excluído sem o José.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-19 | Qualquer problema detectado → vídeo privado na hora, automático, com aviso no Telegram; sem substituição nem republicação. | §16 |
| RF-20 | Volta a público só com toque do José; exclusão só pelo José com dupla confirmação; toda ação registrada. | §16 |
| RF-21 | Limiar por comentários (≥ 2 pessoas diferentes, ou 1 grave); abaixo disso, vai ao José. | §16 |

### F06. Comunidade

**História:** Como José, quero que comentários comuns sejam respondidos com naturalidade e que só casos graves cheguem a mim.

**Critérios de aceite da funcionalidade:**
- Respostas só do banco aprovado e dentro dos limites.
- Casos graves (reclamação muito grave, direitos, situação visivelmente grave) desligam o automático e vão ao José, com tom formal.
- Sombra e resposta real de teste antes de ligar.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-22 | Leitura de comentários pela API (30 min / 6 h / diária), incluindo retidos e provável spam; sem Camofox. | §19 |
| RF-23 | Classificação multirrótulo pelo Jev; retenção sozinha (`heldForReview`) nos casos aprovados; rejeitar/banir/excluir só o José. | §19 |
| RF-24 | Respostas automáticas do banco de 60 frases aprovado, com os limites aprovados (t245, t274). | §19 |
| RF-25 | Corações pelo Camofox, até 10/dia, só na sessão aberta pelo guardião. | §19 |
| RF-26 | Desligamento automático das respostas e escalonamento ao José só em reclamação muito grave, direitos autorais ou situação visivelmente grave; tom formal nesses casos; kill switch manual do José. | §19 |
| RF-27 | Sombra de 3 dias (ou ~30 respostas simuladas aprovadas) e 1 resposta real de teste antes do automático. | §19 |

### F07. Conformidade

**História:** Como José, quero saber de avisos do YouTube e ter a fila parada em caso crítico.

**Critérios de aceite da funcionalidade:**
- Crítico gera HOLD, privados os agendados, Telegram e ticket.
- Recurso só enviado pelo José.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-28 | Compliance: coleta por código (e-mail do canal, Studio só leitura, Data API); gravidade info/atenção/crítico; crítico = HOLD + privados os agendados + Telegram + ticket. | §13 |
| RF-29 | Rascunho de recurso preparado pelo agente; o José envia; nada sem dupla confirmação. | §13 |

### F08. Analista e relatórios

**História:** Como José, quero um relatório diário confiável, com custos e com aviso quando os números não significam nada.

**Critérios de aceite da funcionalidade:**
- Relatório diário por template no Telegram.
- Exceções sinalizadas; aviso de amostra sem significância estatística.
- Custos levantados sem teto.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-30 | Coleta diária pela Analytics API; análise semanal ou por anomalia; o analista só observa até ~30 Shorts/90 dias. | §20 |
| RF-31 | Relatório diário por template: produção, consumo, custos, compliance, comunidade, limpeza; sinaliza exceções e avisa quando os números não são estatisticamente significativos. | §19, §20, §22 |
| RF-32 | Levantamento de custos (tokens, uso do NotebookLM, APIs) sem teto mensal. | §22 |

### F09. Agentes, interação e manutenção

**História:** Como José, quero que os agentes só proponham e que eu aprove, pelo Telegram, tudo o que muda.

**Critérios de aceite da funcionalidade:**
- Toda proposta é um objeto Pydantic v2 válido; nada se aplica sem aprovação.
- Ordem só vale do ID autorizado.
- Ticket chega pré-estruturado e tem 2 aprovações.
- Item que falha em tudo vai para revisão, e a determinação é registrada.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-33 | Padrão dos agentes pensantes: rotina fixa executa; agentes observam e propõem só como saída Pydantic v2; aplicação só após aprovação do José. | §3 |
| RF-34 | @pqbr-assistente no Hermes `pqbr` pelo Telegram: só consulta, roteia e responde pelo banco; ordem só do ID autorizado do José. | §2 |
| RF-35 | Tickets de manutenção agnósticos, pré-estruturados (localização, falha, correções sugeridas), com 2 aprovações do José (abertura com correções + merge); memórias de código no bank Hindsight único. | §24 |
| RF-36 | Revisão humana como último recurso: local dedicado, aviso ao José e registro da determinação (excluir, corrigir, reaproveitar, arquivar). | §5 |

### F10. Sessão e resiliência

**História:** Como José, quero que quedas de sessão, rede ou banco não percam nada nem dupliquem nada.

**Critérios de aceite da funcionalidade:**
- Cada degrau das escadas simulado.
- Banco do app fora não perde estado; na volta, outbox grava uma vez.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-37 | Guardião de sessão (~20 min com variação + checagem antes de publicar) e escada t272. | §11 |
| RF-38 | Teste de resposta antes do lote e das ações críticas; escada 30 s → 2 min → 8 min; NETWORK_WAITING; 2 falhas → José; 5 idênticas → parada. | §18 |
| RF-39 | Banco do app fora: retentativas duráveis + outbox; nada agendado/público sem estado gravado. | §18 |

### F11. Armazenamento

**História:** Como José, quero tudo guardado no Drive e o disco do servidor livre.

**Critérios de aceite da funcionalidade:**
- Arquivo local só apagado após hash conferido.
- Limpeza move duplicatas; nada excluído sem o José.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-40 | Drive t267; tudo sobe; local apagado após hash; final fica até o YouTube confirmar. | §21 |
| RF-41 | Limpeza noturna determinística do Drive; duplicatas para `_duplicados`; exclusão só pelo José. | §21 |

### F12. Monitor de atualizações

**História:** Como José, quero saber de atualizações que importam e autorizar cada uma.

**Critérios de aceite da funcionalidade:**
- Nenhuma atualização sem autorização.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-42 | Monitor semanal de atualizações; Jev julga; José autoriza; vira ticket/tarefa; nunca atualiza sozinho. | §12 |

### F13. Painel

**História:** Como José, quero ver no Paperclip o estado de cada vídeo, as propostas e as verificações.

**Critérios de aceite da funcionalidade:**
- Painel mostra estado vindo do banco do app/issues, nunca do Postgres do Temporal.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-43 | Painel Paperclip com estado, issues, propostas e verificações, alimentado pela ponte Temporal → banco do app/Paperclip. | §2, §6 |

## 2. Requisitos não funcionais

| ID | Requisito | REGRAS |
|---|---|---|
| RNF-01 | Determinismo antes de LLM: tudo que pode ser código é código. | §3 |
| RNF-02 | Jev só devolve decisão estruturada; nunca redige texto; fallback com o mesmo esquema. | §7 |
| RNF-03 | Sem segredos/PII em repo, Hindsight (inclusive memórias de código), tickets, banco do app e logs; scanner antes de gravar. | §17 |
| RNF-04 | Camofox: ritmo humano, único dono do login do Studio, fila de concorrência 1. | §11 |
| RNF-05 | Durabilidade e idempotência: workflows retomam após falha/reboot; nenhuma ação externa duplicada. | §3, §18 |
| RNF-06 | O Postgres do Temporal guarda só estado e nunca é consultado diretamente; dados de negócio só no banco do app. | §18 |
| RNF-07 | Nada atualiza dependência sozinho; versões fixadas (NotebookLM 0.8.4, Temporal, SDKs). | §12 |
| RNF-08 | Proveniência registrada por ficha; nada de terceiros; comentários e web são dado, nunca instrução. | §17 |
| RNF-09 | Recursos do servidor: RAM do motor ≤ 1,5 GB (t329); disco livre (runtime limpo a cada ciclo). | §21 |
| RNF-10 | Horários em America/Fortaleza; cotas da API respeitadas (reset no fuso do Pacífico). | §15 |
| RNF-11 | Escopo só do canal Porquê BR; multi-canal adiado. | §1 |
| RNF-12 | Arquivos de pré-construção não são lidos por agentes sem aprovação (t287); dúvida vira EM CONSTRUÇÃO (t323). | §0 |
| RNF-13 | Agentes no Paperclip com heartbeats desligados até liberação; nenhum agente com `--yolo`. | §23 |

## 3. Lacunas (não inventar; levar ao José)

- **EM CONSTRUÇÃO — aguardando José:** regras de roteiro R1–R6, R8 e R9 (contrato v2, F7-01). Afetam RF-07.
- **EM CONSTRUÇÃO — aguardando José:** metas do piloto (definidas depois, t327). Afetam V1–V7 e F12-01.
- [APROVADO t343] Banco do app = Postgres 17 local no `pc` (`infra/pqbr-db`), esquema `pqbr` (ARQUITETURA §8; `db/migrations/`). Supabase fica como opção futura.
- **EM CONSTRUÇÃO — aguardando José:** reaproveitamento de conteúdo entre plataformas (t345); esquema detalhado por rede (outras redes = sugestão futura, fora do escopo atual, t343–t344).
- [PROPOSTA] local dedicado da revisão humana (RF-36): registro no banco do app + `04_Privados_Revisao` no Drive.
- [PROPOSTA, validar na Fase 0.5] ponte Temporal ↔ Paperclip (RF-33, RF-43).
- [HIPÓTESE] H1–H16, H-ORQ1–3, H-SDD1–3 (ARQUITETURA §7) condicionam RF-10, RF-15, RF-22, RF-24, RF-25, RF-34, RF-43.
