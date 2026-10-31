-- PQBR 0004: comentários, respostas, frases e ações (RF-19..RF-27). Autor só como hash; texto bruto expira em 30 dias.
begin;

create table pqbr.comentarios (
  id                 bigint generated always as identity primary key,
  canal_id           text not null default 'pqbr' references pqbr.canais (id),
  plataforma_id      text not null default 'youtube' references pqbr.plataformas (id),
  external_id        text not null,                    -- ID do comentário na plataforma
  post_external_id   text not null,                    -- ID do vídeo/post comentado (cobre vídeos legados)
  publicacao_id      bigint references pqbr.publicacoes (id),
  autor_hash         text not null check (autor_hash ~ '^[0-9a-f]{64}$'),  -- HMAC-SHA256 com chave fora do banco
  texto_bruto        text,                             -- apagado em até 30 dias
  texto_expira_em    timestamptz not null default (now() + interval '30 days'),
  rotulos            text[] not null default '{}',
  gravidade          text check (gravidade in ('nenhuma', 'baixa', 'grave', 'muito_grave')),
  acao               text check (acao in ('nenhuma', 'responder', 'coracao', 'reter', 'sinal_item5', 'escalar_jose')),
  publicado_em       timestamptz not null,
  lido_em            timestamptz not null default now(),
  unique (plataforma_id, external_id)
);
create index comentarios_post on pqbr.comentarios (canal_id, plataforma_id, post_external_id, publicado_em);
create index comentarios_publicacao on pqbr.comentarios (publicacao_id);
create index comentarios_expira on pqbr.comentarios (texto_expira_em) where texto_bruto is not null;
create index comentarios_autor_post on pqbr.comentarios (autor_hash, plataforma_id, post_external_id);

create table pqbr.frases (
  id          bigint generated always as identity primary key,
  canal_id    text not null default 'pqbr' references pqbr.canais (id),
  texto       text not null,
  aprovada    boolean not null default false,       -- banco de 60 frases aprovado pelo José (F10-01)
  criado_em   timestamptz not null default now(),
  unique (canal_id, texto)
);

create table pqbr.respostas (
  id              bigint generated always as identity primary key,
  canal_id        text not null default 'pqbr' references pqbr.canais (id),
  comentario_id   bigint not null references pqbr.comentarios (id),
  frase_id        bigint not null references pqbr.frases (id),
  plataforma_id   text not null references pqbr.plataformas (id),
  post_external_id text not null,
  autor_hash      text not null,
  enviada_em      timestamptz,
  conferida_60min boolean,
  criado_em       timestamptz not null default now(),
  unique (comentario_id),
  unique (plataforma_id, post_external_id, autor_hash)  -- 1 resposta por pessoa por vídeo/post (REGRAS §18)
);
create index respostas_plataforma on pqbr.respostas (plataforma_id);
create index respostas_frase on pqbr.respostas (frase_id, enviada_em);
create index respostas_canal_enviada on pqbr.respostas (canal_id, enviada_em);

create table pqbr.acoes (
  id          bigint generated always as identity primary key,
  canal_id    text not null default 'pqbr' references pqbr.canais (id),
  plataforma_id text references pqbr.plataformas (id),  -- null = ação geral (ex.: HOLD)
  tipo        text not null,              -- ex.: tornar_privado, reter, hold, retomar
  alvo        text not null,              -- external_id do post/comentário ou código do episódio
  motivo      text not null,
  ator        text not null,
  em          timestamptz not null default now()
);
create index acoes_canal_em on pqbr.acoes (canal_id, em);
create index acoes_plataforma on pqbr.acoes (plataforma_id);

-- Limpeza do texto bruto (rodar por job agendado do Temporal; aqui só a função)
create or replace function pqbr.expirar_textos_comentarios() returns integer
language sql set search_path = '' as $$
  with x as (update pqbr.comentarios set texto_bruto = null
             where texto_bruto is not null and texto_expira_em <= now() returning 1)
  select count(*)::integer from x;
$$;

alter table pqbr.comentarios enable row level security; alter table pqbr.comentarios force row level security;
alter table pqbr.frases      enable row level security; alter table pqbr.frases      force row level security;
alter table pqbr.respostas   enable row level security; alter table pqbr.respostas   force row level security;
alter table pqbr.acoes       enable row level security; alter table pqbr.acoes       force row level security;

commit;
