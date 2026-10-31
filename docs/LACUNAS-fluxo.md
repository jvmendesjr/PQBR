# Lacunas que ainda existem (conferidas no código em 27/10/2026, t130u)

A tabela de 12/10 que bloqueava o fluxo no login da CLI do Paperclip foi para `docs/_obsoleto/lacunas-fluxo-ate-20261027.md`. Não é lacuna. A reposição de temas (`ReposicaoTemasWorkflow`) consulta o NotebookLM e grava no Postgres, sem Paperclip. O descarte de caderno de teste e o episódio estão registrados no `pqbr-episodio-worker`. Itens já feitos (descarte do EP1001, estilo via config, pedido de acesso que se fechou, restauração de sessão) não se repetem aqui.

## Abertas

0b. **Fechado (30/10/2026, José pt162u).** Mapa `01-episodio.mmd` atualizado com `direcao_cenas_nlm` e `flow_projeto_exigir_antes_cenas`; aba Produção no painel.

0c. **EP1003 fora do Temporal (30/10/2026).** O piloto EP1003 (v2/v3) rodou **manual no Flow via Camofox**, sem `EpisodioWorkflow` Temporal. Isso **não** é o caminho oficial. Oficial = `episodio.py` → NLM → `direcao_cenas_nlm` → gates → (passo 2 Flow ainda pendente). Piloto serve só para validar UI/fichas/créditos.

0. **Ativação `processo_criacao_conferir` (t160u).** Activity e testes no repo; o `EpisodioWorkflow` já chama no início. **Falta reinício** do `pqbr-episodio-worker` (OK José) para valer em runtime. Docs: `docs/processos/`.

1. **Auditor no episódio.** `EpisodioWorkflow` para na ficha e não espera `veredito_auditor` (t130u). O sinal continua registrado e não é chamado. Não chama `auditor_gemini` nem `auditor_loop_gemini`. A activity `auditor_gemini` está no worker da fila `camofox-pqbr`. O script `scripts/e2e/auditor_gemini_ep.py` ainda existe. Os critérios `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco` já reprovam sozinhos (t108u); isso não falta.
2. **Fechado (t130u, atualizado 29/10/2026).** `tipo=short` não gera vídeo. `nlm_gerar_short` recusa antes do CLI. O episódio segue roteiro/SEO e depois `direcao_cenas_nlm` (passo 1); para com `proximo=flow_cenas_individuais_pendente` (`storyboard_criar` removido 29/10/2026).
3. **Códigos do lote 2510.** Os prontos em `docs/pesquisas/lote-2510/` não têm `PQBR-EP`. Sem código não há `drive_enviar` nem episódio no Postgres. Quem define os códigos é o José.
4. **Vídeo em série (Fase 4V).** Passo 1 (direção NLM→CenaIndividual) em código (30/10/2026); passo 2 adaptador Flow ainda fora do código. O episódio não baixa vídeo do NotebookLM (t130u). Vids e Vibes continuam fora. Em 27/10 o Flow foi aberto à mão (t132u): duas imagens, nenhum vídeo. HOLD das três rotas está decidido (t529) e não implementado. O mapa de cliques só tem as três surpresas dessa tela.
5. **Projeto Flow EP1003 (t161u — parcial, atualizado 29/10/2026).** Projeto v2 `PQBR-EP1003-cafe-fraco-v2` (`3a9ca558-…`); antigo `025dcfef-…` HOLD intacto. Falta: imagens de início de cena, revisão, vídeo. Storyboard não é mais lacuna (removido). Gate: `src/pqbr/pipeline/flow_projeto.py` (exige só `fichas_ok`).
6. **Imagens das cenas individuais (atualizado 30/10/2026).** Passo 1 pronto: `direcao_cenas_nlm` valida `CenaIndividual` 2.0.0 fail-closed (stickman, adulta, sem girl). Passo 2 (adaptador Flow gerando stills/clipes) ainda não está no código. Piloto manual EP1003 v3/v4 separado. Instruções do Agente no projeto de testes já foram regravadas no flat (t155u); no projeto EP1003 ainda conferir/reaplicar se necessário.
7. **Navegador.** `NavegadorIdentidade` está em `src/pqbr/motores/navegador.py`. Nenhum workflow importa essa porta. O backup diário e o canário do ADR-012 não foram conferidos nesta passagem: não entram como feitos nem como lacuna confirmada.
8. **Publicação, o que ainda falta.** O envio real está desligado de propósito (`YOUTUBE_DRY_RUN=true`) até a produção ativa. O roteiro de cliques do Studio não foi visto. `config/mapa_cliques.json` tem só surpresas do Flow (t132u), não um roteiro do Studio. O worker do episódio não tem o drop-in `telegram.conf`. O resto dessa etapa (chaves, agenda, registro no worker, fallback do refresh) está no ar desde 27/10 08:56 (-03).
9. **Teste adiado, não executar agora.** LOOP do Gemini por cena, e 4 Argon baixo contra 3.8 Flash no mesmo lote.

## Não são lacunas

- Login da CLI do Paperclip, issue no Paperclip para começar episódio ou descarte, e o token do bot Hermes citado em 15/10. O canal vigente é o bot próprio (t538). O corte do serviço Paperclip é o item F05-09 do ROADMAP, não um login pendente.
- Geração de vídeo no NotebookLM. Descartada no fluxo (t130u). `nlm_gerar_short` recusa. A legenda extra no pós continua fora: `scripts/legendar_short.py` é sobra. A decisão t435 vale para o vídeo da cadeia, quando ela existir.
- Critérios visuais `personagem_mexe_labios` / corte / grotesco como "próxima versão do auditor". Já estão no juiz (t108u), com os nomes `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco`.

## Atualização 31/10/2026 (t168u — caderno mestre)

- **Novo:** Caderno Mestre canônico como norteador (briefing JSON → efêmero). Runtime das activities `nlm_mestre_*` / etapa briefing no `EpisodioWorkflow` **falta reinício** do worker NotebookLM/episódio (OK José). ID em `config/caderno_mestre.json`.
- **Atualizado (item 6):** `CenaIndividual`/`DirecaoCenas` passam a **2.0.0** (rótulo `PQBR-EP####-S##`). Passo 2 Flow ainda pendente.
- **Fechado parcialmente:** exportação read-only do mestre legado `c35d7b24` em `docs/pesquisas/mestre-antigo-c35d7b24/` (legado continua em `MESTRES_PROIBIDOS`, não apagado).
- **Mantido:** itens 0 (reinício processo_criacao), 4 (passo 2 Flow), 0c (piloto manual ≠ oficial).

