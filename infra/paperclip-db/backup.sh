#!/bin/sh
# Backup diário do banco local do Paperclip (L-01, t412): pg_dump só leitura dentro do container (socket local,
# sem senha). Não para, não reinicia. Mantém 7 cópias em ~/Backups/paperclip-db (700/600).
set -eu
C=paperclip-db-paperclip-db-1
D="${PAPERCLIP_BACKUP_DIR:-$HOME/Backups/paperclip-db}"; mkdir -p "$D"; chmod 700 "$D"
F="$D/paperclip-$(date +%Y%m%d-%H%M).dump"
umask 077
docker exec "$C" pg_dump -U postgres -d paperclip -Fc -Z 9 > "$F.tmp"
mv "$F.tmp" "$F"; chmod 600 "$F"
ls -1t "$D"/paperclip-*.dump | tail -n +8 | xargs -r rm -f
echo "$(date -Iseconds) backup ok $(basename "$F") $(stat -c %s "$F") bytes; mantidos $(ls "$D"/paperclip-*.dump | wc -l)" >> "$D/backup.log"
