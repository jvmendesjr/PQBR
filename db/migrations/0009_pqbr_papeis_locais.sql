-- PQBR 0009: papéis para Postgres local (t343). Substitui o service_role do Supabase.
--   pqbr_app      escritor, usado só pelo worker do Temporal (Activities/outbox).
--   pqbr_leitura  só-leitura (criado em 0007), sem texto bruto de comentário.
-- Os papéis nascem sem login; login e senha são definidos fora das migrações
-- (infra/pqbr-db/configurar_papeis.sh, senha só no .env do servidor).
begin;
do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'pqbr_app') then
    create role pqbr_app nologin;
  end if;
end $$;
grant usage on schema pqbr to pqbr_app;
grant select, insert, update, delete on all tables in schema pqbr to pqbr_app;
grant usage, select on all sequences in schema pqbr to pqbr_app;
grant execute on all functions in schema pqbr to pqbr_app;
-- Sem DELETE nas tabelas de auditoria e de outbox (histórico imutável para o app)
revoke delete on pqbr.episodio_estados, pqbr.acoes, pqbr.outbox_aplicados, pqbr.auditorias from pqbr_app;
-- RLS forçado: política explícita para o escritor
do $$ declare t text; begin
  for t in select tablename from pg_tables where schemaname = 'pqbr' loop
    execute format('create policy %I on pqbr.%I for all to pqbr_app using (true) with check (true)', t || '_app', t);
  end loop;
end $$;
commit;
