"""Google Drive da PQBR (t427), só stdlib. Credencial: OAuth do usuário (refresh token) em arquivo 600 fora do repo,
caminho em PQBR_DRIVE_CRED_ARQ (padrão ~/.pqbr/secrets/google_drive_token.json). Nunca imprime nem loga o token.
Regras (REGRAS §21): nunca apaga; confere tamanho e md5 após o upload; estrutura PQBR/02_Episodios/AAAA-MM/<código>_<tema>."""
from __future__ import annotations
import hashlib, json, os, time, urllib.parse, urllib.request
from pathlib import Path

ARQ_CRED = Path(os.environ.get("PQBR_DRIVE_CRED_ARQ", str(Path.home() / ".pqbr/secrets/google_drive_token.json")))
API = "https://www.googleapis.com/drive/v3"
UP = "https://www.googleapis.com/upload/drive/v3/files"
PASTA = "application/vnd.google-apps.folder"
_cache: dict = {}


def _acesso() -> str:
    if _cache.get("exp", 0) > time.time() + 60:
        return _cache["tok"]
    c = json.loads(ARQ_CRED.read_text())
    corpo = urllib.parse.urlencode({"client_id": c["client_id"], "client_secret": c["client_secret"],
                                    "refresh_token": c["refresh_token"], "grant_type": "refresh_token"}).encode()
    with urllib.request.urlopen(urllib.request.Request(c.get("token_uri", "https://oauth2.googleapis.com/token"), data=corpo), timeout=30) as r:
        j = json.load(r)
    _cache.update(tok=j["access_token"], exp=time.time() + int(j.get("expires_in", 3600)))
    return _cache["tok"]


def _req(metodo: str, url: str, corpo: bytes | None = None, tipo: str = "application/json", extra: dict | None = None):
    h = {"Authorization": "Bearer " + _acesso(), **(extra or {})}
    if corpo is not None: h["Content-Type"] = tipo
    with urllib.request.urlopen(urllib.request.Request(url, data=corpo, method=metodo, headers=h), timeout=600) as r:
        return r.headers, (json.load(r) if r.headers.get("Content-Type", "").startswith("application/json") else r.read())


def buscar(nome: str, pai: str | None, pasta: bool = True) -> str | None:
    q = [f"name = '{nome.replace(chr(39), ' ')}'", "trashed = false"]
    if pasta: q.append(f"mimeType = '{PASTA}'")
    if pai: q.append(f"'{pai}' in parents")
    _, j = _req("GET", f"{API}/files?" + urllib.parse.urlencode({"q": " and ".join(q), "fields": "files(id,name)", "pageSize": 5}))
    f = j.get("files", [])
    return f[0]["id"] if f else None


def garantir_pasta(caminho: str) -> str:
    """Cria (se faltar) e devolve o id de PQBR/a/b/c. Nunca apaga nem move."""
    pai = None
    for parte in [p for p in caminho.split("/") if p]:
        i = buscar(parte, pai)
        if not i:
            meta = {"name": parte, "mimeType": PASTA, **({"parents": [pai]} if pai else {})}
            _, j = _req("POST", f"{API}/files?fields=id", json.dumps(meta).encode())
            i = j["id"]
        pai = i
    return pai


def enviar(arquivo: str, pasta_id: str) -> dict:
    f = Path(arquivo); dados = f.read_bytes(); md5 = hashlib.md5(dados).hexdigest()
    existente = buscar(f.name, pasta_id, pasta=False)
    if existente:   # idempotente: mesmo nome na pasta → confere hash e não reenvia
        _, j = _req("GET", f"{API}/files/{existente}?fields=id,size,md5Checksum")
        if j.get("md5Checksum") == md5: return {"id": existente, "md5": md5, "bytes": len(dados), "reaproveitado": True}
    hdr, _ = _req("POST", f"{UP}?uploadType=resumable", json.dumps({"name": f.name, "parents": [pasta_id]}).encode(),
                  extra={"X-Upload-Content-Length": str(len(dados))})
    _, j = _req("PUT", hdr["Location"], dados, "application/octet-stream")
    _, j = _req("GET", f"{API}/files/{j['id']}?fields=id,size,md5Checksum")
    if j.get("md5Checksum") != md5 or int(j.get("size", 0)) != len(dados):
        raise RuntimeError(f"Drive: hash/tamanho não conferem para {f.name}")
    return {"id": j["id"], "md5": md5, "bytes": len(dados), "reaproveitado": False}


def saude() -> str:
    """Só leitura: confere o token e a pasta raiz PQBR."""
    return "ok" if buscar("PQBR", None) else "token ok, pasta PQBR não encontrada"
