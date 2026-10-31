# paperclip-db — Postgres 17 local do Paperclip (L-01, t412)

- Container `paperclip-db-paperclip-db-1` (compose project `paperclip-db`), `postgres:17-alpine`, porta só em `127.0.0.1:55434`, 512 MB.
- Banco `paperclip`, role `paperclip` (dono). Separado do banco do app PQBR (`pqbr-db`, 55433) e do Temporal.
- Extensões: `pg_trgm`, `fuzzystrmatch` (public); `pgcrypto`, `uuid-ossp` (extensions), como no Supabase.
- Segredos fora do git: `~/.config/paperclip-db/db.env` (superusuário e senha da role) e `~/.config/paperclip-db/paperclip.env` (`DATABASE_URL` do Paperclip), ambos 600.
- Paperclip lê o banco pela drop-in `~/.config/systemd/user/paperclipai.service.d/20-local-database.conf`.
- Backup: `paperclip-db-backup.timer` 04:00 → `~/Backups/paperclip-db/` (7 cópias, 600). O backup horário interno do Paperclip continua ativo.
- Scripts: `setup.sh` (provisiona), `restore.sh <dump>` (restaura public+drizzle), `switch.sh` (corte feito em 11/10 21:45), `backup.sh`.

## Rollback (até 18/10/2026; Supabase `paperclip` intocado)
1. `systemctl --user stop paperclipai`
2. `mv ~/.config/systemd/user/paperclipai.service.d/20-local-database.conf ~/.paperclip-migration/`
3. `cp ~/.paperclip-migration/20-supabase-database.conf.rollback ~/.config/systemd/user/paperclipai.service.d/20-supabase-database.conf`
4. `systemctl --user daemon-reload && systemctl --user start paperclipai`
Atenção: o que foi gravado no banco local depois de 11/10 21:46 não existe no Supabase. Para levar junto, fazer `pg_dump -n public -n drizzle` do local e restaurar no Supabase antes do passo 4.
Dumps do corte: `~/.paperclip-migration/paperclip-final-20261011-2145.dump` (600; o do Supabase no momento do corte).
