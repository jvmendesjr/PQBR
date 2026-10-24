# Contrato editorial v2 — aprovado para F7-01

- **Status:** aprovado por José em 2026-10-16; gate G7 fechado; F7-01 concluído.
- **Data:** 2026-10-16.
- **Uso:** contrato de processo editorial, runbook e SOP aprovados no G7; complementa REGRAS sem substituí-la e não autoriza produção/publicação.

## 1. Autoridade e limites

Aplicar a precedência de `docs/REGRAS.md` §0 > `SPEC.md` > `ARQUITETURA.md` > `TESTES.md` > `ROADMAP.md`. Para este candidato, as referências operacionais são REGRAS §§4–5 e §9, SPEC RF-07, ARQUITETURA §11, TESTES V1/TS-02 e `docs/AGENTES.md`. José aprovou a CTA contextual em t467 (2026-10-16), agora registrada em `DECISOES-LOG.md` e incorporada a REGRAS §5, RF-07, ARQUITETURA §11, TS-02 e ao validador. `tipo_cta` registra `trocadilho_tema`, `convite_seguir` ou `fallback`; a adequação semântica permanece sujeita à revisão editorial, sem fingir validação automática.

R1–R4/R6/R8/R9 foram aprovadas em t467 como diretrizes revisáveis, não gates automáticos; R5 é alerta não bloqueante. Não há decisão pendente sobre esses itens. Aplicar HOLD por risco material, regra realmente aberta ou bloqueio canônico, não pela falha automática de uma diretriz. R-005 permanece concluído.

Este fluxo descreve gates documentais. Não autoriza geração de vídeo, upload, agendamento, publicação, uso de quota real, criação de issue ou alteração de serviços. O Auditor visual completo pertence a F7-02; o bloco visual e o contador do NotebookLM pertencem a F7-03; os gates de produção e de canal permanecem independentes.

## 2. Regras já confirmadas que o processo deve preservar

- Tom de “nós, brasileiros”: humor predominante, sátira leve e afetuosa do comportamento (nunca da pessoa ou de um grupo), explicação lógica e encerramento caloroso.
- Narrador único; não falar nem escrever nomes de personagens ou rótulos `Nome:`.
- **CTA contextual aprovado e canonicalizado em t467:** trocadilho ligado ao tema quando natural; caso contrário, convite natural a seguir o canal; `Segue o Porquê BR` é fallback. Nunca pedir comentários. O schema valida o tipo declarado e o fallback; o contexto semântico exige revisão editorial.
- Roteiro de 15 a 180 segundos, alvo aproximado de 50 segundos, estimado a 2,3 palavras/segundo.
- O loop deve conectar o encerramento à primeira cena; não acrescentar cauda, tela parada ou fade. A cadência visual e o tratamento do logo/end card seguem REGRAS §5, mas não são aprovados por um dry-run textual.
- Personagem: um por padrão; até dois é desejável. Mais de dois não é, por si só, reprovação editorial em REGRAS; a limitação atual do modelo visual é registrada como lacuna de implementação, não como nova regra.
- Conteúdo fora do escopo ou bloqueado por REGRAS §4/§5 não avança. Dúvida de segurança, direitos ou regra pendente resulta em `HOLD`, nunca em aprovação por conveniência.
- NotebookLM é o motor intelectual para pesquisa, ideação, roteiro e SEO. Agentes orquestram e validam; não substituem essa etapa com pesquisa/criação independente. Produção usa caderno efêmero, nunca o caderno raiz.

### R1–R6, R8 e R9 — diretrizes aprovadas em t467, revisáveis e não bloqueios automáticos

O rascunho legado foi consultado com autorização. José aprovou estas diretrizes em 2026-10-16 como orientação editorial revisável, não como gates automáticos. Elas estão refletidas em REGRAS §5. R5 permanece apenas alerta não bloqueante porque a evidência é limitada a um caso:

| ID | Proposta mapeada | Observação para validação |
|---|---|---|
| R1 | Mostrar a cena do hábito nos primeiros 2 s; evitar abrir com conceito abstrato. | Requer evidência de imagem/timecode; texto isolado não prova. |
| R2 | O gancho levanta a pergunta e não entrega a resposta; reservar resposta para o payoff. | Conferir no roteiro e no plano de cenas. |
| R3 | Apresentar conflito ou piada até 4 s, sem introdução longa. | Critério temporal; validar com fala/timecode. |
| R4 | Se entrar termo técnico, acompanhar no mesmo momento com imagem ou piada. | Diretriz de revisão editorial; fato sem sustentação segue o gate de fontes/factualidade, não bloqueio automático por R4. |
| R5 | Evitar sensação física incômoda no miolo. | Alerta de revisão não bloqueante aprovado; hipótese baseada em um caso e evidência limitada. |
| R6 | Explicar o porquê real como recompensa da piada. | Exige fonte para afirmação factual e linguagem simples. |
| R8 | Priorizar comportamento reconhecível; curiosidade enciclopédica só quando ligada a uma mania. | Diretriz de pauta/enquadramento, sem proibir tema por si só. |
| R9 | Priorizar situações vividas em casa e em família. | Preferência de pauta, não exclusão de outras situações brasileiras. |

**Aplicação:** R1–R4/R6/R8/R9 são revisáveis, não bloqueios automáticos; R5 é alerta não bloqueante. O gate G7 continua sendo o aceite do contrato completo e do SOP/runbook, não uma reabertura destas decisões.

## 3. Fluxo operacional aprovado no G7 (dry-run sem produção)

| Etapa | Entradas | Saída/evidência | Validações e destino de falha | Responsável desenhado |
|---|---|---|---|---|
| 1. Receber pauta | código do episódio, tema vindo da grade, janela e estado de elegibilidade | ficha de entrada versionada | confirmar escopo PQBR, R10/anti-repetição e bloqueios conhecidos; dado ausente ou regra pendente → `HOLD` | Líder Editorial coordena; código/grade fornece os gates determinísticos |
| 2. Pesquisa e procedência | tema elegível, instrução, persona-base e caderno efêmero | resumo/ideação do NotebookLM, lista de fontes e evidência de origem | conferir procedência e pelo menos duas fontes para o roteiro; caderno raiz proibido; insuficiência → reprocessar nos limites vigentes ou `HOLD` | Roteirista orquestra NotebookLM; Pesquisador de Origem confere fontes |
| 3. Brief e estrutura | pacote de pesquisa, tema, público/idioma pt-BR e restrições confirmadas | ângulo, gancho, progressão e payoff; proposta de loop | revisar conexão com cotidiano brasileiro, escopo, procedência e segurança; aplicar R1–R4/R6/R8/R9 como orientação revisável, sem bloqueio automático; risco material ou fato sem fonte → `HOLD` pelo gate correspondente | NotebookLM gera; Líder Editorial revisa e registra versão |
| 4. Roteiro | brief aprovado e fontes | saída estruturada `RoteiroShort` (fala, título, entidades e, quando exigido pela integração atual, bloco visual) | validar schema, duração, `tipo_cta` e CTA conforme §5, veto a pedido de comentário e rótulo de fala; revisão humana adicional para nomes em prosa, tom, lógica, calor e loop, pois o validador não cobre tudo | Roteirista coordena NotebookLM e valida; Líder Editorial responde pela revisão editorial |
| 5. Conformidade editorial | roteiro versionado, fontes e checklist | checklist de segurança/direitos e parecer `PASS`/`HOLD` | política bloqueada, terceiro/marca, fonte insuficiente ou risco não resolvido não avança; aplicar CTA contextual conforme §5 e nunca pedir comentários | Líder Compliance; escalonamento ao Diretor/José conforme regra vigente |
| 6. SEO (pós-roteiro, fora do aceite mínimo de V1) | roteiro validado e mesmas fontes | `PacoteSEO` versionado | geração pelo NotebookLM; validar limites do RF-06; nunca inserir pedido de comentário | Especialista SEO orquestra; validação determinística do pacote |
| 7. Fechamento documental | roteiro, evidências, validações e pareceres | pacote editorial rastreável e pronto apenas para o próximo gate autorizado | todos os itens devem ter evidência e versão; `PASS` editorial não significa G7, liberação de produção ou publicação | Líder Editorial consolida; José aprova o contrato/gate G7 |

### Saída mínima do pacote editorial

1. `episode_id`, tema, estado da pauta e versão do brief;
2. lista de fontes/procedência e resumo de pesquisa;
3. `RoteiroShort` validado e versão/hash do artefato;
4. resultado de cada validação, com evidência e responsável (automático ou humano);
5. pareceres `PASS`/`HOLD`, defeitos e correções tentadas;
6. indicação explícita `SEM PRODUÇÃO` até que os gates independentes autorizem a etapa seguinte.

## 4. SOP e runbook aprovados no G7

1. **Abrir** a ficha somente a partir de pauta elegível; registrar código e versão. Não inventar tema, pesquisa ou fato para preencher campo ausente.
2. **Pesquisar** no NotebookLM em caderno efêmero. Capturar fontes/proveniência; o agente não pesquisa por conta própria, salvo a exceção documentada pelas regras vigentes.
3. **Gerar** brief e roteiro no NotebookLM conforme o contrato vigente. Manter resposta original e versão normalizada separadas para rastreabilidade.
4. **Validar primeiro por código**: schema, faixa de duração, campo `tipo_cta`, coerência do fallback, proibição de pedidos de comentário e campos requeridos. Registrar a saída e os erros sem segredos.
5. **Revisar o que o código não prova**: tom, sátira afetuosa, lógica, nomes falados/escritos, verdade/procedência das afirmações, loop e risco editorial. Não transformar “não detectado” em “aprovado”.
6. **Corrigir apenas dentro das regras já aprovadas**, com a escada e os limites de REGRAS §3.1. Se a correção mudar resultado editorial/conformidade, se uma regra pendente for necessária ou se o erro persistir, registrar `HOLD` e escalar; não contornar o gate.
7. **Aprovar somente o pacote documental** quando todas as verificações aplicáveis tiverem evidência. Este status não autoriza workflow de produção, provider, upload ou publicação.
8. **Fechar a execução** com o veredito, as versões, contagem/duração estimada, fontes e trilha de validação. Manter as evidências de dry-run separadas de episódios reais.

### Estados de trabalho (rótulos deste SOP, não estados implementados no banco)

`RECEBIDO` → `PESQUISA_PRONTA` → `ROTEIRO_RASCUNHO` → `VALIDAÇÃO` → `PASS_EDITORIAL` ou `HOLD`. `PASS_EDITORIAL` pode produzir um handoff documental; não transita para `PRODUÇÃO` por este contrato.

## 5. Matriz de responsabilidade

- **Líder Editorial:** coordena o fluxo, pauta/variedade e revisão do enquadramento; não substitui a pesquisa/ideação do NotebookLM.
- **Roteirista:** orquestra a pesquisa e o roteiro no caderno efêmero, valida o `RoteiroShort` e monta o handoff; não cria roteiro independente.
- **Pesquisador de Origem:** confere a procedência e as fontes da pesquisa do NotebookLM; pesquisa adicional só como complemento/fallback documentado.
- **Líder Compliance:** verifica políticas do YouTube e direitos autorais, escalando dúvidas conforme as regras.
- **Especialista SEO:** orquestra o SEO no NotebookLM e valida `PacoteSEO`; não redige independentemente nem pede comentários.
- **Auditor:** seu gate pré-publicação é F7-02; não é simulado nem considerado concluído aqui.
- **Diretor/José:** diretor roteia/escalona conforme governança; José decide regra canônica e o aceite G7. Este candidato não toma essas decisões por ele.

## 6. Compatibilidade e lacunas da implementação observada

No primeiro dry-run, anterior a t467, o validador aceitou o caso-base e rejeitou a CTA contextual por exigir o fallback literal. Após t467, o código foi atualizado: 25 testes passaram, inclusive o caminho local `roteiro_de_texto` → `RoteiroShort` → Markdown com CTA contextual sintética e sem providers/produção. Também são rejeitados pedido de comentário, rótulo `Nome:`, duração inferior, fonte insuficiente e tipo/fallback incompatível. O dry-run confirma apenas as propriedades estruturais descritas nas lacunas abaixo:

- aceita pontuação final comum após o fallback `Segue o Porquê BR`; t467 define o texto-fallback, sem tornar ponto/exclamação um bloqueio editorial;
- aceita um nome próprio dentro de uma fala se ele não estiver no formato `Nome:`;
- não prova semanticamente o loop, o tom, a procedência das fontes ou a ausência de nomes falados/escritos;
- requer `bloco_visual` e quatro ou mais cenas no validador atual, embora F7-03 continue um item separado e aberto; o fixture visual do dry-run é sintético;
- representa apenas `personagem`/`personagem_2`, enquanto REGRAS diz que mais de dois não é reprovação automática.

### Superfícies impactadas pela CTA contextual aprovada

A reconciliação t467 abrangeu `src/pqbr/contratos/__init__.py` (campo e validador), `src/pqbr/workflows/criativo.py` (prompt/normalização/artefato), fixtures de `activities.py` e `producao.py`, `scripts/e2e/e2e_pre.py` e os testes de contrato/criativo. RF-07, ARQUITETURA §11 e TS-02 agora documentam `tipo_cta`. O schema valida enum, fallback e veto a comentários; revisão humana avalia se o trocadilho é natural e ligado ao tema.

O código foi atualizado e os testes estruturais passaram; o conteúdo completo ainda é candidato até o aceite G7. O validador não prova o mérito editorial nem o loop visual, e o dry-run não substitui a revisão humana nem os gates F7-02/F7-03 ou operacionais.

## 7. Fechamento de F7-01 — G7 aprovado

José aprovou o contrato v2 e fechou G7 em 2026-10-16. V1: contrato aprovado e `RoteiroShort` coerente, verificado por 25 testes unitários afetados. F7-01 está concluído. Isso não fecha F05-06, F05-08, F05-09, F3-01/G3, F7-02, F7-03 ou qualquer gate de produção.
