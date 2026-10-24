# BRIEFING — novo agente específico PQBR / Porquê BR (substitui o YT-LLM)

t531 · 24/10/2026 · pedido do José. **Só leitura e proposta.** O novo agente ainda não foi criado, nenhuma mensagem foi mandada ao YT-LLM e os arquivos dele não foram alterados. O **jr** continua como agente generalista do José.

**Fontes**
- Conversa YT-LLM (agente `018f2ef8-…`): 3100 posições, de 16/09 a 28/09/2026. Lidas quase todas; ficaram de fora só lacunas de 1 a 4 mensagens.
- Arquivos do YT-LLM em `/workspace/yt-llm-bot/` no box: `playbook-decisoes.md`, `roadmap-b1.md`, `ops/`, `branding/`, `notebooks/`, `sources/`, `scripts/`, `temas/`.
- No repo PQBR: `docs/REGRAS.md`, `docs/ARQUITETURA.md` (ADR-011 e ADR-012), `docs/CONTRATO-EDITORIAL.md`, `docs/ROADMAP.md`, `docs/AGENTES.md` e as entradas de 23 e 24/10 do `docs/DECISOES-LOG.md` (t474, t476/t512–t517, t525–t530).

## Linha do tempo do YT-LLM (resumo)
- **16/09:**
  - instalou o notebooklm-py e a rotina de keepalive de 20 min no box;
  - analisou o caderno da "Fábrica de Shorts" e montou os cadernos B1;
  - escolheu o nicho B1, "Por que o Brasil funciona assim?";
  - criou o canal **Porquê BR** (`@porquebr-t4c`) e fez o OAuth da YouTube Data API (projeto `yt-llm-b1`) com o MCP `youtube-shorts`;
  - definiu o estilo **Stickman**, no lugar do VOX/papercut.
- **17/09:**
  - fez os Shorts v1 a v7 da tomada de 3 pinos (o v7 foi "quase lá"), o 127V/220V (FAIL) e o terremoto (PASS);
  - travou o overlay v8 e o logo v4;
  - publicou o 1º Short (privado e depois público): https://www.youtube.com/watch?v=-Af4vua4v9c;
  - criou o repo `jvmendesjr/porque-br` e o `BOOTSTRAP-AGENTE.md`.
- **20/09 a 28/09:** só rodou o keepalive, que falhou repetidamente. A última mensagem pede um novo login da conta e diz que a rotina fica parada até lá.
- **Depois disso:** o projeto foi refeito como **PQBR** no servidor `pc` (repo `jvmendesjr/PQBR`). O YT-LLM não acompanhou essa mudança.

## (a) O que continua válido e deve ser herdado
| Item | Onde está | Observação |
|---|---|---|
| Nicho B1 e o nome **Porquê BR** | `playbook-decisoes.md` §3; REGRAS §1 | Igual na PQBR. |
| Identidade **Stickman**: personagem expressivo e humanizado ("caras e bocas"), logo v4 com mapa e "?" teal, kraft + `#0D9488` | `branding/stickman-character-bible.md`, `identidade-stickman-brief.md`, `paleta-stickman-v1.md` | Aprovada na PQBR para o módulo Flow (REGRAS §6, t465). |
| **Overlay v8**: bug no topo direito com −50 % de tamanho e 50 % de alpha; lockup no canto inferior direito; logo final que cresce opaco por ~2,2 s | `ops/overlay-padrao-shorts-v1.md`, `branding/overlay/` | Vale para o pós. |
| Público, voz e postura: irreverente sem ser brega; curiosidades do **Brasil**, não genéricas | `branding/publico-voz-postura.md` | Vale como regra editorial; conferir com o CONTRATO-EDITORIAL. |
| **Um vídeo, avaliar e só então refazer** (substitui "2 por tema"; José, 17/09) | conversa YT-LLM, 17/09 | Bate com a economia de cota da PQBR. |
| **Séries e blocos** em vez de vídeos aleatórios; série 0 de mitos e cultura popular (só ideação) | `ops/ideacao-serie-mitos-cultura-popular.md`, `ops/ideacao-series-pilares-adiada.md` | Pendente; ver (c). |
| Descrever **2 a 4 movimentos críticos** (origem → destino, props nomeados); compor sem espremer os objetos | `ops/nlm-motion-e-composicao.md` | Passa a valer para os prompts de Flow e Vids. |
| Método **VOX / GUÍA VOX**: beats de 2,5 a 3 s, `.txt` com um prompt por bloco sem números, bloco de estilo repetido, prompt de animação universal | `sources/guia-vox.md`; PESQUISA-extensoes §1.1 | Base do storyboard em série (Fase 4V). |
| **Fábrica de Shorts**: prompts 1.1 a 4.3, persona, prévia de 6 vinhetas | `sources/fabrica-shorts.md`, `notebooks/` | O motor de temas e roteiros reaproveita; a geração de vídeo não. |
| **Gate pré-publicação fail-closed** com dry-run por padrão e live só com ordem explícita | `scripts/prepublish-gate.sh`, skill `gate-pr-publish-porqu-br` | Coerente com a Fase 8 da PQBR (só dry-run). |
| Duração 40 a 55 s; CTA de inscrição e like | `ops/duracao-shorts-porque-br.md`, `ops/cta-shorts-inscreva-like.md` | Conferir com o CONTRATO v2. |
| Hooks de documentação (`on_decision_lock`…) | `playbook-decisoes.md` §14, skill `documentar-decis-es-de-projeto` | Na PQBR viram o DECISOES-LOG e o CHANGELOG. |
| Lições de falha: o papercut sem movimento foi abortado, o stickman sumia, as refs de imagem eram ignoradas pelo Video Overview, as legendas pulavam palavras | `ops/log-falhas-stickman-nlm.md`, `ops/aprendizados-stickman-fluxo-v1.md` | Explicam por que o vídeo saiu do NotebookLM (t512). |

**Skills do usuário que vieram do YT-LLM**: `produ-o-short-b1-notebooklm`, `gate-pr-publish-porqu-br`, `p-s-short-porqu-br`, `capa-canal-porqu-br` e `documentar-decis-es-de-projeto`.
- Herdar: o gate, o pós (trim e logo) e a capa.
- **Revisar antes de usar**: a `produ-o-short-b1-notebooklm`, porque ela gera o vídeo no NotebookLM (ver b).

## (b) O que ficou desatualizado ou mudou
| Antes no YT-LLM | Agora na PQBR | Fonte |
|---|---|---|
| O NotebookLM gera o vídeo (Video Overview Short 9:16 "em volume") | O NotebookLM é o **motor intelectual** (temas, roteiros, direção, SEO). Vídeo pela cadeia **Flow → Google Vids → Meta Vibes → HOLD**, pelo navegador | DECISOES t512, t517, t529; ROADMAP 4V |
| Higgsfield/VOX como camada premium paga | **Sem APIs de geração** (Gemini/Veo/Omni, inclusive free tier); só as cotas já pagas, pelo navegador | DECISOES t516/t517 |
| Agente único que faz tudo pelo chat | **Temporal** como sistema nervoso + **PydanticAI** nas activities + **8 papéis** (Diretor, Líder Editorial, Pesquisador de Origem, Auditor, Compliance, Guardião, Observador, Dev) | ADR-011 (t510), DECISOES t512–t515, AGENTES §2 |
| Sem contratos | Contratos **Pydantic v2** versionados (SemVer em `VERSOES`) e motores atrás de portas (`config/motores.json`) | DECISOES t513, t515 |
| Paperclip / core-eng | **Paperclip removido** da operação (ADR-011). ⚠ A REGRAS §0 ainda cita "o jr constrói no Paperclip (t394)" e precisa ser corrigida | ADR-011; REGRAS §0 |
| Login no Chrome do box + cookies → `storage_state`; keepalive a cada 20 min no box | Sessão Google **só no Camofox PQBR (127.0.0.1:9387)** e no notebooklm-py isolado da PQBR (`NOTEBOOKLM_HEADLESS_REAUTH=0`). **Nenhum login Google em outros navegadores**; um único renovador | REGRAS §10–§11, REFERENCIA-sessao-google, ADR-012 |
| notebooklm-py global no box | Venv isolado `~/.pqbr/notebooklm/venv`, **0.8.5** travada | DECISOES t516 |
| Avisos no chat do agente; Discord cogitado | **Telegram (Hermes `pqbr`)**, só do ID do José; aprovações viram **sinais do Temporal**. Discord revogado | REGRAS §0 (t474) |
| Repo `jvmendesjr/porque-br` e workspace `/workspace/yt-llm-bot` | Repo oficial **`jvmendesjr/PQBR`** em `/home/pc/Workspace/PQBR` no servidor `pc` | REGRAS §24 (t280) |
| Cadernos B1 (Produção, Estilo Stickman, Episódio…) usados direto | Caderno **efêmero** por roteiro/semana, **nunca o mestre**; produção nunca no caderno raiz | REGRAS §9, DECISOES t512 |
| Upload pelo MCP `youtube-shorts` (OAuth no box) | Publicação pela **YouTube Data API**, aprovada (t273), mas na PQBR **só dry-run** (F8-01). O Studio pelo Camofox fica de reserva. A API do YouTube **não** está proibida, porque a proibição de t516 é para as APIs de geração | DECISOES t273, t516; ROADMAP F8 |
| Cadência de 3 a 5 Shorts/dia às 19h30 | A cadência é decidida pela grade da PQBR (Temporal). Grade e lote estão **pausados** | schedules PQBR |
| "Storyboard não", "só imagens de referência" (17/09, para o NotebookLM) | Agora o **storyboard em série é feito no Flow** (Fase 4V). A proibição valia só para o NotebookLM | PESQUISA-extensoes; ROADMAP 4V |
| Estilo A/B Stickman × VOX/papercut | **Stickman** fixado; papercut abortado | REGRAS §6, log de falhas do YT-LLM |
| Camofox inexistente ou global | Camofox **dedicado** à PQBR (9387); migração para `camofox@pqbr` na próxima integração | ADR-012, t526 |

## (c) Pendências abertas que estavam com o YT-LLM
1. **Keepalive NotebookLM falhando desde 20/09.** A rotina está parada à espera de um novo login. **Não reativar**: na PQBR a sessão é do Camofox 9387 e do venv isolado. A rotina deve ser **desligada de vez** quando o agente for arquivado.
2. **Token OAuth do YouTube no box** (`youtube-auth/`) e MCP `youtube-shorts` com `YOUTUBE_DRY_RUN=true`. Decidir com o José se:
   - migra para o cofre e o fluxo da PQBR (a DECISOES-LOG cita o token do yt-llm-bot reaproveitado para o Drive), ou
   - é revogado.
3. **Próximo Short do banco** e a **série 0** (mitos e cultura popular), só ideação. Viram tarefas do motor de temas da PQBR (`ReposicaoTemasWorkflow`).
4. Sanitizar as fontes entre episódios e criar o template PROMPT-EP. Na PQBR, o caderno efêmero resolve isso.
5. **Legendas que pulam palavras** (A5, waiver no 1º Short). Passar para o Auditor e o pós da PQBR.
6. **Silhueta do mapa no logo** ("precisa melhorar", José, 17/09). Fica com a identidade da PQBR.
7. Reserva de handles em outras redes: **só depois** das automações (José, 16/09). Segue adiado.
8. O repo `porque-br` tinha um push pendente de docs do piloto (17/09). Não fazer; a fonte de verdade agora é o `PQBR`.

## (d) Arquivos e recursos: o que migrar, arquivar e não tocar (nada é apagado)
| Ação | Itens |
|---|---|
| **Migrar (copiar) para o PQBR** e revisar | `branding/` (character bible, paleta, logo v4, overlay v8, capa), `ops/overlay-padrao-shorts-v1.md`, `ops/nlm-motion-e-composicao.md`, `ops/log-falhas-stickman-nlm.md`, `ops/aprendizados-stickman-fluxo-v1.md`, `sources/guia-vox.md`, `sources/fabrica-shorts.md`, `temas/banco-temas-b1.md`, `ops/ideacao-serie-mitos-cultura-popular.md`, `branding/publico-voz-postura.md`, `scripts/prepublish-gate.sh` (como referência). Destino sugerido: `docs/legado-yt-llm/` (somente leitura) ou as pastas canônicas, com OK do José |
| **Arquivar em `docs/_obsoleto/`** (com `git mv`, depois de copiados) | `playbook-decisoes.md`, `roadmap-b1.md`, `BOOTSTRAP-AGENTE.md`, `notebooks/sop-producao-shorts-b1.md`, `ops/PASSO-A-PASSO-stickman-completo.md`, os episódios v1 a v7 (só os QA, sem MP4) |
| **Não tocar** | `/workspace/yt-llm-bot/` original (fica como está), `youtube-auth/` (segredo; só o José decide), os cadernos NotebookLM B1 da conta, o canal e os vídeos publicados, o repo `jvmendesjr/porque-br` |

## (e) Proposta: o novo agente "PQBR"
**Escopo**
- Agente específico do Porquê BR que **opera e acompanha** a PQBR pelo repo `jvmendesjr/PQBR` no servidor `pc`.
- Cuida de: roadmap (Fase 4V e os gates), workflows Temporal, contratos, mapa, docs e relatórios das sextas. Prepara os pedidos de decisão ao José e redige o conteúdo editorial pelo motor NotebookLM.
- Não faz trabalho fora do PQBR.

**Fronteira com o jr**
| jr (generalista) | Agente PQBR (específico) |
|---|---|
| Tudo fora do Porquê BR: outros projetos, Camofox global (9377), infraestrutura geral do servidor, Tailscale, outros bots | Repo PQBR, Temporal PQBR, Camofox PQBR (9387, só via activities), NotebookLM PQBR, mapa, ROADMAP e DECISOES-LOG |
| Mudanças de rede ou exposição (com OK do José) | Pede ao José/jr; não mexe em rede |
| Pode ser consultado pelo agente PQBR | Não altera configuração global do servidor |

**Ordem de leitura**
1. `docs/REGRAS.md`
2. `docs/SPEC.md`
3. `docs/ARQUITETURA.md`
4. `docs/TESTES.md`
5. `docs/ROADMAP.md`
6. `AGENTS.md`
7. `docs/CONTRATO-EDITORIAL.md`
8. `docs/mapa/README.md`
9. este BRIEFING
10. `docs/pesquisas/PESQUISA-extensoes-geracao-em-serie.md` (leitura liberada, t530)

O resto de `docs/pesquisas/`, `docs/arquivo/`, `docs/_obsoleto/` e o DECISOES-LOG ficam **só com aprovação do José** (t287). Para registrar decisão nova, apenas acrescentar.

**Regras de segurança**
- **Conta e sessão:**
  - a conta de produção só existe no Camofox PQBR 9387 e no notebooklm-py isolado;
  - nenhum login Google no navegador do box nem em outros navegadores;
  - nenhum re-login headless; o login é feito só pelo José.
- **Segredos:**
  - nunca imprimir segredos ou cookies; passar por stdin;
  - nada de `.env` real no git; o hook `verificar_segredos` fica ativo;
  - sem `bash -x`.
- **Serviços e rede:**
  - não reiniciar o gateway Hermes;
  - não mexer na rede nem no Tailscale sem OK;
  - não tocar na 9387 fora das activities.
- **Ações externas:** publicar, enviar mensagem ou mudar o canal só como rascunho até o OK explícito.
- **Docs:** nunca apagar; mover com `git mv` para `docs/_obsoleto/`.
- **Mapa:** os agentes não alteram o mapa sozinhos; só por tarefa.

## (f) Riscos da troca
| Risco | Mitigação |
|---|---|
| **Identidade Google duplicada**: Chrome do box, `~/.notebooklm` do box e OAuth do YT-LLM usando a mesma conta da 9387 (risco de "dispositivo extra" e de derrubar a sessão) | O novo agente **nunca** usa o Chrome nem o notebooklm do box. Confirmar que o keepalive do YT-LLM está desligado; o José decide se desloga a sessão do box |
| **Tarefas órfãs**: rotina de keepalive, MCP `youtube-shorts` registrado no bot antigo, pedidos pendentes (push do `porque-br`, próximo Short) | Arquivar o YT-LLM só depois de desligar as rotinas dele; a lista (c) vira itens do ROADMAP ou LACUNAS |
| **Duas fontes de verdade** (`porque-br` × `PQBR`, playbook × REGRAS) | O PQBR prevalece; os docs do YT-LLM ficam como legado somente leitura |
| A skill `produ-o-short-b1-notebooklm` gerar vídeo no NotebookLM por engano | Marcar a skill como desatualizada ou ajustá-la (geração de vídeo → cadeia 4V) antes de ligar o novo agente |
| **Escopo sobreposto com o jr** (os dois mexendo no servidor `pc`) | A fronteira em (e); o jr mantém a infraestrutura geral e o agente PQBR só o repo e os serviços `pqbr-*` |
| Perda de contexto histórico | Este briefing + o legado copiado + a conversa YT-LLM continuam acessíveis para leitura |
