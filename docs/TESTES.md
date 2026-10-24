# TESTES da PQBR (plano de testes e validação)

> Autoridade: abaixo de `docs/ARQUITETURA.md`. Cada suíte cobre requisitos do `docs/SPEC.md`; a ligação completa está em `docs/RASTREABILIDADE.md`.
> Não consultar material restrito (t287). Gabaritos que hoje estão fora do repo (`labels.json`, `decide.py` do teste de 08/10) entram em `tests/auditor/` na F7-02.

## 1. Níveis e regras gerais

| Nível | O que cobre | Onde | Quando roda |
|---|---|---|---|
| Unitário | Funções puras (grade, barreiras, pontuação, limites de resposta, templates) | `tests/unit/` | todo commit |
| Contrato | Modelos Pydantic v2 (ARQUITETURA §11): válidos, inválidos, fallback do Jev com o mesmo esquema | `tests/contratos/` | todo commit |
| Replay | Histórico do motor reproduzido contra o código novo (determinismo) | `tests/replay/` | todo commit que muda workflow |
| Integração | Activities contra serviços de **desenvolvimento** (banco do app de teste, caderno clonado, canal em privado) | `tests/integracao/` | por tarefa, com autorização |
| Simulação de falha | Rede fora, banco do app fora, `kill -9`, reboot, sessão caída | `tests/falhas/` | Fases 0.5 e 6 |
| Sombra | Fluxo completo sem efeito externo (respostas e corações simulados) | — | Fases 5 e 10 |

Regras: nenhum teste usa dados pessoais reais nem segredos (RNF-03); nenhum teste publica vídeo público sem portão do José; testes de canal usam vídeo privado.

## 2. Teste de 1 dia do Temporal ligado ao Paperclip (Fase 0.5)

| ID | Teste | Critério de aprovação | Req |
|---|---|---|---|
| TZ-01 | Subir Temporal + Postgres dedicado; medir RAM/CPU em repouso e com carga | Temporal + Postgres dedicado ≤ 1,5 GB de RAM em repouso e com carga (t329); dump/restauração ok | RNF-09 |
| TZ-02 | `EpisodioWorkflow` de brinquedo com timer e Activity que falha; `kill -9` no worker; reboot | Retoma do ponto certo; nenhuma Activity com efeito roda duas vezes | RNF-05 |
| TZ-03 | Banco do app de teste inacessível durante o workflow | Nada perdido; outbox grava uma vez na volta; nada "agendado/público" sem estado | RF-39, RNF-06 |
| TZ-04 | Temporal abre issue no Paperclip; agente de teste devolve proposta; aprovação vira sinal | Proposta valida em Pydantic v2; proposta inválida é rejeitada; nada aplicado sem aprovação; agente não acessa o Postgres do Temporal | RF-33, RF-43 |
| TZ-05 | Alternativa ao worker `hermes_local` | H-SDD1 resolvida pela alternativa de REGRAS §0; H-ORQ3 verificada por inspeção do adapter Paperclip instalado (bundle lido/injetado no prompt; asserção de teste presente, mas não executada); nenhum worker Hermes executado | RNF-13 |
| TZ-06 | Aprovação Temporal pelo Discord/Paperclip | Aprovar/negar só pela identidade vinculada do José; estado válido, fail-closed, idempotência persistente e ticket após 3 falhas | RF-34, RF-43 |
| TZ-07 | Consolidação | Relatório `docs/sdd/adr-001-orquestrador.md`; se o Temporal reprovar algum TZ, repetir TZ-01..TZ-04 com o DBOS | RNF-01 |
| TZ-08 | Menção raiz ao bot Discord no canal privado | Cria tarefa Paperclip atribuída ao Diretor; resposta na thread; usuário José vinculado; não vinculados e canais fora do allowlist rejeitados | RF-34, RF-48 |
| TZ-09 | Alertas proativos dos workflows e rotinas PQBR via Discord/Paperclip | Acessos, Camofox, compliance/HOLD, falhas, tickets e relatório diário chegam uma vez, em canal privado, sem depender de mensagem iniciadora | RF-19, RF-28, RF-31, RF-43 |
| TZ-10 | Corte Telegram e rollback | Só após TZ-06/08/09 aprovados; pausa apenas Hermes `pqbr` e emissores PQBR; rollback reativa rota sem desligar gateway compartilhado; nenhum fluxo PQBR continua enviando Telegram | RF-34, RF-43 |

| TZ-11 | NotebookLM-first e seleção do produtor de vídeo | NotebookLM fornece pesquisa/temas/roteiro/SEO; agente apenas orquestra; vídeo é gerado por Flow, nunca NotebookLM; Vids só em fallback aprovado; quotas reais/artefatos registrados; zero publicação | RF-06, RF-08, RF-09 |
**Resultados (09/10/2026; detalhes em `docs/sdd/adr-001-orquestrador.md`):**

| ID | Resultado |
|---|---|
| TZ-01 | ✅ Aprovado. Pico de 307 MiB, abaixo do teto de 1,5 GB. Dump e restauração ok. Soak encerrado em 10/10 11:57 (t374, sem esperar as 24 h): **122 execuções em ~20 h** (a cada 10 min), 0 falhas ou expiradas, 0 perdidas (`MissedCatchupWindow` 0), 0 duplicatas no outbox; pico do compose 340 MiB, worker 53 MiB, nenhuma amostra acima de 1536 MiB. |
| TZ-02 | ✅ Aprovado, com `kill -9` no worker e restart do motor. Reboot do servidor dispensado (t334). |
| TZ-03 | ✅ Aprovado, com stub; o banco do app de teste fica para a F3. |
| TZ-04 | ✅ Aprovado no Paperclip de teste `PQBR-TESTE`. |
| TZ-05 | ✅ F05-05 fechado por alternativa documentada em REGRAS §0; H-ORQ3 conferida por inspeção de `@paperclipai/hermes-paperclip-adapter` 2026.1001.0 (`supportsInstructionsBundle`, `instructionsFilePath`, injeção no prompt). Há asserção em `dist/index.test.js`, não executada porque o runner não está incluído no pacote instalado. Nenhum worker Hermes foi executado; não é um E2E desse runtime. |
| TZ-06 | ⏸ Pendente (parcial). Endpoint Discord ativo e restrito; `#pqbr` cria tarefa para o Diretor, identidade vinculada e round-trip privado concluído (`PQBR-97`). Ainda sem teste de aprovar/negar no workflow-alvo, estado válido, fail-closed, idempotência persistente ou ticket após 3 falhas. Telegram permanece ativo como rollback. Prova adicional (2026-10-15): correlação real Discord→Temporal validada sem efeito de aprovação — `wakeCommentId` = ID do Update; issue, autor vinculado, endpoint e `#pqbr` coincidiram; probe concluiu. Candidata segue isolada; revisão independente PQBR-101 concluiu parecer estático favorável à validação sem efeito, commit `9c03f61`, com 22 testes e 27 subtests aprovados. F05-06 permanece pendente para a ponte real de aprovação/negar, estado, fail-closed, idempotência durável e ticket após 3 falhas. |
| TZ-07 | ✅ Fechado (t374): RAM e estabilidade medidas no soak; motor escolhido = **Temporal**. |
| TZ-08 | ⏸ Parcial. Menção raiz em `#pqbr` criou tarefa para o Diretor e as respostas foram publicadas na thread; identidade do José vinculada. Somente `#pqbr` está habilitado; DMs e remetentes não vinculados estão bloqueados, e uma menção não vinculada foi filtrada. Falta teste negativo de canal fora do allowlist antes do aceite completo. |
| TZ-09 | ⏸ Pendente. r25 removeu o bypass de `rows`; r26 permite recuperar ticket esgotado pela facade sem sender e valida `janela_horas` como inteiro positivo. Validação: 91/91 testes no worktree, 111/111 no snapshot limpo de aae4895; scanner/whitespace limpos. Endpoint Discord ativo, mas sem sender real, sink idempotente de ticket, integração das quatro rotas ou prova privada de alertas proativos com ACK/retry/deduplicação. SQL não aplicado. |
| TZ-10 | ⏸ Pendente: não pausar Telegram antes do aceite e do rollback ensaiado. |

## 3. Os 7 itens da validação (REGRAS §14)

| ID | Item | Critério de aceite | Evidência |
|---|---|---|---|
| V1 | Contrato editorial | Contrato v2 aprovado pelo José; `RoteiroShort` coerente | F7-01 |
| V2 | Consistência visual | 3 vídeos reaproveitáveis com os mesmos personagens em situações diferentes (não bloqueia, t264) | F5-04, F11-01 |
| V3 | Auditor com defeitos conhecidos | Falso aprovado e falso reprovado medidos no gabarito ampliado (labels.json + vídeos novos); CTA ausente, fala cortada, nome, pedido de comentário detectados | F7-02 |
| V4 | Publicação sem duplicidade | Upload interrompido sem duplicata; horário perdido usa reserva ou cancela; reprovado nunca publicado | F8-01 |
| V5 | Correção pós-publicação | Sinal → privado + aviso pelo canal privado ativo; volta só com toque; exclusão só pelo José | F8-01 |
| V6 | Procedência e proteção | Ficha com origem registrada; scanner bloqueia segredo; comentários tratados como dado | F5-04, F3-02, F8-02 |
| V7 | Premissas técnicas | H1–H16, H-ORQ, H-SDD com status VERIFICADO ou com alternativa aprovada | todas |

Prioridade: V1, V2 e V3. Metas do piloto: EM CONSTRUÇÃO — aguardando José (t327).

## 4. Suítes por funcionalidade

| ID | Funcionalidade | Casos mínimos |
|---|---|---|
| TS-01 | Grade e temas (RF-01..RF-05) | Grade do dia D só depende de D; reproduzir o incidente de 08/10 (grade do dia 7; 3 de 4 repetidos) e barrar; variação próxima de tema publicado barrada; sugestão repetida do José recusada com aviso; polêmica > 75 retida; bloqueio absoluto; mistura 70/30 |
| TS-02 | Roteiro e produção (RF-06..RF-10) | `RoteiroShort` aceita 15 s–3 min e rejeita fora; exige campo `tipo_cta` válido; aceita CTA contextual dos tipos `trocadilho_tema`/`convite_seguir`; fallback exige `Segue o Porquê BR`; rejeita tipo/fallback incompatível e pedido de comentário; nomes rejeitados; revisão humana verifica pertinência contextual sem bloqueio automático pelas diretrizes R1–R4/R6/R8/R9 (R5 é alerta não bloqueante); nenhuma chamada ao caderno raiz; consumo gravado antes/depois; > 80% espaça; end card só cortado se detectado; F7-03: `tests/unit/test_f7_03_limits.py` (bloco obrigatório; cap local simulado e janelas oficiais mockadas, separados) |
| TS-03 | Auditor (RF-11..RF-14) | Gabarito labels.json; 2 rodadas divergentes → 3ª rodada desempata (t357); 3ª falha → revisão; estilo visual e imagem×fala não reprovam; relatório só por template; testes locais em `tests/unit/test_auditor_visual.py`, `test_capa_a9.py`, `test_auditor_gemini.py` e `test_auditor_texto.py` (A9, schema/IDs, persistência controlada, estilo/personagem não avaliados quando o bloco visual é omitido e decisão LOOP). |
| TS-04 | Publicação (RF-15..RF-18) | Busca do código em privados/agendados; 1 tentativa sem confirmação e para; teto 4/dia; reserva ≥ 2; agendado × aprovado |
| TS-05 | Item 5 (RF-19..RF-21) | Cada fonte de sinal torna privado; limiar 2 pessoas / 1 grave; abaixo vai ao José; nunca republica |
| TS-06 | Comunidade (RF-22..RF-27) | Cadência de leitura; retenção só nos casos aprovados; limites de resposta (6/h, 30/dia, 08–22h, 1 por pessoa por vídeo, ~24 h); casos graves desligam e escalam com tom formal; kill switch manual; sombra |
| TS-07 | Conformidade (RF-28, RF-29) | E-mail crítico simulado → HOLD + privados os agendados + aviso pelo canal privado ativo + ticket; recurso não é enviado pelo agente |
| TS-08 | Analista e relatórios (RF-30..RF-32, RF-47) | Consumo por modelo e por tipo de ação no relatório diário a partir de `consumo_diario` (sem teto, só números); Relatório por template; exceções sinalizadas; aviso quando a amostra não é estatisticamente significativa; custos somados |
| TS-09 | Agentes e manutenção (RF-33..RF-36; RNF-12 complementado por TS-GOV-01/02) | Proposta inválida rejeitada; nada aplicado sem aprovação; ordem de outro ID ignorada; ticket com 2 aprovações; revisão humana com as 4 determinações |
| TS-11 | Correção autônoma (RF-44, RF-45, RF-46) | até 3 tentativas, salvo parada imediata; em relógio simulado, intervalo sorteado entre 5 e 15 min do término de uma intervenção ao início da próxima na mesma sessão (não duração/timeout nem pausa entre cliques); waits por condição não liberam ação antes de prontidão, e timeout interrompe sem inventar sucesso; `Retry-After` maior que 15 min não é truncado; CAPTCHA/bloqueio/consentimento necessário interrompem sem bypass; exceção técnica encerra a operação falha, sem retry/fallback automático nem reexecução; sessão ou conta Google diferente da esperada → para e chama o José; corações: anúncio/aviso novo capturado e classificado pelo Jev; envio sem confirmação: busca do código no Studio antes de parar; escada corrigível: esgotamento após a 3ª falha verificada, sem suprimir chamadas imediatas por trava sensível ou exceção técnica; Seletor mudado em página de teste → agente corrige pela Activity e abre proposta; 3 tentativas esgotadas → José avisado com o histórico; pedido de login, exclusão, tornar público ou publicar reprovado → `Sensivel` sem executar; duas intervenções na mesma sessão rodam em série; cada ação registrada sem segredo; o Jev faz a triagem (caso sensível nunca chega ao agente) e a verificação (correção que não passa na verificação conta como tentativa falha); o aprendizado aparece no bank Hindsight da PQBR, sem segredo (RF-46); validação local parcial em 17/10/2026: 26 testes em memória, regressão 216/216, sem comprovação de runtime/integração ([evidência](sdd/f3-05-local-20261017.md)) |
| TS-12 | Retenção do consumo (RF-49) | Prazos t369 (brutos 90 dias, resumo 25 meses) simulados com datas antigas: linha de 91 dias sai e de 89 fica; resumo de 26 meses sai e de 24 fica; dias antigos são agregados no resumo e as somas batem antes de apagar; rodar 2× não duplica nem apaga a mais; conferência falha → nada é apagado e o José é avisado; `pqbr_app` continua sem DELETE; execução registrada em `acoes` |
| TS-10 | Resiliência (RF-37..RF-39) | Cada degrau das escadas; NETWORK_WAITING não gasta tentativa; 2 falhas → correção autônoma, José só após a 3ª tentativa falha (t357); 5 idênticas → parada; banco do app fora |
| TS-ARM | Armazenamento (RF-40, RF-41) | Apaga local só após hash; duplicata movida; nada excluído |
| TS-MON | Monitores (RF-42, RNF-07) | Atualização relevante pede autorização; nada atualiza sozinho |
| TS-13 | Painel (RF-43) | Estado exibido vem do banco do app/issues |
| TS-DB | Migrações (RF-02, RNF-02, RNF-03) | `sh db/test_migrations.sh`: sobe/desce 2 vezes; R10, código PQBR-EP, `video_id` obrigatório, janelas, 1 resposta por pessoa por vídeo, outbox idempotente, revisão coerente; anon/authenticated sem acesso; FKs indexadas. ✅ 09/10 | Banco local (t343): `infra/pqbr-db/verificar.sh` ok (RLS, papéis, senha errada recusada, leitura sem texto bruto, sem escrita em `public`); `testar_restauracao.sh` ok (24/60/1 iguais).
| TS-SEC | Segredos/PII (RNF-03, RNF-08) | Segredo e PII de teste bloqueados em Hindsight, tickets, banco do app, logs e pre-commit | Validado localmente em 17/10/2026: Hindsight, API/CLI de tickets, banco via conexão/cursor/SQL direto/lotes, logging com exceções/extras, stdout e hook em índice descartável. Regressão de segurança + unitários + kit: **190 passed**. Histórico de 09/10: biblioteca e commit com token/e-mail falsos bloqueados. Nesta rodada nenhum commit foi criado; nenhum serviço real foi chamado. [Evidência e comando](sdd/f3-02-ts-sec-20261017.md).
| TS-REPLAY | Determinismo (RNF-01, RNF-05) | Replay de históricos gravados passa após cada mudança de workflow |

### Cobertura transversal de governança — apenas especificada nesta revisão

| ID | Requisitos | Critério de aceite e limites |
|---|---|---|
| TS-GOV-01 | RNF-11, RNF-12 | Revisão documental na ordem canônica e matriz: escopo somente Porquê BR, multi-canal adiado, restrições de leitura e tratamento de dúvida explícitos, sem vínculo ausente ou implementação presumida. Cobertura documental não comprova bloqueio técnico. Aceite final em F00-01/G0. |
| TS-GOV-02 | RNF-12 | Onde existir controle técnico de leitura seguro e verificável, caso negativo isolado com caminhos/conteúdos sintéticos representando material restrito: pedido sem aprovação não retorna conteúdo e registra a recusa sem vazar o dado. Não consultar material real restrito. Se o controle não existir ou não permitir teste seguro, registrar lacuna e critério documental em F00-01, sem afirmar proteção implementada. |

**Estado desta revisão (17/10/2026):** os novos critérios de TS-11 e TS-GOV-01/02 são especificações, não resultados de execução. Nenhum teste automatizado foi implementado ou executado, nenhum serviço acionado e nenhum gate fechado. A inspeção documental não demonstra implementação do pacing ou de uma barreira técnica RNF-12; implementação/validação permanecem pendentes. TS-11 identifica somente correção autônoma, TS-12 somente retenção do consumo; armazenamento = TS-ARM e monitores = TS-MON. Os resultados históricos abaixo foram preservados, sem extensão de sua cobertura aos novos critérios.

## Resultados de 10/10/2026 (t376)
- Unitários (`PYTHONPATH=src python -m unittest discover -s tests/unit -t .`): contratos 10/10, barreira 7/7, grade 7/7 (inclui o incidente de 08/10 e a mistura configurável de t378).
- Workflows no ambiente de teste do Temporal (`tests/workflows`, tempo acelerado): TS-11 correção autônoma 6/6 (1ª e 3ª tentativa, verificação reprovada esgota, sensível sem agente, conta divergente, sem backend não executa); TS-12 retenção 1/1 + seção do relatório 1/1; F5-02 6/6 (grade do dia sem repetidos, agendado, reprovado nunca publica, vigia de prazo com e sem reserva, polêmica espera o José, sem simulação nada é chamado). Total 14/14.
- TS-12 em banco descartável (`db/test_migrations.sh`): agrega 2/3/1/15, apaga 3 brutas e 1 resumo de 26 meses, 2ª execução não muda nada, `pqbr_app` não executa, `pqbr_manutencao` não apaga `acoes`; ciclo UP/DOWN ok.
- Real: 0011 aplicada; `registrar_consumo` gravou 1 linha de verificação; `RetencaoConsumoWorkflow` executado (0 a apagar).
