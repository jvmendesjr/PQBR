-- PQBR 0005: métricas, relatórios, consumo e compliance (RF-10, RF-28, RF-30..RF-32)
begin;

create table pqbr.metricas (
  canal_id        text not null default 'pqbr' references pqbr.canais (id),
  video_id        text not null check (video_id ~ '^[A-Za-z0-9_-]{11}$'),
  dia             date not null,
  visualizacoes   bigint check (visualizacoes >= 0),
  minutos_exibidos numeric(14,2),
  duracao_media_s numeric(10,2),
  inscritos_ganhos integer,
  likes           integer,
  comentarios     integer,
  compartilhamentos integer,
  extra           jsonb not null default '{}'::jsonb,
  coletado_em     timestamptz not null default now(),
  primary key (canal_id, video_id, dia)
);
create index metricas_dia on pqbr.metricas (canal_id, dia);

create table pqbr.relatorios (
  id            bigint generated always as identity primary key,
  canal_id      text not null default 'pqbr' references pqbr.canais (id),
  tipo          text not null check (tipo in ('diario', 'semanal', 'consumo', 'compliance', 'excecao')),
  periodo_ini   date not null,
  periodo_fim   date not null check (periodo_fim >= periodo_ini),
  conteudo      jsonb not null,           -- gerado por template
  excecoes      jsonb not null default '[]'::jsonb,
  amostra_significativa boolean,          -- t327: avisar quando não houver números estatisticamente significativos
  gerado_em     timestamptz not null default now(),
  unique (canal_id, tipo, periodo_ini, periodo_fim)
);

create table pqbr.consumo (
  id          bigint generated always as identity primary key,
  canal_id    text not null default 'pqbr' references pqbr.canais (id),
  ferramenta  text not null,             -- notebooklm, jev, youtube_data_api, gemini_web...
  metrica     text not null,
  valor       numeric(18,4) not null,
  custo_estimado_centavos bigint,
  episodio_id bigint references pqbr.episodios (id),
  em          timestamptz not null default now()
);
create index consumo_canal_ferr_em on pqbr.consumo (canal_id, ferramenta, em);
create index consumo_episodio on pqbr.consumo (episodio_id);

create table pqbr.compliance_eventos (
  id            bigint generated always as identity primary key,
  canal_id      text not null default 'pqbr' references pqbr.canais (id),
  origem        text not null check (origem in ('email', 'studio', 'data_api', 'outro')),
  gravidade     text not null check (gravidade in ('info', 'atencao', 'critico')),
  resumo        text not null,
  prazo_recurso timestamptz,
  status        text not null default 'aberto' check (status in ('aberto', 'em_analise', 'resolvido')),
  em            timestamptz not null default now()
);
create index compliance_canal_status on pqbr.compliance_eventos (canal_id, status, gravidade);

alter table pqbr.metricas           enable row level security; alter table pqbr.metricas           force row level security;
alter table pqbr.relatorios         enable row level security; alter table pqbr.relatorios         force row level security;
alter table pqbr.consumo            enable row level security; alter table pqbr.consumo            force row level security;
alter table pqbr.compliance_eventos enable row level security; alter table pqbr.compliance_eventos force row level security;

commit;
