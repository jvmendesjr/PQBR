-- PQBR 0006: propostas dos agentes, tickets e fila de revisão humana (RF-33..RF-36)
begin;

create table pqbr.propostas (
  id            bigint generated always as identity primary key,
  canal_id      text not null default 'pqbr' references pqbr.canais (id),
  agente        text not null,
  tipo          text not null,
  conteudo      jsonb not null,          -- PropostaAgente validada (Pydantic v2)
  status        text not null default 'aguardando'
                check (status in ('aguardando', 'aprovada', 'negada', 'aplicada', 'rejeitada_validacao')),
  workflow_id   text,
  issue_paperclip text,
  decidido_por  text,
  decidido_em   timestamptz,
  criado_em     timestamptz not null default now()
);
create index propostas_canal_status on pqbr.propostas (canal_id, status);

create table pqbr.tickets (
  id            bigint generated always as identity primary key,
  canal_id      text not null default 'pqbr' references pqbr.canais (id),
  titulo        text not null,
  localizacao   text not null,
  falha         text not null,
  correcoes     jsonb not null default '[]'::jsonb,
  status        text not null default 'aberto'
                check (status in ('aberto', 'aprovado_abertura', 'em_execucao', 'aguardando_merge', 'aprovado_merge', 'fechado', 'negado')),
  aprovacao_1_em timestamptz,          -- abertura (com pedido de correção), t324
  aprovacao_2_em timestamptz,          -- merge
  issue_paperclip text,
  criado_em     timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  constraint ticket_ordem_aprovacoes check (aprovacao_2_em is null or aprovacao_1_em is not null)
);
create index tickets_canal_status on pqbr.tickets (canal_id, status);
create trigger tickets_updated before update on pqbr.tickets for each row execute function pqbr.set_updated_at();

-- Fila de revisão humana: último recurso (t327). Local [PROPOSTA]: esta tabela + Drive 04_Privados_Revisao.
create table pqbr.revisao_humana (
  id               bigint generated always as identity primary key,
  canal_id         text not null default 'pqbr' references pqbr.canais (id),
  item_tipo        text not null check (item_tipo in ('episodio', 'tema', 'comentario', 'asset', 'outro')),
  item_ref         text not null,
  episodio_id      bigint references pqbr.episodios (id),
  caminhos_tentados jsonb not null default '[]'::jsonb,
  local_arquivo    text,                 -- caminho no Drive (sem link público)
  status           text not null default 'pendente' check (status in ('pendente', 'decidido', 'executado')),
  determinacao     text check (determinacao in ('excluir', 'corrigir', 'reaproveitar', 'arquivar')),
  observacao_jose  text,
  avisado_em       timestamptz,
  decidido_em      timestamptz,
  criado_em        timestamptz not null default now(),
  constraint revisao_decisao_coerente check ((status = 'pendente') = (determinacao is null))
);
create index revisao_canal_status on pqbr.revisao_humana (canal_id, status);
create index revisao_episodio on pqbr.revisao_humana (episodio_id);

alter table pqbr.propostas      enable row level security; alter table pqbr.propostas      force row level security;
alter table pqbr.tickets        enable row level security; alter table pqbr.tickets        force row level security;
alter table pqbr.revisao_humana enable row level security; alter table pqbr.revisao_humana force row level security;

commit;
