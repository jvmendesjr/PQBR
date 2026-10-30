# PQBR — onboarding do agente (gerado; não editar à mão)

## ESTADO ATUAL da PQBR — continue daqui

Fonte única de "onde estamos". Não repete o ROADMAP: aponta os itens por id. **Atualize este arquivo a cada correção ou pendência resolvida.** O hook pre-commit exige isso quando o commit toca ROADMAP, LACUNAS, DECISOES-LOG ou CHANGELOG, e o `registrar_alteracao` exige isso para `tipo` correcao ou pendencia_resolvida.

Atualizado: 29/10/2026 (limpeza dos documentos para termos do MCP + ressalva sobre o backend anterior, ordem do José; migração para codebase-memory-mcp, OK José, versão 0.29.5; t164u handoff EP1003 v2 segue pendente de stills/clipes) · versão 0.29.6

## Migração do backend do `codigo` para codebase-memory-mcp (29/10/2026, versão 0.29.5, ADR-012)

> **Ressalva (29/10/2026, ordem do José):** se `GitNexus` for chamado acidentalmente nesta aplicação ou na documentação, leia-se **codebase-memory-mcp** — o backend atual da ferramenta `codigo` do pqbr-mcp. O GitNexus original (1.6.12) foi substituído em 29/10/2026 e permanece apenas no histórico e em `_obsoleto/`, sem desinstalar até ordem expressa.
- Backend do `codigo` agora é o codebase-memory-mcp 0.12.1 (MIT), em `~/.local/opt/codebase-memory-mcp/codebase-memory-mcp`, índice em `~/.cache/codebase-memory-mcp/` (projeto `PQBR`, ready). Interface do `codigo` inalterada; ferramenta da política agora é `codigo_consultar` (1.6.0).
- Backend anterior preservado, não desinstalado: índice fora do repo, wrapper e código em `_obsoleto/`, índice em `docs/_obsoleto/INDICE-migracao-cbm.md`. Rollback no §7 do plano.
- Vigia de sexta 08:00 agora vigia o CBM (entrada `codebase-memory-mcp`, leitura por `--version`); validação em produção é o relatório da sexta seguinte — não disparar o Schedule à mão.
- Pendentes: desinstalação do backend anterior (só com ordem expressa); 2 falhas pré-existentes em `test_flow_projeto.py` (EP1003).

## Onde paramos / handoff (t164u)

**Para o próximo agente (leia antes de qualquer ação):**

1. `docs/BRIEFING.md` → contexto do canal.
2. `docs/processos/CRIACAO-README.md` + `docs/processos/flow.md` → processo canônico (obrigatório antes de tocar Flow).
3. `config/flow_projetos.json` → EP1003 aponta para o projeto **v2** ativo.
4. Camofox **só** PQBR (`127.0.0.1:9387`, `userId=pqbr`); humanizado; **nunca logar**; **nada apagar** (projeto antigo `025dcfef-…` HOLD intacto).
5. Gates: `fichas_ok` / `storyboard_ok` / 0 créditos (parar se custo >0); stills só após storyboard texto OK; clipes só após revisão José das stills; reinício worker / MG-12 / merge main **só com OK José**.

**Onde paramos (29/10/2026, America/Fortaleza):**
- Projeto ativo: `PQBR-EP1003-cafe-fraco-v2` · id `3a9ca558-4c85-4502-8c19-7a8f42fa41dd` · https://flow.google.com/project/3a9ca558-4c85-4502-8c19-7a8f42fa41dd
- Feito: processo canônico; projeto v2; Agent Confirm=Sempre / 9:16 / Nano Banana Pro; Character `@PERS-menina-rosa`; Collections (Referencias/Storyboard/Cenas/Finais criadas na sessão); fichas PERS/OBJ/AMB; **storyboard texto Agente OK** (c01..c08, 0 créditos). Evidência: `/workspace/flow-check/ep1003-v2-storyboard.png`. Commit t163u `bc4101b`.
- **Não feito (próximo):** corrigir capa do Character PERS-menina-rosa (UI mostra imagem do café); confirmar/recriar coleção **Cenas** se ausente; gerar **8 stills** S01..S08 via Agente Flow (0 créditos); revisão José; clipes; MG-05 motion; MG-11 lote; MG-12 `core-ultra`+reinício (OK José); JEV-02; merge → main (OK José); investigar ImportError residual na tool MCP `estado` se voltar a falhar.
- Branch: `cursor/t132u-flow-imagem-849c`. Sem stills/clipes nesta handoff. Sem ações Flow em t164u.

## Onde estamos
- **Produção:** o lote do saldo em `runtime/lote-saldo/` (e o cartum 2D do Higgsfield) está **obsoleto** para publicação (t156u): o Higgsfield foi **DESCARTADO** do PQBR. Não apagar mídia sem OK. Os temas EP1002–EP1010 serão refeitos com Flow + flat + motion (**MG-11**). O EP1002 olhos-da-cara já está em `_descartado/` e o tema voltou a `proposto`. Ordem: fechar Flow → MG-05 (piloto 1) → José assiste → lote dos demais.
- **Publicação (ROADMAP F8-01):** o fluxo pelo Temporal está pronto. O worker foi reiniciado em 27/10 às 08:56 (-03, São Paulo; t128u) e carrega o fallback do refresh e o ensaio. `YOUTUBE_DRY_RUN=true`. Nada foi enviado. Até a produção ativa, vídeo aprovado que subir fica privado; público só depois, na ordem dos roteiros e nas janelas.
- **Agente externo:** o servidor MCP 0.2+ só funciona pela tailnet. A memória escrita leva o autor (o cliente) e o commit. O protocolo obrigatório está no AGENTS.md. O `initialize` do `pqbr-mcp` já devolve a frase de honestidade (t126u), desde o reinício das 08:56. Hindsight: bank `pqbr` com 877 documentos; as 7 candidatas restantes foram apagadas (t128u). **t154u:** a escrita do MCP é assíncrona e idempotente (`async` + `operation_id` determinístico) e o POST ao Hindsight espera até 120 s (`PQBR_HINDSIGHT_TIMEOUT`). Timeout não perde nem duplica: repetir a mesma alteração devolve a operação original. O `pqbr-mcp` foi reiniciado com a versão nova (a memória da t153u ficou duplicada pelo timeout de 30 s antes do conserto; o MCP não apaga).
- **Documentos (t129u):** `docs/LACUNAS-fluxo.md` só lista o que ainda falta no código. O roster vigente está em `docs/AGENTES.md`. Briefing, checklist pré-E2E, rascunho de SOUL e propostas não aplicadas foram para `docs/_obsoleto/`. As provas do F3-05 continuam em `docs/sdd/` porque o item segue aberto no ROADMAP.
- **Fluxo (t130u / t156u):** o episódio para no storyboard. O NotebookLM entrega roteiro, compliance e SEO, e não gera vídeo. `YOUTUBE_DRY_RUN=true`. Os vídeos de `runtime/lote-saldo/` estão **obsoletos** (Higgsfield descartado); não publicam. Refação = MG-11.
- **Paperclip (t130u):** `paperclipai.service` parado e desabilitado em 27/10. Sem desinstalar e sem apagar dados. `config/paperclip.json` está `parado_proposital`.
- **Jev (t143u, t144u — JEV-EF concluído):** `decide()` e funções estruturadas (`classificar_popup_camofox`, `escolher_ref_canario`, `triagem_correcao_jev`, `verificar_correcao_jev`, `decidir_repeticao_jev`, `classificar_email_youtube`) ligadas a `CorrecaoAutonomaWorkflow` e `checar_repeticao`, limiares calibrados na API real TypeSafe (`jev-latest`, 12 casos, 100% de acerto) e workers `pqbr-temporal-worker` / `pqbr-episodio-worker` reiniciados com `TYPESAFE_API_KEY` ativa.
- **Stickman, fichas e catálogo aberto (t133u, t141u, t146u, t148u, t150u):** o padrão definitivo do canal é o conjunto de 20 imagens que o José selecionou no Drive (`Fontes/Imagens`), versionado em `banco-fichas/` e, desde t150u, um **catálogo aberto** (`indice.json` 3.1.0 desde t155u, 62 fichas): catálogo do elenco com 12 personagens (`personagens/ELENCO-catalogo.png`), 6 folhas individuais multi-pose (`PERS-menina-rosa`, `PERS-cacheada`, `PERS-bone-verde`, `PERS-gravata-azul`, `PERS-roxo-ansioso`, `PERS-bob-oculos`, esta o nº 13), 11 ambientes, objetos e animais (cada um com ficha própria) e 11 **situações** (`SIT-*`, sugestões sem mídia). Estilo nas palavras do José: cartoon 2D, flat, colorido, personagens stickman (cabeça redonda branca com contorno preto, 2 olhos sempre visíveis, roupa chapada colorida fixa, fundo creme claro, zero texto). **Protagonistas:** `PERS-menino-azul` (nº 1, masculino) e `PERS-menina-rosa` (nº 2, feminina); a alternância par/ímpar segue. O agente pode inserir fichas novas pelo mecanismo `pipeline/banco_fichas.py` (contrato `FichaCatalogo`, modelos em `banco-fichas/modelos/`, testes); ficha nova nasce `aguardando_ok_jose` (usável) ou `sugestao`, e só o José aprova ou descarta. **t155u:** as 30 fichas que estavam `aguardando_ok_jose` (6 PERS derivadas, 12 OBJ, 12 ANIM) passaram a `permanente` (`indice.json` 3.1.0); as 11 `SIT-*` seguem `sugestao` (sem mídia). Contrato `FichaCatalogo` valida as 62 fichas. Imagem nova entra com até 2 MB e vídeo fica no Drive (o banco já tem ≈ 93 MB). O storyboard (1.3.0) cita o catálogo em `refs` e o pacote canônico do NotebookLM leva o resumo (`catalogo_visual`). As fichas nanquim de t146u foram descartadas e os IDs `PERS-M`/`PERS-F`/`PERS-M-classico` morreram. Regra canônica mantida: o que faltar de permanente é gerado no Google Flow com o modelo mais potente (`🍌 Nano Banana Pro`, 0 créditos). **t155u / P17 parcial:** `Instruções para o agente` no Flow regravadas no flat colorido (projeto `e2dacb70-b9d0-4dc7-8b93-e6ac1688a454`, Camofox PQBR); espelho Drive `00_Biblia_Visual/banco-fichas` com 111 arquivos (0 erros). Ainda faltam a folha individual do nº 1, a mídia das 11 `SIT-*` e o OK do José para reiniciar o worker com o storyboard 1.3.0.
- **Motion graphics (t145u, t147u, t149u, t150u, t153u):** REGRAS §26 aceita motion no pós (ambiente limpo, bom senso, rotina fixa gancho → conflito → cortina → bloco do porquê em motion → cortina → reconhecimento → CTA + loop). Motor próprio em `src/pqbr/pos/motion/` (seek(t), Chrome headless, FFmpeg), **catálogo de 15 modelos**, contrato `PlanoMotion` 1.2.0, papel `motion` (9º, hoje `core-alto`; proposta **MG-12** passa para `core-ultra`/Opus 5.5 com 3 camadas — código determinístico → Jev `decide()` → Opus; ainda sem alterar `config/modelos_9router.json`), preso ao catálogo, sem activity no worker até MG-07. Até o MG-07 a manutenção opera o `PlanoMotion` e o motor próprio renderiza. O piloto de t145u (EP1003 em cartum 2D) teve o **visual** reprovado (t147u) e a **ideia** mantida; a pasta `runtime/piloto-motion/cafe-fraco/` foi deletada em t152u por ordem do José (os originais do EP1003 seguem em `runtime/lote-saldo/cafe-fraco/`). A prova visual vigente do cartão é `runtime/piloto-motion/mg03/folha-cartoes-v2.png`, aprovada pelo José como ponto de partida. **Base visual vigente:** o mesmo flat colorido do stickman, com a **Fredoka** (t149u) e paleta do motor re-basiada em t150u (azul-aço masculino, rosa feminino, fundo creme claro; o papel creme e o nanquim de t146u saíram). **Personagem presente (t150u):** a peça `personagem-moldura` põe um personagem `PERS-*` num quadradinho no canto da zona segura, com a pose escolhida entre os recortes da ficha e criatividade liberada ao papel `motion`; o render acusa sobreposição. **Dossiê de movimento (t150u):** o motor segue próprio; whatships.com, o artigo do 0xMovez e o estudo do MiniMax H3 MAX entram só como gramática de movimento (REF-MG-01), sem frame nem texto de terceiros. **t153u — seis referências, seis peças e a delegação:** o José entregou bitrig, horizonx, omaphoto, vovy, raylight-2 e valendata e delegou a escolha técnica (ele não escolhe movimento a movimento). A análise foi por folha de contato (sem playback completo e sem frame de terceiro no repo), as fichas REF-MG-00..07 estão em `banco-fichas/referencias-motion/` (`indice.json` 0.4.0, **aprovada** desde t155u) e as peças novas são `frase-troca`, `marca-texto` (o `destaque` é trecho de `texto`, conferido pelo contrato), `numero-conta`, `leque`, `elo-causa` e `transicao-pincelada` (uso interno; a cortina padrão continua na entrada e na saída). Prova em `provas/mg10-pecas.png` (12 quadros, sem violação de zona segura; autocrítica 8,5 em `biblioteca/historico.md`). O **riscado** (palavra substituída) é o candidato mais forte do próximo lote. A escolha por episódio é determinística (tipo + semente, MG-04) e o OK do José é sobre a regra e as fichas. Coletânea e desenho em `docs/fases/motion-graphics.md` (Fase 2d), tarefas na Fase MG do ROADMAP (MG-01..MG-12). Nada publicado; `gemini_juiz` ainda não rodou. Falta ver o personagem num vídeo de episódio (MG-05) e o lote de refação sem Higgsfield (MG-11).

## Próximo passo
**Handoff t164u → novo agente:** ler BRIEFING + `processos/CRIACAO-README` + `flow.md` + `config/flow_projetos.json`. Continuar no projeto v2 `3a9ca558-…` (Camofox PQBR): (1) corrigir capa Character PERS-menina-rosa; (2) garantir coleção Cenas; (3) pedir **8 stills** S01..S08 ao Agente (0 créditos); (4) parar para revisão José. Depois: clipes → MG-05 → José assiste → MG-11. MG-12 / reinício worker / merge main **só com OK José**. Projeto `025dcfef-…` HOLD intacto. Sem apagar nada.



## Pendências abertas
| # | Pendência | Ref. ROADMAP | Dono | Bloqueio |
|---|---|---|---|---|
| P1 | Vídeos do saldo **obsoletos** (t156u, Higgsfield descartado). Não publicam. Refação = MG-11 (EP1002–EP1010). Ordem: Flow → MG-05 → José assiste → lote. Não apagar mídia sem OK | t156u · MG-11 | José | sem apagar; sem publicar o lote antigo |
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
| P16 | Piloto EP1003 v2: storyboard texto OK (t163u). Falta capa Character, coleção Cenas, 8 stills, revisão José, clipes, MG-05/11/12. Antigo 025dcfef HOLD | t145u–t164u · Fase MG / 4V | José e agente | stills→revisão→clipes; OK MG-12 |
| P15 | **Feito (t143u/t144u).** Jev (`decide()`, JEV-EF) ligado aos fluxos (`CorrecaoAutonomaWorkflow`, canário, pop-up Flow, e-mail YouTube, repetição R10), limiares calibrados na API real TypeSafe (12 casos, 100% de acerto) e workers reiniciados com `TYPESAFE_API_KEY` ativa. Resta apenas JEV-02 (chave OpenRouter do fallback) | RNF-02 · JEV-EF · t144u | concluído | JEV-02 (fallback OpenRouter) quando José fornecer chave |
| P17 | Processo canônico APROVADO (t160u). EP1003 v2 storyboard texto OK (t163u). **Do José:** revisão stills; folha nº 1; SIT-*; OK reinício worker / MG-12 / merge | t148u–t164u | José | stills+revisão; folha nº 1; SIT-*; OK reinício |
| P18 | Combo `core-ultra` **criado e testado** (t158u: HTTP 200, `claude-opus-5-5-medium`). **Falta:** OK José para trocar `motion` `core-alto`→`core-ultra` em `config/modelos_9router.json` + reinício. Medir custo real em `pqbr.consumo_modelos` no piloto | t157u/t158u · MG-12 | José | OK troca+reinício |

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
- **Processo de criação (t160u):** antes de produzir imagem/vídeo, consultar `docs/processos/CRIACAO-README.md` + playbook da plataforma. Fail-closed no Temporal (`processo_criacao_conferir`).
- **Projeto Flow por episódio (t161u) [VERIFICADO]:** um projeto Google Flow por episódio, título `PQBR-EP<nnnn>-<slug>`, registrado em `config/flow_projetos.json`. Projeto de testes `e2dacb70-…` só para testes — nunca destino de episódio e nada deletar sem OK. Ordem fail-closed: (1) entregar fichas do `banco-fichas/` ao projeto; (2) storyboard **só** via chat do **Agente** do Flow (0 créditos confirmado; padrão de prompt da pesquisa); (3) stills → revisão (`imagens_revisadas`); (4) vídeo. Gate código: `src/pqbr/pipeline/flow_projeto.py` (`exigir_antes_cenas` exige `fichas_ok` + `storyboard_ok`). Upload Angular estável: clicar `.sidebar-upload-btn` (cria o input) e `POST /upload` em `input[type=file]` (aba Envios); detalhe em `docs/processos/flow.md`.
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

- **Atualização 1

## Decisões recentes

## t162u (29/10/2026) — EP1003 Flow: Agent/settings/Character/Collections; storyboard pedido = HOLD render
- **José (via parent):** seguir `docs/processos/CRIACAO-README.md` v1.0.0 + `flow.md` (85c063b); no projeto `PQBR-EP1003-cafe-fraco` ligar Agente, Confirm=Sempre, defaults 9:16 + Nano Banana Pro, instruções flat; Character `PERS-menina-rosa`; Collections; enviar storyboard ao Agente; só confirmar 0 créditos; STOP após storyboard; screenshot; log/commit/MCP.
- **Feito no Flow (Camofox PQBR):** Agent on; Configurações do agente = Confirm **Sempre**, imagem **9:16** ×1, **🍌 Nano Banana Pro** (vídeo 9:16 Omni Flash); instruções flat stickman; Character nativo **PERS-menina-rosa** (resta 1× Personagem sem nome com mídia AMB errada — não apagado); Collections **Referencias / Storyboard / Cenas / Finais**; fichas AMB/OBJ/PERS na grade.
- **Storyboard:** pedido enviado ao Agente (formato 9:16, 8 painéis c01..c08, refs `@PERS-menina-rosa` + AMB/OBJ, SUBJECT/ACTION/CAMERA/ATMOSPHERE do storyboard 1.3.0, modelo sugerido). Sessão *Weak Coffee Storyboard Planning* → **Falha ao renderizar a resposta**. Sem grade visual, sem stills, sem clipes. Nenhum Confirmar com custo >0 (política 0 créditos respeitada). `storyboard_ok=false`.
- **Evidência:** `/workspace/flow-check/ep1003-storyboard.png`.
- **Sem:** stills/clipes, gasto de crédito confirmado, reinício worker, merge main, delete projeto testes.


## t163u (29/10/2026) — EP1003 Flow v2: novo projeto + storyboard Agente OK
- **José t151u:** continuar em **novo** projeto `PQBR-EP1003-cafe-fraco-v2` (Camofox PQBR; humanizado; nunca logar; nada apagado). Projeto anterior `025dcfef-…` permanece como está. Processo canônico `docs/processos/flow.md` (`git pull --rebase` primeiro). Agent on, Confirm=Sempre, 9:16 Nano Banana Pro, instruções, fichas PERS/OBJ/AMB, Character nomeado, Collections; storyboard **uma vez** mais conciso (c01..c08, @Nome); só 0 créditos; se Falha→wait/reload ≤1 extra; STOP após storyboard; apontar `flow_projetos.json`; log/commit/MCP; screenshot `ep1003-v2-storyboard.png`.
- **Feito:** criado projeto Flow `3a9ca558-4c85-4502-8c19-7a8f42fa41dd` (`PQBR-EP1003-cafe-fraco-v2`). Settings Agent: Confirm **Sempre**, **9:16**, **Nano Banana Pro**; instruções flat; uploads Envios PERS/OBJ/AMB; Character **PERS-menina-rosa** (sem unnamed); Collections **Referencias / Storyboard / Cenas / Finais**.
- **Storyboard:** prompt conciso 8 painéis enviado **1×** via Agente (0 créditos). Resposta OK — sessão *Comedic Cafe Coffee Storyboard* com grade c01..c08 (@PERS-menina-rosa + AMB/OBJ). Sem stills/clipes. Sem Falha ao renderizar nesta rodada. `storyboard_ok=true`.
- **Config:** `config/flow_projetos.json` EP1003 → v2; `projeto_anterior_hold` = 025dcfef… intacto.
- **Evidência:** `/workspace/flow-check/ep1003-v2-storyboard.png`.
- **Sem:** stills/clipes, delete do projeto antigo, custo >0, login.


## t164u (29/10/2026) — Handoff EP1003 v2 para outros agentes (José t152u)
- **José (sessão t152u):** salvar onde estamos no ESTADO, ROADMAP, memórias e site de visualização (:8088) para continuar com **outros agentes**. Sem ações no Flow nesta entrega.
- **Estado congelado:** projeto ativo `PQBR-EP1003-cafe-fraco-v2` (`3a9ca558-…`); storyboard texto Agente OK (`storyboard_ok=true`, t163u); antigo `025dcfef-…` HOLD intacto; sem stills/clipes no v2.
- **Docs:** seção **Onde paramos / handoff (t164u)** no ESTADO-ATUAL com instruções explícitas ao novo agente (BRIEFING, processos, flow_projetos, Camofox PQBR, gates). ROADMAP ganha subseção **Piloto EP1003** com checkboxes (feito / pendente). CHANGELOG 0.29.4. Aba Roadmap do mapa regenerada.
- **Pendências explícitas para o próximo agente:** capa Character PERS-menina-rosa (mostra café); coleção Cenas; 8 stills 0 créditos; revisão José; clipes; MG-05/11/12; JEV-02; merge main; ImportError MCP `estado` se reaparecer.
- **Sem:** Flow UI, stills, clipes, login, delete, reinício worker, merge, gasto de crédito.


## 29/10/2026: migração GitNexus → codebase-memory-mcp (aprovada por José)
- **José (20:40, America/Fortaleza):** aprovou o plano em `docs/sdd/PLANO-migracao-codebase-memory-mcp.md` com todos os recomendados: trocar só o backend do `codigo` (pqbr-mcp mantido, `query_graph` bloqueado, instalador sem setup de clientes), reiniciar só a unit `pqbr-mcp` (não o gateway Hermes), preservar o `.gitnexus/` de 215 MB fora do repo com índice, renomear `gitnexus_consultar` → `codigo_consultar` (política 1.6.0), post-commit com CLI CBM em segundo plano (não `auto_watch`), e NÃO desinstalar o GitNexus após o Passo 4 — fica em `_obsoleto/` até ordem expressa posterior.
- **Motivo:** GitNexus 1.6.12, licença PolyForm Noncommercial (aceita em t90u para uso pessoal sem revenda), não serve para uso com fins lucrativos. Substituto: codebase-memory-mcp 0.12.1, MIT, binário local, stdio, sem porta.
- **Desvios do plano, justificados e registrados:** binário em `~/.local/opt/codebase-memory-mcp/` em vez de `~/.local/bin/` (o instalador do CBM recusa diretório grupo-escritível; as permissões do `~/.local/bin/` não foram tocadas); `context`/`impact` não devolvem source (o context do GitNexus também não devolvia; source pelo MCP tripa a barreira de segredos com falso positivo sobre `@activity.defn` e pode vazar segredo embutido no código — o source se lê no arquivo, nas linhas indicadas); ADR numerada 012 (próximo livre após 011).
- **Resultado:** Passo 3 aplicado, Passo 4 verde (ver CHANGELOG 0.29.5),

## 29/10/2026: limpeza dos documentos para termos do MCP + ressalva (ordem do José)
- **José:** retire `GitNexus` de todos os documentos, ficando apenas no histórico; atualize tudo nos termos do MCP. E deixe uma ressalva onde necessário: se `GitNexus` for chamado acidentalmente nesta aplicação, o que realmente se está referindo é ao novo app.
- **Aplicado:** documentos vivos (ARQUITETURA §12, ROADMAP, ESTADO-ATUAL, onboarding, mapa 09/13, nota da política, comentários dos scripts do MCP e docstring do adaptador) falam só em codebase-memory-mcp / `codigo` / `codigo_consultar`. A ressalva está registrada nesses documentos: qualquer chamada acidental a `GitNexus` lê-se codebase-memory-mcp.
- **Histórico mantido, de propósito:** CHANGELOG (entradas antigas e a da migração), DECISOES-LOG (t84u–t90u e a migração), ADR-012, plano de migração, `docs/_obsoleto/` e o código preservado em `scripts/_obsoleto/` continuam citando o backend anterior — é o registro histórico, não uso atual. O backend anterior segue sem desinstalar até ordem expressa.
- Versão do projeto 0.29.6 (só documentação; nenhum código de comportamento alterado além de comentários/docstring).


## Fase atual do ROADMAP

## Fase: Conhecimento e agente externo agnóstico (t84u–t86u, 26/10/2026)

> **Ressalva (29/10/2026, ordem do José):** se `GitNexus` for chamado acidentalmente nesta aplicação ou na documentação, leia-se **codebase-memory-mcp** — o backend atual da ferramenta `codigo` do pqbr-mcp. O GitNexus original (1.6.12) foi substituído em 29/10/2026 e permanece apenas no histórico e em `_obsoleto/`, sem desinstalar até ordem expressa.
- [x] **Índice de código do MCP [agora]:** codebase-memory-mcp 0.12.1 (usuário, MIT, fora do repo), índice da PQBR registrado, reindex no post-commit, pré-requisito fail-closed. ARQUITETURA §12.
- [x] **Política por papel [agora]:** `config/politica_papeis.json` + filtro no Hindsight e no adaptador do MCP (`codigo_consultar`, política 1.6.0).
- [x] **Servidor MCP da PQBR só na tailnet (t89u, OK do José):** `pqbr-mcp`, 127.0.0.1:8791 + tailscale serve, só leitura, token por cliente.
- [x] **AGENTS.md gerado (t89u)** do onboarding do MCP.
- [x] Reclassificar com tags as memórias legadas sem tag (feito em t90u).
- [x] **Escrita de memória pelo MCP (t95u/t96u):** `registrar_memoria`/`registrar_alteracao` (contrato 1.0.0), só papel com escrita na política, autor = cliente do token, referência a commit verificado e arquivos. **t154u:** a escrita virou **assíncrona e idempotente** (`async: true` + `operation_id` determinístico por cliente/commit/conteúdo); timeout do POST ao Hindsight configurável (`PQBR_HINDSIGHT_TIMEOUT`, padrão 120 s, antes 30 s fixos). Reenviar a mesma alteração não duplica.
- [x] **ESTADO-ATUAL (t98u/t99u):** `docs/ESTADO-ATUAL.md` é a fonte única do handoff, a 1ª seção do onboarding/AGENTS.md; hook pre-commit e `registrar_alteracao` (tipo correcao/pendencia_resolvida) exigem a atualização; handoff no Hindsight (tag `estado`, todos os papéis).
- [x] **Papel `mantenedor` externo (t112u–t117u):** política 1.4.0 (lê todas as tags, repo todo, constrói/liga módulos; reinício/migração com OK); pqbr-mcp 0.4.0 exclusivo do mantenedor (outro papel 401/403); reiniciado e validado ao vivo; persistência verificada. Doc: `docs/operacao/onboarding-agente-externo.md`.
- [x] **Teste de agente do zero (t96u):** URL tailnet + token `mantenedor-externo` → onboarding → buscar_memoria → commit local `b63fa56` → registrar_alteracao → buscar_memoria retornou em ~10 s; indexador negado; sem token 401.
- [x] **Licença do backend do MCP:** MIT (codebase-memory-mcp). A licença do backend anterior (aceita em t90u para uso pessoal) não servia para uso com fins lucrativos — motivo da migração (ADR-012).
- [x] **Reclassificação do Hindsight por papel (t90u):** `scripts/hindsight/reclassificar.py`; 220 candidatas a descarte em `docs/operacao/hindsight-descarte-candidatos.md`.
- [x] Descarte das candidatas (t90s398): 231 apagadas após a indexação; docs vigentes corrigidos; indexador com a regra única de tags.
- [x] Revisar as 7 candidatas mantidas (sem substituta direta). Feito em t128u (27/10): as sete apagadas com OK do José; backup fora do git; bank 884 → 877.

- [x] **Migração do backend do `codigo` para codebase-memory-mcp (29/10/2026, OK José com os recomendados):** CBM 0.12.1 (MIT, SHA-256 conferido, `--skip-config`, Lens desligada, stdio) como backend do `codigo`; adaptador `src/pqbr/integrations/codebase_memory.py`; política 1.6.0; vigia com entrada CBM + leitor de binário; scripts `scripts/codebase-memory/`; backend anterior preservado em `_obsoleto/` (índice fora do repo) sem desinstalar; Passo 4 verde (consultas lado a lado, `detect_changes` com exatamente os arquivos da migração, vigia `em_dia`, suíte 686 passados + 2 falhas pré-existentes EP1003). ADR-012, CHANGELOG 0.29.5. Pendente: desinstalação do backend anterior (só com ordem expressa).


## LACUNAS (início)

# Lacunas que ainda existem (conferidas no código em 27/10/2026, t130u)

A tabela de 12/10 que bloqueava o fluxo no login da CLI do Paperclip foi para `docs/_obsoleto/lacunas-fluxo-ate-20261027.md`. Não é lacuna. A reposição de temas (`ReposicaoTemasWorkflow`) consulta o NotebookLM e grava no Postgres, sem Paperclip. O descarte de caderno de teste e o episódio estão registrados no `pqbr-episodio-worker`. Itens já feitos (descarte do EP1001, estilo via config, pedido de acesso que se fechou, restauração de sessão) não se repetem aqui.

## Abertas

0. **Ativação `processo_criacao_conferir` (t160u).** Activity e testes no repo; o `EpisodioWorkflow` já chama no início. **Falta reinício** do `pqbr-episodio-worker` (OK José) para valer em runtime. Docs: `docs/processos/`.

1. **Auditor no episódio.** `EpisodioWorkflow` para na ficha e não espera `veredito_auditor` (t130u). O sinal continua registrado e não é chamado. Não chama `auditor_gemini` nem `auditor_loop_gemini`. A activity `auditor_gemini` está no worker da fila `camofox-pqbr`. O script `scripts/e2e/auditor_gemini_ep.py` ainda existe. Os critérios `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco` já reprovam sozinhos (t108u); isso não falta.
2. **Fechado (t130u).** `tipo=short` não gera vídeo. `nlm_gerar_short` recusa antes do CLI. O episódio segue para roteiro, SEO e `storyboard_criar`.
3. **Códigos do lote 2510.** Os prontos em `docs/pesquisas/lote-2510/` não têm `PQBR-EP`. Sem código não há `drive_enviar` nem episódio no Postgres. Quem define os códigos é o José.
4. **Vídeo em série (Fase 4V).** O episódio para na ficha e não baixa vídeo do NotebookLM (t130u). Flow, Vids e Vibes continuam fora do código. Em 27/10 o Flow foi aberto à mão (t132u): duas imagens, nenhum vídeo. HOLD das três rotas está decidido (t529) e não implementado. O mapa de cliques só tem as três surpresas dessa tela.
5. **Projeto Flow EP1003 (t161u — parcial).** Projeto `PQBR-EP1003-cafe-fraco` (`025dcfef-…`) + 3 fichas na biblioteca. Falta storyboard via Agente (HOLD prompt-padrão), stills, revisão, vídeo. Gate: `src/pqbr/pipeline/flow_projeto.py`.
6. **Imagens do storyboard.** A activity `storyboard_criar` grava a ficha com `imagens_revisadas` false e não gera imagem. O teste manual (t132u) fez duas imagens no Flow; as duas saíram pessoa de cartum, não stickman. O banco `banco-fichas/` já tem o conjunto definitivo (t148u+) e catálogo aberto (t150u). Geração por cena no Flow a partir das fichas (Fase 4V) ainda não está no código. Instruções do Agente no projeto de testes já foram regravadas no flat (t155u); no projeto EP1003 ainda conferir/reaplicar se necessário.
7. **Navegador.** `NavegadorIdentidade` está em `src/pqbr/motores/navegador.py`. Nenhum workflow importa essa porta. O backup diário e o canário do ADR-012 não foram conferidos nesta passagem: não entram como feitos nem como lacuna confirmada.
8. **Publicação, o que ainda falta.** O envio real está desligado de propósito (`YOUTUBE_DRY_RUN=true`) até a pr

## Mapa visual

docs/mapa/index.html (servido em :8088) — diagramas: 00-visao-geral.mmd, 01-episodio.mmd, 02-reposicao-temas.mmd, 03-acessos.mmd, 04-descarte.mmd, 05-vigia-atualizacoes.mmd, 06-runs-presos.mmd, 07-cadeia-video.mmd, 08-identidade-camofox.mmd, 09-agentes-responsabilidades.mmd, 10-catalogo-erros.mmd, 11-publicacao.mmd, 12-storyboard-elenco.mmd, 13-memoria-mcp-handoff.mmd · aba Roadmap gerada de ROADMAP + ESTADO-ATUAL (scripts/mapa/roadmap.py; edite as fontes, nunca o HTML)
