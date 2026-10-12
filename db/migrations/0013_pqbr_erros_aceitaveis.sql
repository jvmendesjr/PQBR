-- PQBR 0013 (t435): erros aceitáveis. O Auditor registra aqui erros sem risco de segurança (ex.: legenda do
-- NotebookLM com palavra errada) em vez de reprovar. Só segurança reprova (CONTRATO §16.4 item 6).
-- Revisão da tabela pelo José/Observador depois dos primeiros dias (ROADMAP ERR-01).
begin;
create table pqbr.erros_aceitaveis (
  id                bigint generated always as identity primary key,
  canal_id          text not null default 'pqbr' references pqbr.canais (id),
  episodio_codigo   text check (episodio_codigo ~ '^PQBR-EP[0-9]{4,}$'),
  tema_slug         text,                                  -- antes do código existir (temas_pendentes.slug)
  cena              text check (cena ~ '^S[0-9]{2,}$'),
  categoria         text not null check (categoria in ('legenda', 'texto', 'visual', 'audio', 'loop', 'outro')),
  chave             text not null,                         -- chave do auditor (ex.: legenda_com_erro)
  descricao         text not null check (length(descricao) between 3 and 500),
  gravidade         text not null default 'leve' check (gravidade in ('leve', 'media')),
  veredito_auditor  text not null check (veredito_auditor in ('aprova', 'aprova_com_ressalva', 'terceira_rodada')),
  rodadas           smallint not null default 2 check (rodadas between 1 and 3),
  evidencia         jsonb not null default '{}',           -- votos por rodada, caminho da prancha; sem segredo/PII
  criado_por        text not null default 'auditor',
  criado_em         timestamptz not null default now(),
  decisao           text not null default 'pendente'
                    check (decisao in ('pendente', 'aceito', 'corrigir_prompt', 'virar_seguranca')),
  revisado_por      text,
  revisado_em       timestamptz,
  check (episodio_codigo is not null or tema_slug is not null),
  check (decisao = 'pendente' or (revisado_por is not null and revisado_em is not null))
);
create index erros_aceitaveis_ep on pqbr.erros_aceitaveis (canal_id, episodio_codigo);
create index erros_aceitaveis_pend on pqbr.erros_aceitaveis (canal_id, categoria) where decisao = 'pendente';

create or replace view pqbr.erros_aceitaveis_resumo as
  select canal_id, categoria, chave, count(*) as total,
         count(*) filter (where decisao = 'pendente') as pendentes,
         min(criado_em) as primeiro, max(criado_em) as ultimo
  from pqbr.erros_aceitaveis group by canal_id, categoria, chave;

alter table pqbr.erros_aceitaveis enable row level security; alter table pqbr.erros_aceitaveis force row level security;
create policy erros_aceitaveis_app on pqbr.erros_aceitaveis for all to pqbr_app using (true) with check (true);
create policy erros_aceitaveis_leitura on pqbr.erros_aceitaveis for select to pqbr_leitura using (true);
grant select, insert, update on pqbr.erros_aceitaveis to pqbr_app;
grant select on pqbr.erros_aceitaveis, pqbr.erros_aceitaveis_resumo to pqbr_leitura;
commit;
