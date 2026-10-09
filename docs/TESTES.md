# TESTES da PQBR (plano de testes e validação)

> Autoridade: abaixo de `docs/ARQUITETURA.md`. Cada suíte cobre requisitos do `docs/SPEC.md`; a ligação completa está em `docs/RASTREABILIDADE.md`.
> Não consultar material restrito (t287). Gabaritos que hoje estão fora do repo (`labels.json`, `decide.py` do teste de 08/10) entram em `tests/auditor/` na F7-02.

## 1. Níveis e regras gerais

| Nível | O que cobre | Onde | Quando roda |
|---|---|---|---|
| Unitário | Funções puras (grade, barreiras, pontuação, limites de resposta, templates) | `tests/unit/` | todo commit |
| Contrato | Modelos Pydantic v2 (ARQUITETURA §11): válidos, inválidos, fallback do Jev com o mesmo esquema | `tests/contratos/` | todo commit |
| Replay | Histórico do motor reproduzido contra o código novo (determinismo) | `tests/replay/` | todo commit que muda workflow |
| Integração | Activities contra serviços de **desenvolvimento** (Supabase dev, caderno clonado, canal em privado) | `tests/integracao/` | por tarefa, com autorização |
| Simulação de falha | Rede fora, Supabase fora, `kill -9`, reboot, sessão caída | `tests/falhas/` | Fases 0.5 e 6 |
| Sombra | Fluxo completo sem efeito externo (respostas e corações simulados) | — | Fases 5 e 10 |

Regras: nenhum teste usa dados pessoais reais nem segredos (RNF-03); nenhum teste publica vídeo público sem portão do José; testes de canal usam vídeo privado.

## 2. Teste de 1 dia do Temporal ligado ao Paperclip (Fase 0.5)

| ID | Teste | Critério de aprovação | Req |
|---|---|---|---|
| TZ-01 | Subir Temporal + Postgres dedicado; medir RAM/CPU em repouso e com carga | Dentro do limite combinado (EM CONSTRUÇÃO — aguardando José o valor); dump/restauração ok | RNF-09 |
| TZ-02 | `EpisodioWorkflow` de brinquedo com timer e Activity que falha; `kill -9` no worker; reboot | Retoma do ponto certo; nenhuma Activity com efeito roda duas vezes | RNF-05 |
| TZ-03 | Supabase dev inacessível durante o workflow | Nada perdido; outbox grava uma vez na volta; nada "agendado/público" sem estado | RF-39, RNF-06 |
| TZ-04 | Temporal abre issue no Paperclip; agente de teste devolve proposta; aprovação vira sinal | Proposta valida em Pydantic v2; proposta inválida é rejeitada; nada aplicado sem aprovação; agente não acessa o Postgres do Temporal | RF-33, RF-43 |
| TZ-05 | Agente Hermes no Paperclip | Roda sem `--yolo`; heartbeats desligados; versão com a correção da #3833 | RNF-13 |
| TZ-06 | Aprovação pelo Telegram (Hermes `pqbr`) | Aprovar/negar chega como sinal; mensagem de outro ID ignorada | RF-34 |
| TZ-07 | Consolidação | Relatório `docs/sdd/adr-001-orquestrador.md`; se o Temporal reprovar algum TZ, repetir TZ-01..TZ-04 com o DBOS | RNF-01 |

## 3. Os 7 itens da validação (REGRAS §14)

| ID | Item | Critério de aceite | Evidência |
|---|---|---|---|
| V1 | Contrato editorial | Contrato v2 aprovado pelo José; `RoteiroShort` coerente | F7-01 |
| V2 | Consistência visual | 3 vídeos reaproveitáveis com os mesmos personagens em situações diferentes (não bloqueia, t264) | F5-04, F11-01 |
| V3 | Auditor com defeitos conhecidos | Falso aprovado e falso reprovado medidos no gabarito ampliado (labels.json + vídeos novos); CTA ausente, fala cortada, nome, pedido de comentário detectados | F7-02 |
| V4 | Publicação sem duplicidade | Upload interrompido sem duplicata; horário perdido usa reserva ou cancela; reprovado nunca publicado | F8-01 |
| V5 | Correção pós-publicação | Sinal → privado + Telegram; volta só com toque; exclusão só pelo José | F8-01 |
| V6 | Procedência e proteção | Ficha com origem registrada; scanner bloqueia segredo; comentários tratados como dado | F5-04, F3-02, F8-02 |
| V7 | Premissas técnicas | H1–H16, H-ORQ, H-SDD com status VERIFICADO ou com alternativa aprovada | todas |

Prioridade: V1, V2 e V3. Metas do piloto: EM CONSTRUÇÃO — aguardando José (t327).

## 4. Suítes por funcionalidade

| ID | Funcionalidade | Casos mínimos |
|---|---|---|
| TS-01 | Grade e temas (RF-01..RF-05) | Grade do dia D só depende de D; reproduzir o incidente de 08/10 (grade do dia 7; 3 de 4 repetidos) e barrar; variação próxima de tema publicado barrada; sugestão repetida do José recusada com aviso; polêmica > 75 retida; bloqueio absoluto; mistura 70/30 |
| TS-02 | Roteiro e produção (RF-06..RF-10) | `RoteiroShort` aceita 15 s–3 min e rejeita fora; CTA diferente de "Segue o Porquê BR" rejeitado; pedido de comentário rejeitado; nomes rejeitados; nenhuma chamada ao caderno raiz; consumo gravado antes/depois; > 80% espaça; end card só cortado se detectado |
| TS-03 | Auditor (RF-11..RF-14) | Gabarito labels.json; 2 rodadas divergentes → revisão; estilo visual e imagem×fala não reprovam; relatório só por template |
| TS-04 | Publicação (RF-15..RF-18) | Busca do código em privados/agendados; 1 tentativa sem confirmação e para; teto 4/dia; reserva ≥ 2; agendado × aprovado |
| TS-05 | Item 5 (RF-19..RF-21) | Cada fonte de sinal torna privado; limiar 2 pessoas / 1 grave; abaixo vai ao José; nunca republica |
| TS-06 | Comunidade (RF-22..RF-27) | Cadência de leitura; retenção só nos casos aprovados; limites de resposta (6/h, 30/dia, 08–22h, 1 por pessoa por vídeo, ~24 h); casos graves desligam e escalam com tom formal; kill switch manual; sombra |
| TS-07 | Conformidade (RF-28, RF-29) | E-mail crítico simulado → HOLD + privados os agendados + Telegram + ticket; recurso não é enviado pelo agente |
| TS-08 | Analista e relatórios (RF-30..RF-32) | Relatório por template; exceções sinalizadas; aviso quando a amostra não é estatisticamente significativa; custos somados |
| TS-09 | Agentes e manutenção (RF-33..RF-36, RNF-12) | Proposta inválida rejeitada; nada aplicado sem aprovação; ordem de outro ID ignorada; ticket com 2 aprovações; revisão humana com as 4 determinações |
| TS-10 | Resiliência (RF-37..RF-39) | Cada degrau das escadas; NETWORK_WAITING não gasta tentativa; 2 falhas → José; 5 idênticas → parada; Supabase fora |
| TS-11 | Armazenamento (RF-40, RF-41) | Apaga local só após hash; duplicata movida; nada excluído |
| TS-12 | Monitores (RF-42, RNF-07) | Atualização relevante pede autorização; nada atualiza sozinho |
| TS-13 | Painel (RF-43) | Estado exibido vem do Supabase/issues |
| TS-SEC | Segredos/PII (RNF-03, RNF-08) | Segredo e PII de teste bloqueados em Hindsight, tickets, Supabase, logs e pre-commit |
| TS-REPLAY | Determinismo (RNF-01, RNF-05) | Replay de históricos gravados passa após cada mudança de workflow |
