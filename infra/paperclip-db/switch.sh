#!/bin/sh
set -e
umask 077
M=$HOME/.paperclip-migration; R=$HOME/Workspace/PQBR/infra/paperclip-db; U=$HOME/.config/systemd/user/paperclipai.service.d
. $HOME/.config/paperclip-db/db.env
printf "DATABASE_URL=postgres://paperclip:%s@127.0.0.1:55434/paperclip\n" "$PAPERCLIP_DB_APP_PASSWORD" > $HOME/.config/paperclip-db/paperclip.env
date; systemctl --user stop paperclipai
TS=$(date +%Y%m%d-%H%M)
( set -a; . $HOME/.config/core-engineering/supabase.env; set +a
  docker run --rm --network host -u $(id -u):$(id -g) -v $M:/w -e U="$DATABASE_URL" postgres:17-alpine sh -c "pg_dump \"\$U\" -Fc -n public -n drizzle -f /w/paperclip-final-$TS.dump" )
chmod 600 $M/paperclip-final-$TS.dump
$R/restore.sh $M/paperclip-final-$TS.dump
mv $U/20-supabase-database.conf $M/20-supabase-database.conf.rollback
printf "[Service]\nEnvironmentFile=%%h/.config/paperclip-db/paperclip.env\n" > $U/20-local-database.conf
systemctl --user daemon-reload; systemctl --user start paperclipai; date
echo FINAL=$M/paperclip-final-$TS.dump
