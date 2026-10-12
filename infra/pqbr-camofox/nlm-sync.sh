#!/bin/sh
# NOTEBOOKLM_REFRESH_CMD da PQBR (José, 12/10): Camofox (userId=pqbr) é a ÚNICA fonte e o ÚNICO renovador da sessão Google.
# Pede checkpoint ao Camofox (import vazio = checkpoint do plugin persistence), lê o storage-state persistido,
# filtra só domínios Google e grava (600, atômico) em NOTEBOOKLM_REFRESH_STORAGE_PATH. Nunca imprime valores.
set -eu
umask 077
set -a; . "$HOME/.pqbr/camofox/.env"; set +a
curl -s -m 20 -o /dev/null -X POST -H "Authorization: Bearer ${CAMOFOX_API_KEY}" -H "Content-Type: application/json" \
  -d '{"cookies":[]}' "http://127.0.0.1:9387/sessions/pqbr/cookies" || true
sleep 2
SRC="$HOME/.pqbr/camofox/profiles/66e057673effe4afdd963a2bd6a45a2a/storage-state.json"
DST="${NOTEBOOKLM_REFRESH_STORAGE_PATH:-$HOME/.pqbr/notebooklm/profiles/pqbr/storage_state.json}"
python3 - "$SRC" "$DST" <<'P'
import json, os, sys
src, dst = sys.argv[1], sys.argv[2]
ok = lambda h: any(h.lstrip('.') == d or h.endswith('.' + d) for d in ("google.com", "google.com.br", "googleusercontent.com"))
s = json.load(open(src))
c = [k for k in s.get("cookies", []) if ok(k.get("domain", ""))]
names = {k["name"] for k in c}
if not {"SID", "__Secure-1PSIDTS"} <= names:
    sys.exit("sessão Camofox sem SID/__Secure-1PSIDTS")
o = [x for x in s.get("origins", []) if ok(x.get("origin", "").split("://")[-1].split(":")[0])]
tmp = dst + ".tmp"
with open(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w") as f:
    json.dump({"cookies": c, "origins": o}, f)
os.replace(tmp, dst)
print(f"nlm-sync ok: {len(c)} cookies Google")
P
