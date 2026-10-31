# Próxima autorização proposta — não enviada

**Esta minuta não é uma autorização e não inicia teste algum.** Não criar/editar ticket ou interação nem usar a CLI/API com base nesta entrega. P119 está consumido e não pode preencher nenhum campo abaixo.

## Payload exato da confirmação proposta

O JSON abaixo é completo: não há placeholder dentro do texto da confirmação. Os IDs do próprio ticket/interação serão vinculados pela origem canônica da nova confirmação, sem autorreferência no texto. O perfil aprovador continua sendo o tutibom Board já autorizado, sem identidade de agente ou run e sem refazer o vínculo Discord.

```json
{
  "version": 1,
  "prompt": "Autoriza uma única prova sintética deste escopo exato, sem efeitos externos?",
  "acceptLabel": "Autorizar execução única",
  "rejectLabel": "Não autorizar",
  "allowDeclineReason": true,
  "detailsMarkdown": "Uma única rodada sintética. Primeira já FAILED, uma tentativa, sem retry ou reexecução. Somente a segunda já aceita e pendente pode retomar uma vez. Temporal Server 1.32.1 descartável somente após autorização específica, rede interna isolada, Activities falsas e armazenamento descartável. Sem Workers persistentes, integrações reais, Discord, produção, publicação, deploy ou mudança da política de falha técnica. issueId e interactionId devem ser exclusivamente os IDs do ticket e da própria confirmação aceita, fixados no manifesto ativo e vinculados integralmente ao snapshot e receipt, nunca IDs de outra autorização. IDs de escopo exatos autorizados: {\"idempotencyKey\":\"pqbr-f3-05-B3-next-single-proof-v1\",\"operationId\":\"second-B3-next-accepted-v1\",\"scopeId\":\"scope-B3-next-once-v1\",\"sessionId\":\"session-B3-next-disposable-v1\"}",
  "supersedeOnUserComment": false
}
```

A solicitação deverá ser `request_confirmation`, com `requestedResolverPolicy=human_only`, política efetiva `human_only` e `continuationPolicy=none`. Destinatário/criador/autor da decisão devem corresponder ao mesmo humano autorizado; nenhum agente/run pode resolver. Isso é uma política candidata, não um comando de criação. Não foram testadas nesta tarefa mutações ou parâmetros reais da CLI.

## Payload mínimo do sender

```json
{
  "issueId": "<NOVO_ISSUE_ID>",
  "interactionId": "<NOVA_INTERACTION_ID>",
  "scopeId": "scope-B3-next-once-v1",
  "sessionId": "session-B3-next-disposable-v1",
  "operationId": "second-B3-next-accepted-v1",
  "idempotencyKey": "pqbr-f3-05-B3-next-single-proof-v1"
}
```

Somente os dois campos delimitados por `<...>` aguardam IDs **novos**. São placeholders propositalmente inválidos para o parser, não IDs inventados de ticket/interação. Nenhum outro campo será ampliado ou preenchido com comando livre. Antes de executar algo real, o payload completo de transporte, os IDs da confirmação e o manifesto ativo com janela de validade deverão ser exibidos e fixados; a decisão canônica dessa confirmação nova deverá autorizar exatamente essa única prova. Se houver divergência, expiração, pendência/rejeição ou resultado ambíguo, parar; não reciclar a chave para outra rodada.

## Limite da eventual prova

Uma única rodada no Temporal Server **1.32.1**, descartável, somente se autorizada em outra interação específica; rede interna isolada sem saída, Activities falsas e armazenamento descartável. Primeira já em FAILED/uma tentativa, sem retry/reexecução; segunda já aceita/pendente, única retomada permitida. Zero efeito externo, sem Worker persistente, Camofox/Hindsight real, Discord, produção/publicação, restart/deploy ou alteração de política. A ativação/receiver operacional e a compatibilidade real da porta Board não estão prontos e não são liberados por esta minuta.

O contrato fake atual serve para preparar e revisar, não é um runner de Temporal real. Qualquer preparação real além desse contrato exigirá escopo próprio antes de executar, preservando a regra de uma nova confirmação Paperclip específica por execução real. F3-05/G4 continua aberto; F05-06 no-arm; F7-02/G7 e PQBR-114 pausados.
