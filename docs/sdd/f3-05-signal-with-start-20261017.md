# F3-05 — Signal-With-Start no ator por sessão: protótipo isolado

**A execução final aprovou 9 cenários e pulou 1 por limitação do servidor de teste. Os 15 históricos finais passaram no replay; a conferência adicional reproduziu os 31 históricos capturados em todas as tentativas.** A corrida inicial teve uma recusa intermitente na primeira tentativa, preservada como limitação aberta, apesar de cinco execuções posteriores bem-sucedidas desse cenário. **Não é aceite operacional: F3-05/G4 permanece aberto.**

## Correção importante: duas operações diferentes

[Update-With-Start não é atômico](https://docs.temporal.io/sending-messages): o Workflow pode iniciar mesmo se o Update não for entregue. O protótipo anterior usou essa operação; seu nome de arquivo e helper `admitir_atomico` eram enganadores. O código anterior foi preservado, e sua evidência recebeu uma errata explícita. Uma resposta bem-sucedida daquele Update confirma o que seu handler validou/enfileirou, não atomicidade entre Start e Update, nem execução do pedido.

[Signal-With-Start é uma operação atômica de start+signal no serviço](https://docs.temporal.io/design-patterns/signal-with-start): inicia quando necessário e entrega o Signal à execução correspondente. **O Signal é assíncrono, fire-and-forget:** a resposta da RPC não diz que o handler o processou, que o pedido foi aceito pelo ator ou que a Activity concluiu. Não há confirmação síncrona de negócio implementada aqui. Tampouco há exactly-once de efeitos externos. A atomicidade documentada não foi demonstrada por injeção de falha entre persistências internas do servidor.

## O que foi criado, separadamente

- [`prototipo_signal_with_start.py`](../../tests/workflows/prototipo_signal_with_start.py): ator sintético e helper `enviar_signal_with_start`.
- [`test_f3_05_signal_with_start_isolado.py`](../../tests/workflows/test_f3_05_signal_with_start_isolado.py): dez cenários opt-in, Activities falsas em memória.
- [`run_f3_05_signal_with_start_isolado.sh`](../../tests/workflows/run_f3_05_signal_with_start_isolado.sh): isolamento obrigatório, binário local sem download e prazo externo de 180 segundos.

O SDK Python local é **1.34.0**. `Client.start_workflow(..., start_signal="solicitar", start_signal_args=[envelope])` usa realmente `SignalWithStartWorkflowExecution`, conforme inspeção do SDK; não é uma composição manual de duas RPCs. O helper usa `USE_EXISTING` e, por padrão, `REJECT_DUPLICATE`. Retorna somente o handle do serviço.

O ID do Workflow é prefixo exclusivo mais SHA-256 da sessão UTF-8 exata. Cada envelope tem configuração e pedido sintético `{id, sessao, falhar}`. O ator guarda ID e payload completo: ID/payload iguais produzem observação `duplicado`; mesmo ID com payload diferente produz `payload_divergente`, sem novo despacho. Configuração divergente também é sinalizada no estado. **Todas essas chamadas de Signal podem retornar normalmente:** os resultados são observados posteriormente por Query ou no resultado terminal, não retornados pelo Signal.

Só o laço principal executa e aguarda uma Activity por vez. Handlers de Signal apenas validam e alteram estado. Filas de Workflow e Activity são próprias, com prefixos `teste-sws-wf-` e `teste-sws-act-`; não há importação de backends PQBR. Workers de Activity têm capacidade 4 cada, portanto a serialização não é causada por capacidade global 1.

## Resultados observados

A [execução final](evidencias-f3-05-signal-with-start-20261017/execucao-v2.log) terminou com **10 testes executados em 5,110 s: 9 aprovados e 1 pulado**.

1. **Start+Signals concorrentes:** 12 primeiras chamadas de dois clientes/runtimes convergiram para um run na execução final. Os 12 pedidos foram processados na ordem observada pelo ator, sem presumir ordem entre chamadores concorrentes. Máximo ativo por sessão: 1; intervalos das Activities não se sobrepuseram. A primeira tentativa, porém, recebeu `WorkflowAlreadyStartedError` em uma chamada da corrida. Um diagnóstico isolado e três repetições limitadas, além da execução final, passaram. Não foi implementado retry de aplicação nem fallback Start+Signal. A recusa inicial permanece falha intermitente não explicada do ambiente SDK/test-server; não afirmamos que a corrida esteja robustamente validada nem atribuímos causa interna sem prova. Os logs originais estão preservados.
2. **ID repetido e payload divergente:** quatro Signals retornaram normalmente. O estado mostrou `aceito`, `duplicado`, `payload_divergente` e `configuracao_divergente`. Houve uma única Activity. A divergência não mata o ator nem fabrica erro síncrono para o cliente.
3. **Destino sem Worker de Workflow:** a RPC retornou em até 5 s; havia um evento de start e um de Signal, nenhum Workflow Task concluído e nenhuma Activity executada. Um segundo envio igual foi persistido. Quando o Worker efêmero apareceu, o mesmo run processou os Signals e despachou uma única Activity. O [histórico anterior ao Worker](evidencias-f3-05-signal-with-start-20261017/runtime-v2/sem-worker-antes.history.json) torna explícita a diferença entre aceitação no serviço e processamento no ator.
4. **Duas sessões:** Activities falsas atingiram simultaneamente uma barreira. Máximo global: 2; máximo por sessão: 1. É concorrência assíncrona observada, não benchmark de CPU.
5. **Ator encerrando/fechado:** Signal novo durante drenagem recebeu resposta RPC normal, mas foi sinalizado como `encerrando`. Após `COMPLETED`, `REJECT_DUPLICATE` recusou reabertura do ID ainda retido. Com `ALLOW_DUPLICATE` explicitamente escolhido somente no teste, houve outro run e o mesmo ID de operação executou novamente.
6. **Retenção/remover registro:** o servidor efêmero respondeu `UNIMPLEMENTED` a `DeleteWorkflowExecution`. O cenário foi **pulado**, com [limitação registrada](evidencias-f3-05-signal-with-start-20261017/runtime-v2/retention-nao-validada.json). Não houve espera de expiração, alteração de retention, remoção simulada bem-sucedida ou validação de reuso após expiração. A política de ID não é memória permanente: conforme [documentação de Workflow ID](https://docs.temporal.io/workflow-execution/workflowid-runid), depende das execuções fechadas ainda retidas. Esse teste permanece pendente em servidor compatível, sob autorização separada.
7. **Falha técnica:** a exceção da Activity propagou como `FAILED`, tentativa 1, sem timer, retry, fallback, sucesso fictício ou despacho do pedido seguinte já aceito. `REJECT_DUPLICATE` bloqueou reentrada. Reuso explícito com `ALLOW_DUPLICATE` criou novo run e repetiu a mesma Activity falha, demonstrando perda da deduplicação entre execuções independentes. É somente fake; não teste de efeito externo real.
8. **Continue-As-New preservando IDs/payloads:** a fila foi drenada e o mapa de deduplicação e os concluídos foram passados no input do novo run. Reenvio do mesmo ID foi `duplicado`; uma Activity no total.
9. **Continue-As-New sem preservar estado:** o mesmo reenvio foi aceito no novo run e gerou a segunda Activity. Isso demonstra que o histórico antigo não transfere sozinho a deduplicação de negócio.
10. **Worker recriado:** após concluir a primeira Activity, o Worker daquela fila foi encerrado. O Signal duplicado foi enviado sem consumidor e outro Worker, com runtime independente, reconstruiu o estado do histórico; nenhuma segunda Activity foi executada. Não foi crash de máquina/processo nem falha entre efeito real e conclusão de Activity.

Os [15 resumos finais](evidencias-f3-05-signal-with-start-20261017/runtime-v2/) registram **11 `COMPLETED`, 2 `FAILED` esperados e 2 `CONTINUED_AS_NEW`**, todos sem Activity pendente. Todos passaram no `Replayer` com sandbox padrão e `raise_on_replay_failure=True`. Incluem a execução concluída antes da tentativa não suportada de remoção. Uma conferência offline adicional passou nos [31 históricos capturados](evidencias-f3-05-signal-with-start-20261017/replay-todos.json), inclusive o parcial sem Worker e os das tentativas anteriores.

## Tentativas preservadas e limites de deduplicação

A [primeira tentativa](evidencias-f3-05-signal-with-start-20261017/execucao-v1.log) teve 6 aprovações e 4 erros: corrida inicial, duas Queries durante a troca de run e remoção não implementada. O [diagnóstico de Continue-As-New](evidencias-f3-05-signal-with-start-20261017/diagnostico-continue.log) reproduziu o timeout de Query. O harness final espera a mudança de run ID via `Describe` e consulta explicitamente o novo run; não mudou a lógica do ator para ocultar falha. O teste de remoção foi convertido em skip explícito apenas para `UNIMPLEMENTED`. O cenário concorrente continua estrito e falha se qualquer RPC for recusada; preserva também resultados individuais antes de falhar. Três [repetições](evidencias-f3-05-signal-with-start-20261017/concorrencia-repeticao-1.log) adicionais limitadas passaram, sem apagar a falha inicial.

A deduplicação existe no estado/histórico do ator enquanto IDs e payloads forem mantidos. Falha de Worker com replay não apaga esse estado; falha terminal pode deixar pedidos aceitos sem execução, e novo run independente não o herda. Continue-As-New exige carregar estado necessário e tratar mensagens/handlers pendentes; neste fake os handlers são síncronos e a fila é drenada. Não foram provadas todas as corridas de Signal no limite de Continue-As-New/fechamento, migração, Reset ou perda/restauração do servidor. Não há armazenamento externo de deduplicação, reconciliação, expiração segura de IDs ou protocolo de confirmação por pedido.

O mapa, a fila e as observações não têm limite: não são prontos para produção. Faltam backpressure, autorização, versionamento, definição da janela de deduplicação e validação de carga. Uma Activity real pode efetuar a ação e falhar antes de registrar conclusão; pode continuar após timeout. O ator não oferece fencing ou exactly-once de efeitos externos. O hash não anonimiza sessões previsíveis nem elimina matematicamente colisões.

## Isolamento e preservação

Cada execução usou servidor local `/tmp/temporal-test-server-sdk-python-1.34.0`, SHA-256 `19defb9f7318c7cf249518b3642a735efb79876c2b6918afe312336476b796a5`, namespaces de usuário/rede/PID e `/proc` isolado, somente loopback e nenhuma rota externa. Ambiente limpo via `env -i`, HOME/TMPDIR temporários, sem credenciais operacionais ou download. O servidor foi encerrado pelo cleanup e o namespace de PID eliminou descendentes. O aviso de capacidade de heartbeat do test-server foi preservado; não valida heartbeat nem equivalência plena com servidor operacional.

A [verificação anterior à documentação](evidencias-f3-05-signal-with-start-20261017/verificacao-pre-documentacao.json) confirmou hashes idênticos dos **89 arquivos preexistentes cobertos pelo manifesto** (fontes Python, testes anteriores, runners anteriores e evidências F3-05 permitidas) e zero processos nos namespaces de rede usados. A [verificação final](evidencias-f3-05-signal-with-start-20261017/verificacao-final.json) separa apenas as três alterações documentais intencionais: esta correção no relatório de Update-With-Start, a nota de esclarecimento no relatório original de ator e o roadmap. A evidência nova não existia no baseline. Nenhum documento restrito foi consultado.

**Protótipos anteriores, workflow operacional e Workers persistentes ficaram intactos.** Não houve mudança de configuração, produção, serviço persistente, commit ou push. A política de exceção técnica permanece intacta. **F3-05/G4 aberto; F7-02/seu G7 e PQBR-114 pausados; F05-06 no-arm.** O roadmap registra somente o protótipo e seus limites.

Para reproduzir somente sob autorização de teste isolado, com diretório de saída inexistente:

```sh
cd /home/pc/Workspace/PQBR
sh tests/workflows/run_f3_05_signal_with_start_isolado.sh /tmp/pqbr-signal-with-start-nova-evidencia
```
