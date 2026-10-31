#!/bin/sh
# uso: restore.sh <dump>  — restaura public+drizzle no banco local (como role paperclip)
set -e
. $HOME/.config/paperclip-db/db.env
F=$1; C=paperclip-db-paperclip-db-1
docker exec -i $C sh -c 'psql -q -U postgres -d paperclip' <<SQL
drop schema if exists drizzle cascade;
do \$\$ declare r record; begin for r in select tablename from pg_tables where schemaname='public' loop execute 'drop table if exists public.'||quote_ident(r.tablename)||' cascade'; end loop; end \$\$;
SQL
docker cp "$F" $C:/tmp/restore.dump
docker exec -e PGPASSWORD="$PAPERCLIP_DB_APP_PASSWORD" $C sh -c 'pg_restore -h 127.0.0.1 -U paperclip -d paperclip --no-owner --no-privileges --no-comments /tmp/restore.dump 2>&1 | grep -E "error|ERROR" | sort | uniq -c | head -30; rm -f /tmp/restore.dump'
