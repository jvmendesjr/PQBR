# Lacunas que ainda existem (conferidas no código em 27/10/2026, t129u)

A tabela de 12/10 que bloqueava o fluxo no login da CLI do Paperclip foi para `docs/_obsoleto/lacunas-fluxo-ate-20261027.md`. Não é lacuna. A reposição de temas (`ReposicaoTemasWorkflow`) consulta o NotebookLM e grava no Postgres, sem Paperclip. O descarte de caderno de teste e o episódio estão registrados no `pqbr-episodio-worker`. Itens já feitos (descarte do EP1001, estilo via config, pedido de acesso que se fechou, restauração de sessão) não se repetem aqui.

## Abertas

1. **Auditor no episódio.** `EpisodioWorkflow` (`src/pqbr/workflows/episodio.py`) espera o sinal `veredito_auditor`. Não chama `auditor_gemini` nem `auditor_loop_gemini`. A activity `auditor_gemini` está no worker da fila `camofox-pqbr`. O script `scripts/e2e/auditor_gemini_ep.py` ainda existe. Os critérios `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco` já reprovam sozinhos (t108u); isso não falta.
2. **Pacote só de roteiro.** Com `tipo=short` e `roteirizar`, `NotebookLMWorkflow` segue para `nlm_gerar_short`. Não há um tipo que pare depois do roteiro. Visto em `src/pqbr/workflows/notebooklm.py`.
3. **Códigos do lote 2510.** Os prontos em `docs/pesquisas/lote-2510/` não têm `PQBR-EP`. Sem código não há `drive_enviar` nem episódio no Postgres. Quem define os códigos é o José.
4. **Vídeo em série (Fase 4V).** O episódio ainda baixa o vídeo do NotebookLM. Flow, Vids e Vibes não estão no código. HOLD das três rotas está decidido (t529) e não implementado.
5. **Storyboard.** O contrato `FichaCena`/`Storyboard` existe. Falta a activity que gera o storyboard e impede a geração sem ele. As imagens de referência do elenco são pagas e seguem postergadas.
6. **Navegador.** `NavegadorIdentidade` está em `src/pqbr/motores/navegador.py`. Nenhum workflow importa essa porta. O backup diário e o canário do ADR-012 não foram conferidos nesta passagem: não entram como feitos nem como lacuna confirmada.
7. **Publicação, o que ainda falta.** O envio real está desligado de propósito (`YOUTUBE_DRY_RUN=true`) até a produção ativa. O roteiro de cliques do Studio não foi visto. `config/mapa_cliques.json` está vazio. O worker do episódio não tem o drop-in `telegram.conf`. O resto dessa etapa (chaves, agenda, registro no worker, fallback do refresh) está no ar desde 27/10 08:56 (-03).
8. **Teste adiado, não executar agora.** LOOP do Gemini por cena, e 4 Argon baixo contra 3.8 Flash no mesmo lote.

## Não são lacunas

- Login da CLI do Paperclip, issue no Paperclip para começar episódio ou descarte, e o token do bot Hermes citado em 15/10. O canal vigente é o bot próprio (t538). O corte do serviço Paperclip é o item F05-09 do ROADMAP, não um login pendente.
- Legenda extra no pós. José decidiu em t435 que a legenda do NotebookLM fica e o pós não grava outra. `scripts/legendar_short.py` é sobra, não um passo do fluxo.
- Critérios visuais `personagem_mexe_labios` / corte / grotesco como "próxima versão do auditor". Já estão no juiz (t108u), com os nomes `boca_articula_fala`, `corte_oculos_cabeca` e `grotesco`.
