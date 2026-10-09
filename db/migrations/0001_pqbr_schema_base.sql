-- PQBR 0001: esquema dedicado, canais, flags e utilitários (F3-01 / D3; ARQUITETURA §8)
-- Projeto Supabase: o mesmo do Paperclip (decisão 3 do DECISOES-LOG). Nada é criado em "public".
-- O esquema "pqbr" NÃO deve ser exposto na Data API; acesso só no servidor (service_role ou papel próprio, a decidir).
begin;

create schema if not exists pqbr;
comment on schema pqbr is 'PQBR: dados de negócio (Temporal guarda só estado de workflow). Sem segredos nem PII.';

-- Ninguém além do dono e do service_role enxerga o esquema.
revoke all on schema pqbr from public;
do $$ begin
  if exists (select 1 from pg_roles where rolname = 'anon') then execute 'revoke all on schema pqbr from anon'; end if;
  if exists (select 1 from pg_roles where rolname = 'authenticated') then execute 'revoke all on schema pqbr from authenticated'; end if;
  if exists (select 1 from pg_roles where rolname = 'service_role') then execute 'grant usage on schema pqbr to service_role'; end if;
end $$;

-- updated_at automático
create or replace function pqbr.set_updated_at() returns trigger
language plpgsql set search_path = '' as $$
begin
  new.updated_at := now();
  return new;
end $$;

-- Canais (escopo atual: só PQBR; coluna canal_id nas tabelas para o futuro multi-canal, t327)
create table pqbr.canais (
  id          text primary key check (id ~ '^[a-z0-9_]{2,32}$'),
  nome        text not null,
  ativo       boolean not null default true,
  criado_em   timestamptz not null default now()
);
insert into pqbr.canais (id, nome) values ('pqbr', 'Porquê BR');

-- Plataformas (t339–t344): modelo genérico; hoje só YouTube. Esquema detalhado por rede: EM CONSTRUÇÃO.
create table pqbr.plataformas (
  id          text primary key check (id ~ '^[a-z0-9_]{2,32}$'),
  nome        text not null,
  ativa       boolean not null default false
);
-- Só o YouTube no escopo atual. Outras redes = sugestão futura, fora do escopo atual (t343–t344).
insert into pqbr.plataformas (id, nome, ativa) values ('youtube', 'YouTube Shorts', true);

-- Contas do canal em cada plataforma (rótulo, nunca e-mail ou login)
create table pqbr.canal_plataformas (
  canal_id      text not null references pqbr.canais (id),
  plataforma_id text not null references pqbr.plataformas (id),
  conta_rotulo  text not null,
  conta_externa_id text,                 -- ID público do canal/perfil na plataforma
  ativo         boolean not null default false,
  primary key (canal_id, plataforma_id)
);
create index canal_plataformas_plataforma on pqbr.canal_plataformas (plataforma_id);
insert into pqbr.canal_plataformas (canal_id, plataforma_id, conta_rotulo, ativo) values ('pqbr', 'youtube', 'Porquê BR (YouTube)', true);

-- Flags operacionais: kill switch das respostas, HOLD da fila (RF-26, RF-28)
create table pqbr.config_flags (
  canal_id    text not null default 'pqbr' references pqbr.canais (id),
  chave       text not null check (chave in ('respostas_pausadas', 'hold_fila', 'publicacao_pausada')),
  valor       boolean not null default false,
  motivo      text,
  definido_por text not null,             -- 'jose', 'compliance', 'sistema' (nunca e-mail ou ID pessoal)
  updated_at  timestamptz not null default now(),
  primary key (canal_id, chave)
);
create trigger config_flags_updated before update on pqbr.config_flags
  for each row execute function pqbr.set_updated_at();
insert into pqbr.config_flags (chave, valor, definido_por) values
  ('respostas_pausadas', false, 'sistema'), ('hold_fila', false, 'sistema'), ('publicacao_pausada', false, 'sistema');

alter table pqbr.canais enable row level security;
alter table pqbr.canais force row level security;
alter table pqbr.plataformas enable row level security;
alter table pqbr.plataformas force row level security;
alter table pqbr.canal_plataformas enable row level security;
alter table pqbr.canal_plataformas force row level security;
alter table pqbr.config_flags enable row level security;
alter table pqbr.config_flags force row level security;

commit;
