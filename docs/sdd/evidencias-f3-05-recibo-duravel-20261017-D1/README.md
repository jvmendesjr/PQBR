# F3-05 — recibo durável sintético com recuperação após crash

**44/44 testes aprovados em duas rodadas da versão final. Cada rodada criou 409 subprocessos e encerrou 9 deles com SIGKILL real. F3-05/G4 continua aberto.** O protótipo está inteiramente nesta pasta, sem importação pelos Workers, integrações reais ou servidor Temporal.

O avanço sobre H2/H3 é específico: decisão, manifesto, consumo, outbox e deduplicação do receptor agora sobrevivem ao encerramento do processo por estarem em SQLite temporário, e não em memória. Não se trata de autenticação humana real nem de durabilidade do Paperclip/Temporal operacional.

## O que foi construído

`duravel_d1.py` contém uma API canônica **fake**, com gravação e releitura reais apenas em um SQLite sintético, além de um dispatcher e um receptor Temporal **fake** em outro SQLite. Nenhum módulo `pqbr`/`temporalio`, HTTP, CLI de integração, credencial, ticket, mensagem ou workflow real é utilizado. Os bancos são criados somente em diretórios `/tmp/pqbr-d1-*` com marcador `SYNTHETIC_ONLY`; cada teste os remove ao terminar.

O manifesto imutável inclui ticket/interação, supervisor/run, operação falha/run, recibo sintético do registro da falha, revisão, sequência exata de IDs pendentes, decisor sintético já vinculado, canal, timestamp, expiração e decisão. Mantém `request_confirmation`, política solicitada e efetiva `human_only`, destinatário humano fixo da fixture, destinatário agente nulo e `continuationPolicy="none"`. Campos extras como `target=plan` são recusados.

A sessão de board ou o vínculo Discord são **fronteiras de confiança simuladas**, selecionadas pelo harness. O nome do decisor não constitui autenticação. Sessão/token de agente de workflow, canal sem vínculo e decisão extraída de um comando isolado não autorizam. Não é proposta uma nova identidade, allowlist ou integração operacional.

### Origem: duas transações explícitas

1. A API fake grava decisão + manifesto canônico/binding + receipt + estado `pending` na mesma transação. A chave única ticket/interação usa hash de um array JSON canônico, sem ambiguidade por separadores. Decisão e manifesto não podem ser atualizados ou apagados pelos caminhos normais do esquema.
2. O consumo relê a decisão canônica, confere aprovação, validade, revisão e escopo completos contra o estado vivo sintético, aplica CAS `pending → consumed` e insere um comando imutável na outbox **na mesma transação**. Se a inserção falha, o consumo reverte. `consumed` significa comando duravelmente admitido, **não** efeito já executado.

Uma nova execução do dispatcher varre a outbox ainda `pending`. O status somente vira `acked` depois de o receptor ter confirmado seu commit. A coluna `attempts` conta tentativas de entrega, não execuções. Não há daemon, Schedule, retry de operação técnica ou reconexão com produção: as novas invocações de recuperação são explícitas nos testes.

### Receptor: deduplicação não depende de memória

Antes do primeiro aceite, o receptor relê a decisão fake na origem, verifica binding/comando, consumo/outbox admitidos e o seu próprio escopo vivo. Exige exatamente as operações pendentes autorizadas; operação nova, removida, já concluída ou falha terminal não pode entrar na retomada.

A deduplicação possui `PRIMARY KEY(receipt)` e `UNIQUE(scope)` em **outro banco SQLite**. O escopo técnico inclui ticket, supervisor/run, falha/run/registro, revisão e sequência de pendentes; exclui interação, canal e decisor deliberadamente: outra interação não pode entregar uma segunda vez o mesmo escopo já aceito. Novo receipt para escopo já entregue é conflito, não nova autorização. O mesmo receipt com payload divergente também é conflito.

O registro de deduplicação, o ACK e os efeitos **sintéticos** das pendentes são gravados na mesma transação receptora. Uma duplicata exata recupera o ACK persistido sem executar de novo, inclusive após expiração da autorização original: nesse caminho não há novo aceite/efeito nem dependência de nova autenticação; o comando idêntico já validado está persistido. Após o primeiro aceite, o estado vivo do receptor pode ter mudado para fila vazia sem impedir a recuperação do ACK.

A operação falha é **semeada pela fixture** como `terminal_failed`, com contador 1, e nunca muda nem incrementa. As duas pendentes começam com contador 0 e só podem chegar a 1. Isso prova a preservação desse estado sintético; não executa uma intervenção real nem revalida toda a política de falha de H3.

## O que os testes demonstraram

| Interrupção ou falha | Resultado após abrir outro subprocesso |
| --- | --- |
| SIGKILL antes do commit da decisão | Decisão/receipt/estado não aparecem parcialmente; nova submissão sintética pode gravar. |
| SIGKILL depois do commit da decisão | Decisão e recibo são relidos; consumo continua `pending`, sem resume implícito. |
| SIGKILL antes do commit do consumo | CAS e outbox revertem juntos. |
| SIGKILL depois do consumo, antes do envio | `consumed` + comando na outbox sobrevivem; nova execução entrega as pendentes exatas. |
| SIGKILL antes do commit receptor | Nem dedup nem efeito parcial sobrevivem. |
| SIGKILL depois do commit receptor, antes da resposta | Efeito/dedup sobrevivem; reentrega retorna ACK sem repetir. |
| SIGKILL após aceite, antes de armazenar ACK na origem | Outbox segue pendente; reentrega idempotente conclui o ACK. |
| SIGKILL depois do commit do ACK | Novo dispatcher não reenvia comando já confirmado. |
| Falha de escrita do ACK (`SQLITE_READONLY`) | Receptor já terminou; outbox fica pendente, próxima entrega deduplica. |
| `SQLITE_READONLY`, falha de constraint e `SQLITE_FULL` após CAS | Nenhum consumo isolado ou outbox parcial; rollback conferido. |
| `SQLITE_BUSY` com lock real na origem ou receptor | Falha fechada; sem efeito/ACK inventado, recuperação explícita após liberar lock. |

Também foram cobertos replay sequencial e concorrente com processos independentes, decisão/consumo/receiver/dispatcher concorrentes, conflito da mesma chave com payload divergente, receipt ausente/forjado, ticket/interação/supervisor/falha/revisão/pendentes stale, prazo expirado antes do consumo ou primeiro aceite, recusa humana, política/destinatário errados, terminal incluída na fila, operação nova, falha no segundo efeito com rollback do primeiro e regressão de IDs que colidiam quando concatenados com `/`.

Os testes de concorrência toleram apenas `SQLITE_BUSY` como recusa concorrente transitória; validam o estado final persistente e pelo menos uma admissão. Os testes de lock dedicados exigem o código `SQLITE_BUSY`. `SQLITE_FULL` é produzido de verdade limitando páginas na conexão de teste, sem encher o disco do PC. O modo read-only produz erro real SQLite; não é uma simulação de pane elétrica ou erro físico de disco.

Em cada teste, outro subprocesso inspeciona os dois bancos, exige `PRAGMA integrity_check=ok`, nenhum contador de operação acima de 1, terminal inalterada e igualdade entre receipts consumidos e receipts presentes na outbox. Os nove SIGKILL incluem o caso de ACK perdido seguido de expiração. As quedas usam marcador de checkpoint e SIGKILL enviado pelo pai; não usam exceção Python como substituto de queda.

## Resultados e arquivos

- [Resultado final](execucao-final/resultado.json): **44 aprovados, zero falhas/erros/pulados**, Python **3.13.5**, SQLite **3.46.1**, 409 processos e 9 SIGKILL.
- [Log final](execucao-final/testes.log) e [trilha dos subprocessos](execucao-final/subprocessos.json): IDs de testes, PIDs, checkpoints, sinais, códigos de saída e leituras do estado sintético.
- [Rodada anterior da mesma versão final](execucao-v3/resultado.json): também 44/44, 409 processos e 9 SIGKILL. Rodadas independentes, não 88 cenários distintos.
- [Preservação](preservacao.json): hashes de **1.471 arquivos**, metadados de **1.552 arquivos** e quatro Workers nos mesmos PIDs/inícios/restarts, com apenas esta pasta nova e a nota F3-05 alteradas. Os números são conjuntos parcialmente sobrepostos, não devem ser somados. Configuração e documentos restritos não foram lidos; o verificador só coletou metadados desses caminhos.
- `worker_d1.py`: entrada JSON restrita aos subprocessos de teste. `test_duravel_d1.py` e `run_tests_d1.py`: suíte/runner stdlib. `preservar_d1.py`: comparação somente leitura dos arquivos e propriedades dos serviços.

A primeira tentativa, [v1](execucao-v1/resultado.json), teve 38 erros de preparação: o audit hook do runner bloqueava o `os.posix_spawn` usado pelo Python 3.13, antes de qualquer worker rodar. O gate foi corrigido para permitir somente o argv exato do worker sintético; a [v2](execucao-v2/resultado.json) passou 38/38. A revisão estática encontrou uma chave ticket/interação concatenada ambígua; ela foi substituída por hash de tupla canônica e coberta no teste 44 antes das rodadas finais. Os registros anteriores foram preservados, não reclassificados como sucesso.

## Como reproduzir sem integração

No PC, escolha um diretório de saída **novo**. Não há instalação, container, pull ou servidor Temporal:

```bash
cd /home/pc/Workspace/PQBR
env -i PATH=/usr/bin:/bin HOME=/home/pc \
  python3 -I -S -B \
  docs/sdd/evidencias-f3-05-recibo-duravel-20261017-D1/run_tests_d1.py \
  /tmp/pqbr-d1-resultados-REPRO-NOVO
```

O runner recusa sobrescrever saída existente. Cada caso cria e remove seus próprios dois bancos temporários. Os workers não recebem ambiente de credenciais. Audit hooks bloqueiam sockets e execução externa nos workers; no runner, somente a criação do worker Python com argv exato é permitida. **Isso é um gate contra efeitos acidentais, não isolamento de kernel contra código hostil.** A execução de processos sintéticos é local; nenhuma CLI mutável de serviço é chamada.

## Limites que continuam abertos

**Não há autenticação, assinatura ou receipt oficial.** SHA-256/JSON canônico faz binding de conteúdo e correlação. A sessão humana, vínculo existente, relógio fixo e leituras canônicas são fixtures confiáveis. Quem puder escrever arbitrariamente no banco local, remover triggers ou controlar o programa está fora da garantia; constraints não são uma fronteira de autorização.

**SQLite local não valida Postgres/Paperclip.** O ensaio usa dois arquivos locais, transações `BEGIN IMMEDIATE`, journal `DELETE`, `synchronous=FULL`, locks locais e os comportamentos do SQLite/filesystem deste PC. Não prova equivalência de isolamento, concorrência, ACL, migrações, APIs, autenticação, failover, backups, filesystem de rede, corrupção, fsync/hardware ou recuperação após queda do host. SIGKILL prova recuperação da queda do processo observada, não de qualquer pane elétrica.

**Não existe transação distribuída entre os bancos.** A outbox admite entrega pelo menos uma vez; a deduplicação persiste no receptor. A atomicidade dos efeitos só existe porque os efeitos aqui são linhas no mesmo SQLite receptor. Uma chamada externa real não participa dessa transação: crash entre efeito externo e commit continua podendo gerar resultado incerto. Não há prova de exactly-once de efeitos externos, fencing, idempotência de fornecedor ou replay/histórico Temporal. Um receptor operacional teria de justificar sua própria persistência e protocolo, não copiar essa conclusão automaticamente.

H2/H3, candidatas, supervisores, `src/`, Workers, units e configuração permanecem intactos. Nenhum servidor/container foi iniciado, nenhuma identidade real foi presumida e nenhuma integração foi armada. Não houve restart de serviço, deploy, ticket/aviso/HTTP real, credencial, publicação, commit/push nem consulta aos documentos vedados.

**F3-05/G4 aberto; política de exceção técnica intacta; F05-06 no-arm; F7-02/G7 e PQBR-114 pausados.** Integração controlada real ainda exige plano/aceite explícitos; o fechamento também depende do TS-11 e aceite operacional completos.
