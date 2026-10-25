begin;
alter table pqbr.revisao_humana drop column if exists chave_saida;
drop table if exists pqbr.entrada_telegram;
drop table if exists pqbr.pedido_aprovacao;
drop table if exists pqbr.saida_telegram;
commit;
