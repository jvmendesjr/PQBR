-- PQBR 0010: consumo por modelo e por tipo de ação (t357 h). Sem teto de tokens: só monitoramento (REGRAS §22).
-- Uma linha por chamada (ou lote) a modelo/ferramenta; agregados pela view consumo_diario para o relatório diário.
-- Sem prompt, resposta, segredo ou dado pessoal: só contagens, tempos e classes (REGRAS §17).
begin;
create table pqbr.consumo_modelos (
  id                bigint generated always as identity primary key,
  canal_id          text not null default 'pqbr' references pqbr.canais (id),
  em                timestamptz not null default now(),
  provedor          text not null,          -- 9router, openrouter, openai, google, notebooklm, jev...
  modelo            text not null,          -- nome exato devolvido pelo provedor (ex.: gemini-3.8-flash)
  tipo_acao         text not null check (tipo_acao in (
                      'ideacao', 'roteiro', 'seo', 'pesquisa', 'ficha_visual',
                      'auditor_visual', 'auditor_texto', 'auditor_desempate',
                      'jev_triagem', 'jev_classificacao', 'jev_decisao', 'jev_verificacao',
                      'correcao_autonoma', 'comunidade', 'compliance', 'analista',
                      'assistente', 'publicacao', 'teste_resposta', 'outro')),
  ferramenta        text,                   -- camofox, notebooklm, gemini_web, api... (null = chamada direta ao modelo)
  episodio_id       bigint references pqbr.episodios (id),
  workflow_id       text,                   -- Temporal
  run_id            text,
  activity          text,
  tentativa         smallint not null default 1 check (tentativa >= 1),
  chamadas          integer not null default 1 check (chamadas >= 1),
  tokens_entrada    bigint check (tokens_entrada >= 0),
  tokens_saida      bigint check (tokens_saida >= 0),
  tokens_cache      bigint check (tokens_cache >= 0),
  tokens_raciocinio bigint check (tokens_raciocinio >= 0),
  unidades          numeric(18,4),          -- uso que não é token (ex.: % da janela do NotebookLM, minutos de áudio)
  unidade           text,
  duracao_ms        integer check (duracao_ms >= 0),
  sucesso           boolean not null,
  erro_classe       text,                   -- classe do erro, nunca a mensagem bruta
  custo_estimado_micro_usd bigint check (custo_estimado_micro_usd >= 0),  -- estimativa; null quando sem preço
  extra             jsonb not null default '{}'::jsonb
);
create index consumo_modelos_em on pqbr.consumo_modelos (canal_id, em);
create index consumo_modelos_modelo on pqbr.consumo_modelos (provedor, modelo, em);
create index consumo_modelos_acao on pqbr.consumo_modelos (tipo_acao, em);
create index consumo_modelos_episodio on pqbr.consumo_modelos (episodio_id);
alter table pqbr.consumo_modelos enable row level security;
alter table pqbr.consumo_modelos force row level security;

-- Agregado diário (fuso de Fortaleza) para o relatório
create view pqbr.consumo_diario with (security_invoker = true) as
select canal_id, (em at time zone 'America/Fortaleza')::date as dia, provedor, modelo, tipo_acao,
       sum(chamadas) as chamadas, count(*) filter (where not sucesso) as falhas,
       sum(tokens_entrada) as tokens_entrada, sum(tokens_saida) as tokens_saida,
       sum(tokens_cache) as tokens_cache, sum(tokens_raciocinio) as tokens_raciocinio,
       sum(duracao_ms) as duracao_ms, sum(custo_estimado_micro_usd) as custo_estimado_micro_usd
from pqbr.consumo_modelos group by 1, 2, 3, 4, 5;

-- Papéis: escritor só insere e lê (histórico imutável); só-leitura lê
do $$ begin
  if exists (select 1 from pg_roles where rolname = 'pqbr_app') then
    grant select, insert on pqbr.consumo_modelos to pqbr_app;
    grant select on pqbr.consumo_diario to pqbr_app;
    grant usage, select on sequence pqbr.consumo_modelos_id_seq to pqbr_app;
    create policy consumo_modelos_app on pqbr.consumo_modelos for all to pqbr_app using (true) with check (true);
  end if;
  if exists (select 1 from pg_roles where rolname = 'pqbr_leitura') then
    grant select on pqbr.consumo_modelos, pqbr.consumo_diario to pqbr_leitura;
    create policy consumo_modelos_leitura on pqbr.consumo_modelos for select to pqbr_leitura using (true);
  end if;
  if exists (select 1 from pg_roles where rolname = 'service_role') then
    grant select, insert on pqbr.consumo_modelos to service_role;
    grant select on pqbr.consumo_diario to service_role;
  end if;
end $$;
commit;
