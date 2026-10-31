# Playbook `nlm-cadernos` — ciclo do caderno efêmero (t459, ADR-003)

**REGRA PERMANENTE (José 12/10): arquivar e verificar SEMPRE antes de apagar.** Todo caderno (episódio ou pesquisa) só é apagado depois de exportar tudo (fontes com URL e texto integral, relatórios, respostas do chat, notas, metadados + resumo de achados) para Drive `00_Biblia_Visual/pesquisas` (ou pasta do episódio), repo e `pqbr.arquivo_caderno`, e de conferir as 3 cópias (contagem e bytes; `verificar_arquivo` grava `verificado_em`). Falhou um export → **não apaga** aquele caderno. Indexar no Hindsight.

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
6. **`CSRF token not found` / final URL notebook.google.com** (rebrand Gemini Notebook, 12/10): não é página mudada;
   a cópia da sessão ficou velha. Rodar `~/.pqbr/camofox/nlm-sync.sh` (o `_cli` já faz isso sozinho) e repetir.
7. **Isolamento entre cadernos de episódio (t459c):** toda atividade de produção usa o **id registrado** do caderno do
   episódio (nunca título nem "mais recente"); o caderno recebe só o pacote canônico + as fontes do próprio episódio,
   cada uma registrada por id em `pqbr.fontes_caderno`. Antes de gerar, `nlm_conferir_fontes` compara a lista do
   NotebookLM com o registro: fonte estranha → **bloqueia** (`ContaminacaoCaderno`, sem retentativa), resultado
   `bloqueado` e ticket. Não remover a fonte às cegas: investigar a origem (outro episódio? pesquisa?) e registrar.

## NotebookLM-first (t464, José 14:00)
No caderno do episódio: persona → pacote → briefing do tema → `add-research` fast (fontes importadas registradas como `pesquisa`) → `ask` do roteiro (JSON validado em `RoteiroShort`, 2 tentativas) → Compliance/Guardião (9router, combo do papel) → roteiro como fonte registrada → checagem anti-contaminação → Short com steering do bloco 2D → `ask` SEO (`PacoteSEO`; reserva 9router `especialista-seo`) → capa `generate infographic --orientation portrait` (reserva: A9 num quadro).

