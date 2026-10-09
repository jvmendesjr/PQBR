#!/bin/sh
# Restaura o backup mais recente num banco descartável (no mesmo container), compara contagens e apaga.
set -eu; cd "$(dirname "$0")"
D="${PQBR_BACKUP_DIR:-$HOME/Backups/pqbr-db}"; F=$(ls -1t "$D"/pqbr-*.dump | head -1)
C="$(docker compose ps -q pqbr-db)"; T=pqbr_restauracao_teste
docker exec "$C" dropdb -U postgres --if-exists $T; docker exec "$C" createdb -U postgres $T
docker exec -i "$C" pg_restore -U postgres -d $T --no-owner --no-privileges < "$F" 2>&1 | grep -v "role .* does not exist" || true
Q="select count(*) from pg_tables where schemaname='pqbr'; select count(*) from pqbr.temas; select count(*) from pqbr.plataformas;"
O=$(docker exec "$C" psql -U postgres -d pqbr -qAt -c "$Q" | tr '\n' ' '); R=$(docker exec "$C" psql -U postgres -d $T -qAt -c "$Q" | tr '\n' ' ')
docker exec "$C" dropdb -U postgres $T
echo "dump: $(basename "$F")  original: $O  restaurado: $R  $( [ "$O" = "$R" ] && echo IGUAL || echo DIFERENTE )"
