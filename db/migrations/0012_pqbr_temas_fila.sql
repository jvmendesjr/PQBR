-- PQBR 0012 (t427): fila de temas (pendentes → publicados), catálogo de produções e anti-repetição.
-- Categorias: 80% perene (expressao, habito_mania, curiosidade_cultura_pop) + ≤20% sazonal (CONTRATO §16.5).
begin;
create extension if not exists pg_trgm;

create table pqbr.temas_pendentes (
  id                bigint generated always as identity primary key,
  canal_id          text not null default 'pqbr' references pqbr.canais (id),
  slug              text not null unique check (slug ~ '^[a-z0-9][a-z0-9-]{1,60}$'),
  tema              text not null check (length(tema) between 3 and 300),
  tema_normalizado  text not null check (length(tema_normalizado) between 3 and 300),
  categoria         text not null check (categoria in ('expressao', 'habito_mania', 'curiosidade_cultura_pop', 'sazonal')),
  janela_sazonal    daterange,                         -- só sazonal: 30 dias antes da data (Caçador)
  data_prevista     date,                              -- folga: fila ≥ 7 dias à frente
  status            text not null default 'proposto'
                    check (status in ('proposto', 'aprovado', 'em_producao', 'auditado', 'pronto_publicar', 'falhou')),
  fontes            jsonb not null default '[]',       -- ≥ 2 fontes (§16.5)
  bloco_visual      jsonb,                             -- RoteiroShort.bloco_visual (§16.4)
  metadados         jsonb not null default '{}',       -- pontuação, polemica, origem, caderno NLM, SEO, código PQBR-EP
  caminhos          jsonb not null default '{}',       -- raw/final/pranchas (local) + ids/paths no Drive
  criado_por        text not null default 'codigo',
  criado_em         timestamptz not null default now(),
  updated_at        timestamptz not null default now(),
  check (categoria <> 'sazonal' or janela_sazonal is not null)
);
create unique index temas_pendentes_norm on pqbr.temas_pendentes (canal_id, tema_normalizado);
create index temas_pendentes_data on pqbr.temas_pendentes (canal_id, data_prevista) where status <> 'falhou';
create index temas_pendentes_trgm on pqbr.temas_pendentes using gin (tema_normalizado gin_trgm_ops);
create trigger temas_pendentes_updated before update on pqbr.temas_pendentes for each row execute function pqbr.set_updated_at();

create table pqbr.temas_publicados (
  id                bigint primary key,                -- mesmo id do pendente (movido)
  canal_id          text not null default 'pqbr' references pqbr.canais (id),
  slug              text not null unique,
  tema              text not null,
  tema_normalizado  text not null,
  categoria         text not null,
  codigo            text not null unique check (codigo ~ '^PQBR-EP[0-9]{4,}$'),
  video_id          text unique check (video_id ~ '^[A-Za-z0-9_-]{11}$'),
  publicado_em      timestamptz not null default now(),
  privacidade       text not null default 'private' check (privacidade in ('private', 'public', 'scheduled')),
  fontes            jsonb not null default '[]',
  bloco_visual      jsonb,
  metadados         jsonb not null default '{}',
  caminhos          jsonb not null default '{}'
);
create unique index temas_publicados_norm on pqbr.temas_publicados (canal_id, tema_normalizado);
create index temas_publicados_trgm on pqbr.temas_publicados using gin (tema_normalizado gin_trgm_ops);

-- Anti-repetição antes de criar tema: exato nas duas tabelas + legado (pqbr.temas) e parecido por trigram.
create or replace function pqbr.tema_parecido(p_norm text, p_limiar real default 0.55)
returns table (origem text, tema text, similaridade real) language sql stable as $$
  select 'pendente', tema, similarity(tema_normalizado, p_norm) from pqbr.temas_pendentes where similarity(tema_normalizado, p_norm) >= p_limiar
  union all
  select 'publicado', tema, similarity(tema_normalizado, p_norm) from pqbr.temas_publicados where similarity(tema_normalizado, p_norm) >= p_limiar
  union all
  select 'legado', tema, similarity(tema_normalizado, p_norm) from pqbr.temas where similarity(tema_normalizado, p_norm) >= p_limiar
  order by 3 desc
$$;

create or replace function pqbr.barrar_tema_repetido() returns trigger language plpgsql as $$
begin
  if exists (select 1 from pqbr.temas_publicados where canal_id = new.canal_id and tema_normalizado = new.tema_normalizado)
     or exists (select 1 from pqbr.temas where canal_id = new.canal_id and tema_normalizado = new.tema_normalizado
                and status not in ('recusado_r10', 'descartado')) then
    raise exception 'tema repetido (R10): %', new.tema using errcode = 'unique_violation';
  end if;
  return new;
end $$;
create trigger temas_pendentes_r10 before insert on pqbr.temas_pendentes for each row execute function pqbr.barrar_tema_repetido();

-- Publicar = mover (transação única). Só pronto_publicar.
create or replace function pqbr.publicar_tema(p_id bigint, p_codigo text, p_video_id text, p_privacidade text default 'private')
returns bigint language plpgsql as $$
declare r pqbr.temas_pendentes;
begin
  select * into r from pqbr.temas_pendentes where id = p_id for update;
  if not found then raise exception 'tema % não está pendente', p_id; end if;
  if r.status <> 'pronto_publicar' then raise exception 'tema % em status %, esperado pronto_publicar', p_id, r.status; end if;
  insert into pqbr.temas_publicados (id, canal_id, slug, tema, tema_normalizado, categoria, codigo, video_id, privacidade,
                                     fontes, bloco_visual, metadados, caminhos)
  values (r.id, r.canal_id, r.slug, r.tema, r.tema_normalizado, r.categoria, p_codigo, p_video_id, p_privacidade,
          r.fontes, r.bloco_visual, r.metadados, r.caminhos);
  delete from pqbr.temas_pendentes where id = p_id;
  return p_id;
end $$;

-- Folga da fila (meta ≥ 7 dias) e mix 80/20 dos pendentes.
create or replace view pqbr.fila_folga as
  select canal_id,
         count(*) filter (where status <> 'falhou') as pendentes,
         coalesce(max(data_prevista) filter (where status <> 'falhou') - current_date, 0) as dias_a_frente,
         round(100.0 * count(*) filter (where categoria = 'sazonal') / nullif(count(*), 0), 1) as pct_sazonal
  from pqbr.temas_pendentes group by canal_id;

alter table pqbr.temas_pendentes enable row level security;  alter table pqbr.temas_pendentes force row level security;
alter table pqbr.temas_publicados enable row level security; alter table pqbr.temas_publicados force row level security;
create policy temas_pendentes_app on pqbr.temas_pendentes for all to pqbr_app using (true) with check (true);
create policy temas_publicados_app on pqbr.temas_publicados for all to pqbr_app using (true) with check (true);
create policy temas_pendentes_leitura on pqbr.temas_pendentes for select to pqbr_leitura using (true);
create policy temas_publicados_leitura on pqbr.temas_publicados for select to pqbr_leitura using (true);
grant select, insert, update, delete on pqbr.temas_pendentes, pqbr.temas_publicados to pqbr_app;
grant select on pqbr.temas_pendentes, pqbr.temas_publicados, pqbr.fila_folga to pqbr_leitura;
grant execute on function pqbr.tema_parecido(text, real), pqbr.publicar_tema(bigint, text, text, text) to pqbr_app;
commit;
