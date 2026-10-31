#!/bin/sh
# Protótipo apenas: não conecta a Temporal existente nem importa backends PQBR.
set -eu
cd "$(dirname "$0")/../.."
ROOT=$(pwd)
SERVER=/tmp/temporal-test-server-sdk-python-1.34.0
[ -x "$SERVER" ] || { echo 'Binario local ausente; download proibido.' >&2; exit 1; }
OUT=${1:?Informe um diretorio novo para evidencias}
mkdir -m 700 "$OUT"
OUT=$(realpath "$OUT")
TMP=$(mktemp -d /tmp/pqbr-f3-05-ator-ambiente-XXXXXX)
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
mkdir -m 700 "$TMP/home"
HOST_NETNS=$(readlink /proc/self/ns/net)
printf 'Evidencias: %s\nNamespace original: %s\n' "$OUT" "$HOST_NETNS"
sha256sum "$SERVER"
timeout --signal=TERM --kill-after=10s 180s \
  unshare --user --map-root-user --net --pid --fork --mount-proc --kill-child=KILL \
  env -i PATH=/usr/bin:/bin LANG=C.UTF-8 HOME="$TMP/home" TMPDIR="$TMP" \
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" \
    PQBR_TEMPORAL_ISOLADO=1 PQBR_HOST_NETNS="$HOST_NETNS" \
    PQBR_TEMPORAL_EVIDENCIAS="$OUT" \
    sh -eu -c '
      ip link set lo up
      readlink /proc/self/ns/net > "$PQBR_TEMPORAL_EVIDENCIAS/netns.txt"
      printf "Namespace isolado: "; cat "$PQBR_TEMPORAL_EVIDENCIAS/netns.txt"
      ip -brief address
      test -z "$(ip route show)"
      exec .venv/bin/python -m unittest -v tests.workflows.test_f3_05_ator_sessao_isolado
    '
printf 'Servidor e namespace encerrados; evidencias preservadas em %s\n' "$OUT"
