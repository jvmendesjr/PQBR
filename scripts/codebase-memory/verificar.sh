#!/usr/bin/env bash
# Pré-requisito codebase-memory-mcp (migração para codebase-memory-mcp, 2026-10-29), mesmo padrão de scripts/_obsoleto/gitnexus/verificar.sh. Fail-closed: sai != 0 se faltar algo.
# A instalação é do usuário no servidor (fora do repo): ~/.local/opt/codebase-memory-mcp/codebase-memory-mcp (0.12.1, MIT).
# A PQBR só exige: binário, versão >= MIN, projeto PQBR registrado com índice ready e Lens desligada (ui_enabled=false). Nunca sobe MCP em --http, nunca abre a porta 9749.
set -euo pipefail
MIN="0.12.1"
BIN="${PQBR_CBM_BIN:-$HOME/.local/opt/codebase-memory-mcp/codebase-memory-mcp}"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
falha(){ echo "CBM FALHA: $*" >&2; exit 1; }
[ -x "$BIN" ] || falha "binário ausente em $BIN (instale: codebase-memory-mcp 0.12.1, release GitHub DeusData, --skip-config)"
V="$("$BIN" --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)" || falha "binário não executa"
[ -n "$V" ] || falha "versão não lida em $BIN --version"
[ "$(printf '%s\n%s\n' "$MIN" "$V" | sort -V | head -1)" = "$MIN" ] || falha "versão $V < $MIN"
"$BIN" cli list_projects 2>/dev/null | grep -q "$REPO" || falha "projeto PQBR não registrado no CBM (indexe: $BIN cli index_repository --repo-path $REPO --name PQBR)"
"$BIN" cli index_status --project PQBR --format json 2>/dev/null | grep -q '"status":"ready"' || falha "índice PQBR não está ready no CBM"
"$BIN" config list 2>/dev/null | grep -q 'ui_enabled.*false' || falha "Lens deve estar desligada (ui_enabled=false)"
echo "CBM OK: $V em $BIN; projeto PQBR ready; Lens desligada"
