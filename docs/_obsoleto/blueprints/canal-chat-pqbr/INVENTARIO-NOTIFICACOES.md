# Inventário de notificações operacionais — migração para Discord/Paperclip

Data de referência: 15/10/2026 09:00 (Fortaleza)
> **Tipo:** inventário estático/snapshot, não status operacional em tempo real. Atualização de navegação em 16/10/2026: o Discord já responde no canal `#pqbr`, mas F05-08/TZ-09 continua aberto porque não há prova de transporte proativo durável integrado a todas as rotas. Confira o estado atual em `docs/ROADMAP.md`.
Escopo: inventário estático do código e dos resultados registrados nos tickets PQBA-87/PQBA-89; nenhuma configuração de canal, serviço ou credencial foi alterada.

## Resumo executivo

A migração cobre mais do que trocar o destino de uma mensagem. Há quatro grupos de avisos: pedidos de acesso e eventos de sessão; decisões de aprovação de workflows Temporal; incidentes de compliance/pós-publicação; relatórios operacionais e de consumo. O inventário do Dev Corretor foi concluído em PQBA-87. Um primeiro recorte de código, PQBA-89, extraiu a formatação dos pedidos de acesso sem mudar o transporte, a agenda ou o comportamento de envio. Validação: 4 testes próprios; 49/49 na suíte do worktree Dev; depois 69/69 ao reaplicar o recorte em um worktree temporário limpo do HEAD 85e3060 e executar pytest.

Isso não fecha F05-08 nem prova que o Discord consegue enviar avisos proativos. O recorte permanece não commitado no worktree isolado do Dev e ainda precisa de revisão antes de qualquer integração. Telegram continua sendo a rota ativa durante a transição; não deve ser pausado até TZ-06, TZ-08, TZ-09 e o rollback TZ-10 estarem aceitos.

## Revisão independente de PQBA-91 — 15/10/2026 09:00

A primeira versão foi aplicada somente em worktree temporário sobre o HEAD oficial 96579e5. A suíte indicada executou 85 testes: 84 passaram e 1 falhou porque o teste de `main(sender=...)` mockava `conectar`, enquanto `main()` prefere `pacote._banco()` e acabou tentando ler `PQBR_APP_PASSWORD`. Nenhuma credencial foi adicionada. Também bloqueiam a aceitação: a migration candidata `0012_pqbr_notificacoes_operacionais.sql` colide com a migration oficial `0012_pqbr_temas_fila.sql`; a tabela usa FORCE RLS e concede a `pqbr_app` sem criar policy correspondente; e o dispatcher não lê nem grava a `notificacoes_outbox`, portanto o ACK não é durável. A tarefa foi devolvida ao Dev para renumerar a migration como 0017, alinhar o rollback, corrigir policy e injetar o estado durável no dispatcher, com teste de falha após envio/antes do commit. O SQL não foi aplicado, a rota ativa não foi alterada e nenhum código foi mesclado.

## Rotas e estado observado

| Grupo | Origem e gatilho identificados | Destino/payload atual ou previsto | Estado e gate |
|---|---|---|---|
| Acesso e sessão | `src/pqbr/workflows/acesso.py` produz pedidos/avisos; `src/pqbr/workflows/pedidos_telegram.py` consulta `pqbr.revisao_humana`. O inventário aponta o Schedule Temporal `pqbr-acessos` de hora em hora e o cron Hermes `pqbr-pedidos-jose` a cada 10 minutos. | Telegram durante a migração; Discord/Paperclip após F05-08/F05-09. Itens carregam referência, ação e motivo; há deduplicação por `item_ref` e o campo `avisado_em`. | PQBA-89 extrai somente o formatador. A entrega, confirmação e semântica de retry continuam sem prova de ponta a ponta; F05-08/TZ-09.
| Aprovação Temporal | Despachante legado `src/pqbr/integrations/telegram_aprovacao.py`; evento normalizado contém update, usuário, workflow e decisão. | A arquitetura aprovada prevê interação autenticada no Discord/Paperclip e sinal ao workflow Temporal. | O protótipo anterior não foi aprovado para merge: idempotência em memória e falta de ticket após três falhas. A substituição e seus testes pertencem a F05-06/TZ-06; não tratar a ponte antiga como concluída.
| Compliance, falhas críticas e Item 5 | RF-19, RF-28 e os workflows de publicação/compliance definem avisos após privação de vídeo, HOLD e incidentes. | Ticket Paperclip e aviso privado pelo canal ativo; Discord/Paperclip é o destino depois da migração. | O inventário identificou o contrato, mas não comprovou um emissor proativo Discord em produção; F05-08/TZ-09.
| Relatórios e consumo | Relatório diário e rotinas de consumo/retensão em `scripts/temporal/schedules.py` e F08/RF-31. | Issue/comentário Paperclip ou canal privado Discord, conforme o contrato aprovado. | Rota de entrega proativa e idempotência ainda precisam de implementação e prova; F05-08/TZ-09.

## Recorte implementado em PQBA-89

- Novo módulo puro `src/pqbr/workflows/notificacoes_operacionais.py`, com `formatar_pedidos_acesso()`.
- `src/pqbr/workflows/pedidos_telegram.py` preserva `formatar()` como wrapper compatível; `main()`, `avisado_em`, agenda e envio atual não foram alterados.
- Novo teste `tests/unit/test_notificacoes_operacionais.py`, cobrindo vazio, motivo, ausência de motivo, ordenação e equivalência do wrapper.
- Validação independente: 4/4 testes focados; 49/49 em `tests/unit` no worktree Dev; e 69/69 em `tests/unit` após reaplicar somente os três arquivos do patch em um worktree temporário limpo do HEAD 85e3060. A tentativa inicial com `unittest discover` não descobriu as funções pytest; não foi usada como evidência de falha do código.
- Estado: alterações ainda não commitadas, não mescladas e não implantadas. As alterações anteriores de F05-06 no worktree foram preservadas. Não houve chamada de rede, envio de aviso ou mudança de serviço.

## Risco operacional a validar

O fluxo existente grava `avisado_em` e faz commit antes de imprimir a mensagem. Para confirmar o impacto da ordem, executei uma simulação local com banco stub e stdout substituído por uma função que lança OSError. A sequência observada foi update de avisado_em → commit → falha de stdout. Isso confirma o risco do desenho sem enviar mensagens, conectar banco ou tocar em dados reais. A simulação ainda deve virar teste permanente. Para os itens `aviso:` sem lembrete periódico, o risco de perda merece cobertura explícita. PQBA-91 foi aberta para definir saída durável com chave idempotente, ACK somente após entrega confirmada e retry seguro, sem perda nem duplicação.

## Próximos gates e critérios

1. F05-06/TZ-06: provar identidade Paperclip vinculada do José, autorização de aprovar/negar apenas em estado Temporal válido, idempotência persistente, fail-closed e ticket de manutenção após três falhas. A revisão do conector e identidade está em andamento em PQBA-88.
2. F05-08/TZ-09: implementar o destino de avisos proativos e duráveis; cobrir pedidos de acesso, Camofox/sessão, compliance/HOLD, incidentes/tickets e relatórios; testar entrega única, retry após falha e rejeição de destinatários não autorizados. O formatador neutro é somente uma preparação.
3. F05-09/TZ-10: executar ensaio de rollback e comprovar que nenhum emissor PQBR continua usando Telegram; somente então pausar o perfil Hermes `pqbr` e os emissores específicos da PQBR. Não desligar o gateway Hermes compartilhado.

## Referências internas

- `docs/ROADMAP.md`: F05-06, F05-08 e F05-09.
- `docs/TESTES.md`: TZ-06, TZ-08, TZ-09 e TZ-10; TS-05/TS-07; V5.
- `docs/RASTREABILIDADE.md`: RF-19, RF-28, RF-31, RF-34 e RF-48.
- `docs/LACUNAS-fluxo.md`: vínculo com as rotas operacionais atuais.
- Paperclip: PQBA-87 (inventário) e PQBA-89 (extração preparatória).

## Reteste da candidata de outbox — 15/10/2026
A candidata de PQBA-91 foi reconstruída e revisada pelo coordenador somente no worktree isolado `dev/agentes`. A candidata incorpora migration aditiva 0017 (sem aplicação), RLS/policy e grants explícitos, dispatcher com chave por item/ciclo, snapshot do payload antes do envio, claim atômico com lease, validação do tipo, chave e receipt no ACK, retry sem marcar `avisado_em` prematuramente e limite fixo de três tentativas com ticket estruturado idempotente. Sem sender injetado, a entrada retorna antes de abrir o banco; sem `commit()` confirmado, o dispatcher falha antes do envio em vez de tratar a outbox como durável. A consulta também seleciona somente `status = pendente`, inclusive para avisos, excluindo itens decididos/executados. O adapter de transporte real e o adapter idempotente de criação de ticket ainda são seams injetáveis, não implementações operacionais.

Validação em 15/10: `py_compile` aprovado; 86/86 testes na suíte do worktree; 106/106 ao aplicar apenas os cinco arquivos candidatos sobre snapshot limpo do commit-base de código `dbd6d61`; migration e rollback passaram parser PostgreSQL, mas não foram aplicados. Os testes usam banco e remetentes stub. Não houve envio de mensagens, credenciais, acesso ao banco, mudança de agenda/configuração, merge ou publicação. Uma revisão independente somente leitura está solicitada ao Dev Revisor (PQBA-95), pendente.

**Estado:** candidato promissor, ainda não aceito nem mesclado; F05-08/TZ-09 permanece aberto até revisão sem blockers, integração aos fluxos e prova de entrega privada com ACK/idempotência. Discord não foi habilitado e Telegram permanece ativo como rollback.

## Revisão manual da candidata r17 — 15/10/2026
A revisão manual do coordenador encontrou três blockers técnicos e os corrigiu apenas no worktree isolado `dev/agentes`, chegando à r24:
- As policies de canal da r17 eram permissivas; a policy `revisao_humana_app` da migration 0009 já permite todas as linhas. r24 marca as policies SELECT/INSERT/UPDATE/DELETE de `pqbr_app` como RESTRICTIVE, limitadas a `canal_id = 'pqbr'`.
- A consulta r17 selecionava toda a fila humana com status pendente. r24 filtra também `item_ref LIKE 'acesso:%'`, evitando enviar outros tipos de revisão como pedidos de acesso.
- O rollback r17 podia remover uma outbox com dados e falhava se a tabela ainda não existisse. r24 verifica `to_regclass` e bloqueia rollback com linhas existentes.
- A chamada sem sender e sem sink de ticket é no-op antes de consultar/gravar; a recuperação de ticket esgotado continua disponível pelo sink independente.
Validação final r24 em 15/10: 88/88 testes no worktree e 108/108 ao aplicar os cinco arquivos F05-08 em snapshot limpo do commit-base `dbd6d61`; `pglast` parseou migration/rollback e o scanner não achou segredos. Nada foi aplicado ao banco, enviado a um canal, integrado a um schedule/workflow, mesclado ou publicado.
**Parecer:** r24 melhora o contrato da outbox, mas não fecha F05-08/TZ-09: cobre apenas a fila de pedidos de acesso; sender Discord, sink idempotente de ticket e integração/prova privada das rotas de sessão/Camofox, compliance/HOLD, tickets e relatórios permanecem ausentes. Telegram continua ativo como rollback. A revisão independente PQBA-95 não executou porque o Dev Revisor está em erro.

## Revisão r24/r25 e estado do Discord — 15/10/2026
A revisão independente da r24 encontrou que a entrada opcional `rows` permitia contornar o filtro SQL por canal, estado e `item_ref`. A candidata isolada r25 removeu o parâmetro público; os testes de lembrete e reentrância agora usam a consulta do banco simulado, e há regressão explícita para rejeitar tentativa de injeção de `rows`.
Validação r25: `py_compile` aprovado; 89/89 testes no worktree e 109/109 ao aplicar os cinco arquivos candidatos em snapshot limpo do HEAD documental `c1e7210`; scanner de segredos e verificação de whitespace limpos. A migration/rollback não mudou desde a validação de parser PostgreSQL da r24. Não houve execução SQL, merge ou publicação. A revisão independente validou a r24, não a r25; a auditoria independente da r25 ainda está pendente.
No Discord, o bot foi adicionado somente ao canal privado indicado; `View Channel` permitido e `Mention @everyone/@here/roles` negado foram confirmados pela API, sem alterar `@everyone`. O endpoint nativo do Paperclip não foi criado: a tentativa via API recebeu HTTP 403 antes da criação; o browser mostrou `ERR_TUNNEL_CONNECTION_FAILED` na navegação direta (a tentativa anterior pelo túnel temporário retornara HTTP 502), embora curl do Debian tenha respondido HTTP 200. A UI não abriu. Nenhuma mensagem de teste ou workflow foi disparado; o usuário esclareceu que não quer outra conta e indicou a interface web do Paperclip como caminho. Telegram permanece ativo como rollback.
**Estado:** r25 continua candidata, sem merge; F05-06/F05-08/TZ-06/TZ-09 seguem abertos até endpoint, vínculo de identidade, adapters e testes privados integrados.

## Follow-up r26 — 15/10/2026
A revisão independente da r25 encontrou dois defeitos adicionais, corrigidos na candidata isolada r26:
- `pedidos_telegram.main()` agora permite a passagem ticket-only quando `sender` está ausente e há `ticket_sink`, para recuperar outbox esgotado. Sem ambos adapters, a facade continua retornando antes de abrir o banco. Testes usam a facade para validar a recuperação e que pedidos normais não consomem tentativa.
- `janela_horas` agora exige inteiro positivo (booleano não aceito), prevenindo lembretes repetidos por valor zero/negativo.
Validação r26 em 15/10: `py_compile`; 91/91 testes no worktree; 111/111 testes em snapshot limpo do HEAD documental `aae4895`; scanner de segredos e whitespace limpos. Migration/rollback permanecem iguais à r24, parseados anteriormente e nunca aplicados.
**Blockers remanescentes:** sender Discord e sink idempotente de ticket sem implementação real; dispatcher não integrado às rotas de sessão/Camofox/NotebookLM, compliance/HOLD, tickets e relatórios; sem prova privada E2E de entrega/ACK/deduplicação/retry. O endpoint nativo do Paperclip ainda não foi criado (API 403; browser `ERR_TUNNEL_CONNECTION_FAILED`; tentativa pelo túnel temporário `HTTP 502`). Bot continua limitado ao canal privado; Telegram permanece ativo como rollback. F05-08/TZ-09 continua aberto.

## Revisão da ponte de aprovação Telegram local — 15/10/2026
A revisão da candidata `src/pqbr/integrations/telegram_aprovacao.py` em `dev/agentes` encontrou idempotência apenas em memória, sem proteção concorrente; após resposta ambígua do Temporal há risco de reenviar o sinal. O tratamento retorna o texto bruto da última exceção e não cria ticket após três falhas. O arquivo está ausente do checkout oficial, portanto a ponte não está integrada nem aprovada para merge; não foi alterada. F05-06 exige que a aprovação seja implementada/validada pela rota Discord/Paperclip, com identidade autenticada, persistência e comportamento fail-closed.
## Piloto Discord nativo — 15/10/2026
O endpoint Discord da PQBR foi criado e ativado no Paperclip, vinculado diretamente ao Diretor. O teste privado criou uma tarefa por menção de raiz em `#pqbr`, vinculou `mendes_junior` ao usuário Owner autenticado no Paperclip, recebeu respostas na thread e concluiu dois runs do teste `PQBR-97`; não houve publicação nem sinal enviado a workflows de produção. A identidade não vinculada foi filtrada quando `allowUnlinkedPeople=false`. A configuração final verificada permite canais de servidor somente no recurso `#pqbr`, mantém DMs desligadas e `allowUnlinkedPeople=false`; a exceção temporária de convidado foi desligada logo após o vínculo.

O piloto comprova a rota de conversa, não a aprovação Temporal nem os avisos proativos. F05-06/TZ-06 continua aberto até testar aprovar/negar com metadado autenticado, validação de estado, fail-closed, idempotência persistente e ticket após três falhas. TZ-08 é parcial: a menção raiz, a resposta na thread, o vínculo e a filtragem de remetente não vinculado foram exercitados; ainda falta o teste negativo de um canal fora do allowlist. F05-08/TZ-09 continua aberto: a candidata r26 de outbox permanece isolada, sem adapters reais nem integração/prova das quatro rotas operacionais. Telegram/Hermes PQBR permanece ativo exclusivamente como rollback até F05-06/F05-08/TZ-10 e ensaio de rollback.

## Prova real de correlação Discord→Temporal — 15/10/2026

Foi executado um workflow temporário sem efeito de aprovação, usando uma mensagem Discord já recebida e a prova estruturada do Paperclip. O validador conferiu o run e seu `contextSnapshot`, o motivo de wake externo, o `PAPERCLIP_WAKE_PAYLOAD_JSON`, o comentário persistido indicado por `wakeCommentId`, a identidade vinculada, o vínculo issue→endpoint e o recurso autorizado `#pqbr`. O Temporal recebeu um Update cujo ID era exatamente o ID do comentário validado; o workflow de probe aceitou um Update e concluiu.

Resultado observado: wake Discord real confirmado; comment ID/run/Update ID coincidentes; autor igual à identidade Paperclip vinculada; issue, endpoint e `#pqbr` coincidentes; um Update aceito; probe concluído. Não houve mensagem enviada pelo agente, aprovação/negação de produção, sinal a workflow de produção, publicação ou alteração do endpoint. Nenhum worker de produção foi reiniciado.

A candidata permanece em `/home/pc/.pqbr/f05-06-discord-approval-update`, isolada do checkout oficial. Suítes focadas: 22 testes passaram, com 27 subtests. Revisão independente somente leitura do Dev Revisor em `PQBR-101` concluída, com parecer estático favorável à candidata sem efeitos de produção; commit isolado `9c03f61`, 22 testes e 27 subtests aprovados.

**Limite da evidência:** comprova a correlação real de comentário e execução Temporal, não conecta ainda essa ferramenta ao gate de publicação/proposta real. F05-06/TZ-06 permanece aberto até aprovar/negar autenticado no workflow-alvo, verificar estado válido, falhas fechadas, idempotência durável e o ticket após três falhas; sem receber sinais em workflows de produção durante o piloto.
