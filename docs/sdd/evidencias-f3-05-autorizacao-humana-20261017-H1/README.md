# F3-05: autorização humana antes de retomar pendentes

**Protótipo offline: 57 testes passaram, sem tickets ou mensagens reais. F3-05/G4 continua aberto.** Paperclip é o registro oficial; Discord só referencia o ticket e encaminha uma decisão autenticada pela porta falsa. Nada foi conectado aos Workers persistentes.

## O que foi implementado

Os arquivos novos ficam exclusivamente nesta pasta de evidências, fora de `src/` e dos entrypoints operacionais:

- `contratos.py`: modelos imutáveis e interfaces independentes para ticket Paperclip, painel, aviso/decisão Discord, política configurável de autorizadores, relógio e supervisor Temporal.
- `fluxo.py`: abertura idempotente, aviso opcional, decisão por ambos os canais, validação de identidade, persistência canônica e emissão do comando correlacionado.
- `fakes.py`: implementações em memória e injeção de falhas; nenhum cliente HTTP, SDK, endpoint, token ou pessoa real.
- `test_autorizacao.py`, `test_adversarial.py`, `test_limites.py`: cenários positivos, negativos, conflitos, corridas controladas e perda de respostas.
- `run_tests.py`: reprodução stdlib com ambiente isolado de importações e bloqueio Python de sockets, DNS e subprocessos.

O ticket contém versão, revisão, IDs do supervisor e runs, falha, recibo do registro da falha, IDs ordenados das operações pendentes, prazo, chaves de idempotência e, depois do despacho, decisão, ator sintético, canal e timestamps. Não contém conteúdo das operações, mensagem bruta de erro, segredo, contato ou nome real. O aviso Discord contém apenas referência/revisão do ticket.

A allowlist é configurada explicitamente em `PoliticaAutorizadores.por_canal`; as fixtures usam exclusivamente IDs artificiais. Nenhuma identidade real foi buscada, atribuída ou presumida. `FakePainel.autenticar_fixture` simula metadados server-side: não representa uma API pública que aceite a identidade informada no texto pelo usuário.

## Quando uma retomada é permitida

1. O supervisor falso está bloqueado, com falha correlacionada, recibo técnico e pendentes já aceitos.
2. Existe ticket canônico com receipt íntegro e revisão exata; o evento vem da porta autenticada correta, com ator na allowlist daquele canal e dentro da janela temporal.
3. Uma única decisão vence por compare-and-set. A aprovação é persistida no ticket, e uma leitura posterior confirma o mesmo registro/receipt **antes de chamar o supervisor**.
4. O receptor revalida o ticket aprovado, a allowlist, o prazo e o escopo exato, incluindo supervisor/run, falha/run, revisão e lista ordenada de pendentes. Só consome a autorização dentro da seção crítica falsa de deduplicação.
5. Somente IDs do conjunto imutável de pendentes capturado na falha podem prosseguir. Novos, falhos e concluídos não entram; a falha terminal permanece falha e a admissão de novos pedidos continua fechada.

Recusa ou expiração não chama retomada nem libera fila. Falha de Ticket API ou resultado de persistência incerto não chama Temporal. Aviso Discord indisponível retorna status de não notificado; não inventa aprovação e não impede o despacho posterior pelo painel. Erros propagam, sem fallback nem retries automáticos: os testes fazem reenvios explícitos com a mesma identidade/correlação.

Uma resposta perdida após gravar decisão deixa a primeira tentativa sem chamada ao supervisor; repetir o mesmo despacho relê a decisão canônica e prossegue. Um ACK perdido depois da retomada faz o reenvio retornar `retomada_ja_confirmada`, sem executar novamente os pendentes. O receipt da decisão não é confundido com confirmação da retomada.

## Evidências

- `execucao-pc/resultado.json`: contagem e identificação dos **57 testes**, todos aprovados, zero falhas/erros/pulados; registra que nenhum SDK Temporal ou módulo operacional `pqbr` foi importado.
- `execucao-pc/testes.log`: saída completa da suíte.
- `execucao-pc/demo-paperclip.json` e `execucao-pc/demo-discord.json`: estado sintético antes/depois, ticket decidido, comando, trilha de persistência anterior à chamada e resultado da duplicata.
- `primeira-execucao.log`: primeira rodada local, **45 testes com duas falhas**. Os testes adversariais detectaram falta da captura imutável de elegíveis na falha e de rejeição antecipada de concluídos no snapshot falso; ambas foram corrigidas e os testes foram mantidos. Não há alteração de política operacional.
- `preservacao.json` e `baseline.json`: comparação dos arquivos preexistentes, nota exata acrescentada ao roadmap e estado/units dos quatro Workers por consultas somente leitura.

A suíte cobre aprovação/recusa nos dois canais; ausência e troca de identidade; allowlist por canal e revogação; ticket ausente, stale, sem receipt ou adulterado; revisão/falha/run/pendentes divergentes; aprovação antiga e futura; expiração antes e durante o despacho; conflito de decisões; duplicatas; perda de resposta na abertura, na decisão e no ACK; API falsa indisponível; Discord indisponível; troca de estado entre persistência e retomada; recusa de operações novas/falhas/concluídas; e reconstrução da fachada sem cache local.

## Como reproduzir no PC

Na raiz `/home/pc/Workspace/PQBR`, execute com **um diretório de saída novo**:

```bash
cd docs/sdd/evidencias-f3-05-autorizacao-humana-20261017-H1
env -i PATH=/usr/bin:/bin python3 -I -S run_tests.py /tmp/pqbr-autorizacao-humana-repro-H2
```

O diretório informado precisa não existir; o runner não sobrescreve resultados. Não instala dependências, não inicia servidor, Worker ou container, não consulta credenciais e não executa CLI Paperclip/Discord/Temporal. O bloqueio de rede é no Python, não isolamento de kernel contra código hostil. O protótipo não precisa de conexão com esses serviços.

## O que ainda não foi validado

**Não é integração nem política de produção.** Identidades e receipts são simulados. O prefixo `fake-receipt` usa hash de integridade para exercitar correlação: não é assinatura, autenticação ou prova de um ticket real. A porta canônica é uma dependência confiável; adulteração simultânea do armazenamento falso e do seu hash está fora dessa garantia. Autenticação real, vínculo Discord–Paperclip, privacidade do canal, roteamento ao responsável real e persistência/controle de acesso dos serviços continuam pendentes.

Os locks/CAS e o consumo da autorização existem apenas em memória. A suíte demonstra reconstrução da fachada e retry contra os mesmos fakes; **não demonstra reinício de processo, crash safety, outbox durável, transação distribuída, fencing ou exactly-once de efeitos externos**. O supervisor é fake: não houve servidor Temporal, Workflow real, histórico ou replay nesta rodada, nem Activity externa. Uma futura implementação precisa revalidar ticket/receipt e fazer o consumo atômico no receptor; não basta transportar o antigo sinal de correlação dos protótipos anteriores. Não se reabre ator terminal nem se reconcilia efeito externo.

A expiração é exercitada por relógio injetado e chamada explícita; nenhum agendamento ou automação foi criado. Não há concessão de shell ou execução livre pelo canal.

Candidata, supervisores anteriores, correção operacional, Workers, units, configuração e serviços não foram alterados, reiniciados ou ligados ao protótipo. Nenhum ticket/aviso real, deploy, publicação, commit ou push. Nenhum conteúdo restrito foi consultado; os hashes de preservação são apenas comparação de bytes, não leitura documental.

**F3-05/G4 aberto; F7-02/G7 e PQBR-114 pausados; F05-06 no-arm.** Os testes não fecham TS-11, F05-06 nem qualquer gate operacional.
