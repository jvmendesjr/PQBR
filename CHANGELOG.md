# CHANGELOG — PQBR

## [0.31.1] — 2026-10-31 (docs/mapa/memórias do fluxo mestre; José t169u)
### Alterado
- Documentos vivos (REGRAS, ARQUITETURA, ESTADO, ROADMAP, LACUNAS, processos, CONTRATO-EDITORIAL) alinhados ao fluxo: mestre `00ce61ae` → `BriefingEfemerico` → efêmero → direção 2.0.0 → Flow pendente; papéis NLM/Temporal/agente explícitos.
- Mapa `01-episodio.mmd` + `producao-episodios.json` 1.2.1 + `index.html` regenerado (:8088).
### Adicionado
- Próximos tópicos (só registro): (1) papel mestre/efêmero na validação e auditoria; (2) José ajusta refs **VISUAIS** (fichas de personagens, objetos, estilo).
### Corrigido
- `LIMITE_ESTADO` do onboarding 20k→28k (P18 cortada); AGENTS.md regenerado.
### Alterado (correção José)
- Mapa :8088 prioriza etapa dos **CADERNOS** (mestre+efêmero); publicação só rótulo/rastreabilidade.
### Sem
- Reinício worker, push/merge, implementação dos próximos tópicos, alteração de fichas.

## [0.31.0] — 2026-10-31 (Caderno Mestre canônico + rótulo S##; José t168u)
### Adicionado
- Contrato `BriefingEfemerico` / `PedidoBriefingMestre` 1.0.0 (persona, prompts por etapa, pesquisa obrigatória + URLs, refs, modelo sugerido).
- Activities `nlm_mestre_perguntar`, `nlm_mestre_limpar_chat`, `nlm_mestre_briefing`, `nlm_abrir_efemero_com_briefing` (adaptador falso para testes).
- `config/caderno_mestre.json` + `templates/notebooklm/persona-mestre.txt` + scripts `criar_mestre_canonico.py` / `exportar_mestre_legado.py`.
- Export read-only `docs/pesquisas/mestre-antigo-c35d7b24/`.
### Alterado
- `CenaIndividual` e `DirecaoCenas` **2.0.0**: rótulo canônico `PQBR-EP####-S##`; `validar_stem_rotulo(stem==rótulo)`.
- `PedidoEpisodioE2E` / `PedidoNotebookLM` **1.1.0** (`usar_mestre`, `papel`, `briefing_id`).
- `MESTRES_PROIBIDOS` só legado; mestre novo allowlist por ID em config; trava: mestre nunca gera mídia.
### Removido / revertido
- Decisão operacional de 12/10 que excluía mestre do pipeline (papel de norteador restaurado; mídia continua proibida no mestre).
### Sem
- Reinício de worker, push/merge, geração de mídia, delete do caderno legado.

## [0.30.0] — 2026-10-30 (aba Produção + divergências; José pt162u)
### Adicionado
- Aba do painel **Produção de episódios (tema → publicação)** (`#producao`), gerada de `docs/mapa/producao-episodios.json` via `scripts/mapa/producao.py`.
- Contratos `PedidoEpisodioE2E` e `PedidoNotebookLM` 1.0.0 em `VERSOES` (`contratos/pedidos_producao.py`) + testes.
### Alterado
- Mapa `01-episodio.mmd`: `direcao_cenas_nlm` + `flow_projeto_exigir_antes_cenas`.
- Núcleo/processo `CRIACAO-README` e `flow.md` → **1.2.0**: direção/prompts vêm do NotebookLM; agentes só operam o Flow; `VERSAO_ESPERADA` 1.2.0.
- `EpisodioWorkflow` em `workflows.py` documentado como **legado**; oficial = `episodio.py` / fila `episodio-pqbr`.
- LACUNAS/DECISOES: EP1003 manual fora do Temporal ≠ caminho oficial.
### Não feito
- Reinício de worker; push/merge.


## [0.29.9] — 2026-10-30 (passo 1 direção NLM → CenaIndividual; José pt161u)
### Adicionado
- Passo 1 pós-roteiro no `EpisodioWorkflow`: activity `direcao_cenas_nlm` (porta `DiretorCenas`, adaptador NotebookLM via notebooklm-py + adaptador falso para testes).
- Contrato versionado `DirecaoCenas` 1.0.0 (`src/pqbr/contratos/direcao_cenas.py`): lista de `CenaIndividual` + estilo + `proximo=flow_cenas_individuais_pendente`.
- Validação fail-closed (`pipeline/validar_direcao_cenas.py`): refs no catálogo, trava stickman, persona adulta quando a ficha diz adulta, nada de `girl`/`menina`-idade para PERS-menina-rosa.
- Gates após a direção: `flow_projeto_exigir_antes_cenas` + `processo_criacao_conferir`. Passo 2 (adaptador Flow) permanece pendente.
- Testes com adaptador falso (sem rede): `tests/unit/test_direcao_cenas.py`.
- Ficha `PERS-menina-rosa` no `indice.json` alinhada ao MD (mulher jovem adulta, tag `adulta`).
- Handoffs: `docs/HANDOFF-EP1003-20261030.md`, `docs/PROMPT-CORRECAO-BLOQUEIO-EP1003.md`.
### Não feito (de propósito)
- Reinício de worker; geração Flow/NLM; merge em main; alteração em `docs/mapa/` (falta OK José — `test_mapa` aponta as duas activities novas).

## Não lançado — 2026-10-30 — EP1003 v3: 8 imagens de início + movimentos (sem vídeo)
- Regeneração 30/10/2026 (revisão do piloto, José): novas versões de S03, S04, S05 e S07 com a correção adulta — mulher jovem adulta, em pé no chão, sem banquinho, sem braços realistas extras (ficha PERS-menina-rosa e playbook atualizados, commit ea449f4). S07 precisou de 3 tentativas (falha de política, pergunta de confirmação não respondida, geração com movimento registrado). Versões antigas com problema permanecem na biblioteca, não apagadas. Nenhum vídeo gerado; revisão do piloto ainda pendente.


- Projeto Flow novo `PQBR-EP1003-cafe-fraco-v3` (`9c4ad934-…`), criado via Camofox com acesso livre (conta PRO José Vieira): settings verificados Confirm=Sempre, imagem 9:16 x1 Nano Banana 2.1, vídeo 9:16 x1 Omni 1.1 Flash; instrução do Agente salva; fichas PERS/OBJ/AMB entregues; coleção Referencias com 3 itens.
- 8 imagens de início S01..S08 geradas (Nano Banana 2.1, 9:16) e 8 prompts de movimento registrados no Flow, sem vídeo gerado — portão de revisão do piloto pendente (José). Correção: o v2 (`3a9ca558-…`) ainda existe no Flow e nada foi apagado nele; o v3 começa limpo. Objeto Character não criado no v3 (Agente: só via seção Personagens da UI); cenas usam o Element PERS. Plano validado em `runtime/piloto-flow/EP1003/PLANO-CENAS-v3.md/.json` (gitignored).
- Núcleo de criação continua 1.1.0, sem mudança de versão do projeto e sem reinício de worker.


## 0.29.8 — 2026-10-29 — Sincronização dos documentos vivos (ordem do José)

- Docs vivos limpos de storyboard como etapa: ESTADO-ATUAL (gates, onde paramos, fluxo, P6/P16/P17),
  ROADMAP (Fase 4V, R2/R3, MG-05/MG-06, piloto EP1003), CONTRATO-EDITORIAL §18, CRIACAO-README e flow.md.
- Modelo de imagem vigente uniformizado para Nano Banana 2.1 (antes Nano Banana Pro) em flow.md,
  CONTRATO-EDITORIAL, ESTADO-ATUAL e ROADMAP; Pro fica só como histórico.
- Papéis dos agentes no núcleo reescritos agente-primeiro (Diretor, Guardião, Auditor são agentes;
  José só decide, nunca executa). Motion: bloco de números passa a ser do roteiro/cenas individuais.
- Conteúdos obsoletos extraídos e indexados em `docs/_obsoleto/INDICE-sincronizacao-0.29.8.md` (nada apagado);
  história deliberadamente mantida em ROADMAP "Estado em 26/10/2026", CHANGELOG/DECISOES e _obsoleto/.
- `AGENTS.md` regenerado e site do mapa regenerado; estado novo registrado no Hindsight via pqbr-mcp.
- Núcleo de criação continua 1.1.0 (sem mudança de versão, sem reinício de worker necessário: o worker lê
  os docs do disco e a versão pinada não mudou). Pendentes: MG-05 (definição), folha nº 1, mídia SIT-*,
  OK MG-12 / merge main.

## 0.29.2 — 2026-10-29 (t162u)
- Flow EP1003: Agent/Character/Collections conforme `docs/processos/flow.md`; storyboard pedido ao Agente com HOLD por falha de render da UI.

## [0.29.7] — 2026-10-29 (storyboard removido definitivamente; cenas individuais; agente primeiro)
### Removido
- Storyboard do fluxo ativo, por ordem definitiva do José: board geral, `storyboard_criar`, `PROMPT_STORYBOARD`, gate `storyboard_ok` e etapa de storyboard no `EpisodioWorkflow` e nos playbooks. Motivo: um encarte só com muitas cenas facilita o erro do agente; cenas individuais com movimento bem definido no prompt são mais determinísticas. Código antigo preservado em `scripts/_obsoleto/` com índice em `docs/_obsoleto/INDICE-storyboard-removido.md`; nada foi apagado.
### Alterado
- **Cenas individuais:** cada cena é criada, validada e animada sozinha, uma por vez, pelo Agente do Google Flow, a partir das fichas pinadas, no formato do projeto, com modelo de imagem atual **Nano Banana 2.1** (registrado, fail-closed se ausente na UI). Contrato novo `CenaIndividual` 1.0.0 (`contratos/cena.py`, derivado da antiga FichaCena); gate `exigir_antes_cenas` exige só `fichas_ok`.
- **Regra suprema agente-primeiro** registrada no núcleo (`docs/processos/CRIACAO-README.md` 1.1.0): "manual" significa o agente faz; não há processo manual humano. **Piloto e automático:** a visualização que vai para aprovação do José é a do episódio piloto; depois do piloto aprovado, o fluxo fica automático e o José monitora independentemente; alteração → botão de emergência do Telegram ou pedido ao agente para interromper; operação interrompida só volta ao público por ordem do José.
- **Centro criativo:** NotebookLM (pai, via `notebooklm-py`) cria roteiro, personalidade, caderno, informações e pesquisa; o agente compila os prompts do Flow a partir do roteiro, do catálogo, do formato e do registro de modelos, em contratos Pydantic v2 no Temporal.
- Núcleo de criação 1.0.0 → 1.1.0 (`VERSAO_ESPERADA` atualizada); playbook Flow 1.0.0 → 1.1.0; mapa 12 renomeado para `12-cenas-elenco.mmd` e índice regenerado.
### Não alterado
- Motion graphic (MG-05): segurado, definição pendente. Google Vids / Meta Vibes: fallback. Publicação: dry-run; item 5 das REGRAS (voltar a público) intacto.

## [0.29.6] — 2026-10-29 (documentação em termos do MCP + ressalva)
### Alterado
- Documentos vivos atualizados para termos do MCP: ARQUITETURA §12, ROADMAP (fase Conhecimento), ESTADO-ATUAL, onboarding do agente externo, mapa 09 e 13, nota da política e comentários dos scripts do MCP passam a falar em codebase-memory-mcp / ferramenta `codigo` / `codigo_consultar`, sem apresentar o backend anterior como ferramenta atual.
- **Ressalva registrada (ordem do José):** se `GitNexus` for chamado acidentalmente nesta aplicação ou na documentação, leia-se **codebase-memory-mcp** (backend atual do `codigo` do pqbr-mcp). A ressalva está em ARQUITETURA §12, ROADMAP, ESTADO-ATUAL, onboarding do agente externo, mapa 13, nota da política (`gitnexus_consultar` → `codigo_consultar`) e docstring do adaptador. O backend anterior permanece apenas no histórico (CHANGELOG, DECISOES-LOG, ADR-012, plano) e em `_obsoleto/`, sem desinstalar até ordem expressa.

## [0.29.5] — 2026-10-29 (migração GitNexus → codebase-memory-mcp, OK José)
### Alterado
- Backend do `codigo` do pqbr-mcp trocado do GitNexus 1.6.12 (PolyForm Noncommercial) para o codebase-memory-mcp **0.12.1** (MIT, release GitHub 2026-10-16, SHA-256 conferido). Interface do `codigo` inalterada (`query|context|impact`, filtrada pelo papel, fail-closed). Adaptador novo: `src/pqbr/integrations/codebase_memory.py`.
- Política 1.5.0 → **1.6.0**: ferramenta `gitnexus_consultar` renomeada para `codigo_consultar` (dev e mantenedor). `query_graph`/`cypher` continuam bloqueados.
- Contrato `FerramentaVigiada` 1.0.0 → **1.1.0** (campo opcional novo `binario`); vigia de sexta 08:00 passa a vigiar o codebase-memory-mcp (versão instalada via `--version`, última via GitHub releases, mesmo `classificar`; nunca aplica, nunca dispara o Schedule à mão).
- Scripts: `scripts/codebase-memory/verificar.sh` (fail-closed, Lens desligada) e `hook-post-commit.sh` (reindex em segundo plano; o `auto_watch` do CBM só vale na sessão dona, por isso o post-commit é o mecanismo durável de frescor). `.githooks/post-commit` aponta para o novo hook.
- Mapa: `05-vigia-atualizacoes` (entrada CBM + leitura por binário), `13-memoria-mcp-handoff` (subgrafo CBM) e `00-visao-geral` (nó K13) atualizados; `index.html` regenerado.
### Preservado (nada apagado, sem desinstalar)
- GitNexus: wrapper em `~/.local/bin/_obsoleto/gitnexus`, índice de 215 MB em `~/.local/share/_obsoleto/gitnexus-pqbr-1.6.12/.gitnexus/`, código em `scripts/_obsoleto/`, índice em `docs/_obsoleto/INDICE-migracao-cbm.md`. Pacote npm e registry global intactos. Desinstalação só com ordem expressa posterior.
### Gaps documentados (ADR-012)
- Saída não é byte-idêntica (comparação semântica no Passo 4); processos e classificação de risco do GitNexus sem equivalente (risco devolvido como `sem_equivalente`, sem escore emulado); `wiki` sem equivalente (não era usado); parse parcial de SQL no índice CBM (28 arquivos parciais, 6 inutilizáveis — ler o SQL direto); chamadas por string (ex.: atividades Temporal) não geram aresta em nenhum dos dois índices; `indexed_at` do CBM não atualiza em reindex em segundo plano (frescor se verifica buscando um símbolo novo).
### Verificação (Passo 4)
- Mesmas consultas nos dois lados (lado GitNexus = linha de base do Passo 1, pois o índice foi preservado fora do repo): `query`/`context`/`impact` para `vigia_checar` e `VigiaAtualizacoesWorkflow` equivalentes ou mais ricos no CBM (callees de `vigia_checar`: `_get_json`, `classificar` nos dois, mais `_versao_binario`, `ItemAtualizacao`, `_num`, `int` no CBM); `consultar` sem desambiguador devolve ambiguidade explícita nos dois lados (12 sugestões no CBM, incluindo o novo `codebase_memory.consultar`); papel `auditor`/desconhecido negado, `cypher`/`query_graph` bloqueados.
- `detect_changes --base-branch HEAD`: exatamente os 17 arquivos da migração, nem mais nem menos.
- Vigia: `vigia_checar` para o CBM devolve instalada `0.12.1`, última `v0.12.1`, `em_dia`.
- Suíte completa: 686 passados, 2 falhas pré-existentes em `test_flow_projeto.py` (EP1003), reproduzidas no HEAD limpo sem a migração — não são regressão.


Versionamento SemVer (MAJOR.MINOR.PATCH) a partir de t510. Versão do pacote canônico/contrato segue o próprio hash.




## 0.29.1 — 2026-10-29 (t161u)
- Projeto Google Flow `PQBR-EP1003-cafe-fraco` (`025dcfef-…`) + fichas PERS/OBJ/AMB entregues; storyboard **não** enviado (HOLD prompt-padrão).
- `config/flow_projetos.json` + gate `src/pqbr/pipeline/flow_projeto.py` (fail-closed antes de cenas).
- Playbook Flow: receita de upload Angular ajustada (click + `input[type=file]`).
- Docs: REGRAS, DECISOES-LOG, ESTADO-ATUAL, LACUNAS, PLANO-CENAS EP1003.

## [0.29.4] — 2026-10-29 (t164u)
### Handoff
- ESTADO-ATUAL: seção **Onde paramos / handoff (t164u)** com instruções ao novo agente (BRIEFING, processos/flow, flow_projetos, Camofox PQBR, gates).
- ROADMAP: subseção Piloto EP1003 (checkboxes feito/pendente: stills, capa Character, Cenas, MG-05/11/12, JEV-02, merge, MCP estado).
- Mapa :8088 (aba Roadmap) regenerado. Sem ações Flow.

## [0.29.3] — 2026-10-29 (t163u)
### Flow EP1003 v2
- Novo projeto `PQBR-EP1003-cafe-fraco-v2` (`3a9ca558-…`); antigo `025dcfef-…` intacto.
- Agent Confirm=Sempre, 9:16, Nano Banana Pro; Character `@PERS-menina-rosa`; Collections Referencias/Storyboard/Cenas/Finais.
- Storyboard conciso c01..c08 enviado 1× (0 créditos) → resposta Agente OK; `storyboard_ok=true`. STOP sem stills/clipes.

## [0.29.0] — 2026-10-29
### Adicionado
- Processo canônico de criação (t160u / José t149u): `docs/processos/CRIACAO-README.md` v1.0.0, playbook `flow.md`, stubs Vids/Vibes (`a descobrir`).
- Pré-condição Temporal fail-closed: `processo_criacao_conferir` + `src/pqbr/pipeline/processo_criacao.py` (versão pinada + hash); testes unitários.
### Alterado
- REGRAS §6: processo de produção por episódio **APROVADO** (deixa de ser PROPOSTA t159u); ponteiros em ARQUITETURA e personas.
- ESTADO-ATUAL / ROADMAP / LACUNAS / mapa (`01-episodio`, `07-cadeia-video`).
### Notas
- Reinício do `pqbr-episodio-worker` **não** feito (ativação da activity em runtime pendente de OK do José).

## [0.28.1] — 2026-10-29
### Adicionado
- Registro do teste do combo `core-ultra` no 9router (t158u): HTTP 200 (~3,4 s), modelo `claude-opus-5-5-medium`; `core-ulta` → 404; stream sem pedido; uso estimado ~2035 tokens de entrada (`estimated: true`).
- Storyboard 1.3.0 offline do piloto EP1003 cafe-fraco (MG-05), fora do worker (`runtime/piloto-flow/EP1003/`).
- Produção Flow EP1003: elementos anexados; **S01..S08** geradas (Nano Banana Pro, 0 créditos) via Camofox PQBR; `imagens_revisadas` ainda false; sem vídeo Omni/Veo.
### Alterado
- MG-12: combo `core-ultra` **criado e testado**; troca de `motion` em `config/modelos_9router.json` + reinício do worker continuam no portão do José (não feitos).
- ESTADO-ATUAL P18/próximo passo: pendência restante = OK José para troca+reinício; produção Flow do EP1003: S01..S08 geradas (elenco feminino / menina-rosa); falta revisão José + vídeo/motion.

## [0.28.0] — 2026-10-29
### Adicionado
- Aprovação em massa das fichas do catálogo visual e das REF-MG (t155u): `banco-fichas/indice.json` 3.1.0 (30 fichas → `permanente`; 11 SIT-* seguem `sugestao`); `referencias-motion/indice.json` 0.4.0 (REF-MG-00..07 → `aprovada`).
- ROADMAP MG-11 (lote de refação EP1002–EP1010 sem Higgsfield) e MG-12 (`core-ultra` / Opus 5.5 para o papel `motion`, proposta).
### Alterado
- P17: `Instruções para o agente` no Google Flow regravadas no estilo cartoon 2D flat colorido; espelho Drive `00_Biblia_Visual/banco-fichas` com 111 arquivos (t155u).
- Higgsfield marcado como descartado (t156u); vídeos do `runtime/lote-saldo/` obsoletos para publicação; ordem Flow → MG-05 → lote de refação.
- ESTADO-ATUAL / REGRAS / fases: P16 regra e fichas aprovadas; P17 parcialmente concluída (faltam folha do nº 1, mídia das SIT-*, OK reinício worker storyboard 1.3.0).

## [0.27.1] — 2026-10-28
### Corrigido
- Escrita do `pqbr-mcp` no Hindsight deixou de estourar timeout e de duplicar memória (t154u): `storage/hindsight.reter` aceita `operacao_id` e envia `async: true` + `operation_id` determinístico (`id_da_operacao`, `uuid5` de cliente + commit + conteúdo), então reenviar a mesma alteração devolve a operação original; `mcp/escrita.py` usa ids próprios para o conteúdo e para o handoff e traduz `TimeoutError` em mensagem com orientação de retry; o timeout do POST virou `PQBR_HINDSIGHT_TIMEOUT` (padrão 120 s, antes 30 s fixos).
- `mcp/servidor.py`: o erro genérico de ferramenta passou a incluir a mensagem (`erro: Tipo: mensagem`), não só o nome do tipo.
- Testes: `tests/unit/test_mcp_escrita.py` cobre o id determinístico, o payload assíncrono e o reenvio sem duplicar; o caminho síncrono sem `operacao_id` continua igual.

## [0.27.0] — 2026-10-28
### Adicionado
- Motion, seis peças novas (MG-10 parcial, t153u): `frase-troca`, `marca-texto`, `numero-conta`, `leque`, `elo-causa` e `transicao-pincelada` em `src/pqbr/pos/motion/catalogo/`; catálogo `indice.json` 1.2.0 com parâmetros travados e `fragmento_de` no `destaque`; `contratos/motion.py` passou a validar que o `destaque` é trecho literal de `texto`.
- Coletânea de referências: REF-MG-02 a REF-MG-07 em `banco-fichas/referencias-motion/` (link, data, medida, gramática observada, o que entra e o que fica de fora), README com a tabela referência → peças e `indice.json` 0.3.0 com o campo `delegacao_escolha`; prova em `provas/mg10-pecas.png`.
- Testes: casos novos em `tests/unit/test_motion_contrato.py` (catálogo novo e destaque-trecho) e `tests/unit/test_motion_motor.py` (zona segura e desenho das seis peças). Suíte: 672 passed, 73 skipped, 2 xfailed.
### Alterado
- REGRAS §26: "Quem escolhe o movimento" (delegação do José em t153u, o OK dele é sobre a regra e as fichas), estado do vocabulário (seis peças no catálogo, riscado como candidato) e a coletânea com a escolha determinística por episódio.
- `docs/fases/motion-graphics.md` (Fase 2d com método, peças e recusas), ROADMAP (MG-02, MG-04, MG-10 e o portão da Fase MG), `biblioteca/regras.md`, `biblioteca/historico.md` (autocrítica 7 → 8,5), persona `motion` (regras 10 e 11) e ESTADO-ATUAL (0.27.0).

## [0.26.0] — 2026-10-28
### Removido
- `runtime/piloto-motion/cafe-fraco/` (327 MB, fora do git): piloto de t145u com o visual reprovado, deletado por ordem do José (t152u). Originais do EP1003 intactos em `runtime/lote-saldo/cafe-fraco/`. Referências vivas nos docs ajustadas.
### Alterado
- Cartão do MG-03 aprovado pelo José (`runtime/piloto-motion/mg03/folha-cartoes-v2.png`) como ponto de partida; piloto 2 (MG-05) aguarda o Flow em operação regular.

## [0.25.0] — 2026-10-28
### Alterado
- MG-03 (t151u): cartões do catálogo de motion no traço do stickman (`g.cartao`: contorno preto e sombra chapada) em `versus`, `origem-pino`, `recorte-aponta` e `imagem-cena`; peso 800 → 700 em `titulo-expressao`, `origem-pino` e `versus` (teto da Fredoka). Custo medido: 35–43 ms por quadro.
- Testes: `test_motion_motor.py` confere o teto de peso do catálogo e o uso do cartão.

## [0.24.0] — 2026-10-28
### Adicionado
- Catálogo visual aberto (t150u): contrato `FichaCatalogo` 1.0.0 (`src/pqbr/contratos/catalogo_visual.py`, com `PROTAGONISTAS` e `TAMANHO_MAX_IMAGEM` de 2 MB) e `src/pqbr/pipeline/banco_fichas.py` (buscar, registrar, anexar mídia, adicionar recorte, aprovar, descartar, gerar o `.md`, resumo para prompt, CLI). `banco-fichas/indice.json` 3.0.0 (62 fichas): categoria nova de situações (`SIT-*`, 11 sugestões sem mídia), `PERS-menino-azul` (nº 1, protagonista masculino) e 6 derivadas do elenco (`aguardando_ok_jose`), uma ficha por objeto (12) e por animal (12), modelos `figura`, `animal` e `situacao`.
- Motion, personagem presente no layout (MG-09): peça `catalogo/personagem-moldura.js`, `PlanoMotion` 1.2.0 (`elenco` `masculino`/`feminino`, tipos de parâmetro `personagem` e `pose`, faixa numérica), `render.quadros()` (prévia sem compor) e `catalogo/indice.json` 1.1.0. O render acusa o personagem que cobre texto ou cartão.
- Coletânea de motion: `REF-MG-01` (vocabulário de movimento do dossiê whatships, MiniMax H3 MAX e 0xMovez, `aguardando_ok_jose`) e `referencias-motion/indice.json` 0.2.0. Fase MG do ROADMAP ganha MG-09 (feito no código) e MG-10 (peças do dossiê).
- Testes: `tests/unit/test_catalogo_visual.py`, `tests/unit/test_banco_fichas_pipeline.py` e casos novos nos de banco-fichas, motion (incluindo render real), storyboard e pacote. Suíte: 668 passed, 73 skipped, 2 xfailed.
### Alterado
- Estilo nas palavras do José: cartoon 2D, flat, colorido, com personagens stickman (REGRAS §5/§6/§25/§26, CONTRATO-EDITORIAL §18/§19, `config/estilo_visual.json`, `ESTILO_PADRAO_STICKMAN`).
- Protagonistas definidos (nº 1 masculino, nº 2 feminina) e `PERS-bob-oculos` como nº 13. Correções nas fichas: sapato da `PERS-menina-rosa` (brancos ovais, não vermelhos) e cachecol do nº 3 (cinza, poucos fios de cabelo).
- Storyboard 1.3.0 (`refs` com ids do catálogo, coadjuvante qualquer `PERS-*`), pacote canônico com o item `catalogo_visual`, `templates/notebooklm/*` e `templates/auditor/VISUAL_2D.txt`. O prompt novo só vale no episódio depois do reinício do `pqbr-episodio-worker`, que exige OK do José (não feito).
- Motion: `catalogo.PALETA` e `CORES` do motor re-basiadas no flat colorido (masculino azul-aço, feminino rosa, fundo creme claro); `titulo-expressao` e `versus` usam o tom escuro para letra colorida; persona `motion` com as regras 9 e 10; REF-MG-00 e README da coletânea re-basiados.
- Docs: `docs/fases/stickman.md` e `docs/fases/motion-graphics.md` (personagem presente, vocabulário do dossiê), ROADMAP (MG-03 parcial, MG-09, MG-10), LACUNAS (item 5), mapa (`12-storyboard-elenco`, `01-episodio`, `07-cadeia-video` e README, sem consulta específica ao José, como em t148u) e ESTADO-ATUAL (P5, P6, P16, P17).

## [0.23.0] — 2026-10-28
### Adicionado
- Banco de fontes do motion (t149u): `src/pqbr/pos/motion/fontes.py` (leitor sfnt em Python puro, cobertura pt-BR, registro com licença livre e índice atômico, CLI) e `banco-fichas/referencias-motion/fontes/` com `baloo-2`, `fredoka`, `shantell-sans` e `short-stack` (OFL-1.1, nomes canônicos `<id>/<id>.ttf` e `LICENSE.txt`), todas aprovadas pelo José em 28/10/2026. Patrick Hand ficou de fora (licença traz e-mail pessoal do autor).
- `PlanoMotion` 1.1.0: campo `fonte` (id do banco, só fonte aprovada; padrão `fredoka`, fonte do padrão do canal por decisão do José). `render.py` injeta o `@font-face` por arquivo local (`file://`, nunca CDN) e confere que a fonte carregou antes de desenhar; `motor.js` usa `PQBRMotion.FONTE`.
- Testes: `tests/unit/test_motion_fontes.py` e casos novos em `test_motion_contrato.py` e `test_motion_render.py`.
### Removido
- `banco-fichas/referencias-canal/` (frames antigos do canal, obsoletos por ordem do José).

## [0.22.0] — 2026-10-28
### Adicionado
- Padrão visual definitivo do canal (t148u): conjunto de 20 imagens selecionadas pelo José no Drive (`Fontes/Imagens`) versionado em `banco-fichas/` — catálogo do elenco com 12 personagens (`personagens/ELENCO-catalogo.png`), 6 folhas individuais multi-pose (`PERS-menina-rosa`, `PERS-cacheada`, `PERS-bone-verde`, `PERS-gravata-azul`, `PERS-roxo-ansioso`, `PERS-bob-oculos`), 11 ambientes 16:9 (`ambientes/AMB-*.png`), catálogo de 12 objetos (`objetos/OBJ-catalogo.png`) e de 12 animais domésticos (`animais/ANIM-catalogo.png`, pasta nova). 20 fichas Markdown novas e `banco-fichas/indice.json` 2.0.0 (estado `permanente`, decisão t148u, origem Drive; `referencias-canal/` marcada como histórico).
- Testes `tests/unit/test_banco_fichas.py` (índice × arquivos, contagens 7 pers/11 amb/1 obj/1 anim, ausência das fichas antigas e do gerador aposentado, folhas em paisagem).
### Alterado
- Estilo canônico reescrito para o cartum 2D flat colorido do conjunto t148u: `docs/REGRAS.md` §5/§6/§26, `docs/CONTRATO-EDITORIAL.md` §19, `config/estilo_visual.json`, `ESTILO_PADRAO_STICKMAN` e `BlocoVisual` 3.0.0 (`src/pqbr/contratos/__init__.py`), `docs/fases/stickman.md`, `docs/fases/motion-graphics.md`, `company/agents/motion/AGENTS.md` e mapa `docs/mapa/12-storyboard-elenco.mmd`.
- Motion graphics: a âncora visual do catálogo v2 (MG-03) deixa de ser o nanquim de t146u e passa a ser o conjunto flat colorido t148u; paleta do motor, persona `motion` e `PlanoMotion.elenco` (PERS-M/PERS-F aposentados) entram no re-base do MG-03 (ROADMAP Fase MG).
- Pacote de onboarding: `LIMITE_ESTADO` sobe de 12000 para 20000 caracteres (`src/pqbr/mcp/onboarding.py`) porque o `ESTADO-ATUAL` passou de 13,4k com a P17 e a linha P15 era cortada; `AGENTS.md` regenerado (`scripts/mcp/gerar_agents_md.py`).
### Removido
- As 12 fichas permanentes nanquim de t146u (reprovadas pelo José) e o `ELENCO-frente.*` saem do `banco-fichas/`; o gerador programático `scripts/visual/frente_stickman.py` é aposentado em `scripts/aposentado/` e `tests/unit/test_frente_stickman.py` removido. Os IDs `PERS-M`, `PERS-F` e `PERS-M-classico` deixam de existir; os protagonistas por gênero aguardam o José (P17).

## [0.21.0] — 2026-10-28
### Adicionado
- Motion graphics no pós (REGRAS §26, t145u): `src/pqbr/pos/motion/` com `motor.js` (quadro = função pura do tempo, molas fechadas, ruído com semente, zona segura 9:16), catálogo inicial de 8 modelos (`transicao-cortina`, `titulo-expressao`, `linha-tempo`, `origem-pino`, `versus`, `recorte-aponta`, `barra-progresso`, `imagem-cena`), `render.py` (Playwright + Chrome do sistema, PNG por quadro, checagem de determinismo e de zona), `compor.py` (FFmpeg troca o trecho do porquê, aplica a camada sobre, copia a narração; folha de contato e teste a 360 px), `cli.py` e `biblioteca/regras.md`.
- Contrato `PlanoMotion` 1.0.0 (`src/pqbr/contratos/motion.py`): texto na tela só do bloco de números travados, cores só da paleta do elenco e da marca, bloco nunca na última cena nem sobre o gancho, transição padrão obrigatória, peças presas ao catálogo.
- Nono papel-agente `motion` (`company/agents/motion/AGENTS.md`, `REGISTRO`, `modelos_9router.json` → `core-alto`, `politica_papeis.json` 1.5.0, `mcp_kit.PAPEIS`). Sem activity no worker ainda.
- Testes `tests/unit/test_motion_contrato.py`, `test_motion_motor.py` (Node) e `test_motion_render.py` (Chrome, curto).
- `playwright==1.64.1` no venv, sem baixar Chromium.
- Coletânea de referências de motion (t147u): `banco-fichas/referencias-motion/` (README, `indice.json` 0.1.0, ficha REF-MG-00 "Papel e nanquim do canal", `aguardando_ok_jose`) e `docs/fases/motion-graphics.md` (base visual, variáveis de lista fechada, escolha determinística por categoria + semente do episódio, fases de trabalho e riscos). Documentadas as três fontes de referências: a biblioteca do próprio canal (âncora), o material de estudo de t145u e a pesquisa externa de MG-02 com OK do José por referência.
### Alterado
- CONTRATO-EDITORIAL §16.4 (substitui t435: o pós pode colocar motion graphics) e §12 (partitura com bloco de motion). BLUEPRINT §10 ganha o bloco na montagem. `docs/AGENTES.md`, `docs/ARQUITETURA.md`, `docs/README.md` e REGRAS §0/§3.x passam de 8 para 9 papéis.
- Piloto em `runtime/piloto-motion/cafe-fraco/` (fora do git): bloco 14,87–33,5 s sobre o EP1003, original intacto, áudio idêntico. O José reprovou o visual (t147u: vídeo base obsoleto, cartum 2D aposentado) e manteve a ideia; o piloto passa a valer só como prova da mecânica.
- Direção visual do motion (t147u, REGRAS §26): o bloco é desenhado na mesma folha do stickman (papel creme `#f5f0e4`, nanquim, hachura, tipografia manuscrita única OFL a escolher); um padrão fixo com variações sutis de lista fechada, por tipo de conteúdo e semente do episódio. ROADMAP ganha a Fase MG (MG-01 a MG-08: coletânea, referências externas, catálogo v2 no traço do canal, variação determinística, piloto 2 com cenas do Flow, bloco de números no storyboard, activity `pos_motion` no worker, finalização e entrada do logotipo — propostas A/B/C aguardando a escolha do José).
## [0.20.0] — 2026-10-28
### Adicionado
- Referências reais do canal Porquê BR preservadas em `banco-fichas/referencias-canal/` (`ref-01..05` + `ref-canal-composta-sem-texto.png`) e ficha permanente do stickman clássico sem óculos (`PERS-M-classico.png`, `PERS-M-classico-folha.png`, `PERS-M-classico.md`) (t146u).
- Pesquisa e validação empírica em `docs/pesquisas/flow-agente-e-nano-banana-pro-20261028.md`: avaliação do Agente do Google Flow na produção de vídeo, configuração real do Agente (`Confirmar antes de gerar = Sempre`, `9:16`, `x1`, `🍌 Nano Banana Pro`, `Instruções para o agente`) e receita determinística para upload de imagens em Angular Material (`.sidebar-upload-btn`) via Camofox (t146u).
### Alterado
- **Regra canônica das fichas permanentes (`docs/REGRAS.md` §5/§6, `docs/CONTRATO-EDITORIAL.md` §19, `docs/fases/stickman.md`):** para personagens, objetos e locais permanentes (`banco-fichas/`), as fichas são permanentes e geradas no Google Flow com o modelo mais potente de geração de imagens (`🍌 Nano Banana Pro`, 0 créditos), padronizadas pelo traço real do canal (nanquim preto + hachura sobre papel creme `#f5f0e4`, dois olhos expressivos sempre visíveis, mãos estilo luva branca, pés pretos ovais) (t146u).
- Todas as 12 fichas permanentes de `banco-fichas/` (`PERS-M`, `PERS-M-folha`, `PERS-F`, `PERS-F-folha`, `PERS-M-classico`, `PERS-M-classico-folha`, `AMB-cozinha`, `AMB-sala`, `OBJ-chaleira`, `OBJ-xicara`, `OBJ-filtro-pano`, `OBJ-controle-remoto`) regeneradas ao vivo no Google Flow com `🍌 Nano Banana Pro` e inspecionadas visualmente (`banco-fichas/indice.json` v1.0.0) (t146u).

## [0.19.0] — 2026-10-28
### Adicionado
- Funções de decisão estruturada do Jev (`src/pqbr/motores/decisao.py`): `jev_disponivel`, `classificar_popup_camofox`, `escolher_ref_canario` (`EscolhaRefCanario`), `triagem_correcao_jev`, `verificar_correcao_jev`, `decidir_repeticao_jev` e `classificar_email_youtube` (t144u).
- Ligação do Jev em `CorrecaoAutonomaWorkflow` (`triagem_jev` e `verificar_jev`, `src/pqbr/workflows/correcao.py`) e na checagem semântica de repetição R10 (`checar_repeticao`, `src/pqbr/pipeline/grade.py`).
- Folhas completas de personagens (`PERS-M-folha.png`/`.svg`, `PERS-F-folha.png`/`.svg`, 1920×1080 com frente, perfil e 4 expressões de boca fechada), recortes 9:16 com roupa 2D chapada fixa (`PERS-M.png`, `PERS-F.png`), ambientes (`AMB-cozinha.png`, `AMB-sala.png`) e objetos (`OBJ-chaleira.png`, `OBJ-xicara.png`, `OBJ-filtro-pano.png`, `OBJ-controle-remoto.png`) gerados por `scripts/visual/frente_stickman.py` (t144u).
### Alterado
- Limiares de confiança calibrados empiricamente na API real TypeSafe (`jev-latest`, 12 casos canônicos, 100% de acerto) em `config/motores.json`: `0.9` para pop-up, canário e triagem; `0.85` para repetição; `0.8` para verificação e e-mail YouTube. Workers `pqbr-temporal-worker`, `pqbr-episodio-worker` e `pqbr-mcp` reiniciados com `TYPESAFE_API_KEY` ativa (t144u).
- `banco-fichas/indice.json` (v0.4.0) e fichas Markdown atualizados para `aguardando_ok_jose` com as cores chapadas e caminhos dos PNG/SVG.

## [0.18.0] — 2026-10-28
### Adicionado
- Porta `decide()` do Jev (`src/pqbr/motores/decisao.py`): adaptador TypeSafe (`systemone`, `jev-latest`), fallback OpenRouter desligado, limiar de confiança por contrato e registro de cada chamada em `pqbr.consumo_modelos`. Sem uso em workflow ainda (JEV-EF, t143u).
### Alterado
- A activity `registrar_consumo` grava pela função compartilhada `storage/consumo.py`. O SQL é o mesmo.
### Corrigido
- O pacote de onboarding (AGENTS.md) cortava o ESTADO-ATUAL em 6000 caracteres e perdia as últimas pendências (P14 e P15). O limite do ESTADO passa a 8000, com teste de regressão (t143u).

## [0.17.9] — 2026-10-28
### Alterado
- Documentos, mapa e memória alinhados para retomar depois (t142u). O mapa do elenco mostra o stickman e a roupa ainda sem cor. A memória do bloco visual deixa de mandar o cartum de 12/10.

## [0.17.8] — 2026-10-28
### Alterado
- O material de stickman fica como inspiração do desenho e do prompt (t141u). NotebookLM, Flow e o resto da arquitetura permanecem. O comando do storyboard pede o frame de início, a frase-trava e o movimento do corpo. A cor da roupa continua em aberto.

## [0.17.7] — 2026-10-28
### Alterado
- José recusou o stickman sem roupa (t140u). Os PNG de 27/10 deixam de ser referência. O estilo passa a cabeça branca, membros de palito, uma roupa chapada fixa e cara de reação. A cor da roupa continua em aberto. Não gerar o personagem até a folha nova.

## [0.17.6] — 2026-10-27
### Alterado
- Corpo do elenco fechado (t139u). Sem roupa. Tubo preto, cabeça branca. PERS-M: óculos vermelhos, sem cabelo, mais alto. PERS-F: mais baixa, coque, argola amarela e pinta do lado esquerdo de quem olha. Desenho em `banco-fichas/personagens/`, regravado por `scripts/visual/frente_stickman.py`. Não é geração do Flow. A aba Personagens não recebeu esses arquivos.

## [0.17.5] — 2026-10-27
### Operação
- Frente do personagem masculino no Flow, pela aba Personagens, com manifesto gravado antes (t138u). A imagem saiu pessoa com volume, 1376×768. Não virou asset. O prompt não se repete.

## [0.17.4] — 2026-10-27
### Documentação
- Juntada da conversa paralela, renumerada porque t133u/0.17.3 já são o stickman. t134u: ferramentas só leitura para os agentes, sem MCP interno. t135u: acompanhamento de mudanças sem agente novo. t136u: José aprovou sem agente novo; o NotebookLM é só CLI e sai do canário. t137u: Jev efetivo como item prioritário JEV-EF. Nenhum código destas propostas foi alterado; o stickman e o banco de fichas ficam como estão.

## [0.17.3] — 2026-10-27
### Alterado
- Stickman passa a ser a identidade única (t133u). O bloco de cartum genérico sai do contrato vigente. `BlocoVisual` 2.0.0 exige a palavra stickman e recusa 3D.
- Banco de fichas em texto: `banco-fichas/` (dois personagens, cozinha, sala, quatro objetos). Sem imagem. Espelho no Drive `00_Biblia_Visual/banco-fichas` (`config/drive_pastas.json`, chave `banco_fichas`).
- O roteiro e o storyboard recebem o estilo stickman. Roupa nova por episódio fica pausada até a imagem de referência.

## [0.17.2] — 2026-10-27
### Operação
- Duas imagens estáticas no Google Flow, pelo Camofox, modelo Nano Banana 2 Lite, 9:16 (t132u). A ficha não mostrou crédito. As duas saíram cartum de pessoa, não stickman. Vídeo não foi gerado. Baixado só o 1K original.
- `config/mapa_cliques.json` ganhou três surpresas dessa tela: o diálogo "O que há de novo", o menu 2K/4K e a confirmação que não apareceu.

## [0.17.1] — 2026-10-27
### Alterado
- A silhueta do mapa do Brasil no logo não bloqueia gerar nem subir. O aviso sai antes de tornar público (t131u).
- Imagem no Google Flow está autorizada, sem teto. Vídeo gasta o saldo do Flow e depois cai no Google Vids e no Meta Vibes.
- `config/mapa_cliques.json` deixa de ser catálogo. A tela do Camofox manda; o arquivo só anota surpresa.

## [0.17.0] — 2026-10-27
### Alterado
- O episódio para no storyboard. `storyboard_criar` grava a ficha (Storyboard 1.2.0) com `imagens_revisadas` false. Não gera imagem nem vídeo (t130u).
- O NotebookLM deixa de gerar vídeo. `tipo=short` faz roteiro, compliance e SEO no chat. `nlm_gerar_short` recusa antes do CLI.
- Contrato de gasto por etapa (`src/pqbr/contratos/gasto.py`): diz se pode gastar, o modelo e o meio. Vídeo e infográfico do NotebookLM estão negados.
- `paperclipai.service` parado e desabilitado, sem desinstalar. `config/paperclip.json` em `parado_proposital`.
- `pqbr-episodio-worker` e `pqbr-notebooklm-worker` reiniciados às 11:27 (-03), com 0 workflows em execução. `YOUTUBE_DRY_RUN=true`. Nada enviado.

## [0.16.10] — 2026-10-27
### Corrigido
- Lacunas: sai o que o código já faz ou o que era ponte do Paperclip. Ficam auditor no episódio, pacote só de roteiro, códigos do lote 2510, Fase 4V, storyboard, porta do navegador sem uso, cliques do Studio e o teste de LOOP adiado (t129u).
- Documentos que não são regra, decisão, contrato, mapa nem diagrama vigente foram para `docs/_obsoleto/`, sem apagar.

## [0.16.9] — 2026-10-27
### Operação
- `pqbr-episodio-worker` e `pqbr-mcp` reiniciados às 08:56 (-03) com OK do José (t128u). O processo do worker carrega t124u–t126u. O handshake do MCP devolve a frase de honestidade. `YOUTUBE_DRY_RUN=true`. Nada enviado.
- Apagadas as 7 memórias `obsoleto_candidato` do roster antigo de `docs/AGENTES.md`. Bank de 884 para 877. Backup fora do git.

## [0.16.8] — 2026-10-27
### Corrigido
- Diagrama 11: o worker está no ar desde 26/10 22:06 (Fortaleza), a migração 0020 já foi aplicada e as chaves do YouTube já estão no processo. O código de t124u–t126u entra no próximo reinício.

## [0.16.7] — 2026-10-26
### Adicionado
- Honestidade como regra comum (t126u), no onboarding e na instrução do MCP: dizer o que foi visto, e questionar ideia que não se sustenta ou só aumenta o sistema.
- Registro de cliques `config/mapa_cliques.json`, vazio: elemento só entra com a data da tela. Pop-up e botão fora do lugar atualizam o registro e o processo segue.

## [0.16.6] — 2026-10-26
### Adicionado
- Ensaio de cliques do fallback de publicação, em memória, sobre o corpo da API (t125u, base 0.1.0). Pode estar desatualizado. Não abre o Studio e não envia.

## [0.16.5] — 2026-10-26
### Adicionado
- Publicação: se o refresh de 7 dias for recusado (`invalid_grant`), o envio inteiro passa ao Studio pelo Camofox (t124u). O roteiro de cliques ainda é hipótese: grava o plano, avisa e não envia. Nada publicado.

## [0.16.4] — 2026-10-26
### Operação
- `pqbr-episodio-worker` reiniciado às 22:06 (Fortaleza) com OK do José (t123u). Chaves do YouTube no processo; `YOUTUBE_DRY_RUN=true`. Nada publicado.

## [0.16.3] — 2026-10-26
### Operação
- OAuth do YouTube no projeto `pqbr-publicacao` (app Externo PQBR, em teste; cliente Desktop). Chaves em `episodio.env` (600). `channels.list` confirmou o canal Porquê BR. Worker não reiniciado; nada publicado.

## [0.16.2] — 2026-10-26
### Alterado
- Aba Roadmap: ☑ em itens feitos, ☐ em falta e próximos passos (só leitura); teste cobre contagens e ausência de elementos editáveis.

## [0.16.1] — 2026-10-26
### Corrigido
- ESTADO-ATUAL P2: removidos passos já feitos (2SV, migração 0020/reinício do worker); aba Roadmap regenerada.

## [0.16.0] — 2026-10-26
### Adicionado
- Aba **Roadmap** no painel do mapa (:8088), só leitura: Próximos passos, Falta, Feito, gerados de ROADMAP + ESTADO-ATUAL (`scripts/mapa/roadmap.py`, testes em `tests/unit/test_mapa_roadmap.py`).
- Pre-commit regenera o `docs/mapa/index.html` quando ROADMAP/ESTADO-ATUAL/mapa mudam.
### Corrigido
- Título da aba 13 do painel ("Memória, MCP e handoff").

## [0.15.1] — 2026-10-26
### Documentação
- Mapa 13: bloco de persistência (units, linger, containers, checagem); 00 e 09: MCP só do mantenedor.
- ROADMAP, AGENTES.md, REGRAS, ARQUITETURA §12, ESTADO-ATUAL e DECISOES-LOG com mantenedor exclusivo, construção de módulos e persistência.

## [0.15.0] — 2026-10-26
### Adicionado
- Política de papéis 1.4.0: `mantenedor` externo lê todas as tags de conteúdo e o repo todo; escreve decisao, incidente, licao, playbook, doc, estado.
- `docs/operacao/onboarding-agente-externo.md` (cliente-agnóstico, inclui construir e ligar módulo novo).
### Alterado
- pqbr-mcp 0.4.0: exclusivo do papel `mantenedor` (token de outro papel recusado; `X-PQBR-Papel` diferente ⇒ 403); `scripts/mcp/novo_cliente.py` só aceita mantenedor.
### Testes
- Mantenedor lê tudo, internos restritos, sem papel sem escrita, MCP recusa outros papéis.

## [0.14.1] — 2026-10-26
### Operação
- Backup `pqbr-20261026-1656.dump` e depois aplicação da migração `0020_pqbr_publicacao_agenda_emergencia.sql` (via `infra/pqbr-db/aplicar.sh`).
- Worker `pqbr-episodio-worker` reiniciado (0 workflows em execução). Carrega `PublicacaoAgendadaWorkflow` e o juiz por etapa.
### Documentação
- Mapa 12: juízes por etapa e os 3 bloqueios do gate VISUAL (antes marcados como proposto).

## [0.14.0] — 2026-10-26
### Adicionado
- Juiz Gemini por etapa: `gemini_juiz` em `config/motores.json` com contrato `pqbr.contratos.juiz_gemini` v1.0.0. Pré-produção usa 3.8 Flash e produção usa 4 Argon (Baixo). A etapa é passada como argumento das activities `auditor_gemini` e `auditor_loop_gemini`, com padrão "producao".
- Gate VISUAL com 3 bloqueios automáticos: `boca_articula_fala`, `corte_oculos_cabeca`, `grotesco`.
- `scripts/lote/loop_comparar_modelo.py` aceita `PQBR_ETAPA` e deixa de exigir o override.
### Nota
- O worker Temporal precisa ser reiniciado (com OK) para aplicar a mudança.

## [0.13.0] — 2026-10-26
### Adicionado
- t105u: override por execução do juiz Gemini (`PQBR_GEMINI_MODELO`, `PQBR_GEMINI_RACIOCINIO`, com confirmação do nível no seletor), `scripts/lote/loop_comparar_modelo.py`, `tests/unit/test_gemini_override.py`; resultado 4 Argon do EP1002 em `loop-gemini-4argon.json`. Padrão 3.8 Flash inalterado.

## [0.12.1] — 2026-10-26
### Alterado
- t101u: mapa 13 (memória, MCP e handoff); 09 e 00 apontam para ele; ARQUITETURA §12 completada.

## [0.12.0] — 2026-10-26
### Adicionado
- t98u/t99u: `docs/ESTADO-ATUAL.md`; `pqbr.governanca.estado_atual` + `scripts/seguranca/verificar_estado_atual.py` no pre-commit; `registrar_alteracao` 1.1.0 (`tipo`, `handoff`, handoff no Hindsight); `tests/unit/test_estado_atual.py`.
### Alterado
- Política 1.3.0 (tag `estado` para todos); onboarding/AGENTS.md começam pelo ESTADO-ATUAL e o protocolo inclui atualizá-lo; MCP 0.3.0; indexador inclui o ESTADO-ATUAL; mapa 09.

## [0.11.1] — 2026-10-26
### Corrigido
- t97u: licença do GitNexus (PolyForm Noncommercial aceita em t90u, uso pessoal, sem revenda) corrigida na ARQUITETURA §12 e no DECISOES-LOG; 3 documentos superados do bank `pqbr` substituídos (backup antes).

## [0.11.0] — 2026-10-26
### Adicionado
- t95u/t96u: ferramentas MCP `registrar_memoria` e `registrar_alteracao` (`pqbr.contratos.memoria_mcp` 1.0.0, `pqbr.mcp.escrita`), autor por cliente do token, commit verificado; `tests/unit/test_mcp_escrita.py`.
### Alterado
- Servidor MCP 0.2.0; onboarding e AGENTS.md com o protocolo obrigatório; `hindsight.reter` aceita `autor`; mapa 09 com a aresta MCP → Hindsight.
- Guia de acesso com nota do MCP (commit do teste de agente do zero).

## [0.10.0] — 2026-10-26
### Adicionado
- t90s398: `pqbr.storage.hindsight_tags` (regra única de tags, usada por `indexar.py` e `reclassificar.py`) + `tests/unit/test_hindsight_tags.py`.
### Alterado
- Política 1.2.0: indexador escreve as tags de conteúdo. ROADMAP/REFERENCIA com Paperclip histórico; AGENTES.md só com os 8 papéis (histórico em `docs/_obsoleto/agentes-equipe-14-t395.md`); `memoria:jev` corrigida. Teste F3-02 do Hindsight atualizado para `papel`/`tags`.
### Removido
- 231 documentos obsoletos do bank `pqbr` (backup antes; ids no doc de candidatos).

## [0.9.0] — 2026-10-26
### Adicionado
- t90u: `scripts/hindsight/reclassificar.py` (tags por papel nos documentos legados do bank `pqbr`, `obsoleto_candidato` reversível, dry-run/idempotente) e `docs/operacao/hindsight-descarte-candidatos.md`.
### Decisão
- Licença PolyForm Noncommercial do GitNexus aceita (uso pessoal).

## [0.8.0] — 2026-10-26
### Adicionado
- t89u: servidor MCP `pqbr-mcp` (`src/pqbr/mcp/`, só leitura, Streamable HTTP em 127.0.0.1:8791, só tailnet via tailscale serve), token por cliente (`scripts/mcp/novo_cliente.py`), `AGENTS.md` gerado do onboarding (base manual movida para `docs/operacao/AGENTS-base.md`), política 1.1.0 com `estado_ler`.

## [0.7.0] — 2026-10-26
### Adicionado
- t84u–t86u: `config/politica_papeis.json` + `pqbr.contratos.politica` (papel desconhecido ⇒ negado); `storage.hindsight.reter` exige `papel`/`tags` e novo `recuperar` filtrado; `integrations/gitnexus.py` filtra por caminho; `scripts/gitnexus/verificar.sh` (pré-requisito fail-closed) e reindex no post-commit. GitNexus 1.6.12 global, fora do repo.

## [0.6.1] — 2026-10-26
### Alterado
- t79u: `Storyboard`/`FichaCena` 1.2.0 com protagonista único e campo `coadjuvante` (outro membro do elenco) com justificativa obrigatória. Ficha feminina: morena, cabelo liso, penteados variados, mais baixa. CONTRATO-EDITORIAL §18.10, REGRAS §25, mapa 12, index regenerado.

## [0.6.0] — 2026-10-26
### Adicionado
- t78u: `FichaCena`/`Storyboard` 1.1.0. Campos `papel_personagem` (observa|participa), `figurino` (epoca_local|atual_variavel), `expressao` (caras e bocas, sem fala), `cenario_encaixe`; `Storyboard.elenco` alternado por `elenco_alternado(codigo)`, com `elenco_excecao`. 15 testes.
- `config/estilo_visual.json` → `elenco` com as fichas masculina e feminina (texto).
- Mapa: `12-storyboard-elenco.mmd`; 01, 07, 09 e 11 atualizados; `scripts/mapa/gerar_index.py` regenera o `index.html`.
### Consolidado do dia
- ROADMAP "Estado em 26/10/2026": Camofox 3 GB, 3.8 Flash com imagens, LOOP e descarte do EP1002, bloqueio 2SV/OAuth, publicação Temporal (publishAt + escopo), auditoria do storyboard, pesquisa Flow e testes pendentes (por cena; 4 Argon).

## [0.5.0] — 2026-10-26
### Adicionado
- t75u–t77u: contrato `contratos/storyboard.py` (`FichaCena`/`Storyboard` 1.0.0), com ficha numerada e rotulada, norte/início/fim, refs `ASSET_*`, "lips closed", proibição de framing descritivo e de fala no prompt, personagem observador ou caracterizado no passado, e vídeo só com imagens revisadas. Testes `test_storyboard.py`.
- CONTRATO-EDITORIAL §18 e REGRAS §25; pesquisa `docs/pesquisas/flow-storyboard-por-cena.md`.
### Alterado
- EP1002 olhos-da-cara descartado (reversível); o tema voltou a `proposto`.
- 0.4.5: publicação agendada com publishAt, escopo por código e registro no worker do episódio. Upload real bloqueado: sem OAuth (2SV pendente).

## [0.4.4] — 2026-10-25
### Alterado
- t546: o juiz Gemini espera `gemini_espera_s` (90 s) desde a última aba fechada e só abre aba nova com o `pqbr-camofox` abaixo de `gemini_mem_abrir_mb` (1400). Se não baixar, levanta `MemoriaAlta` após `gemini_mem_timeout_s` (600 s), com falha fechada. Pranchas: 2 por pedido, 300 px. Uma recusa conta como tentativa falha (1 nova tentativa). A espera do LOOP textual ficou configurável (`gemini_loop_espera_s` = 480 s; com 240 s estourou). Testes `test_gemini_memoria.py`.
- Lote: olhos-da-cara chegou a completar as 2 rodadas VISUAL com o 3.8 Flash (pico de 1848 MB). O LOOP textual estourou 240 s. Na nova execução, a memória passou de 1,9 GB (1990 MB) na 1ª rodada e o lote parou. Gates regenerados: todos em P1_HOLD. Nada publicado.

## [0.4.3] — 2026-10-25
### Alterado
- t545: pranchas do juiz Gemini com 360 px por quadro, todas do mesmo tamanho, compostas em grade (até 4 colunas) com o id de cada cena visível. São N pranchas por pedido (padrão 3), cobrindo todas as cenas. `gemini_prancha_px` e `gemini_pranchas_por_pedido` ficam em `config/motores.json`. Teste `test_gemini_pranchas.py`.
- `loop_lote2510.py`: `persistir=False` (o registro fica em `loop-gemini.json`; sem escrita no banco, que exigia credencial).
- `gate_lote2510.py` agora usa o gate determinístico (`gate_publicacao.avaliar_pasta`) e o `loop-gemini.json`; brigadeiro adiado. `GATE-PRONTO-LOTE.md` regenerado: todos em P1_HOLD (LOOP ausente), porque o lote parou por memória do Camofox (pico de 2057 MB > 1,9 GB) na 2ª rodada VISUAL de olhos-da-cara. Nada publicado.

## [0.4.2] — 2026-10-25
### Adicionado
- t544 (José 22:52): modelo do juiz Gemini (LOOP e VISUAL) fixado por config (`config/motores.json` → `gemini_modelo`, padrão "3.8 Flash"). Antes de CADA envio: abre o seletor pelo rótulo, escolhe, reabre e confere "Selecionado"; senão `ModeloIndisponivel` (falha fechada). Modelo registrado no log e nos resultados (`ResultadoAuditorGemini.modelo`, `ResultadoLoopGemini` 1.1.0 `modelo`). Testes `test_gemini_modelo.py`. Observação: no Camofox a escolha persiste entre abas novas.

## [0.4.1] — 2026-10-25
### Corrigido
- t543: juiz Gemini (`perguntar_gemini`) parava de responder sem aviso. Duas falhas: (1) uma resposta terminada que não era JSON (recusa) só saía depois do prazo inteiro (420 s × até 4 tentativas); (2) o envio não conferia os anexos. Agora: confere `img "attachment"` = n antes de enviar (prazo de 90 s), aborta com `RespostaRecusada` após 3 leituras estáveis sem o JSON, levanta `TimeoutError` no prazo e registra o progresso por etapa no stderr. Tudo com falha fechada.

## [0.4.0] — 2026-10-25
### Adicionado
- F8-01 v2 (t540): `PublicacaoAgendadaWorkflow` — publicação AUTOMÁTICA (sem aprovação humana): gate → reserva 11:40/18:35 America/Fortaleza (1 por janela, idempotente) → upload privado → público na janela → `temas_publicados` + Drive → aviso Telegram (só aviso). Sinal `reverter` (volta para privado, nunca apaga).
- Adaptador `integrations/youtube.py` (Data API v3): sempre `private` + `containsSyntheticMedia=true`, hash sha256, PQBR-EP na descrição/tags, duplicata no banco e no canal. **Simulação por padrão** (real exige `YOUTUBE_DRY_RUN=false` + `PQBR_PUBLICACAO_REAL=1`).
- `pipeline/gate_publicacao.py` (DecisaoGate): técnico, editorial, LOOP Gemini, hash, tema adiado.
- Pedido LOOP do juiz Gemini (`workflows/auditor_loop.py`, contrato `ResultadoLoopGemini` 1.0.0): imagem×fala, capa×título e loop textual, pelo Camofox 9387 humanizado; `perguntar_gemini` aceita pedido sem anexos. `scripts/lote/loop_lote2510.py`.
- Botão de emergência (t541): contrato `contratos/emergencia.py` 1.0.0 (`/pausar`, `/retomar`, `/privar EP|todos`), `ControlePublicacaoWorkflow`, flag global fail-closed, auditoria; entrada do Telegram trata comandos só do `from.id` do José (desligado por padrão: `comandos_emergencia`).
- Migração 0020 (`agenda_publicacao`, `controle_publicacao`, `auditoria_publicacao`) + rollback — testada em Postgres descartável, **não aplicada**.
- Mapa `docs/mapa/11-publicacao.mmd` (agente externo, autorizado) e cobertura no verificador.
### Alterado
- t542: Telegram = manutenção/relatórios/observabilidade, não aprovação de publicação (DECISOES, PLANO da ponte, ROADMAP; trechos movidos para `docs/_obsoleto/telegram-aprovacao-publicacao-t542.md`).
### Corrigido
- 4 testes antigos do Telegram que esperavam a ponte desligada (agora fixam a config por monkeypatch; a real foi ligada na t538-A).

## [0.3.22] — 2026-10-25
### Adicionado
- lote-runway: `MANUS-MODELOS.md` (modelos de vídeo/imagem do Manus, estimativas da comunidade; Seedance 2.0 Fast falhou por confirmação de autoria no modo sem interação). `PRECO-RUNWAY.md` atualizado (gen-4-turbo 29/clipe medido, kling-3 49/clipe).
### Removido
- Encerramento do lote de saldo (José): Runway e Manus descartados para vídeo; volta ao fluxo ordinário (Fase 4V R1). Nada publicado.

## [0.3.21] — 2026-10-25
### Adicionado
- ERR-ROT-02 (roteiro): narração fora da 3ª pessoa / personagem "falando" com a voz da narradora. Seed `db/seeds/seed_catalogo_erros_err_rot_02.sql` aplicado em `pqbr.catalogo_erros`; CATALOGO-ERROS atualizado.
- `pqbr.contratos.roteiro_terceira_pessoa` (validador Pydantic `RoteiroTerceiraPessoa` + `problemas_roteiro`, v1.0.0) com 13 testes em `tests/unit/test_roteiro_terceira_pessoa.py`. Reprova 1ª pessoa do singular, diálogo ou rótulo de fala, e prompts em que o personagem fala, explica ou encara a câmera.
- `scripts/lote/roteiro_lote_runway.py`: fluxo de roteiro fail-closed (versionado; substitui `runtime/lote-runway/consolidar.py`) com ERR-ROT-02 e cobertura por cena.
### Corrigido
- lote-runway, 8 roteiros: personagem só reage (8 trechos de prompt trocados, "Silent reaction only, mouth closed." nos movimentos). Clipes extras sem custo nas cenas curtas: Finados c4d, ENEM c1b, gás c1c, molhar-o-dedo c1c–c4c, panetone c1c. Backups em `roteiro.json.bak-pre-err-rot-02`.
### Removido
- Dia do Saci: Short reprovado e tema descartado (José), movido para `_descartado/` sem apagar; lote Runway suspenso. Nada pago, nada publicado.

## [0.3.20] — 2026-10-25
### Adicionado
- lote-2510: códigos PQBR-EP1002–EP1010; SEO+fontes do NotebookLM (seo.json); juiz Gemini VISUAL via Camofox (juiz-gemini.json); Drive 02_Episodios/2026-10; Postgres temas_pendentes (em_producao); gate rerodado — todos P1_HOLD (LOOP inexistente). Scripts em scripts/lote/. Nada publicado, nada pago.

## [0.3.19] — 2026-10-25
### Corrigido
- lote-2510 ERR-MON-02: CTA personalizado do roteiro restaurado em 6 Shorts (fechadura, formiga, crostinha, brigadeiro, nao-e-bem-assim, olhos-da-cara) → `<tema>-pronto-v2.mp4` (v1 preservados; P1_HOLD; 467,95 créditos ElevenLabs; nada publicado). `scripts/montar_voz_dinamica.py`: recusa CTA genérico por padrão, fades 30 ms, reusa clipes em vez de still. Catálogo: `ERR-MON-02` (seed). Docs: VOZ-DINAMICA-CTA-PADRAO corrigido, CONTRATO-EDITORIAL (CTA preservado na produção), CATALOGO-ERROS, GATE-PRONTO-LOTE, gate-pronto.json.

## [0.3.18] — 2026-10-25
### Adicionado
- lote-2510: pós-produção ordinária (`scripts/pos/post-short.sh`) nos 9 Shorts → `runtime/lote-saldo/<tema>/<tema>-pronto.mp4`; gate fail-closed com `gate-pronto.json` por tema e `docs/pesquisas/lote-2510/GATE-PRONTO-LOTE.md` (todos P1_HOLD); LACUNAS de alocação (sem PQBR-EP). Sem geração paga, sem publicação.

## [0.3.17] — 2026-10-25
### Adicionado
- lote-2510: `scripts/montar_voz_dinamica.py` (remontagem genérica: corpo da voz dinâmica + atempo + CTA padrão fixo `cta-padrao-B.mp3` após 0,3 s; cortes nas pausas via silencedetect; sem quadro congelado, último segmento vira still se faltar clipe; nunca sobrescreve). Nota em `docs/pesquisas/lote-2510/VOZ-DINAMICA-CTA-PADRAO.md`.

## [0.3.16] — 2026-10-25
### Adicionado
- t539: catálogo de erros de produção, com migração 0019, rollback, seed lote-2510 (11 erros), contrato `ErroCatalogo` v1.0.0, leitura por papel com testes, `docs/CATALOGO-ERROS.md`, ARQUITETURA §8 e mapa `10-catalogo-erros` (+ index.html).

## [0.3.15] — 2026-10-25
### Alterado
- t538-A: ponte Telegram ativada (merge local da feature, config ligada, unit `pqbr-telegram-entrada` ativa, drop-in de env no `pqbr-temporal-worker`, job Hermes `pqbr-pedidos-jose` pausado); teste real enviado. DECISOES-LOG, REGRAS §2 e ROADMAP F05-06.

## [0.3.14] — 2026-10-25
### Corrigido
- Banco do PQBR: `0016_pqbr_eventos_acesso.sql` registrada em `public.pqbr_migracoes` sem reexecutar (OK do José). O esquema de `pqbr.eventos_acesso` em produção foi conferido e é idêntico ao gerado pelo arquivo num Postgres descartável (`pg_dump -s`). Agora 0001–0018 estão registradas.

## [0.3.13] — 2026-10-25
### Alterado
- t538: migração 0018 (ponte Telegram) aplicada no banco do PQBR com OK do José, após backup de `pqbr.revisao_humana`; ROADMAP F05-06 atualizado e ideia futura (menu de decisões e pedidos rotineiros no bot) no backlog.

## [0.3.12] — 2026-10-25
### Alterado
- t538 (supera t537): ponte Telegram com bot próprio do PQBR (token e ID do José no `.env`, 600), adaptador determinístico do Temporal; saída por outbox, entrada por long polling; DECISOES-LOG (t537 marcada superada) e REGRAS §2.
- t538-P: princípios do sistema (determinismo máximo + agentes LLM autônomos; manutenção só por agente externo, hoje o "PQBR" Grok Bot do José; agentes internos não se reconfiguram); DECISOES-LOG, REGRAS §3 e BRIEFING (e).

## [0.3.11] — 2026-10-25
### Alterado
- t537: callbacks do Telegram repassados pelo gateway Hermes (perfil `pqbr`), sem bot próprio (DECISOES-LOG + REGRAS §2); desenho e rascunho na branch `feature/f05-06-ponte-duravel`.

## [0.3.10] — 2026-10-25
### Alterado
- t536: t287 ajustada (agente PQBR lê todos os docs; especialistas restritos às suas áreas) em REGRAS §0, ARQUITETURA e ROADMAP; DECISOES-LOG com a entrada t536; ROADMAP F05-09 em duas etapas (Paperclip parado/desabilitado agora, desinstalado só após validar a nova arquitetura).

## [0.3.9] — 2026-10-24
- t533–t535: agente PQBR criado; keepalive do YT-LLM pausado; mapa ganhou o `09-agentes-responsabilidades` e o `03-acessos` foi atualizado (YouTube planejado); BRIEFING atualizado.

## [0.3.8] — 2026-10-24
- t532:
  - keepalive do YT-LLM desligado no box (binário em `_obsoleto`);
  - plano de migração do acesso do YouTube no BRIEFING;
  - análise das legendas puladas;
  - pré-requisito do logo no ROADMAP 4V;
  - proposta da skill de produção em `docs/sdd/`.

## [0.3.7] — 2026-10-24
### Alterado
- t530: exceção de leitura (somente leitura) para `docs/pesquisas/PESQUISA-extensoes-geracao-em-serie.md` nas regras de consulta; pesquisa complementada com achados da conversa YT-LLM (§1.1).

## [0.3.6] — 2026-10-24
### Adicionado
- t529: decisão HOLD + pedido ao José quando Flow, Vids e Meta Vibes falham; pesquisa `docs/pesquisas/PESQUISA-extensoes-geracao-em-serie.md`; ROADMAP Fase 4V (R1–R7); LACUNAS; mapas 07 (storyboard em série + HOLD decidido) e 01 (HOLD/alvo).

## [0.3.5] — 2026-10-24
### Corrigido
- t528: `deploy/camofox/criar_instancia.sh` idempotente (mantém `.env` completo, completa só chaves faltantes sem exibir valores, `--instalar` repetível) com destino alternativo `CAMOFOX_INSTANCIAS_DIR`/`SYSTEMD_DIR`/`SKIP_PORT_CHECK`; teste `tests/unit/test_criar_instancia.py`.

## [0.3.4] — 2026-10-24
### Adicionado
- t526: kit de instância Camofox (`deploy/camofox/`), reserva `config/camofox_instancias.json` (proxima:9397), porta `NavegadorIdentidade` + contratos `InstanciaNavegador`/`SaudeNavegador` 1.0.0 com testes, `docs/RUNBOOK-nova-instancia-camofox.md`. Nada instalado; PQBR segue em 9387.

## [0.3.3] — 2026-10-24 (t525)
- ADR-012 (Camofox: 1 instalação, 1 instância por conta, `NavegadorIdentidade`) registrado; diagnóstico e plano em REFERENCIA-sessao-google §9.
- Camofox global (9377) v1.15.0 → v1.18.1 (fora do repo; 9387 intocada).
- Mapa: `docs/mapa/08-identidade-camofox.mmd`.

## [0.3.2] — 2026-10-24 (t517)
- Meta Vibes restaurado: cadeia de vídeo `flow → google_vids → meta_vibes` (`CADEIA_VIDEO`, `video_fallback`), só navegador; corrige 0.3.1.
- Vigia de atualizações registrado no worker e agendado (sexta 08:00 Fortaleza); relatório em `pqbr.relatorios_atualizacoes` (migração 0017).
- Caderno semanal de temas registrado em `pqbr.cadernos_episodio` (classe `pesquisa`) para o descarte.
- `docs/mapa/`: mapa do sistema em Mermaid + `index.html`.

## [0.3.1] — 2026-10-24 (t516)
- notebooklm-py 0.8.4 → 0.8.5 (venv isolado), pin em `requirements-notebooklm.txt` + `requirements-notebooklm.lock`.
- Sem API Google: docs marcados. (Retirada do Meta Vibes revertida em 0.3.2.)
- Dev: `VigiaAtualizacoesWorkflow` (esqueleto, não registrado/agendado) + contratos `FerramentaVigiada`, `ItemAtualizacao`, `RelatorioAtualizacoes` 1.0.0.
- `mcp_kit.PAPEIS` com os 8 papéis; PROPOSTA-papeis-skills atualizada.
- Testes: 338 passed, 70 skipped, 2 xfailed.

## [0.3.0] — 2026-10-24 (t512–t514)
- **Portas de motor** (`src/pqbr/motores/`, `config/motores.json`): `MotorIntelectual` (adaptador NotebookLM) e `GeradorVideo` (contrato; adaptadores Flow/NotebookLM vídeo/Vibes/Vids ainda a extrair). Atividade `motor_consultar` na fila `notebooklm-pqbr`.
- **`ReposicaoTemasWorkflow`:** temas vêm do motor (NotebookLM, caderno efêmero semanal, nunca mestre); Líder Editorial monta o pedido e valida (`parse_direto` → PydanticAI só se preciso → filtros → escrita).
- **8 papéis:** registro e `config/modelos_9router.json` reduzidos; persona nova `company/agents/dev`; 7 personas movidas para `docs/_obsoleto/company/agents/`.
- Princípios t512–t514 em REGRAS, ARQUITETURA, ADR-011, DECISOES-LOG (t476); CONTRATO corrigido (NotebookLM não gera mais vídeo; hash do pacote muda).
- **Contratos (t515):** contratos das portas movidos para `src/pqbr/contratos/`; `VERSOES` SemVer por contrato (33, todos 1.0.0) com teste de completude; princípio registrado.
- Testes: 334 passed, 70 skipped, 2 xfailed.

## [0.2.0] — 2026-10-23 (t510, ADR-011)
- **Agentes PydanticAI:** nova fábrica/registro `src/pqbr/agents/` (persona de `company/agents/<papel>/AGENTS.md`, combo do 9router via `OpenAIChatModel` + `OpenAIProvider` em `127.0.0.1:20130/v1`, `FallbackModel` opcional, meta de modelo/fallback no log e no resultado do workflow).
- **`ReposicaoTemasWorkflow` sem Paperclip:** `temas_situacao` → `temas_propor_agente` (só gera/valida, contrato `PropostaTemas`) → `temas_inserir` (escrita). Atividade `paperclip_ids` removida. Novos contratos `TemaProposto`/`PropostaTemas`.
- **Dependências versionadas:** `requirements.txt` (diretas: temporalio 1.34.0, pydantic 2.14.0, pydantic-ai-slim[openai] 2.60.0, psycopg 3.2.13) e `requirements.lock` (freeze do `.venv`).
- **Run preso:** `scripts/temporal/runs_presos.py` + `infra/systemd/pqbr-runs-presos.{service,timer}` (hora em hora, > 6 h → WARNING no journal).
- Docs: ARQUITETURA §10, AGENTES §7/§10, ROADMAP F05-06/08/09 e Fase 1 reescritos; trechos antigos em `docs/_obsoleto/paperclip-trechos-t510.md`.
- Testes: 328 passed, 70 skipped, 2 xfailed (+4 com `TestModel`).

## [0.1.0] — 2026-10-23
- **Contrato editorial v2 oficial (t473):** `docs/CONTRATO-EDITORIAL-v2-CANDIDATO.md` passou a ser `docs/CONTRATO-EDITORIAL.md`. O v1 foi para `docs/_obsoleto/CONTRATO-EDITORIAL-v1.md`. As seções canônicas do v1 (incl. §16/§16.7 usadas por `src/pqbr/workflows/pacote.py` e `scripts/e2e/e2e_pre.py`) estão no Anexo A, sem alteração. O caminho lido pelo código não mudou. Efeito: o hash do pacote canônico muda (nova versão do pacote na próxima montagem). Testes: 324 passed, 70 skipped, 2 xfailed.
- `docs/CONTRATO-EDITORIAL.md` saiu das listas de "não consultar" (AGENTS.md, README.md, ROADMAP.md); entrou `docs/_obsoleto/`.
- **Canal e agentes (t474):** t464 (Discord) revogada; canal = Telegram (Hermes `pqbr`) + sinais do Temporal; painel = Temporal UI. Nova ADR-011 (agentes PydanticAI em activities do Temporal; Paperclip em retirada). Docs canônicos reescritos; guia de acesso renomeado para `docs/operacao/GUIA-ACESSO-PC-TEMPORAL.md`.

- Revisão de `docs/pesquisas/`: nada movido (ver `docs/_obsoleto/README.md`).
