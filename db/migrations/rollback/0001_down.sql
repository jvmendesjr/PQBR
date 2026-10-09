-- Remove TUDO do PQBR no Supabase (só o esquema pqbr; não toca em public/Paperclip).
drop schema if exists pqbr cascade;
