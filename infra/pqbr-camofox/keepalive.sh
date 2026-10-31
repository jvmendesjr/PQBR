#!/bin/sh
# PQBR 24/7 keepalive (t395/F4C-04; José 12/10: Camofox é a única fonte e o ÚNICO renovador da sessão Google).
# Mantém a aba do Studio, toca as abas a cada 60s, checkpoint a cada 5 min; a cada 15 min abre uma página
# Google (NotebookLM) para o Google rotacionar os cookies, salva (checkpoint) e fecha a aba.
# Ritmo humano (REGRAS §157): intervalos com jitter, pausa antes de abrir/fechar; sem clique/digitação aqui.
# O NotebookLM só lê via NOTEBOOKLM_REFRESH_CMD (nlm-sync.sh). Nunca imprime valores.
B=http://127.0.0.1:9387
SRC_DIR="$HOME/.pqbr/camofox/profiles"
LOG="$HOME/.pqbr/logs/camofox-keepalive.log"
mkdir -p "$(dirname "$LOG")"
umask 077
api() { curl -s -m 30 -H "Authorization: Bearer ${CAMOFOX_API_KEY}" "$@"; }
checkpoint() { api -o /dev/null -X POST -H "Content-Type: application/json" -d '{"cookies":[]}' "$B/sessions/pqbr/cookies" && sleep 2 && for f in "$SRC_DIR"/*/storage-state.json; do [ -s "$f" ] && chmod 600 "$f"; done; }
n=0
while true; do
  T=$(api "$B/tabs?userId=pqbr" | python3 -c "import sys,json;[print(x.get(\"tabId\")) for x in json.load(sys.stdin).get(\"tabs\",[])]" 2>/dev/null)
  [ -z "$T" ] && api -o /dev/null -X POST -H "Content-Type: application/json" -d '{"userId":"pqbr","sessionKey":"sessao","url":"https://studio.youtube.com/"}' "$B/tabs"
  for t in $T; do api -o /dev/null "$B/tabs/$t/stats?userId=pqbr"; done
  n=$((n+1))
  if [ $((n%15)) -eq 0 ]; then
    sleep $(shuf -i 3-25 -n 1)
    K=$(api -X POST -H "Content-Type: application/json" -d '{"userId":"pqbr","sessionKey":"keepalive","url":"https://notebooklm.google.com/"}' "$B/tabs" | python3 -c "import sys,json;print(json.load(sys.stdin).get(\"tabId\",\"\"))" 2>/dev/null)
    sleep $(shuf -i 18-45 -n 1); checkpoint; sleep $(shuf -i 2-8 -n 1)
    [ -n "$K" ] && api -o /dev/null -X DELETE "$B/tabs/$K?userId=pqbr"
    echo "$(date -Is) renovação Google + checkpoint (aba ${K:-falhou})" >> "$LOG"
  elif [ $((n%5)) -eq 0 ]; then checkpoint; fi
  sleep $(shuf -i 50-75 -n 1)
done
