# Playbook `nlm-cadernos` — ciclo do caderno efêmero (t459, ADR-003)

Regra: sem caderno mestre; um caderno por episódio, casado pelo **id** registrado em `pqbr.cadernos_episodio`.

1. **Caderno registrado sumiu do NotebookLM** (`nlm_caderno` falha "sumiu"): não recriar às cegas. Conferir
   `pqbr.arquivo_caderno`; se já arquivado, marcar `apagado_em` e seguir; senão, ticket para o Diretor.
2. **Pacote não injetado / hash divergente:** rodar `pacote_garantir` (idempotente); conferir `pqbr.pacote_canonico`
   (`ativo`) e a pasta `00_Biblia_Visual/pacote-<hash12>`.
3. **Arquivamento falhou** (Drive/banco): repetir (idempotente por `caderno_id, tipo, nome`). Sem arquivamento o
   apagamento é recusado — nunca forçar.
4. **Apagamento recusado** (allowlist, título, dono, antes de D+2): é proteção. Registrar na issue; não contornar,
   não apagar por título, não usar id parcial. Mestres (`MESTRES_PROIBIDOS`) nunca.
5. **Cadernos órfãos/antigos:** gerar a lista classificada (id/título/data) e pedir aprovação ao José. Nada de apagar
   em massa por código.
