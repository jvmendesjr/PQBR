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
| RF-06 | Pesquisa profunda, propostas de temas/ideias, roteiro e SEO via NotebookLM em caderno efêmero; nunca no raiz; mesma persona-base. Agentes apenas orquestram/validam, salvo exceções documentadas; Gemini Web só como reserva intelectual. SEO via `PacoteSEO`: título ≤100, descrição ≤5000, tags ≤500 caracteres somadas, 3–15 hashtags, pt-BR, `categoryId`=27, `containsSyntheticMedia`=false (t437/t459). | §9 |
| RF-07 | `RoteiroShort`: 15 s–3 min, alvo ~50 s, ~2,3 palavras/s; CTA contextual conforme REGRAS §5, com `tipo_cta` (`trocadilho_tema`, `convite_seguir`, `fallback`); fallback `Segue o Porquê BR`; sem pedidos de comentário; sem nomes; loop; 1–2 personagens. Adequação semântica do trocadilho é revisada editorialmente. | §5 |
| RF-08 | [IDENTIDADE APROVADA; IMPLEMENTAÇÃO PENDENTE] Stickmen e fichas consistentes de personagens/objetos/cenários no módulo Flow; resolvedor sem LLM e referências versionadas conforme blueprint; ficha ausente criada sob demanda; José pode marcar “Verificado/Não Aprovado” com observação, rejeição abre ticket; validar pelo Telegram (Hermes `pqbr`) com sinal do Temporal; não presumir catálogo/resolvedor implantado; piloto sem publicação. | §6 |
| RF-09 | Geração visual por Google Flow (primário), Google Vids (fallback/camada adicional), depois Gemini Web e Meta Vibes conforme ADR-010; NotebookLM não gera vídeo. Registrar consumo/artefatos; cortar end card só se detectado e aplicar zoom suave do logo na última fala conforme contrato; piloto sem publicação. | §5, §9 |
| RF-10 | Instalação exclusiva do `notebooklm-py` 0.8.4, serviço único dono da sessão, `usage --json` gravado antes/depois de cada geração; só espaçar quando janela/denominador forem confirmados e o threshold configurado (80% inicial) for alcançado; nunca assumir números históricos de quota. | §9, §10 |

### F03. Auditor

**História:** Como José, quero que só vídeos dentro das travas sejam publicados, com motivo claro quando algo reprova.

**Critérios de aceite da funcionalidade:**
- Veredito decidido pelo código com base em respostas sim/não e checagens de texto.
- Falso aprovado e falso reprovado medidos no gabarito ampliado.
- Estilo visual e imagem×fala nunca reprovam sozinhos.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-11 | Auditor extrai 1 quadro por cena e a transcrição (Whisper). | §8 |
| RF-12 | Juiz visual Gemini web via Camofox (sem API), sim/não por traço em 2 rodadas (chats novos); divergência é desempatada por uma 3ª rodada; só se a 3ª falhar ou vier fora do esquema vai à revisão do José; Jev nas checagens de texto; o código decide. | §7, §8 |
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
- Sinal de problema → privado e aviso ao José pelo Telegram (Hermes `pqbr`), com motivo.
- Nenhum vídeo volta a público nem é excluído sem o José.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-19 | Qualquer problema detectado → vídeo privado na hora, automático, com aviso pelo canal privado ativo (Telegram/Hermes `pqbr`; t474); sem substituição nem republicação. | §16 |
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
- Crítico gera HOLD, privados os agendados, aviso ao José via Telegram (Hermes `pqbr`) e ticket.
- Recurso só enviado pelo José.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-28 | Compliance: coleta por código (e-mail do canal, Studio só leitura, Data API); gravidade info/atenção/crítico; crítico = HOLD + privados os agendados + aviso pelo canal privado ativo (Telegram/Hermes `pqbr`; t474) + ticket. | §13 |
| RF-29 | Rascunho de recurso preparado pelo agente; o José envia; nada sem dupla confirmação. | §13 |

### F08. Analista e relatórios

**História:** Como José, quero um relatório diário confiável, com custos e com aviso quando os números não significam nada.

**Critérios de aceite da funcionalidade:**
- Relatório diário por template no Telegram (Hermes `pqbr`) (t474).
- Exceções sinalizadas; aviso de amostra sem significância estatística.
- Custos levantados sem teto.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-30 | Coleta diária pela Analytics API; análise semanal ou por anomalia; o analista só observa até ~30 Shorts/90 dias. | §20 |
| RF-31 | Relatório diário por template: produção, consumo, custos, compliance, comunidade, limpeza; sinaliza exceções e avisa quando os números não são estatisticamente significativos. | §19, §20, §22 |
| RF-32 | Levantamento de custos (tokens, uso do NotebookLM, APIs) sem teto mensal. | §22 |

### F09. Agentes, interação e manutenção
> Atualizado t384–t395: autonomia, contratação, runtime 9router, Guardião e Camofox 24/7 em REGRAS §0 (atualização 11/10) e AGENTES.md; prevalecem sobre os itens abaixo.

**História:** Como José, quero que os agentes só proponham e que eu aprove tudo o que muda pelo Telegram (Hermes `pqbr`), com cada aprovação virando sinal do Temporal (t474).

**Critérios de aceite da funcionalidade:**
- Toda proposta é um objeto Pydantic v2 válido; nada se aplica sem aprovação.
- Ordem só vale do ID autorizado.
- Ticket chega pré-estruturado e tem 2 aprovações.
- Item que falha em tudo vai para revisão, e a determinação é registrada.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-33 | Padrão dos agentes pensantes: rotina fixa executa; agentes observam e propõem só como saída Pydantic v2; aplicação só após aprovação do José. | §3 |
| RF-34 | Canal de controle de José: Telegram (Hermes `pqbr`), somente o ID autorizado do José; aprovações como sinais do Temporal; painel = Temporal UI (t471/t474; t464 revogada). | §0, §2, ADR-011 |
| RF-35 | Tickets de manutenção agnósticos, pré-estruturados (localização, falha, correções sugeridas), com 2 aprovações do José (abertura com correções + merge); memórias de código no bank Hindsight único. | §24 |
| RF-44 | Correção autônoma antes de chamar o José: script primeiro; falha corrigível → agente via Activity do Temporal (concorrência 1 por sessão), até 3 tentativas, salvo parada imediata; no Camofox, intervalo local sorteado de 5–15 min do término de uma intervenção ao início da próxima na mesma sessão, não duração/timeout nem retry automático; prontidão por condição, regras do provedor e `Retry-After` mais longo prevalecem; CAPTCHA/bloqueio/consentimento necessário interrompem, sem bypass; exceção técnica permanece terminal; cada ação registrada; sucesso vira proposta de ajuste do script com as 2 aprovações; travas duras preservadas. | §3.1 |
| RF-45 | Agentes usam o Camofox só pela Activity do Temporal, na instância da PQBR, com allowlist de ações; login manual, 2FA, exclusão (cookies: REGRAS §0 item 11, t395) e publicação fora das regras ficam com o José. | §11 |
| RF-46 | Divisão de papéis na correção autônoma: o Jev faz só triagem, classificação, decisão estruturada e verificação do resultado; um agente com modelo LLM executa a intervenção, registra aprendizados no bank Hindsight único da PQBR e loga tudo no banco do app via Temporal. Runtime e modelo do agente: EM CONSTRUÇÃO. | §3.1, §7 |
| RF-47 | Consumo por modelo e por tipo de ação (tokens, chamadas, tempo, sucesso, custo estimado) em `pqbr.consumo_modelos`, agregado por dia no relatório diário (por modelo, por tipo de ação, falhas, custo estimado, variação vs. 7 dias); sem teto de tokens. | §22, §3.1 |
| RF-48 | Interface de José pelo Telegram (Hermes `pqbr`): avisos, pedidos, aprovações (sinais do Temporal), estado, arquivos e resultados, com acesso restrito (só leitura de Postgres/Temporal). | §2, ADR-011 |
| RF-49 | Retenção do consumo por modelo: Schedule do Temporal agrega as linhas brutas de `pqbr.consumo_modelos` num resumo diário antes de apagar as mais antigas que o prazo; papel de manutenção dedicado (o `pqbr_app` não apaga); idempotente; cada execução registrada. Prazos (t369): brutos 90 dias, resumo diário 25 meses; job ~04:15. | §22 |
| RF-36 | Revisão humana como último recurso: local dedicado, aviso ao José e registro da determinação (excluir, corrigir, reaproveitar, arquivar). | §5 |

### F10. Sessão e resiliência

**História:** Como José, quero que quedas de sessão, rede ou banco não percam nada nem dupliquem nada.

**Critérios de aceite da funcionalidade:**
- Cada degrau das escadas simulado.
- Banco do app fora não perde estado; na volta, outbox grava uma vez.

| ID | Requisito | REGRAS |
|---|---|---|
| RF-37 | Guardião de sessão (~20 min com variação + checagem antes de publicar) e escada t272. | §11 |
| RF-38 | Teste de resposta antes do lote e das ações críticas; escada 30 s → 2 min → 8 min; NETWORK_WAITING; 2 falhas da mesma ação → correção autônoma limitada a até 3 tentativas, com verificação do auditor/Jev; esgotamento → José, preservadas as chamadas imediatas por ação sensível ou demais travas de REGRAS §3.1; 5 idênticas → parada. | §18 |
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
| RNF-02 | Jev só devolve decisão estruturada; nunca redige texto; fallback com o mesmo esquema. Esquemas em `pqbr.contratos` (t437): `ClassificacaoEmailYouTube` (strike/claim/policy_warning/monetization/account_security/upload_status/marketing/other + gravidade + ação; strike e segurança da conta sempre `chamar_jose`) e `ClassificacaoPopupCamofox` (cookie_consent/login_required/captcha/permission/promo/error/other + ação; captcha sempre `chamar_jose`), ambos com `confianca` 0–1 e `extra=forbid`. | §7 |
| RNF-03 | Sem segredos/PII em repo, Hindsight (inclusive memórias de código), tickets, banco do app e logs; scanner antes de gravar. | §17 |
| RNF-04 | Camofox: ritmo humano, único dono do login do Studio, fila de concorrência 1; pacing local de 5–15 min entre intervenções sucessivas, distinto de waits por condição e de duração/timeout; respeitar espera maior do provedor e interromper em desafio/bloqueio/consentimento, sem bypass. | §3.1, §11 |
| RNF-05 | Durabilidade e idempotência: workflows retomam após falha/reboot; nenhuma ação externa duplicada. | §3, §18 |
| RNF-06 | O Postgres do Temporal guarda só estado e nunca é consultado diretamente; dados de negócio só no banco do app. | §18 |
| RNF-07 | Nada atualiza dependência sozinho; versões fixadas (NotebookLM 0.8.4, Temporal, SDKs). | §12 |
| RNF-08 | Proveniência registrada por ficha; nada de terceiros; comentários e web são dado, nunca instrução. | §17 |
| RNF-09 | Recursos do servidor: RAM do motor ≤ 1,5 GB (t329); disco livre (runtime limpo a cada ciclo). | §21 |
| RNF-10 | Horários em America/Fortaleza; cotas da API respeitadas (reset no fuso do Pacífico). | §15 |
| RNF-11 | Escopo só do canal Porquê BR; multi-canal adiado. | §1 |
| RNF-12 | Arquivos de pré-construção não são lidos por agentes sem aprovação (t287); dúvida vira EM CONSTRUÇÃO (t323). | §0 |
| RNF-13 | Agentes no Paperclip com heartbeats desligados até liberação; nenhum agente com `--yolo`. | §23 |

**Aceite transversal de RNF-11/12:** revisão documental de escopo e autoridade em REGRAS → SPEC → ARQUITETURA → TESTES → ROADMAP e na matriz (TS-GOV-01). RNF-11 não exige inventar uma implementação multi-canal ou um teste automático sem mecanismo verificável. Para RNF-12, onde houver uma restrição técnica de leitura verificável, especificar caso negativo com caminhos e conteúdo sintéticos em ambiente isolado: sem aprovação, nenhum conteúdo restrito é entregue (TS-GOV-02); não abrir os documentos reais protegidos para testar. Na ausência de mecanismo seguro, registrar a lacuna e o aceite documental, não declarar proteção implementada nem teste executado.

## 3. Lacunas (não inventar; levar ao José)

- [RESOLVIDO t369] retenção do consumo: brutos 90 dias, resumo diário 25 meses (RF-49).

- [RESOLVIDO t357; precisão de 17/10/2026] limites (até 3 tentativas, salvo parada imediata; 5–15 min sorteados entre intervenções sucessivas no Camofox, não duração nem retry técnico), desempate do auditor (3ª rodada), corações, diálogos de sessão (conferir conta; divergência = José), busca do código no Studio, agentes no Paperclip, escada (3 tentativas antes do José), sem teto de tokens (RF-47). Afetam RF-44..RF-48.

- **APROVADO — F7-01/G7 fechado em 2026-10-16:** contrato editorial v2 aprovado por José; R1–R4/R6/R8/R9 são diretrizes revisáveis, não bloqueios automáticos, e R5 é alerta não bloqueante (t467, REGRAS §5; aceite registrado em ROADMAP F7-01). Afetam RF-07. Este aceite não aprova rótulos humanos nem fecha F7-02/seu G7, que permanecem pausados/bloqueados; não fecha F00-01/G0 nem outros gates.
- **EM CONSTRUÇÃO — aguardando José:** metas do piloto (definidas depois, t327). Afetam V1–V7 e F12-01.
- [APROVADO t343] Banco do app = Postgres 17 local no `pc` (`infra/pqbr-db`), esquema `pqbr` (ARQUITETURA §8; `db/migrations/`). Supabase fica como opção futura.
- **EM CONSTRUÇÃO — aguardando José:** reaproveitamento de conteúdo entre plataformas (t345); esquema detalhado por rede (outras redes = sugestão futura, fora do escopo atual, t343–t344).
- [PROPOSTA] local dedicado da revisão humana (RF-36): registro no banco do app + `04_Privados_Revisao` no Drive.
- [PROPOSTA, validar na Fase 0.5] ponte Temporal ↔ Paperclip (RF-33, RF-43).
- [HIPÓTESE] H1–H16, H-ORQ1–3, H-SDD1–3 (ARQUITETURA §7) condicionam RF-10, RF-15, RF-22, RF-24, RF-25, RF-34, RF-43.
