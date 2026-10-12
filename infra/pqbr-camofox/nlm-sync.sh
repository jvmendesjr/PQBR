#!/bin/sh
# NOTEBOOKLM_REFRESH_CMD da PQBR: o Camofox é o único dono/rotacionador da sessão Google.
# Pede um checkpoint ao Camofox (import vazio de cookies) e copia o storage-state (600, atômico)
# para o perfil pqbr do NotebookLM. Usado pelo notebooklm-py em falha de auth e pelo worker antes de repetir.
set -eu
umask 077
set -a; . "$HOME/.pqbr/camofox/.env"; set +a
curl -s -m 20 -o /dev/null -X POST -H "Authorization: Bearer ${CAMOFOX_API_KEY}" -H "Content-Type: application/json" \
  -d '{"cookies":[]}' "http://127.0.0.1:9387/sessions/pqbr/cookies"
sleep 2
DST="${NOTEBOOKLM_REFRESH_STORAGE_PATH:-$HOME/.pqbr/notebooklm/profiles/pqbr/storage_state.json}"
for f in "$HOME"/.pqbr/camofox/profiles/*/storage-state.json; do
  [ -s "$f" ] || continue
  chmod 600 "$f"
  python3 -c "import json,sys;json.load(open(sys.argv[1]))" "$f"
  cp "$f" "$DST.tmp" && chmod 600 "$DST.tmp" && mv -f "$DST.tmp" "$DST"
done
