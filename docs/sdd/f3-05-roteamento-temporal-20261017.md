# F3-05 — roteamento confirmado no Temporal isolado

**O runtime confirmou a lacuna: `intervir_agente` herda a fila do workflow, não escolhe a fila Camofox a partir de `ferramenta` ou `sessao`.** Foram executados 5 testes em 4,784 segundos, com servidor Temporal efêmero, loopback e Activities falsas. Não houve correção do workflow nem alteração de Workers persistentes. **F3-05/G4 continua aberto; os dois XFAIL anteriores continuam lacunas.**

## O que os históricos demonstraram

Os testes executam o `CorrecaoAutonomaWorkflow` real do checkout. Cada cenário usa filas exclusivas, com sufixo aleatório, que representam a principal e a sessão apenas no ambiente descartável; não são as filas de um serviço real.

1. **Workflow na fila principal sintética:** mesmo com um Worker efêmero de sessão registrado para `intervir_agente`, o evento `ActivityTaskScheduled.task_queue.name` aponta para a principal. A Activity falsa confirmou essa mesma fila por `activity.info().task_queue`. Houve sucesso simulado; as quatro Activities foram executadas na principal e nenhuma na sessão.
2. **Controle experimental na fila de sessão:** ao iniciar o workflow na fila sintética da sessão e registrar nela todas as Activities falsas, todas as quatro chamadas herdaram essa fila e o fluxo terminou. Isso explica o mecanismo de herança; **não representa a configuração operacional existente nem é uma solução aprovada**.
3. **Sem registro da intervenção no Worker principal:** o Worker principal, que continua consumindo sua fila para as outras Activities, recebeu a tarefa e a rejeitou com `NotFoundError`: `intervir_agente` não registrada. Houve um evento de falha da Activity e nenhuma execução da função falsa de intervenção; o Worker de sessão não recebeu chamada e não houve registro final. Portanto, não se tratou de uma tarefa que ficou pendente sem consumidor: havia consumidor na fila, mas sem registro daquele tipo de Activity. A presença de outro Worker em outra fila não a redirecionou.
4. **Exceção técnica sintética da intervenção:** preservou a falha atual, com uma execução observada, `maximum_attempts=1`, sem verificação, timer ou registro final e sem chamada na fila de sessão. Isso não altera a política nem pretende generalizar para toda classe de exceção real.
5. **Replay dos históricos anteriores:** os 14 históricos da primeira suíte e os 18 da suíte de intervalos passaram no `Replayer`, com sandbox padrão, conversor Pydantic e `raise_on_replay_failure=True`.

Os quatro históricos novos também foram capturados diretamente do servidor, gravados em JSON, recarregados e aprovados no replay. Nenhum evento foi fabricado. **Resultado: 32 replays anteriores e 4 novos aprovados.** Como nenhum arquivo anterior ou fonte foi alterado, não foi necessário acrescentar patch/versionamento ao workflow.

[Log de execução](evidencias-f3-05-roteamento-temporal-20261017/execucao.log) · [Históricos e resumos](evidencias-f3-05-roteamento-temporal-20261017/runtime/) · [Verificação factual](evidencias-f3-05-roteamento-temporal-20261017/verificacao.json).

## Blocker para corrigir, não para diagnosticar

O teste autorizado conseguiu provar o comportamento atual sem tocar em Workers persistentes. **O passo seguinte de correção exige reconciliar o despacho do workflow e o registro das Activities nos Workers por ferramenta/sessão.** Não foi aplicada uma `task_queue` nova que pudesse deixar tarefas sem consumidor no desenho operacional atual, nem foi movido o workflow para outra fila.

A garantia de exclusão mútua por sessão depende da arquitetura e da topologia dos consumidores. `max_concurrent_activities=1` limita uma instância de Worker, não garante exclusividade global da sessão. Essa decisão e qualquer alteração de Workers persistentes estão fora desta execução: a tarefa para aqui. Roteamento, exclusão por sessão, implantação e aceite de TS-11 são assuntos distintos.

## Isolamento e encerramento

Foi acrescentado `tests/workflows/run_f3_05_roteamento_isolado.sh`, derivado do runner anterior preservado. As barreiras permanecem: namespaces de usuário/rede/PID e montagem de `/proc`; somente loopback ativo; nenhuma rota externa; `env -i`, HOME/TMPDIR temporários e sem credenciais/proxies herdados; timeout externo de 300 s; binário local explícito sem download; encerramento do servidor por cleanup e dos descendentes pelo namespace PID.

Binário: `/tmp/temporal-test-server-sdk-python-1.34.0`, SHA-256 `19defb9f7318c7cf249518b3642a735efb79876c2b6918afe312336476b796a5`. Namespace do host: `net:[4026531840]`; namespace do teste: `net:[4026533133]`. A conferência posterior encontrou **zero processos restantes no namespace de teste**. Não se conectou a servidores preexistentes.

Os Workers do harness existem apenas dentro do servidor/namespace descartáveis. As Activities de triagem/intervenção/verificação usam somente simulações sintéticas; o registro é em memória. Nenhum Jev, Paperclip, Camofox, banco, outbox ou Hindsight real foi chamado. O SDK emitiu o aviso já conhecido sobre capacidade de heartbeat do test-server; heartbeat não foi validado.

## Regressão e preservação

A regressão posterior foi executada sem opt-in, em namespace sem rede e ambiente limpo: **277 passed, 24 skipped, 2 xfailed in 2.13s**. Os 24 pulados são os 19 testes do harness anterior mais os 5 novos; o servidor não foi repetido nessa regressão. Os dois XFAIL estritos da suíte estática continuam corretamente abertos.

Os hashes de **389 arquivos anteriores permitidos** permaneceram iguais, inclusive fonte do workflow, Workers, testes existentes e evidências anteriores. Conteúdos de `docs/arquivo/`, `docs/pesquisas/`, `docs/DECISOES-LOG.md` e contratos editoriais restritos foram excluídos da leitura e do manifesto. Somente a nova suíte, seu runner, esta evidência e os novos artefatos foram adicionados.

[Regressão](evidencias-f3-05-roteamento-temporal-20261017/regressao.log) · [Manifesto inicial](evidencias-f3-05-roteamento-temporal-20261017/antes.json).

A política de exceção técnica permanece exatamente como estava. A proposta alternativa continua apenas para revisão 5–7 dias após início efetivo e confirmado da produção, ou antes mediante pedido humano de revisão de expressão visual; nenhum marco de produção ou agendamento foi criado.

**F3-05/G4 aberto; F7-02/G7 e PQBR-114 pausados; F05-06 no-arm.** Sem commit/push, deploy, produção, instalação, alteração de serviço persistente ou política.

## Reprodução somente com nova autorização de servidor isolado

```sh
cd /home/pc/Workspace/PQBR
# O diretório de saída deve ainda não existir.
sh tests/workflows/run_f3_05_roteamento_isolado.sh /tmp/pqbr-f3-05-roteamento-nova-execucao
```

Não executar esse runner apenas para reproduzir a regressão offline. Para esta, sem `PQBR_TEMPORAL_ISOLADO`:

```sh
unshare --user --map-root-user --net --pid --fork --mount-proc --kill-child=KILL \
  env -i PATH=/usr/bin:/bin HOME=/tmp LANG=C.UTF-8 \
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  PQBR_PAPERCLIP_API=http://127.0.0.1:1 \
  .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/seguranca tests/unit tests/test_kit.py \
  tests/workflows/test_f3_05_temporal_isolado.py \
  tests/workflows/test_f3_05_roteamento_temporal_isolado.py
```
