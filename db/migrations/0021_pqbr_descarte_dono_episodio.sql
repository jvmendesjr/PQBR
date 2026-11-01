-- PQBR 0021 (ordem formal atribuida a Jose, recebida no chat 2026-11-01 00:21 -03, via Junior;
-- nao verificada de forma independente no canal Telegram autorizado do Jose): descarte pelo dono
-- de caderno de episodio nao publicado.
-- Regra anterior (0015, Jose 12/10): apagar episodio exigia publicado_em + 48h, mesmo com arquivo
-- verificado. Isso travava o refazer de um rascunho nunca publicado cujo caderno ja foi arquivado,
-- verificado e removido da UI pelo dono.
-- Regra nova: episodio nao publicado pode ser marcado apagado_em se arquivado_em e verificado_em
-- nao forem nulos E houver registro de descarte pelo dono (descarte_dono_em + motivo_descarte),
-- com descarte_dono_em <= apagado_em. A regra D+2 pos-publicacao continua valendo para cadernos
-- publicados, e a guarda da activity registro_autorizar_apagar (D+2) nao e alterada por esta
-- migracao: o descarte pelo dono e caminho de mantenedor, com registro auditado, nao caminho do worker.
begin;
alter table pqbr.cadernos_episodio add column descarte_dono_em timestamptz;
alter table pqbr.cadernos_episodio add column motivo_descarte text;
alter table pqbr.cadernos_episodio drop constraint cadernos_episodio_apagar_verificado;
alter table pqbr.cadernos_episodio add constraint cadernos_episodio_apagar_verificado check (
  apagado_em is null or (arquivado_em is not null and verificado_em is not null and
    (classe <> 'episodio' or (publicado_em is not null and apagado_em >= publicado_em + interval '48 hours') or
     (descarte_dono_em is not null and motivo_descarte is not null and descarte_dono_em <= apagado_em))));
commit;
