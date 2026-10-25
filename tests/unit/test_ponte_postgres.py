"""t538: RepositorioPostgres contra Postgres 17 descartável (docker, só 127.0.0.1, porta aleatória).
Opt-in: PQBR_TESTE_PG=1 (precisa de docker)."""
import asyncio, os, shutil, subprocess, time, uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

pytestmark = pytest.mark.skipif(os.environ.get("PQBR_TESTE_PG") != "1" or not shutil.which("docker"), reason="PQBR_TESTE_PG=1 + docker")
R = Path(__file__).resolve().parents[2]; SENHA = "teste-local-" + uuid.uuid4().hex[:8]


@pytest.fixture(scope="module")
def dsn():
    import psycopg
    n = f"pqbr-pgtest-{uuid.uuid4().hex[:8]}"
    subprocess.run(["docker", "run", "-d", "--rm", "--name", n, "-m", "256m", "-p", "127.0.0.1::5432", "-e", "POSTGRES_PASSWORD=" + SENHA,
                    "-e", "POSTGRES_DB=pqbr", "-v", f"{R}:/repo:ro", "postgres:17-alpine"], check=True, capture_output=True)
    try:
        Q = lambda *a, **k: subprocess.run(["docker", "exec", "-i", "-w", "/repo", n, "psql", "-U", "postgres", "-d", "pqbr", "-v", "ON_ERROR_STOP=1", "-qAt", *a], check=True, capture_output=True, **k)
        for _ in range(60):
            if subprocess.run(["docker", "exec", n, "pg_isready", "-U", "postgres", "-q"]).returncode == 0: break
            time.sleep(1)
        time.sleep(2)
        Q("-c", "create role anon nologin; create role authenticated nologin; create role service_role nologin bypassrls;")
        for f in sorted((R / "db/migrations").glob("[0-9][0-9][0-9][0-9]_*.sql")):
            Q("-f", f"/repo/db/migrations/{f.name}")
        Q("-c", f"alter role pqbr_app login password '{SENHA}'; grant connect on database pqbr to pqbr_app")
        porta = subprocess.run(["docker", "port", n, "5432/tcp"], check=True, capture_output=True, text=True).stdout.split(":")[-1].strip()
        base = f"host=127.0.0.1 port={porta} dbname=pqbr"
        yield base, Q
    finally:
        subprocess.run(["docker", "rm", "-f", n], capture_output=True)


@pytest.fixture()
def repo(dsn):
    import psycopg
    from pqbr.workflows.ponte_postgres import RepositorioPostgres
    return RepositorioPostgres(lambda: psycopg.connect(f"{dsn[0]} user=pqbr_app", password=SENHA))


def test_outbox_claim_confirma_e_avisado(repo, dsn):
    from pqbr.contratos.ponte_telegram import MensagemSaida
    from pqbr.workflows.ponte_telegram import enviar_idempotente
    Q = dsn[1]
    rid = Q("-c", "insert into pqbr.revisao_humana (item_tipo, item_ref) values ('tema','pg-1') returning id", text=True).stdout.strip()
    m = MensagemSaida(chave="aviso:pg:0001", classe="aviso_operacional", texto="oi")
    assert repo.enfileirar(m) and not repo.enfileirar(m)
    Q("-c", f"update pqbr.revisao_humana set chave_saida='aviso:pg:0001' where id={rid}")
    class Rem:
        async def enviar(self, m, reenvio): return 77
    r = asyncio.run(enviar_idempotente(repo, Rem(), m.chave))
    assert r.estado == "enviado" and r.mensagem_id == 77
    assert repo.reivindicar(m.chave) is None
    assert Q("-c", f"select avisado_em is not null from pqbr.revisao_humana where id={rid}", text=True).stdout.strip() == "t"


def test_falha_tres_vezes_vira_ticket_unico(repo):
    from pqbr.contratos.ponte_telegram import MensagemSaida
    from pqbr.workflows.ponte_telegram import enviar_idempotente
    m = MensagemSaida(chave="aviso:pg:0002", classe="aviso_operacional", texto="x"); repo.enfileirar(m)
    class Rem:
        async def enviar(self, m, reenvio): raise RuntimeError("fora")
    for _ in range(4): r = asyncio.run(enviar_idempotente(repo, Rem(), m.chave))
    assert r.estado == "ticket" and r.tentativas == 3
    repo.abrir_ticket("ticket:aviso:pg:0002", "de novo")


def test_entrada_dedupe_e_fluxo(repo):
    from pqbr.contratos.ponte_telegram import EventoCallbackTelegram, PedidoAprovacao
    from pqbr.workflows.ponte_telegram import novo_token, processar_callback
    ref = novo_token()
    repo.registrar_pedido(PedidoAprovacao(token=ref, workflow_id="ep-pg", etapa="aguardando_aprovacao", tarefa="publicar",
                                          expira_em=datetime.now(timezone.utc) + timedelta(hours=1)))
    assert repo.pedido(ref).workflow_id == "ep-pg" and repo.pedido("x" * 20) is None
    sinais = []
    async def s(wf, r, d, esp): sinais.append(d); return esp
    ev = lambda uid, d="aprovar": EventoCallbackTelegram(update_id=uid, remetente_id="1", ref_pedido=ref, decisao=d)
    assert asyncio.run(processar_callback(repo, "1", ev(1), s)).status == "sinalizado"
    assert asyncio.run(processar_callback(repo, "1", ev(1), s)).motivo == "update_repetido"
    assert asyncio.run(processar_callback(repo, "1", ev(2, "negar"), s)).motivo == "token_decidido"
    assert sinais == ["aprovar"]
