"""Relay de saída dos Devs (rede docker interna pqbr-dev-int): só 9router, Temporal e Paperclip (t415).
O container NÃO recebe segredos: manda `Authorization: Bearer via-relay:<papel>`; o relay troca, **a cada requisição
HTTP**, pelo segredo real lido de ~/.pqbr/dev-secrets/<papel>.env (700/600, fora de qualquer mount do container),
gravado pelo wrapper no início do run e apagado no fim. Temporal (7233) é TCP puro, sem credencial."""
import asyncio, http.client, json, os, re, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

GW = "172.31.250.1"
SEG = Path.home() / ".pqbr/dev-secrets"
PAPEL = re.compile(r"^bearer\s+via-relay:([a-z0-9-]{2,40})$", re.I)
SALTO = {"connection", "keep-alive", "proxy-connection", "transfer-encoding", "te", "trailer", "upgrade", "authorization", "host"}


def _paperclip():
    c = json.load(open(os.path.expanduser("~/.paperclip/context.json")))
    u = urlparse(os.environ.get("PQBR_PAPERCLIP_API") or c["profiles"][c["currentProfile"]]["apiBase"])
    return (u.hostname, u.port or 80)


def _segredo(papel: str, var: str) -> str | None:
    f = SEG / f"{papel}.env"
    if not f.is_file():
        return None
    for l in f.read_text().splitlines():
        if l.startswith(var + "="):
            return l.split("=", 1)[1] or None
    return None


def _handler(dest, var):
    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        def log_message(self, *a): pass
        def _go(self):
            m = PAPEL.match(self.headers.get("Authorization", "").strip())
            seg = _segredo(m.group(1), var) if m else None
            n = int(self.headers.get("Content-Length") or 0)
            corpo = self.rfile.read(n) if n else None
            if not seg:
                self.send_response(401); self.send_header("Content-Length", "0"); self.end_headers(); return
            h = {k: v for k, v in self.headers.items() if k.lower() not in SALTO}
            h["Authorization"] = "Bearer " + seg
            c = http.client.HTTPConnection(*dest, timeout=900)
            try:
                c.request(self.command, self.path, body=corpo, headers=h)
                r = c.getresponse()
                self.send_response(r.status, r.reason)
                for k, v in r.getheaders():
                    if k.lower() not in SALTO and k.lower() != "content-length":
                        self.send_header(k, v)
                self.send_header("Transfer-Encoding", "chunked"); self.end_headers()
                while (b := r.read1(65536)):
                    self.wfile.write(b"%x\r\n%s\r\n" % (len(b), b)); self.wfile.flush()
                self.wfile.write(b"0\r\n\r\n"); self.wfile.flush()
            except Exception:
                self.close_connection = True
            finally:
                c.close()
        do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = _go
    return H


async def _pipe(r, w):
    try:
        while (b := await r.read(65536)):
            w.write(b); await w.drain()
    except Exception:
        pass
    finally:
        w.close()


def _tcp_para(porta):
  async def _tcp(cr, cw):
    try:
        ur, uw = await asyncio.open_connection("127.0.0.1", porta)
    except Exception:
        cw.close(); return
    await asyncio.gather(_pipe(cr, uw), _pipe(ur, cw))
  return _tcp


def main():
    for porta, dest, var in [(20130, ("127.0.0.1", 20130), "NINEROUTER_API_KEY"), (3100, _paperclip(), "PAPERCLIP_API_KEY")]:
        s = ThreadingHTTPServer((GW, porta), _handler(dest, var)); s.daemon_threads = True
        threading.Thread(target=s.serve_forever, daemon=True).start()
    print("egress-dev: 20130/3100 (HTTP, injeta credencial) + 7233/8890 (TCP)", flush=True)
    async def tcp():
        srvs = [await asyncio.start_server(_tcp_para(p), GW, p) for p in (7233, 8890)]  # Temporal + Hindsight (memória)
        await asyncio.gather(*(x.serve_forever() for x in srvs))
    asyncio.run(tcp())

main()
