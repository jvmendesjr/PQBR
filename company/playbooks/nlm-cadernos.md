# Playbook `nlm-cadernos` — mestre norteador + efêmero (t459; atualizado t168u/t169u)

**REGRA PERMANENTE (José 12/10): arquivar e verificar SEMPRE antes de apagar.** Todo caderno (episódio ou pesquisa) só é apagado depois de exportar tudo (fontes com URL e texto integral, relatórios, respostas do chat, notas, metadados + resumo de achados) para Drive `00_Biblia_Visual/pesquisas` (ou pasta do episódio), repo e `pqbr.arquivo_caderno`, e de conferir as 3 cópias (contagem e bytes; `verificar_arquivo` grava `verificado_em`). Falhou um export → **não apaga** aquele caderno. Indexar no Hindsight.

Regra (t168u): **Caderno Mestre** `00ce61ae…` (`config/caderno_mestre.json`) = norteador permanente (briefing `BriefingEfemerico`; salvar nota; limpar chat `ask --new -y`; **nunca mídia**). Legado `c35d7b24` e `MESTRES_PROIBIDOS` continuam bloqueados. Um caderno **efêmero** por episódio, casado pelo **id** em `pqbr.cadernos_episodio`. Versão antiga “sem mestre”: `docs/_obsoleto/nlm-cadernos-sem-mestre-ate-20261031.md`.

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

## NotebookLM-first (t464; fluxo t168u)
1. **Mestre** (Temporal `nlm_mestre_briefing`): pede `BriefingEfemerico` → nota → limpa chat. Sem generate/download.
2. **Efêmero** (`nlm_abrir_efemero_com_briefing`): persona do briefing + `add-research` com `prompt_pesquisa` do mestre.
3. No efêmero: pacote hash → `ask` roteiro (`RoteiroShort`) → compliance → SEO (`PacoteSEO`) → `direcao_cenas_nlm` (`DirecaoCenas` 2.0.0, rótulo `PQBR-EP####-S##`).
4. **Sem vídeo NLM.** Cenas no Flow = passo 2 (agente/UI; adaptador pendente).
5. Papéis: Temporal orquestra; NLM mestre/efêmero geram texto; agente só Flow.

**Próximos (José 31/10, só registro):** papel dos cadernos na validação/auditoria; José ajusta refs VISUAIS (fichas/objetos/estilo).

