#!/bin/sh
# Adapter `process` dos agentes só-texto da PQBR (ADR-006, t396). Sem ferramentas; só API do Paperclip + 9router.
cd /home/pc/Workspace/PQBR && PYTHONPATH=src exec .venv/bin/python -m pqbr.kit.agente_texto
