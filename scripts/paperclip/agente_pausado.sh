#!/bin/sh
# Stub do adaptador `process` dos agentes da PQBR (F1-01): não executa nada.
# O hermes_local força --yolo (H-SDD1) e não é usado; liberar um agente real é decisão do José.
echo "pqbr: agente ${PAPERCLIP_AGENT_ID:-?} em modo stub (sem execução)." >&2
exit 0
