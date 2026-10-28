"""Activities de demonstração. O 'Supabase' é um stub em arquivo local (sem escrita real)."""
from __future__ import annotations
import json, os, fcntl
from pathlib import Path
from temporalio import activity
from temporalio.exceptions import ApplicationError
from .contracts import EpisodioInput, RoteiroShort, OutboxEvento
from ..seguranca.barreira import exigir_limpo
from ..seguranca.segredos import SegredoDetectado

RUNTIME = Path(os.environ.get("PQBR_TZ_DIR", Path(__file__).resolve().parents[3] / "runtime" / "tz"))
RUNTIME.mkdir(parents=True, exist_ok=True)
EFEITOS = RUNTIME / "efeitos.jsonl"        # toda execução com efeito (para provar "uma vez só")
OUTBOX = RUNTIME / "supabase_stub.jsonl"   # tabela simulada
SUPABASE_FORA = RUNTIME / "supabase_fora"  # existe = "Supabase" inacessível


def _append(p: Path, obj: dict) -> None:
    try:
        exigir_limpo(obj, "banco")
    except SegredoDetectado as e:
        raise ApplicationError(str(e), type="SegredoDetectado", non_retryable=True) from None
    with open(p, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")


@activity.defn
async def gerar_roteiro(inp: EpisodioInput) -> RoteiroShort:
    tentativa = activity.info().attempt
    if tentativa <= inp.falhas_simuladas:
        raise ApplicationError(f"falha simulada (tentativa {tentativa})")
    from ..contratos import CTA, BlocoVisual, CenaVisual, ESTILO_PADRAO_STICKMAN
    falas = [f"Por que {inp.tema}?",
             "A explicação é mais lógica do que parece, e a gente repete isso todo santo dia sem perceber.",
             "No fim, é só mais uma mania nossa que tem história, e a história é boa demais.", CTA]
    bloco = BlocoVisual(estilo=ESTILO_PADRAO_STICKMAN,
                        personagem="stickman de tubos pretos, sem roupa, óculos redondos vermelhos, boca fechada (demonstração)",
                        cenas=[CenaVisual(fala=f, acao="personagem reage", enquadramento="plano médio",
                                          ambiente="sala brasileira") for f in falas[:2]])
    return RoteiroShort(episodio_id=inp.episodio_id, titulo=f"Porquê: {inp.tema}"[:100], falas=falas,
                        tipo_cta="fallback", entidades_cena=["personagem"], bloco_visual=bloco)


@activity.defn
async def gravar_outbox(ev: OutboxEvento) -> bool:
    """Grava no 'Supabase' com chave de idempotência; repetir não duplica."""
    from ..seguranca.barreira import exigir_limpo
    from ..seguranca.segredos import SegredoDetectado
    try:
        exigir_limpo(ev, "banco")
    except SegredoDetectado as e:
        raise ApplicationError(str(e), type="SegredoDetectado", non_retryable=True) from None
    if SUPABASE_FORA.exists():
        raise ApplicationError("supabase indisponível (simulado)")
    ja = set()
    if OUTBOX.exists():
        ja = {json.loads(l)["chave_idempotencia"] for l in OUTBOX.read_text().splitlines() if l.strip()}
    if ev.chave_idempotencia in ja:
        return False
    _append(OUTBOX, ev.model_dump(mode="json"))
    _append(EFEITOS, {"chave": ev.chave_idempotencia, "tentativa": activity.info().attempt})
    return True


from .contracts import PropostaAgente  # noqa: E402

APLICADAS = RUNTIME / "propostas_aplicadas.jsonl"


@activity.defn
async def aplicar_proposta_stub(p: PropostaAgente) -> bool:
    """Stub: registra a aplicação em arquivo local; nenhuma mudança real."""
    _append(APLICADAS, {"workflow": activity.info().workflow_id, **p.model_dump()})
    return True
