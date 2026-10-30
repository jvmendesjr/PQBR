#!/usr/bin/env bash
# Reindexa o GitNexus em segundo plano após cada commit (t84u). Não bloqueia o commit; nada escrito no repo além de .gitnexus/.
BIN="$HOME/.local/bin/gitnexus"; [ -x "$BIN" ] || exit 0
R="$(git rev-parse --show-toplevel)"
( cd "$R" && nice -n 10 "$BIN" analyze --index-only . > "$HOME/.cache/pqbr-gitnexus-reindex.log" 2>&1 & ) >/dev/null 2>&1
exit 0
