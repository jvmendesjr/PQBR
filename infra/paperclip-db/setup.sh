#!/bin/sh
set -e
umask 077
D=$HOME/.config/paperclip-db; mkdir -p -m 700 $D
if [ ! -f $D/db.env ]; then
  { echo POSTGRES_USER=postgres; echo POSTGRES_DB=paperclip
    for v in POSTGRES_PASSWORD PAPERCLIP_DB_APP_PASSWORD; do echo "$v=$(openssl rand -hex 24)"; done; } > $D/db.env
fi
. $D/db.env
R=$HOME/Workspace/PQBR/infra/paperclip-db
cd $R && docker compose -p paperclip-db up -d
for i in $(seq 1 30); do docker exec paperclip-db-paperclip-db-1 pg_isready -U postgres -d paperclip >/dev/null 2>&1 && break; sleep 2; done
docker exec -i -e AP="$PAPERCLIP_DB_APP_PASSWORD" paperclip-db-paperclip-db-1 sh -c 'psql -v ON_ERROR_STOP=1 -U postgres -d paperclip -v ap="$AP"' <<SQL
do \$\$ begin if not exists (select 1 from pg_roles where rolname='paperclip') then create role paperclip login; end if; end \$\$;
alter role paperclip password :'ap';
alter database paperclip owner to paperclip;
alter schema public owner to paperclip;
create extension if not exists pg_trgm schema public;
create extension if not exists fuzzystrmatch schema public;
create schema if not exists extensions authorization paperclip;
create extension if not exists pgcrypto schema extensions;
create extension if not exists "uuid-ossp" schema extensions;
SQL
echo setup-ok
