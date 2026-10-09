#!/bin/sh
# Verificação não destrutiva do banco local, conectando PELO HOST (127.0.0.1:55433), como o worker faria.
set -eu; cd "$(dirname "$0")"; . ./.env
C="$(docker compose ps -q pqbr-db)"
S() { docker exec -i "$C" psql -U postgres -d pqbr -qAt -c "$1"; }
H() { docker run --rm --network host -e PGPASSWORD="$1" postgres:17-alpine psql -h 127.0.0.1 -p 55433 -U "$2" -d pqbr -qAt -c "$3" 2>&1 | grep -vE '^(LINE|\s)' | head -1; }
echo "tabelas pqbr: $(S "select count(*) from pg_tables where schemaname='pqbr'")  temas: $(S "select count(*) from pqbr.temas")  plataformas: $(S "select string_agg(id,',') from pqbr.plataformas")"
echo "RLS ligado+forçado em todas: $(S "select bool_and(relrowsecurity and relforcerowsecurity) from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='pqbr' and c.relkind='r'")"
echo "papéis: $(S "select string_agg(rolname||'(login='||rolcanlogin||',super='||rolsuper||',bypassrls='||rolbypassrls||')', ' ') from pg_roles where rolname like 'pqbr_%'")"
echo "pg_hba localhost: $(docker exec "$C" sh -c "grep -cE '^host\s+all\s+all\s+127.0.0.1/32\s+scram-sha-256' /var/lib/postgresql/data/pg_hba.conf") linha(s) scram"
echo "senha errada: $(H errada pqbr_app 'select 1')"
echo "pqbr_app escreve (desfeito): $(H "$PQBR_APP_PASSWORD" pqbr_app 'begin; insert into pqbr.config_flags (chave, valor, definido_por) values ($$hold_fila$$, false, $$teste$$) on conflict (canal_id, chave) do update set motivo = excluded.motivo; select $$sim$$; rollback;' )"
echo "pqbr_app apaga ações: $(H "$PQBR_APP_PASSWORD" pqbr_app 'delete from pqbr.acoes')"
echo "pqbr_leitura lê temas: $(H "$PQBR_LEITURA_PASSWORD" pqbr_leitura 'select count(*) from pqbr.temas')"
echo "pqbr_leitura escreve: $(H "$PQBR_LEITURA_PASSWORD" pqbr_leitura 'insert into pqbr.acoes (tipo,alvo,motivo,ator) values ($$x$$,$$x$$,$$x$$,$$agente$$)')"
echo "pqbr_leitura lê texto bruto: $(H "$PQBR_LEITURA_PASSWORD" pqbr_leitura 'select texto_bruto from pqbr.comentarios limit 1')"
echo "pqbr_leitura cria tabela em public: $(H "$PQBR_LEITURA_PASSWORD" pqbr_leitura 'create table public.x (i int)')"
