"""t528: criar_instancia.sh idempotente — tudo em tmp, sem systemd real."""
import os, re, subprocess
from pathlib import Path
S = Path(__file__).resolve().parents[2] / "deploy/camofox/criar_instancia.sh"


def run(tmp, *a):
    env = dict(os.environ, HOME=str(tmp / "home"), CAMOFOX_INSTANCIAS_DIR=str(tmp / "inst"),
               SYSTEMD_DIR=str(tmp / "sd"), SKIP_PORT_CHECK="1")
    return subprocess.run(["sh", str(S), "teste-ficticio", "9391", *a], env=env, capture_output=True, text=True)


def chaves(e):
    return dict(re.findall(r"^(CAMOFOX_\w+_KEY)=(.*)$", e.read_text(), re.M))


def test_idempotente_e_instalar(tmp_path):
    e = tmp_path / "inst/teste-ficticio.env"
    r1 = run(tmp_path); assert r1.returncode == 0, r1.stdout + r1.stderr
    k1 = chaves(e); assert len(k1) == 3 and all(len(v) > 30 for v in k1.values())
    assert oct(e.stat().st_mode)[-3:] == "600" and "<" not in e.read_text()
    assert not any(v in r1.stdout + r1.stderr for v in k1.values())
    r2 = run(tmp_path); assert r2.returncode == 0 and "geradas agora: 0" in r2.stdout and chaves(e) == k1
    # incompleto: placeholder volta e uma chave some → só elas são geradas
    t = e.read_text().replace(f"CAMOFOX_ADMIN_KEY={k1['CAMOFOX_ADMIN_KEY']}", "CAMOFOX_ADMIN_KEY=<gerar>")
    t = "\n".join(l for l in t.splitlines() if not l.startswith("CAMOFOX_ACCESS_KEY")) + "\n"
    e.write_text(t)
    r3 = run(tmp_path); assert r3.returncode == 0 and "geradas agora: 2" in r3.stdout
    k3 = chaves(e); assert k3["CAMOFOX_API_KEY"] == k1["CAMOFOX_API_KEY"] and len(k3) == 3
    for _ in range(2):
        r = run(tmp_path, "--instalar"); assert r.returncode == 0, r.stdout + r.stderr
    assert (tmp_path / "sd/camofox@.service").exists() and "já instalado" in r.stdout
    assert chaves(e) == k3


def test_porta_divergente_aborta(tmp_path):
    assert run(tmp_path).returncode == 0
    env = dict(os.environ, HOME=str(tmp_path / "home"), CAMOFOX_INSTANCIAS_DIR=str(tmp_path / "inst"), SKIP_PORT_CHECK="1")
    r = subprocess.run(["sh", str(S), "teste-ficticio", "9392"], env=env, capture_output=True, text=True)
    assert r.returncode == 2
