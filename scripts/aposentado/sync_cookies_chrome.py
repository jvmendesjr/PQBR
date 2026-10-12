#!/usr/bin/env python3
"""Reautenticação do Camofox da PQBR (playbook camofox-sessao, passo 2; ADR-008, t395).
Copia os cookies do Google/YouTube do perfil Chrome **PorqueBR** (só esse) para a sessão `pqbr` da instância
`pqbr-camofox` (127.0.0.1:9387). Nunca imprime, grava ou registra valores de cookie: só contagens.
Uso: sync_cookies_chrome.py [--dry-run]   (saída 0 = ok; 2 = nada a sincronizar; 1 = erro)"""
from __future__ import annotations
import hashlib, json, os, shutil, sqlite3, subprocess, sys, tempfile, time, urllib.request

PERFIL = os.path.expanduser("~/.config/google-chrome/PorqueBR")  # perfil do canal; nenhum outro
DOMINIOS = (".youtube.com", "youtube.com", ".google.com", "accounts.google.com", ".accounts.google.com", "studio.youtube.com")
CAMOFOX = os.environ.get("PQBR_CAMOFOX_URL", "http://127.0.0.1:9387")
ENV_CAMOFOX = os.path.expanduser("~/.pqbr/camofox/.env")
LOG = os.path.expanduser("~/.pqbr/logs/cookies-sync.log")
USUARIO = "pqbr"


def _log(msg: str) -> None:
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%S%z ") + msg + "\n")
    print(msg)


def _senha_chrome() -> bytes:
    for app in ("chrome", "Chrome"):
        r = subprocess.run(["secret-tool", "lookup", "application", app], capture_output=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return b"peanuts"  # v10 sem keyring


def _chave(senha: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha1", senha, b"saltysalt", 1, 16)


def _decifrar(blob: bytes, chaves: list[bytes], host: str) -> str | None:
    if blob[:3] not in (b"v10", b"v11"):
        return None
    for k in chaves:
        r = subprocess.run(["openssl", "enc", "-d", "-aes-128-cbc", "-K", k.hex(), "-iv", "20" * 16],
                           input=blob[3:], capture_output=True)
        if r.returncode != 0:
            continue
        txt = r.stdout
        if len(txt) >= 32 and txt[:32] == hashlib.sha256(host.encode()).digest():
            txt = txt[32:]  # Chrome ≥ 130: prefixo SHA-256 do domínio
        try:
            return txt.decode()
        except UnicodeDecodeError:
            continue
    return None


def ler_cookies() -> list[dict]:
    tmp = tempfile.mkdtemp(prefix="pqbr-ck-")
    try:
        os.chmod(tmp, 0o700)
        db = os.path.join(tmp, "c.db")
        shutil.copy2(os.path.join(PERFIL, "Cookies"), db)
        chaves = [_chave(_senha_chrome()), _chave(b"peanuts")]
        con = sqlite3.connect(db)
        linhas = con.execute("select host_key,name,path,expires_utc,is_secure,is_httponly,samesite,encrypted_value,value from cookies").fetchall()
        con.close()
        out = []
        for host, nome, path, exp, sec, httponly, same, enc, val in linhas:
            if not any(host == d or host.endswith(d) for d in DOMINIOS):
                continue
            v = val or (_decifrar(enc, chaves, host) if enc else None)
            if not v:
                continue
            c = {"name": nome, "value": v, "domain": host, "path": path or "/", "secure": bool(sec), "httpOnly": bool(httponly),
                 "sameSite": {0: "None", 1: "Lax", 2: "Strict"}.get(same, "Lax")}
            if exp:
                c["expires"] = int(exp / 1_000_000 - 11644473600)
            out.append(c)
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _chave_camofox() -> str:
    for l in open(ENV_CAMOFOX, encoding="utf-8"):
        if l.startswith("CAMOFOX_API_KEY="):
            return l.split("=", 1)[1].strip()
    raise RuntimeError("sem chave do Camofox da PQBR")


def main() -> int:
    seco = "--dry-run" in sys.argv
    try:
        ck = ler_cookies()
    except Exception as e:
        _log(f"erro ao ler cookies do perfil PorqueBR: {type(e).__name__}")
        return 1
    _log(f"{'dry-run: ' if seco else ''}{len(ck)} cookies Google/YouTube decifrados do perfil PorqueBR")
    if not ck:
        return 2
    if seco:
        return 0
    r = urllib.request.Request(f"{CAMOFOX}/sessions/{USUARIO}/cookies", data=json.dumps({"cookies": ck[:500]}).encode(), method="POST",
                               headers={"Content-Type": "application/json", "Authorization": "Bearer " + _chave_camofox()})
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            _log(f"importados no Camofox pqbr: HTTP {resp.status}")
    except Exception as e:
        _log(f"falha ao importar no Camofox: {type(e).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
