#!/bin/sh
# Testa as migrações num Postgres 17 descartável (sem rede, sem porta, 256 MB). Não toca no Supabase.
# Uso (na raiz do repo): sh db/test_migrations.sh
set -eu
R="$(cd "$(dirname "$0")/.." && pwd)"; N=pqbr-migtest-$$
docker run -d --rm --name $N --network none -m 256m -e POSTGRES_PASSWORD=teste-local -v "$R":/repo:ro -w /repo postgres:17-alpine >/dev/null
trap 'docker rm -f $N >/dev/null 2>&1' EXIT
for i in $(seq 1 30); do docker exec $N pg_isready -U postgres -q && break; sleep 1; done; sleep 2
Q() { docker exec -i $N psql -U postgres -v ON_ERROR_STOP=1 -qAt "$@"; }
Q -c "create role anon nologin; create role authenticated nologin; create role service_role nologin bypassrls;"
up() { for f in "$R"/db/migrations/000[1-8]_*.sql; do Q -f "/repo/${f#$R/}" >/dev/null; done; }
down() { for f in $(ls "$R"/db/migrations/rollback/*_down.sql | sort -r); do Q -f "/repo/${f#$R/}" >/dev/null; done; }
up; echo "UP ok: $(Q -c "select count(*) from pg_tables where schemaname='pqbr'") tabelas, $(Q -c "select count(*) from pqbr.temas") temas carregados"
echo "RLS ligado+forçado em todas: $(Q -c "select bool_and(relrowsecurity and relforcerowsecurity) from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='pqbr' and c.relkind='r'")"
echo "canal_id nas tabelas de negócio: $(Q -c "select count(distinct table_name) from information_schema.columns where table_schema='pqbr' and column_name='canal_id'")"
F() { if Q -c "$2" >/dev/null 2>&1; then echo "FALHOU (aceitou): $1"; exit 1; else echo "ok (recusou): $1"; fi; }
T=$(Q -c "select tema_normalizado from pqbr.temas limit 1")
F "R10 tema repetido" "insert into pqbr.temas (tema, tema_normalizado, origem) values ('x repetido', '$T', 'jose')"
F "código fora do padrão" "insert into pqbr.episodios (codigo, tema_id) values ('EP-1', 1)"
E=$(Q -c "insert into pqbr.episodios (codigo, tema_id, estado) values ('PQBR-EP0001', 1, 'aprovado') returning id")
F "publicação enviada sem external_id" "insert into pqbr.publicacoes (episodio_id, plataforma_id, estado) values ($E, 'youtube', 'enviado')"
Q -c "insert into pqbr.publicacoes (episodio_id, plataforma_id, estado, external_id) values ($E, 'youtube', 'enviado', 'AbCdEfGhIj0'), ($E, 'tiktok', 'aprovado', null)"
F "2ª publicação do mesmo episódio na mesma plataforma" "insert into pqbr.publicacoes (episodio_id, plataforma_id) values ($E, 'youtube')"
F "plataforma inexistente" "insert into pqbr.publicacoes (episodio_id, plataforma_id) values ($E, 'orkut')"
F "janela fora da grade" "insert into pqbr.grade (data, janela, tema_id, polemica, fonte) values ('2026-10-10','10:00',1,50,'perene')"
F "revisão decidida sem determinação" "insert into pqbr.revisao_humana (item_tipo, item_ref, status) values ('tema','x','decidido')"
F "ticket merge sem aprovação 1" "insert into pqbr.tickets (titulo, localizacao, falha, aprovacao_2_em) values ('t','l','f',now())"
F "autor sem hash" "insert into pqbr.comentarios (external_id, post_external_id, autor_hash, publicado_em) values ('c0','x8Rmv-Tkso4','joao@x.com',now())"
F "anon lê temas" "set role anon; select * from pqbr.temas"
F "authenticated lê temas" "set role authenticated; select * from pqbr.temas"
echo "service_role lê temas: $(Q -c "set role service_role; select count(*) from pqbr.temas")"
H=$(printf '%064d' 0)
Q -c "insert into pqbr.frases (texto, aprovada) values ('Boa pergunta.', true);
      insert into pqbr.comentarios (external_id, post_external_id, autor_hash, publicado_em, texto_bruto) values ('c1','x8Rmv-Tkso4','$H',now(),'texto'), ('c2','x8Rmv-Tkso4','$H',now(),null);
      insert into pqbr.respostas (comentario_id, frase_id, plataforma_id, post_external_id, autor_hash) select id,1,'youtube','x8Rmv-Tkso4','$H' from pqbr.comentarios where external_id='c1';"
F "2ª resposta à mesma pessoa no mesmo vídeo" "insert into pqbr.respostas (comentario_id, frase_id, plataforma_id, post_external_id, autor_hash) select id,1,'youtube','x8Rmv-Tkso4','$H' from pqbr.comentarios where external_id='c2'"
echo "mesma pessoa em outra plataforma pode: $(Q -c "insert into pqbr.comentarios (plataforma_id, external_id, post_external_id, autor_hash, publicado_em) values ('tiktok','t1','p1','$H',now()); insert into pqbr.respostas (comentario_id, frase_id, plataforma_id, post_external_id, autor_hash) select id,1,'tiktok','p1','$H' from pqbr.comentarios where external_id='t1'; select 'sim'")"
echo "só-leitura lê temas: $(Q -c "set role pqbr_leitura; select count(*) from pqbr.temas")"
F "só-leitura escreve" "set role pqbr_leitura; insert into pqbr.acoes (tipo, alvo, motivo, ator) values ('x','x','x','agente')"
F "só-leitura lê texto bruto" "set role pqbr_leitura; select texto_bruto from pqbr.comentarios"
echo "só-leitura lê comentários sem texto: $(Q -c "set role pqbr_leitura; select count(*) from pqbr.comentarios")"
Q -c "insert into pqbr.outbox_aplicados (chave_idempotencia, tabela, workflow_id) values ('wf:run:passo1','episodios','wf') on conflict do nothing;
      insert into pqbr.outbox_aplicados (chave_idempotencia, tabela, workflow_id) values ('wf:run:passo1','episodios','wf') on conflict do nothing;"
echo "outbox repetido gravou: $(Q -c "select count(*) from pqbr.outbox_aplicados") (esperado 1)"
Q -c "update pqbr.comentarios set texto_bruto='oi', texto_expira_em=now()-interval '1 day' where external_id='c1'"
echo "expirar textos: $(Q -c "select pqbr.expirar_textos_comentarios()") (esperado 1)"
echo "FKs sem índice: $(Q -c "select count(*) from pg_constraint c join pg_namespace n on n.oid=c.connamespace where n.nspname='pqbr' and c.contype='f' and not exists (select 1 from pg_index i where i.indrelid=c.conrelid and i.indkey[0]=c.conkey[1])")"
Q -c "truncate pqbr.respostas, pqbr.comentarios, pqbr.publicacoes, pqbr.episodio_estados, pqbr.episodios, pqbr.frases, pqbr.outbox_aplicados restart identity cascade"  # limpa dados de teste
down; echo "DOWN ok: esquema pqbr existe? $(Q -c "select count(*) from pg_namespace where nspname='pqbr'")"
up; down; echo "ciclo UP/DOWN repetido ok"
