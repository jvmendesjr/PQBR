#!/bin/sh
# Backup diário do Hindsight (F3-03, t351): pg_dump só leitura do Postgres embutido (pg0). Não para, não reinicia,
# não muda configuração. A senha é lida do instance.json do pg0 na hora (nunca impressa nem gravada).
set -eu
PG0="$HOME/.pg0"; INST="$PG0/instances/hindsight/instance.json"
D="${HINDSIGHT_BACKUP_DIR:-$HOME/Backups/hindsight}"; mkdir -p "$D"; chmod 700 "$D"
eval "$(python3 - "$INST" <<'PY'
import json, shlex, sys
d = json.load(open(sys.argv[1]))
print(f"V={shlex.quote(d['version'])} PORTA={int(d['port'])} U={shlex.quote(d['username'])} DB={shlex.quote(d['database'])}")
print(f"export PGPASSWORD={shlex.quote(d['password'])}")
PY
)"
F="$D/hindsight-$(date +%Y%m%d-%H%M).dump"
"$PG0/installation/$V/bin/pg_dump" -h 127.0.0.1 -p "$PORTA" -U "$U" -d "$DB" -Fc -Z 9 -f "$F.tmp"
unset PGPASSWORD
mv "$F.tmp" "$F"; chmod 600 "$F"
ls -1t "$D"/hindsight-*.dump | tail -n +8 | xargs -r rm -f
echo "$(date -Iseconds) backup ok $(basename "$F") $(stat -c %s "$F") bytes; mantidos $(ls "$D"/hindsight-*.dump | wc -l)" >> "$D/backup.log"
