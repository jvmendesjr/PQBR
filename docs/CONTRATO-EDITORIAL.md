# Contrato editorial da PQBR (v2, oficial desde 23/10/2026)

- **Status:** aprovado por José em 2026-10-16; gate G7 fechado; F7-01 concluído.
- **Data:** 2026-10-16. Oficializado como `docs/CONTRATO-EDITORIAL.md` em 23/10/2026 (t473); o v1 foi para `docs/_obsoleto/CONTRATO-EDITORIAL-v1.md`. O anexo A traz, sem alteração, as seções do v1 que continuam canônicas (público, promessa, tom, categorias de sátira, gabarito, duração, diretrizes de roteiro/estilo, §15–§17, incluindo o bloco §16.7 usado pelo pacote canônico). Ficaram só no v1 arquivado: §9 (métricas sugeridas), §10 (divergências entre fontes), a nota de fonte do `rede`, §14 (superado) e as partes de inventário/próximo passo do §15.
- **Uso:** contrato de processo editorial, runbook e SOP aprovados no G7; complementa REGRAS sem substituí-la e não autoriza produção/publicação.

## 1. Autoridade e limites

Aplicar a precedência de `docs/REGRAS.md` §0 > `SPEC.md` > `ARQUITETURA.md` > `TESTES.md` > `ROADMAP.md`. Para este contrato, as referências operacionais são REGRAS §§4–5 e §9, SPEC RF-07, ARQUITETURA §11, TESTES V1/TS-02 e `docs/AGENTES.md`. José aprovou a CTA contextual em t467 (2026-10-16), agora registrada em `DECISOES-LOG.md` e incorporada a REGRAS §5, RF-07, ARQUITETURA §11, TS-02 e ao validador. `tipo_cta` registra `trocadilho_tema`, `convite_seguir` ou `fallback`; a adequação semântica permanece sujeita à revisão editorial, sem fingir validação automática.

R1–R4/R6/R8/R9 foram aprovadas em t467 como diretrizes revisáveis, não gates automáticos; R5 é alerta não bloqueante. Não há decisão pendente sobre esses itens. Aplicar HOLD por risco material, regra realmente aberta ou bloqueio canônico, não pela falha automática de uma diretriz. R-005 permanece concluído.

Este fluxo descreve gates documentais. Não autoriza geração de vídeo, upload, agendamento, publicação, uso de quota real, criação de issue ou alteração de serviços. O Auditor visual completo pertence a F7-02; o bloco visual e o contador do NotebookLM pertencem a F7-03; os gates de produção e de canal permanecem independentes.

## 2. Regras já confirmadas que o processo deve preservar

- Tom de “nós, brasileiros”: humor predominante, sátira leve e afetuosa do comportamento (nunca da pessoa ou de um grupo), explicação lógica e encerramento caloroso.
- Narrador único; não falar nem escrever nomes de personagens ou rótulos `Nome:`.
- **CTA contextual aprovado e canonicalizado em t467:** trocadilho ligado ao tema quando natural; caso contrário, convite natural a seguir o canal; `Segue o Porquê BR` é fallback. Nunca pedir comentários. O schema valida o tipo declarado e o fallback; o contexto semântico exige revisão editorial.
- **CTA preservado na produção (José 25/10/2026, ERR-MON-02):** voz, montagem e pós nunca trocam o CTA aprovado do roteiro por um fechamento genérico; um take padrão (ex.: `cta-padrao-B.mp3`) serve só de referência de entonação. A última linha da legenda deve ser igual à última linha do roteiro.
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

---

# Anexo A — regras canônicas herdadas do v1 (texto integral, sem alteração)

## 1. Público (relatório principal)

| Dado | Valor | O que significa para o roteiro |
|---|---|---|
| País | Brasil 81,3%; lusófonos somam mais de 85% (Portugal 2,4%, Moçambique 0,7%, Angola 0,5%) | Os costumes são brasileiros e a linguagem é a do Brasil. |
| Gênero | Masculino 67,4%, feminino 32,6% | Não usar piada que depende de estereótipo de gênero para agradar a maioria. |
| Idade | 13–17: 23,4% · 18–24: 10,0% · 25–34: 24,1% · 35–44: 22,4% · 45–54: 14,5% · 55+: 5,7% | Quase 1 em 4 espectadores é adolescente. O humor tem de servir para a família, e nenhum vídeo pode ensinar ou incentivar um ato perigoso. |
| Aparelho | Celular 77,2% · TV 15,4% · tablet 5,2% · computador 3,0% | O texto na tela precisa ser legível no celular **e** na TV. |
| Fidelidade | 99,5% são espectadores novos; recorrentes abaixo de 0,1% | Quase ninguém conhece o canal. Cada vídeo tem de funcionar sozinho nos 2 primeiros segundos. |
| Descoberta | Feed de Shorts 93,2% · busca 3,3% · externo 0,3% (WhatsApp 60% e Telegram 20% do externo) | O feed decide quase tudo. Quando há compartilhamento, ele acontece em família, pelo WhatsApp. |
| Pico de audiência (horário de Brasília) | Dias úteis das 14h às 16h; fins de semana das 07h às 09h e das 14h/15h às 16h | Serve para conferir os horários de publicação. Fica fora deste contrato. |

**Resumo:** um público brasileiro amplo, de 13 a 44 anos e majoritariamente masculino, que chega pelo feed sem conhecer o canal e assiste no celular ou na TV da sala.

## 2. Promessa do canal (uma frase)

**"O Porquê BR pega uma mania que todo brasileiro tem, ri dela junto com você e mostra por que a gente faz isso."**

## 3. Tom

- O objetivo do humor é a **identificação**: o espectador pensa "sou eu" ou "é meu pai". Ninguém deve sair se sentindo alvo.
- **Satiriza o comportamento, nunca a pessoa ou o grupo.** Não pode haver piada sobre região, sotaque, classe social, pobreza, gênero, idade, religião, corpo ou profissão como identidade.
- **Satiriza, nunca incentiva.** Quando o hábito tem risco (trânsito, eletricidade, fogo), o vídeo pode rir do hábito, mas o desfecho mostra o custo ou a regra certa, nunca o atalho como solução.
- Os personagens usam ironia e não dão aula. A Dra. Sandra é a "norma rígida" cômica e **não** dá orientação médica, jurídica ou financeira. O Seu Valdemar defende a gambiarra com orgulho, mas o vídeo nunca ensina uma gambiarra perigosa como receita.
- A explicação científica do "porquê" funciona bem, desde que seja o *payoff* da piada, e não uma aula (ver seção 5).

## 4. Três categorias de sátira

### 4.1 Aceitável (segue direto, dentro das barreiras normais)
1. Manias domésticas inofensivas: o restinho do sabonete, espremer a caixa de leite, bater no fundo da lata, lamber a tampa do iogurte.
2. Rituais do cotidiano: parar o micro-ondas em 00:01, a despedida no portão, abrir a geladeira sem fome.
3. Hábitos de família: só acordar quando desligam a TV.
4. Gambiarras sem risco: fita adesiva no controle remoto, garrafa de gelo atrás do ventilador.

### 4.2 Inadequada (bloqueada em qualquer pontuação de polêmica)
1. Humilhar pessoas ou grupos: região ou sotaque, classe social ou pobreza como piada, gênero, idade, religião, corpo, deficiência.
2. Ensinar ou incentivar um ato ilegal ou perigoso: "como passar no amarelo sem levar multa", gambiarra elétrica como solução, beber e dirigir.
3. Política partidária, tragédias e notícias de morte ou violência.
4. Conselho de especialista em saúde, finanças ou direito dado por personagem, inclusive pela "Dra." Sandra.
5. Tema que só existe para gerar briga nos comentários, sem uma mania reconhecível por trás.

### 4.3 Exige revisão humana do José antes de entrar na grade
> ⚠️ **SUPERADO** por t327: não há revisão humana prévia da grade. A revisão humana só acontece quando um item falha em todos os caminhos previstos (REGRAS §5). Os temas abaixo continuam como referência de risco; a regra de polêmica > 75 (t200) segue no REGRAS §4.

1. **Referência: o sinal amarelo** ("acelera que dá tempo"). O tema é trânsito, com risco real, e os comentários viraram debate de regra. Mesmo assim, é o vídeo de maior tempo de exibição do canal (10,6 h). Funcionou **porque** satiriza a conta mental do motorista sem ensinar a avançar.
   - **O que serve de régua:** o hábito com risco aparece como absurdo, e o fecho deixa a regra correta clara.
2. **Eletricidade, fogo e risco doméstico:** a tomada do chuveiro que derrete, o "rabo quente" para ferver água, o chuveiro elétrico que "não eletrocuta", 127 V e 220 V. O roteiro precisa remeter a um profissional e não pode sugerir conserto ou uso caseiro arriscado.
3. **Preço, dinheiro e economia:** o feijão no pote de sorvete (os comentários foram para "o Brasil é pobre"), "café tão caro", "PIX de graça", chorar desconto. O risco é a piada escorregar para a pobreza ou para um conselho financeiro.
4. **Hierarquia e relações sociais e de trabalho:** chamar estranho de "chefe" ou "patrão". O tema encosta em classe social e ainda falhou na retenção.
5. **Qualquer tema com pontuação de polêmica acima de 75** (regra já aprovada no ponto 3).

## 5. O que funcionou e o que falhou, transformado em regras

| Evidência | Regra editorial |
|---|---|
| "Chefe/Patrão": só 10,1% assistiram, com queda entre 0:02 e 0:04 porque o gancho soou abstrato (relatório). Pelo aditivo, ~3,9 s por visualização. | **R1. O gancho é a cena do hábito, mostrada nos primeiros 2 s, e não um conceito.** |
| "Garrafa de gelo": só 19,3% assistiram, com queda entre 0:03 e 0:05 porque o gancho entregou a resposta cedo demais. Pelo aditivo, 1.201 visualizações, mas só ~6 s por visualização. | **R2. O gancho levanta a pergunta e não responde. A resposta fica para o *payoff*.** |
| "Churrasqueiro": queda em 0:04 e introdução explicativa arrastada. "Despedida no portão" e "sacola bonita" ficaram em ~4 a 4,5 s por visualização. | **R3. O conflito ou a piada aparece em até 4 s, sem introdução.** |
| "Lata": queda em 0:18, no termo "tixotrópico" sem apoio visual. | **R4. Termo técnico só entra com imagem ou piada no mesmo segundo.** |
| "Picolé": queda entre 0:20 e 0:24, na "aflição da madeira". | **R5. Evitar sensação física incômoda no miolo.** Hipótese, com um caso só. |
| "Sinal amarelo" (~29 s por visualização), "TV" (~27 s) e "tomada do chuveiro" seguram pela curiosidade sobre a causa real. | **R6. Explicar o porquê de verdade, como recompensa da piada.** |
| "Sinal amarelo": queda leve em 0:48, só na transição para o CTA. | **R7. CTA contextual no fecho: trocadilho ligado ao tema quando natural; caso contrário, convite natural a seguir, com `Segue o Porquê BR` como fallback. Nunca pedir comentários.** [t467; t263] |
| Temas de curiosidade enciclopédica tiveram baixo alcance: copo americano (206), horário de Brasília (85, apesar de 1.219 impressões), 127 V/220 V (56), "PIX de graça" (43), filtro de barro (34). A exceção é "terremoto", com 135 visualizações e +3 inscritos. | **R8. Priorizar comportamento que o espectador reconhece em si. Curiosidade "de almanaque" só quando houver uma mania por trás.** |
| Os dois maiores geradores de inscritos ("TV", +14) e os seguintes ("sabonete" e "tomada do chuveiro", +4 cada) são situações de casa e de família. | **R9. Priorizar situações vividas em casa e em família.** |
| O feijão no pote de sorvete foi publicado **duas vezes** (76 e 387 visualizações). Há temas vizinhos repetidos: chuveiro elétrico x tomada do chuveiro; sacola de sacolas x sacola bonita. | **R10. Um tema, um vídeo.** A barreira contra repetição vale também para variações próximas (ver o observador de conformidade, item de variedade). |

## 6. Duração (decisão do José, t208)

> ⚠️ **SUPERADO** em parte por t271: duração de 15 s a 3 min, **alvo de ~50 s** (REGRAS §5).

- **A duração é definida pela qualidade. Não há teto editorial.** Um bom trabalho não é cortado para caber num limite, e passar de 60 s é aceito inclusive como norma.
- **O teto técnico é o limite do Shorts: 3 minutos (180 s), em formato vertical ou quadrado.** Fonte: Central de Ajuda do YouTube, "Understand three-minute YouTube Shorts" (support.google.com/youtube/answer/15424877).
- **Atenção de direitos:** um Short com mais de 1 minuto que recebe reivindicação do Content ID **fica bloqueado** (support.google.com/youtube/answer/10343433). Acima de 60 s, a checagem de direitos de áudio do auditor e do observador de conformidade passa a ser bloqueante.
- **Precisam de revisão (marcar no blueprint):**
  - o contrato `RoteiroShort`, hoje com 40 a 60 s → **de 15 s até o máximo do Shorts**, ajustando também o limite de palavras proporcionalmente;
  - a checagem de duração do auditor, hoje de 15 a 60 s → **de 15 s até o máximo do Shorts**.
- **O que os dados mostram (observação, não causa).** Na tabela do aditivo, a mediana de visualizações por faixa de duração foi:

  | Faixa de duração | Vídeos | Mediana de visualizações |
  |---|---|---|
  | Até 59 s | 17 | 138 |
  | 60 a 69 s | 21 | 707 |
  | 70 s ou mais | 8 | 161 |

  Data e tema não estão isolados. A duração em si não é critério de reprovação.
- **Pendência técnica:** verificar se o NotebookLM entrega vídeos verticais acima de ~60 s no formato usado hoje (ver o relatório ao José).

## 7. Regra explícita: engajamento não é medida de segurança

- Muitos comentários, debate ou visualizações **não** tornam um tema aceitável. A segurança é decidida pelas categorias da seção 4 e pelo observador de conformidade, **antes** de olhar números.
- A pontuação de polêmica serve só para **priorizar** temas que já passaram pelo filtro de segurança. Ela nunca libera um tema bloqueado.
- **Caso de referência:** o sinal amarelo teve o maior tempo de exibição do canal e mesmo assim é um tema de revisão humana. O sucesso dele não libera outros temas de trânsito.

## 8. Gabarito (casos de referência para o auditor e o piloto)

Os números vêm do aditivo. "s/vis" é o tempo de exibição dividido pelas visualizações.

**Fortes:**

| Vídeo | Duração | Visualizações | Tempo de exibição | s/vis | Inscritos | Por que é referência |
|---|---|---|---|---|---|---|
| Só Acorda Quando Desligam a TV? | 1:09 | 1.372 | 10,2 h | ~27 | **+14** | Mais visualizações e mais inscritos (25% do total). |
| Sinal amarelo "acelera que dá tempo" | 1:06 | 1.318 | **10,6 h** | **~29** | +3 | Maior tempo de exibição; é o modelo de tema "perto da linha". |
| Tomada do Chuveiro Derrete | 1:07 | 1.141 | 5,9 h | ~19 | +4 | A explicação técnica funciona como *payoff*. Também é caso de revisão por segurança. |
| Controle Remoto com Fita Adesiva | 1:00 | 926 | 4,8 h | ~19 | +1 | Gambiarra visual que segura o espectador (55% de retenção no relatório). |
| Restinho do sabonete | 1:05 | 1.009 | 3,9 h | ~14 | +4 | Mania clássica que converte em inscritos. |

**Fracos:**

| Vídeo | Duração | Visualizações | s/vis | Defeito |
|---|---|---|---|---|
| Chefe ou Patrão | 1:03 | 275 | ~4 | Gancho abstrato; queda entre 0:02 e 0:04. |
| Sacola bonita de loja de shopping | 1:13 | 482 | ~4,5 | Menor % da duração assistida entre os vídeos com mais de 200 visualizações. |
| Despedida no Portão | 0:55 | 458 | ~4 | Abandono quase imediato. A causa não foi analisada no relatório. |
| Garrafa de Gelo no Ventilador | 1:00 | 1.201 | ~6 | Resposta entregue no gancho. **Prova que alcance não é qualidade.** |
| Prendedor de roupa na cozinha / Biscoito na xícara | 1:05 / 0:58 | 707 / 450 | ~5,6 | Abandono precoce. Causa a investigar. |
| Fundo da lata / Palito de picolé | 1:08 / 1:00 | 1.035 / 1.219 | ~11,5 | Termo técnico em 0:18 / aflição física entre 0:20 e 0:24. |

**Repetição a não imitar:** feijão no pote de sorvete, publicado duas vezes (lote 1 com 76 visualizações, lote 2 com 387).

## 11. Diretrizes de roteiro (t212 e t213, José, 08/10/2026), regras
1. **Elenco enxuto:** um personagem por padrão; nunca mais de dois por vídeo. ⚠️ SUPERADO por t264: até 2 é o desejado; mais que isso **não reprova**. O plano final também respeita esse limite (nada de "foto de grupo" com mais personagens do que o vídeo usa).
2. **Sem nomes:** nenhum nome de personagem falado ou escrito na legenda ou na tela. O personagem sem nome é "qualquer brasileiro". (Fichas Zé/Lia/Valdemar **pausadas**, t400; §16.)
3. **Enquadramento brasileiro:** o texto trata a mania como coisa nossa ("nós, brasileiros, temos essa mania…", "todo brasileiro já…"), mesmo que aconteça em outros lugares. Busca uma explicação lógica, mas o **humor predomina** sobre a aula.
4. **Sátira leve:** "aquele sorrisinho no canto da boca". Nunca ridiculariza o brasileiro; o brasileiro é brincalhão, esperto, criativo.
5. **Sentimento "a gente é assim mesmo" (t213):** engraçado, mas verdadeiro. Orgulho carinhoso de ser brasileiro; o espectador reconhece a própria identidade, sem vergonha. **O final pousa no reconhecimento caloroso** ("é, a gente é assim mesmo… e tudo bem"), nunca na zombaria nem no sermão. A explicação lógica não "corrige" o espectador: ela dá um motivo para a mania e a devolve com carinho.
6. **Narração:** um único narrador em 3ª pessoa ou 1ª do plural ("a gente"), sem rótulos "Nome:" no texto (o gerador lê rótulos em voz alta; teste de 08/10).

## 12. Guia de estilo (a partir dos vídeos mais fortes)
> **Limite da evidência:** os roteiros e transcrições dos 4 vídeos mais fortes **não existem localmente** (nem em /workspace nem nas skills; os episódios locais são só tomada 3 pinos, 127/220 V e terremoto). Os padrões abaixo vêm dos títulos, das métricas do aditivo e da retenção e dos comentários do relatório inicial. Confirmar com os roteiros quando o rede os entregar.

| Vídeo de referência | Métrica (aditivo / relatório) | O que ensina |
|---|---|---|
| Só acorda quando desligam a TV | 1.372 vis., +14 inscritos (1,02%), 64,1% escolheram assistir; curiosidade "o cérebro processa o silêncio" segura até 0:40 | Cena de família que todo mundo viveu + um porquê de cérebro/corpo, dito simples. CTA fluido. |
| Sinal amarelo | 10,6 h (maior tempo), 79,8% de retenção; queda só em 0:48, na transição para o CTA; comentário: "a capacidade do brasileiro de fazer essa conta em um milésimo de segundo" | O monólogo interno vira o título ("acelera que dá tempo"). O humor elogia a esperteza do brasileiro. A quebra para o CTA é o ponto fraco. |
| Controle remoto com fita | 926 vis., 55% de retenção; "o tapa no controle" segura os primeiros 25 s | Gag visual repetível no início; a gambiarra é tratada com orgulho. |
| Tomada do chuveiro | 1.141 vis., 67,9%; a tensão segura até 0:42 e cai depois do fim da explicação | O porquê técnico funciona como payoff, mas depois que ele termina o vídeo precisa acabar logo. |

**Padrões para roteiro:**
- **Gancho (0–2 s):** a cena da mania já acontecendo + a frase-pensamento do brasileiro entre aspas ou exagero carinhoso ("como quem desarma bomba", "acelera que dá tempo"). Pergunta "Por que a gente…?" até 3 s, sem resposta.
- **Voz do narrador:** "a gente" / "todo brasileiro", cúmplice, com o sorrisinho no canto da boca; frases curtas; nada de professor.
- **Ritmo da piada:** uma imagem engraçada ou exagero a cada 5–8 s nos primeiros 25 s (onde a curva se decide); depois a piada continua dentro da explicação.
- **O porquê:** UM mecanismo real, em palavras do dia a dia, com imagem no mesmo segundo (sem termo técnico solto). Entra depois de ~40% do vídeo.
- **Partitura com bloco de motion (t145u, REGRAS §26):** gancho (vídeo) → conflito (vídeo) → transição padrão → **bloco explicativo em motion graphics** (o porquê, ~18–20 s, com o bloco de números travados na tela) → transição de volta → reconhecimento (vídeo) → CTA + loop (vídeo retomando a cena 1). O gancho fica em vídeo (R1); o bloco nunca é a última cena (§11.2) e não cobre o CTA falado (§11.1). Vale como padrão da rotina; o roteiro continua do NotebookLM.
- **CTA contextual vigente (t467):** trocadilho ligado ao tema quando natural; senão, convite natural a seguir; fallback `Segue o Porquê BR`. Nunca pedir comentários. O CTA fecha o payoff sem ponte longa, nos últimos ~5–8 s.
- ⚠️ SUPERADO em parte por t271 (alvo ~50 s; "60–80 s, 185–235 palavras" não vale mais). Texto antigo: **Duração:** dimensionar pelo texto. Na rodada final de 08/10 a voz leu ~3,0 palavras/s: 178 palavras deram 59,3 s e 190 deram 63,9–67 s. Para 60–80 s, use **185–235 palavras**.

### 11.1 CTA e encerramento (t214, José, 08/10/2026), regra
> **Regra vigente (t467):** CTA contextual conforme §5; t262 (CTA exclusivamente literal) foi substituída; a proibição de comentários de t263 permanece.

- **CTA contextual [t467]:** use trocadilho ligado ao tema quando natural; caso contrário, convite natural a seguir, com `Segue o Porquê BR` como fallback; nunca pedir comentários.
- **Encerramento visual:** o logo do Porquê BR entra no fim com zoom-in suave (~1,5–2 s), feito na pós-produção com FFmpeg.
- O CTA não pode ser coberto por selo ou logo enquanto é falado.

### 11.2 Loop (t215, José, 08/10/2026), regra
- O fim emenda no começo: a última frase (que já carrega o CTA) é completada pela primeira frase/cena, ou leva direto a ela, para que o replay pareça contínuo.
- A última cena retoma o enquadramento, o objeto e a pose da primeira cena.
- Nada de cauda depois do CTA: o logo entra como sobreposição rápida com zoom-in **durante** a última fala (≈1,5 s), sem tela final parada, sem silêncio e sem fade-out.
- Sem end card da NotebookLM. O corte do fim só acontece se o end card for detectado.

## 13. Dinamismo e relação texto-imagem (t217)
- Tom/redação da rodada final (toalha molhada) aprovado por José como referência.
- Cada fala tem imagem correspondente ao que está sendo dito (relação texto-imagem verificável pelo auditor: transcrição × frames). ⚠️ RESOLVIDO por t327: imagem que não corresponde à fala **não reprova** (pode ser transição breve); não é critério estrito.
- O personagem age em cena (faz o hábito), não só observa; roteiros descrevem ações visíveis.
- Ritmo de vídeo, não de slide: troca de plano/ação a cada ~3–5 s; reprovar sequências estáticas ou só infográfico.
- Consistência do personagem segue como meta com tolerância (reforçado por t264: métrica, não trava): desvios leves aceitos se o dinamismo e a relação texto-imagem estiverem bons; reavaliar conforme evolução do modelo/plataforma.

## 15. Aditivo: 4 roteiros de referência (09/10/2026, incorporado)

> Completa a seção 12 do rascunho v1. Os roteiros dos 4 vídeos de referência chegaram do rede em `docs/pesquisas/REF-roteiros-4-videos.md`. O levantamento amplo está no levantamento de vídeos publicados (60 vídeos; fora do git, arquivado no Drive `PQBR/_arquivo-docs-2026-10-09/`; a lista de temas está em `db/seeds/temas-publicados.csv`). Métricas por vídeo continuam hipótese até a YouTube Analytics API.

### O que os 4 roteiros confirmam (vira regra)

1. **Partitura em 3 blocos (~50–52 s, ~110–120 palavras):** _(RESOLVIDO [t324–t326]: dimensionar o roteiro a ~2,3 palavras/s; o modelo pode esticar ou acelerar. Os ~3 palavras/s da §12 ficam SUPERADOS.)_ gancho 0–3 s, miolo com o porquê até ~45 s, fecho/CTA nos últimos ~5–8 s. O controle remoto ainda está num formato mais antigo (~60 s, blocos 10/15/20 s); os outros três já usam a partitura técnica. Padronizar a partitura.
2. **Gancho:** cena da mania já acontecendo + pergunta "por que…" sem resposta. Legenda curta e gritante (ACORDOU MOÍDO?, AMARELO = ACELERA?, TOMADA DERRETIDA!).
3. **Um mecanismo real no miolo**, nomeado em linguagem de rua (luz azul / melatonina, "cálculo quântico" do motorista, óxido nas molas + tapa, Efeito Joule). Termo técnico só com imagem no mesmo segundo.
4. **Personagem age:** dorme, acelera, tapa o controle, toma banho enquanto a tomada derrete. Não fica parado olhando.
5. ~~**Steering visual canônico (3 dos 4):** stickman 2D limpo, fundo cream...~~ **SUPERADO (t399/t400):** ver §16.
6. **Risco doméstico / trânsito (tomada e sinal amarelo):** satiriza a conta mental ou o hábito, e o fecho aponta a regra certa (conector cerâmico / não passar no amarelo), sem ensinar o atalho. Confirma a categoria 4.3 do contrato.
7. **Orgulho da gambiarra (controle):** o stickman ergue o controle com fita como troféu. Casa com "a gente é assim mesmo".

### CTA contextual — decisão encerrada (t467)
> **APROVADO:** a CTA segue o contexto do tema conforme §5. O trocadilho contextual é preferido quando natural; na ausência dele, usar convite natural a seguir. `Segue o Porquê BR` é fallback. Nunca pedir comentários (t263).

A decisão t467 substitui t262 (somente frase literal) e os exemplos t214 que pediam comentários. A classificação estrutural `tipo_cta` é validada pelo schema; a pertinência do trocadilho é revisão editorial, não inferência automática.

## 16. Linha editorial 80/20 (t399–t402). O visual desta seção foi substituído (t133u)
> O cartum genérico, a pausa das fichas e o bloco que pedia ilustração plana não são mais a regra. A identidade é stickman, seção 19. O texto antigo do bloco está no DECISOES-LOG (t429) e em `docs/pesquisas/estilo-2d-referencias.md`. Não copiar daqui para prompt.
1. **Vídeo:** o NotebookLM pesquisa, planeja, roteiriza e propõe temas. Não gera vídeo (t130u). Flow primeiro, Vids e Vibes na sequência do contrato de gasto.
2. **Bloco visual do roteiro:** o estilo vigente é o da seção 19 (`ESTILO_PADRAO_STICKMAN`). Uma frase-trava de stickman, repetida. Sem nome. Cena 1 = a imagem literal da expressão; a última retoma a primeira.
3. **Ambiente por cena:** lugar, época, 3 a 5 objetos-âncora, luz. Os objetos recorrentes têm ficha em `banco-fichas/`.
4. **Legenda e motion graphics (t145u, substitui t435):** a regra de legenda queimada do Short do NotebookLM é histórica. No vídeo da cadeia Flow/Vids/Vibes, o pós **pode** colocar motion graphics (REGRAS §26): gráfico sobre a cena, corte para gráfico em tela cheia no bloco do porquê, barra de progresso discreta, vídeo ou imagem dentro do gráfico. Máxima: ambiente limpo, por bom senso, sem cota. O texto na tela sai só do **bloco de números travados** do storyboard (ano, origem, números do roteiro e das fontes do NotebookLM); o Auditor confere tela × bloco, e divergência que muda o sentido reprova (§16.6). A imagem gerada continua sem texto escrito dentro do desenho (§19). Nunca pedir clique nem comentário.

5. **Linha editorial 80/20:** ≥ 80% origem de expressões brasileiras e curiosidades "inúteis" do cotidiano (ex.: "podre de rico", "o cão chupando manga"); ≤ 20% sazonal, só na janela do Caçador Sazonal (30 dias antes). Fora da janela, sem tendência. Etimologia disputada: "a versão mais aceita é… mas tem quem diga…"; ≥ 2 fontes. Gancho: a expressão em cena literal absurda + "Por que a gente fala isso?" até 3 s.
6. **Auditoria visual** (Auditor): enquanto a imagem da ficha não estiver aprovada, estilo e coerência do personagem dentro do vídeo seguem **métrica** (não reprovam, REGRAS §5), junto com legibilidade mobile e adequação cultural. **Reprovam** (segurança): semelhança com pessoa real/celebridade, marca/logo real, estereótipo ofensivo, texto na tela (imagem **ou legenda**) com erro que mude o sentido. **Erros aceitáveis (t435):** erro sem risco de segurança (ex.: legenda com palavra errada sem mudar o sentido, texto dentro da imagem sem erro) não reprova; o Auditor registra em `pqbr.erros_aceitaveis` para revisão (ROADMAP ERR-01).

### 16.7 Bloco visual de 12/10 — histórico
O bloco que começava com "Ilustração plana de cartum" deixou de ser o padrão em 27/10 (t133u). Não está reproduzido aqui para não ser copiado. O padrão vigente é a seção 19.

## 17. Tom editorial: cultura brasileira, ironia leve, nunca aula (José, 12/10/2026 17:13 e 17:17), regra
- **A essência é a cultura brasileira:** ditados, expressões, atitudes, gestos e comportamentos do brasileiro.
- **Sempre reforçar que o brasileiro usa a expressão hoje**, mesmo quando ela nasceu fora do Brasil: a origem estrangeira é curiosidade; o centro é como a gente fala e vive isso agora.
- **Comédia inteligente e leve, com palavras fáceis para todos os públicos.**
- **Ironia e sátira brasileiras, leves e brincalhonas**, da situação atual que a expressão descreve (o boleto, o mercado, a fila, o grupo da família), com exagero carinhoso. A origem histórica entra como a "fofoca" que explica a piada.
- **Nunca soar como aula nem instrução:** proibido "vamos aprender", "você sabia que", "saiba que", "o correto é", "dica:", imperativo didático, tom de professor ou de manual.
- **Ritmo de referência:** o teste de estilos B (12/10): narrador único, frases curtas, cada fala puxa a curiosidade da próxima.
- Continua valendo a §3: satiriza o comportamento e a situação, nunca a pessoa ou o grupo; satiriza, nunca incentiva.
- Aplicação: este tom vai no pacote canônico (este contrato), no prompt do roteiro (`criativo.TOM_EDITORIAL`) e no steering do vídeo (`notebooklm.TOM_NARRACAO`). O Auditor reprova roteiro com cara de aula.

## 17. Precedência visual e de geração de vídeo (t465)
> t133u e a seção 19 fecham o que aqui ainda estava em aberto: a identidade é stickman, e o 3D não se pede. O texto das fichas existe; a imagem, o catálogo e o resolvedor não. Isso não está concluído.
> NotebookLM continua o cérebro intelectual para pesquisa, temas, ideias, roteiro e SEO, mas sua geração antiga de vídeo fica desativada. Rota visual: Google Flow primeiro, Vids como fallback adicional, Gemini Web terceira rota e Meta Vibes posterior, conforme blueprint. Agentes Paperclip orquestram/validam, não substituem a autoria intelectual do NotebookLM. A regra de legenda do Short gerado no NotebookLM é histórica; a política de legendas/pós-produção do Flow precisa ser definida e testada separadamente no blueprint. Piloto sem publicação; preservar marca d'água/proveniência e direitos; não remover nem encobrir marcas do provedor. Instruções técnicas em inglês; roteiro, narração e conteúdo editorial em pt-BR.

## 18. Storyboard em série, personagem, cenário e elenco (t75u–t79u, 26/10/2026), regra central autorizada pelo José
1. **Antes de gerar qualquer imagem ou vídeo** é obrigatório ter: storyboard geral (norte do episódio, bloco de estilo, ficha do personagem) e uma **ficha por cena** numerada e rotulada (`<ep>_cNN`), com norte, início, fim, movimento, plano, prompt de imagem catalogado, prompt de animação e referências identificadas (`refs`: até 6 ids do catálogo visual, `PERS-`, `AMB-`, `OBJ-`, `ANIM-`, `FIG-` e `SIT-`; o `ASSET_*` ficou só no legado). Contrato: `contratos/storyboard.py` (Storyboard 1.3.0, t150u).
2. **Imagens revisadas antes do vídeo** (`imagens_revisadas`); sem revisão não há vídeo.
3. **Personagem engraçado, de caras e bocas (t78u, travado t133u).** É um stickman do cartoon 2D flat colorido do canal (§19), com expressão exagerada ligada à situação (espanto, nojo, desconfiança, alívio). A consistência vale para o corpo, a cabeça, o acessório e a cor de acento. Roupa nova a cada episódio fica pausada.
4. **Reagir sim, falar não.** O personagem nunca mexe os lábios como se narrasse: a narração é em off, nenhum prompt leva fala, aspas ou verbo de fala, e a animação usa "lips closed". Caras e bocas de reação (boca aberta de espanto, careta, beiço) são permitidas; articular palavras é proibido.
5. **Proibido cortar óculos ou cabeça** no enquadramento: plano nomeado, cabeça inteira com folga acima.
6. **Nada grotesco** (olho saltando, deformação corporal, gore), nem como metáfora visual de expressão.
7. **Encaixe no cenário (t78u).** Toda ficha define como o personagem está no cenário (`cenario_encaixe`). As roupas respeitam o ambiente temático, histórico e cultural:
   - **participa** do ambiente → caracterizado com roupas e traços da época ou do local (`figurino=epoca_local`);
   - **só observa** (ex.: espiando o passado, escondido, em terceira pessoa, enquanto outros personagens atuam) → usa o visual cotidiano travado da ficha (`figurino=atual_variavel`), não uma roupa inventada na cena.
8. **Visual cotidiano travado (t133u).** O campo `atual_variavel` permanece no contrato por compatibilidade, mas não autoriza roupa nova a cada episódio. O cotidiano é o da ficha do personagem (`PERS-*`), igual em todas as cenas e entre vídeos, até o José aprovar outra imagem. Dentro de um mesmo vídeo, não muda.
9. **Elenco alternado (t78u, protagonistas definidos em t150u).** Um protagonista masculino e uma feminina, alternando por episódio (número do código par = masculino, ímpar = feminino; exceção só com motivo em `elenco_excecao`). **O José definiu (t150u): masculino = `PERS-menino-azul` (nº 1 do catálogo), feminino = `PERS-menina-rosa` (nº 2).** Fichas em `config/estilo_visual.json` → `elenco` e em `banco-fichas/`. Sem nomes falados nem escritos (§16).
10. **Protagonista único, interação livre (t79u, t133u, t150u).** O protagonista do episódio fica constante. Quando o roteiro pedir, contracena com outro personagem do catálogo (`coadjuvante` + justificativa): o elenco é aberto e varia entre episódios, não é só o outro gênero. Todos são stickmen do mesmo traço. Sem nome no vídeo. Fichas: `banco-fichas/personagens/`.
11. **Motion com personagem presente (José, t150u).** No bloco do porquê em motion, um personagem do catálogo pode aparecer num quadro do layout (o "quadradinho"), explicando ou participando da explicação, no mesmo traço. É recorte da folha ou vídeo de situação (`SIT-*`), nunca texto gerado por IA. Regra de motion em REGRAS §26; contrato `PlanoMotion.personagem`.

## 19. Stickman único e fichas permanentes (José, 27–28/10/2026, t133u / t146u / t148u / t150u), regra
Fecha a identidade. Prevalece sobre o visual do §16, sobre o §16.7 antigo e sobre o que no §17 ainda dizia que a ficha estava só prometida.

1. **Só stickman no padrão definitivo do canal (t148u). Estilo, nas palavras do José (t150u): cartoon 2D, flat, colorido, com personagens stickman.** Cabeça redonda branca grande com contorno preto, **dois olhos pretos sempre visíveis** (proibido ciclope / um olho só), sobrancelhas expressivas, boca fechada ou de reação (`lips closed`), corpo e membros em traço preto fino, roupa chapada colorida fixa por personagem, cabelo preto simples quando houver, fundo claro em tom creme. Sem pessoa 3D e sem fotorrealismo. O padrão é o conjunto de 20 imagens que o José selecionou no Drive (`Fontes/Imagens`) e que está versionado em `banco-fichas/`; as fichas em nanquim de t146u foram descartadas a pedido dele (e a pasta `banco-fichas/referencias-canal/`, que guardava os frames antigos do canal, foi deletada em t149u).
2. **3D descartado.** Não se pede volume, fotorrealismo nem desenho 3D. Vídeo de teste 3D, se for localizado, vai para o Drive em `99_Arquivo/desenvolvimento-3d`, sem apagar o original. Em 27/10 essa pasta de teste não foi encontrada. Ver `docs/fases/stickman.md`.
3. **Regra canônica das fichas permanentes (t146u; conjunto trocado em t148u).** Para **personagens, objetos e locais permanentes** (`banco-fichas/`), as fichas são **permanentes** e o que faltar é gerado a partir do **modelo mais potente de geração de imagens (atualmente `🍌 Nano Banana Pro` no Google Flow, 0 créditos)**. O conjunto vigente é o entregue pelo José no Drive (`Fontes/Imagens`, t148u): catálogo do elenco com 12 personagens (`personagens/ELENCO-catalogo.png`), 6 folhas individuais multi-pose (`PERS-menina-rosa`, `PERS-cacheada`, `PERS-bone-verde`, `PERS-gravata-azul`, `PERS-roxo-ansioso`, `PERS-bob-oculos`), 11 ambientes (`ambientes/AMB-*.png`), catálogo de 12 objetos (`objetos/OBJ-catalogo.png`) e de 12 animais domésticos (`animais/ANIM-catalogo.png`). Índice: `banco-fichas/indice.json` 3.0.0 (t150u).
4. **Elenco permanente (t148u, t150u).** Catálogo de 13 personagens: os 12 numerados da grade (`ELENCO-catalogo.png`) e `PERS-bob-oculos` como nº 13 (o José o aceitou em t150u). 6 têm folha individual multi-pose: `PERS-menina-rosa` (nº 2), `PERS-cacheada` (nº 5), `PERS-bone-verde` (nº 8), `PERS-gravata-azul` (nº 9), `PERS-roxo-ansioso` (nº 12) e `PERS-bob-oculos` (nº 13); os demais usam o recorte `num-NN` da grade até ganhar folha. **Protagonistas (José, t150u): nº 1 = masculino (`PERS-menino-azul`), nº 2 = feminino (`PERS-menina-rosa`).** Sem nomes falados ou escritos; o número do catálogo não entra no vídeo. Nomes da bíblia de 08/10 não voltam; os IDs `PERS-M`, `PERS-F` e `PERS-M-classico` morreram com as fichas de t146u.
5. **Catálogo aberto e situações (José, t150u).** Tudo em `banco-fichas/` é referência e sugestão, não lista fechada. O agente pode inserir personagens (`PERS-`), figuras (`FIG-`, entes de apoio fora do elenco e dos animais), animais (`ANIM-`), objetos (`OBJ-`), ambientes (`AMB-`) e **situações** (`SIT-`, imagens e vídeos de personagens em poses e movimentos corriqueiros: acenar, pensar, digitar, correr), e deve variar o elenco. Mecanismo: `pipeline/banco_fichas.py` (buscar, registrar, anexar mídia, aprovar, descartar) sobre o contrato `FichaCatalogo` 1.0.0 (`contratos/catalogo_visual.py`). Regras: buscar antes de criar; ficha nova nasce `aguardando_ok_jose` (com mídia, já usável) ou `sugestao` (sem mídia); só o José aprova ou manda descartar, e ficha permanente só muda por ordem dele; o estilo é sempre cartoon 2D flat colorido com personagens stickman (3D, realismo, texto na imagem, pessoa real e nome são recusados); imagem nova fica no repositório até 2 MB, acima disso e todo vídeo vão para o Drive. O storyboard cita os ids em `refs` e o NotebookLM recebe a lista no item `catalogo_visual` do pacote.
6. **Estilo no código.** `ESTILO_PADRAO_STICKMAN` (`BlocoVisual` 3.0.0, texto do padrão t148u com a frase do José de t150u). O roteiro e o storyboard recebem esse texto. Pedido com 3D é recusado. O pacote do caderno ainda guarda o bloco no slot `bloco_visual_16_7`; o texto é este:

```
[ESTILO] Cartoon 2D flat colorido do canal Porquê BR (padrão definitivo t148u/t150u): personagens stickman de cabeça redonda branca grande com contorno preto, DOIS OLHOS pretos sempre visíveis, sobrancelhas e boca de reação, corpo e membros em traço preto fino, roupa chapada colorida fixa por personagem, cabelo preto simples quando houver. Fundo limpo e claro em tom creme, paleta suave, no máximo 3 a 5 objetos, humor de comédia leve. Personagem grande no quadro, cabeça inteira visível, agindo, expressão simples e exagerada. Proibido: um olho só (ciclope), pessoa realista, volume 3D, rosto de pessoa real ou celebridade, marca ou logo real, texto escrito dentro da imagem. Formato vertical 9:16, faixas de cima e de baixo livres.

[PERSONAGEM] Um stickman, a frase-trava da ficha do protagonista do episódio (PERS-menino-azul ou PERS-menina-rosa) e, se o roteiro pedir, de um coadjuvante do catálogo, sem nome. A mesma cabeça e o mesmo traço em todas as cenas. Dois olhos visíveis, boca de reação, sem fala.

[AMBIENTE] Cena <n>: <lugar da ficha permanente AMB-* ou novo>, <época: hoje / passado>, objetos-âncora: <3 a 5, do OBJ-catalogo quando recorrente>, luz <hora>.

[CENAS]
1. Fala: "<frase>" → Ação: o stickman vive a situação → Plano: <plano_geral / plano_medio / plano_medio_curto / close>.
N. Fala: "<frase final>" → Ação: retoma a imagem da cena 1 → Plano: o mesmo da cena 1.
```
7. **Drive.** Ferramenta da mesma conta Google, já em uso. Estrutura `PQBR/` na REGRAS §21. O banco espelha em `00_Biblia_Visual/banco-fichas` (espelho com o conjunto de t146u; atualização para o conjunto t148u e o catálogo 3.0.0 de t150u pendente — P17). Vídeo de situação e imagem acima de 2 MB ficam no Drive, com o id na ficha. Isso não cria o catálogo no banco do app.
8. **Agente do Google Flow + Fichas Permanentes + Storyboard na produção (t141u, atualizado em t146u e t150u).** O NotebookLM continua no roteiro, na compliance, no SEO e no JSON do storyboard (`S01..S0N`). No Google Flow, as **fichas permanentes** (`PERS-*`, `AMB-*`, `OBJ-*`, e as novas do catálogo aberto) e os quadros iniciais (`start frames`) usam **`🍌 Nano Banana Pro`** (0 créditos), com o **Agente do Flow** configurado com `Instruções para o agente` fixas no estilo do canal e `Confirmar antes de gerar = Sempre`. Na produção de cada cena `S01..S0N`, anexam-se as fichas permanentes do conjunto t148u (o recorte individual do personagem, gerado a partir da folha `PERS-*-folha.png`, + `AMB-*.png` + `OBJ-catalogo.png` conforme a cena) como `Elemento` (`Adicionar elementos à caixa de comando`), gera-se o frame de início em `Nano Banana Pro` e anima-se **1 clipe contínuo por cena** (`Single continuous shot, no cuts, lips closed`). A folha multi-pose (`*-folha.png`) serve para validação e referência de expressões, nunca como imagem única para animar vídeo. As `Instruções para o agente` gravadas no projeto ainda descrevem o traço de t146u e serão regravadas com o estilo t148u antes da produção (P17). Não entram Claude como autor, Vsub, CapCut nem várias contas Gmail.

