do $$ declare t text; begin
  for t in select tablename from pg_tables where schemaname = 'pqbr' loop
    execute format('drop policy if exists %I on pqbr.%I', t || '_leitura', t);
  end loop;
end $$;
drop table if exists pqbr.outbox_aplicados;
do $$ begin
  if exists (select 1 from pg_roles where rolname = 'pqbr_leitura') then
    execute 'revoke all on all tables in schema pqbr from pqbr_leitura';
    execute 'revoke all on schema pqbr from pqbr_leitura';
  end if;
end $$;
