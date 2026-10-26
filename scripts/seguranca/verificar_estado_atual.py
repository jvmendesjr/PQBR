"""Hook pre-commit (t98u/t99u): exige docs/ESTADO-ATUAL.md no commit quando ROADMAP/LACUNAS/DECISOES-LOG/CHANGELOG mudam."""
import subprocess, sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(RAIZ / "src"))
from pqbr.governanca.estado_atual import ESTADO, exige_estado  # noqa: E402
arqs = subprocess.run(["git", "-C", str(RAIZ), "diff", "--cached", "--name-only"], capture_output=True, text=True).stdout.split()
falta = exige_estado(arqs)
if falta:
    print(f"verificar_estado_atual: {', '.join(falta)} mudou sem {ESTADO}. Atualize o estado/pendências e faça git add {ESTADO}.", file=sys.stderr)
    sys.exit(1)
print("verificar_estado_atual: ok.")
