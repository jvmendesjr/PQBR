# D2 — decisão Board real, recibo exclusivamente local

A interação aprovada do PQBR-118 foi relida duas vezes com `issue interactions <issueId> --json`, no CLI atual e perfil já autenticado, sem abrir credenciais. IDs de organização/ticket/interação/ator/destinatário, status, outcome, políticas solicitada/efetiva, ausência de agente/run e escopo exato foram conferidos antes da gravação. A idempotencyKey original foi preservada e conferida na releitura. O timestamp é o resolvedAt canônico. Nenhuma resposta raw completa foi persistida.

## Resultado

1 inserção em processo separado, encerrado normalmente; novo cliente CLI, novas conexões SQLite e 16 reenvios concorrentes em processos distintos produziram 16 duplicatas e exatamente 1 recibo. pendingCount=0, resumeCount=0, effectCount=0; integrity_check=ok. O SQLite usa BEGIN IMMEDIATE, chave única para idempotência/interação, journal DELETE e synchronous FULL; corpo divergente falha fechado. Workers locais têm ambiente mínimo e audit hook bloqueando sockets/subprocessos; não é isolamento de kernel. Só o runner faz o GET autorizado.

## Limites

Prova atribuição da decisão Board pelo Paperclip ao userId esperado, que o proprietário autorizou como perfil tutibom neste teste. Não usa aprovação do chat como decisão no ticket e não demonstra autenticação via Discord, posse de credenciais ou uma assinatura independente. Deduplicação persiste após encerramento normal/reabertura do SQLite local; não é teste de SIGKILL, queda do host ou crash safety Paperclip/Temporal real, transação distribuída, fencing ou exactly-once externo. Não há pendentes, dispatcher, outbox ou integração operacional. Efeito e resume são literalmente zero.

A única alteração preexistente autorizada é a nota F3-05; demais arquivos são preservados. Nenhum endpoint mutável, comentário, aviso Discord, chamada Temporal, alteração de Worker, publicação, commit/push ou documento restrito. F3-05/G4 segue aberto; demais gates/pausas e política operacional intactos.

## Artefatos

- `receipt.json`: whitelist do recibo; `audit.sqlite3`: a mesma decisão persistida.
- `resultado.json`: contagens e hash anterior do roadmap.
- `test_integracao_d2.py`: ensaio reproduzível; o diretório de saída deve ser novo.
- `nota-roadmap.txt`: inserção exata no roadmap.
