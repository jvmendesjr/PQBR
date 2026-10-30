- **1.2.0 (30/10/2026, José pt162u):** direção e prompts de cena vêm do NotebookLM (`DirecaoCenas`); agentes só operam o Flow; `EpisodioWorkflow` oficial = `episodio.py`; `workflows.py` marcado legado; pin `VERSAO_ESPERADA` 1.2.0.
- **1.1.0 (29/10/2026, José):** storyboard removido definitivamente; cenas individuais no lugar (uma por vez, movimento definido no prompt); regra agente-primeiro, piloto e emergência; centro criativo NotebookLM; modelo de imagem Nano Banana 2.1.
# CHANGELOG — docs/processos

## [1.0.0] — 2026-10-29 (t163u operacional v2)
### Operação EP1003 v2
- Novo projeto Flow `PQBR-EP1003-cafe-fraco-v2`; setup canônico + storyboard Agente **OK** (grade c01..c08). Projeto `025dcfef-…` mantido (HOLD t162u).

## [1.0.0] — 2026-10-29 (t162u operacional)
### Operação EP1003
- Aplicado `flow.md` no projeto `PQBR-EP1003-cafe-fraco`: Agent Confirm=Sempre, 9:16, Nano Banana Pro; Character `@PERS-menina-rosa`; Collections Referencias/Storyboard/Cenas/Finais.
- Pedido de storyboard ao Agente **enviado**; Flow retornou *Falha ao renderizar a resposta* → HOLD (`storyboard_ok=false`). Sem stills/clipes; 0 créditos confirmados.

## [1.0.0] — 2026-10-29
### Adicionado
- `CRIACAO-README.md` v1.0.0 — núcleo agnóstico (José t149u / decisão t160u) [APROVADO].
- `flow.md` v1.0.0 — playbook Google Flow (Agent, Confirm=Sempre, Characters/@Nome, Collections, ≤3 ingredients, Nano Banana Pro, 0-credit check).
- `google-vids.md` / `meta-vibes.md` v0.0.0 — stubs `a descobrir` (cadeia flow → vids → vibes → HOLD).

### Notas
- Origem da pesquisa: `docs/pesquisas/flow-processo-comunidade-20261029.md` (t159u, PROPOSTA → t160u APROVADO).
- Runtime Temporal: activity `processo_criacao_conferir` no código; ativação após reinício do worker (OK José).
