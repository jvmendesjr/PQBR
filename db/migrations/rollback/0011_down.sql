begin;
drop policy if exists acoes_manut on pqbr.acoes;
drop policy if exists consumo_modelos_manut on pqbr.consumo_modelos;
drop function if exists pqbr.reter_consumo(date, int, int, int);
drop table if exists pqbr.consumo_resumo_diario;
do $$ begin
  if exists (select 1 from pg_roles where rolname = 'pqbr_manutencao') then
    revoke all on all tables in schema pqbr from pqbr_manutencao;
    revoke all on all sequences in schema pqbr from pqbr_manutencao;
    revoke usage on schema pqbr from pqbr_manutencao;
    drop role pqbr_manutencao;
  end if;
end $$;
commit;
