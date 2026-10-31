# F3-05 — Update-With-Start no ator por sessão (não atômico)

> **Errata técnica, 2026-10-17:** Update-With-Start **NÃO é atômico**. O Workflow pode iniciar mesmo se o Update não for entregue; rejeição/falha do Update não desfaz o start. O nome histórico deste arquivo, do protótipo `prototipo_admissao_atomica.py` e do helper `admitir_atomico` não descreve uma garantia real de atomicidade. O código anterior foi preservado. [Semântica oficial](https://docs.temporal.io/sending-messages).
>
> A variante posterior [Signal-With-Start](f3-05-signal-with-start-20261017.md) é outro protótipo: start+signal atômico no serviço, mas Signal fire-and-forget, sem confirmação síncrona de processamento e sem exactly-once de efeitos externos. Não confundir as duas operações.

**Este protótipo passou nos 10 cenários sintéticos, com 11 históricos aprovados no replay.** A entrada usa Update-With-Start em vez de duas chamadas de negócio independentes no cliente, mas isso **não torna start+update atômicos**. A resposta bem-sucedida do Update confirma a validação/enfileiramento feita pelo handler, não a execução da Activity. O próprio cenário de primeiro pedido inválido abaixo já mostrou o Workflow iniciado apesar da rejeição. F3-05/G4 continua aberto.

## O que mudou

Foram criados três arquivos, sem modificar o protótipo anterior ou o código operacional:

- [`prototipo_admissao_atomica.py`](../../tests/workflows/prototipo_admissao_atomica.py): ator sintético separado e helper `admitir_atomico`.
- [`test_f3_05_admissao_atomica_isolado.py`](../../tests/workflows/test_f3_05_admissao_atomica_isolado.py): testes opt-in com Activities falsas.
- [`run_f3_05_admissao_atomica_isolado.sh`](../../tests/workflows/run_f3_05_admissao_atomica_isolado.sh): runner isolado com binário Temporal já disponível localmente, sem download.

O helper chama `Client.execute_update_with_start_workflow` com `WithStartWorkflowOperation`, `USE_EXISTING` e `REJECT_DUPLICATE`. O SDK local é o Python 1.34.0. A identidade tem prefixo próprio e SHA-256 da sessão UTF-8 exata, sem normalização implícita.

O Update síncrono compara a configuração esperada com a fixada pelo primeiro start, valida o pedido e o enfileira. A comparação inclui sessão, fila do workflow, fila da Activity e prazo. O resultado bem-sucedido confirma **admissão**, não execução da Activity. Somente o laço principal do ator despacha trabalho, aguardando cada Activity antes da próxima.

Há duas deduplicações: o Update ID estável deriva do envelope JSON canônico, incluindo pedido e configuração; o ator também guarda ID de pedido e payload. Um reenvio idêntico pode receber o resultado original `aceito` do SDK, sem novo enfileiramento. Um payload diferente para o mesmo ID gera outro Update ID e chega à validação do ator, que o rejeita. Uma chamada com outro Update ID e payload igual retorna `duplicado`.

## O que os testes mostraram

A [execução final](evidencias-f3-05-admissao-atomica-20261017/execucao-v2.log) terminou com **10 testes aprovados em 7,752 s**:

1. **Criação concorrente:** 12 pedidos iniciais, distribuídos entre dois clientes/runtimes, convergiram para um único run ID. Todos foram admitidos; a ordem de execução correspondeu à ordem de admissão observada no ator, não a uma ordem presumida entre chamadas concorrentes. Máximo ativo por sessão: 1, com dois Workers de workflow e dois de Activity disponíveis.
2. **Resposta descartada e reenvio:** o teste descartou deliberadamente a resposta de uma chamada já completada e a reenviou. Houve uma única Activity. Payload divergente foi rejeitado e a deduplicação de negócio também foi exercitada com outro Update ID. Isso não simula uma quebra real de conexão.
3. **Configuração divergente:** mudança de prazo ou de qualquer fila foi rejeitada, sem admitir o pedido.
4. **Configurações concorrentes:** entre dois primeiros pedidos com prazos diferentes, apenas o compatível com a configuração do primeiro start foi admitido. Não há reconfiguração implícita.
5. **Sem Worker de workflow:** a chamada permaneceu pendente durante a janela de 0,15 s. Após iniciar um Worker exclusivamente efêmero, ela completou; o reenvio usou o mesmo run ID e gerou uma só Activity. Não existe confirmação antecipada de admissão sem processamento do Update.
6. **Sessões diferentes:** duas Activities falsas ficaram ativas simultaneamente, com máximo 1 por sessão e 2 global. É concorrência assíncrona, não benchmark de CPU.
7. **Sem consumidor de Activity:** timeout `SCHEDULE_TO_CLOSE`, uma Activity agendada, workflow terminal e nenhuma Activity pendente. Consumidores efêmeros iniciados depois não executaram a tarefa na janela observada de 0,3 s.
8. **Exceção técnica:** a falha propagou, tentativa 1, sem retry, fallback, timer ou despacho do pedido seguinte. Reentrada em ator falho foi rejeitada.
9. **Fechamento:** pedidos previamente aceitos foram drenados; pedido novo após o signal foi rejeitado. A execução encerrada não foi reaberta.
10. **Primeiro pedido inválido:** o Update falhou, mas o ator permaneceu `RUNNING`, com fila vazia, e depois aceitou um pedido válido. **A rejeição não desfaz o start.**

Os [11 históricos e resumos finais](evidencias-f3-05-admissao-atomica-20261017/runtime-v2/) passaram no `Replayer` com sandbox padrão e erro de replay fatal: nove execuções `COMPLETED` e duas `FAILED` esperadas, todas sem Activity pendente. Os eventos verificam fila explícita, prazos finitos e `maximum_attempts=1`.

## O que ainda não está garantido

A operação delega ao servidor o start/reuso junto ao envio do Update, em vez de depender de duas RPCs de negócio separadas. **Não testamos uma queda do servidor entre persistências internas.** Não afirmamos atomicidade end-to-end entre Temporal e um backend externo.

A [primeira execução de desenvolvimento](evidencias-f3-05-admissao-atomica-20261017/execucao-v1.log) foi preservada: seis testes passaram e três deram erro. Dois eram expectativas incorretas sobre a exceção de reabertura: nessa API/versão, o retorno é `RPCError(ALREADY_EXISTS)`, não `WorkflowAlreadyStartedError`. O helper agora também consome a exceção espelhada no Future público do handle e relança a original; isso não captura nem converte a exceção técnica da Activity.

O terceiro erro ocorreu ao tentar um deadline de RPC sem Worker de workflow: o servidor efêmero retornou `RPCError UNKNOWN`, com `Application error processing RPC`. **Recuperação após deadline RPC real permanece não validada.** Esse cenário não integra os dez aprovados; o teste final distinto demonstra espera sem Worker e posterior processamento, sem alegar equivalência com timeout. Não se trocou de servidor nem se acessou rede externa para contornar a limitação.

A exclusão é interna ao ator, no mesmo namespace e espaço de IDs. Não cobre ingressos que o contornem, outros namespaces ou efeitos de uma Activity real que continue após timeout. Não fornece fencing nem exactly-once de efeitos externos. `USE_EXISTING` não reconfigura o ator: a divergência é rejeitada pelo Update, não pela opção de start.

Pedido aceito pode ficar sem executar após uma falha técnica ou timeout anterior. Não foram implementados reconciliação, resposta final por pedido, autorização, backpressure, limites de fila, retenção de deduplicação, Continue-as-New, migração ou reabertura após retenção. O ator pode permanecer vazio após uma rejeição inicial, até fechamento explícito ou o prazo total sintético de dois minutos. A validação de prefixos é proteção do harness, não fronteira de segurança. O hash da sessão não é anonimização de identificadores previsíveis nem prova matemática contra colisões.

## Isolamento e preservação

As duas execuções utilizaram namespaces efêmeros de usuário/rede/PID, somente loopback, sem rota externa, ambiente limpo via `env -i`, HOME/TMPDIR temporários, timeout externo e binário local explícito. O SHA-256 do servidor foi `19defb9f7318c7cf249518b3642a735efb79876c2b6918afe312336476b796a5`. O aviso de capacidade de heartbeat do test-server permanece uma limitação conhecida, não validação de heartbeat operacional.

A [verificação final](evidencias-f3-05-admissao-atomica-20261017/verificacao.json) confirmou **437 arquivos preexistentes permitidos com hashes idênticos** e **zero processos nos namespaces dos testes**. Os números de namespace foram reutilizados pelo sistema entre execuções; a verificação posterior comprova ausência de processos remanescentes naquele momento. Fontes, Workers persistentes, alterações locais anteriores e protótipo anterior foram preservados. Os caminhos restritos foram excluídos antes da leitura e do hash.

A [regressão offline selecionada](evidencias-f3-05-admissao-atomica-20261017/regressao.log), também sem rede e com ambiente limpo, retornou **273 passed, 39 skipped, 2 xfailed em 2,05 s**. Foram selecionados `tests/unit`, `tests/seguranca` e `tests/workflows/test_f3_05*`, sem opt-in. Não é a suíte completa: os workflows de produção/correção não foram executados. Os dois XFAIL anteriores continuam abertos.

Não houve backends reais, serviços persistentes iniciados/reiniciados, implantação, commit ou push. **A política de exceção técnica atual permanece intacta. F3-05/G4 fica aberto; F7-02/G7 e PQBR-114 ficam pausados; F05-06 permanece no-arm.** Esta evidência não altera regras nem autoriza adoção operacional.

Para reproduzir, somente dentro da autorização de teste isolado e com diretório de saída inexistente:

```sh
cd /home/pc/Workspace/PQBR
sh tests/workflows/run_f3_05_admissao_atomica_isolado.sh /tmp/pqbr-admissao-atomica-nova-evidencia
```
