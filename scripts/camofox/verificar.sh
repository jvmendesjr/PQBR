#!/bin/sh
# Verificação do Camofox isolado (F4C-02/03). Não imprime a chave.
set -u
echo "escuta: $(ss -ltn | awk '$4 ~ /:9387$/ {print $4}' | tr '\n' ' ')"
echo "saúde: $(curl -s -m5 http://127.0.0.1:9387/health | head -c 90)"
echo "sem chave: $(curl -s -o /dev/null -w %{http_code} -m5 'http://127.0.0.1:9387/tabs?userId=pqbr') (esperado 401)"
echo "9377 compartilhado: $(curl -s -m5 http://127.0.0.1:9377/health | head -c 60)"
cd /home/pc/Workspace/PQBR && PYTHONPATH=src .venv/bin/python - <<'P'
import asyncio, uuid
from pqbr.workflows.worker import client
from pqbr.workflows.camofox import CamofoxSaudeWorkflow, FILA_CAMOFOX
async def main():
    c = await client()
    hs = [await c.start_workflow(CamofoxSaudeWorkflow.run, 3.0, id=f"camofox-saude-{uuid.uuid4().hex[:6]}", task_queue=FILA_CAMOFOX) for _ in range(2)]
    r = [await h.result() for h in hs]
    a, b = sorted(r, key=lambda x: x.inicio)
    print(f"activity: ok={a.ok} navegador={a.navegador} autenticado={a.autenticado} rss={a.rss_mb}MB")
    print(f"serial (concorrência 1): {'sim' if b.inicio >= a.fim - 0.05 else 'NÃO'} (2ª começou {b.inicio - a.fim:+.2f}s após o fim da 1ª)")
asyncio.run(main())
P
