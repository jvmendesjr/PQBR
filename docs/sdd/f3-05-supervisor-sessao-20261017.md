# F3-05: supervisor sintético preserva a próxima operação

**Protótipo separado aprovado nos três testes, sem ativação operacional. F3-05/G4 permanece aberto.** A candidata, a correção operacional e os quatro Workers persistentes ficaram inalterados.

## O que aconteceu com as duas operações

O teste confirmou por query que `primeira` e `segunda` já estavam aceitas antes de liberar a falha falsa. A intervenção da primeira foi chamada uma única vez; seu workflow filho terminou em `FAILED`, sem timer de retentativa e sem registro de sucesso. O supervisor guardou `falha_tecnica_terminal`, o ID/run do filho e `resultado_efeito=nao_reconciliado`.

Uma Activity falsa separada, `registrar_falha_supervisor_falsa`, registrou a falha técnica em uma tentativa, sem retry nem fallback. O evento não contém mensagem bruta de exceção ou payload do pedido. O recibo é correlacionado por chave estável de supervisor/run do filho/operação. Isso não transforma a falha em sucesso nem prova idempotência de armazenamento externo.

A segunda permaneceu pendente. A recriação **apenas dos Workers sintéticos**, o reenvio dos mesmos IDs, um comando com revisão errada e o pedido de encerramento não a liberaram nem repetiram a primeira. Somente o comando explícito correto liberou a segunda, que concluiu uma vez. O comando repetido não abriu nova retomada. A primeira continuou `FAILED`, com a mesma falha registrada. Novas admissões ficam fechadas após a falha.

## Evidência verificável

- [Resultado consolidado](evidencias-f3-05-supervisor-sessao-20261017-S1/resultado.json): **3/3 testes em 3,822 s; 11 capturas de 7 runs reproduzidas com sucesso no replay**. As capturas incluem versões parciais e finais; não são 11 execuções independentes.
- [Log runtime](evidencias-f3-05-supervisor-sessao-20261017-S1/candidate-test.log) e [estado antes/depois das duas operações](evidencias-f3-05-supervisor-sessao-20261017-S1/runtime/test_duas_operacoes_falha_terminal_e_retomada_explicita.result.json).
- Os dois testes negativos fizeram o registro falso falhar ou devolver recibo inválido. Em ambos, houve uma tentativa de registro, nenhuma repetição da intervenção e a segunda operação continuou pendente; até o comando correlacionado foi recusado.
- [Gate de isolamento](evidencias-f3-05-supervisor-sessao-20261017-S1/isolation-gate.json), `network-*.json` e `commands.jsonl`: rede Docker dedicada `internal`, gateway `isolated`, bridge sem endereço no host, sem IPv6, rota padrão, portas publicadas ou saída roteável. As verificações negativas consultaram rotas; não enviaram tráfego externo. Banco e servidor só iniciaram após aprovação do gate. Bootstrap e testes rodaram no namespace de rede do servidor, UID não privilegiado e ambiente limpo. Somente imagens locais com `--pull=never`; nenhum pull.
- [Preservação](evidencias-f3-05-supervisor-sessao-20261017-S1/protected-verification.json): hashes da candidata, correção, código/units dos Workers, protótipo anterior e documentos normativos idênticos; os quatro serviços mantiveram PID, início, contador de reinícios, estado ativo e `Restart=always`. Apenas leitura por `systemctl show`; nenhum controle ou conexão com os Workers operacionais.
- [Limpeza](evidencias-f3-05-supervisor-sessao-20261017-S1/final-verification.json): três containers e uma rede removidos, sem processos restantes no namespace de teste e sem containers/redes/volumes novos ou ausentes em relação ao inventário inicial.

## Código e reprodução opt-in

Foram acrescentados somente quatro arquivos em `tests/workflows/`: `prototipo_supervisor_sessao.py`, `test_f3_05_supervisor_runtime.py`, `f3_05_supervisor_bootstrap.py` e `run_f3_05_supervisor_container.py`. O filho usa `CorrecaoCandidata` sem alteração; nenhum registro foi acrescentado aos entrypoints persistentes. Não houve edição do protótipo de recuperação anterior.

No PC, a partir da raiz do projeto, a reprodução exige um diretório de evidências **novo**, terminado em token alfanumérico:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python tests/workflows/run_f3_05_supervisor_container.py docs/sdd/evidencias-f3-05-supervisor-sessao-20261017-S2
```

O runner recusa imagens ausentes e assertions desabilitadas, falha fechado se o isolamento não passar e só limpa recursos criados com sua identificação exclusiva.

## Limites que continuam abertos

O supervisor só captura a exceção sintética allowlisted `FalhaTecnicaFalsa`. Timeout, cancelamento e erro desconhecido não recebem política de recuperação neste protótipo. Não reabre ator terminal, não adota históricos antigos e não implementa Continue-As-New, retenção longa ou autorização humana autenticada. Correlação do sinal não é autenticação.

O registro é falso, em memória na Activity e comprovado pelo histórico descartável; não é escrita em `pqbr.acoes`, outbox real ou reconciliação do efeito externo. Se o registro falhar, o recibo divergir ou uma resposta se perder, não há repetição nem fallback: a fila permanece bloqueada; recuperação desse registro não foi implementada. Não há exactly-once, fencing, cobertura de todos os modos de falha nem autorização para produção.

A intervenção continua com uma tentativa técnica; as políticas preexistentes de triagem/verificação/registro de sucesso da candidata não foram alteradas. Esta evidência não modifica a política operacional nem fecha TS-11. **F3-05/G4 aberto; F7-02/G7 e PQBR-114 pausados; F05-06 no-arm. Sem commit, push ou consulta a documentos restritos.**
