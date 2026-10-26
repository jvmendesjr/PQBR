-- PQBR 0020 (t540/t541, F8-01): agenda de publicação idempotente + flag global de pausa + auditoria de privacidade.
-- RASCUNHO, NÃO APLICADA: aplicar exige OK do José. Rollback: rollback/0020_down.sql. Sem delete (nunca apagar).
begin;
create table pqbr.agenda_publicacao (
  codigo        text primary key check (codigo ~ '^PQBR-EP[0-9]{4,}$'),
  sha256        text not null check (sha256 ~ '^[0-9a-f]{64}$'),
  horario       timestamptz not null unique,                     -- 1 vídeo por janela (11:40 / 18:35 America/Fortaleza)
  estado        text not null default 'reservado'
                check (estado in ('reservado','enviado_privado','publicado','privado','revertido','reprovado','erro')),
  video_id      text unique check (video_id ~ '^[A-Za-z0-9_-]{11}$'),
  workflow_id   text not null,
  simulado      boolean not null default true,
  atualizado_em timestamptz not null default now()
);
create table pqbr.controle_publicacao (
  id        int primary key default 1 check (id = 1),               -- linha única
  pausado   boolean not null default true,                          -- fail-closed: nasce pausado
  desde     timestamptz not null default now(),
  autor_id  text not null default 'sistema',
  motivo    text not null default 'instalação (fail-closed)'
);
insert into pqbr.controle_publicacao (id) values (1);
create table pqbr.auditoria_publicacao (
  id        bigint generated always as identity primary key,
  acao      text not null check (acao in ('pausar','retomar','privar','reverter','publicar')),
  alvo      text not null,
  video_id  text,
  motivo    text not null,
  autor_id  text not null,
  origem    text not null check (origem in ('telegram','sinal','sistema')),
  simulado  boolean not null,
  update_id bigint unique,                                          -- dedupe do comando Telegram
  em        timestamptz not null default now()
);
do $$ declare t text; begin
  foreach t in array array['agenda_publicacao','controle_publicacao','auditoria_publicacao'] loop
    execute format('alter table pqbr.%I enable row level security; alter table pqbr.%I force row level security', t, t);
    execute format('create policy %I on pqbr.%I for all to pqbr_app using (true) with check (true)', t||'_app', t);
    execute format('create policy %I on pqbr.%I for select to pqbr_leitura using (true)', t||'_leitura', t);
    execute format('grant select, insert, update on pqbr.%I to pqbr_app; grant select on pqbr.%I to pqbr_leitura', t, t);
  end loop; end $$;
commit;
