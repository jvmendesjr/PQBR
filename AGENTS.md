# PQBR — onboarding do agente (gerado; não editar à mão)

## ESTADO ATUAL da PQBR — continue daqui

Fonte única de "onde estamos". Não repete o ROADMAP: aponta os itens por id. **Atualize este arquivo a cada correção ou pendência resolvida.** O hook pre-commit exige isso quando o commit toca ROADMAP, LACUNAS, DECISOES-LOG ou CHANGELOG, e o `registrar_alteracao` exige isso para `tipo` correcao ou pendencia_resolvida.

Atualizado: 28/10/2026 (t148u: padrão visual definitivo do canal fixado pelo José — as 12 fichas nanquim de t146u foram reprovadas e descartadas do `banco-fichas/`; no lugar, o conjunto de 20 imagens que ele selecionou no Drive (`Fontes/Imagens`): catálogo dos 12 personagens + 6 folhas individuais multi-pose, 11 ambientes, catálogos de 12 objetos e de 12 animais (`indice.json` 2.0.0); estilo canônico reescrito (REGRAS §5/§6, CONTRATO §19, `ESTILO_PADRAO_STICKMAN`/`BlocoVisual` 3.0.0); motion (t145u/t147u) já está na main e o catálogo v2 (MG-03) será re-basiado nesse conjunto) · versão 0.22.0

## Onde estamos
- **Produção:** o lote do saldo está em `runtime/lote-saldo/` (um diretório por tema). O EP1002 olhos-da-cara foi reprovado e descartado (`runtime/lote-saldo/_descartado/`), e o tema voltou a `proposto`.
- **Publicação (ROADMAP F8-01):** o fluxo pelo Temporal está pronto. O worker foi reiniciado em 27/10 às 08:56 (-03, São Paulo; t128u) e carrega o fallback do refresh e o ensaio. `YOUTUBE_DRY_RUN=true`. Nada foi enviado. Até a produção ativa, vídeo aprovado que subir fica privado; público só depois, na ordem dos roteiros e nas janelas.
- **Agente externo:** o servidor MCP 0.2+ só funciona pela tailnet. A memória escrita leva o autor (o cliente) e o commit. O protocolo obrigatório está no AGENTS.md. O `initialize` do `pqbr-mcp` já devolve a frase de honestidade (t126u), desde o reinício das 08:56. Hindsight: bank `pqbr` com 877 documentos; as 7 candidatas restantes foram apagadas (t128u).
- **Documentos (t129u):** `docs/LACUNAS-fluxo.md` só lista o que ainda falta no código. O roster vigente está em `docs/AGENTES.md`. Briefing, checklist pré-E2E, rascunho de SOUL e propostas não aplicadas foram para `docs/_obsoleto/`. As provas do F3-05 continuam em `docs/sdd/` porque o item segue aberto no ROADMAP.
- **Fluxo (t130u):** o episódio para no storyboard. O NotebookLM entrega roteiro, compliance e SEO, e não gera vídeo. `YOUTUBE_DRY_RUN=true`. Os vídeos de `runtime/lote-saldo/` ficam parados até a etapa de publicação.
- **Paperclip (t130u):** `paperclipai.service` parado e desabilitado em 27/10. Sem desinstalar e sem apagar dados. `config/paperclip.json` está `parado_proposital`.
- **Jev (t143u, t144u — JEV-EF concluído):** `decide()` e funções estruturadas (`classificar_popup_camofox`, `escolher_ref_canario`, `triagem_correcao_jev`, `verificar_correcao_jev`, `decidir_repeticao_jev`, `classificar_email_youtube`) ligadas a `CorrecaoAutonomaWorkflow` e `checar_repeticao`, limiares calibrados na API real TypeSafe (`jev-latest`, 12 casos, 100% de acerto) e workers `pqbr-temporal-worker` / `pqbr-episodio-worker` reiniciados com `TYPESAFE_API_KEY` ativa.
- **Stickman e fichas permanentes (t133u, t141u, t146u, t148u):** o padrão definitivo do canal é o conjunto de 20 imagens que o José selecionou no Drive (`Fontes/Imagens`) e que está versionado em `banco-fichas/` (`indice.json` 2.0.0): catálogo do elenco com 12 personagens (`personagens/ELENCO-catalogo.png`), 6 folhas individuais multi-pose (`PERS-menina-rosa`, `PERS-cacheada`, `PERS-bone-verde`, `PERS-gravata-azul`, `PERS-roxo-ansioso`, `PERS-bob-oculos` — esta fora do catálogo dos 12, a confirmar), 11 ambientes (`ambientes/AMB-*.png`), catálogo de 12 objetos (`objetos/OBJ-catalogo.png`) e de 12 animais domésticos (`animais/ANIM-catalogo.png`). Estilo: cartum 2D flat colorido (cabeça redonda branca com contorno preto, 2 olhos sempre visíveis, roupa chapada colorida fixa por personagem, fundo creme claro, zero texto). As 12 fichas nanquim de t146u foram reprovadas pelo José e descartadas do diretório; o gerador programático de t144u foi aposentado (`scripts/aposentado/frente_stickman.py`) e os IDs `PERS-M`/`PERS-F`/`PERS-M-classico` morreram com elas. Regra canônica mantida: o que faltar de permanente é gerado no Google Flow com o modelo mais potente (`🍌 Nano Banana Pro`, 0 créditos). Agente do Flow calibrado no projeto (`Confirmar antes de gerar = Sempre`, `9:16`, `x1`, `Nano Banana Pro`); as `Instruções para o agente` gravadas ainda descrevem o traço de t146u e serão regravadas (P17). Os protagonistas por gênero da alternância par/ímpar aguardam o José (P17).
- **Motion graphics (t145u, t147u):** REGRAS §26 aceita motion no pós (ambiente limpo, bom senso, rotina fixa gancho → conflito → cortina → bloco do porquê em motion → cortina → reconhecimento → CTA + loop). Motor próprio em `src/pqbr/pos/motion/` (seek(t), Chrome headless, FFmpeg), catálogo de 8 modelos, contrato `PlanoMotion`, papel `motion` (9º, `core-alto`, preso ao catálogo, sem activity no worker). Piloto em `runtime/piloto-motion/cafe-fraco/saida/piloto-motion.mp4` (bloco 14,87–33,5 s, original intacto): o José reprovou o **visual** (t147u — vídeo base em cartum 2D obsoleto; cartão branco e fonte de interface fora do traço) e manteve a **ideia**; o piloto vale como prova da mecânica. Base visual nova (REGRAS §26): o motion segue a mesma folha do stickman (papel creme `#f5f0e4`, nanquim, hachura, tipografia manuscrita única). Coletânea de referências em `banco-fichas/referencias-motion/` (REF-MG-00, `aguardando_ok_jose`), desenho em `docs/fases/motion-graphics.md`, tarefas na Fase MG do ROADMAP (MG-01..MG-07). Nada publicado, nada no Drive, `gemini_juiz` ainda não rodou. Nota t148u: a âncora visual do motion deixa de ser o nanquim de t146u e passa a ser o conjunto flat colorido novo de `banco-fichas/`; a paleta do motor, a persona e o `PlanoMotion.elenco` são re-basiados no MG-03.

## Próximo passo
O conjunto visual definitivo (t148u) já está em `banco-fichas/`. Falta o José apontar os protagonistas masculino e feminino do elenco novo (`ELENCO-catalogo.png`) para a alternância par/ímpar e confirmar se `PERS-bob-oculos` entra no catálogo (P17); depois o agente regrava as `Instruções para o agente` no Flow com o traço t148u e espelha o banco novo no Drive (`00_Biblia_Visual/banco-fichas`), liberando a produção das cenas `S01..S0N` no Flow com o Agente + fichas permanentes. OK do José na direção visual do motion e na coletânea de referências (P16: REF-MG-00 em `banco-fichas/referencias-motion/` e `docs/fases/motion-graphics.md`); depois dele: MG-02 (propostas de referências externas para o José escolher), MG-03 (catálogo v2 re-basiado no conjunto t148u + fonte manuscrita OFL), campo do bloco de números no contrato do storyboard e no template do NotebookLM (MG-06), activity `pos_motion` no worker (reinício exige OK, MG-07), checagem automática tela × bloco no Auditor, finalização e entrada do logotipo (MG-08 — propostas A/B/C em `docs/fases/motion-graphics.md`, o José escolhe o desenho).

## Pendências abertas
| # | Pendência | Ref. ROADMAP | Dono | Bloqueio |
|---|---|---|---|---|
| P1 | Vídeos do saldo ficam parados. José assiste quando puder. O EP1003 cafe-fraco já está aprovado (26/10, único até agora). Não roda o LOOP e não publica agora | Estado 27/10 · t130u | José | sem mexer nos arquivos até a etapa do Studio |
| P2 | Publicação: worker reiniciado 27/10 11:50 (-03), 0 workflows Running. `YOUTUBE_DRY_RUN=true`. Nada agendado (`agenda_publicacao` com 0 linhas). Envio real desligado. Refresh do app em teste vence ~2/11 21:20 (-03) | F8-01 | agente | sem envio até a produção ativa |
| P3 | Teste: LOOP por cena vs o atual | Estado 26/10 · Testes pendentes | agente | depois do fluxo de publicação |
| P4 | **Feito (t108u/t109u).** Juiz por etapa (`gemini_juiz` v1.0.0): pré-produção usa 3.8 Flash; produção (VISUAL e LOOP) usa 4 Argon Baixo. O worker `pqbr-episodio-worker` foi reiniciado com OK do José às 16:57 (-03), e o poller está ativo na fila `episodio-pqbr`, ns `pqbr` | Estado 26/10 · DECISOES-LOG t109u | agente | concluído |
| P5 | **Substituída (t148u).** O José reprovou as 12 fichas permanentes de t146u (nanquim, Nano Banana Pro) e mandou descartá-las do diretório. No lugar ele entregou o conjunto definitivo de 20 imagens no Drive (`Fontes/Imagens`), já versionado em `banco-fichas/` (`indice.json` 2.0.0). Os protagonistas por gênero seguem em aberto na P17 | t146u/t148u · Fase 3 | José | fichas de t146u descartadas; conjunto novo instalado; falta apontar os protagonistas (P17) |
| P6 | **Feito (t130u).** `storyboard_criar` valida o Storyboard 1.2.0, grava a ficha e deixa `pode_gerar_video` false. O episódio para aí. Imagem e vídeo desta etapa não rodam | Estado 27/10 · DECISOES-LOG t130u | agente | concluído |
| P7 | **Feito (t108u).** O gate VISUAL agora tem `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco` (FichaCena/REGRAS §25), e cada um reprova sozinho. Validado no EP1002 (`loop-gemini-4argon-v2.json`): reprova, com S01 corte+grotesco, S04 corte e S02/S05/S09 boca | Estado 26/10 · CHANGELOG 0.14.0 | agente | concluído |
| P8 | **Feito (t128u).** As 7 memórias `obsoleto_candidato` do roster antigo de `docs/AGENTES.md` foram apagadas em 27/10 ~08:57 (-03). Bank 884 → 877. Backup fora do git | `docs/operacao/hindsight-descarte-candidatos.md` | agente | concluído |
| P9 | **Feito (t112u–t116u).** Papel `mantenedor` (política 1.4.0) lê todas as tags e o repo todo; pqbr-mcp 0.4.0 exclusivo do mantenedor; onboarding em `docs/operacao/onboarding-agente-externo.md`. Falta só entregar token por cliente novo (`scripts/mcp/novo_cliente.py <nome> mantenedor`) | Fase Conhecimento | agente | concluído |
| P10 | Hindsight conferido 27/10 08:10 (São Paulo): API healthy, banco conectado. A reconsolidação segue automática | Fase Conhecimento | Hindsight (automático) | só conferir de novo se o bank acusar falha |
| P11 | Merge da branch `feat/f8-01-publicacao-automatica` (já no GitHub) na main | — | José | merge/PR exige OK |
| P12 | ERR-01: revisar os erros aceitáveis | ERR-01 | agente | depois dos primeiros dias de produção |
| P13 | Proposta não aplicada: ferramentas só leitura para os agentes PydanticAI, sem MCP interno | F1-05 · t134u | José | sem efeito externo |
| P14 | Proposta não aplicada: acompanhamento de mudanças (vigia de fallbacks, canário, deriva de contrato, `dev_diagnosticar`). Sem agente novo. O NotebookLM não entra no canário | F6-02 · t135u/t136u | José | registro no worker exige reinício |
| P16 | Motion graphics: piloto do EP1003 café fraco com visual reprovado (t147u — vídeo base obsoleto, cartum 2D aposentado; o piloto vale só como prova da mecânica, autocrítica 8/10 em `src/pqbr/pos/motion/biblioteca/historico.md`). Ideia aprovada; base visual nova = folha do stickman; coletânea em `banco-fichas/referencias-motion/` (REF-MG-00 `aguardando_ok_jose`); Fase MG no ROADMAP. `gemini_juiz` não rodou. Papel `motion` sem activity. t148u: a âncora visual do motion passa a ser o conjunto flat colorido de `banco-fichas/` (nanquim de t146u descartado); MG-03 re-basia | t145u/t147u · REGRAS §26 · Fase MG | José | OK do José na coletânea/direção visual; depois MG-02 (referências) e MG-03 (catálogo v2); piloto 2 só com cenas do Flow (MG-05); entrada do logotipo aguarda a escolha do desenho (MG-08) |
| P15 | **Feito (t143u/t144u).** Jev (`decide()`, JEV-EF) ligado aos fluxos (`CorrecaoAutonomaWorkflow`, canário, pop-up Flow, e-mail YouTube, repetição R10), limiares calibrados na API real TypeSafe (12 casos, 100% de acerto) e workers reiniciados com `TYPESAFE_API_KEY` ativa. Resta apenas JEV-02 (chave OpenRouter do fallback) | RNF-02 · JEV-EF · t144u | concluído | JEV-02 (fallback OpenRouter) quando José fornecer chave |
| P17 | Conjunto visual t148u: o José aponta os protagonistas masculino e feminino do elenco novo (alternância par/ímpar) e confirma se `PERS-bob-oculos` entra no catálogo; depois o agente regrava as `Instruções para o agente` no projeto do Flow com o traço t148u e espelha o `banco-fichas/` novo no Drive (`00_Biblia_Visual/banco-fichas`, substituindo o espelho de t146u) | t148u · REGRAS §6 | José → agente | escolha dos protagonistas pelo José |

## Painel
Aba **Roadmap** no painel (:8088): Próximos passos, Falta e Feito gerados deste arquivo e do ROADMAP por `scripts/mapa/roadmap.py` (via `gerar_index.py`; o pre-commit regenera quando ROADMAP/ESTADO-ATUAL/mapa mudam). Itens com ☑ (feito) e ☐ (falta/próximos), só símbolo, nada clicável. Só leitura.

## Operacional e persistência (verificado 26/10/2026 18:21 -03)
pqbr-mcp 0.4.0 (user unit, enabled, Restart=on-failure, linger=yes), hindsight-api (enabled, Restart=always), Docker DB/Temporal (`unless-stopped`), worker enabled. Comando de checagem e detalhes: `docs/operacao/onboarding-agente-externo.md` § Operacional e persistência.

## Como atualizar
Resolveu ou corrigiu algo: tire a linha da tabela (ou mude o bloqueio), ajuste "Próximo passo" e a data acima, faça o commit junto com o DECISOES-LOG/CHANGELOG e chame `registrar_alteracao` com `tipo` igual a `pendencia_resolvida` ou `correcao`.


Fontes canônicas: docs/ESTADO-ATUAL.md (onde estamos), docs/REGRAS.md, docs/DECISOES-LOG.md, docs/ROADMAP.md, docs/LACUNAS-fluxo.md, docs/ARQUITETURA.md, docs/AGENTES.md, docs/mapa/. Em conflito, vale o doc canônico. O briefing do YT-LLM está em docs/_obsoleto/BRIEFING-novo-agente-pqbr.md e não é procedimento.

# Instruções para agentes que trabalham no repositório PQBR

Este arquivo é o ponto de entrada operacional para trabalho no checkout. Ele não cria uma nova fonte de decisão nem substitui as regras do projeto.

## Antes de trabalhar

1. Leia `docs/README.md` para localizar documentos e distinguir os roadmaps.
2. Para trabalho geral, siga a ordem autoritativa indicada em `docs/REGRAS.md` §0: REGRAS → SPEC → ARQUITETURA → TESTES → ROADMAP. Preserve decisões e gates; em conflito, vale o documento de maior autoridade.
3. Para uma tarefa de vídeo, leia `docs/blueprints/modulo-producao-video/README.md`, depois o blueprint e o roadmap do módulo. Esse roadmap é auxiliar: o estado global continua em `docs/ROADMAP.md`.
4. Canal do José: Telegram (bot próprio do PQBR, t538) + sinais do Temporal; painel: Temporal UI (t471/t474). Agentes: PydanticAI em activities do Temporal (ADR-011); o Paperclip está sendo retirado.
5. Trate relatórios em `docs/sdd/` como snapshots: confira data e status antes de usá-los como estado atual.

## Regras de segurança e escopo

- `docs/REGRAS.md` é a autoridade para decisões, permissões, fluxo e limites. Este arquivo não pode alterá-la.
- Não consulte `docs/arquivo/`, `docs/pesquisas/`, `docs/DECISOES-LOG.md`, `docs/_obsoleto/` ou outro material marcado como rascunho/legado sem a aprovação explícita exigida em `docs/REGRAS.md` §0. **Exceção (t530, José):** `docs/pesquisas/PESQUISA-extensoes-geracao-em-serie.md` pode ser lido por qualquer agente, **somente leitura** (referência da Fase 4V).
- Não altere, apague ou sobrescreva mudanças preexistentes; verifique `git status` antes de editar e use commits seletivos. Não faça push sem autorização.
- O Paperclip está em retirada (ADR-011): não crie organização, agente ou integração nova nele e não altere o código dele. `company/` continua como fonte das personas (`company/agents/<slug>/AGENTS.md`) e dos playbooks.
- Não marque um item como concluído sem evidência verificável. Um aceite de gate não fecha automaticamente checklists técnicos.
- Não publique vídeos, faça upload, use quota real ou acione efeitos externos sem cumprir os gates e autorizações previstos.
- NotebookLM continua sendo a fonte intelectual para pesquisa profunda, temas, ideias, roteiros e SEO; agentes (PydanticAI em activities do Temporal) orquestram e validam, sem duplicar esse trabalho, salvo complemento de relatório ou indisponibilidade documentada da ferramenta central.

## Identificação rápida dos documentos

- `docs/ROADMAP.md` — roadmap canônico geral, com estado oficial, dependências, tarefas e gates.
- `docs/blueprints/modulo-producao-video/ROADMAP.md` — plano auxiliar do módulo visual; não é o roadmap geral.
- `docs/AGENTES.md` — roster e desenho dos papéis; não é este arquivo de instruções.
- `company/agents/<slug>/AGENTS.md` — persona/instruções versionadas de cada papel (usadas pelos agentes PydanticAI).

## Mapa do sistema (t517)
- `docs/mapa/` (Mermaid + `index.html`) é gerado do código e serve de comunicação com o José e entre agentes.
- **Agentes nunca alteram o mapa sozinhos.** Mudança só por proposta aprovada pelo José. Divergência código × mapa: sinalizar (Observador/Dev) e propor o diff; `tests/unit/test_mapa.py` acusa.
- O registro de cliques (`config/mapa_cliques.json`, t126u) é outra coisa: elemento visto na tela, com data. Pop-up e botão fora do lugar atualizam esse registro e o processo segue.

## Honestidade (t126u)
- Dizer o que foi visto e o que não foi. Não inventar seletor, medida ou resultado.
- Se uma ideia do José não se sustenta, ou só aumenta o sistema, dizer isso antes de construir.
- Vale para todos os papéis e para quem entra pelo MCP.


## Conexão MCP

Servidor MCP da PQBR (só tailnet): porta HTTPS 8791 do host pc na tailnet (nome MagicDNS fora do repo), caminho /mcp, Streamable HTTP, Bearer token por cliente. Ferramentas conforme o papel: onboarding, buscar_memoria, codigo, estado (leitura) e registrar_memoria, registrar_alteracao (única escrita: Hindsight).

## Protocolo obrigatório do agente externo (t95u/t96u)

1. `onboarding` (este pacote).
2. `buscar_memoria` sobre o assunto antes de agir; em conflito, vale o doc canônico.
3. Implementar no checkout com commit local (sem push) e registrar a decisão em docs/DECISOES-LOG.md e a versão em CHANGELOG.md (SemVer).
4. Atualizar docs/ESTADO-ATUAL.md a cada correção ou pendência resolvida (o hook pre-commit exige quando ROADMAP/LACUNAS/DECISOES-LOG/CHANGELOG mudam).
5. Ao final, `registrar_alteracao` com o hash do commit e `tipo` (alteracao | correcao | pendencia_resolvida), citando arquivos; ele grava também o handoff. Sem commit, `registrar_memoria`. Sem esse registro a alteração não conta como entregue.

## BRIEFING

Histórico, fora do procedimento: docs/_obsoleto/BRIEFING-novo-agente-pqbr.md (herança do YT-LLM, 24/10/2026). O que vale está em REGRAS, CONTRATO-EDITORIAL e ESTADO-ATUAL.

## REGRAS (início)

# REGRAS da PQBR (Porquê BR)

## 0. Autoridade e uso deste arquivo

- **Este é o arquivo de autoridade.** As §0–§3 são a **constituição** do projeto (t328). Ordem: `docs/REGRAS.md` > `docs/SPEC.md` (requisitos) > `docs/ARQUITETURA.md` (desenho) > `docs/TESTES.md` (testes e validação) > `docs/ROADMAP.md` (tarefas, estado, fases e portões; o PLANO foi incorporado). `docs/AGENTES.md` é o roster vigente (9 papéis, ADR-011; o nono, `motion`, entrou em t145u). O corpo antigo, com contratação e issues do Paperclip, está em `docs/_obsoleto/` e não é instrução (t129u). `docs/CONTRATO-EDITORIAL.md` é canônico para tom, categorias e gabarito (t394). `docs/RASTREABILIDADE.md` liga requisito → desenho → tarefa → teste. Agentes leem nessa ordem. As regras são o núcleo e não podem se perder; a arquitetura se adapta a elas (t285).
- **Leitura (t536, José, 25/10/2026, ajusta t287):** o **agente PQBR** (auxiliar do José, t533) pode ler **todos** os documentos do PQBR, inclusive `docs/DECISOES-LOG.md`, `docs/arquivo/`, `docs/pesquisas/` e `docs/_obsoleto/`. Ele usa o material legado como histórico e aplica sempre o que é vigente neste arquivo. A restrição abaixo vale para os **agentes especialistas** do sistema, que se limitam às suas áreas.
- ⛔ **Agentes especialistas — proibido consultar sem aprovação explícita do José (t287):** `docs/arquivo/`, `docs/pesquisas/`, `docs/DECISOES-LOG.md` (só para registrar decisão nova) e qualquer rascunho ou material legado. Eles podem ser mal interpretados e aplicados em produção. Tudo o que vale deles já está aqui. **Exceção (t530, José):** `docs/pesquisas/PESQUISA-extensoes-geracao-em-serie.md` pode ser lido por qualquer agente, **somente leitura** (referência da Fase 4V).
- **Dúvida ou conflito sem certeza** nas decisões aprovadas: não adivinhar. Marcar "EM CONSTRUÇÃO — aguardando José" e levar a ele (t323).
- **Lacuna (t129u):** só entra em `docs/LACUNAS-fluxo.md` o que foi conferido no código e ainda falta. Login, issue ou ponte do Paperclip não são lacuna. O Paperclip aparece como histórico e como infraestrutura em retirada (ADR-011, F05-09).
- **NotebookLM (t130u):** não gera vídeo. Entrega pesquisa, roteiro, compliance e SEO. `storyboard_criar` valida o `Storyboard` 1.2.0 e grava a ficha. `imagens_revisadas` fica false. Esta etapa não gera imagem nem vídeo.
- **Gasto (t130u):** o contrato da etapa diz se pode gastar, qual modelo e qual meio (`src/pqbr/contratos/gasto.py`). O que o contrato não autoriza não roda. Storyboard: chat do NotebookLM, sim. Vídeo e infográfico do NotebookLM, não. O fallback de SEO usa o 9router no combo `especialista-seo` só depois de duas respostas inválidas do caderno.
- **Paperclip (t130u):** `paperclipai.service` parado e desabilitado, sem desinstalar e sem apagar dados. `config/paperclip.json` está `parado_proposital`, então a checagem não abre pedido. Apagar o produto fica para depois, com novo OK.
- **Login (t130u):** consentimento permanente para manter as sessões ativas. José entra só se a reautenticação autônoma não fechar. Parar um fluxo, pelo Telegram ou por pedido ao mantenedor, não desloga.
- **Saldo e cliques (t130u, ajustado t131u):** os vídeos já prontos ficam parados até a etapa de publicação no YouTube Studio. Envio real continua desligado. Não inventar seletor. O arquivo `config/mapa_cliques.json` não é catálogo: a tela do Camofox manda. O arquivo só anota surpresa, com data.
- **Logo (t131u):** a silhueta do mapa do Brasil não bloqueia geração nem subida. Antes de tornar público, avisar o José para ele olhar o logo. A correção do desenho pode ficar para depois.
- **Gasto visual (t131u):** imagem no Google Flow é gratuita e pode ser gerada na quantidade que o storyboard pedir. Vídeo gasta o saldo que houver no Flow; acabou, Google Vids; depois, Meta Vibes.
- **Flow, primeira tela (t132u) [VERIFICADO]:** em 27/10 a sessão já logada abriu `https://flow.google.com/`. Duas imagens estáticas, modelo Nano Banana 2 Lite, 9:16, 768×1376. A ficha da imagem não mostrou crédito. O pedido de stickman de tubos saiu cartum de pessoa, nas duas. O líquido claro só apareceu na segunda. O menu Baixar oferece 2K e 4K; só o 1K original foi baixado. Vídeo não foi gerado. O episódio ainda não chama o Flow. Não repetir o mesmo prompt.
- **Honestidade (t126u, José):** o agente diz o que viu e o que não viu. Não inventa seletor, número ou resultado para a conta fechar. Se uma ideia do José não se sustenta, ou só aumenta o sistema, o agente diz isso antes de construir. Vale para todos os papéis e para o agente externo no MCP.
- **Decisão nova:** entra no `DECISOES-LOG.md` (tNNN) **e** aqui, no mesmo commit. Se este arquivo divergir do log, vale a entrada mais nova do log e este arquivo é corrigido.
- **Legenda:** [APROVADO] decisão do José · [VERIFICADO] testado/visto na fonte · [HIPÓTESE] a confirmar antes de construir o que depende dela · EM CONSTRUÇÃO — aguardando José.
- Origem: os códigos (tNNN, "item N", nomes de bloco) remetem ao `DECISOES-LOG.md`; "07/10" = registro de 07/10/2026.

- **Atualização 11/10 (t384–t394), prevalece sobre qualquer trecho abaixo que diga o contrário:**
  1. **Estratégia:** a entrega à core-eng foi abolida; o jr constrói a PQBR **no Paperclip** (t394). **[SUPERADO por ADR-011/t510 e t536:** agentes em PydanticAI nas activities do Temporal; o Paperclip fica **parado e desabilitado** até a nova arquitetura ser validada, e só depois é desinstalado.**]** A ENTREGA está em `arquivo/`. A equipe vigente e o mapa @prod-* → agentes estão em `AGENTES.md` (§3 e §11).
  2. **Autonomia/proatividade (t384, t390):** a empresa opera semanas ou meses sem o José. Agentes aplicam sozinhos dentro de faixas e playbooks; o José só vê no relatório. Ainda exigem o José: excluir/rejeitar/banir; voltar a público vídeo do item 5 ou recorrer ao YouTube; gastar dinheiro; login manual pelo noVNC ou 2FA (só depois de esgotada a reautenticação autônoma, item 11); mudar regra canônica; segredos e infraestrutura.
  3. **Equipe:** 14 agentes já 

## Decisões recentes

## t144u (28/10/2026) — JEV-EF concluído, calibrado na API real e ligado aos fluxos + fichas completas em `banco-fichas/`
- **Diretriz do José:** prosseguir autonomamente para concluir todo o ciclo do JEV-EF (ligar `decide()`, calibrar com casos reais, reiniciar workers) e definir/gerar as fichas completas de personagens (com roupa 2D chapada fixa e expressões), ambientes e objetos em `banco-fichas/`, apresentando as primeiras definições para o OK dele.
- **JEV-EF ligado nos fluxos (`src/pqbr/motores/decisao.py`, `src/pqbr/workflows/correcao.py`, `src/pqbr/pipeline/grade.py`):**
  - Funções estruturadas: `jev_disponivel`, `classificar_popup_camofox`, `escolher_ref_canario` (`EscolhaRefCanario`, segundo nível do canário ADR-012), `triagem_correcao_jev`, `verificar_correcao_jev`, `decidir_repeticao_jev` e `classificar_email_youtube`.
  - `CorrecaoAutonomaWorkflow` (`triagem_jev` e `verificar_jev`): mantém a trava dura de `SENSIVEIS` e `simulacao`; quando `simulacao is None` e `jev_disponivel()` é `True`, chama o Jev via `asyncio.to_thread` (escalando para `sensivel` / `ok=False` se `dec.escalar`). Sem chave, preserva `EmConstrucao` (compatível com testes offline).
  - `checar_repeticao` (`grade.py`): consulta `decidir_repeticao_jev` na faixa semântica quando `usar_jev=True` ou `decisor` é passado.
- **Calibração empírica real na API TypeSafe (`jev-latest`, 12 casos canônicos, 100% de acerto, gravado em `pqbr.consumo_modelos`):**
  - Pop-up promo (`0.98`), pop-up CAPTCHA (`0.99`

## t145u (28/10/2026) — Motion graphics no pós: regra, papel `motion` (híbrido, preso ao catálogo) e piloto no café fraco
- **Contexto:** José trouxe materiais sobre motion graphics (manual "Stickman & Motion Studio", artigo 0xMovez, skill `motion-graphics-studio`, `motion-reel-kit`, repositórios `motion-reels-f100k` e `sirioberati/YouTube-AI-Motion-Graphics`). Técnica comum: página HTML onde o quadro é função pura do tempo (`seek(t)`), molas fechadas, ruído com semente, sem timer nem transição CSS; Chrome headless captura quadro a quadro; FFmpeg junta. Ciclo de autocrítica: folha de contato → teste a 360 px → nota 1–10 → corrigir os 3 piores → repetir até ≥ 8.
- **Decisão 1 (José): a regra de t435 muda.** O pós passa a aceitar motion graphics sobre o vídeo da cadeia Flow/Vids/Vibes. Máxima: **ambiente limpo**. Gráfico entra por bom senso, sem cota. Usos: gráfico sobre a cena; cortar o vídeo para gráfico em tela cheia (explicação, passagem de tempo); barra de progresso discreta; vídeo ou imagem junto do gráfico para corrigir ou melhorar uma cena. "Interatividade passiva": sensação de movimento e ação, respeitando o lazer de quem assiste; nunca pedir clique nem comentário (t263 continua).
- **Decisão 2 (José): rotina fixa com transição padrão.** Gancho (vídeo Flow) → conflito (vídeo Flow) → transição padrão → **bloco explicativo em motion** (o porquê, ~18–20 s) → transição de volta → reconhecimento (vídeo Flow) → CTA + loop (vídeo Flow retoma a cena 1). O bloco nunca é a últim

## t146u (28/10/2026) — Regra das fichas permanentes em Nano Banana Pro (ancoradas nos frames reais do canal) + pesquisa sobre o Agente do Google Flow
- **Feedback e decisão do José:** avaliou os desenhos programáticos anteriores (`t144u`), apontou que ainda não gostou (inclusive erro grotesco de um olho só na pose lateral), enviou 5 recortes reais tirados de vídeos do próprio canal Porquê BR (`banco-fichas/referencias-canal/`) e determinou:
  1. **Regra canônica [APROVADO]:** para **personagens, objetos e locais permanentes** (`banco-fichas/`), as fichas são **permanentes** e devem ser geradas no Google Flow usando o **modelo mais potente de geração de imagens (atualmente `🍌 Nano Banana Pro`)**, mantendo a padronização estética dos personagens principais do canal.
  2. **Pesquisa solicitada:** verificar se é melhor usar o **Agente do Google Flow** entregando as imagens de referência (fichas permanentes), os storyboards como referência e os prompts na produção do vídeo.
- **Achado técnico de automação no Google Flow (`flow-media-upload`):** o botão `.sidebar-upload-btn` dentro de `Adicionar elementos à caixa de comando` (Angular Material) só monta o `<input type="file">` quando recebe `.click()`. Como `/tabs/:id/upload` do Camofox tenta primeiro `locator.focus()`, validamos a receita determinística: registrar `b.addEventListener("focus", () => b.click(), { once: true })` antes de chamar `/tabs/:id/upload` com `selector=".sidebar-upload-btn"`, anexando imagens de referência co

## t147u (28/10/2026) — Motion: o piloto não vale como visual; base no traço do canal e coletânea de referências
- **José, depois de assistir ao piloto de t145u:** o vídeo usado (EP1003, cartum 2D de 25/10) está obsoleto; o modelo 2D não será usado. A ideia do motion é interessante e deve ser implementada. O visual precisa melhorar e ficar mais atrativo, com referência atual, como os tutoriais pedem ("name a look, feed a frame"). Deve existir uma **coletânea de referências**, para que os vídeos não fiquem iguais: um padrão, com mudanças sutis que atendam ao tipo de conteúdo. Pediu avaliação, documentos atualizados e roadmap. A subida para a `main` ele confere na outra sessão.
- **Avaliação (mantenedor):**
  1. O piloto provou só a mecânica (corte, cortina, sincronia com a narração, áudio intacto, determinismo, zona segura). O visual v1 (cartões brancos, Liberation Sans, azul chapado) **não casa** com o traço do canal fixado em t146u (nanquim preto, hachura, papel creme `#f5f0e4`). Fica registrado como mecânica aprovada para seguir e visual reprovado.
  2. A referência que o canal já tem é a melhor que existe: os 5 frames reais em `banco-fichas/referencias-canal/`. "Your own library is a reference nobody else can copy" (artigo 0xMovez, passo 05). A base do motion passa a ser **papel creme + nanquim**, a mesma folha do stickman, para que gráfico e personagem pareçam desenhados pela mesma mão.
  3. Coletânea: faz sentido como **padrão fixo + variáveis sutis**. O padrão (papel, t

## t148u (28/10/2026) — Padrão visual definitivo do canal: conjunto do Drive (Fontes/Imagens) substitui as fichas nanquim de t146u
- **Decisão do José:** as 12 fichas geradas no Flow em t146u (nanquim sobre papel creme) não estavam num bom nível — mandou **descartá-las e tirá-las do diretório** e disse que quer refazer os personagens. Entregou no Drive da conta PQBR (`Fontes/Imagens`, pasta `1ziYivEewPQIvlgt6Z7v7R8wXPerPLvLd`) 20 imagens no estilo que quer, declarado **o padrão definitivo do canal**. Autorizou usar as imagens como fichas ("algumas delas são fichas, já podem servir como base") e a renomear os arquivos como necessário.
- **O conjunto (versionado em `banco-fichas/`, `indice.json` 2.0.0):** catálogo do elenco com 12 personagens numerados (`personagens/ELENCO-catalogo.png`); 6 folhas individuais multi-pose — `PERS-menina-rosa` (nº 2), `PERS-cacheada` (nº 5), `PERS-bone-verde` (nº 8), `PERS-gravata-azul` (nº 9), `PERS-roxo-ansioso` (nº 12) e `PERS-bob-oculos` (personagem nova, fora do catálogo dos 12 — sinalizado ao José); 11 ambientes (`ambientes/`, 3 deles com 3 personagens do elenco em cena: metrô, skatepark urbano, rua de compras); catálogo de 12 objetos (`objetos/OBJ-catalogo.png`); catálogo de 12 animais domésticos (`animais/ANIM-catalogo.png`, pasta nova).
- **Estilo canônico novo:** cartum 2D flat colorido — stickman de cabeça redonda branca grande com contorno preto, dois olhos pretos sempre visíveis, boca de reação, membros em traço preto fino, roupa chap

## Fase atual do ROADMAP

## Fase: Conhecimento e agente externo agnóstico (t84u–t86u, 26/10/2026)
- [x] **GitNexus [agora]:** global no servidor (1.6.12, fora do repo), índice da PQBR registrado, reindex no post-commit, pré-requisito fail-closed. ARQUITETURA §12.
- [x] **Política por papel [agora]:** `config/politica_papeis.json` + filtro no Hindsight e no adaptador GitNexus.
- [x] **Servidor MCP da PQBR só na tailnet (t89u, OK do José):** `pqbr-mcp`, 127.0.0.1:8791 + tailscale serve, só leitura, token por cliente.
- [x] **AGENTS.md gerado (t89u)** do onboarding do MCP.
- [x] Reclassificar com tags as memórias legadas sem tag (feito em t90u).
- [x] **Escrita de memória pelo MCP (t95u/t96u):** `registrar_memoria`/`registrar_alteracao` (contrato 1.0.0), só papel com escrita na política, autor = cliente do token, referência a commit verificado e arquivos.
- [x] **ESTADO-ATUAL (t98u/t99u):** `docs/ESTADO-ATUAL.md` é a fonte única do handoff, a 1ª seção do onboarding/AGENTS.md; hook pre-commit e `registrar_alteracao` (tipo correcao/pendencia_resolvida) exigem a atualização; handoff no Hindsight (tag `estado`, todos os papéis).
- [x] **Papel `mantenedor` externo (t112u–t117u):** política 1.4.0 (lê todas as tags, repo todo, constrói/liga módulos; reinício/migração com OK); pqbr-mcp 0.4.0 exclusivo do mantenedor (outro papel 401/403); reiniciado e validado ao vivo; persistência verificada. Doc: `docs/operacao/onboarding-agente-externo.md`.
- [x] **Teste de agente do zero (t96u):** URL tailnet + token `mantenedor-externo` → onboarding → buscar_memoria → commit local `b63fa56` → registrar_alteracao → buscar_memoria retornou em ~10 s; indexador negado; sem token 401.
- [x] Licença do GitNexus aceita (uso pessoal, sem revenda; t90u).
- [x] **Reclassificação do Hindsight por papel (t90u):** `scripts/hindsight/reclassificar.py`; 220 candidatas a descarte em `docs/operacao/hindsight-descarte-candidatos.md`.
- [x] Descarte das candidatas (t90s398): 231 apagadas após a indexação; docs vigentes corrigidos; indexador com a regra única de tags.
- [x] Revisar as 7 candidatas mantidas (sem substituta direta). Feito em t128u (27/10): as sete apagadas com OK do José; backup fora do git; bank 884 → 877.


## LACUNAS (início)

# Lacunas que ainda existem (conferidas no código em 27/10/2026, t130u)

A tabela de 12/10 que bloqueava o fluxo no login da CLI do Paperclip foi para `docs/_obsoleto/lacunas-fluxo-ate-20261027.md`. Não é lacuna. A reposição de temas (`ReposicaoTemasWorkflow`) consulta o NotebookLM e grava no Postgres, sem Paperclip. O descarte de caderno de teste e o episódio estão registrados no `pqbr-episodio-worker`. Itens já feitos (descarte do EP1001, estilo via config, pedido de acesso que se fechou, restauração de sessão) não se repetem aqui.

## Abertas

1. **Auditor no episódio.** `EpisodioWorkflow` para na ficha e não espera `veredito_auditor` (t130u). O sinal continua registrado e não é chamado. Não chama `auditor_gemini` nem `auditor_loop_gemini`. A activity `auditor_gemini` está no worker da fila `camofox-pqbr`. O script `scripts/e2e/auditor_gemini_ep.py` ainda existe. Os critérios `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco` já reprovam sozinhos (t108u); isso não falta.
2. **Fechado (t130u).** `tipo=short` não gera vídeo. `nlm_gerar_short` recusa antes do CLI. O episódio segue para roteiro, SEO e `storyboard_criar`.
3. **Códigos do lote 2510.** Os prontos em `docs/pesquisas/lote-2510/` não têm `PQBR-EP`. Sem código não há `drive_enviar` nem episódio no Postgres. Quem define os códigos é o José.
4. **Vídeo em série (Fase 4V).** O episódio para na ficha e não baixa vídeo do NotebookLM (t130u). Flow, Vids e Vibes continuam fora do código. Em 27/10 o Flow foi aberto à mão (t132u): duas imagens, nenhum vídeo. HOLD das três rotas está decidido (t529) e não implementado. O mapa de cliques só tem as três surpresas dessa tela.
5. **Imagens do storyboard.** A activity `storyboard_criar` grava a ficha com `imagens_revisadas` false e não gera imagem. O teste manual (t132u) fez duas imagens no Flow; as duas saíram pessoa de cartum, não stickman. O banco `banco-fichas/` já tem o conjunto definitivo de imagens entregue pelo José (t148u, `indice.json` 2.0.0); o que falta é a geração por cena no Flow a partir dessas fichas (Fase 4V), que ainda não está no código.
6. **Navegador.** `NavegadorIdentidade` está em `src/pqbr/motores/navegador.py`. Nenhum workflow importa essa porta. O backup diário e o canário do ADR-012 não foram conferidos nesta passagem: não entram como feitos nem como lacuna confirmada.
7. **Publicação, o que ainda falta.** O envio real está desligado de propósito (`YOUTUBE_DRY_RUN=true`) até a produção ativa. O roteiro de cliques do Studio não foi visto. `config/mapa_cliques.json` tem só surpresas do Flow (t132u), não um roteiro do Studio. O worker do episódio não tem o drop-in `telegram.conf`. O resto dessa etapa (chaves, agenda, registro no worker, fallback do refresh) está no ar desde 27/10 08:56 (-03).
8. **Teste adiado, não executar agora.** LOOP do Gemini por cena, e 4 Argon baixo contra 3.8 Flash no mesmo lote.

## Não são lacunas

- Login da CLI do Paperclip, issue no Paperclip para começar episódio ou descarte, e o token do bot

## Mapa visual

docs/mapa/index.html (servido em :8088) — diagramas: 00-visao-geral.mmd, 01-episodio.mmd, 02-reposicao-temas.mmd, 03-acessos.mmd, 04-descarte.mmd, 05-vigia-atualizacoes.mmd, 06-runs-presos.mmd, 07-cadeia-video.mmd, 08-identidade-camofox.mmd, 09-agentes-responsabilidades.mmd, 10-catalogo-erros.mmd, 11-publicacao.mmd, 12-storyboard-elenco.mmd, 13-memoria-mcp-handoff.mmd · aba Roadmap gerada de ROADMAP + ESTADO-ATUAL (scripts/mapa/roadmap.py; edite as fontes, nunca o HTML)
