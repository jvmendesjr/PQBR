# PQBR-119 — uma confirmação real, uma retomada sintética

**Uma única rodada passou em Temporal Server 1.32.1 descartável. Não houve efeito externo real. F3-05/G4 continua aberto. Não reexecutar esta autorização.**

## Confirmação usada

Ticket `d3b2eb41-63e5-4e7e-8cb7-06672e3ddab9` (PQBR-119), interação `815e9e44-cf90-45b4-86a2-23aafd45d0fc`. GETs pela CLI autenticada validaram o texto exato do escopo, organização, autor/criador/destinatário e `resolvedByUserId=eHIQgWDGucnmgW8xT19VvSsypXRdbTr7` (perfil tutibom autorizado), `status=accepted`, `result.outcome=accepted`, políticas solicitada/efetiva `human_only`, `continuationPolicy=none`, sem agente ou run resolvedor. O ticket, não a resposta do chat, foi a autorização. Os snapshots iniciais e imediatamente anteriores à prova são idênticos.

Antes de criar os artefatos, a busca nos caminhos de evidência/código/testes relevantes não encontrou uso deste ticket/interação; a busca em /tmp tampouco encontrou artefato nominal correspondente. Isso não é uma prova global contra execução fora desses caminhos. O arquivo exclusivo `single-attempt-reserved.json` reserva a tentativa local, e a saída nova falha se já existir. O runner não tem laço de repetição da rodada. A autorização deve ser tratada como consumida localmente; Paperclip não foi modificado.

## O que aconteceu

A fixture descartável admitiu somente `primeira` e `segunda`. Antes de consumir o receipt, `primeira` já estava terminal `FAILED`, com uma tentativa e sem retry/timer; `segunda` já estava aceita e pendente. O receipt foi correlacionado a esse estado e consumido no histórico do supervisor. Só `segunda` foi liberada.

Resultado: **1 rodada, 1 receipt consumido, 1 retomada, primeira FAILED/1 tentativa/0 reexecuções, segunda 1 tentativa/1 efeito fake, 0 pendentes e 0 efeitos externos reais**. O mesmo receipt foi entregue novamente dentro da mesma rodada: 1 duplicata reconhecida, sem nova validação/retomada/efeito. Não foi uma segunda rodada. Históricos e replay comprovaram dois filhos apenas e preservação da primeira falha.

## Isolamento e limpeza

Gate estrutural aprovado antes de criar/iniciar qualquer container: bridge dedicada `internal`, gateway IPv4/IPv6 `isolated`, IPv6 desativado, bridge do host sem endereço e somente imagens já locais. A sonda admin-tools confirmou adicionalmente ausência de rota default e consultas de rota externa IPv4/IPv6 falhando sem enviar tráfego, antes de iniciar Postgres/Temporal. Todos os containers sem portas publicadas e com `--pull=never`; Postgres em tmpfs. O SDK rodou no namespace de rede do servidor descartável, com ambiente limpo e somente Activities falsas.

Três containers e uma rede próprios foram removidos; nenhum PID/namespace residual. Containers, redes e volumes finais são idênticos ao baseline. Hashes dos arquivos protegidos e quatro Workers/units/PIDs/inícios/restarts permaneceram iguais. Nenhuma alteração em H3/D1/H2, código, Workers, units ou configuração persistente; a configuração temporária pertence exclusivamente ao ensaio.

## Limites e pendências

A autorização foi relida por GET no host antes do runtime. A Activity isolada valida um snapshot canônico/binding local, **não faz uma consulta de rede real ao Paperclip**. O hash é correlação, não assinatura independente. O consumo é observado no histórico Temporal e em replay; não houve crash injection nem prova de recuperação após queda de processo/host, transação distribuída, fencing ou exactly-once externo. Não demonstra autenticação via Discord ou receiver operacional. O D1 local não foi usado como receiver real.

Faltam a ponte/receptor operacionais autorizados, recuperação durável sob falha, integrações/registro restantes, TS-11 completo e aceite operacional. F3-05/G4 permanece aberto; F05-06 no-arm; F7-02/seu G7 e PQBR-114 pausados. Política de exceção técnica intacta. Sem mutação Paperclip/Discord, avisos, publicação, produção, commit/push ou consulta aos documentos proibidos.

## Evidências principais

- `authorization-initial.json` e `authorization-rechecked.json`: whitelists canônicas conferidas.
- `single-attempt-reserved.json`: trava da tentativa local; não remover/reutilizar para repetir o teste.
- `execucao-P119/runtime/estado-antes-consumo.json`, `receipt.json`, `resultado.json`, históricos e summaries: estados/contagens/replay.
- `execucao-P119/pre-container-isolation-gate.json`, `isolation-gate.json`, `network-*.json`: isolamento.
- `execucao-P119/final-verification.json`, `protected-before.json`, `protected-after.json`: limpeza/baseline.
- Scripts novos nesta pasta: validador GET, fixture única e harness derivado. Importam H3/H2 sem alterá-los; não são integração de produção.
