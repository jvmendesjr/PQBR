"""Testes da barreira (TS-SEC). Rodar: PYTHONPATH=src python -m pytest tests/seguranca  (ou python tests/seguranca/test_segredos.py)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from pqbr.seguranca.segredos import encontrar, bloquear, SegredoDetectado

FALSOS = {  # valores inventados, montados em partes para não parecerem reais no código
    "github_token": "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8",
    "telegram_bot_token": "123456789" + ":AA" + "Fake_Token_For_Test_Only_1234567890",
    "email": "fulano.teste" + "@" + "gmail.com",
    "ip_tailnet": "100.101." + "1.2",
    "google_api_key": "AIza" + "SyFAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE1",
    "atribuicao_segredo": "POSTGRES_PASSWORD" + "=" + "abc123def456ghi",
    "jwt": "eyJ" + "hbGciOiJIUzI1NiJ9" + ".eyJ" + "zdWIiOiIxMjM0NTY3ODkwIn0" + ".abcdefghijklmnop",
}


def test_detecta_cada_regra():
    for regra, v in FALSOS.items():
        assert regra in {a.regra for a in encontrar(f"x {v} y")}, regra


def test_nao_vaza_valor():
    a = encontrar(FALSOS["github_token"])[0]
    assert FALSOS["github_token"] not in a.trecho


def test_permite_exemplos():
    assert encontrar("contato: alguem@example.com; POSTGRES_PASSWORD=TROCAR; senha=$SENHA") == []


def test_bloquear():
    try:
        bloquear("token=" + FALSOS["github_token"])
    except SegredoDetectado:
        return
    raise AssertionError("não bloqueou")


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f(); print("ok", n)
