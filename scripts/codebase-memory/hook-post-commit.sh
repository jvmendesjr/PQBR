#!/usr/bin/env bash
# Reindexa o codebase-memory-mcp em segundo plano após cada commit (migração GitNexus -> CBM, 2026-10-29).
# Não bloqueia o commit; nada escrito no repo (o índice vive em ~/.cache/codebase-memory-mcp/).
# O auto_watch do CBM só vale na sessão dona; a indexação por CLI não registra watch, por isso o post-commit é o mecanismo durável de frescor.
BIN="${PQBR_CBM_BIN:-$HOME/.local/opt/codebase-memory-mcp/codebase-memory-mcp}"; [ -x "$BIN" ] || exit 0
R="$(git rev-parse --show-toplevel)"
( cd "$R" && nice -n 10 "$BIN" cli index_repository --repo-path "$R" --name PQBR > "$HOME/.cache/pqbr-cbm-reindex.log" 2>&1 & ) >/dev/null 2>&1
exit 0
