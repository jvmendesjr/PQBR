#!/bin/sh
# Backup diário do banco local do PQBR: pg_dump -Fc (comprimido), rotação de 7, em ~/Backups/pqbr-db (fora do git).
set -eu; cd "$(dirname "$0")"
D="${PQBR_BACKUP_DIR:-$HOME/Backups/pqbr-db}"; mkdir -p "$D"; chmod 700 "$D"
F="$D/pqbr-$(date +%Y%m%d-%H%M).dump"
docker exec "$(docker compose ps -q pqbr-db)" pg_dump -U postgres -d pqbr -Fc -Z 9 > "$F.tmp"
mv "$F.tmp" "$F"; chmod 600 "$F"
ls -1t "$D"/pqbr-*.dump | tail -n +8 | xargs -r rm -f
echo "$(date -Iseconds) backup ok $(basename "$F") $(stat -c %s "$F") bytes; mantidos $(ls "$D"/pqbr-*.dump | wc -l)" >> "$D/backup.log"
