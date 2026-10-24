# F3-05 — confirmação canônica conectada ao supervisor por sessão

**18/18 testes E2E passaram em Temporal Server 1.32.1 descartável, sem falhas ou pulados. A regressão H2 permaneceu em 104/104. Foram reproduzidas com sucesso 57 capturas de 39 runs. F3-05/G4 continua aberto; produção não foi ativada.**

## O que o ciclo mostrou

Duas operações foram admitidas antes da falha. A primeira sofreu a exceção técnica sintética e seu filho permaneceu `FAILED`, sem nova intervenção, retry ou reabertura. O supervisor registrou uma falha falsa separada e manteve a segunda na fila, com a admissão fechada. Nem o comando correlacionado antigo, nem uma interação ainda pendente, nem a decisão somente enfileirada liberaram a segunda operação.

O adaptador H2 original foi importado **sem alteração**. Ele abriu uma única interação `request_confirmation` no ticket fake preexistente, com políticas solicitada/efetiva `human_only`, destinatário humano sintético, `continuationPolicy="none"`, sem agente destinatário e sem alvo `plan`. Painel e Discord, ambos fakes, convergiram para essa mesma interação. A aprovação foi gravada e relida pelo adaptador; o receptor fez outra leitura canônica antes do consumo no workflow.

Nos dois caminhos aprovados, apenas a segunda operação foi executada uma vez. Recriação somente dos Workers sintéticos, reconstrução do adaptador, reenvios por outro canal, duplicatas concorrentes, replay e ACK perdido depois do consumo não repetiram nenhuma operação. O consumo é identificado pela interação, não pelo canal nem pelo evento de entrega.

Nos caminhos bloqueados, a segunda permaneceu pendente: negativa, identidade não autorizada, ticket/revisão/escopo stale, resposta de gravação perdida, falha de persistência da decisão, falha/recibo inválido do registro técnico, receipt forjado/ambíguo/expirado, falha de releitura e falha sintética do receptor. Conteúdo divergente para uma chave já consumida também foi recusado sem repetir a segunda.

[Resultado consolidado](resultado.json) · [Log runtime](runtime-A1/candidate-test.log) · [Regressão H2](regressao-H2/resultado.json). Os arquivos `runtime-A1/runtime/*.e2e.json` contêm decisões, trilha, chamadas sintéticas e estados; os pares `*.history.json`/`*.summary.json` registram históricos e replay.

## Como a composição foi separada

Tudo que é novo está nesta pasta, sem entrypoint em `src/` ou nos Workers persistentes:

- `supervisor_h3.py`: cópia experimental identificada por outro tipo Temporal. Preserva o tratamento da falha terminal e do registro separado; recusa a retomada crua. Serializa a validação, revalida o escopo depois do await e grava o receipt consumido no estado do workflow antes de liberar a fila.
- `ponte_h3.py`: porta síncrona do adaptador apenas enfileira um receipt; retorna explicitamente `enfileirado_sem_ack`, não confirmação de execução. A entrega assíncrona usa Signal e consulta ACK correlacionado pelo receipt completo. A Activity de releitura é sintética, com `maximum_attempts=1`.
- `runtime_base_h3.py` e `test_e2e_h3.py`: Activities e testes. A allowlist limita a fixture às duas operações `primeira`/`segunda`, sessão `FAKE-H3-*`, erros e simulação sintéticos; os IDs humanos/Discord/canal são os artificiais do H2. Isso não configura allowlist operacional.
- `run_container_h3.py`: provisiona e remove apenas os recursos descartáveis rotulados nesta execução. Reutiliza o bootstrap anterior somente dentro do namespace de rede criado.

Enquanto bloqueado, `fechar` não é um bypass da confirmação: o supervisor pode continuar `RUNNING` e pausado. Os testes negativos terminam esses workflows **apenas para limpar o ambiente descartável**, sem executar os pendentes. Esse encerramento do teste não é um procedimento operacional de recuperação.

## Isolamento e preservação

O gate foi aprovado **antes do banco e do servidor**: bridge dedicada `internal`, modos de gateway `isolated`, sem endereço no host, rota padrão, IPv6, publicação de porta ou egress; consultas de rota negativa não enviaram tráfego externo. Todas as imagens já estavam locais e foram usadas com `--pull=never`. O runtime e o SDK rodaram no namespace de rede do servidor descartável, com ambiente limpo e Activities falsas. O servidor informou `serverVersion=1.32.1`.

Sem o opt-in explícito, o runner recusou a execução com código 2 antes de criar diretório ou recurso: [gate negativo](gate-negativo.log). O gate de rede também é verificado antes do bootstrap e novamente pela suíte. Isso é isolamento de rede e disciplina de fixture, não um sandbox de filesystem contra código hostil.

[Limpeza final](runtime-A1/final-verification.json): três containers e uma rede removidos, nenhum processo remanescente nos namespaces criados, inventários de containers/redes/volumes iguais aos iniciais. [Preservação](preservacao.json): **1.264 arquivos preexistentes** de código, testes, evidências anteriores, templates e units protegidos por hashes; quatro Workers ativos nos mesmos PIDs, inícios e contagens de restart. A única diferença permitida no roadmap é a nota nova de F3-05. Configuração e credenciais reais não foram abertas; os valores do Postgres descartável são exclusivamente fictícios.

Não houve ticket, aviso, HTTP externo, consulta/emissão de credenciais reais, alteração no bot/integração, chamada ao Temporal operacional, restart de serviço persistente, deploy, produção, commit ou push. Não foram lidos os diretórios/documentos restritos. Política de exceção técnica, candidata e protótipos anteriores intactos. F7-02/seu G7 e PQBR-114 continuam pausados; F05-06 permanece no-arm.

## O próximo gate que ainda falta

**A composição sintética não fecha G4. O próximo gate técnico é validar uma ponte/receptor reais com autorização canônica e consumo durável sob falha, em etapa controlada e explicitamente autorizada, ainda sem ativar produção.** É preciso demonstrar autoria humana pela identidade já vinculada de José, persistência/releitura canônicas reais e recuperação idempotente do consumo/resume quando o processo cai ou a resposta se perde. Deve existir plano aprovado antes de qualquer acesso mutável real. Não é necessário redefinir o autorizador nem refazer a aprovação da integração Paperclip–Discord já existente.

F3-05/G4 só poderá fechar com as integrações/registro operacionais restantes, TS-11 completo e aceite operacional de José; o êxito deste teste não é esse aceite.

Os fakes Paperclip/Discord/vínculo, CAS e registros canônicos continuam em memória. Não foi provada autenticação real, recuperação do armazenamento fake após crash, transação distribuída entre Paperclip e Temporal, fencing ou exactly-once de efeitos externos. O hash `FAKE-SNAPSHOT:` é correlação demonstrativa, não assinatura ou receipt emitido pela API. Recriar Workers sintéticos no mesmo processo não equivale a reiniciar o processo inteiro nem recuperar banco. O replay comprovado é dos históricos do ciclo Temporal descartável; a política atual para efeitos externos incertos não foi alterada.

## Reprodução

Use uma saída **nova**, terminada em token alfanumérico, sem reutilizar `runtime-A1`. Os quatro Workers persistentes não precisam de qualquer alteração.

```bash
cd /home/pc/Workspace/PQBR
env -i PATH=/usr/bin:/bin HOME=/home/pc XDG_RUNTIME_DIR=/run/user/1000 \
  PQBR_H3_ALLOW_DISPOSABLE=CONFIRMO_SOMENTE_FIXTURE_H3 \
  python3 docs/sdd/evidencias-f3-05-composicao-e2e-20261017-H3/run_container_h3.py \
  /tmp/pqbr-f305-h3-REPRO1
```

Exige imagens locais, `.venv` já disponível e os mesmos privilégios limitados de Docker/nsenter do harness anterior. Não instala dependências nem baixa imagens. `consolidar_h3.py` é o registro da consolidação original e não deve ser reexecutado para inserir outra nota no roadmap. A checagem de preservação pode ser repetida, somente leitura, com `preservar_h3.py depois`.
