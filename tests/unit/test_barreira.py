"""TS-SEC: a barreira bloqueia segredo de teste antes de Hindsight, tickets, banco e logs (F3-02)."""
import asyncio, io, logging, unittest
from pqbr.seguranca.barreira import exigir_limpo, FiltroLog, mascarar
from pqbr.seguranca.segredos import SegredoDetectado
from pqbr.storage import hindsight, banco

FALSO = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
IP = "100.101." + "1.2"
EMAIL = "fulano.teste" + "@" + "gmail.com"


class _Conn:
    def __init__(self): self.exec = []
    def cursor(self):
        c = self
        class Cur:
            rowcount = 1
            def __enter__(s): return s
            def __exit__(s, *a): return False
            def execute(s, sql, p): c.exec.append((sql, p))
        return Cur()


class Barreira(unittest.TestCase):
    def test_aninhado(self):
        with self.assertRaises(SegredoDetectado):
            exigir_limpo({"a": [{"b": f"x {FALSO}"}]}, "ticket")
        exigir_limpo({"a": ["texto limpo", 3, None]}, "ticket")

    def test_mensagem_mascarada(self):
        with self.assertRaises(SegredoDetectado) as e:
            exigir_limpo(FALSO, "banco")
        self.assertNotIn(FALSO, str(e.exception))

    def test_hindsight(self):
        enviados = []
        with self.assertRaises(SegredoDetectado):
            hindsight.reter(f"autor {EMAIL} disse", transporte=lambda u, c: enviados.append(c))
        self.assertEqual(enviados, [])
        hindsight.reter("ajuste: botão Publicar mudou de lugar", transporte=lambda u, c: enviados.append(c) or {})
        self.assertEqual(len(enviados), 1)

    def test_banco(self):
        c = _Conn()
        with self.assertRaises(SegredoDetectado):
            banco.escrever(c, "insert into x values (%s)", [FALSO])
        self.assertEqual(c.exec, [])
        banco.escrever(c, "insert into x values (%s)", ["ok"])
        self.assertEqual(len(c.exec), 1)

    def test_ticket_activity(self):
        from temporalio.exceptions import ApplicationError
        from pqbr.workflows import paperclip
        chamou = []
        async def falso_cli(*a): chamou.append(a); return {"id": "1"}
        paperclip._cli = falso_cli
        c = paperclip.Comentario(issue_id="i", corpo=f"senha {FALSO}")
        with self.assertRaises(ApplicationError) as e:
            asyncio.run(paperclip.comentar_paperclip.__wrapped__(c) if hasattr(paperclip.comentar_paperclip, "__wrapped__") else paperclip.comentar_paperclip(c))
        self.assertTrue(e.exception.non_retryable)
        self.assertEqual(chamou, [])

    def test_log(self):
        buf = io.StringIO(); h = logging.StreamHandler(buf); h.addFilter(FiltroLog())
        lg = logging.getLogger("t-barreira"); lg.addHandler(h); lg.propagate = False
        lg.warning("token %s e ip %s", FALSO, IP)
        out = buf.getvalue()
        self.assertNotIn(FALSO, out); self.assertNotIn(IP, out)
        self.assertIn("oculto", mascarar(EMAIL))

    def test_destino_invalido(self):
        with self.assertRaises(ValueError):
            exigir_limpo("x", "drive")


if __name__ == "__main__":
    unittest.main()
