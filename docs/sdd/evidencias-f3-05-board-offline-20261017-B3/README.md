# F3-05: ponte Board candidata, somente offline — B3

**Candidato separado, não operacional. F3-05/G4 permanece aberto.** Nenhuma autorização nova foi consumida; P119 não foi executado novamente. F05-06 continua no-arm; F7-02/G7 e PQBR-114 continuam pausados. A política de falha técnica está intacta.

## O que foi construído

`candidate.py` é uma fatia Python stdlib sem importação/registro em `src/` ou Workers. Importar o módulo não roda testes, abre banco, consulta CLI ou envia algo. O dispatcher exige `opt_in=True` e aceita exclusivamente as classes fake exatas do harness, não uma implementação real nem subclasses.

O parser recebe duas strings JSON sintéticas: snapshot do ticket e lista correspondente ao formato candidato de `paperclipai issue interactions <issue> --json`. A porta fake aceita somente GET lógico e os comandos `issue get <id> --json` e `issue interactions <id> --json`; não contém subprocesso de CLI, HTTP ou autenticação. A lista deve conter exatamente uma interação. Ausências, campos adicionais em qualquer nível, chaves duplicadas, tipos incorretos, booleano em lugar de inteiro, Unicode inválido e JSON não finito falham fechados. Só a whitelist fica no snapshot, sem resposta raw nem campos arbitrários em logs.

A validação exige perfil Board esperado, humano esperado, autor/criador = destinatário = resolvedor autorizado, status e resultado `accepted`, `request_confirmation`, políticas solicitada/efetiva/declarada `human_only`, origem explícita/solicitada, `continuationPolicy=none` e todos os campos de agente/run nulos. Ticket, organização, interação, descrição e payload inteiro devem coincidir com o manifesto ativo; ticket terminal/em execução é rejeitado. Há janela de validade, aceitação não anterior ao escopo, observação recente e rejeição de observação futura. P119 tem bloqueio nominal adicional; isso não substitui um registro global de autorizações consumidas.

**Payload exato** significa igualdade estrutural e de tipos do JSON e igualdade literal de cada string, incluindo espaços e detalhes. Ordem das chaves e espaços de serialização JSON são normalizados. Não significa igualdade dos bytes raw da CLI.

## Receipt, CAS e outbox

O receipt SQLite guarda o hash do snapshot projetado, hash do manifesto completo, interação, chave de idempotência e payload mínimo completo. O binding inclui perfil/principal Board, campos de política, texto autorizado, IDs de escopo e janela de validade. `observed_at` é freshness de transporte verificada a cada leitura; não faz parte do hash para permitir uma releitura idêntica posterior, dentro da validade.

`consume()` faz, na mesma transação `BEGIN IMMEDIATE`, um CAS `ISSUED/v0 → CONSUMED/v1` e a inserção única no outbox. Qualquer falha entre as duas operações reverte ambas. SQLite usa `synchronous=FULL`, foreign keys e journal DELETE. Interação e chave de idempotência são únicas no banco. Antes do envio fake há uma nova leitura pela porta fake, nova validação e conferência integral do binding do receipt/outbox. Divergência bloqueia; não troca silenciosamente a autorização.

O outbox passa por `READY → SENDING → ACKED`, com owner e versão de CAS. Após resultado ambíguo ele fica `SENDING`. Somente uma chamada **manual e explícita** de recuperação com versão esperada o devolve a READY; nenhum timer, loop ou retry automático foi criado. ACK de owner antigo é recusado. Um erro do destino não devolve o receipt a ISSUED.

`FakeTemporal` tem SQLite próprio descartável, uma primeira operação já FAILED/uma tentativa e uma segunda já aceita/pendente. O efeito fake e sua dedupe são gravados na mesma transação. O sender transmite apenas seis IDs autorizados: `issueId`, `interactionId`, `scopeId`, `sessionId`, `operationId`, `idempotencyKey`. Não transmite comandos, texto de shell, identidade humana presumida, segredo nem payload de ferramenta real. Os quatro IDs de escopo são fixados literalmente no texto da confirmação; issue/interação são os IDs do próprio objeto aprovado, fixados no manifesto e no snapshot. Isso evita exigir que uma confirmação conheça seu próprio ID antes de existir.

## Evidência de testes

O resultado da suíte final está em [`execucao-final-validada/result.json`](execucao-final-validada/result.json), com log completo em [`tests.log`](execucao-final-validada/tests.log): **41 testes, 195 subtests, 193 casos negativos com fake_effects=0 e external_effects=0; 19 subprocessos Python do harness, quatro SIGKILL reais**. Os dois subtests restantes são as injeções de morte dentro da transação.

Foram exercitados pending/rejected/stale/expired, ator/perfil divergente, políticas inconsistentes, agente/run, campos falsificados/adicionais/ausentes, payload alterado, receipt/outbox adulterados, janela inativa, snapshot expirado, P119, duplicação, replay, colisão de idempotência, CAS entre oito processos e claims concorrentes. Todos os negativos da matriz partem de destino sem efeito e exigem contagem zero. Nos testes de replay/ACK perdido que começam **depois de um efeito fake legítimo**, a propriedade é delta de efeito zero: a contagem permanece um, não volta artificialmente a zero.

Crash antes do commit reverte receipt/outbox; crash antes do envio mantém pendência; queda depois do efeito/ACK remoto e ACK perdido permitem recuperação manual com dedupe persistente no destino fake após processo reiniciado. A primeira operação continua com uma tentativa, nunca é reaberta/reexecutada.

A guarda do runner é instalada e autotestada por um evento auditável sintético, sem conectar rede. Bloqueia eventos `socket.*`, shell e subprocessos não allowlisted; permite somente o Python isolado executando `crash_child.py` com ações fixas. O filho também bloqueia rede e criação de subprocessos. Não é uma sandbox de segurança contra Python arbitrário malicioso; é uma trava do harness controlado. Nenhum servidor/container Temporal foi iniciado. CLI/API Paperclip, Discord e efeitos externos reais: zero.

A primeira rodada (`execucao-01`) ficou **reprovada**: no Python 3.13 do PC, a guarda bloqueou o `os.posix_spawn` usado pelos próprios subprocessos do harness. Foi corrigida para permitir apenas a mesma argv Python estrita já allowlisted. `execucao-02` passou na versão intermediária. `execucao-final` passou após revisão de Unicode/testes; a pasta `execucao-final-validada` corresponde ao código final com o texto de escopo sem autorreferência. As rodadas antigas não são apagadas nem renomeadas como aprovadas. A revisão independente distinguiu o limite de autenticação fake e motivou rejeição Unicode uniforme e teste da guarda que funciona sem abrir socket.

## Como reproduzir sem integrar nada

No PC, dentro desta pasta:

```sh
python3 -I -B run_offline.py --run-offline --output execucao-local-NOVA
```

A pasta de saída deve ser nova. Não instalar dependências, usar `.venv` do projeto, carregar `.env` nem importar Workers. O runner fabrica apenas snapshots e bancos sintéticos em diretórios temporários; os bancos de teste são descartados ao terminar, mas são reabertos por processos reais durante os testes. Os snapshots JSON persistidos em `execucao-*` são **fakes**, não comprovações de decisão humana real. `python3 -B -m unittest test_candidate` também é uma execução fake, mas o runner acima é o caminho documentado com guarda de rede no processo pai.

## O que esta prova não permite concluir

**Não há autenticação Board real nesta fatia.** `BoardContext` é metadado injetado e forjável do harness. Um snapshot perfeitamente falsificado com todos os valores esperados não pode ser distinguido por um hash. A prova cobre divergências de esquema/valores/binding, não assinatura ou autenticidade criptográfica. A futura porta real deverá obter principal/perfil exclusivamente da CLI Board autenticada existente, por GET autorizado, nunca do texto do JSON nem da identidade de agente do worker. Não foi consultada ou alterada a autenticação existente, nem refeita a integração Paperclip–Discord/tutibom.

O esquema externo ainda não foi reconfirmado por uma leitura real nesta tarefa. Campos adicionais normais de outra versão da CLI serão recusados até revisão explícita da whitelist; não há adaptação permissiva automática. Compatibilidade com a CLI instalada e um receiver operacional continuam pendentes.

**Não há Temporal Server nem prova de exactly-once real.** Trata-se de entrega fake pelo menos uma vez com dedupe durável fake. A atomicidade do efeito e dedupe só existe no SQLite fake. CAS local não é transação distribuída nem fencing remoto: um sender antigo ainda pode transportar mensagem depois da recuperação; o teste mostra que o destino fake deduplica e só o ACK antigo é bloqueado. Dois bancos de receipt independentes também podem consumir a mesma autorização; só a dedupe compartilhada do destino fake evita efeito duplicado nesse cenário. Não há dedupe global, proteção contra rollback/restauração maliciosa, perda do banco do destino, corrupção coordenada do disco ou garantia após falha elétrica/host. Esses limites foram mantidos explícitos.

Revogação entre a última leitura e o efeito continua sendo uma janela de TOCTOU; aqui apenas se comprova rejeição quando a mudança já aparece na releitura fake. Não há protocolo real de revogação/fencing. Retenção de dedupe e reconciliação operacionais não estão implementadas.

## Próxima autorização, ainda não solicitada

[`PROXIMA-AUTORIZACAO.md`](PROXIMA-AUTORIZACAO.md) mostra o texto e JSON exatos propostos, sem executar ou criar a interação. [`next-confirmation-payload.json`](next-confirmation-payload.json) é o payload completo da confirmação proposta. Os quatro IDs de escopo já são explícitos; os dois IDs de ticket/interação do transporte só poderão ser preenchidos com **uma confirmação nova e específica**, nunca P119. O template de transporte não é executável enquanto não existirem esses IDs e o manifesto ativo aprovado.

Nenhuma confirmação do chat, inclusive “Siga”, substitui o aceite específico no Paperclip para nova execução real. Antes de qualquer prova real, mostrar novamente o payload final com IDs novos e manifesto/janela fixados, obter a confirmação específica e validar sua decisão canônica por GET autorizado. Não há autorização nesta entrega para fazer essa leitura, abrir ticket, aprovar, enviar Discord ou iniciar runtime.

## Preservação

`protected-before.json` e `verification-final.json` registram hashes de arquivos de código/testes/documentação permitida selecionados, e propriedades dos quatro Workers. A única alteração preexistente pretendida é a nota factual de F3-05 em `docs/ROADMAP.md`; a verificação reconstrói o hash anterior retirando só essa nota. Não é uma auditoria global de todos os arquivos do PC. Não foram alterados `src/`, Workers, units, configuração, clientes ou autenticação existentes. Sem credenciais, ticket/mensagem/API real, restart, deploy, commit, push ou leitura de documentos proibidos.
