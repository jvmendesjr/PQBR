# PQBR — onboarding do agente (gerado; não editar à mão)

## ESTADO ATUAL da PQBR — continue daqui

Fonte única de "onde estamos". Não repete o ROADMAP: aponta os itens por id. **Atualize este arquivo a cada correção ou pendência resolvida.** O hook pre-commit exige isso quando o commit toca ROADMAP, LACUNAS, DECISOES-LOG ou CHANGELOG, e o `registrar_alteracao` exige isso para `tipo` correcao ou pendencia_resolvida.

Atualizado: 28/10/2026 (t153u: o José **delegou a escolha do movimento** ("não quero escolher movimentos") e entregou seis vídeos de referência; a manutenção analisou por folha de contato, escreveu as fichas REF-MG-02..07 e entregou **seis peças novas** no catálogo — `frase-troca`, `marca-texto`, `numero-conta`, `leque`, `elo-causa`, `transicao-pincelada` —, com catálogo 1.2.0, `fragmento_de` no contrato e prova em `banco-fichas/referencias-motion/provas/mg10-pecas.png`. Antes, t152u: pasta do piloto cafe-fraco deletada por ordem do José; cartão do MG-03 aprovado (`folha-cartoes-v2.png`); piloto 2 só com o Flow em operação regular. Antes, t151u: MG-03 feito — cartões do catálogo no traço do stickman (contorno preto e sombra chapada), peso 800 → 700 na Fredoka e custo de render medido (35–43 ms por quadro)) · versão 0.27.0

## Onde estamos
- **Produção:** o lote do saldo está em `runtime/lote-saldo/` (um diretório por tema). O EP1002 olhos-da-cara foi reprovado e descartado (`runtime/lote-saldo/_descartado/`), e o tema voltou a `proposto`.
- **Publicação (ROADMAP F8-01):** o fluxo pelo Temporal está pronto. O worker foi reiniciado em 27/10 às 08:56 (-03, São Paulo; t128u) e carrega o fallback do refresh e o ensaio. `YOUTUBE_DRY_RUN=true`. Nada foi enviado. Até a produção ativa, vídeo aprovado que subir fica privado; público só depois, na ordem dos roteiros e nas janelas.
- **Agente externo:** o servidor MCP 0.2+ só funciona pela tailnet. A memória escrita leva o autor (o cliente) e o commit. O protocolo obrigatório está no AGENTS.md. O `initialize` do `pqbr-mcp` já devolve a frase de honestidade (t126u), desde o reinício das 08:56. Hindsight: bank `pqbr` com 877 documentos; as 7 candidatas restantes foram apagadas (t128u).
- **Documentos (t129u):** `docs/LACUNAS-fluxo.md` só lista o que ainda falta no código. O roster vigente está em `docs/AGENTES.md`. Briefing, checklist pré-E2E, rascunho de SOUL e propostas não aplicadas foram para `docs/_obsoleto/`. As provas do F3-05 continuam em `docs/sdd/` porque o item segue aberto no ROADMAP.
- **Fluxo (t130u):** o episódio para no storyboard. O NotebookLM entrega roteiro, compliance e SEO, e não gera vídeo. `YOUTUBE_DRY_RUN=true`. Os vídeos de `runtime/lote-saldo/` ficam parados até a etapa de publicação.
- **Paperclip (t130u):** `paperclipai.service` parado e desabilitado em 27/10. Sem desinstalar e sem apagar dados. `config/paperclip.json` está `parado_proposital`.
- **Jev (t143u, t144u — JEV-EF concluído):** `decide()` e funções estruturadas (`classificar_popup_camofox`, `escolher_ref_canario`, `triagem_correcao_jev`, `verificar_correcao_jev`, `decidir_repeticao_jev`, `classificar_email_youtube`) ligadas a `CorrecaoAutonomaWorkflow` e `checar_repeticao`, limiares calibrados na API real TypeSafe (`jev-latest`, 12 casos, 100% de acerto) e workers `pqbr-temporal-worker` / `pqbr-episodio-worker` reiniciados com `TYPESAFE_API_KEY` ativa.
- **Stickman, fichas e catálogo aberto (t133u, t141u, t146u, t148u, t150u):** o padrão definitivo do canal é o conjunto de 20 imagens que o José selecionou no Drive (`Fontes/Imagens`), versionado em `banco-fichas/` e, desde t150u, um **catálogo aberto** (`indice.json` 3.0.0, 62 fichas): catálogo do elenco com 12 personagens (`personagens/ELENCO-catalogo.png`), 6 folhas individuais multi-pose (`PERS-menina-rosa`, `PERS-cacheada`, `PERS-bone-verde`, `PERS-gravata-azul`, `PERS-roxo-ansioso`, `PERS-bob-oculos`, esta o nº 13), 11 ambientes, objetos e animais (cada um com ficha própria) e 11 **situações** (`SIT-*`, sugestões sem mídia). Estilo nas palavras do José: cartoon 2D, flat, colorido, personagens stickman (cabeça redonda branca com contorno preto, 2 olhos sempre visíveis, roupa chapada colorida fixa, fundo creme claro, zero texto). **Protagonistas:** `PERS-menino-azul` (nº 1, masculino) e `PERS-menina-rosa` (nº 2, feminina); a alternância par/ímpar segue. O agente pode inserir fichas novas pelo mecanismo `pipeline/banco_fichas.py` (contrato `FichaCatalogo`, modelos em `banco-fichas/modelos/`, testes); ficha nova nasce `aguardando_ok_jose` (usável) ou `sugestao`, e só o José aprova ou descarta. Hoje `aguardando_ok_jose`: 6 derivadas do elenco (`PERS-senhor-cachecol` nº 3, `PERS-punk-azul`, `PERS-pijama-sono`, `PERS-fones-vermelho`, `PERS-nerd-laco`, `PERS-rei-coroa`), 12 objetos e 12 animais. Imagem nova entra com até 2 MB e vídeo fica no Drive (o banco já tem ≈ 93 MB). O storyboard (1.3.0) cita o catálogo em `refs` e o pacote canônico do NotebookLM leva o resumo (`catalogo_visual`). As fichas nanquim de t146u foram descartadas e os IDs `PERS-M`/`PERS-F`/`PERS-M-classico` morreram. Regra canônica mantida: o que faltar de permanente é gerado no Google Flow com o modelo mais potente (`🍌 Nano Banana Pro`, 0 créditos). Agente do Flow calibrado no projeto; as `Instruções para o agente` gravadas ainda descrevem o traço de t146u e serão regravadas (P17).
- **Motion graphics (t145u, t147u, t149u, t150u, t153u):** REGRAS §26 aceita motion no pós (ambiente limpo, bom senso, rotina fixa gancho → conflito → cortina → bloco do porquê em motion → cortina → reconhecimento → CTA + loop). Motor próprio em `src/pqbr/pos/motion/` (seek(t), Chrome headless, FFmpeg), **catálogo de 15 modelos**, contrato `PlanoMotion` 1.2.0, papel `motion` (9º, `core-alto`, preso ao catálogo, sem activity no worker). O piloto de t145u (EP1003 em cartum 2D) teve o **visual** reprovado (t147u) e a **ideia** mantida; a pasta `runtime/piloto-motion/cafe-fraco/` foi deletada em t152u por ordem do José (os originais do EP1003 seguem em `runtime/lote-saldo/cafe-fraco/`). A prova visual vigente do cartão é `runtime/piloto-motion/mg03/folha-cartoes-v2.png`, aprovada pelo José como ponto de partida. **Base visual vigente:** o mesmo flat colorido do stickman, com a **Fredoka** (t149u) e paleta do motor re-basiada em t150u (azul-aço masculino, rosa feminino, fundo creme claro; o papel creme e o nanquim de t146u saíram). **Personagem presente (t150u):** a peça `personagem-moldura` põe um personagem `PERS-*` num quadradinho no canto da zona segura, com a pose escolhida entre os recortes da ficha e criatividade liberada ao papel `motion`; o render acusa sobreposição. **Dossiê de movimento (t150u):** o motor segue próprio; whatships.com, o artigo do 0xMovez e o estudo do MiniMax H3 MAX entram só como gramática de movimento (REF-MG-01), sem frame nem texto de terceiros. **t153u — seis referências, seis peças e a delegação:** o José entregou bitrig, horizonx, omaphoto, vovy, raylight-2 e valendata e delegou a escolha técnica (ele não escolhe movimento a movimento). A análise foi por folha de contato (sem playback completo e sem frame de terceiro no repo), as fichas REF-MG-02..07 estão em `banco-fichas/referencias-motion/` (`indice.json` 0.3.0, `aguardando_ok_jose`) e as peças novas são `frase-troca`, `marca-texto` (o `destaque` é trecho de `texto`, conferido pelo contrato), `numero-conta`, `leque`, `elo-causa` e `transicao-pincelada` (uso interno; a cortina padrão continua na entrada e na saída). Prova em `provas/mg10-pecas.png` (12 quadros, sem violação de zona segura; autocrítica 8,5 em `biblioteca/historico.md`). O **riscado** (palavra substituída) é o candidato mais forte do próximo lote. A escolha por episódio é determinística (tipo + semente, MG-04) e o OK do José é sobre a regra e as fichas. Coletânea e desenho em `docs/fases/motion-graphics.md` (Fase 2d), tarefas na Fase MG do ROADMAP (MG-01..MG-10). Nada publicado, nada no Drive, `gemini_juiz` ainda não rodou. Falta ver o personagem num vídeo de episódio (MG-05).

## Próximo passo
Os protagonistas e o catálogo aberto (t150u) estão no repositório. Falta o agente regravar as `Instruções para o agente` no Flow com o estilo flat e espelhar o `banco-fichas/` 3.0.0 no Drive (`00_Biblia_Visual/banco-fichas`), e o José aprovar ou descartar as fichas `aguardando_ok_jose` e gerar a folha individual do nº 1 e a mídia das situações (P17); depois disso a produção das cenas `S01..S0N` no Flow com o Agente + fichas do catálogo. Subir o prompt novo do storyboard (1.3.0) para valer no episódio exige reiniciar o worker, com OK do José. Motion: as seis peças novas e as fichas REF-MG-02..07 estão no repositório (t153u); o José aprova a **regra** e as fichas (P16), não movimento a movimento. Depois dele: MG-04 (semente determinística no `PlanoMotion`), MG-05 (piloto 2 com o Flow em operação regular), MG-06 (campo do bloco de números no storyboard e no template do NotebookLM), MG-07 (activity `pos_motion`; reinício exige OK), checagem automática tela × bloco no Auditor e MG-08 (entrada do logotipo — propostas A/B/C em `docs/fases/motion-graphics.md`, o José escolhe o desenho).

## Pendências abertas
| # | Pendência | Ref. ROADMAP | Dono | Bloqueio |
|---|---|---|---|---|
| P1 | Vídeos do saldo ficam parados. José assiste quando puder. O EP1003 cafe-fraco já está aprovado (26/10, único até agora). Não roda o LOOP e não publica agora | Estado 27/10 · t130u | José | sem mexer nos arquivos até a etapa do Studio |
| P2 | Publicação: worker reiniciado 27/10 11:50 (-03), 0 workflows Running. `YOUTUBE_DRY_RUN=true`. Nada agendado (`agenda_publicacao` com 0 linhas). Envio real desligado. Refresh do app em teste vence ~2/11 21:20 (-03) | F8-01 | agente | sem envio até a produção ativa |
| P3 | Teste: LOOP por cena vs o atual | Estado 26/10 · Testes pendentes | agente | depois do fluxo de publicação |
| P4 | **Feito (t108u/t109u).** Juiz por etapa (`gemini_juiz` v1.0.0): pré-produção usa 3.8 Flash; produção (VISUAL e LOOP) usa 4 Argon Baixo. O worker `pqbr-episodio-worker` foi reiniciado com OK do José às 16:57 (-03), e o poller está ativo na fila `episodio-pqbr`, ns `pqbr` | Estado 26/10 · DECISOES-LOG t109u | agente | concluído |
| P5 | **Substituída (t148u).** O José reprovou as 12 fichas permanentes de t146u (nanquim, Nano Banana Pro) e mandou descartá-las do diretório. No lugar ele entregou o conjunto definitivo de 20 imagens no Drive (`Fontes/Imagens`), já versionado em `banco-fichas/` (`indice.json` 2.0.0). Os protagonistas foram definidos em t150u (nº 1 masculino, nº 2 feminina) | t146u/t148u/t150u · Fase 3 | José | fichas de t146u descartadas; conjunto novo instalado; protagonistas definidos; o resto segue na P17 |
| P6 | **Feito (t130u).** `storyboard_criar` valida o Storyboard (1.2.0 em t130u; 1.3.0 desde t150u, com `refs` do catálogo aberto), grava a ficha e deixa `pode_gerar_video` false. O episódio para aí. Imagem e vídeo desta etapa não rodam | Estado 27/10 · DECISOES-LOG t130u | agente | concluído |
| P7 | **Feito (t108u).** O gate VISUAL agora tem `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco` (FichaCena/REGRAS §25), e cada um reprova sozinho. Validado no EP1002 (`loop-gemini-4argon-v2.json`): reprova, com S01 corte+grotesco, S04 corte e S02/S05/S09 boca | Estado 26/10 · CHANGELOG 0.14.0 | agente | concluído |
| P8 | **Feito (t128u).** As 7 memórias `obsoleto_candidato` do roster antigo de `docs/AGENTES.md` foram apagadas em 27/10 ~08:57 (-03). Bank 884 → 877. Backup fora do git | `docs/operacao/hindsight-descarte-candidatos.md` | agente | concluído |
| P9 | **Feito (t112u–t116u).** Papel `mantenedor` (política 1.4.0) lê todas as tags e o repo todo; pqbr-mcp 0.4.0 exclusivo do mantenedor; onboarding em `docs/operacao/onboarding-agente-externo.md`. Falta só entregar token por cliente novo (`scripts/mcp/novo_cliente.py <nome> mantenedor`) | Fase Conhecimento | agente | concluído |
| P10 | Hindsight conferido 27/10 08:10 (São Paulo): API healthy, banco conectado. A reconsolidação segue automática | Fase Conhecimento | Hindsight (automático) | só conferir de novo se o bank acusar falha |
| P11 | Merge da branch `feat/f8-01-publicacao-automatica` (já no GitHub) na main | — | José | merge/PR exige OK |
| P12 | ERR-01: revisar os erros aceitáveis | ERR-01 | agente | depois dos primeiros dias de produção |
| P13 | Proposta não aplicada: ferramentas só leitura para os agentes PydanticAI, sem MCP interno | F1-05 · t134u | José | sem efeito externo |
| P14 | Proposta não aplicada: acompanhamento de mudanças (vigia de fallbacks, canário, deriva de contrato, `dev_diagnosticar`). Sem agente novo. O NotebookLM não entra no canário | F6-02 · t135u/t136u | José | registro no worker exige reinício |
| P16 | Motion graphics: piloto do EP1003 café fraco reprovado (t147u) e **deletado em t152u**; o cartão do MG-03 (`folha-cartoes-v2.png`) foi aprovado pelo José em 28/10. **t153u: o José delegou a escolha do movimento** (não aprova movimento a movimento), entregou seis referências e a manutenção entregou seis peças (`frase-troca`, `marca-texto`, `numero-conta`, `leque`, `elo-causa`, `transicao-pincelada`), as fichas REF-MG-02..07 (`indice.json` 0.3.0, `aguardando_ok_jose`) e a prova `provas/mg10-pecas.png` (autocrítica 8,5). O OK dele agora é sobre a **regra e as fichas**, não sobre cada peça. Seguem candidatos: carimbo, tarja, zoom, recorte-colagem, match cut e o riscado | t145u/t147u/t150u/t153u · REGRAS §26 · Fase MG | José | OK do José na regra e nas fichas (REF-MG-00..07); depois MG-04 (semente no código), MG-05 (piloto 2 só com cenas do Flow, quando o Flow estiver em operação regular), MG-06 (campo do bloco de números), MG-07 (activity `pos_motion`, reinício exige OK) e MG-08 (desenho do logo) |
| P15 | **Feito (t143u/t144u).** Jev (`decide()`, JEV-EF) ligado aos fluxos (`CorrecaoAutonomaWorkflow`, canário, pop-up Flow, e-mail YouTube, repetição R10), limiares calibrados na API real TypeSafe (12 casos, 100% de acerto) e workers reiniciados com `TYPESAFE_API_KEY` ativa. Resta apenas JEV-02 (chave OpenRouter do fallback) | RNF-02 · JEV-EF · t144u | concluído | JEV-02 (fallback OpenRouter) quando José fornecer chave |
| P17 | Catálogo visual t148u/t150u: protagonistas e nº 13 **já definidos** (t150u). Falta o agente regravar as `Instruções para o agente` no projeto do Flow com o estilo flat e espelhar o `banco-fichas/` 3.0.0 no Drive (`00_Biblia_Visual/banco-fichas`, id `1JcDUFDEdiQmDtHX_4c57lgLFcM6-yoT4`, substituindo o espelho de t146u; o banco passa de 90 MB, então confirmar o envio). O José aprova ou descarta as fichas `aguardando_ok_jose` (6 derivadas de `PERS-*`, 12 `OBJ-*`, 12 `ANIM-*`), gera a folha individual do nº 1 e a mídia das 11 `SIT-*`, e dá OK para reiniciar o worker com o prompt novo do storyboard | t148u/t150u · REGRAS §6 | José e agente | OK do José para o Drive, para o Flow e para o reinício do worker; aprovação das fichas |

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

## t149u (28/10/2026) — Banco de fontes do motion e Fredoka como fonte do canal
- **Decisão do José:** `banco-fichas/referencias-canal/` é obsoleto e foi deletado; o nome dos arquivos de fonte ficou a critério técnico do mantenedor; as candidatas foram aprovadas; **Fredoka é a fonte do padrão do canal** (aprovada e aceita). Fonte única definitiva, sem sorteio entre as quatro: identidade reconhecível e render determinístico.
- **Decisões técnicas (mantenedor):** (1) nome canônico ASCII `<id>/<id>.ttf` + `LICENSE.txt` (os nomes do Google Fonts têm colchetes e vírgulas que quebram URL e shell), nome original em `arquivo_original`; (2) Patrick Hand excluída (licença com e-mail pessoal; a barreira de segredos bloqueia); (3) `fonte_css` emite `font-stretch` quando há eixo `wdth`; (4) sem checagem de Reserved Font Name (só importa para fonte modificada; nenhuma declara RFN); (5) `PlanoMotion.fonte` aceita só fonte `aprovada` do banco, padrão `fredoka`; (6) fonte só por arquivo local, nunca CDN.
- **Não verificado:** o catálogo v1 usa pesos até 800 e a Fredoka vai a 700 (o navegador usa 700); o MG-03 deve ajustar. Amostra renderizada com Fredoka conferida a olho (título e rótulo), sem teste de leitura a 360 px.


## t150u (28/10/2026) — Estilo cartoon flat, protagonistas, catálogo aberto com situações, personagem presente no motion e dossiê de movimento
- **Decisão do José (nove pontos):** (1) estilo, nas palavras dele: cartoon 2D, flat, colorido, com personagens stickman; (2) protagonistas: o nº 1 do catálogo (`PERS-menino-azul`: cabelo preto espetado, camiseta azul, boca aberta sorrindo) é o masculino e o nº 2 (`PERS-menina-rosa`) é a feminina; (3) `PERS-bob-oculos` entra como nº 13; (4) o catálogo é aberto: tudo é referência, e o agente pode inserir personagens, figuras, objetos, lugares e situações, com regra, mecanismo, modelo e testes; (5) nova categoria situações (imagens e vídeos de poses e movimentos corriqueiros); (6) o bloco de motion pode ter um personagem presente num "quadradinho" do layout, com criatividade liberada; (7) quis saber como acrescentar fontes ao motion; (8) pediu a melhor estratégia para a galeria whatships.com e para o post do 0xMovez; (9) em seguida mandou `whatships.com/videos/minimax-h3-max-motion/`: adaptar paleta, visual e gráficos ao canal e manter só os movimentos gráficos.
- **Resolve:** o "EM CONSTRUÇÃO — aguardando José" de t148u sobre os protagonistas por gênero e a dúvida sobre `PERS-bob-oculos`. Segue aberto na P17: regravar as `Instruções para o agente` do Flow, espelhar o banco no Drive e as aprovações de ficha.
- **Catálogo aberto (mantenedor, dentro do pedido):** contrato `FichaCatalogo` 1.0.0 (`contratos/catalogo_visual.py`) e `pipeline/b

## t151u (28/10/2026) — MG-03: cartões no traço do stickman, peso 700 e custo de render
- **Ordem do José:** protagonistas e `PERS-bob-oculos` já definidos em t150u; o catálogo é aberto (o agente pode criar personagens novos seguindo a identidade e avisando o José). Fazer commit e push, depois seguir o roadmap.
- **Feito:** `g.cartao` no motor (contorno preto de 5 px, sombra chapada deslocada de 10 px, sem desfoque) nos quatro modelos de cartão; peso 800 → 700 nos modelos que o usavam. Sem textura de papel (o conjunto t148u é flat colorido; a textura só aumentaria o custo).
- **Medido:** bloco de 24 s a 30 fps, 720 quadros de tela cheia, 25–31 s de render, 35–43 ms por quadro. Antes e depois do cartão novo, sem diferença relevante.
- **Verificado a olho:** quatro quadros (título, linha do tempo, origem, versus) com a Fredoka. Não verificado: leitura a 360 px, nem o encaixe com cenas reais do Flow (MG-05).


## t152u (28/10/2026) — Piloto cafe-fraco deletado, cartão aprovado e piloto 2 só com o Flow em operação
- **Ordem do José:** deletar `runtime/piloto-motion/cafe-fraco/` (estilo errado desde o início); aprovou `folha-cartoes-v2.png` como ponto de partida; sanear o que for descartável; o piloto 2 será criado com a layoutica padrão do canal quando o Flow estiver em operação regular.
- **Feito:** pasta de 327 MB deletada (movida para `/tmp` e apagada lá; não tinha nada versionado). Os originais do EP1003 estão em `runtime/lote-saldo/cafe-fraco/` (conferido: 32 arquivos). Sanado também o lixo temporário desta sessão em `/tmp`. Referências vivas ajustadas em ESTADO-ATUAL, `docs/fases/motion-graphics.md` e `biblioteca/historico.md`; CHANGELOG e este log mantêm o histórico.
- **Não tocado:** `attachments/` e `pasta-temporario-deletar-depois/` (não são desta sessão; só o José diz se saem).
- **Referências do whatships:** entram como ficha de texto (REF-MG-NN, `aguardando_ok_jose`) com link, data e gramática; nunca vídeo ou quadro de terceiro. O José manda o link da página de cada vídeo e uma frase do que gostou.



## t153u (28/10/2026) — O José delega a escolha do movimento; seis referências viram seis peças (MG-10 parcial)
- **Pedido do José:** ele **não quer escolher movimentos**. Pediu que a manutenção fizesse a análise técnica e decidisse o que aproveitar dos seis vídeos de referência, **respeitando a identidade visual do projeto/canal e o tema do episódio**; sugeriu assistir ou "passar no Google" para descrever e roteirizar as transições, com possibilidades de uso combinado. Entregou: bitrig, horizonx, omaphoto, vovy, raylight-2 e valendata (galeria whatships.com).
- **Delegação registrada [APROVADO]:** a escolha técnica do movimento passa a ser da manutenção. O OK do José é sobre a **regra** ("como se escolhe") e sobre a ficha, não sobre cada peça ou movimento. A escolha por episódio é determinística — tipo de conteúdo + semente do código (MG-04), sem repetir a variante anterior — e fica na `justificativa` de cada peça até o MG-04 existir no código. Peça nova continua nascendo no catálogo com prova e `aguardando_ok_jose`; referência nova continua `aguardando_ok_jose`. Registrado em REGRAS §26 ("Quem escolhe o movimento"), `banco-fichas/referencias-motion/indice.json` (`delegacao_escolha`) e na persona `motion` (regra 11).
- **Como a análise foi feita (honestidade t126u):** as páginas têm o mp4 no JSON embutido; o CDN do X recusa `Referer`, então o download foi sem ele. Seis mp4 ficaram **só em `/tmp`** (nada versionado), e a análise foi por **folha de contato 5×5** (10 imagens, u

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
5. **Imagens do storyboard.** A activity `storyboard_criar` grava a ficha com `imagens_revisadas` false e não gera imagem. O teste manual (t132u) fez duas imagens no Flow; as duas saíram pessoa de cartum, não stickman. O banco `banco-fichas/` já tem o conjunto definitivo de imagens entregue pelo José (t148u) e, desde t150u, é um catálogo aberto (`indice.json` 3.0.0: personagens, figuras, animais, objetos, ambientes e situações; o storyboard 1.3.0 cita as fichas em `refs`). O que falta é a geração por cena no Flow a partir dessas fichas (Fase 4V), que ainda não está no código, e regravar as `Instruções para o agente` do Flow com o estilo novo (P17).
6. **Navegador.** `NavegadorIdentidade` está em `src/pqbr/motores/navegador.py`. Nenhum workflow importa essa porta. O backup diário e o canário do ADR-012 não foram conferidos nesta passagem: não entram como feitos nem como lacuna confirmada.
7. **Publicação, o que ainda falta.** O envio real está desligado de propósito (`YOUTUBE_DRY_RUN=true`) até a produção ativa. O roteiro de cliques do Studio não foi visto. `config/mapa_cliques.json` tem só surpresas do Flow (t132u), não um roteiro do Studio. O worker do episódio não tem o drop-in `telegram.conf`. O resto dessa etapa (chaves, agenda, registro no worker, fallback do refresh) está no ar desde 27/10 08:56 (-03).
8. **Teste adi

## Mapa visual

docs/mapa/index.html (servido em :8088) — diagramas: 00-visao-geral.mmd, 01-episodio.mmd, 02-reposicao-temas.mmd, 03-acessos.mmd, 04-descarte.mmd, 05-vigia-atualizacoes.mmd, 06-runs-presos.mmd, 07-cadeia-video.mmd, 08-identidade-camofox.mmd, 09-agentes-responsabilidades.mmd, 10-catalogo-erros.mmd, 11-publicacao.mmd, 12-storyboard-elenco.mmd, 13-memoria-mcp-handoff.mmd · aba Roadmap gerada de ROADMAP + ESTADO-ATUAL (scripts/mapa/roadmap.py; edite as fontes, nunca o HTML)
