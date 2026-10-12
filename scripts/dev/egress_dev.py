"""Relay de saída dos Devs (rede docker interna pqbr-dev-int): só 9router, Temporal e Paperclip.
Escuta no gateway 172.31.250.1; o container não tem outra rota."""
import asyncio, json, os
from urllib.parse import urlparse
GW = "172.31.250.1"
def _paperclip():
    c = json.load(open(os.path.expanduser("~/.paperclip/context.json")))
    u = urlparse(os.environ.get("PQBR_PAPERCLIP_API") or c["profiles"][c["currentProfile"]]["apiBase"])
    return (u.hostname, u.port or 80)
ROTAS = {20130: ("127.0.0.1", 20130), 7233: ("127.0.0.1", 7233), 3100: _paperclip()}

async def _pipe(r, w):
    try:
        while (b := await r.read(65536)):
            w.write(b); await w.drain()
    except Exception:
        pass
    finally:
        w.close()

def _handler(dest):
    async def h(cr, cw):
        try:
            ur, uw = await asyncio.open_connection(*dest)
        except Exception:
            cw.close(); return
        await asyncio.gather(_pipe(cr, uw), _pipe(ur, cw))
    return h

async def main():
    srv = [await asyncio.start_server(_handler(d), GW, p) for p, d in ROTAS.items()]
    print("egress-dev:", list(ROTAS), flush=True)
    await asyncio.gather(*(s.serve_forever() for s in srv))

asyncio.run(main())
