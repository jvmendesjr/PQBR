-- PQBR 0011: retenção do consumo por modelo (t358, t369). Bruto 90 dias; resumo diário 25 meses.
-- Resumo permanente + papel dedicado pqbr_manutencao (o pqbr_app continua sem DELETE).
begin;
create table pqbr.consumo_resumo_diario (
  canal_id   text not null default 'pqbr' references pqbr.canais (id),
  dia        date not null,                -- dia em America/Fortaleza
  provedor   text not null,
  modelo     text not null,
  tipo_acao  text not null,
  linhas     bigint not null check (linhas >= 0),
  chamadas   bigint not null check (chamadas >= 0),
  falhas     bigint not null check (falhas >= 0),
  tokens_entrada bigint, tokens_saida bigint, tokens_cache bigint, tokens_raciocinio bigint,
  duracao_ms bigint, custo_estimado_micro_usd bigint,
  resumido_em timestamptz not null default now(),
  primary key (canal_id, dia, provedor, modelo, tipo_acao)
);
create index consumo_resumo_dia on pqbr.consumo_resumo_diario (dia);
alter table pqbr.consumo_resumo_diario enable row level security;
alter table pqbr.consumo_resumo_diario force row level security;

-- Agrega → confere → apaga, numa transação (tudo ou nada). Idempotente: o resumo de um dia é
-- recalculado inteiro a partir do bruto ainda existente; depois de apagado, o dia não volta.
create or replace function pqbr.reter_consumo(p_hoje date, p_bruto_dias int default 90,
                                              p_resumo_meses int default 25, p_lote int default 5000)
returns jsonb language plpgsql set search_path = '' as $$
declare
  v_corte date := p_hoje - p_bruto_dias;
  v_corte_resumo date := (p_hoje - make_interval(months => p_resumo_meses))::date;
  v_dias int; v_apagadas bigint := 0; v_n bigint; v_resumo_apagado bigint; v_dif bigint;
begin
  if p_bruto_dias < 1 or p_resumo_meses < 1 then raise exception 'prazos inválidos'; end if;
  insert into pqbr.consumo_resumo_diario as r (canal_id, dia, provedor, modelo, tipo_acao, linhas, chamadas, falhas,
         tokens_entrada, tokens_saida, tokens_cache, tokens_raciocinio, duracao_ms, custo_estimado_micro_usd)
  select canal_id, (em at time zone 'America/Fortaleza')::date, provedor, modelo, tipo_acao, count(*), sum(chamadas),
         count(*) filter (where not sucesso), sum(tokens_entrada), sum(tokens_saida), sum(tokens_cache),
         sum(tokens_raciocinio), sum(duracao_ms), sum(custo_estimado_micro_usd)
    from pqbr.consumo_modelos where (em at time zone 'America/Fortaleza')::date < v_corte
   group by 1, 2, 3, 4, 5
  on conflict (canal_id, dia, provedor, modelo, tipo_acao) do update set
    linhas = excluded.linhas, chamadas = excluded.chamadas, falhas = excluded.falhas,
    (tokens_entrada, tokens_saida, tokens_cache, tokens_raciocinio)
      = (excluded.tokens_entrada, excluded.tokens_saida, excluded.tokens_cache, excluded.tokens_raciocinio),
    duracao_ms = excluded.duracao_ms, custo_estimado_micro_usd = excluded.custo_estimado_micro_usd, resumido_em = now();
  get diagnostics v_dias = row_count;
  -- conferência: linhas e chamadas do bruto que vai sair = resumo daqueles dias
  with b as (select canal_id, (em at time zone 'America/Fortaleza')::date as dia, provedor, modelo, tipo_acao,
                    count(*) + sum(chamadas) as n
               from pqbr.consumo_modelos where (em at time zone 'America/Fortaleza')::date < v_corte
              group by 1, 2, 3, 4, 5)
  select coalesce(sum(b.n - coalesce(r.linhas + r.chamadas, 0)), 0) into v_dif
    from b left join pqbr.consumo_resumo_diario r using (canal_id, dia, provedor, modelo, tipo_acao);
  if v_dif <> 0 then raise exception 'conferência do resumo falhou (diferença %), nada apagado', v_dif; end if;
  loop
    delete from pqbr.consumo_modelos where id in (
      select id from pqbr.consumo_modelos where (em at time zone 'America/Fortaleza')::date < v_corte limit p_lote);
    get diagnostics v_n = row_count; v_apagadas := v_apagadas + v_n; exit when v_n = 0;
  end loop;
  delete from pqbr.consumo_resumo_diario where dia < v_corte_resumo;
  get diagnostics v_resumo_apagado = row_count;
  insert into pqbr.acoes (tipo, alvo, motivo, ator)
  values ('retencao_consumo', 'consumo_modelos',
          format('hoje=%s corte_bruto=%s grupos_resumidos=%s brutas_apagadas=%s resumo_apagado=%s',
                 p_hoje, v_corte, v_dias, v_apagadas, v_resumo_apagado), 'RetencaoConsumoWorkflow');
  return jsonb_build_object('corte_bruto', v_corte, 'corte_resumo', v_corte_resumo, 'grupos_resumidos', v_dias,
                            'brutas_apagadas', v_apagadas, 'resumo_apagado', v_resumo_apagado);
end $$;
revoke all on function pqbr.reter_consumo(date, int, int, int) from public;

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'pqbr_manutencao') then
    create role pqbr_manutencao nologin;   -- login/senha só pelo infra/pqbr-db/aplicar.sh (.env 600)
  end if;
end $$;
grant usage on schema pqbr to pqbr_manutencao;
grant select, delete on pqbr.consumo_modelos to pqbr_manutencao;
grant select, insert, update, delete on pqbr.consumo_resumo_diario to pqbr_manutencao;
grant insert on pqbr.acoes to pqbr_manutencao;
grant usage on sequence pqbr.acoes_id_seq to pqbr_manutencao;
grant execute on function pqbr.reter_consumo(date, int, int, int) to pqbr_manutencao;
create policy consumo_modelos_manut on pqbr.consumo_modelos for all to pqbr_manutencao using (true) with check (true);
create policy consumo_resumo_manut on pqbr.consumo_resumo_diario for all to pqbr_manutencao using (true) with check (true);
create policy acoes_manut on pqbr.acoes for insert to pqbr_manutencao with check (tipo = 'retencao_consumo');
do $$ begin
  if exists (select 1 from pg_roles where rolname = 'pqbr_app') then
    grant select on pqbr.consumo_resumo_diario to pqbr_app;
    create policy consumo_resumo_app on pqbr.consumo_resumo_diario for select to pqbr_app using (true);
  end if;
  if exists (select 1 from pg_roles where rolname = 'pqbr_leitura') then
    grant select on pqbr.consumo_resumo_diario to pqbr_leitura;
    create policy consumo_resumo_leitura on pqbr.consumo_resumo_diario for select to pqbr_leitura using (true);
  end if;
end $$;
commit;
