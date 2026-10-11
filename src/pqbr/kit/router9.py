"""Chamada única ao 9router (OpenAI-compatível). Chave só por env (secret_ref do Paperclip)."""
from __future__ import annotations
import json, os, urllib.request

URL = os.environ.get("PQBR_9ROUTER_URL", "http://127.0.0.1:20130/v1").rstrip("/")


def chat(modelo: str, sistema: str, usuario: str, max_tokens: int = 800) -> str:
    corpo = {"model": modelo, "max_tokens": max_tokens, "temperature": 0.2, "stream": False,
             "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}]}
    r = urllib.request.Request(URL + "/chat/completions", data=json.dumps(corpo).encode(), method="POST",
                               headers={"Authorization": "Bearer " + os.environ["NINEROUTER_API_KEY"],
                                        "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=180) as resp:
        return json.load(resp)["choices"][0]["message"]["content"]
