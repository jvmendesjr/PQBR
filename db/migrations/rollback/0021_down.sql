-- Reverte 0021. Atencao: reverter o schema exige primeiro desfazer a marcacao de apagado do
-- EP1003 feita sob 0021, senao a constraint antiga falha. O arquivo do caderno (15 itens,
-- 3 copias) permanece intacto; so a marcacao e desfeita.
begin;
update pqbr.cadernos_episodio set apagado_em = null, descarte_dono_em = null, motivo_descarte = null where caderno_id = 'b0a178b8-a108-4912-9514-dd629e0ab688';
alter table pqbr.cadernos_episodio drop constraint cadernos_episodio_apagar_verificado;
alter table pqbr.cadernos_episodio drop column motivo_descarte;
alter table pqbr.cadernos_episodio drop column descarte_dono_em;
alter table pqbr.cadernos_episodio add constraint cadernos_episodio_apagar_verificado check (
  apagado_em is null or (arquivado_em is not null and verificado_em is not null and
    (classe <> 'episodio' or (publicado_em is not null and apagado_em >= publicado_em + interval '48 hours'))));
commit;
