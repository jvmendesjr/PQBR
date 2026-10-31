#!/bin/sh
# Agente de teste do TZ-04 (adaptador "process" do Paperclip; sem LLM, sem --yolo).
# Roda só dentro de um run do Paperclip: usa PAPERCLIP_API_KEY e PAPERCLIP_RUN_ID injetados pelo harness.
# Para cada issue da ponte atribuída a ele, comenta uma proposta inválida e depois uma válida (PropostaAgente).
set -eu
NODE="$HOME/.hermes/node/bin/node"; CLI="$HOME/.paperclip/cli/current/node_modules/paperclipai/dist/index.js"
# O PAPERCLIP_API_URL do run aponta para o hostname local, que não escuta; usa o apiBase do contexto do CLI.
API_BASE=$("$NODE" "$CLI" context show --json | python3 -c 'import sys,json;print(json.load(sys.stdin)["profile"]["apiBase"])')
pc() { "$NODE" "$CLI" "$@" --api-base "$API_BASE" --run-id "$PAPERCLIP_RUN_ID" --json; }
IDS=$(pc agent inbox | python3 -c '
import sys,json
d=json.load(sys.stdin); d=d if isinstance(d,list) else d.get("items",d.get("issues",[]))
print(" ".join(i["id"] for i in d if "[wf:" in (i.get("title") or "") and i.get("status") not in ("done","cancelled")))')
for I in $IDS; do
  pc issue comment "$I" --body 'Proposta malformada de propósito:
```json
{"agente":"tz-proponente","tipo":"apagar_tudo","resumo":"x"}
```' >/dev/null
  pc issue comment "$I" --body 'Proposta do agente de teste:
```json
{"agente":"tz-proponente","tipo":"melhoria","resumo":"ajustar o ritmo da narração do episódio de teste","risco":"baixo"}
```' >/dev/null
  echo "propostas comentadas em $I"
done
