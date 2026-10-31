# ADR-003: cadernos efêmeros do NotebookLM + pacote canônico (t459)

> Status: **APROVADO pelo José (12/10/2026)**. Autoridade: abaixo de REGRAS, SPEC e ARQUITETURA.

## Decisão
- **Sem caderno mestre permanente.** Cada episódio usa um caderno próprio, criado como `Short - <PQBR-EPxxxx> - <slug>`.
  A identidade é o **id** gravado em `pqbr.cadernos_episodio` para o código do episódio (o título é só rótulo).
- **Pacote canônico** = persona (`templates/notebooklm/persona-pqbr.txt`) + comandos/prompts
  (`templates/notebooklm/comandos-pqbr.md`) + contrato editorial (`docs/CONTRATO-EDITORIAL.md`) + bloco visual §16.7
  (extraído do contrato). Versão = sha256 do JSON canônico dos itens.
  - **Fonte de verdade:** Postgres local, `pqbr.pacote_canonico` (migração 0014), uma versão `ativo` por canal.
  - **Espelho legível:** Drive `PQBR/00_Biblia_Visual/pacote-<hash12>/` (ids gravados em `drive_ids`).
  - Um caderno mestre, se um dia for preciso, se recria do pacote em minutos.
- **Ciclo** (`src/pqbr/workflows/pacote.py`, `notebooklm.py`, `episodio.py`):
  `pacote_garantir` → `registro_buscar_caderno` → `nlm_caderno(slug, código, id registrado)` → `registro_caderno`
  → persona → `nlm_injetar_pacote` → roteiro → Short → download/pós/auditor → `nlm_exportar_caderno` +
  `arquivar_caderno` (fontes, respostas, metadados e vídeo → Drive `02_Episodios/AAAA-MM/<código>_<slug>/caderno` +
  `pqbr.arquivo_caderno`) → publicação → `ApagarCadernoWorkflow` (só em publicação real).
- **Apagar** (`nlm_apagar_caderno`): D+2 (48 h + 5–90 min sorteados) após a publicação; só o id registrado para o
  código, arquivado; UUID completo (a CLI aceita id parcial → recusado); título no NotebookLM tem de ser o registrado
  (`Short - <código> - …`) e o dono a conta PQBR; `MESTRES_PROIBIDOS` sempre recusado. **Nunca por título.**
  Em dry-run nada é apagado.
- Cadernos antigos (teste, stickman, B1, pesquisa) **não** são apagados por código: lista para o José aprovar.

## Consequências
- Mudar persona/comandos/contrato/§16.7 gera hash novo automaticamente no próximo episódio.
- O worker `episodio-pqbr` lê `~/.pqbr/worker.env` (drop-in `20-banco-pqbr.conf`) para o papel `pqbr_app`.
- Testes: `tests/unit/test_pacote.py` (hash determinístico, §16.7, travas do apagamento); `db/test_migrations.sh`.

> **Atualização 31/10/2026 (t168u):** mestre norteador permitido; mídia no mestre continua proibida. Ver REGRAS §9 e config/caderno_mestre.json.

