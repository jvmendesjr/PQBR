-- PQBR 0016 (José 12/10/2026 18:06): toda queda de acesso (sessão Google/Camofox, NotebookLM, Paperclip) fica registrada,
-- com causa e resultado da restauração automática; avisos ao José saem por pqbr.revisao_humana → Telegram.
begin;
create table pqbr.eventos_acesso (
  id          bigint generated always as identity primary key,
  canal_id    text not null default 'pqbr' references pqbr.canais (id),
  servico     text not null check (servico in ('google_camofox', 'notebooklm', 'paperclip_cli')),
  tipo        text not null check (tipo in ('queda', 'restauro_ok', 'restauro_falhou', 'normalizado')),
  causa       text not null,
  resultado   text,
  criado_em   timestamptz not null default now()
);
alter table pqbr.eventos_acesso enable row level security; alter table pqbr.eventos_acesso force row level security;
create policy eventos_acesso_app on pqbr.eventos_acesso for all to pqbr_app using (true) with check (true);
create policy eventos_acesso_leitura on pqbr.eventos_acesso for select to pqbr_leitura using (true);
grant select, insert on pqbr.eventos_acesso to pqbr_app;
grant select on pqbr.eventos_acesso to pqbr_leitura;
commit;
