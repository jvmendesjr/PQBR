# F3-05 — lacuna no roteamento da intervenção

**O próximo requisito restante verificável offline é o roteamento da Activity de intervenção para a fila da ferramenta/sessão. O checkout atual ainda não o atende para Camofox.** Foi acrescentado um diagnóstico estático, sem alterar código de aplicação, iniciar serviços ou fechar F3-05/G4.

## O que foi encontrado

O requisito consta em `docs/REGRAS.md` §3.1, `docs/SPEC.md` RF-44, `docs/ARQUITETURA.md` §2 (correção autônoma), `docs/TESTES.md` TS-11 e `docs/ROADMAP.md` F3-05.

Em `src/pqbr/workflows/correcao.py`, a chamada `workflow.execute_activity(intervir_agente, ...)` não fornece `task_queue`: herda a fila do workflow. Em `src/pqbr/workflows/worker.py`, `CorrecaoAutonomaWorkflow` e `intervir_agente` estão registrados na fila `pqbr-episodio`. O Worker de `src/pqbr/workflows/worker_camofox.py` declara a fila `camofox-pqbr` e `max_concurrent_activities=1`, mas não registra `intervir_agente`.

Logo, o caminho declarado no checkout não encaminha explicitamente a intervenção Camofox ao Worker da sessão. Isso é constatação do código, não observação dos Workers implantados. Um limite de uma Activity por instância de Worker também não prova exclusão mútua global por sessão se houver outras instâncias consumindo a mesma fila.

## Testes acrescentados

Arquivo: `tests/unit/test_f3_05_roteamento_offline.py`.

Os testes usam somente AST e leitura dos fontes: não importam os Workers nem executam seu `main()`. Três testes aprovados verificam a declaração da fila/limite Camofox, o registro atual no Worker principal e `maximum_attempts=1` na intervenção. Dois contratos estão marcados `xfail(strict=True)`: exigem roteamento explícito da intervenção e seu registro no Worker Camofox, respectivamente. Esses **dois XFAIL são lacunas abertas, não testes aprovados nem aceite de TS-11**. Se os contratos passarem, o XPASS estrito exigirá revisão dos marcadores e da evidência. Mudanças arquiteturais também podem exigir revisão desses testes estáticos.

Resultado focado: **3 passed, 2 xfailed in 0.07s**.

Regressão: **277 passed, 19 skipped, 2 xfailed in 2.30s**. Os 19 testes do harness Temporal foram pulados por ausência de opt-in; nenhum servidor efêmero foi repetido. A contagem anterior registrada era 274 aprovados; os três novos testes aprovados explicam os 277 desta rodada.

[Log focado](evidencias-f3-05-roteamento-offline-20261017/focado.log) · [Regressão](evidencias-f3-05-roteamento-offline-20261017/regressao.log) · [Preservação](evidencias-f3-05-roteamento-offline-20261017/preservacao.json).

## Blocker e ponto de parada

**Não foi alterado o roteamento.** Sua correção envolve reconciliar o despacho do workflow e o registro de Activities nos Workers por ferramenta/sessão. A validação ponta a ponta de despacho e serialização depende de um runtime Temporal autorizado; a garantia global por sessão exige conferir a topologia e os consumidores concorrentes, não apenas adicionar `max_concurrent_activities=1`. Esses passos estão fora da autorização offline atual. A tarefa para aqui, sem presumir autorização para servidor, consulta a backend, reinício, implantação ou produção.

Os backends Jev/Paperclip, a checagem real prévia de conta/sessão, o registro por outbox/Hindsight e a proposta real de ajuste continuam sem comprovação por esta evidência. Não se afirma que o diagnóstico estático valida timers, replay, execução real, concorrência, exclusão por sessão ou persistência.

## Reprodução sem serviços

No checkout `/home/pc/Workspace/PQBR`:

```sh
unshare --user --map-root-user --net --pid --fork --mount-proc --kill-child=KILL \
  env -i PATH=/usr/bin:/bin HOME=/tmp LANG=C.UTF-8 \
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  PQBR_PAPERCLIP_API=http://127.0.0.1:1 \
  .venv/bin/python -m pytest -q -rx -p no:cacheprovider \
  tests/unit/test_f3_05_roteamento_offline.py
```

Para a regressão, substituir o último caminho por `tests/seguranca tests/unit tests/test_kit.py tests/workflows/test_f3_05_temporal_isolado.py`, sem variável de opt-in. O endereço Paperclip é sintético, sem credencial e sem conexão feita pela tarefa. As execuções ocorreram em namespaces de rede/PID e ambiente limpo. O SSH foi usado somente para operar arquivos e processos de teste locais no checkout solicitado.

## Preservação

Somente a nova suíte, esta evidência e seu diretório de artefatos foram adicionados ao checkout. Os hashes de **381 arquivos preexistentes permitidos** foram conferidos antes/depois e nenhum divergiu. O manifesto e o status inicial estão no diretório de evidências; os conteúdos restritos foram excluídos do manifesto e não foram lidos. Não houve alteração de documentação normativa ou de arquivos anteriores.

A política atual de exceção técnica permanece integralmente preservada. A alternativa continua apenas proposta para revisão entre 5 e 7 dias após início efetivo e confirmado da produção, ou antes mediante pedido humano de revisão de expressão visual; nenhum lembrete foi criado e nenhuma data de produção foi presumida.

**F3-05/G4 aberto; F7-02/G7 e PQBR-114 pausados; F05-06 no-arm.** Sem commit/push, instalação, backend, serviço iniciado/reiniciado, alteração de política ou produção. Não foram consultados `docs/arquivo/`, `docs/pesquisas/`, `docs/DECISOES-LOG.md` nem contrato editorial restrito.
