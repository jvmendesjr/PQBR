# db/migrations

Esquema do Supabase do PQBR (ARQUITETURA §8; F3-01/D3). **Nada aplicado ainda: aplicar exige o OK do José (G3).**

- Projeto: o mesmo Supabase do Paperclip (decisão 3 do DECISOES-LOG). Tudo fica no esquema dedicado **`pqbr`**; nada em `public`, que é do Paperclip.
- Ordem: `0001` … `0008`. Rollback: `rollback/000N_down.sql` em ordem inversa (`0001_down` remove o esquema inteiro).
- Segurança:
  - RLS ligado e forçado em todas as tabelas, sem políticas: anon e authenticated não leem nada.
  - Acesso só pelo servidor (`service_role`).
  - O esquema `pqbr` **não** deve ser adicionado aos "Exposed schemas" da Data API.
- Sem segredos nem PII: autor de comentário só como HMAC; texto bruto expira em 30 dias (`pqbr.expirar_textos_comentarios()`).
- `canal_id` em todas as tabelas de negócio (padrão `pqbr`) para o multi-canal futuro.
- Testar localmente (Postgres 17 descartável, sem rede):

  ```
  sh db/test_migrations.sh
  ```
