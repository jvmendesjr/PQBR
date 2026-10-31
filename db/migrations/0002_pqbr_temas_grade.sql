-- PQBR 0002: temas (R10) e grade (RF-01..RF-05)
begin;

create table pqbr.temas (
  id               bigint generated always as identity primary key,
  canal_id         text not null default 'pqbr' references pqbr.canais (id),
  tema             text not null check (length(tema) between 3 and 300),
  tema_normalizado text not null check (length(tema_normalizado) between 3 and 300),  -- minúsculas, sem acento/pontuação (código)
  origem           text not null check (origem in ('em_alta', 'perene', 'jose', 'legado')),
  status           text not null default 'proposto'
                   check (status in ('proposto', 'aprovado', 'em_producao', 'publicado', 'recusado_r10', 'descartado')),
  video_id         text unique check (video_id ~ '^[A-Za-z0-9_-]{11}$'),  -- legado: vídeo do YouTube do CSV; publicações novas ficam em pqbr.publicacoes
  publicado_em     date,
  repete_n         smallint check (repete_n >= 0),       -- legado do CSV
  motivo_recusa    text,
  criado_em        timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);
-- R10: um tema, um vídeo (barreira exata no banco; variações próximas são barradas em código, pg_trgm como apoio)
-- Exceção: repetições históricas do CSV (repete_n preenchido, anteriores à R10) ficam registradas, fora do índice.
create unique index temas_r10_unico on pqbr.temas (canal_id, tema_normalizado)
  where status not in ('recusado_r10', 'descartado') and repete_n is null;
create index temas_canal_status on pqbr.temas (canal_id, status);
create trigger temas_updated before update on pqbr.temas for each row execute function pqbr.set_updated_at();

create table pqbr.grade (
  id          bigint generated always as identity primary key,
  canal_id    text not null default 'pqbr' references pqbr.canais (id),
  data        date not null,
  janela      time not null check (janela in ('11:40', '14:40', '18:35', '21:15')),  -- Fortaleza (t324–t326)
  tema_id     bigint not null references pqbr.temas (id),
  polemica    smallint not null check (polemica between 0 and 100),
  fonte       text not null check (fonte in ('em_alta', 'perene', 'reserva')),
  status      text not null default 'planejado'
              check (status in ('planejado', 'aguardando_jose', 'em_producao', 'agendado', 'publicado', 'trocado', 'cancelado')),
  criado_em   timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  unique (canal_id, data, janela)
);
create index grade_tema on pqbr.grade (tema_id);
create trigger grade_updated before update on pqbr.grade for each row execute function pqbr.set_updated_at();

alter table pqbr.temas enable row level security;  alter table pqbr.temas force row level security;
alter table pqbr.grade enable row level security;  alter table pqbr.grade force row level security;

commit;
