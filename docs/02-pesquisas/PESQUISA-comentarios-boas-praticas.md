# Pesquisa: boas práticas para ler, classificar e agir sobre comentários (PQBR)

Data: 08/10/2026 (~23:00 PT). Pesquisa feita só na web (docs oficiais, papers, Reddit/HN via resultados de busca, GitHub). Nada foi alterado em host remoto, nenhum segredo foi lido e o YouTube Studio não foi acessado.

Legenda:
- **VERIFICADO**: li na documentação oficial ou no paper citado.
- **HIPÓTESE**: opinião da comunidade, blog de ferramenta, ou inferência nossa ainda não testada.
- **ESTIMATIVA**: conta nossa, a confirmar no piloto.

Contexto que muda tudo: a base hoje é pequena, de **0 a 3 comentários por vídeo** (contrato editorial, seção de métricas). O sistema tem que ser correto e barato, não "de escala".

---

## 1. Fontes

### 1.1 Oficiais (YouTube / Google)
| # | Fonte | O que importa para nós | Marca |
|---|---|---|---|
| Y1 | [commentThreads.list](https://developers.google.com/youtube/v3/docs/commentThreads/list) | Custa **1 unidade** por chamada; `maxResults` 1–100 (padrão 20); filtros `videoId` **ou** `allThreadsRelatedToChannelId`; `moderationStatus` = `published` (padrão), `heldForReview`, `likelySpam` (só com OAuth do dono); `order` = `time` (padrão) ou `relevance`; `pageToken`; `searchTerms`; `textFormat` = `html` (padrão) ou `plainText`. Erro 403 `commentsDisabled`. | VERIFICADO |
| Y2 | [commentThreads (recurso)](https://developers.google.com/youtube/v3/docs/commentThreads) | `replies` traz **só parte** das respostas; para todas, `comments.list` com `parentId`. Tem `totalReplyCount` e `isPublic`. | VERIFICADO |
| Y3 | [comments (recurso)](https://developers.google.com/youtube/v3/docs/comments) | Campos: `authorDisplayName`, `authorChannelId`, `textDisplay`, `textOriginal` (só volta para o autor do comentário), `parentId`, `likeCount`, `moderationStatus` (só para o dono), `publishedAt`, `updatedAt`, `imageUrl` (link assinado, expira em 6 h). `textDisplay` pode diferir do original (ex.: troca link de vídeo pelo título). **`markAsSpam` não é mais suportado.** | VERIFICADO |
| Y4 | [comments.setModerationStatus](https://developers.google.com/youtube/v3/docs/comments/setModerationStatus) | **50 unidades**; até 50 IDs; escopo `youtube.force-ssl`; valores `heldForReview`, `published`, `rejected`. **Um comentário `rejected` não pode voltar a `published`**; `rejected` também esconde as respostas. `banAuthor=true` só junto com `rejected`. Para remover comentário de terceiro o caminho é `rejected` (o `comments.delete` só vale para o autor). | VERIFICADO |
| Y5 | [Calculadora de cota](https://developers.google.com/youtube/v3/determine_quota_cost) | 10.000 unidades/dia (reset à meia-noite do Pacífico, ~04:00/05:00 PT-Fortaleza); toda chamada, mesmo inválida, custa ≥ 1; `comments.insert` 50, `videos.update` 50, `commentThreads.insert` 50; `search.list` e `videos.insert` têm balde próprio de 100/dia. | VERIFICADO |
| Y6 | [Políticas de desenvolvedor da API](https://developers.google.com/youtube/terms/developer-policies) (atualizada 14/09/2026) | (a) **não automatizar comentários, likes etc. sem consentimento prévio, específico e expresso** do usuário (III.I.2); (b) **não mudar visibilidade de conteúdo sem instrução expressa** do dono (III.E.3.f); (c) dado autorizado (como comentários) pode ficar guardado **no máximo 30 dias**, depois apagar ou atualizar (III.E.4.c); (d) **proibido raspar (scraping)** as aplicações do YouTube e usar outra tecnologia que não a API para obter dados da API (III.E.6 e III.I.14); (e) pedir só os escopos usados (III.D.2.a.ii); (f) não guardar dado de usuário indefinidamente. | VERIFICADO |
| Y7 | [Configurações de comentários (Ajuda)](https://support.google.com/youtube/answer/9483359?hl=en) | Moderação por vídeo: Nenhuma / **Básica** (retém spam, autopromoção, texto sem sentido, potencialmente impróprio) / **Rigorosa** / Reter todos; retidos ficam **até 60 dias** no Studio; **palavras bloqueadas**, **reter comentários com links**, **ocultar usuário** (some de todos os vídeos) e **usuários aprovados** valem para o canal inteiro; dá para **pausar** comentários num vídeo. O próprio YouTube avisa que o filtro "nem sempre acerta". | VERIFICADO |
| Y8 | [Política de spam](https://support.google.com/youtube/answer/2801973?hl=en) | Proíbe spam de comentários repetitivos/enganosos, golpes ("suporte falso", investimento), engajamento artificial por bots, e **produção em massa automatizada/sintética repetitiva** (vale para o canal como um todo). | VERIFICADO |
| Y9 | [Sugestões de resposta](https://support.google.com/youtube/answer/10357396) e [Ask Studio](https://support.google.com/youtube/answer/16291691?hl=en) | O Studio já sugere respostas com IA e o Ask Studio resume comentários e propõe ideias; a aba Inspiração está sendo descontinuada desde ago/2026. Lido só pelo resumo da busca. | VERIFICADO (parcial) |

### 1.2 Segurança de LLM e moderação (indústria)
| # | Fonte | O que importa | Marca |
|---|---|---|---|
| S1 | [OWASP LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | Injeção **indireta** vem de conteúdo externo (comentário é exatamente isso). Mitigações: restringir o papel do modelo; **formato de saída definido e validado por código determinístico**; filtros de entrada/saída; **menor privilégio** (as ações ficam no código, não no modelo); **humano aprova ação de alto risco**; **separar e marcar o conteúdo não confiável**; testes adversariais. Ataques citados: instrução escondida, payload dividido, **multilíngue/ofuscado (Base64, emoji)**. | VERIFICADO |
| S2 | [Anthropic: guia de moderação de conteúdo](https://docs.anthropic.com/en/docs/about-claude/use-case-guides/content-moderation) | Montar **exemplos permitidos e proibidos com casos de borda antes** de escrever o prompt; **categorias com definição**; resposta só em JSON; **níveis de risco** (bloquear só o alto, revisar o médio); medir **precisão e recall**; acompanhar tendência do que é marcado; **lote** para reduzir custo quando não precisa ser em tempo real; cuidado com metáfora ("killed it"). | VERIFICADO |
| S3 | [OpenAI: Moderation guide](https://developers.openai.com/api/docs/guides/moderation) e [cookbook de moderação](https://developers.openai.com/cookbook/examples/how_to_use_moderation) | "Trate os scores como **sinais** da sua política, **não como bloqueio automático**." Limiar se escolhe com **conjunto de avaliação e matriz de confusão**. | VERIFICADO |
| S4 | [OpenAI: Guardrails e revisão humana](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals) | Pausar antes de efeito colateral (edição, cancelamento); **validação ao lado da ferramenta que causa o efeito**, não só no agente. | VERIFICADO |
| S5 | [Xiong et al., ICLR 2024: "Can LLMs Express Their Uncertainty?"](https://arxiv.org/abs/2306.13063) | A confiança **verbalizada** pelo LLM é **excessiva**, concentrada em **80–100%**; **amostrar várias respostas e medir consistência** prevê erro melhor. | VERIFICADO (resumo do paper) |
| S6 | [Perspective API (Jigsaw)](https://www.perspectiveapi.com/faq/) | **Encerra em 31/12/2026**; sem novos pedidos desde fev/2026; sem migração. **Não adotar.** | VERIFICADO |
| S7 | [Unit 42: injeção indireta observada na prática](https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/), [Trend Micro: injeção invisível](https://www.trendmicro.com/en_us/research/25/a/invisible-prompt-injection-secure-ai.html) | Texto invisível (Unicode tag/zero-width) e instruções escondidas já são usados contra agentes. | VERIFICADO (resumo) |

### 1.3 Golpes, coordenação e pt-BR (pesquisa)
| # | Fonte | O que importa | Marca |
|---|---|---|---|
| G1 | [NDSS 2024 "Like, Comment, Get Scammed"](https://like-comment-get-scammed.github.io/paper/ndss24-like-comment-get-scammed.pdf) | **208 mil** comentários-golpe em 6 meses; 76% cripto, 22% prêmio falso; levam para **WhatsApp/Telegram**; **imitam o dono do canal** (nome e foto); usam **símbolos Unicode parecidos** para fugir de filtro de palavra; **dividem o contato em várias respostas/contas**. | VERIFICADO |
| G2 | [RANLP 2023: golpes em conluio](https://aclanthology.org/2023.ranlp-1.114.pdf) | Fios falsos de "depoimento" com várias contas; contato fatiado em respostas. | VERIFICADO |
| G3 | [EU DisinfoLab: árvore de detecção de CIB](https://www.disinfo.eu/wp-content/uploads/2024/08/20240805-CIB-detection-tree.pdf), [IFTAS: brigading](https://about.iftas.org/library/brigading/) | Coordenação se detecta por **sinais correlacionados** (tempo sincronizado, texto quase igual, perfis parecidos, contas novas). Texto parecido é **indício, não prova**; preservar revisão humana. | VERIFICADO (resumo) |
| G4 | [IDPT 2021 (ironia em pt)](https://ceur-ws.org/Vol-2943/idpt_paper6.pdf), [Sotaques Digitais (benchmark pt-BR)](https://github.com/ramondomiingos/ptbr-irony-idioms-regionalism-benchmark) | Ironia em pt-BR é tarefa à parte e difícil; existe benchmark com 30 casos de ironia + idiomatismos + regionalismos (inclui Nordeste) para testar LLMs. | VERIFICADO |

### 1.4 Comunidade e repositórios
| # | Fonte | O que diz | Marca |
|---|---|---|---|
| C1 | [r/NewTubers: responder comentários?](https://www.reddit.com/r/NewTubers/comments/1qg7fxu/replying_to_comments_good_or_bad/), [r/NewTubers: responder todos no Short?](https://www.reddit.com/r/NewTubers/comments/1jqudvv/should_you_really_respond_to_every_comment_on/) | Responder cria vínculo; não precisa responder tudo; **não dar coração em tudo** (perde valor); fixar um bom comentário; responder perguntas comuns. | HIPÓTESE |
| C2 | [r/NewTubers: resposta automática com IA](https://www.reddit.com/r/NewTubers/comments/1gdz4fa/thoughts_on_youtubes_ai_auto_response_for_comments/), [r/PartneredYoutube: usam as respostas de IA?](https://www.reddit.com/r/PartneredYoutube/comments/1uq97rz/do_you_use_the_ai_generated_comment_replies/) | Público percebe resposta genérica/repetida; IA serve para **priorizar e rascunhar**, humano revisa; crítica e assunto delicado ficam com humano. (Lido pelo resumo da busca; o Reddit bloqueou a leitura direta.) | HIPÓTESE |
| C3 | Blogs de ferramentas ([commentshark](https://www.commentshark.com/blog/youtube-shorts-comments-management), [ytshark](https://ytshark.com/youtube-shorts-engagement/), [growvib](https://growvib.com/blog/youtube-comments-algorithm-what-counts)) | No Short o engajamento **decai rápido** (primeiras horas); fixar uma pergunta do criador; triagem por classe. O número "50+ respostas em 2 h = 15–20% mais alcance" é **alegação de marketing sem método**. | HIPÓTESE |
| C4 | [ThioJoe/YT-Spammer-Purge](https://github.com/ThioJoe/YT-Spammer-Purge) | Ferramenta de referência contra golpes: filtros por **caracteres não-ASCII no nome**, regex, ID do canal; mostra amostras para **achar falso positivo antes** de agir; tem **modo de recuperação**; recomenda **"modo moderador"** com conta separada que só consegue reter para revisão (menor privilégio). | VERIFICADO (README) |
| C5 | [benmfzen/meta-youtube-comment-mcp](https://github.com/benmfzen/meta-youtube-comment-mcp) | Pipeline real: coleta → classifica (LLM em lote) → triagem auto/revisão/ignorar; **só elogio com confiança alta e "zero superfície factual" pode ser automático**; resto vai para humano; **"sem ✅ na fila, sem efeito colateral"**; registro de lições. | VERIFICADO (README) |
| C6 | [HN: detecção de texto por LLM](https://news.ycombinator.com/item?id=47943714) | Moderadores do HN: certeza é impossível; falso positivo é inevitável; usar como **fila de revisão, não veredito**. | HIPÓTESE |

---

## 2. Boas práticas (síntese)

1. **Comentário é dado, nunca instrução**: delimitar o texto, normalizar, e o modelo não ter ferramenta nenhuma (S1, S4).
2. **Código antes do LLM**: normalizar Unicode (NFKC + tabela de "confusables" + remover caracteres invisíveis), regex de link/telefone/@/Telegram/WhatsApp/PIX/e-mail/CPF, lista de bloqueio, detecção de quase-duplicata (G1, C4).
3. **Usar o sinal do próprio YouTube**: ler também `heldForReview` e `likelySpam` (Y1). O filtro do YouTube já retém parte dos golpes, mas uma **reclamação legítima também pode ficar retida** e não aparece na leitura padrão.
4. **Taxonomia fechada, com definição e exemplos de borda**; saída em JSON validada; níveis de risco em vez de sim/não único (S2).
5. **Não confiar na "confiança" que o modelo declara** (S5). Usar **2 rodadas e concordância**, como já fazemos no auditor; divergência → humano.
6. **Ação automática exige alta precisão; detecção do grave exige alto recall** (S3). Por isso a ação automática deve ser **reversível**.
7. **Contar pessoas, não comentários**: autores distintos (`authorChannelId`), sem contar o próprio canal, sem contar texto quase igual de contas diferentes como votos separados (G3).
8. **Conjunto de avaliação + matriz de confusão** antes de ligar qualquer ação automática; reavaliar quando mudar prompt, modelo ou fallback (S2, S3).
9. **Menor privilégio**: escopo de leitura separado do de escrita; ações de moderação irreversíveis (`rejected`, `banAuthor`) só com humano (Y4, Y6, C4).
10. **Retenção curta**: comentário bruto no máximo 30 dias ou atualizado (Y6); guardar só rótulo e agregados anonimizados.
11. **Respostas**: IA prioriza e rascunha; humano decide; nada de resposta genérica repetida (C1, C2, C5, Y6 III.I.2).
12. **Primeiras horas valem mais** para conversa no Short (C3, HIPÓTESE), e é quando a nossa leitura é mais frequente.

## 3. Oportunidades

1. **Reter (não apagar) golpe e dado pessoal**: `setModerationStatus=heldForReview` é **reversível** e custa 50 unidades (Y4). Protege o público sem a irreversibilidade do `rejected`.
2. **Configuração de uma vez no Studio, feita por José**: moderação **Básica** (ou Rigorosa), **reter comentários com link**, palavras bloqueadas típicas de golpe (`telegram`, `whatsapp`, `wa.me`, `t.me`, "ganhou", "prêmio", "suporte"), e a variante do nome do canal. Custo zero e reduz o trabalho do classificador (Y7, G1). Não achamos endpoint da API para palavras bloqueadas (HIPÓTESE: não existe).
3. **Leitura por canal inteiro**: `allThreadsRelatedToChannelId` + `order=time` + `maxResults=100`, parando quando chega no último comentário já visto. **Uma chamada cobre todos os vídeos** (HIPÓTESE a testar: que inclua comentários de todos os vídeos do canal, inclusive Shorts).
4. **Respostas ao CTA viram pauta**: o roteiro já termina com "e aí na sua casa, quem faz isso?". As respostas são relatos de manias brasileiras = matéria-prima para a grade de temas, contadas por **autores distintos e vídeos distintos** (mesma lógica já aprovada para a grade).
5. **Perguntas repetidas → comentário fixado** proposto pelo agente e aprovado por José com um toque (já previsto no item 5).
6. **Telegram com resumo curto nas primeiras horas**: com 0–3 comentários por vídeo, José consegue responder à mão, no tom do canal, que é o que a comunidade recomenda (C1, C2).
7. **Lições automáticas**: cada decisão de José no Telegram (confirma / descarta) vira rótulo para o conjunto de avaliação (C5 "lessons ledger"; item 5 "todo caso vira aprendizado").

## 4. Cuidados e riscos

1. **Brigada e trote derrubando vídeo**: com a regra "≥ 2 pessoas → privado", duas contas descartáveis bastam. Mitigar com contagem de autores distintos qualificados (ver 6.3) e exigência de reclamação **específica** (o que está errado), não só "vídeo ruim".
2. **Alvo errado**: um comentário **com** dado pessoal ou ofensivo **não significa** que o vídeo tem problema. A ação certa é reter o comentário, não tornar o vídeo privado. Só alegação **sobre o vídeo** ("o vídeo mostra meu número", "usaram meu personagem") conta para o item 5.
3. **Ironia pt-BR**: "kkkk que aula de física errada" pode ser elogio. A ironia é difícil até para modelo treinado (G4). Na dúvida, José decide.
4. **Golpes que fogem de palavra-chave**: Unicode parecido, contato fatiado em várias respostas, imitação do nome/foto do canal (G1, G2). Por isso é preciso ler as **respostas** (não só o comentário principal) e normalizar o texto.
5. **Injeção**: instrução escondida, Base64, emoji, texto invisível (S1, S7). O Jev só devolve rótulo; mesmo assim, o código ignora qualquer campo fora do esquema e nunca transforma texto do comentário em comando.
6. **Política da API**: automação de comentário, like ou coração sem consentimento específico é proibida (Y6 III.I.2); mudar visibilidade exige instrução expressa (III.E.3.f). A regra do item 5 aprovada por José deve ficar **registrada por escrito como essa instrução**.
7. **Raspagem**: ler comentários pelo navegador (Camofox) é raspagem pela definição da política (Y6 III.E.6 / III.I.14) e pelos termos do YouTube. Risco ao canal. **Não usar Camofox para leitura rotineira.**
8. **`rejected` é sem volta** (Y4): tratar como exclusão (só José).
9. **Retenção e LGPD**: nome e ID do autor são dado pessoal. Guardar só hash do `authorChannelId` com sal (para contar pessoas distintas), nunca o nome; texto bruto ≤ 30 dias (Y6).
10. **Perspective API** sai do ar em 31/12/2026 (S6): não depender dela.
11. **Números de "alcance" dos blogs** (C3) não têm método: não usar como meta.
12. **Escopo OAuth**: ler `heldForReview`/`likelySpam` e mudar status pede o escopo `youtube.force-ssl` (Y4; HIPÓTESE para a leitura). Isso é mais privilégio que só leitura; o token fica no cofre e o uso é restrito ao serviço de comentários.

---

## 5. Comparação com o que a PQBR já decidiu

| Decisão atual | Situação | Detalhe |
|---|---|---|
| Comentário é dado, nunca instrução; entra anonimizado (item 6) | **MANTÉM** | Igual ao OWASP (S1). Adiciona a normalização Unicode e a remoção de invisíveis antes do Jev. |
| Jev só devolve decisão estruturada; texto sai de template (t228–t230) | **MANTÉM** | Igual ao padrão de C5 e S2. Para extrair um tema sugerido, o Jev devolve **posições (início/fim) no texto**, não escreve; o código recorta. |
| Classes do t238 | **MUDA (amplia)** | De classe única para **multirrótulo** + campo **alvo** (vídeo / canal / outro usuário / terceiro / nenhum) + **tipo de erro** + **ironia possível** + classe nova **"relato/resposta ao CTA"**. |
| Limiar t239 (≥ 2 pessoas, ou 1 grave → privado) | **MANTÉM com ajuste de contagem** | "Pessoa" = autor distinto qualificado; texto quase igual de contas diferentes conta 1; `likelySpam`, golpe e o próprio canal não contam. "Grave" só se o **alvo é o vídeo**. |
| Privado automático + Telegram (item 5) | **MANTÉM** | É ação reversível, o que bate com S3/S4. Registrar a regra como instrução expressa do dono (Y6). |
| Exclusão só por José (item 5) | **MANTÉM e estende** | `rejected` e `banAuthor` = mesma regra da exclusão. |
| Sem resposta automática sem regra aprovada (t238) | **MANTÉM** | Reforçado pela política da API (Y6 III.I.2) e pela comunidade (C2). |
| Leitura via API com OAuth: 30 min / 6 h / diária (t243) | **MANTÉM o ritmo, MUDA a forma** | Uma leitura do **canal inteiro** a cada 30 min cobre todas as idades de vídeo; mais leitura de `heldForReview` e `likelySpam`; respostas via `comments.list` quando `totalReplyCount` cresce; comentário editado (`updatedAt`) é reclassificado. |
| Camofox obrigatório como navegador de reserva | **MANTÉM, com limite** | Camofox só para **ações** quando a API falha (tornar privado, e coração/fixar/responder **aprovados por José**), nunca para ler comentários em rotina. |
| Fallback Jev → OpenRouter → OpenAI, mesmo esquema Pydantic | **MANTÉM e ADICIONA** | Ao trocar de provedor, rodar o conjunto de avaliação antes de permitir ação automática com o novo modelo; até lá, o novo modelo só alerta José. |
| Escada de falhas / buffer local (t241–t242) | **MANTÉM** | Cota estourada (`quotaExceeded`) = espera o reset, sem nova tentativa. |
| Sem PII em logs (item 6) | **MANTÉM e ADICIONA** | Hash do autor com sal; texto bruto expira em 30 dias (Y6); o resumo no Telegram mostra o texto do comentário só para José. |
| — | **ADICIONA** | Reter (`heldForReview`) golpe/dado pessoal/ofensa a terceiros (pergunta 1). Configuração única do Studio por José. Conjunto de avaliação pt-BR. Detecção de imitação do canal. |

---

## 6. Proposta concreta

### 6.1 Caminho API (normal)

**Leitura (código)**
1. A cada 30 min: `commentThreads.list(part=snippet,replies, allThreadsRelatedToChannelId=<canal>, order=time, maxResults=100, textFormat=plainText)`, paginando só até o último ID já visto.
   - Se a HIPÓTESE do canal inteiro falhar no teste: volta ao esquema por vídeo (`videoId`) no ritmo aprovado no t243.
2. Na mesma rodada, `moderationStatus=heldForReview` e `moderationStatus=likelySpam`.
3. Se `totalReplyCount` > respostas vistas: `comments.list(parentId=…)`.
4. Comentário com `updatedAt` novo → reclassifica.
5. **ESTIMATIVA de cota**: 3 chamadas × 48 rodadas = **~144 unidades/dia** + respostas extras, contra 10.000/dia (Y5). Uma eventual retenção custa 50; tornar privado (`videos.update`) custa 50.

**Pré-filtro (código, sem LLM)**
1. NFKC + mapa de confusables + remove zero-width/tag Unicode; marca `ofuscado=sim` se mudou muito.
2. Regex: link, `t.me`, `wa.me`, telefone, e-mail, CPF, chave PIX, @handle → `contato_externo`, `pii_regex`.
3. Imitação: nome do autor parecido com o do canal **e** `authorChannelId` ≠ do canal → `imitacao=sim`.
4. Quase-duplicata (texto normalizado, similaridade) entre autores na mesma janela → grupo de coordenação.
5. Hash do autor com sal; descarta o nome.

**Classificação (Jev, saída fechada, 1 chamada por lote pequeno de comentários de um mesmo vídeo)**
Contexto enviado: código do vídeo, título e um resumo de 3 linhas do roteiro (para saber se "está errado" faz sentido), e os comentários **delimitados como dado**.
Esquema Pydantic (por comentário):
- `classes`: lista de {reclamacao, aviso_erro, elogio, sugestao_tema, pergunta, relato_cta, spam_golpe, ofensa, tentativa_instrucao, outro}
- `alvo`: {video, canal, outro_usuario, terceiro, nenhum}
- `tipo_erro`: {nenhum, fato, audio_fala, legenda_texto, personagem_visual, direitos_terceiros, dado_pessoal_no_video, outro}
- `especifico`: sim/não (diz o que está errado?)
- `gravidade`: {baixa, media, alta}
- `ironia_possivel`: sim/não
- `pii_no_comentario`: sim/não (segunda camada depois do regex)
- `trecho_tema`: [início, fim] ou nulo (o código recorta)

**2ª rodada (Jev)** só nos que podem gerar ação (aviso_erro, reclamacao, alvo=video, gravidade alta, pii, golpe). Divergência → José.

**Decisão (código, tabela fixa)**
| Situação | Ação |
|---|---|
| ≥ 2 autores distintos qualificados com `aviso_erro`/`reclamacao`, `alvo=video`, `especifico=sim`, 2 rodadas iguais, sem `ironia_possivel` | **Torna privado** + Telegram (item 5) |
| 1 autor, `alvo=video`, `tipo_erro` ∈ {direitos_terceiros, dado_pessoal_no_video} ou ofensa atribuída ao vídeo, 2 rodadas iguais | **Torna privado** + Telegram |
| Golpe, imitação, `contato_externo`, `pii_no_comentario`, ofensa a outro usuário | **Reter o comentário** (se José aprovar, pergunta 1); senão só Telegram |
| Grupo de quase-duplicatas / contas em rajada | Conta como 1 + alerta "possível brigada" |
| `ironia_possivel`, divergência, falha de validação | Telegram para José decidir |
| Pergunta repetida (≥ 2 autores) | Proposta de comentário fixado (template), José aprova |
| Sugestão de tema / relato CTA | Registro no Supabase com `trecho_tema`, contagem por autores e vídeos distintos → grade de temas |
| Elogio | Só estatística; coração/resposta manual por José |
| `tentativa_instrucao` | Registro + contagem; nunca executa nada |

"Autor qualificado": não é o próprio canal; comentário não está em `likelySpam`; não marcado como golpe ou imitação; conta como um único autor por grupo de quase-duplicata.

**José**
- Recebe no Telegram: alertas (na hora) e um resumo por vídeo nas primeiras horas (template: código, contagem por classe, comentários que merecem resposta, com link).
- Responde, dá coração e fixa **à mão** (ou aprova uma ação do agente com um toque).
- Exclui, rejeita ou bane: só ele.
- Cada decisão dele vira rótulo do conjunto de avaliação.

**Avaliação (antes de ligar ação automática)**
- Conjunto pt-BR: comentários dos nossos vídeos e dos ~300/dia da grade de temas (já aprovados como fonte), mais casos sintéticos de borda (ironia, golpe com Unicode, injeção, PII), e os 30 casos de ironia do benchmark Sotaques Digitais (G4).
- Medir precisão e recall por classe; a ação automática só liga quando a precisão de "torna privado" no conjunto ficar alta o bastante para José aceitar (sem número inventado; José define depois de ver a matriz).
- Reavaliar ao trocar modelo, prompt ou provedor de fallback.

**Retenção**
- Texto bruto: ≤ 30 dias (Y6). Depois, apaga e fica só o rótulo + agregados.
- Autor: só hash com sal.

### 6.2 Caminho Camofox (reserva, ritmo humano)

| Situação | O que o Camofox faz | O que NÃO faz |
|---|---|---|
| API falhou ao **tornar privado** (escada de falhas esgotada) | O agente do Studio torna o vídeo privado pela interface, no ritmo humano, e confirma por leitura da tela | Não insiste além da escada; avisa José |
| José aprovou coração / fixar / responder (texto de template ou dele) | Executa a ação aprovada, uma por vez, com pausas | Nunca age sem o toque de José; nunca em lote |
| API de leitura fora por > 2 h (ESTIMATIVA de prazo, a definir) | **Não lê comentários.** Telegram para José: "leitura parada", com link para ele olhar no celular | Não raspa comentários (Y6) |
| Configuração de moderação do canal | Nada; José faz uma vez no Studio | — |

Jev no Camofox: só perguntas fechadas sobre o texto da tela (ex.: "o status mostrado é Privado? sim/não"), como já aprovado.

### 6.3 Quem faz o quê

| Parte | Jev | Código | José |
|---|---|---|---|
| Ler comentários | — | API, paginação, dedupe | — |
| Limpar/normalizar, regex, hash | — | sim | — |
| Classificar | sim (JSON fechado, 2 rodadas no que gera ação) | valida esquema | — |
| Contar autores distintos, brigada | — | sim | — |
| Tornar vídeo privado | — | sim (API; Camofox na falha) | é avisado |
| Reter comentário | — | sim, se aprovado | aprova a regra |
| Rejeitar, banir, excluir | — | — | **só ele** |
| Responder, coração, fixar | — | executa o aprovado | decide e escreve/aprova |
| Resumo e alertas | — | template | lê |
| Temas e perguntas | marca o trecho | recorta, conta, envia à grade | aprova o fixado |

---

## 7. Perguntas para José (máx. 3)

1. **Reter comentários automaticamente?** Golpe, contato externo, imitação do canal, dado pessoal no comentário e ofensa a outro usuário: o agente pode colocá-los em "retido para revisão" sozinho? É reversível e custa 50 unidades. Ou só avisa no Telegram?
2. **Falso positivo de privado**: se você conferir e o vídeo estiver certo, ele pode voltar a público com um toque seu, sem contar como "republicação" (item 5)?
3. **Configuração única no Studio, feita por você**: moderação **Básica** ou **Rigorosa**, reter comentários com link, e a lista inicial de palavras bloqueadas (telegram, whatsapp, t.me, wa.me, "ganhou", "prêmio", variações do nome do canal). Faz você mesmo? E as respostas aos comentários ficam com você, pelo resumo do Telegram nas primeiras horas?

---

## 8. Respostas e reações automáticas (pedido do José, 08/10 ~23:02 PT)

Pedido: responder e reagir automaticamente a TODOS os comentários não críticos (elogio, comentário comum: agradecer por assistir/feedback), com variação para não parecer robô, no ritmo de leitura aprovado; só o crítico vai para o José. Restrições: o Jev não escreve texto (a variação vem de um banco de templates escolhido por código); sem API, a única via é o Camofox (há risco conhecido de queda de sessão no Studio); custo mínimo.

### 8.1 Fontes novas
| # | Fonte | O que importa | Marca |
|---|---|---|---|
| R1 | [comments.insert](https://developers.google.com/youtube/v3/docs/comments/insert) | Responde a um comentário existente (`snippet.parentId` + `snippet.textOriginal`); escopo `youtube.force-ssl`; **50 unidades** por chamada (a mesma página fala em "2 unidades" para o `part=snippet`; a calculadora oficial Y5 diz 50, então usamos 50). Erros: `parentCommentIsPrivate`, `operationNotSupported` (se `canReply` for falso), `commentTextTooLong`. | VERIFICADO |
| R2 | [Guia de implementação de comentários](https://developers.google.com/youtube/v3/guides/implementation/comments) e recurso `comments` (Y3) | Métodos: list, insert, update, delete, setModerationStatus. **Não há método para dar like nem coração em comentário**; `viewerRating`/`canRate` só servem para leitura. `allThreadsRelatedToChannelId` pode trazer comentários "do canal ou de qualquer vídeo do canal" (reforça a hipótese 3 da seção 3). | VERIFICADO (sem endpoint) |
| R3 | [Stack Overflow: dar coração via API?](https://stackoverflow.com/questions/75953822/can-you-heart-a-youtube-comment-via-youtube-api-data-v3) e [like em comentário](https://stackoverflow.com/questions/79670745/) | Confirma, pela comunidade, que não existe endpoint de coração/like em comentário. | HIPÓTESE (coerente com R2) |
| R4 | Políticas da API (Y6) | III.I.2: **proibido automatizar comentários sem consentimento prévio, específico e expresso** do usuário; III.E.3.d: o usuário deve consentir expressamente nas ações de inserção; III.I.11: não enganar nem fazer spam. Então resposta automática no **próprio canal** é permitida com o consentimento do dono, desde que não seja spam. | VERIFICADO (texto) / HIPÓTESE (que uma regra permanente aprovada pelo José satisfaz o "específico e expresso") |
| R5 | Política de spam (Y8) | Proíbe "comentários em alto volume, repetitivos ou enganosos" e engajamento artificial por bots. Resposta idêntica em massa é o risco. | VERIFICADO |
| R6 | [r/SmallYTChannel: respostas automáticas](https://www.reddit.com/r/SmallYTChannel/comments/1ir0qv5/automated_comment_responses/) | Um criador relata **canal excluído** por usar automação parecida com resposta automática, recuperado depois de apelação. Relato único, sem detalhes da ferramenta. | HIPÓTESE |
| R7 | [r/youtube: "shadow ban" de respostas](https://www.reddit.com/r/youtube/comments/1e6jc56/i_figured_out_the_shadow_ban/), [r/youtube: respostas somem](https://www.reddit.com/r/youtube/comments/cus4d0/looks_like_youtube_is_going_bonkers_with_its/) | Usuários relatam respostas que **somem sem aviso**: várias respostas à mesma pessoa, texto colado, edições repetidas, links. Mecanismo não confirmado pelo YouTube. | HIPÓTESE |
| R8 | Blogs de ferramentas ([commentshark](https://www.commentshark.com/blog/youtube-comment-bot-tos-safe), [blabla.ai](https://blabla.ai/blog/youtube-comment-automation), [rocket.new](https://www.rocket.new/blog/youtube-comment-auto-reply-bot), [replient.ai](https://replient.ai/en/platform/ai-for-youtube-comments)) | Consenso comercial: responder no **próprio canal via API** é gestão normal; postar em vídeos alheios é spam; variar o texto, espaçar, sem links; **coração fica manual** (não há endpoint); começar com fila de aprovação. São vendedores (conflito de interesse). | HIPÓTESE |
| R9 | Comunidade (C1, C2) | Não dar coração em tudo; resposta genérica é percebida; humano cuida de crítica e assunto sensível. | HIPÓTESE |

### 8.2 Até onde dá para ir com segurança
**Permitido**
- **Responder via API** (`comments.insert`) a comentários **no próprio canal**, com consentimento expresso do dono (VERIFICADO: os métodos e a regra de consentimento existem; HIPÓTESE: que a regra permanente registrada satisfaz a exigência).
- **Variar o texto a partir de templates aprovados pelo José**: o texto é dele, o código só escolhe. Isso reduz o risco de "repetitivo" (R5) e mantém a regra "o Jev não escreve".

**Não existe na API**
- **Coração e like em comentário** (VERIFICADO pela ausência em R2). A única via é a interface (Camofox), que é automação de navegador: contraria os termos do YouTube sobre acesso automatizado e expõe a sessão do Studio, que é exatamente o ponto frágil (queda de sessão, desafio de login). Risco **maior** que o da resposta via API.

**Proibido ou fora**
- Comentar em vídeos de outros canais.
- Respostas idênticas em massa.
- Links nas respostas.
- Responder no lugar do José em crítica, pergunta factual ou tema sensível.

### 8.3 Riscos
1. **Spam/terminação** (R5, R6): o volume e a repetição é que pesam. Nossa base é de 0 a 3 comentários por vídeo, então o volume é baixo; a repetição se controla com o banco de templates.
2. **Resposta some** (R7): mais de uma resposta à mesma pessoa, texto repetido, edição. Por isso, no máximo 1 resposta por autor por vídeo, nunca editar, sempre conferir depois.
3. **Ironia pt-BR**: agradecer um "kkkk que vídeo ruim" é pior que não responder. Qualquer `ironia_possivel` fica fora.
4. **Responder golpista ou bot**: valida o golpe e o comentário ganha destaque. Golpe, imitação, link e `likelySpam` ficam fora.
5. **Prometer o que não vamos cumprir** ("vamos fazer esse tema!"): os templates não prometem nada.
6. **Nome do autor no texto**: é dado pessoal e pode trazer ofensa ou injeção. Nunca usar o nome.
7. **Camofox para coração**: queda de sessão e desafio de login no Studio; padrão de automação na conta do canal.
8. **Público infantil**: em vídeo "feito para crianças" os comentários ficam desligados (Ajuda do YouTube). A PQBR não marca esse selo, mas comentário que pareça de criança (idade declarada, escola) fica fora por precaução (HIPÓTESE de risco).
9. **Divulgação**: a política exige não enganar (III.I.11). Não achamos regra que obrigue a avisar que a resposta é automática (HIPÓTESE).

### 8.4 Proposta concreta

**Elegibilidade (Jev classifica; o código decide)**
- **Elegível**: `classes` ⊆ {elogio, relato_cta, outro/comentário comum, sugestao_tema}, `alvo` ≠ outro_usuario, `ironia_possivel=não`, 2 rodadas iguais **só se** houver dúvida (1 rodada basta para elogio claro, que é o custo mínimo), comentário de nível superior, `moderationStatus=published`, `canReply=true`, idioma pt.
- **Excluído (vai para o fluxo atual ou é ignorado)**: reclamação, aviso de erro, **pergunta** (precisa de resposta real → José), spam/golpe, ofensa, tentativa de instrução, dado pessoal, link/contato externo, imitação, `likelySpam`/`heldForReview`, ironia possível, divergência, tema sensível da lista de bloqueio do contrato (política, religião, tragédia, saúde/finanças/jurídico), possível criança, autor = canal, resposta entre espectadores, comentário editado depois da resposta, vídeo em HOLD ou privado, comentário com mais de 7 dias.
- O Jev devolve também `tipo_resposta` ∈ {agradecer_elogio, agradecer_relato, agradecer_sugestao, agradecer_risada, agradecer_generico} e `tom` ∈ {curto, normal}. Nada de texto.

**Banco de templates (texto do José; o código escolhe)**
- **5 tipos × 12 frases inteiras = 60 frases** aprovadas pelo José antes de ligar (podem ser rascunhadas por outro modelo, nunca pelo Jev). Frases inteiras em vez de pedaços montados, para não sair texto estranho.
- Emoji opcional de uma lista curta (0 ou 1 por resposta), escolhido por código.
- **Regras de variação (código)**:
  - nunca repetir frase no mesmo vídeo;
  - nunca repetir frase nas últimas 30 respostas do canal;
  - nunca o mesmo par frase+emoji em 7 dias;
  - sem nome do autor, sem citar o comentário, sem link, sem "inscreva-se" (o CTA já está no vídeo), sem promessa.
- Revisão do banco a cada 30 dias, ou quando o uso passar de 50%.

**Ritmo e limites (código)**
- Ciclo: a leitura de 30 min (t243) alimenta a fila; a resposta sai com **atraso aleatório de 15 a 120 min** depois do comentário (dá tempo de outros sinais críticos chegarem e evita resposta "instantânea de robô").
- **Espaçamento**: mínimo 3 min e aleatório até 12 min entre respostas.
- **Teto**: **6 respostas/hora** e **30/dia** (ESTIMATIVA: 30 × 50 = 1.500 unidades, ~15% da cota diária; com 0–3 comentários por vídeo, quase nunca chega lá). Passou do teto: o resto fica sem resposta automática e entra no resumo do José.
- **1 resposta por autor por vídeo** e no máximo **2 por autor por 24 h** no canal. Nunca responde à resposta de alguém à nossa resposta (aí a conversa vai para o José, se ele quiser).
- Janela: só entre 08:00 e 22:00 PT (horário humano).

**Conferência depois de responder (código)**
- 60 min depois: `comments.list(id=…)` (1 unidade) para confirmar que a resposta existe e está `published`.
- Se sumir ou ficar retida: **para todas as respostas automáticas** e avisa o José (sinal de filtro de spam).

**Reações (coração)**
- **Via API: impossível.**
- **Via Camofox: proposta conservadora**: no máximo **1 sessão por dia**, junto de uma sessão do Studio que o guardião de sessão já abriria, até **10 corações por dia**, só em elogio ou relato elegível, em ritmo humano (pausa aleatória entre cliques). Qualquer sinal de sessão instável, desafio de login ou tela diferente do esperado → aborta sem tentar de novo e avisa o José.
- **Alternativa de menor risco**: nenhum coração automático; o resumo do Telegram lista "merece coração" e o José dá à mão pelo celular.

**Kill switch (desliga as respostas e reações automáticas)**
- **Manual**: comando `/pausar_respostas` e `/retomar_respostas` no Telegram, só do ID do José. Uma flag no Supabase é conferida antes de cada envio.
- **Automático**:
  - resposta sumiu ou ficou retida;
  - erro 403 ou `quotaExceeded`;
  - HOLD de conformidade ou vídeo tornado privado;
  - e-mail do YouTube classificado como atenção/crítico pelo observador;
  - pico de comentários acima de 3× a média do vídeo na hora (possível brigada);
  - Jev rodando por fallback ainda não avaliado;
  - falha de validação do esquema.
- Volta só com `/retomar_respostas` do José.

**Implantação em 2 fases**
1. **Sombra (7 dias)**: o código escolhe a resposta e manda ao José no resumo ("responderia X com Y"), sem postar. José marca o que não gostou e isso vira rótulo.
2. **Automático**: liga com os tetos acima; o relatório diário mostra respostas enviadas, conferidas e bloqueadas.

**Consentimento**: registrar no `decisoes-jose-2026-10-08.md` a regra completa (classes, tetos, banco de templates, kill switch) como a autorização expressa exigida em III.I.2 e III.E.3.d.

### 8.5 Quem faz o quê
| Parte | Jev | Código | José |
|---|---|---|---|
| Elegível? tipo de resposta | sim (JSON fechado) | valida, aplica exclusões | — |
| Escolher a frase | — | sim (regras de variação) | escreve/aprova o banco |
| Postar | — | API `comments.insert` | — |
| Conferir se apareceu | — | sim | — |
| Coração | — | Camofox (se aprovado) ou lista no resumo | aprova a opção / dá à mão |
| Pergunta, crítica, sensível | — | encaminha | responde |
| Pausar/retomar | — | obedece à flag | comanda |

### 8.6 Perguntas para o José
1. **Coração**: Camofox automático (até 10/dia, 1 sessão por dia, com o risco de sessão do Studio) **ou** só a lista no resumo para você dar à mão?
2. **Fase sombra de 7 dias** antes de postar de verdade: aceita? E você escreve as 60 frases ou prefere que outro modelo rascunhe para você aprovar?
