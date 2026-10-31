#!/bin/sh
# Protótipo separado; somente servidor efêmero local, nenhuma conexão operacional.
set -eu
cd "$(dirname "$0")/../.."
ROOT=$(pwd)
SERVER=/tmp/temporal-test-server-sdk-python-1.34.0
[ -x "$SERVER" ] || { echo 'Binario local ausente; download proibido.' >&2; exit 1; }
OUT=${1:?Informe diretorio novo para evidencias}
mkdir -m 700 "$OUT"
OUT=$(realpath "$OUT")
TMP=$(mktemp -d /tmp/pqbr-f3-05-sws-ambiente-XXXXXX)
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
mkdir -m 700 "$TMP/home"
HOST_NETNS=$(readlink /proc/self/ns/net)
sha256sum "$SERVER"
printf 'Evidencias: %s\nNamespace original: %s\n' "$OUT" "$HOST_NETNS"
timeout --signal=TERM --kill-after=10s 180s \
  unshare --user --map-root-user --net --pid --fork --mount-proc --kill-child=KILL \
  env -i PATH=/usr/bin:/bin LANG=C.UTF-8 HOME="$TMP/home" TMPDIR="$TMP" \
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" \
    PQBR_TEMPORAL_ISOLADO=1 PQBR_HOST_NETNS="$HOST_NETNS" \
    PQBR_TEST_TARGET="${2:-tests.workflows.test_f3_05_signal_with_start_isolado}" \
    PQBR_TEMPORAL_EVIDENCIAS="$OUT" \
    sh -eu -c '
      ip link set lo up
      readlink /proc/self/ns/net > "$PQBR_TEMPORAL_EVIDENCIAS/netns.txt"
      readlink /proc/self/ns/pid > "$PQBR_TEMPORAL_EVIDENCIAS/pidns.txt"
      ip -brief address
      test -z "$(ip route show)"
      exec .venv/bin/python -m unittest -v "$PQBR_TEST_TARGET"
    '
printf 'Servidor e namespace encerrados; evidencias em %s\n' "$OUT"
