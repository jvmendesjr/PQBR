# F3-05 — espera determinística entre intervenções do Camofox

**A espera foi implementada no workflow e validada no servidor Temporal efêmero isolado: 19 testes passaram, 18 históricos novos passaram no replay e os 14 históricos anteriores também passaram com o código novo.** A regressão offline terminou com **274 passed, 19 skipped**. F3-05/G4 permanece aberto; não houve implantação nem ativação.

## O que mudou

Em `src/pqbr/workflows/correcao.py`, cada nova intervenção do Camofox após a primeira aguarda um intervalo sorteado de **300 a 900 segundos**, usando exclusivamente `workflow.random()` e `workflow.sleep()`. O timer começa depois da intervenção anterior e, quando houver, da verificação negativa. Não existe espera antes da primeira intervenção, depois da última, após sucesso ou parada sensível. Outras ferramentas mantêm seu comportamento anterior.

O intervalo é independente do `start_to_close_timeout` da Activity. Os timeouts existentes foram mantidos, assim como o teto de três intervenções e `maximum_attempts=1` da intervenção. Não foi introduzido `asyncio.sleep`, relógio de parede ou aleatoriedade externa no workflow.

A mudança usa `workflow.patched("f3-05-camofox-intervalo-v1")`. Durante replay dos históricos antigos sem o marcador, o caminho anterior não consome os sorteios novos nem emite timers novos. Isso foi comprovado nos 14 históricos capturados na tarefa anterior, sem modificar seus eventos. Não é uma autorização de deploy nem uma comprovação de compatibilidade com todos os históricos possíveis.

Foram editados somente o workflow, `tests/unit/test_f3_05_local.py` e `tests/workflows/test_f3_05_temporal_isolado.py`. O runner de isolamento anterior permaneceu byte a byte igual. As diferenças desta tarefa, relativas ao estado encontrado e não ao HEAD, estão em [alteracoes.patch](evidencias-f3-05-intervalo-20261017/alteracoes.patch).

## O que o histórico mostrou

No cenário de sucesso na terceira intervenção, os dois timers foram de **433 s e 318 s**. Os timeouts das três Activities foram **465 s, 573 s e 524 s**, respectivamente. Os agendamentos ocorreram em `13:26:42.529Z`, `13:33:55.635Z` e `13:39:13.755Z`, no relógio virtual do servidor de teste.

Os testes verificam `TimerStarted` e `TimerFired` reais, associação pelo identificador do timer, faixa de duração e ordem dos eventos: conclusão da intervenção/verificação anterior → início do timer → disparo → próxima intervenção. Também verificam ausência de espera inicial/final, sucesso na segunda tentativa, esgotamento, verificação negativa, caminhos sensíveis e ferramenta não-Camofox.

Cancelamento durante a espera gerou `TimerCanceled` e workflow cancelado, sem segunda intervenção ou registro falso. Na troca controlada de Worker durante uma espera de **666 s**, o mesmo timer foi retomado, com intervenções `[1, 2]`, sem duplicação. Isso não simula reboot, perda do servidor ou queda abrupta.

A execução dos 19 testes levou **12,142 s reais**, com avanço de tempo do test-server; não se alega espera de minutos de relógio de parede. Há 18 workflows novos, cada um com histórico JSON e resumo, mais um teste que reexecuta os 14 históricos legados. Todos os replays usam `Replayer`, sandbox padrão, conversor Pydantic e `raise_on_replay_failure=True`, sem fabricar eventos. [Resumo factual](evidencias-f3-05-intervalo-20261017/resumo-validacao.json) · [Log do harness](evidencias-f3-05-intervalo-20261017/execucao.log) · [Replay legado](evidencias-f3-05-intervalo-20261017/replay-legado.summary.json).

Os testes locais adicionais exercitam os limites exatos 300/900 com sorteio substituído e o caminho sem patch. Esses mocks não são a evidência de runtime; os eventos reais acima são.

## Exceção técnica: política não alterada

Uma exceção técnica sintética na primeira intervenção continua produzindo falha do workflow, uma única execução da Activity, nenhum timer, nenhuma verificação e nenhum registro falso. O teste confirma a causa `FalhaSintetica`. Não foi acrescentado tratamento que converta essa exceção em nova tentativa, resultado registrado ou aviso.

**Continua pendente de decisão separada:** como tratar e reportar a exceção técnica da intervenção, sem confundi-la com `resolvido=False`. Nenhum canal real foi acionado.

## Isolamento e preservação

Foi reutilizado `tests/workflows/run_f3_05_isolado.sh`: namespaces de usuário, rede, PID e montagem de `/proc`, apenas loopback ativo, sem rotas externas; `env -i`, HOME/TMPDIR temporários, sem credenciais/proxies herdados; binário local explícito, sem download; fila e workflow IDs únicos, timeout externo de 300 s e cleanup do servidor. O namespace Temporal `default` pertence exclusivamente a cada test-server descartável, não a um servidor compartilhado.

O binário `/tmp/temporal-test-server-sdk-python-1.34.0` manteve SHA-256 `19defb9f7318c7cf249518b3642a735efb79876c2b6918afe312336476b796a5`. O namespace de rede da execução foi `net:[4026533133]`, distinto do host `net:[4026531840]`. A conferência posterior encontrou **zero processos** no namespace encerrado. Dois test-servers preexistentes no host, iniciados em 15/10/2026, foram preservados e não receberam conexão. [Encerramento](evidencias-f3-05-intervalo-20261017/encerramento.log).

As Activities falsas usam dados sintéticos e os caminhos simulados/fail-closed; o registro é apenas em memória. Não foram chamados Jev, Paperclip, Camofox, outbox, Hindsight, serviços reais, backends ou produção. Nenhum Worker persistente foi iniciado. O aviso do SDK sobre capacidade de heartbeat do test-server continua presente; heartbeat não foi validado.

A regressão também rodou em namespace sem rede externa e ambiente limpo. A coleta inicial encontrou ausência de contexto Paperclip no HOME temporário; a repetição usou somente `PQBR_PAPERCLIP_API=http://127.0.0.1:1` sintético, sem chave e sem servidor nesse endereço. O log inicial foi preservado, sem recorrer à conta real. [Regressão final](evidencias-f3-05-intervalo-20261017/regressao.log).

Os três arquivos alterados foram comparados com as cópias iniciais antes da aplicação. **68 hashes anteriores** de arquivos não alterados nesta tarefa, incluindo artefatos anteriores, permaneceram iguais; o relatório de preservação e o manifesto estão no diretório novo. O estado inicial do checkout já continha mudanças e arquivos não rastreados; não houve reset, limpeza do checkout ou substituição dessas mudanças.

Não houve commit/push, instalação de dependências, acesso a serviços de produção ou alteração da documentação normativa. Não foram consultados os conteúdos de `docs/arquivo/`, `docs/pesquisas/`, `docs/DECISOES-LOG.md` ou contrato editorial restrito. Não foram alterados gates: **F3-05/G4 aberto; F7-02/G7 e PQBR-114 pausados; F05-06 no-arm**.

## Reprodução segura

No checkout `/home/pc/Workspace/PQBR`, com nova autorização para repetir o servidor efêmero e um diretório de saída ainda inexistente:

```sh
sh tests/workflows/run_f3_05_isolado.sh /tmp/pqbr-f3-05-intervalo-nova-execucao
```

A regressão sem servidor usa:

```sh
unshare --user --map-root-user --net --pid --fork --mount-proc --kill-child=KILL \
  env -i PATH=/usr/bin:/bin HOME=/tmp LANG=C.UTF-8 \
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  PQBR_PAPERCLIP_API=http://127.0.0.1:1 \
  .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/seguranca tests/unit tests/test_kit.py \
  tests/workflows/test_f3_05_temporal_isolado.py
```

Sem opt-in, os 19 testes do harness são pulados. As evidências novas, hashes e logs ficam em `docs/sdd/evidencias-f3-05-intervalo-20261017/`.
