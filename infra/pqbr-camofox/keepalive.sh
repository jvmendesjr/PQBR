#!/bin/sh
# PQBR 24/7 keepalive (t395/F4C-04, F4-05). Credentials come from the unit EnvironmentFile.
# Keeps one Studio tab open, touches tabs every 60s, checkpoints storage every 5 min,
# (empty cookie import = persistence-plugin checkpoint; the storage_state export route only exists with VNC on),
# NotebookLM tem sessão própria (reauth nativa do notebooklm-py, t-nlm2): NÃO copiar para o perfil dele.
B=http://127.0.0.1:9387
SRC_DIR="$HOME/.pqbr/camofox/profiles"
DST="$HOME/.pqbr/notebooklm/profiles/pqbr/storage_state.json"
umask 077
api() { curl -s -H "Authorization: Bearer ${CAMOFOX_API_KEY}" "$@"; }
sync_state() {
  for f in "$SRC_DIR"/*/storage-state.json; do
    [ -s "$f" ] || continue
    chmod 600 "$f"
    python3 -c "import json,sys;json.load(open(sys.argv[1]))" "$f" || continue
    mkdir -p "$(dirname "$DST")"
    cp "$f" "$DST.tmp" && chmod 600 "$DST.tmp" && mv -f "$DST.tmp" "$DST"
  done
}
n=0
while true; do
  T=$(api "$B/tabs?userId=pqbr" | python3 -c "import sys,json;[print(x.get(\"tabId\")) for x in json.load(sys.stdin).get(\"tabs\",[])]" 2>/dev/null)
  [ -z "$T" ] && api -o /dev/null -X POST -H "Content-Type: application/json" -d "{\"userId\":\"pqbr\",\"sessionKey\":\"sessao\",\"url\":\"https://studio.youtube.com/\"}" "$B/tabs"
  for t in $T; do api -o /dev/null "$B/tabs/$t/stats?userId=pqbr"; done
  n=$((n+1))
  if [ $((n%5)) -eq 0 ]; then api -o /dev/null -X POST -H "Content-Type: application/json" -d "{\"cookies\":[]}" "$B/sessions/pqbr/cookies" && sleep 2 && for f in "$SRC_DIR"/*/storage-state.json; do [ -s "$f" ] && chmod 600 "$f"; done; fi
  sleep 60
done
