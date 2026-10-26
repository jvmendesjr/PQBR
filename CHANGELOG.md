# CHANGELOG — PQBR

Versionamento SemVer (MAJOR.MINOR.PATCH) a partir de t510. Versão do pacote canônico/contrato segue o próprio hash.




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
