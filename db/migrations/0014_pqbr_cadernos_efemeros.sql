-- PQBR 0014 (t459, José 12/10/2026): cadernos efêmeros. Pacote canônico do NotebookLM (persona, comandos/prompts,
-- contrato editorial, bloco visual §16.7) versionado por hash — fonte de verdade aqui; espelho no Drive 00_Biblia_Visual.
-- Sem caderno mestre permanente. Registro de cada caderno por episódio (casar por código, nunca por título) e do
-- arquivamento (fontes/respostas/vídeo) antes de apagar o caderno em D+2 após a publicação.
begin;
create table pqbr.pacote_canonico (
  id            bigint generated always as identity primary key,
  canal_id      text not null default 'pqbr' references pqbr.canais (id),
  hash          text not null unique check (hash ~ '^[0-9a-f]{64}$'),   -- sha256 do JSON canônico dos itens
  itens         jsonb not null,                                          -- {nome: texto}; sem segredo/PII
  origem        jsonb not null default '{}',                             -- arquivo/commit de cada item
  drive_ids     jsonb not null default '{}',                             -- {arquivo: id} em 00_Biblia_Visual
  criado_em     timestamptz not null default now(),
  ativo         boolean not null default false
);
create unique index pacote_canonico_um_ativo on pqbr.pacote_canonico (canal_id) where ativo;

create table pqbr.cadernos_episodio (
  id               bigint generated always as identity primary key,
  canal_id         text not null default 'pqbr' references pqbr.canais (id),
  caderno_id       text not null unique check (caderno_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'),
  episodio_codigo  text not null check (episodio_codigo ~ '^PQBR-EP[0-9]{4,}$'),
  slug             text not null,
  titulo           text not null,
  pacote_hash      text references pqbr.pacote_canonico (hash),
  criado_em        timestamptz not null default now(),
  publicado_em     timestamptz,
  arquivado_em     timestamptz,
  apagar_apos      timestamptz,                            -- publicado_em + 48 h (gravado pelo workflow)
  apagado_em       timestamptz,
  check (apagado_em is null or (arquivado_em is not null and publicado_em is not null and apagado_em >= publicado_em + interval '48 hours'))
);
create unique index cadernos_episodio_vivo on pqbr.cadernos_episodio (canal_id, episodio_codigo) where apagado_em is null;

create table pqbr.arquivo_caderno (
  id               bigint generated always as identity primary key,
  canal_id         text not null default 'pqbr' references pqbr.canais (id),
  caderno_id       text not null references pqbr.cadernos_episodio (caderno_id),
  tipo             text not null check (tipo in ('fonte', 'resposta', 'video', 'metadados')),
  nome             text not null,
  sha256           text not null check (sha256 ~ '^[0-9a-f]{64}$'),
  bytes            bigint not null check (bytes >= 0),
  drive_id         text,
  conteudo         text,                                   -- texto (fontes/respostas); vídeo só no Drive
  criado_em        timestamptz not null default now(),
  unique (caderno_id, tipo, nome)
);
create index arquivo_caderno_cad on pqbr.arquivo_caderno (caderno_id);

alter table pqbr.pacote_canonico enable row level security; alter table pqbr.pacote_canonico force row level security;
alter table pqbr.cadernos_episodio enable row level security; alter table pqbr.cadernos_episodio force row level security;
alter table pqbr.arquivo_caderno enable row level security; alter table pqbr.arquivo_caderno force row level security;
create policy pacote_canonico_app on pqbr.pacote_canonico for all to pqbr_app using (true) with check (true);
create policy pacote_canonico_leitura on pqbr.pacote_canonico for select to pqbr_leitura using (true);
create policy cadernos_episodio_app on pqbr.cadernos_episodio for all to pqbr_app using (true) with check (true);
create policy cadernos_episodio_leitura on pqbr.cadernos_episodio for select to pqbr_leitura using (true);
create policy arquivo_caderno_app on pqbr.arquivo_caderno for all to pqbr_app using (true) with check (true);
create policy arquivo_caderno_leitura on pqbr.arquivo_caderno for select to pqbr_leitura using (true);
grant select, insert, update on pqbr.pacote_canonico, pqbr.cadernos_episodio, pqbr.arquivo_caderno to pqbr_app;
grant select on pqbr.pacote_canonico, pqbr.cadernos_episodio, pqbr.arquivo_caderno to pqbr_leitura;
commit;
