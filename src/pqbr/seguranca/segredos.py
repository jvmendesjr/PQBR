"""Detector de segredos e PII sem dependências (estilo gitleaks, regras próprias).

Uso como biblioteca (antes de gravar em Hindsight, tickets, Supabase, logs):
    from pqbr.seguranca.segredos import encontrar, bloquear
    bloquear(texto)            # levanta SegredoDetectado se achar algo
Uso no git: scripts/seguranca/verificar_segredos.py (--staged | --tudo).

As regras são genéricas de propósito: nenhum valor real (e-mail, IP, chat ID) aparece neste arquivo.
"""
from __future__ import annotations
import re
from dataclasses import dataclass

REGRAS: list[tuple[str, re.Pattern[str]]] = [
    ("chave_privada", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY")),
    ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("google_oauth_secret", re.compile(r"\bGOCSPX-[0-9A-Za-z_\-]{20,}")),
    ("google_refresh_token", re.compile(r"\b1//0[0-9A-Za-z_\-]{30,}")),
    ("github_token", re.compile(r"\b(?:gh[pousr]_[0-9A-Za-z]{30,}|github_pat_[0-9A-Za-z_]{40,})")),
    ("openai_like_key", re.compile(r"\bsk-(?:proj-|ant-|or-)?[0-9A-Za-z_\-]{20,}")),
    ("xai_key", re.compile(r"\bxai-[0-9A-Za-z]{20,}")),
    ("slack_token", re.compile(r"\bxox[abprs]-[0-9A-Za-z\-]{10,}")),
    ("telegram_bot_token", re.compile(r"\b[0-9]{8,10}:AA[0-9A-Za-z_\-]{30,}")),
    ("supabase_secret", re.compile(r"\bsb_(?:secret|publishable)_[0-9A-Za-z_\-]{20,}")),
    ("jwt", re.compile(r"\beyJ[0-9A-Za-z_\-]{10,}\.eyJ[0-9A-Za-z_\-]{10,}\.[0-9A-Za-z_\-]{10,}")),
    ("url_com_senha", re.compile(r"\b[a-z][a-z0-9+.\-]*://[^\s:/@]+:[^\s@/]{3,}@[^\s]+", re.I)),
    ("atribuicao_segredo", re.compile(
        r"(?i)\b[A-Za-z0-9_]*(?:password|passwd|senha|secret|token|api[_-]?key|private[_-]?key|client[_-]?secret|pwd)[A-Za-z0-9_]*"
        r"['\"]?\s*[:=]\s*['\"]?(?!\$|<|\{|scram-sha-256|md5\b|TROCAR|teste-local|xxx|\*\*\*|changeme|None|null|\"\"|'')[^\s'\"]{8,}")),
    ("cookie_sessao", re.compile(r"(?i)\b(?:SAPISID|__Secure-[0-9A-Za-z]+PSID[A-Za-z]*|SID|HSID|SSID)=[0-9A-Za-z_\-]{16,}")),
    ("email", re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}\b")),
    ("ip_tailnet", re.compile(r"\b100\.(?:6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])\.[0-9]{1,3}\.[0-9]{1,3}\b")),
    ("host_tailnet", re.compile(r"\b[a-z0-9\-]+\.(?:tail[0-9a-f]{4,}\.)?ts\.net\b|\btail[0-9a-f]{6}\b", re.I)),
    ("telegram_chat_id", re.compile(r"(?i)\b(?:chat[_ ]?id|telegram[_ ]?id|user[_ ]?id)\b\s*[:=]\s*['\"]?-?[0-9]{9,}")),
    ("id_numerico_longo_negativo", re.compile(r"(?<![0-9.])-100[0-9]{10}\b")),
]

# E-mails permitidos (exemplos e endereços sem pessoa)
EMAIL_OK = re.compile(r"(?i)@(?:example\.(?:com|org|net)|exemplo\.com|x\.com|users\.noreply\.github\.com)$|^(?:noreply|no-reply|git)@")


@dataclass(frozen=True)
class Achado:
    regra: str
    trecho: str  # já mascarado

    def __str__(self) -> str:
        return f"{self.regra}: {self.trecho}"


class SegredoDetectado(ValueError):
    pass


def _mascarar(s: str) -> str:
    return f"[oculto; {len(s)} chars]"


def encontrar(texto: str) -> list[Achado]:
    achados = []
    for nome, rx in REGRAS:
        for m in rx.finditer(texto):
            v = m.group(0)
            if nome == "email" and EMAIL_OK.search(v):
                continue
            achados.append(Achado(nome, _mascarar(v)))
    return achados


def bloquear(texto: str) -> str:
    a = encontrar(texto)
    if a:
        raise SegredoDetectado("; ".join(map(str, a)))
    return texto
