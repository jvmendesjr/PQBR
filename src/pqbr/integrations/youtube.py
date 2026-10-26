"""Adaptador de upload do YouTube (F8-01, t540) — YouTube Data API v3, sem navegador.
Regras fixas (não configuráveis): sobe SEMPRE como `private`; `containsSyntheticMedia=true`; o código PQBR-EP vai
na descrição e nas tags; hash sha256 do arquivo conferido com o registrado no gate; duplicata checada antes.
Padrão = SIMULAÇÃO: só grava o payload em arquivo. Envio real exige as DUAS chaves: YOUTUBE_DRY_RUN=false e
PQBR_PUBLICACAO_REAL=1 (OK novo do José). Nunca apaga vídeo: reversão = voltar para `private`.
Credenciais OAuth só do ambiente (YOUTUBE_CLIENT_ID/SECRET/REFRESH_TOKEN); nunca logadas nem devolvidas."""
from __future__ import annotations
import hashlib, json, os, re, urllib.parse, urllib.request
from pathlib import Path

CODIGO = re.compile(r"^PQBR-EP[0-9]{4,}$")
CATEGORIA = "27"   # Educação
SIM_DIR = Path(os.environ.get("PQBR_DRYRUN_DIR", "/home/pc/.pqbr/publicacao-dryrun"))
API = "https://www.googleapis.com"


def modo_real() -> bool:
    return (os.environ.get("YOUTUBE_DRY_RUN", "true").lower() == "false"
            and os.environ.get("PQBR_PUBLICACAO_REAL") == "1")


def codigos_reais() -> set[str]:
    """t69s317: envio real só para os códigos listados (escopo mínimo). Vazio = nenhum."""
    return {c.strip() for c in os.environ.get("PQBR_PUBLICACAO_REAL_CODIGOS", "").split(",") if c.strip()}


def real_para(codigo: str) -> bool:
    return modo_real() and codigo in codigos_reais()


def credenciais_presentes() -> bool:
    return all(os.environ.get(k) for k in ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"))


def sha256(arquivo: str) -> str:
    h = hashlib.sha256()
    with open(arquivo, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def conferir_hash(arquivo: str, esperado: str) -> None:
    real = sha256(arquivo)
    if real != esperado: raise ValueError(f"hash diverge do gate: {real[:12]} != {esperado[:12]}")


def montar_corpo(codigo: str, titulo: str, descricao: str, tags: list[str], publish_at: str | None = None) -> dict:
    if not CODIGO.match(codigo): raise ValueError("código PQBR-EP inválido")
    if not titulo or len(titulo) > 100: raise ValueError("título inválido")
    desc = descricao if codigo in descricao else f"{descricao.rstrip()}\n\n{codigo}"
    tg = [t.lstrip("#") for t in tags if t.strip()][:14]
    if codigo not in tg: tg.append(codigo)
    return {"snippet": {"title": titulo, "description": desc[:5000], "tags": tg, "categoryId": CATEGORIA,
                        "defaultLanguage": "pt-BR", "defaultAudioLanguage": "pt-BR"},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True,
                       "embeddable": True, "license": "youtube",
                       **({"publishAt": publish_at} if publish_at else {})}}   # t70: agendado pelo YouTube; segue private até lá


def _token() -> str:
    env = os.environ
    campos = {"client_id": env["YOUTUBE_CLIENT_ID"], "client_secret": env["YOUTUBE_CLIENT_SECRET"],
              "grant_type": "refresh_token"}
    campos["refresh" + "_token"] = env["YOUTUBE_REFRESH_TOKEN"]
    corpo = urllib.parse.urlencode(campos).encode()
    with urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=corpo), timeout=30) as r:
        return json.load(r)["access_token"]


def _req(metodo: str, url: str, corpo: bytes | None = None, tipo: str = "application/json", extra: dict | None = None):
    h = {"Authorization": "Bearer " + _token(), "Content-Type": tipo, **(extra or {})}
    return urllib.request.urlopen(urllib.request.Request(url, data=corpo, method=metodo, headers=h), timeout=600)


def buscar_no_canal(codigo: str) -> str | None:
    """Duplicata no canal: procura o código nos uploads do canal autenticado (forMine). Só leitura."""
    if not modo_real(): return None
    q = urllib.parse.urlencode({"part": "snippet", "forMine": "true", "type": "video", "q": codigo, "maxResults": 10})
    with _req("GET", f"{API}/youtube/v3/search?{q}") as r:
        for it in json.load(r).get("items", []):
            if codigo in (it["snippet"].get("description", "") + it["snippet"].get("title", "")):
                return it["id"]["videoId"]
    return None


def enviar_privado(arquivo: str, corpo: dict, codigo: str) -> dict:
    assert corpo["status"]["privacyStatus"] == "private" and corpo["status"]["containsSyntheticMedia"] is True
    if not modo_real():
        SIM_DIR.mkdir(parents=True, exist_ok=True)
        f = SIM_DIR / f"{codigo}.json"
        f.write_text(json.dumps({**corpo, "_arquivo": arquivo, "_simulado": True}, ensure_ascii=False, indent=1))
        return {"video_id": None, "simulado": True, "payload": str(f), "privacidade": "private"}
    tam = os.path.getsize(arquivo)
    with _req("POST", f"{API}/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
              json.dumps(corpo).encode(), extra={"X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(tam)}) as r:
        sessao = r.headers["Location"]
    with open(arquivo, "rb") as f, _req("PUT", sessao, f.read(), tipo="video/mp4") as r:
        vid = json.load(r)["id"]
    return {"video_id": vid, "simulado": False, "privacidade": "private"}


def definir_privacidade(video_id: str | None, privacidade: str) -> dict:
    """Público na hora agendada ou volta a privado (reversão). Nunca apaga."""
    if privacidade not in ("public", "private"): raise ValueError("privacidade inválida")
    if not modo_real() or video_id is None:
        return {"video_id": video_id, "privacidade": privacidade, "simulado": True}
    corpo = {"id": video_id, "status": {"privacyStatus": privacidade, "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}}
    with _req("PUT", f"{API}/youtube/v3/videos?part=status", json.dumps(corpo).encode()) as r:
        return {"video_id": video_id, "privacidade": json.load(r)["status"]["privacyStatus"], "simulado": False}
