#!/bin/sh
# Amostra RAM do Temporal + Postgres dedicado + worker (MiB) em runtime/tz/ram.log (fora do git).
export LC_ALL=C
D="$(cd "$(dirname "$0")/../.." && pwd)/runtime/tz"; mkdir -p "$D"
T=$(date -Iseconds)
docker stats --no-stream --format '{{.Name}} {{.MemUsage}}' | grep pqbr-temporal | awk -v t="$T" '
 function mib(v){ if(v~/GiB/){sub(/GiB/,"",v);return v*1024} if(v~/MiB/){sub(/MiB/,"",v);return v+0} if(v~/KiB/){sub(/KiB/,"",v);return v/1024} return v+0 }
 {s+=mib($2); printf "%s %s %.1f\n", t, $1, mib($2)} END{printf "%s TOTAL_COMPOSE %.1f\n", t, s}' >> "$D/ram.log"
W=$(systemctl --user show pqbr-temporal-worker -p MemoryCurrent --value 2>/dev/null)
echo "$T WORKER_MIB $(awk -v b="$W" 'BEGIN{printf "%.1f", b/1048576}')" >> "$D/ram.log"
