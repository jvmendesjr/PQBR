# Inventário de notificações operacionais — migração para Discord/Paperclip

Data de referência: 15/10/2026 00:41 (Fortaleza)
Escopo: inventário estático do código e dos resultados registrados nos tickets PQBA-87/PQBA-89; nenhuma configuração de canal, serviço ou credencial foi alterada.

## Resumo executivo

A migração cobre mais do que trocar o destino de uma mensagem. Há quatro grupos de avisos: pedidos de acesso e eventos de sessão; decisões de aprovação de workflows Temporal; incidentes de compliance/pós-publicação; relatórios operacionais e de consumo. O inventário do Dev Corretor foi concluído em PQBA-87. Um primeiro recorte de código, PQBA-89, extraiu a formatação dos pedidos de acesso sem mudar o transporte, a agenda ou o comportamento de envio. O recorte passou em 4 testes próprios e na suíte unitária completa (49/49) quando executado no ambiente Python do projeto.

Isso não fecha F05-08 nem prova que o Discord consegue enviar avisos proativos. O recorte permanece não commitado no worktree isolado do Dev e ainda precisa de revisão antes de qualquer integração. Telegram continua sendo a rota ativa durante a transição; não deve ser pausado até TZ-06, TZ-08, TZ-09 e o rollback TZ-10 estarem aceitos.

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
- Validação independente no worktree: 4/4 testes do módulo e 49/49 testes de `tests/unit` passaram via `pytest` usando o Python do ambiente do projeto. A tentativa inicial com `unittest discover` não descobriu as funções pytest; não foi usada como evidência de falha do código.
- Estado: alterações ainda não commitadas, não mescladas e não implantadas. As alterações anteriores de F05-06 no worktree foram preservadas. Não houve chamada de rede, envio de aviso ou mudança de serviço.

## Risco operacional a validar

O fluxo existente grava `avisado_em` e faz commit antes de imprimir a mensagem. Isso cria um risco potencial de perda: se o consumidor do stdout falhar depois do commit, a linha pode ser considerada avisada antes de haver confirmação de entrega. Para os itens `aviso:` que não têm lembrete periódico, a consequência pode ser mais grave. Esta é uma inferência estática; ainda não foi demonstrada por um teste de falha do consumidor. Antes de migrar, definir um contrato durável de saída com chave idempotente, estado pendente/enviado, confirmação somente após entrega e retry seguro, evitando tanto perda quanto duplicação.

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
