-- PQBR 0015 (t459b, José 12/10/2026): nunca perder pesquisa. Cadernos de pesquisa também são registrados/arquivados;
-- apagar exige arquivo VERIFICADO (Drive + repo + Postgres conferidos) — regra permanente, inclusive para episódios.
begin;
alter table pqbr.cadernos_episodio alter column episodio_codigo drop not null;
alter table pqbr.cadernos_episodio add column classe text not null default 'episodio'
  check (classe in ('episodio', 'pesquisa'));
alter table pqbr.cadernos_episodio add column verificado_em timestamptz;
alter table pqbr.cadernos_episodio add column copias jsonb not null default '{}';   -- {drive: n, repo: n, postgres: n, bytes...}
alter table pqbr.cadernos_episodio add constraint cadernos_episodio_codigo_ep check (classe <> 'episodio' or episodio_codigo is not null);
alter table pqbr.cadernos_episodio drop constraint cadernos_episodio_check;
alter table pqbr.cadernos_episodio add constraint cadernos_episodio_apagar_verificado check (
  apagado_em is null or (arquivado_em is not null and verificado_em is not null and
    (classe <> 'episodio' or (publicado_em is not null and apagado_em >= publicado_em + interval '48 hours'))));
alter table pqbr.arquivo_caderno drop constraint arquivo_caderno_tipo_check;
alter table pqbr.arquivo_caderno add constraint arquivo_caderno_tipo_check
  check (tipo in ('fonte', 'resposta', 'video', 'metadados', 'resumo', 'nota', 'relatorio'));
commit;
-- t459c: isolamento entre cadernos de episódio — toda fonte injetada fica registrada; fonte fora do registro bloqueia a geração.
begin;
create table pqbr.fontes_caderno (
  id          bigint generated always as identity primary key,
  canal_id    text not null default 'pqbr' references pqbr.canais (id),
  caderno_id  text not null references pqbr.cadernos_episodio (caderno_id),
  fonte_id    text not null check (fonte_id ~ '^[0-9a-f-]{36}$'),
  tipo        text not null check (tipo in ('pacote', 'roteiro', 'pesquisa', 'outra')),
  titulo      text,
  criado_em   timestamptz not null default now(),
  unique (caderno_id, fonte_id)
);
alter table pqbr.fontes_caderno enable row level security; alter table pqbr.fontes_caderno force row level security;
create policy fontes_caderno_app on pqbr.fontes_caderno for all to pqbr_app using (true) with check (true);
create policy fontes_caderno_leitura on pqbr.fontes_caderno for select to pqbr_leitura using (true);
grant select, insert, update on pqbr.fontes_caderno to pqbr_app;
grant select on pqbr.fontes_caderno to pqbr_leitura;
commit;
