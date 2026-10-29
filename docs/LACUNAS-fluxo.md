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
8. **Publicação, o que ainda falta.** O envio real está desligado de propósito (`YOUTUBE_DRY_RUN=true`) até a produção ativa. O roteiro de cliques do Studio não foi visto. `config/mapa_cliques.json` tem só surpresas do Flow (t132u), não um roteiro do Studio. O worker do episódio não tem o drop-in `telegram.conf`. O resto dessa etapa (chaves, agenda, registro no worker, fallback do refresh) está no ar desde 27/10 08:56 (-03).
9. **Teste adiado, não executar agora.** LOOP do Gemini por cena, e 4 Argon baixo contra 3.8 Flash no mesmo lote.

## Não são lacunas

- Login da CLI do Paperclip, issue no Paperclip para começar episódio ou descarte, e o token do bot Hermes citado em 15/10. O canal vigente é o bot próprio (t538). O corte do serviço Paperclip é o item F05-09 do ROADMAP, não um login pendente.
- Geração de vídeo no NotebookLM. Descartada no fluxo (t130u). `nlm_gerar_short` recusa. A legenda extra no pós continua fora: `scripts/legendar_short.py` é sobra. A decisão t435 vale para o vídeo da cadeia, quando ela existir.
- Critérios visuais `personagem_mexe_labios` / corte / grotesco como "próxima versão do auditor". Já estão no juiz (t108u), com os nomes `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco`.
