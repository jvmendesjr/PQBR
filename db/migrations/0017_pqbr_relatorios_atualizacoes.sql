-- PQBR 0017 (t516/t517, José 24/10/2026): relatório semanal do vigia de atualizações (Dev). Só leitura + proposta; nunca aplica.
begin;
create table pqbr.relatorios_atualizacoes (
  id          bigint generated always as identity primary key,
  canal_id    text not null default 'pqbr' references pqbr.canais (id),
  semana      text not null check (semana ~ '^[0-9]{4}w[0-9]{2}$'),
  resumo      text not null,
  itens       jsonb not null,
  versao_contrato text not null default '1.0.0',
  criado_em   timestamptz not null default now()
);
alter table pqbr.relatorios_atualizacoes enable row level security; alter table pqbr.relatorios_atualizacoes force row level security;
create policy relatorios_atualizacoes_app on pqbr.relatorios_atualizacoes for all to pqbr_app using (true) with check (true);
create policy relatorios_atualizacoes_leitura on pqbr.relatorios_atualizacoes for select to pqbr_leitura using (true);
grant select, insert on pqbr.relatorios_atualizacoes to pqbr_app;
grant select on pqbr.relatorios_atualizacoes to pqbr_leitura;
commit;
