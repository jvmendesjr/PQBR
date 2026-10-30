#!/usr/bin/env bash
# Pré-requisito GitNexus (t84u–t86u), mesmo padrão de scripts/camofox/verificar.sh. Fail-closed: sai != 0 se faltar algo.
# A instalação é GLOBAL do servidor (fora do repo, compartilhada): ~/.local/opt/node22 + wrapper ~/.local/bin/gitnexus.
# A PQBR só exige: binário, versão >= MIN e o índice deste repo registrado. Nunca sobe MCP em --http.
set -euo pipefail
MIN="1.6.12"
BIN="${PQBR_GITNEXUS_BIN:-$HOME/.local/bin/gitnexus}"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
falha(){ echo "GITNEXUS FALHA: $*" >&2; exit 1; }
[ -x "$BIN" ] || falha "binário ausente em $BIN (instale global: npm i -g gitnexus@$MIN com Node >= 22.18, prefixo ~/.local/opt/node22)"
V="$("$BIN" --version 2>/dev/null | tr -d '[:space:]')" || falha "binário não executa"
[ "$(printf '%s\n%s\n' "$MIN" "$V" | sort -V | head -1)" = "$MIN" ] || falha "versão $V < $MIN"
[ -d "$REPO/.gitnexus" ] || falha "índice da PQBR ausente: cd $REPO && $BIN analyze --index-only ."
"$BIN" list 2>/dev/null | grep -q "$REPO" || falha "índice da PQBR não registrado no registry global"
echo "GITNEXUS OK: $V em $BIN; índice $REPO/.gitnexus"
