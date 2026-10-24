"""TS-SEC/F3-02: bloqueio antes dos efeitos; somente dados sintéticos e mocks."""
import asyncio
import importlib
import io
import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import AsyncMock, Mock, patch
import urllib.error

import pytest

from pqbr.seguranca.barreira import FiltroLog, exigir_limpo, instalar_no_logging
from pqbr.seguranca.segredos import SegredoDetectado
from pqbr.storage import banco, hindsight

FALSO = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
EMAIL = "pessoa.sintetica" + "@" + "gmail.com"
OPACO = "somente_valor_sintetico_123"
RAIZ = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def sem_efeitos_reais(tmp_path, monkeypatch):
    monkeypatch.setenv("PQBR_TZ_DIR", str(tmp_path / "runtime"))
    monkeypatch.setenv("PQBR_PAPERCLIP_API", "http://127.0.0.1:1")
    monkeypatch.setenv("PAPERCLIP_API_KEY", "teste-local")
    with patch("urllib.request.urlopen", side_effect=AssertionError("rede proibida")), \
         patch("asyncio.create_subprocess_exec", side_effect=AssertionError("processo proibido")):
        yield


@pytest.mark.parametrize("obj", [
    {"password": OPACO}, {"nested": [{"api_key": OPACO}]},
    {FALSO: "valor"}, {"valor": FALSO.encode()},
    {"valor": memoryview(FALSO.encode())}, {"valor": EMAIL},
    {"user_id": 123456789012},
])
def test_estrutura_e_erro_sem_valor_ou_chave(obj):
    for destino in ("hindsight", "ticket", "banco", "log", "commit"):
        with pytest.raises(SegredoDetectado) as e:
            exigir_limpo(obj, destino)
        assert FALSO not in str(e.value)
        assert EMAIL not in str(e.value)
        assert OPACO not in str(e.value)


@pytest.mark.parametrize("valor", [FALSO, EMAIL])
@pytest.mark.parametrize("campo", ["conteudo", "contexto"])
def test_hindsight_antes_do_transporte(valor, campo):
    transporte = Mock(return_value={})
    with pytest.raises(SegredoDetectado):
        hindsight.reter(**{campo: valor, **({"conteudo": "limpo"} if campo == "contexto" else {})}, transporte=transporte)
    transporte.assert_not_called()
    hindsight.reter("ajuste de seletor", "licao", transporte=transporte)
    transporte.assert_called_once()


@pytest.mark.parametrize("valor", [FALSO, EMAIL])
@pytest.mark.parametrize("inline", [False, True])
def test_banco_bloqueia_antes_de_abrir_cursor(valor, inline):
    conn = Mock()
    sql, params = (f"insert into exemplo values ('{valor}')", ()) if inline else ("insert into exemplo values (%s)", [valor])
    with pytest.raises(SegredoDetectado):
        banco.escrever(conn, sql, params)
    conn.cursor.assert_not_called()


def test_banco_limpo_executa_uma_vez():
    conn = Mock()
    cur = conn.cursor.return_value.__enter__ = Mock()
    conn.cursor.return_value.__exit__ = Mock(return_value=False)
    cur.return_value.rowcount = 1
    assert banco.escrever(conn, "insert into exemplo values (%s)", ["limpo"]) == 1
    cur.return_value.execute.assert_called_once()


@pytest.mark.parametrize("valor", [FALSO, EMAIL])
@pytest.mark.parametrize("acao", ["comentar", "atualizar", "criar_issue"])
def test_ticket_api_bloqueia_antes_do_http(valor, acao):
    api = importlib.import_module("pqbr.kit.paperclip_api")
    with patch.object(api.urllib.request, "urlopen") as enviar:
        with pytest.raises(SegredoDetectado):
            if acao == "comentar":
                api.comentar("issue-teste", valor)
            elif acao == "atualizar":
                api.atualizar("issue-teste", description=valor)
            else:
                api.criar_issue("empresa-teste", title="teste", description=valor)
        enviar.assert_not_called()


def test_ticket_api_limpo_e_erro_sem_resposta_bruta():
    api = importlib.import_module("pqbr.kit.paperclip_api")
    resposta = Mock()
    resposta.__enter__ = Mock(return_value=resposta)
    resposta.__exit__ = Mock(return_value=False)
    resposta.read.return_value = b'{"id":"teste"}'
    with patch.object(api.urllib.request, "urlopen", return_value=resposta) as enviar:
        assert api.comentar("issue-teste", "limpo") == {"id": "teste"}
        enviar.assert_called_once()
    erro = urllib.error.HTTPError("http://127.0.0.1:1", 400, "erro", {}, io.BytesIO(FALSO.encode()))
    with patch.object(api.urllib.request, "urlopen", side_effect=erro):
        with pytest.raises(RuntimeError) as e:
            api.comentar("issue-teste", "limpo")
        assert FALSO not in str(e.value)
        assert str(e.value) == "Paperclip: HTTP 400"


@pytest.mark.parametrize("valor", [FALSO, EMAIL])
@pytest.mark.parametrize("acao", ["abrir", "comentar", "concluir"])
def test_ticket_temporal_bloqueia_sem_processo(valor, acao):
    from temporalio.exceptions import ApplicationError
    from pqbr.workflows import paperclip as p
    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as processo:
        with pytest.raises(ApplicationError) as e:
            if acao == "abrir":
                pedido = p.PedidoIssue(company_id="c", project_id="p", marcador="m", titulo="teste", descricao=valor)
                asyncio.run(p.abrir_issue_paperclip(pedido))
            elif acao == "comentar":
                asyncio.run(p.comentar_paperclip(p.Comentario(issue_id="i", corpo=valor)))
            else:
                asyncio.run(p.concluir_issue_paperclip(valor))
        assert e.value.non_retryable
        assert FALSO not in str(e.value)
        processo.assert_not_called()


def test_ticket_cli_erro_sem_stderr():
    from temporalio.exceptions import ApplicationError
    from pqbr.workflows import paperclip as p
    processo = Mock(returncode=1)
    processo.communicate = AsyncMock(return_value=(b"", FALSO.encode()))
    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock, return_value=processo):
        with pytest.raises(ApplicationError) as e:
            asyncio.run(p._cli("issue", "list"))
        assert FALSO not in str(e.value)


@pytest.mark.parametrize("valor", [FALSO, EMAIL])
def test_stub_bloqueia_antes_do_arquivo(tmp_path, valor):
    from temporalio.exceptions import ApplicationError
    from pqbr.workflows import activities
    destino = tmp_path / "nao-criado.jsonl"
    with pytest.raises(ApplicationError) as e:
        activities._append(destino, {"valor": valor})
    assert e.value.non_retryable
    assert not destino.exists()
    activities._append(destino, {"valor": "limpo"})
    assert "limpo" in destino.read_text()


@pytest.mark.parametrize("origem", ["msg", "args", "extra", "exc", "exc_text", "stack_info"])
@pytest.mark.parametrize("valor", [FALSO, EMAIL])
def test_logs_descartam_registro_contaminado(origem, valor):
    buf = io.StringIO()
    handler = logging.StreamHandler(buf)
    logger = logging.Logger("f3-02-teste")
    logger.addHandler(handler)
    instalar_no_logging(logger)
    instalar_no_logging(logger)
    assert sum(isinstance(f, FiltroLog) for f in handler.filters) == 1
    if origem == "msg":
        logger.warning(valor)
    elif origem == "args":
        logger.warning("dado %s", valor)
    elif origem == "extra":
        logger.warning("texto limpo", extra={"payload": {"valor": valor}})
    elif origem == "exc":
        try:
            raise RuntimeError(valor)
        except RuntimeError:
            logger.exception("falhou")
    else:
        record = logger.makeRecord(logger.name, logging.WARNING, "teste.py", 1, "limpo", (), None)
        setattr(record, origem, valor)
        logger.handle(record)
    assert buf.getvalue() == ""
    logger.warning("registro limpo %s", "preservado")
    assert "registro limpo preservado" in buf.getvalue()


@pytest.mark.parametrize("valor", [FALSO, EMAIL, "texto limpo"])
def test_hook_real_com_indice_descartavel(tmp_path, valor):
    # Não toca no índice/checkout real e não executa git commit.
    repo = tmp_path / "repo"
    repo.mkdir()
    for rel in ("scripts/seguranca/verificar_segredos.py", ".githooks/pre-commit", "src/pqbr/seguranca/segredos.py"):
        dest = repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RAIZ / rel, dest)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    for args in (("init", "-q"), ("config", "core.hooksPath", ".githooks")):
        subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True)
    (repo / "amostra.txt").write_text(valor + "\n")
    subprocess.run(["git", "add", "amostra.txt"], cwd=repo, env=env, check=True, capture_output=True)
    r = subprocess.run(["sh", ".githooks/pre-commit"], cwd=repo, env=env, capture_output=True, text=True)
    assert r.returncode == (0 if valor == "texto limpo" else 1), r.stdout + r.stderr
    if valor != "texto limpo":
        assert valor not in r.stdout + r.stderr


@pytest.mark.parametrize("valor", [FALSO, EMAIL, {"password": OPACO}])
@pytest.mark.parametrize("caminho", ["connection", "cursor", "executemany"])
def test_conexao_protegida_sem_bypass(valor, caminho):
    real = Mock()
    conn = banco.ConexaoProtegida(real)
    with pytest.raises(SegredoDetectado):
        if caminho == "connection":
            conn.execute("insert into exemplo values (%s)", [valor])
        elif caminho == "cursor":
            conn.cursor().execute("insert into exemplo values (%s)", [valor])
        else:
            conn.cursor().executemany("insert into exemplo values (%s)", iter([["limpo"], [valor]]))
    real.execute.assert_not_called()
    real.cursor.return_value.execute.assert_not_called()
    real.cursor.return_value.executemany.assert_not_called()


def test_conexao_e_cursor_preservam_contexto_e_leitura():
    from unittest.mock import MagicMock
    real = MagicMock()
    real.execute.return_value.fetchone.return_value = (7,)
    real.cursor.return_value.fetchone.return_value = (8,)
    conn = banco.ConexaoProtegida(real)
    with conn as ativo:
        assert ativo is conn
        assert ativo.execute("select id from exemplo").fetchone() == (7,)
        with ativo.cursor() as cur:
            assert cur.execute("select id from exemplo").fetchone() == (8,)
            assert cur.executemany("insert into exemplo values (%s)", [["um"], ["dois"]]) is cur
        ativo.commit()
    real.__enter__.assert_called_once()
    real.__exit__.assert_called_once()
    real.commit.assert_called_once()
    real.cursor.return_value.__enter__.assert_called_once()
    real.cursor.return_value.__exit__.assert_called_once()


def test_conectar_instala_protecao_sem_banco_real(monkeypatch):
    import psycopg
    monkeypatch.setenv("PQBR_APP_PASSWORD", "teste-local")
    real = Mock()
    with patch.object(psycopg, "connect", return_value=real) as conectar:
        conn = banco.conectar()
        assert isinstance(conn, banco.ConexaoProtegida)
        with pytest.raises(SegredoDetectado):
            conn.execute("insert into exemplo values (%s)", [FALSO])
        real.execute.assert_not_called()
        conectar.assert_called_once()


def test_sql_composable_e_json_opaco():
    from psycopg import sql
    conn = banco.ConexaoProtegida(Mock())
    with pytest.raises(SegredoDetectado):
        conn.execute(sql.SQL("insert into exemplo values ('" + FALSO + "')"))
    with pytest.raises(SegredoDetectado):
        exigir_limpo('{"password": "' + OPACO + '"}', "banco")


def test_sql_bytes_e_copy_nao_suportado():
    conn = banco.ConexaoProtegida(Mock())
    with pytest.raises(SegredoDetectado):
        conn.execute(("insert into exemplo values ('" + FALSO + "')").encode())
    with pytest.raises(ValueError, match="COPY"):
        conn.cursor().copy("COPY exemplo FROM STDIN")


@pytest.mark.parametrize("acao", ["evento", "aviso", "pedido", "caderno"])
@pytest.mark.parametrize("valor", [FALSO, EMAIL])
def test_activities_sql_direto_passam_pela_barreira(acao, valor):
    from unittest.mock import MagicMock
    from pqbr.workflows import acesso, pacote
    real = MagicMock()
    real.execute.return_value.fetchone.return_value = None
    with patch.object(pacote, "_banco", return_value=banco.ConexaoProtegida(real)):
        with pytest.raises(SegredoDetectado):
            if acao == "evento":
                asyncio.run(acesso.registrar_evento(acesso.EventoAcesso(servico="notebooklm", tipo="queda", causa=valor)))
            elif acao == "aviso":
                asyncio.run(acesso.avisar_jose("notebooklm", valor))
            elif acao == "pedido":
                asyncio.run(acesso.pedir_jose(acesso.PedidoJose(servico="notebooklm", motivo=valor, acao_jose="verificar")))
            else:
                asyncio.run(pacote.registro_caderno("aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee", "PQBR-EP9999", valor, None))
    # pedir_jose pode fazer leitura de idempotência; INSERT/UPDATE não chegam ao driver.
    for chamada in real.execute.call_args_list:
        assert chamada.args[0].lstrip().lower().startswith("select")
    real.commit.assert_not_called()
