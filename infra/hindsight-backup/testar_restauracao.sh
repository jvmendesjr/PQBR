#!/bin/sh
# Restaura o dump mais recente do Hindsight num container descartável (pgvector/pg18, sem rede), compara e apaga.
# Não toca na instância real do Hindsight além de uma leitura de contagens.
set -eu
PG0="$HOME/.pg0"; INST="$PG0/instances/hindsight/instance.json"
D="${HINDSIGHT_BACKUP_DIR:-$HOME/Backups/hindsight}"; F=$(ls -1t "$D"/hindsight-*.dump | head -1)
IMG="${HINDSIGHT_RESTORE_IMAGE:-pgvector/pgvector:pg18}"; N=hindsight-restore-$$
docker run -d --rm --name $N --network none -m 512m -e POSTGRES_PASSWORD=teste-local "$IMG" >/dev/null
trap 'docker rm -f $N >/dev/null 2>&1' EXIT
for i in $(seq 1 40); do docker exec $N pg_isready -U postgres -q 2>/dev/null && break; sleep 1; done; sleep 2
docker exec $N createdb -U postgres hindsight
docker exec -i $N pg_restore -U postgres -d hindsight --no-owner --no-privileges < "$F" 2>&1 | grep -vE "role .* does not exist" | tail -5 || true
Q="select count(*) from information_schema.tables where table_schema not in ('pg_catalog','information_schema');"
for t in banks memory_units documents entities; do Q="$Q select coalesce((select count(*) from $t)::text, '-') ;"; done
R=$(docker exec $N psql -U postgres -d hindsight -qAt -c "$Q" 2>/dev/null | tr '\n' ' ')
eval "$(python3 - "$INST" <<'PY'
import json, shlex, sys
d = json.load(open(sys.argv[1]))
print(f"V={shlex.quote(d['version'])} PORTA={int(d['port'])} U={shlex.quote(d['username'])} DB={shlex.quote(d['database'])}")
print(f"export PGPASSWORD={shlex.quote(d['password'])}")
PY
)"
O=$("$PG0/installation/$V/bin/psql" -h 127.0.0.1 -p "$PORTA" -U "$U" -d "$DB" -qAt -c "$Q" 2>/dev/null | tr '\n' ' '); unset PGPASSWORD
echo "dump: $(basename "$F")  original: $O  restaurado: $R  $( [ "$O" = "$R" ] && echo IGUAL || echo DIFERENTE )"
