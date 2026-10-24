# CHANGELOG — PQBR

Versionamento SemVer (MAJOR.MINOR.PATCH) a partir de t510. Versão do pacote canônico/contrato segue o próprio hash.


## [0.3.1] — 2026-10-24 (t516)
- notebooklm-py 0.8.4 → 0.8.5 (venv isolado), pin em `requirements-notebooklm.txt` + `requirements-notebooklm.lock`.
- Sem API Google e sem Meta Vibes: `meta_vibes` fora de `GERADORES_VIDEO`/`config/motores.json`; docs marcados.
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
