#!/bin/sh
# F3-05: servidor de testes somente em namespaces efêmeros, sem rede externa.
set -eu
cd "$(dirname "$0")/../.."
ROOT=$(pwd)
SERVER=/tmp/temporal-test-server-sdk-python-1.34.0
[ -x "$SERVER" ] || { echo 'Binario local ausente; download proibido.' >&2; exit 1; }
OUT=${1:-$(mktemp -d /tmp/pqbr-f3-05-roteamento-evidencia-XXXXXX)}
if [ "$#" -gt 0 ]; then
    # Nunca substituir evidência existente.
    mkdir -m 700 "$OUT"
fi
OUT=$(realpath "$OUT")
TMP=$(mktemp -d /tmp/pqbr-f3-05-temporal-ambiente-XXXXXX)
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
mkdir -m 700 "$TMP/home"
HOST_NETNS=$(readlink /proc/self/ns/net)
printf 'Evidencias: %s\n' "$OUT"
printf 'Namespace original: %s\n' "$HOST_NETNS"
sha256sum "$SERVER"
# env -i remove credenciais e proxies herdados. PID namespace elimina descendentes
# quando o processo principal termina; timeout limita inclusive falhas de limpeza.
timeout --signal=TERM --kill-after=10s 300s \
  unshare --user --map-root-user --net --pid --fork --mount-proc --kill-child=KILL \
  env -i PATH=/usr/bin:/bin LANG=C.UTF-8 HOME="$TMP/home" TMPDIR="$TMP" \
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT/src" \
    PQBR_TEMPORAL_ISOLADO=1 PQBR_HOST_NETNS="$HOST_NETNS" \
    PQBR_TEMPORAL_EVIDENCIAS="$OUT" \
    sh -eu -c '
      ip link set lo up
      printf "Namespace isolado: "; readlink /proc/self/ns/net
      ip -brief address
      test -z "$(ip route show)"
      exec .venv/bin/python -m unittest -v tests.workflows.test_f3_05_roteamento_temporal_isolado
    '
printf 'Servidor e namespace encerrados; evidencias preservadas em %s\n' "$OUT"
