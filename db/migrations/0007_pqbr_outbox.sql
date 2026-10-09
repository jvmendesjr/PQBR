-- PQBR 0007: idempotência do outbox (RF-39, RNF-06). Cada gravação vinda do Temporal leva uma chave única;
-- a Activity grava o dado e a chave na MESMA transação; repetição vira no-op (insert ... on conflict do nothing).
begin;

create table pqbr.outbox_aplicados (
  chave_idempotencia text primary key check (length(chave_idempotencia) between 8 and 300), -- workflow_id:run_id:passo
  canal_id      text not null default 'pqbr' references pqbr.canais (id),
  tabela        text not null,
  registro_id   text,
  workflow_id   text not null,
  aplicado_em   timestamptz not null default now()
);
create index outbox_workflow on pqbr.outbox_aplicados (workflow_id);
create index outbox_canal_em on pqbr.outbox_aplicados (canal_id, aplicado_em);

-- Concede ao service_role (servidor) o acesso às tabelas do esquema; anon/authenticated ficam sem nada.
do $$ begin
  if exists (select 1 from pg_roles where rolname = 'service_role') then
    execute 'grant select, insert, update, delete on all tables in schema pqbr to service_role';
    execute 'grant usage, select on all sequences in schema pqbr to service_role';
    execute 'grant execute on all functions in schema pqbr to service_role';
  end if;
  if exists (select 1 from pg_roles where rolname = 'anon') then
    execute 'revoke all on all tables in schema pqbr from anon';
  end if;
  if exists (select 1 from pg_roles where rolname = 'authenticated') then
    execute 'revoke all on all tables in schema pqbr from authenticated';
  end if;
end $$;
revoke execute on all functions in schema pqbr from public;

alter table pqbr.outbox_aplicados enable row level security;
alter table pqbr.outbox_aplicados force row level security;

commit;
