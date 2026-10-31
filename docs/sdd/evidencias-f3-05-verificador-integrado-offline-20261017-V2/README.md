# F3-05 — verificador integrado offline V2

**33 testes unitários aprovados, exit 0. Integração somente offline; F3-05/G4 permanece aberto.** Não foi necessário modificar o runner existente. O runtime histórico B3-v2 permanece PASS sintético; seu orquestrador permanece **exit 1 / FAILED_FINAL_VERIFIER**. Manifesto consumido e artefatos históricos intactos.

## O que foi integrado

`verificador_integrado.py` conecta o produtor e consumidor da candidata V1 em uma API nova e isolada:

- `prepare_baseline`: usa o produtor explícito `snapshot_resources` e valida a proteção recebida, sem criar estados ou escrever arquivos. Recebe apenas dados fornecidos pelo chamador; não coleta serviços. Um baseline incompleto é recusado, não parcialmente fabricado.
- `verify_inputs`: executa as quatro verificações independentes da V1 (inventário, operacional, hashes/Workers e limpeza). Depois valida o contrato cruzado do snapshot posterior pelo mesmo produtor. A quinta verificação, `snapshot_contract`, garante que os IDs operacionais esperados pertençam ao inventário posterior.
- `verify_files`: adapta arquivos JSON explicitamente fornecidos para essa API. Falhas de leitura dos baselines não impedem as verificações seguintes; falhas nos arquivos posteriores ficam isoladas em seus checks. Não há CLI, coleta real ou execução no import.

O núcleo `verificador_offline.py` e seus 20 testes são cópias byte a byte da V1, mantida intacta no diretório anterior. A V2 acrescenta integração e 13 testes, não substitui a proveniência da V1.

## Contrato e falha fechada

O produtor usa apenas `Id`, `Name`, `State.Status`, `State.Pid`, `State.StartedAt`, observados no inspect histórico já inspecionado. A projeção é `id`, `name`, `status`, `pid`, `startedAt`. Os IDs completos esperados devem ser fornecidos explicitamente, sem descoberta por prefixo ou expansão de IDs curtos. Nenhum timestamp ou estado é inventado.

Ausência/invalidez gera `INCONCLUSIVE` no check dependente; diferenças válidas geram `FAIL`. Nunca se aplica default vazio para ocultar evidência faltante. Os demais checks continuam sendo tentados, inclusive após falhas simultâneas. O resultado global só é PASS se todos os checks forem PASS e o código de runtime fornecido for exatamente inteiro zero. Um resultado inconclusivo mantém a saída global fechada em FAIL/código 2.

`after_snapshot` só aparece no relatório se o produtor posterior concluir com dados válidos. Ele não preenche nem corrige `before_resources`. Uma captura posterior válida não transforma um baseline ausente em evidência anterior.

**Não usar `prepare_baseline` para reconstruir a rodada B3-v2 a partir de dados posteriores.** A API não autentica JSONs nem verifica sua proveniência temporal: isso depende de capturas legítimas da futura etapa autorizada. O teste de regressão lê o baseline original sem campo operacional, mantém esse check INCONCLUSIVE, não muta o arquivo/dados e preserva o runtime exit 1 fornecido.

## Testes executados

No PC remoto, a partir deste diretório:

```sh
python3 -I -B -m unittest discover -s . -p 'test_verificador*.py' -v
```

Resultado registrado em `unit-tests.log`: **33 testes, OK, exit 0** (`unit-tests-exit-code.txt`). São 20 testes de regressão V1 e 13 da integração. Os testes usam somente a biblioteca padrão, fixtures explicitamente sintéticas e arquivos temporários locais. `socket.socket` e `subprocess.Popen` são bloqueados durante os casos de teste. Não houve instalação de dependência.

A integração foi testada em round-trip sintético produtor → JSON → consumidor, arquivos ausentes/inválidos por categoria, baseline ausente/malformado, campo operacional ausente/inválido, falhas individuais/simultâneas, continuidade dos checks, inconsistência entre inventário/operacionais, preservação do exit de runtime e ausência de efeitos/CLI/imports de runtime por análise estática. Os testes de proteção e inspect históricos validam apenas JSONs salvos, sem consultar serviços ou os caminhos referidos dentro dos snapshots.

## Evidências de preservação

- `preservacao-before.json` / `preservacao-after.json`: hashes de todos os arquivos B3-v2, V1 e dos cinco canônicos; status Git e digest do diff dos caminhos permitidos, antes/depois.
- `preservacao_v2.py`: utilitário offline dessas comparações, separado da API integrada; usa apenas arquivos e consultas Git, sem consulta de serviços.
- `diff-check.log`: whitespace dos arquivos novos conferido explicitamente, inclusive untracked; sem abrir diffs de materiais proibidos.
- `git-status-after.txt`: estado final do checkout, preservando alterações preexistentes.
- `v1-copy-check.log`: confirmação de que núcleo e testes copiados são idênticos à V1.
- `revisao-estatica.md`: parecer independente limitado à candidata offline.

Não houve edição de roadmap/wiki, produção, workflow, Worker, política ou configuração persistente. Nenhum runner histórico foi importado, sobrescrito ou executado; nenhum manifesto foi reutilizado. Sem B3, Temporal, Docker, workers, serviços, commit/push ou consulta a conteúdo de documentos proibidos.

## Limite do resultado

A V2 está integrada **somente na camada offline de verificação de dados/arquivos**, não ao executor B3 nem a um coletor operacional. Não há novo aceite operacional, prova do receptor/ponte, autenticação no receptor, crash safety, fencing, transação distribuída ou exactly-once externo. Qualquer adoção operacional, coleta conectada ou nova rodada requer escopo e aprovação específicos. O histórico exit 1 não foi reclassificado. **G4 continua aberto.**
