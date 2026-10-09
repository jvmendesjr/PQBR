#!/bin/sh
# Resumo do soak de 24 h. Uso: sh scripts/tz/soak_check.sh
export LC_ALL=C
R="$(cd "$(dirname "$0")/../.." && pwd)"; L="$R/runtime/tz/ram.log"
echo "Amostras: $(grep -c TOTAL_COMPOSE "$L")  Pico compose (MiB): $(grep TOTAL_COMPOSE "$L" | awk '$3>m{m=$3}END{print m}')  Pico worker (MiB): $(grep WORKER_MIB "$L" | awk '$3>m{m=$3}END{print m}')"
echo "Acima de 1536 MiB: $(grep TOTAL_COMPOSE "$L" | awk '$3>1536' | wc -l)"
T='docker run --rm --network pqbr-temporal temporalio/admin-tools:1.32.1 temporal --address temporal:7233 -n pqbr'
$T schedule describe --schedule-id pqbr-soak-24h 2>/dev/null | grep -Ei 'RecentActions|ActionCount|Missed|Running' 
echo "Soak concluídos: $($T workflow count -q 'WorkflowId STARTS_WITH "pqbr-soak" AND ExecutionStatus="Completed"')"
echo "Soak falhos/expirados: $($T workflow count -q 'WorkflowId STARTS_WITH "pqbr-soak" AND ExecutionStatus!="Completed" AND ExecutionStatus!="Running"')"
echo "Efeitos de outbox duplicados: $(sed -n 's/.*"chave": "\([^"]*\)".*/\1/p' "$R/runtime/tz/efeitos.jsonl" | sort | uniq -d | wc -l)"
