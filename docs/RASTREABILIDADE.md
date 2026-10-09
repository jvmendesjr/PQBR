# Matriz de rastreabilidade

> Requisito → regra → desenho → tarefa → teste. Gerada a partir da mesma lista de `docs/SPEC.md`; ao mudar um ID, atualize os cinco documentos no mesmo commit.

| Requisito | REGRAS | ARQUITETURA | ROADMAP | TESTES |
|---|---|---|---|---|
| RF-01 | §3, §4 | §9 GradeDiariaWorkflow | F5-01 | TS-01 |
| RF-02 | §4 | §8 temas; §11 DecisaoRepeticao | F3-01, F5-01 | TS-01, V4 |
| RF-03 | §4 | §9 GradeDiariaWorkflow | F5-01 | TS-01 |
| RF-04 | §4 | §9 GradeDiariaWorkflow | F5-01 | TS-01 |
| RF-05 | §4 | §11 PontuacaoPolemica | F5-01 | TS-01 |
| RF-06 | §9 | §9 EpisodioWorkflow | F5-02 | TS-02 |
| RF-07 | §5 | §11 RoteiroShort | F3-01, F7-01 | TS-02, V1 |
| RF-08 | §6 | §8 visual_assets; §10 | F5-04 | TS-02, V2, V6 |
| RF-09 | §5, §9 | §9 EpisodioWorkflow (Activity render) | F5-05 | TS-02 |
| RF-10 | §9, §10 | §2 NotebookLM; §9 fila notebooklm | F4-01..F4-05 | TS-02, V7 |
| RF-11 | §8 | §9 EpisodioWorkflow (Activity auditor) | F7-02 | TS-03, V3 |
| RF-12 | §7, §8 | §11 VereditoAuditor | F7-02 | TS-03, V3 |
| RF-13 | §5, §8 | §11 VereditoAuditor | F7-02 | TS-03, V3 |
| RF-14 | §7, §8 | §11 VereditoAuditor | F7-02 | TS-03 |
| RF-15 | §15 | §9 PublicacaoWorkflow | F8-01 | TS-04, V4 |
| RF-16 | §15 | §9 PublicacaoWorkflow; §8 episodios | F8-01 | TS-04, V4 |
| RF-17 | §15 | §9 Schedules | F5-02, F8-01 | TS-04, V4 |
| RF-18 | §7, §15 | §11 DecisaoPublicacao | F8-01 | TS-04 |
| RF-19 | §16 | §9 Item5Workflow | F8-01 | TS-05, V5 |
| RF-20 | §16 | §9 Item5Workflow; §8 acoes | F8-01 | TS-05, V5 |
| RF-21 | §16 | §11 SinalItem5 | F8-01, F10-03 | TS-05 |
| RF-22 | §19 | §9 ComentariosWorkflow | F10-03 | TS-06 |
| RF-23 | §19 | §11 ClassificacaoComentario | F10-03 | TS-06 |
| RF-24 | §19 | §9 ComentariosWorkflow; §8 frases | F10-01, F10-03 | TS-06 |
| RF-25 | §19 | §9 ComentariosWorkflow (fila camofox) | F10-03 | TS-06 |
| RF-26 | §19 | §9 sinal pausar_respostas | F10-03 | TS-06 |
| RF-27 | §19 | — | F10-03 | TS-06 |
| RF-28 | §13 | §9 ComplianceWorkflow | F9-02 | TS-07 |
| RF-29 | §13 | §10 | F9-02 | TS-07 |
| RF-30 | §20 | §9 AnalistaWorkflow | F9-03 | TS-08 |
| RF-31 | §19, §20, §22 | §9 RelatorioDiarioWorkflow | F9-01 | TS-08 |
| RF-32 | §22 | §8 consumo | F9-01 | TS-08 |
| RF-33 | §3 | §10; §11 PropostaAgente | F05-04, F1-01 | TS-09, TZ-04 |
| RF-44 | §3.1 | §2 Correção autônoma | F3-05 | TS-11 |
| RF-45 | §11 | §2 Camofox; Correção autônoma | F4C-08 | TS-11 |
| RF-46 | §3.1, §7 | §2 Correção autônoma (etapas) | F3-05 | TS-11 |
| RF-47 | §22, §3.1 | §2 Consumo por modelo; migração 0010 | F3-06 | TS-08, TS-DB |
| RF-48 | §2 | §3 @pqbr-assistente | F1-03 | TS-09 |
| RF-49 | §22 | §8 Retenção do consumo | F3-07 | TS-DB, TS-08 |
| RF-34 | §2 | ADR-003; §10 | F05-06, F1-03 | TS-09, TZ-06 |
| RF-35 | §24 | ADR-004; §11 TicketManutencao | F1-04 | TS-09 |
| RF-36 | §5 | §8 revisao_humana; §9 sinal determinacao_revisao | F8-03 | TS-09 |
| RF-37 | §11 | §9 GuardiaoSessaoWorkflow | F6-01 | TS-10 |
| RF-38 | §18 | §9 RetryPolicy | F6-01 | TS-10 |
| RF-39 | §18 | ADR-001; §8 outbox | F05-03, F6-01 | TS-10, TZ-03 |
| RF-40 | §21 | §9 EpisodioWorkflow (Activity drive) | F8-02 | TS-11, V6 |
| RF-41 | §21 | §9 LimpezaDriveWorkflow | F8-02 | TS-11 |
| RF-42 | §12 | §9 MonitorAtualizacoesWorkflow | F9-01 | TS-12 |
| RF-43 | §2, §6 | ADR-002; §10 | F05-04, F1-02 | TS-13, TZ-04 |
| RNF-01 | §3 | ADR-001 | F00-01 | TS-REPLAY |
| RNF-02 | §7 | §11 decide() | F3-01, F6-01 | TS-03, TS-10 |
| RNF-03 | §17 | §11; D14 | F3-02 | TS-SEC |
| RNF-04 | §11 | §9 fila camofox | F6-01 | TS-10 |
| RNF-05 | §3, §18 | ADR-001 | F05-02 | TZ-02, TS-REPLAY |
| RNF-06 | §18 | ADR-001 | F05-03, F05-04 | TZ-03, TZ-04 |
| RNF-07 | §12 | §5 | F9-01 | TS-12 |
| RNF-08 | §17 | §8 visual_assets | F5-04 | TS-SEC, V6 |
| RNF-09 | §21 | ADR-001 | F05-01 | TZ-01 |
| RNF-10 | §15 | §2 Data API | F5-02 | TS-04 |
| RNF-11 | §1 | ADR-001 | — | — |
| RNF-12 | §0 | — | F1-01 | TS-09 |
| RNF-13 | §23 | ADR-002 | F05-05, F1-02 | TZ-05 |

Validação (REGRAS §14): V1 contrato editorial · V2 consistência visual · V3 auditor · V4 publicação sem duplicidade · V5 correção pós-publicação · V6 procedência · V7 premissas técnicas. Detalhe em `docs/TESTES.md` §3.
