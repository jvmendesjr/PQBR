-- PQBR 0018 (rascunho t536, F05-06/F05-08): outbox de saída Telegram + dedupe de entrada. NÃO APLICADA.
begin;
create table pqbr.saida_telegram (
  chave         text primary key check (chave ~ '^[a-z0-9_:.\-]{8,200}$'),
  classe        text not null check (classe in ('pedido_aprovacao','pedido_acesso','aviso_operacional','lembrete')),
  texto         text not null,
  ref_pedido  text,
  estado        text not null default 'pendente' check (estado in ('pendente','enviando','enviado','incerto','falhou','ticket')),
  tentativas    int  not null default 0,
  claim_token   text,
  claim_ate     timestamptz,
  mensagem_id   bigint,
  motivo        text not null default '',
  criado_em     timestamptz not null default now(),
  enviado_em    timestamptz
);
create index saida_telegram_fila on pqbr.saida_telegram (estado, criado_em) where estado in ('pendente','falhou','enviando');
create table pqbr.pedido_aprovacao (
  token        text primary key,
  workflow_id  text not null,
  etapa        text not null,
  tarefa       text not null,
  expira_em    timestamptz not null,
  criado_em    timestamptz not null default now()
);
create table pqbr.entrada_telegram (
  update_id    bigint primary key,                                    -- dedupe do update
  ref_pedido text not null unique references pqbr.pedido_aprovacao (token),  -- uma decisão por pedido
  decisao      text not null check (decisao in ('aprovar','negar')),
  status       text not null default 'recebido',
  tentativas   int  not null default 0,
  motivo       text not null default '',
  criado_em    timestamptz not null default now()
);
-- revisao_humana: a ligação com a outbox substitui o "marca avisado_em antes de imprimir"
alter table pqbr.revisao_humana add column if not exists chave_saida text references pqbr.saida_telegram (chave);
do $$ declare t text; begin
  foreach t in array array['saida_telegram','pedido_aprovacao','entrada_telegram'] loop
    execute format('alter table pqbr.%I enable row level security; alter table pqbr.%I force row level security', t, t);
    execute format('create policy %I on pqbr.%I for all to pqbr_app using (true) with check (true)', t||'_app', t);
    execute format('create policy %I on pqbr.%I for select to pqbr_leitura using (true)', t||'_leitura', t);
    execute format('grant select, insert, update on pqbr.%I to pqbr_app; grant select on pqbr.%I to pqbr_leitura', t, t);
  end loop; end $$;
commit;
-- Claim atômico (adaptador Postgres, mesma semântica do RepositorioMemoria):
--   update pqbr.saida_telegram set estado='enviando', tentativas=tentativas+1, claim_token=$2,
--          claim_ate=now()+interval '2 min'
--    where chave=$1 and estado in ('pendente','falhou') returning tentativas;
-- Claim vencido em 'enviando' vira 'incerto' (Observador); nunca reenvio automático.
-- Confirmação: update ... set estado='enviado', mensagem_id=$3, enviado_em=now(), claim_token=null
--    where chave=$1 and claim_token=$2;  e, na mesma transação,
--    update pqbr.revisao_humana set avisado_em=now() where chave_saida=$1;
