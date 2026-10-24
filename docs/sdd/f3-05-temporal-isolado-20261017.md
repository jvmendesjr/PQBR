# F3-05 — Temporal validado em servidor efêmero isolado

**14 testes passaram e os 14 históricos capturados passaram no replay.** A execução usou o workflow real com Activities falsas, sem rede externa, backends ou produção. O servidor de testes e seu namespace foram encerrados. **F3-05/G4 continua aberto.**

## As duas lacunas mais importantes

**Não existe espera entre intervenções.** No cenário corrigido na terceira tentativa, o histórico não contém `TimerStarted`. As três intervenções foram agendadas em `13:21:31.915Z`, `13:21:31.967Z` e `13:21:32.027Z`; seus limites de execução foram 503, 804 e 702 segundos. Isso confirma que o código configura timeouts de 5–15 minutos, mas não implementa o intervalo entre tentativas exigido por `REGRAS.md` §0, item 8. O teste caracteriza a lacuna; sua aprovação não é aceite desse requisito.

**Exceção técnica na intervenção aborta o fluxo.** Uma `ApplicationError` sintética na primeira intervenção produz falha do workflow, sem nova intervenção, verificação ou chamada ao registro falso. A política `maximum_attempts=1` é aplicada, mas não existe tratamento no workflow que converta essa exceção na escada de correção ou em resultado registrado. Não foi acionado nenhum canal de aviso real. Esse caminho não deve ser confundido com a resposta de negócio `resolvido=False`, para a qual o laço de até três intervenções funciona.

Nenhuma dessas lacunas foi corrigida nesta tarefa, que foi autorizada para testes isolados. O código de produção permaneceu intacto.

## O que agora foi verificado

A suíte nova `tests/workflows/test_f3_05_temporal_isolado.py` executa `CorrecaoAutonomaWorkflow` no runtime Temporal, sem substituir seu executor nem sua aleatoriedade:

- Sucesso na primeira e terceira intervenções; esgotamento após três respostas negativas; verificação negativa impedindo sucesso.
- Interrupção diante de passo sensível, triagem fora de escopo e resposta de conta divergente. Esse último caso testa a resposta simulada, não uma checagem real de conta antes da ação.
- Ausência de backend propagando `EmConstrucao` não repetível, com uma execução de triagem e sem intervenção ou registro.
- Retries efetivos de triagem, verificação e registro falso: as Activities receberam tentativas 1, 2 e 3. A triagem que continua falhando para na terceira execução. Retry automático de Activity e nova intervenção do laço são contados separadamente.
- Intervenção configurada com uma execução por Activity, timeouts sorteados registrados no histórico e transporte de argumentos/resultados Pydantic pelo servidor/Worker.
- Troca de Worker: o primeiro agenda a triagem, sem executar Activities; após seu encerramento, outro Worker conclui a mesma execução, no mesmo servidor e fila, sem intervenção nem registro duplicados nesse cenário.
- Replay, com sandbox padrão, dos 14 históricos reais capturados por `fetch_history()`, recarregados do JSON e processados por `Replayer` com falhas de replay habilitadas. Não foram fabricados eventos.

O registro falso mantém resultados somente em memória. As outras três Activities falsas são invólucros tipados que chamam exclusivamente os caminhos simulados ou de falha fechada das funções existentes. O escritor real `registrar_correcao`, Jev, Paperclip, Camofox, outbox e Hindsight não foram acionados.

## Isolamento e encerramento

O proprietário autorizou nesta conversa o servidor efêmero isolado para testes Temporal. O runner novo `tests/workflows/run_f3_05_isolado.sh` usa:

- `unshare` com namespaces de usuário, rede, PID e montagem de `/proc`; somente a interface `lo` foi habilitada, sem rotas externas.
- Ambiente `env -i`, sem credenciais/proxies herdados, e HOME/TMPDIR temporários exclusivos.
- Binário existente passado explicitamente em `test_server_existing_path`, sem downloads: `/tmp/temporal-test-server-sdk-python-1.34.0`, SHA-256 `19defb9f7318c7cf249518b3642a735efb79876c2b6918afe312336476b796a5`.
- Fila e identificador de workflow exclusivos por teste, timeout externo de 300 segundos, encerramento do servidor por cleanup e eliminação dos descendentes com o namespace PID.
- Ativação opt-in: fora do runner, os 14 testes são pulados; o setup também recusa o namespace do host, interfaces adicionais ou rotas IPv4.

O namespace de rede da execução foi `net:[4026533133]`, distinto do host `net:[4026531840]`. Após o término, não havia processos nesse namespace. Dois processos do mesmo binário encontrados no host haviam começado em 15/10/2026, antes desta tarefa; foram apenas identificados e permaneceram intocados.

O SDK emitiu aviso de que o test-server não anuncia a capacidade `activity_failure_include_heartbeat`; preservação de heartbeat em falhas não foi testada nem é alegada.

## Resultados e reprodução

No checkout `/home/pc/Workspace/PQBR`:

```sh
# Opt-in com servidor isolado: 14 testes, OK, em 7,520 s.
# Se informado, o diretório de evidência deve ainda não existir.
sh tests/workflows/run_f3_05_isolado.sh /tmp/pqbr-f3-05-minha-nova-execucao

# Regressão sem servidor/opt-in: 269 passed, 14 skipped.
unshare --user --map-root-user --net -- \
  env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/seguranca tests/unit tests/test_kit.py \
  tests/workflows/test_f3_05_temporal_isolado.py
```

Os 14 históricos e seus 14 resumos estão em `docs/sdd/evidencias-f3-05-temporal-isolado-20261017/`. Cada resumo identifica o workflow, chamadas/tentativas, resultado ou falha e replay aprovado. `SHA256SUMS` registra os hashes dos históricos, resumos, arquivos novos de teste e fonte do workflow. O log da execução está em `execucao.log`.

## O que ainda não foi comprovado

O replay cobre estes 14 históricos sintéticos de teste e esta versão do código, não todos os caminhos, históricos de produção ou compatibilidade entre versões. A retomada foi uma troca controlada de Worker no mesmo servidor efêmero, não queda abrupta de processo, reboot, perda de servidor, disco ou durabilidade persistente. Não houve teste de concorrência por sessão na configuração real, disparo efetivo de timeout, heartbeat ou relógio de produção. As condições de fila e concorrência são exclusivas do harness e não validam os Workers implantados.

Continuam pendentes os backends reais Jev/Paperclip e persistência por outbox/Hindsight. Os próximos passos seguros são tratar as duas lacunas em tarefa própria, com testes de regressão isolados, e planejar separadamente durabilidade, concorrência e integração, sem inferir autorização para produção.

## Preservação dos limites

Foram adicionados apenas a nova suíte, seu runner, esta evidência e o diretório de artefatos desta execução. Os cinco hashes conferidos antes e depois permaneceram iguais: `correcao.py`, `test_f3_05_local.py`, `test_f3_05_sdk_offline.py`, `test_correcao_retencao.py` e a evidência `f3-05-sdk-offline-20261017.md`. Nenhuma alteração preexistente foi sobrescrita.

Não houve commit, push, dependência instalada, serviço real iniciado/reiniciado, ativação ou gate fechado. F7-02/seu G7 e PQBR-114 permanecem pausados; F05-06 permanece no-arm. Não foram consultados `docs/arquivo/`, `docs/pesquisas/`, `docs/DECISOES-LOG.md`, contrato editorial restrito ou material legado. A documentação autoritativa e as evidências anteriores não foram editadas.
