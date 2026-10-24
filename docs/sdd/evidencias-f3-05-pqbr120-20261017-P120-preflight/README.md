# PQBR-120: parada antes da prova única

O GET autenticado confirmou a confirmação aceita pelo humano autorizado, sem agente/run, com `human_only`, `continuationPolicy=none` e payload idêntico à minuta B3. Isso não basta para passar todos os gates.

## Bloqueio

Não foi localizado nos artefatos de evidência permitidos um manifesto ativo da autorização PQBR-120 com janela de validade previamente fixada. Os manifestos B3 encontrados são sintéticos: IDs `issue-synthetic-B3`/`interaction-synthetic-B3`, ticket `SYNTHETIC-B3`, não os IDs de PQBR-120. O GET não contém `expiresAt`. Não foi inventada uma janela com base no horário atual ou no aceite.

## O que foi e não foi feito

Somente consultas autenticadas GET e registro local desta evidência. Nenhum runtime Temporal, container, rede, workflow ou Activity foi iniciado. Nenhum receipt foi emitido/consumido, nenhuma autorização foi marcada como usada, nenhuma operação externa foi executada. Não houve mutação Paperclip, Discord, commit ou push.

O estado FAILED/1 tentativa/0 retry da primeira e a retomada única da segunda não foram testados. A ausência global de consumo não foi certificada: a verificação parou no gate anterior; uma retomada exigirá conferir novamente os registros locais antes de consumir.

## Para prosseguir

É necessário fixar/vincular explicitamente o manifesto real com os IDs desta confirmação, escopo e validade aprovada, e então revalidar GET e consumo antes de qualquer runtime. Esta tarefa não consumiu a autorização, mas não certifica que ela ainda estará válida; não reutilizar se expirada, divergente ou já consumida. Se não for possível comprovar a validade da confirmação existente, será necessária uma nova autorização específica.

F3-05/G4 continua aberto; F05-06 no-arm; F7-02/G7 e PQBR-114 pausados.

## Evidências

- `ticket-get.json`, `interactions-get.json`: respostas canônicas GET.
- `canonical-checks.json`: verificações do aceite e identidade.
- `manifest-inventory.json`: inventário limitado aos manifestos de evidência permitidos.
- `result.json`: resultado e limites.
- `protected-before.json`, `protected-after.json`, `verification-final.json`: comparação dos arquivos protegidos e dos quatro Workers durante o registro.
