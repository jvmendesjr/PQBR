#!/bin/sh
# Aplica as migrações 0001..0012 (todas em ordem) no banco local e define login/senha dos papéis (senhas lidas do .env, sem eco).
set -eu; cd "$(dirname "$0")"; . ./.env
C="$(docker compose ps -q pqbr-db)"
P() { docker exec -i -w /repo "$C" psql -U postgres -d pqbr -v ON_ERROR_STOP=1 -qAt "$@"; }
P -c "create table if not exists public.pqbr_migracoes (arquivo text primary key, aplicado_em timestamptz not null default now())"
for f in ../../db/migrations/[0-9][0-9][0-9][0-9]_*.sql; do
  b=$(basename "$f")
  if [ "$(P -c "select count(*) from public.pqbr_migracoes where arquivo='$b'")" = 1 ]; then echo "já aplicada: $b"; continue; fi
  P -f "/repo/db/migrations/$b" >/dev/null && P -c "insert into public.pqbr_migracoes (arquivo) values ('$b')" && echo "aplicada: $b"
done
# login + senha (via variáveis psql, não aparecem em ps nem em log)
docker exec -i "$C" psql -U postgres -d pqbr -v ON_ERROR_STOP=1 -q \
  -v app="$PQBR_APP_PASSWORD" -v leit="$PQBR_LEITURA_PASSWORD" -v manut="${PQBR_MANUT_PASSWORD:-}" <<'SQL'
alter role pqbr_app login password :'app' connection limit 10;
alter role pqbr_leitura login password :'leit' connection limit 5;
revoke all on database pqbr from public;
grant connect on database pqbr to pqbr_app, pqbr_leitura;
select :'manut' <> '' as tem_manut \gset
\if :tem_manut
alter role pqbr_manutencao login password :'manut' connection limit 2;
grant connect on database pqbr to pqbr_manutencao;
\endif
revoke create on schema public from public;
SQL
# Sem "trust" no localhost do container: só o socket local (docker exec) fica sem senha.
docker exec "$C" sed -i -E 's/^(host\s+(all|replication)\s+all\s+(127\.0\.0\.1\/32|::1\/128)\s+)trust/\1scram-sha-256/' /var/lib/postgresql/data/pg_hba.conf
P -c "select pg_reload_conf()" >/dev/null
echo "papéis e pg_hba configurados"
