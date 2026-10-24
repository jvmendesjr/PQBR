# F3-05: integração candidata local, sem ativação

**A candidata passou nos 10 testes de runtime e nos 81 testes da regressão em memória, dos quais 21 são novos. As 40 capturas de histórico de 38 runs distintos passaram no replay com o código candidato atual. F3-05/G4 permanece aberto.** Não há ligação aos Workers persistentes, deploy ou produção.

## O que está integrado no código candidato

O novo [`candidato_sessao.py`](../../src/pqbr/workflows/candidato_sessao.py) contém o ator `PQBRAtorSessaoCandidato`, o workflow filho `PQBRCorrecaoCandidata` e o helper de Signal-With-Start. Nenhum módulo existente de execução foi alterado. Os módulos `worker.py` e `worker_camofox.py` não foram importados nem editados; os `__init__.py` existentes também ficaram intactos. A candidata não foi acrescentada a registro, entrypoint, configuração ou unit de nenhum Worker persistente.

O helper usa a RPC Signal-With-Start do SDK, com `USE_EXISTING`, `REJECT_DUPLICATE` e ID do ator derivado da sessão UTF-8 exata. Retorna somente o handle do serviço. **Signal-With-Start é fire-and-forget: resposta da RPC não significa que o handler processou o pedido, que houve aceite de negócio ou que uma ação terminou.** O estado posterior é consultável por Query; o resultado terminal também contém resultados por operação. Isso não é um protocolo durável de ACK por pedido.

O handler síncrono valida sessão, versão, configuração e payload normalizado pelo contrato `PedidoCorrecao`; registra ID/payload e apenas enfileira. ID e payload iguais são duplicados; o mesmo ID com payload diferente é recusado no estado observável, sem substituir o original. Configuração ou versão divergente também não despacha. Não se presume ordem entre chamadores concorrentes: a ordem seguida é a observada pelo ator.

Somente o laço principal despacha. Ele aguarda **todo o workflow de correção de uma operação** antes de iniciar a próxima da mesma sessão, evitando intercalar triagem/intervenção/verificação entre operações. Sessões distintas possuem atores independentes. O filho tem ID derivado da sessão e operação e não é reaberto automaticamente.

A candidata preserva contratos, Activities e tratamento atual da correção: triagem/verificação/registro com até três tentativas técnicas; intervenção com `maximum_attempts=1`; até três respostas de negócio negativas, com duração e espera Camofox sorteadas deterministicamente entre 300 e 900 segundos. A intervenção tem `task_queue` Camofox **explícito**, separado da fila de workflow; as outras Activities também têm fila explícita. Os prefixos aceitos são exclusivamente `teste-f3-05-candidato-wf-` e `teste-f3-05-candidato-camofox-`: filas operacionais são bloqueadas na validação. Não se alterou o workflow operacional de correção.

**Exceção técnica na intervenção continua propagando como falha terminal**, sem retry da intervenção, fallback, reconciliação por leitura, sucesso fictício ou execução da operação seguinte. Isso também falha o ator: pedidos já aceitos podem permanecer sem execução, e `REJECT_DUPLICATE` impede reabrir esse ID enquanto a execução terminal estiver retida. Esse bloqueio é um limite de lifecycle conhecido, não uma recuperação implementada ou uma mudança de política. A revisão futura da política de exceção técnica no roadmap permanece intocada.

## Registro experimental, somente para testes

[`composicao_candidata.py`](../../tests/workflows/composicao_candidata.py) cria explicitamente dois Workers **efêmeros**: workflow/Activities de controle e Activity falsa de intervenção Camofox. Importar a composição não inicia Worker. A fábrica exige opt-in e namespace sintético `f3-05-candidate`. Ambos têm capacidade de Activity 8; a serialização não depende de uma trava global ou capacidade 1.

As Activities de intervenção, verificação e registro são falsas, em memória. A triagem usa o contrato e a trava sensível atuais com simulação sintética. Não houve chamada a Camofox, Paperclip, Jev real, banco do app, Hindsight, conta, login ou efeito externo. A composição não é importada por nenhum entrypoint persistente.

## O que os testes demonstraram

A [execução final](evidencias-f3-05-integracao-candidata-20261017-C3/candidate-test.log) passou **10/10 em 18,597 s**, no Temporal Server **1.32.1**, SDK Python **1.34.0**:

| Cenário | Resultado observado |
|---|---|
| 12 primeiras chamadas concorrentes, mesma sessão | Um run; 12 correções na ordem aceita; máximo ativo por sessão 1; intervalos das intervenções sem sobreposição. |
| Sessões diferentes | Duas intervenções falsas simultâneas, máximo global 2 e por sessão 1. É concorrência assíncrona observada, não benchmark de CPU. |
| Fila de workflow sem consumidor | Duas RPCs retornaram; histórico tinha dois Signals e nenhum Workflow Task concluído. Ao iniciar o consumidor efêmero, o mesmo run executou uma única operação e reconheceu o duplicado. |
| Fila Camofox sem consumidor | Triagem ocorreu, intervenção ficou agendada para a fila explícita, sem execução pelo Worker de controle. O consumidor tardio executou a intervenção pendente. Não se aguardou timeout de 5–15 min. |
| Dedup, divergências e versão | Um despacho apesar dos reenvios; divergências de payload/configuração/versão registradas no estado. Envelope v1 sem campo de versão continuou compatível. |
| Exceção técnica | Uma intervenção falha, tentativa 1; nenhum registro de sucesso, timer de espera ou operação seguinte. Ator e filho falharam; tentativa posterior de reabertura foi recusada. |
| Worker de teste recriado | Histórico reconstruiu dedup; reenvio não executou nova intervenção. Não foi crash de máquina nem falha entre efeito real e confirmação de Activity. |
| Continue-As-New | Fila drenada; IDs/payloads e resultados transferidos; reenvio no novo run permaneceu duplicado. |
| Replay/versionamento | Histórico realmente gerado pela fixture V1 sem patch foi gravado e reproduzido pelo `Replayer` com a classe candidata atual. Execução nova gravou o patch e usou ID estável de Activity. Ambos passaram no replay. |
| Travas sensíveis e conta divergente | Login sensível não chamou intervenção; conta divergente interrompeu antes de verificar. |

Cada histórico capturado é reproduzido com sandbox padrão e `raise_on_replay_failure=True`. A [pasta runtime](evidencias-f3-05-integracao-candidata-20261017-C3/runtime/) contém **40 capturas**, incluindo duas capturas parciais, de **38 runs distintos**, resumos de fila/política/timeout e dez resultados com intervalos das Activities falsas. Não confundir capturas com runs nem somar contagens de Activities de capturas repetidas como novas execuções.

A [regressão em memória](evidencias-f3-05-integracao-candidata-20261017-C3/regression.log) passou **81/81**: 60 testes preexistentes de F3-05 local/SDK e 21 novos de validação, ingresso, roteamento, escada de três respostas negativas e preservação das opções de patch. A [execução unitária isolada](evidencias-f3-05-integracao-candidata-20261017-C3/unit.log) passou 21/21; esses 21 estão incluídos nos 81, não são contagem adicional. A escada longa de negócio foi validada em memória; não se acelerou nem se aguardou os timers reais de 5–15 min nesta suíte em containers.

## Compatibilidade e limites que continuam abertos

O esquema candidato é v1; campo ausente equivale a v1, e versões incompatíveis são recusadas sem despacho. Tipos de Workflow são novos: **não houve migração nem adoção de históricos dos tipos operacionais**. O patch `f3-05-candidato-intervencao-id-v2` acrescenta ID estável à intervenção; replay anterior ao marcador conserva o comando com ID automático. A fixture V1 produz um histórico real sem esse patch e o código atual o reproduz. Isso valida essa mudança específica, não qualquer alteração futura, Reset, migração, Worker Deployment Versioning ou todos os pontos de suspensão possíveis.

Continue-As-New sempre transfere IDs/payloads e resultados nesta candidata, mas todas as corridas de fechamento/Signals e retomada não foram exauridas. O fechamento drena a fila já aceita e não admite operações novas. A deduplicação não sobrevive por si só a expiração de retention, novo workflow independente, perda/restauração do servidor ou migração sem estado. Há limite experimental de 1.000 IDs, sem remoção silenciosa; observações e histórico ainda podem crescer sem limite. Autorização, confirmação durável por pedido, janela de dedup, recuperação de ator falho e proteção contra efeitos tardios não foram implementadas.

**Não há exactly-once de efeitos externos nem fencing.** Uma Activity real pode efetuar uma ação e perder a confirmação, ou continuar depois de timeout. Serialização pelo ator e dedup de pedidos no histórico não resolvem essa incerteza. Nenhum efeito externo real foi exercitado.

A comparação anterior continua sendo apenas evidência limitada: **7 `ALREADY_EXISTS` em 27.600 chamadas no test-server; zero em 13.800 chamadas de rajada no Temporal Server 1.32.1 em containers**, além das chamadas-semente contabilizadas separadamente. Não se repetiu esse stress nesta integração; o caso novo tem somente 12 chamadas concorrentes. Nem a comparação nem a candidata provam robustez geral ou validam produção. Referências preservadas: [stress anterior](f3-05-sws-stress-20261017.md) e relatório anterior no PC `/tmp/pqbr-sws-containers-20261017-hdPt5X/resultado.md`.

## Tentativas reprovadas, sem apagar evidência

A [primeira preparação](evidencias-f3-05-integracao-candidata-20261017/orchestrator.log) passou no gate de rede, mas parou antes de iniciar Temporal/testes: `pg_isready` aceitou o servidor temporário do initdb antes de o banco sintético existir. A sondagem foi corrigida para exigir `SELECT 1` por TCP no banco final. Runner inicial, logs e cleanup foram preservados.

A [segunda execução](evidencias-f3-05-integracao-candidata-20261017-B2/candidate-test.log) passou no isolamento e executou os dez testes: **9 passaram e 1 falhou numa asserção do harness**, que procurava o texto do patch no JSON sem decodificar `Payload.data` em base64. O marcador estava gravado no histórico. O harness reprovado e todos os históricos foram preservados. A correção decodifica o payload protobuf, exige o ID esperado e acrescenta assertions de fila/tentativas/timeout para cada Activity capturada. Só o harness mudou entre essa execução e a final; o módulo candidato não foi alterado para ocultar a falha.

As três preparações usam diretórios distintos. Falhas de preparação e harness não são tratadas como aprovação ou reenvio compensatório de pedidos. Não houve falha do gate de isolamento, relaxamento desse gate ou uso do test-server anterior.

## Isolamento, preservação e reprodução

O [runner novo](../../tests/workflows/run_f3_05_candidate_container.py) exige imagens **já locais**, sempre com `--pull=never`: `temporalio/server:1.32.1`, `temporalio/admin-tools:1.32.1` e `postgres:17-alpine`. Rede Docker `internal`, gateway `isolated`, sem portas publicadas, sem segunda rede, sem IPv6 nos containers e sem endereço na bridge do host. Somente a bridge recém-criada teve IPv6 desabilitado. O gate confere ausência de rotas default IPv4/IPv6 e destinos de documentação sem rota, usando apenas consulta de rota, sem tráfego externo.

O gate é obrigatório antes do Postgres/Temporal/testes; qualquer falha aborta. O cliente e Workers efêmeros rodam no namespace de rede do servidor descartável, como UID 1000, em `env -i`, endpoint `127.0.0.1:7233`, namespace sintético, sem credenciais operacionais e sem downloads. O Postgres usa tmpfs, sem volume persistente; o servidor recebe apenas configuração sintética read-only. Há prazo de 300 s para a suíte, cleanup em `finally`, labels próprias e inventário antes/depois.

A [verificação final do runner](evidencias-f3-05-integracao-candidata-20261017-C3/final-verification.json) confirma containers/rede descartáveis removidos, **zero processos nos namespaces de teste**, zero PIDs dos containers restantes e inventários de containers/redes/volumes iguais ao baseline. As preparações anteriores também encerraram seus próprios recursos. A [verificação de preservação](evidencias-f3-05-integracao-candidata-20261017-C3/preservation-verification.json) confere arquivos preexistentes permitidos, serviços e alterações limitadas; o [manifesto](evidencias-f3-05-integracao-candidata-20261017-C3/SHA256.json) relaciona os artefatos.

Workers persistentes continuam ativos, `Restart=always`, mesmos PIDs **6868** (episódio) e **6867** (Camofox), mesmos instantes de início e `NRestarts=1`; nenhuma unit foi editada e nenhum restart foi solicitado. Documentos restritos não foram consultados. Não houve commit, push, deploy, produção, Schedule, automação, ativação ou alteração dos demais gates. Entre os documentos preexistentes, **somente a nota de F3-05 no roadmap foi atualizada**.

Reprodução da suíte em memória, sem servidor:

```sh
cd /home/pc/Workspace/PQBR
env -i PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. \
  .venv/bin/python -m pytest -p no:cacheprovider -q \
  tests/unit/test_f3_05_local.py tests/unit/test_f3_05_sdk_offline.py \
  tests/unit/test_f3_05_candidate_unit.py
```

Runtime somente sob autorização de container descartável isolado, escolhendo diretório de saída **inexistente**, cujo último componente após `-` seja um token alfanumérico curto:

```sh
cd /home/pc/Workspace/PQBR
python3 tests/workflows/run_f3_05_candidate_container.py \
  /tmp/pqbr-f305-candidato-NOVO1
```

**Estado mantido: F3-05/G4 aberto; F7-02/G7 e PQBR-114 pausados; F05-06 no-arm. Nada está ligado aos Workers persistentes.**
