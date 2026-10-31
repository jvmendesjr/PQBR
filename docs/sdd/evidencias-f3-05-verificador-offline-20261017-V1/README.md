# F3-05 — candidata offline do verificador final V1

**Candidata isolada; 20 testes unitários aprovados. F3-05/G4 permanece aberto.** O runner e todos os artefatos B3-v2 continuam históricos e não foram corrigidos, importados ou reexecutados. O runtime B3 permanece PASS sintético; o orquestrador histórico permanece **exit 1 / FAILED_FINAL_VERIFIER**.

## O que esta candidata corrige

`verificador_offline.py` implementa um produtor puro de snapshot com contrato explícito de `operational_states` e um consumidor final com quatro verificações independentes: inventário, preservação operacional, hashes/Workers e limpeza. Ausência, formato inválido ou erro de callback geram `INCONCLUSIVE`; diferenças geram `FAIL`. Somente todos os checks PASS e código de runtime exatamente inteiro zero permitem PASS. Uma falha não pula os demais checks e não apaga falhas do runtime.

Não é um novo runner nem um adaptador conectado a Docker/Temporal. Os callbacks dos testes são exclusivamente fakes. Não há coleta real, autorização operacional, instalação ou integração desta candidata.

## Contrato baseado nos arquivos existentes

Foram inspecionados, somente como arquivos:

- [Runner histórico](../evidencias-f3-05-confirmacao-janela-20261017-B3-v2/run_pqbr121.py), linhas 138–146 e 461–485: o produtor antigo retorna apenas listas de IDs em `containers`, `networks`, `volumes`; o consumidor exige uma chave adicional inexistente.
- [Baseline original](../evidencias-f3-05-confirmacao-janela-20261017-B3-v2/runtime-run-B3121/resources-before.json): contém somente esses três inventários. **Não existe baseline operacional para reconstruir retrospectivamente.** O teste com esse arquivo continua inconclusivo no check operacional e falha no resultado global.
- [Inspect histórico descartável](../evidencias-f3-05-confirmacao-janela-20261017-B3-v2/runtime-run-B3121/inspect-final-pqbr-f305-B3121-server.json): observa `Id`, `Name`, `State.Status`, `State.Pid`, `State.StartedAt`. É usado no teste apenas para validar o formato real do JSON; não é tratado como container operacional nem como evidência de preservação.
- [Verificação suplementar](../evidencias-f3-05-confirmacao-janela-20261017-B3-v2/post-cleanup-supplemental-verification.json): contém projeção operacional posterior com `id`, `name`, `status`, `pid`, `startedAt`, além do campo derivado `startPredatesSingleAttempt`. A candidata usa apenas os cinco campos observáveis, não copia o campo derivado nem fabrica valores. Os IDs curtos desse arquivo não são convertidos/inventados como IDs completos.
- [Proteção anterior](../evidencias-f3-05-confirmacao-janela-20261017-B3-v2/runtime-run-B3121/protected-before.json): estrutura real `hashes` e `services`, inclusive os quatro Workers. O teste verifica somente o formato salvo, sem consultar serviços ou recalcular os hashes dos caminhos referidos.

Na candidata, `operational_states` é uma lista não vazia dos cinco campos acima, ordenada por ID completo. O conjunto protegido deve ser fornecido explicitamente com IDs completos, únicos e não vazios; nenhuma descoberta automática por prefixo. Ausência de campo, dados malformados, IDs faltantes/extra/duplicados ou baseline ausente não recebem default vazio. Containers protegidos devem pertencer ao inventário do snapshot. Projeções iguais não provam preservação se o baseline obrigatório estiver ausente.

## Testes executados

Comando no PC remoto, a partir deste diretório:

```sh
python3 -I -B -m unittest discover -s . -p test_verificador_offline.py -v
```

Resultado: **20 testes, OK, exit 0**. Registro completo em `unit-tests.log`; código em `unit-tests-exit-code.txt`. Os testes usam biblioteca padrão, dados sintéticos explicitamente identificados e leitura dos JSONs citados. `socket.socket` e `subprocess.Popen` ficam bloqueados durante os testes. A candidata só importa `datetime` e `re`; o teste estático também verifica ausência de chamadas no nível superior das atribuições do módulo. O runner histórico nunca é importado.

Cobertura: contrato produtor/consumidor; ordenação e não mutação; campos ausentes/malformados; IDs esperados estritos; PID/início/status alterados; recursos adicionados/removidos; alteração de hash/Worker; falha individual em cada callback sem pular os demais; retorno de limpeza estritamente booleano; códigos de runtime inválidos/falhos sem falso PASS; baseline histórico sem campo operacional; estruturas reais de inspect/proteção.

Revisão estática independente dos dois arquivos: nenhum bug material encontrado nos critérios de isolamento, continuidade das verificações e bloqueio de falso PASS. É parecer estático, não validação operacional.

## Preservação e checagens finais

`preservacao-before.json` registra os hashes dos arquivos B3-v2 e dos cinco documentos canônicos, além do status Git e numstat limitado a caminhos de código/configuração permitidos. `preservacao-after.json` registra a comparação final; não consulta estado de serviços. `preservacao.py` é apenas um utilitário offline de leitura desses arquivos e consultas Git, não faz parte do verificador.

O diff-check considera os arquivos novos explicitamente, pois são untracked; não abre diffs de documentos proibidos. Resultado em `diff-check.log`. O status final fica em `git-status-after.txt`. Não houve consulta ao conteúdo de documentos proibidos, alteração do roadmap geral/wiki, workflow, Worker, produção, política ou configuração persistente. Nenhum commit/push, container, serviço, Temporal ou prova B3 foi executado. A autorização consumida continua não reutilizável.

## O que continua pendente

Esta evidência não fecha TS-11, F3-05 ou G4 e não comprova integração do receptor/ponte, autenticação no receptor, durabilidade/recuperação operacional, crash safety, fencing ou exactly-once externo. O PASS dos unitários é da candidata offline, não uma nova avaliação bem-sucedida do orquestrador histórico.

Qualquer integração futura ou nova rodada operacional exige escopo e aprovação específicos, autorização/manifesto novos quando aplicável e baseline operacional capturado antes da execução. **Não reutilizar o manifesto B3-v2.** F05-06 segue no-arm; F7-02/G7 e PQBR-114 permanecem pausados.
