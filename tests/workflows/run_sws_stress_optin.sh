#!/bin/sh
# Experimento F3-05 opt-in. Nenhum download, segredo ou conexão operacional.
set -eu
cd "$(dirname "$0")/../.."
ROOT=$(pwd)
SERVER=/tmp/temporal-test-server-sdk-python-1.34.0
[ -x "$SERVER" ] || { echo 'Binario local ausente; download proibido.' >&2; exit 2; }
OUT=${1:?Informe diretorio novo para evidencias}
shift
mkdir -m 700 "$OUT"
OUT=$(realpath "$OUT")
TMP=$(mktemp -d /tmp/pqbr-f3-05-sws-stress-XXXXXX)
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
mkdir -m 700 "$TMP/home"
HOST_NETNS=$(readlink /proc/self/ns/net)
sha256sum "$SERVER"
printf 'Evidencias: %s\nNamespace original: %s\n' "$OUT" "$HOST_NETNS"
set +e
timeout --signal=TERM --kill-after=10s 900s \
  unshare --user --map-root-user --net --pid --fork --mount-proc --kill-child=KILL \
  env -i PATH=/usr/bin:/bin LANG=C.UTF-8 HOME="$TMP/home" TMPDIR="$TMP" \
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$ROOT" \
    PQBR_TEMPORAL_ISOLADO=1 PQBR_HOST_NETNS="$HOST_NETNS" \
    PQBR_TEMPORAL_EVIDENCIAS="$OUT" \
    sh -c '
      set -eu
      ip link set lo up
      readlink /proc/self/ns/net > "$PQBR_TEMPORAL_EVIDENCIAS/netns.txt"
      readlink /proc/self/ns/pid > "$PQBR_TEMPORAL_EVIDENCIAS/pidns.txt"
      ip -brief address
      test -z "$(ip route show)"
      set +e
      .venv/bin/python tests/workflows/stress_signal_with_start_optin.py "$@"
      rc=$?
      set -e
      .venv/bin/python -c '\''import json,pathlib,os
out=pathlib.Path(os.environ["PQBR_TEMPORAL_EVIDENCIAS"])
left=[]
for p in pathlib.Path("/proc").glob("[0-9]*"):
 try:
  if str((p/"exe").resolve())=="/tmp/temporal-test-server-sdk-python-1.34.0":
   left.append(dict(pid=int(p.name),cmdline=(p/"cmdline").read_bytes().replace(b"\0",b" ").decode()))
 except OSError: pass
(out/"processes-after-shutdown.json").write_text(json.dumps(dict(remaining_test_servers=left),indent=2)+"\n")
assert not left,left'\'' || rc=2
      exit "$rc"
    ' sh "$@"
rc=$?
set -e
printf '%s\n' "$rc" > "$OUT/runner-exit-code.txt"
printf 'Namespace encerrado; codigo experimental: %s; evidencias: %s\n' "$rc" "$OUT"
exit "$rc"
