# db/migrations

Esquema `pqbr` do banco do app (ARQUITETURA §8; F3-01/D3). Banco: **Postgres 17 local** no `pc` (`infra/pqbr-db`, t343). O Supabase fica como opção futura: as migrações rodam nele sem mudança, porque os blocos do `service_role`, `anon` e `authenticated` só agem se esses papéis existirem.

- **Ordem:** `0001` … `0009`. Aplicar com `sh infra/pqbr-db/aplicar.sh`, que é idempotente e registra cada arquivo em `public.pqbr_migracoes`.
- **Rollback:** `rollback/000N_down.sql`, em ordem inversa. O `0001_down` remove o esquema e os papéis.
- **Segurança:**
  - RLS ligado e forçado em todas as tabelas.
  - Políticas só para `pqbr_app` (escritor do Temporal) e `pqbr_leitura` (só-leitura, sem texto bruto de comentário).
  - Agentes do Paperclip nunca escrevem aqui.
- **Sem segredos nem PII:** autor de comentário só como HMAC; o texto bruto expira em 30 dias (`pqbr.expirar_textos_comentarios()`).
- **Diretriz (t346):** canal / plataforma / publicações genéricos, com jsonb de extensão. Rede nova = linhas novas, não tabelas novas. No catálogo, só o YouTube.
- **Testes:**
  - Postgres 17 descartável, sem rede: `sh db/test_migrations.sh`.
  - Banco real, sem alterar nada: `sh infra/pqbr-db/verificar.sh`.

- `0010_pqbr_consumo_modelos.sql` (t357 h): consumo por modelo e por tipo de ação (tokens, chamadas, tempo, sucesso, custo estimado), view `consumo_diario` para o relatório; sem teto, só monitoramento; sem prompt nem resposta gravados.
- `0013_pqbr_erros_aceitaveis.sql` (t435): erros sem risco de segurança aceitos pelo Auditor (legenda, texto, visual…), com decisão posterior (`pendente/aceito/corrigir_prompt/virar_seguranca`); view `erros_aceitaveis_resumo`.
