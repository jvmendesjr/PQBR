# F3-05 — adaptador da confirmação canônica Paperclip

**104/104 testes passaram no PC, sem falhas, erros ou pulados. Todas as portas são fakes em memória. F3-05/G4 permanece aberto.** Não houve ticket novo, aviso, HTTP, CLI mutável ou comando Temporal real.

## O que foi implementado

Os módulos novos ficam somente nesta pasta de evidências. Não são importados pelos Workers persistentes e não importam `pqbr` nem `temporalio`.

- `modelos.py`: escopo imutável, contexto da falha, evento vinculado e interfaces injetáveis.
- `adaptador_confirmacao.py`: construção e validação de `request_confirmation`, releitura canônica e convergência da decisão Discord para a interação existente.
- `fakes.py`: Paperclip, Discord/vínculo existente, relógio e supervisor falsos, com falhas injetáveis, CAS e deduplicação apenas em memória.
- `test_confirmacao.py` e `run_tests.py`: testes stdlib com rede/subprocessos bloqueados por audit hook Python. Isso não é isolamento de kernel contra código hostil.

Não há função de criar ticket nem enviar aviso nas portas. A confirmação pertence a um **ticket já existente**; painel e Discord usam o mesmo `issueId`, `interactionId` e chave de confirmação. O round-trip de uma thread não é interpretado como autorização.

## Formato canônico, sem wake automático

O código instalado do Paperclip foi lido, não executado. O [recorte do contrato](contrato-instalado.txt) registra caminho, linhas e SHA-256 do bundle. O formato utiliza:

- `kind="request_confirmation"`, `resolverPolicy="human_only"` e `addresseeUserId` proveniente da porta do vínculo existente;
- `addresseeAgentId=null` e `continuationPolicy="none"` explícitos;
- payload sem `target`, especialmente sem `plan`, e sem `toolAction` ou `secretProposal`;
- `detailsMarkdown` com manifesto exato: revisão da falha, supervisor/run, falha/run terminal, receipt do registro da falha, sequência completa de pendentes e prazo imutável.

A revisão aqui é a **revisão do escopo da falha**, gravada no manifesto. Não foi inventado um campo de revisão de interação nem um endpoint de receipt. A leitura corresponde à listagem de interações do ticket; a decisão humana corresponde a `accept`/`reject`. Os métodos dessas portas não fazem requisições nesta evidência.

O receptor exige tanto a política solicitada quanto a efetiva `human_only`, destinatário correto, ausência de agente resolutor/run, autor canônico, decisão, timestamp e payload exatos. `true` e `1`, por exemplo, não são aceitos como a mesma versão JSON.

## Identidade já aprovada

José já é o autorizador pela identidade vinculada existente. Não se pede nova definição, não se cria uma allowlist paralela nem se modifica bot, configuração ou vínculo. O adaptador recebe a porta `VinculoExistentePort`; **os testes substituem essa porta por IDs artificiais**, sem consultar a identidade real, tokens, contexto de CLI ou arquivos de credenciais.

No Discord, a porta confiável entrega metadados já vinculados à identidade Paperclip e ao canal privado permitido. Texto, nome de exibição, thread ou ID de evento inexistente não fornecem autorização. Contas não vinculadas, canal fora da permissão e DM são recusados nos fakes.

No painel, a decisão já está gravada pela sessão humana do Paperclip: o adaptador **apenas relê**. `resolvedByUserId` é metadado confiável da API, não campo que um agente pode atribuir no corpo da decisão. A porta `resolver_como_humano` exige sessão humana autenticada já vinculada; não é uma API que aceite um autor arbitrário informado pelo cliente. As funções com sufixo `fixture` montam o cenário sintético, não um mecanismo real de autenticação.

## Quando os pendentes podem prosseguir

A aprovação precisa estar persistida no registro canônico e ser relida antes da chamada ao supervisor. A resposta da gravação isoladamente não basta. No receptor falso, outra leitura revalida o receipt, a identidade, o prazo, a revisão e o conjunto exato dos pendentes, antes do consumo na seção crítica em memória.

O receipt local inclui autor, decisão, timestamp, revisão, escopo, ticket/interação e hash do snapshot. Os campos estão no registro canônico falso; a projeção consumida é retida pelo supervisor falso antes de executar os pendentes. A chave de consumo depende da interação, **não do canal ou ID de entrega**. Reenvios explícitos convergem para o mesmo consumo, inclusive após perder o ACK ou reconstruir a fachada contra os mesmos fakes. Não há retries automáticos nem fallback.

A operação terminal e as já concluídas nunca entram na lista executável. A admissão continua fechada. Recusa, expiração, revisão/pendentes divergentes, usuário inválido, política de continuação errada, API indisponível ou receipt ausente, ambíguo ou incerto não produzem retomada. Uma resposta perdida após gravar a decisão bloqueia a tentativa atual; um reenvio explícito pode reler a decisão conhecida. ACK perdido após execução não causa nova execução.

## Evidências e reprodução

[Resultado final no PC](execucao-pc/resultado.json): 104 testes identificados, zero falhas/erros/pulados e nenhum módulo operacional `pqbr` ou SDK Temporal importado. [Log completo](execucao-pc/testes.log). As demonstrações [painel](execucao-pc/demo-paperclip.json) e [Discord](execucao-pc/demo-discord.json) mostram a mesma estrutura canônica, receipt, ordem de persistência/leitura/consumo e duplicata sem efeito adicional.

A suíte inclui perda de resposta na abertura e na decisão, perda de ACK, replay, entrega duplicada com outro ID, concorrência de aprovações, recusa concorrente, revogação do vínculo, expiração durante CAS e antes do consumo, adulteração entre fachada/receptor, políticas incorretas, status sem decisão e escopos com pendentes extras, faltantes ou reordenados. A primeira rodada, com 94 testes também aprovados, foi preservada em `primeira-execucao/`; a rodada final ampliou a validação de tipos/campos, autoria da porta fake, incerteza e bloqueios.

Para reproduzir, use um diretório de saída **novo**:

```bash
cd /home/pc/Workspace/PQBR/docs/sdd/evidencias-f3-05-confirmacao-canonica-20261017-H2
env -i PATH=/usr/bin:/bin python3 -I -S run_tests.py /tmp/pqbr-confirmacao-h2-repro-novo
```

Nenhuma dependência é instalada. O runner não sobrescreve saída existente. `preservacao.json` compara os 125 arquivos do baseline (código, testes, evidência H1 e roadmap), comprova somente a inserção da nova nota no roadmap e compara estado/PID/início/restarts dos quatro Workers por `systemctl show` somente leitura. Configuração e credenciais não são abertas pelo runner ou pelo adaptador.

## O que isso não prova

**Não é integração real, deploy nem autorização operacional. Crash safety e durabilidade real NÃO estão provadas.** Registro, CAS, locks, receipts e consumo estão somente em memória. Reconstruir a fachada contra os mesmos fakes não equivale a reiniciar processo ou recuperar banco após crash.

`FAKE-SNAPSHOT:` é hash demonstrativo, não assinatura, receipt emitido pelo Paperclip ou prova criptográfica de autoria. A API canônica, a sessão humana, o vínculo e o relógio injetados são fronteiras de confiança; uma API adversarial que falsifique armazenamento e autoria está fora da garantia. A revisão estática independente reforçou essa fronteira do painel e a necessidade de relógio confiável; não foi validada autenticação real nem comportamento de relógio arbitrariamente regressivo.

Não há prova de transação distribuída, outbox durável, fencing, exactly-once externo, replay/histórico Temporal ou recuperação após crash. O supervisor sintético anterior não foi alterado ou conectado: seu sinal correlacionado, sozinho, não fornece esta autorização. Um transporte real e um receptor durável continuam fora desta rodada.

Política de exceção, candidatas, supervisores anteriores, `worker.py`, `worker_camofox.py`, demais Workers, units e serviços não foram alterados. Sem restart, deploy, ticket, aviso, publicação, commit/push ou consulta a documentos restritos. **F3-05/G4 aberto; F7-02/G7 e PQBR-114 pausados; F05-06 no-arm.**
