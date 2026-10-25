# CHANGELOG — PQBR

Versionamento SemVer (MAJOR.MINOR.PATCH) a partir de t510. Versão do pacote canônico/contrato segue o próprio hash.




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
