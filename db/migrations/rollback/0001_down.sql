-- Remove TUDO do PQBR (só o esquema pqbr e o papel pqbr_leitura).
drop schema if exists pqbr cascade;
do $$ begin if exists (select 1 from pg_roles where rolname = 'pqbr_leitura') then execute 'drop role pqbr_leitura'; end if; end $$;
