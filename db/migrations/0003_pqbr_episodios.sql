-- PQBR 0003: episódios, códigos, estados, fichas visuais e auditorias (RF-08, RF-11..RF-16)
begin;

create table pqbr.episodios (
  id            bigint generated always as identity primary key,
  canal_id      text not null default 'pqbr' references pqbr.canais (id),
  codigo        text not null unique check (codigo ~ '^PQBR-EP[0-9]{4,}$'),
  tema_id       bigint not null references pqbr.temas (id),
  grade_id      bigint references pqbr.grade (id),
  estado        text not null default 'em_producao'
                check (estado in ('em_producao', 'aprovado', 'enviando', 'enviado', 'agendado', 'publicado',
                                  'privado', 'revisao_humana', 'descartado')),
  video_id      text unique check (video_id ~ '^[A-Za-z0-9_-]{11}$'),
  janela_em     timestamptz,
  hashes        jsonb not null default '{}'::jsonb,   -- sha256 dos arquivos (vídeo, áudio, legenda)
  workflow_id   text,                                 -- referência ao Temporal (sem consultar o Postgres dele)
  criado_em     timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  -- "enviado" em diante exige video_id
  constraint episodio_video_id_obrigatorio check (estado not in ('enviado', 'agendado', 'publicado', 'privado') or video_id is not null)
);
create index episodios_tema on pqbr.episodios (tema_id);
create index episodios_grade on pqbr.episodios (grade_id);
create index episodios_canal_estado on pqbr.episodios (canal_id, estado);
create trigger episodios_updated before update on pqbr.episodios for each row execute function pqbr.set_updated_at();

-- Histórico de transições (auditoria da máquina de estados)
create table pqbr.episodio_estados (
  id            bigint generated always as identity primary key,
  episodio_id   bigint not null references pqbr.episodios (id) on delete cascade,
  de            text,
  para          text not null,
  motivo        text,
  ator          text not null,     -- 'temporal', 'jose', nome do agente
  em            timestamptz not null default now()
);
create index episodio_estados_ep on pqbr.episodio_estados (episodio_id, em);

create table pqbr.visual_assets (
  id            bigint generated always as identity primary key,
  canal_id      text not null default 'pqbr' references pqbr.canais (id),
  tipo          text not null check (tipo in ('personagem', 'cenario', 'objeto', 'fonte', 'outro')),
  nome          text not null,
  ferramenta    text not null,
  conta_rotulo  text not null,     -- rótulo da conta, nunca e-mail
  gerado_em     timestamptz not null,
  prompt        text,
  versao        text,
  licenca       text,
  status        text not null default 'pendente' check (status in ('pendente', 'verificado', 'rejeitado')),
  sha256        text check (sha256 ~ '^[0-9a-f]{64}$'),
  criado_em     timestamptz not null default now()
);
create index visual_assets_canal_tipo on pqbr.visual_assets (canal_id, tipo);

create table pqbr.episode_assets (
  episodio_id   bigint not null references pqbr.episodios (id) on delete cascade,
  asset_id      bigint not null references pqbr.visual_assets (id),
  uso           text,
  primary key (episodio_id, asset_id)
);
create index episode_assets_asset on pqbr.episode_assets (asset_id);

create table pqbr.auditorias (
  id            bigint generated always as identity primary key,
  episodio_id   bigint not null references pqbr.episodios (id) on delete cascade,
  rodada        smallint not null check (rodada >= 1),
  veredito      text not null check (veredito in ('aprovado', 'reprovado', 'revisao')),
  motivo        text,
  cena_id       text,
  respostas     jsonb not null default '{}'::jsonb,   -- sim/não por pergunta
  modelo        text,
  em            timestamptz not null default now(),
  unique (episodio_id, rodada)
);

alter table pqbr.episodios        enable row level security; alter table pqbr.episodios        force row level security;
alter table pqbr.episodio_estados enable row level security; alter table pqbr.episodio_estados force row level security;
alter table pqbr.visual_assets    enable row level security; alter table pqbr.visual_assets    force row level security;
alter table pqbr.episode_assets   enable row level security; alter table pqbr.episode_assets   force row level security;
alter table pqbr.auditorias       enable row level security; alter table pqbr.auditorias       force row level security;

commit;
