import json
import sys
from pathlib import Path
import pytest

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))


def test_stdout_dinamico_contaminado_descartado(capsys):
    from pqbr.kit.agente_texto import _imprimir_limpo
    secret = "api_key=abcdefghij1234567890"
    _imprimir_limpo(f"modelo={secret}")
    out = capsys.readouterr()
    assert secret not in out.out + out.err
    assert out.out == ""


def test_stdout_limpo_preservado(capsys):
    from pqbr.kit.agente_texto import _imprimir_limpo
    _imprimir_limpo("pqbr-kit: modelo=router9 descricao=12")
    assert capsys.readouterr().out == "pqbr-kit: modelo=router9 descricao=12\n"


def test_estado_indexador_exige_metadados_limpos():
    import importlib.util
    spec = importlib.util.spec_from_file_location("pqbr_indexar_test", RAIZ / "scripts/hindsight/indexar.py")
    indexar = importlib.util.module_from_spec(spec)
    antes = list(sys.path)
    try:
        spec.loader.exec_module(indexar)
    finally:
        sys.path[:] = antes   # indexar.py fixa o src do checkout principal no sys.path; não vazar para outros testes (sandbox do Temporal)
    assert indexar.validar_estado({"commit:a1": "abcdef0123456789"})["commit:a1"] == "abcdef0123456789"
    with pytest.raises(Exception):
        indexar.validar_estado({"ghp_" + "A" * 36: "abcdef0123456789"})
    with pytest.raises(ValueError, match="estado inválido"):
        indexar.validar_estado({"ok": 42})


def test_jsonrpc_saida_limpa_preserva_contrato(capsys):
    from pqbr.kit.mcp_kit import _imprimir_jsonrpc
    _imprimir_jsonrpc({"jsonrpc": "2.0", "id": "req-1", "result": {"content": [{"type": "text", "text": "ok"}]}})
    assert json.loads(capsys.readouterr().out) == {"jsonrpc": "2.0", "id": "req-1", "result": {"content": [{"type": "text", "text": "ok"}]}}


def test_jsonrpc_saida_sensivel_nao_echo_id(capsys):
    from pqbr.kit.mcp_kit import _imprimir_jsonrpc
    sensitive_id = "pii.sintetica" + "@" + "gmail.com"
    _imprimir_jsonrpc({"jsonrpc": "2.0", "id": sensitive_id, "error": {"code": -32000, "message": "api_key=abcdefghij1234567890"}})
    out = capsys.readouterr().out
    assert sensitive_id not in out
    assert "api_key=abcdefghij1234567890" not in out
    response = json.loads(out)
    assert response["error"]["message"] == "resposta bloqueada"
    assert response["id"] is None


def test_jsonrpc_erro_preserva_id_limpo(capsys):
    from pqbr.kit.mcp_kit import _imprimir_jsonrpc
    _imprimir_jsonrpc({"jsonrpc": "2.0", "id": "req-2", "result": {"text": "ghp_" + "A" * 36}})
    response = json.loads(capsys.readouterr().out)
    assert response["id"] == "req-2"
    assert response["error"]["code"] == -32000


def test_jsonrpc_id_contaminado_bloqueia_mesmo_com_resultado_limpo(capsys):
    from pqbr.kit.mcp_kit import _imprimir_jsonrpc
    _imprimir_jsonrpc({"jsonrpc": "2.0", "id": "ghp_" + "A" * 36, "result": {"text": "limpo"}})
    response = json.loads(capsys.readouterr().out)
    assert response["id"] is None
    assert "result" not in response
