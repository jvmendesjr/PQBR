# Índice — Sincronização 0.29.8 (29/10/2026, ordem do José)

Nada foi apagado. O que saiu dos documentos vivos foi marcado como superado/histórico no lugar
ou já estava preservado em `_obsoleto/`. Este índice diz, para cada conteúdo obsoleto, onde ele
vive agora e o que o substitui — para que um agente externo novo não o ressuscite como etapa viva.

## Extraído dos documentos vivos (agora só histórico ou superado)

| Conteúdo obsoleto | Onde vivia | Onde vive agora | Substituto vigente |
|---|---|---|---|
| Board geral / `storyboard_criar` / `PROMPT_STORYBOARD` / gate `storyboard_ok` | `docs/processos/CRIACAO-README.md`, `flow.md`, `EpisodioWorkflow`, `config/flow_projetos.json` | `scripts/_obsoleto/storyboard.py`, `scripts/_obsoleto/storyboard_criar_arquivado.py`, `docs/_obsoleto/INDICE-storyboard-removido.md` | Cenas individuais, uma por vez, contrato `CenaIndividual` 1.0.0 |
| Storyboard como etapa em ESTADO/ROADMAP (gates, "episódio para no storyboard", "stills só após storyboard") | `docs/ESTADO-ATUAL.md` (gates, onde paramos, fluxo, P6/P16/P17), `docs/ROADMAP.md` (Fase 4V, R2/R3, MG-05/MG-06, piloto) | Marcado "só histórico / SUPERADO" no lugar; história completa em `docs/_obsoleto/INDICE-storyboard-removido.md` | Roteiro aprovado → cenas individuais Flow → revisão (piloto: José; depois: automática) |
| Storyboard texto do EP1003 v2 (8 painéis, t163u) como próximo passo | `docs/ESTADO-ATUAL.md`, `docs/ROADMAP.md` piloto | Só histórico (t163u, evidência `/workspace/flow-check/ep1003-v2-storyboard.png`); não é etapa nem gate | 8 imagens de início de cena S01..S08 (Nano Banana 2.1) |
| Nano Banana Pro como modelo de imagem vigente | `docs/processos/flow.md`, `docs/CONTRATO-EDITORIAL.md` §§18, `docs/ESTADO-ATUAL.md`, `docs/ROADMAP.md` piloto | Só histórico (modelo anterior, superado em 29/10/2026) | **Nano Banana 2.1** (registrado 29/10/2026, ordem do José; conferir 0 créditos) |
| "OK reinício worker com storyboard 1.3.0" como pendência | `docs/ESTADO-ATUAL.md`, `docs/ROADMAP.md` | Resolvido: worker reiniciado 29/10/2026 às 23:14 para o núcleo 1.1.0 (`processo_criacao_conferir` ok) | Pendências restantes: folha nº 1, mídia SIT-*, OK MG-12 / merge |
| 2 falhas pré-existentes `test_flow_projeto.py` (EP1003) como pendência | `docs/ESTADO-ATUAL.md` (seção migração CBM) | Resolvidas no commit 0.29.7; suíte canônica `pytest tests` = 677 passed, 0 falhas | — |
| Papéis dos agentes com revisão humana implícita | `docs/processos/CRIACAO-README.md` (Diretor, Guardião, Auditor) | Reescritos agente-primeiro: Diretor/Guar­dião/Auditor são agentes; José só decide, nunca executa (clicar, baixar, olhar) | Regra suprema agente-primeiro (núcleo 1.1.0) |
| Bloco de números "do storyboard" no motion | `src/pqbr/pos/motion/biblioteca/regras.md` | Reescrito: bloco de números do roteiro/cenas individuais | Motion (MG-05) segue segurado, definição pendente |
| `contratos/storyboard.py` como caminho de política | `config/politica_papeis.json` (lista de arquivos) | Arquivo renomeado em 0.29.7 para `contratos/cena.py`; a entrada antiga na política é referência histórica ao caminho antigo | `contratos/cena.py` (`CenaIndividual`) |

## Mantido de propósito, só como histórico (não é instrução viva)

- `docs/ROADMAP.md` "Estado em 26/10/2026" (marcado "Histórico" no próprio título): contrato `FichaCena`/`Storyboard` 1.1.0, pesquisa `flow-storyboard-por-cena.md`, activity que gerava o `Storyboard`.
- `docs/processos/CHANGELOG.md` e `CHANGELOG.md`/`DECISOES-LOG.md`: entradas antigas citando storyboard e Nano Banana Pro (t163u, flow.md v1.0.0).
- `docs/ESTADO-ATUAL.md` tabela P5 (fichas nanquim t146u reprovadas, Nano Banana Pro): registro de decisão passada, não regra vigente.
- Classificador `src/pqbr/storage/hindsight_tags.py`: a palavra "storyboard" continua como palavra-chave de tag editorial, só para classificar documentos históricos — não é uma etapa do fluxo.
- Backend anterior do `codigo`: preservado em `_obsoleto/` (índice `docs/_obsoleto/INDICE-migracao-cbm.md`), sem desinstalar até ordem expressa.

## O que um agente externo novo deve ler primeiro (ordem)

1. `AGENTS.md` (gerado, `scripts/mcp/gerar_agents_md.py`) — roster, regras, ESTADO, ROADMAP vigente.
2. `docs/processos/CRIACAO-README.md` 1.1.0 (núcleo, agente-primeiro) + `docs/processos/flow.md` 1.1.0 (playbook Flow).
3. `docs/ESTADO-ATUAL.md` (onde paramos) + `docs/ROADMAP.md` (Fase 4V e MG).
4. Este índice + `docs/_obsoleto/INDICE-storyboard-removido.md` + `docs/_obsoleto/INDICE-migracao-cbm.md` — só para não ressuscitar o que foi removido.
5. `docs/operacao/onboarding-agente-externo.md` (procedimento de cliente pqbr-mcp) e, via pqbr-mcp, `onboarding` → `buscar_memoria` antes de agir.
