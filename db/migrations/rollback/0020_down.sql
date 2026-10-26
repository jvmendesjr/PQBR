-- Rollback da 0020: só derruba tabelas novas (sem dados de produção antes do primeiro envio real).
begin;
drop table if exists pqbr.auditoria_publicacao;
drop table if exists pqbr.controle_publicacao;
drop table if exists pqbr.agenda_publicacao;
commit;
