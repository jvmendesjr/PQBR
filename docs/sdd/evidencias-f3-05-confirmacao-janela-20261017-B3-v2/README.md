# PQBR-121 — prova única B3 e limpeza

**Aceite humano validado e uma única rodada executada. O runtime passou; o orquestrador terminou com erro no verificador final. Nenhuma segunda execução foi tentada. F3-05/G4 permanece aberto.**

## Resultado observado

O ensaio no Temporal Server **1.32.1** descartável passou **1 teste**. A primeira operação terminou **FAILED, com uma tentativa e zero reexecuções**. A segunda, já aceita e pendente no supervisor, retomou **exatamente uma vez** e produziu **um efeito falso**. A reentrega do mesmo receipt no mesmo run não acrescentou efeito nem retomada. Os **três históricos** (supervisor e duas operações) passaram pelo replay.

O receipt/outbox SQLite local usou `synchronous=FULL`, chave única e CAS, com consumo e criação do outbox na mesma transação. Houve **1 receipt consumido, 1 outbox ACKED e 1 efeito fake**. Um novo processo reabriu o banco após commit; reconsumo/reclaim foram recusados. Bancos temporários removidos ao final. [Resultado do runtime](runtime-run-B3121/runtime/resultado.json), [log do teste](runtime-run-B3121/candidate-test.log), [consolidação](final-result.json).

## Erro preservado e verificação suplementar

Depois do teste (`candidate-exit-code.txt = 0`) e da limpeza, o orquestrador lançou **`KeyError: operational_states`** no verificador final e saiu com **código 1**. Uma preparação do runner não acrescentou essa chave ao snapshot; não foi corrigido nem executado novamente. O resultado PASS do teste não transforma a execução completa do orquestrador em sucesso. [Console original](runtime-console.log), [runner exato usado](run_pqbr121.py).

A inspeção pós-limpeza foi **somente leitura, sem runtime/retry**: os **3 containers** descartáveis e a rede foram removidos; nenhum processo/namespace de teste restou; inventários de containers/redes/volumes iguais ao baseline; SQLite temporário removido. Os **1.664 hashes** protegidos e os **quatro Workers persistentes** (PIDs, horários de início e contadores de restart) permaneceram iguais. Os horários de início atuais do Temporal operacional antecedem a reserva da prova, sem restart durante a rodada. [Limpeza original](runtime-run-B3121/final-verification.json), [verificação suplementar](post-cleanup-supplemental-verification.json).

## Aceite e vínculo exatos

- Ticket **PQBR-121**: `730f420b-4d74-48be-894c-a79b13c035f2`.
- Interação: `ee39501d-3787-470a-b871-7800669759b9`.
- Board tutibom: userId `eHIQgWDGucnmgW8xT19VvSsypXRdbTr7`, destinatário/criador/resolvedor esperado; agentes e runs nulos.
- `request_confirmation`, políticas solicitada/efetiva `human_only`, `continuationPolicy=none`; chave/payload/descrição/IDs comparados literalmente com o manifesto.
- Janela: `2026-10-17T19:15:00-03:00` até `2026-10-18T19:15:00-03:00`; Unix UTC **1792275300–1792361700**, `max_snapshot_age=60`.
- Escopo: `scope-B3-next-once-v1`; sessão `session-B3-next-disposable-v1`; operação `second-B3-next-accepted-v1`; chave `pqbr-f3-05-B3-next-single-proof-v2`.

O contrato instalado usa **`result.outcome`**, observado `accepted`. A exigência anterior de `result.decision` era incorreta; não faz parte do gate. Os GETs foram projetados em memória, sem persistir resposta raw. A validação inicial ativou o manifesto; novo GET no host, depois do bootstrap e antes do teste, confirmou o mesmo vínculo. A Activity falsa apenas validou o snapshot local recente e seu binding — não acessou Paperclip.

[Manifesto pendente original](manifest-awaiting-original.json), [validação](approval-validation.json), [snapshot projetado recente](authorization-rechecked.json), [manifesto ativo usado no binding](manifest-active-used.json), [manifesto final consumido/não reutilizável](manifest.json), [reserva exclusiva](single-attempt-reserved.json).

## Isolamento e limites

Imagens locais com **`--pull=never`**; rede dedicada rotulada `internal` e gateway `isolated`, sem rota default, egress, IPv6 ou porta publicada. Gates estruturais aprovados antes de banco/servidor; Postgres em tmpfs. Python dentro do namespace isolado com ambiente limpo; Activities exclusivamente falsas, sem importar backends de produção. [Gate anterior aos containers](runtime-run-B3121/pre-container-isolation-gate.json), [gate de isolamento](runtime-run-B3121/isolation-gate.json), [harness exato](test_pqbr121.py), [validador GET](auth121.py).

Harness novo e separado: não é adoção do candidato offline B3 nem mudança de seu contrato fixo de fixtures. Durabilidade observada é SQLite local/reabertura normal e histórico Temporal descartável. **Sem injeção de crash, autenticação direta na Activity isolada, transação distribuída, fencing ou exactly-once de efeitos externos**; não comprova robustez operacional, queda de host ou recuperação geral. Duas entregas do mesmo receipt pertencem à mesma rodada, não são uma segunda execução.

P120 não se aplica e não foi alterado/cancelado/executado. Não houve Discord, efeitos externos do ensaio, produção/publicação/deploy, restart de Worker persistente, alteração de política, commit/push ou consulta a documentos proibidos. Roadmap/wiki receberam somente notas factuais. **F3-05/G4 aberto; F05-06 no-arm; F7-02/G7 e PQBR-114 pausados.**
