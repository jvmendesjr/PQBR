-- PQBR 0008: carga dos temas já publicados (R10). Rodar com psql a partir da raiz do repositório:
--   psql "$PQBR_DB_URL" -v ON_ERROR_STOP=1 -f db/migrations/0008_pqbr_seed_temas.sql
-- (\copy lê db/seeds/temas-publicados.csv do cliente). Idempotente pelo video_id.
begin;
create temp table _temas_csv (n int, data_publicacao date, video_id text, titulo_publicado text, repete_n text) on commit drop;
\copy _temas_csv from 'db/seeds/temas-publicados.csv' with (format csv, header true)
insert into pqbr.temas (tema, tema_normalizado, origem, status, video_id, publicado_em, repete_n)
select titulo_publicado,
       trim(regexp_replace(lower(translate(titulo_publicado,
            'áàâãäéèêëíìîïóòôõöúùûüçÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ',
            'aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC')), '[^a-z0-9]+', ' ', 'g')),
       'legado', 'publicado', video_id, data_publicacao, nullif(repete_n, '')::smallint
from _temas_csv
on conflict (video_id) do nothing;
commit;
