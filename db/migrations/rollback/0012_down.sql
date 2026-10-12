begin;
drop view if exists pqbr.fila_folga;
drop function if exists pqbr.publicar_tema(bigint, text, text, text);
drop trigger if exists temas_pendentes_r10 on pqbr.temas_pendentes;
drop function if exists pqbr.barrar_tema_repetido();
drop function if exists pqbr.tema_parecido(text, real);
drop table if exists pqbr.temas_publicados;
drop table if exists pqbr.temas_pendentes;
commit;
