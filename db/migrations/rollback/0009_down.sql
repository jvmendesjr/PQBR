do $$ declare t text; begin
  for t in select tablename from pg_tables where schemaname = 'pqbr' loop
    execute format('drop policy if exists %I on pqbr.%I', t || '_app', t);
  end loop;
end $$;
do $$ begin
  if exists (select 1 from pg_roles where rolname = 'pqbr_app') then
    execute 'revoke all on all tables in schema pqbr from pqbr_app';
    execute 'revoke all on all sequences in schema pqbr from pqbr_app';
    execute 'revoke all on all functions in schema pqbr from pqbr_app';
    execute 'revoke all on schema pqbr from pqbr_app';
  end if;
end $$;
