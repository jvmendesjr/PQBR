-- PQBR 0019 (José 25/10/2026 14:09): catálogo de erros de produção. Agentes internos só leem (pqbr_leitura);
-- quem cadastra é o agente externo (via pqbr_app/manutenção, com OK do José). Sem delete: desativar com ativo=false.
begin;
create table pqbr.catalogo_erros (
  id                  bigint generated always as identity primary key,
  codigo              text not null unique check (codigo ~ '^ERR-[A-Z]{3}-[0-9]{2}$'),
  categoria           text not null check (categoria in ('estilo','personagem','roteiro','montagem','texto_na_imagem','compliance','custo')),
  descricao           text not null check (length(descricao) between 10 and 1000),
  exemplo             jsonb not null default '{}'::jsonb,      -- {"tema": "...", "caminho": "..."}
  prevencao           text not null check (length(prevencao) between 10 and 2000),  -- instrução para prompt/checagem
  severidade          text not null check (severidade in ('baixa','media','alta','bloqueante')),
  papeis_interessados text[] not null default '{}' check (cardinality(papeis_interessados) >= 1),
  ativo               boolean not null default true,
  criado_em           timestamptz not null default now()
);
create index catalogo_erros_ativos on pqbr.catalogo_erros using gin (papeis_interessados) where ativo;
alter table pqbr.catalogo_erros enable row level security;
alter table pqbr.catalogo_erros force row level security;
create policy catalogo_erros_app on pqbr.catalogo_erros for all to pqbr_app using (true) with check (true);
create policy catalogo_erros_leitura on pqbr.catalogo_erros for select to pqbr_leitura using (true);
grant select, insert, update on pqbr.catalogo_erros to pqbr_app;
grant select on pqbr.catalogo_erros to pqbr_leitura;
commit;
