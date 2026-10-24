import asyncio, pytest
from pydantic import ValidationError
from pydantic_ai.models.test import TestModel
from pqbr.agents import persona, criar_agente, rodar, REGISTRO
from pqbr.contratos import PropostaTemas
from pqbr.motores import PedidoMotor, RespostaMotor, motor_intelectual, gerador_video, MotorIntelectual, config
from pqbr.workflows.temas import propostas_de, pedido_temas, parse_direto


def test_persona_sem_frontmatter():
    p = persona("lider-editorial")
    assert p.startswith("# Líder Editorial") and "reportsTo" not in p


def test_registro_combo():
    _, combos = criar_agente("lider-editorial", PropostaTemas, model=TestModel())
    assert combos[0] == "core-medio" and "lider-editorial" in REGISTRO


def test_rodar_testmodel_saida_tipada():
    tm = TestModel(custom_output_args={"temas": [
        {"categoria": "expressao", "tema": "Por que se diz 'pagar o pato'?"},
        {"categoria": "habito_mania", "tema": "Por que o brasileiro guarda sacola de mercado?"}],
        "justificativa": "perenes"})
    out, meta = asyncio.run(rodar("lider-editorial", PropostaTemas, "extraia", model=tm))
    assert isinstance(out, PropostaTemas) and meta["combo"] == "core-medio"
    assert [p["categoria"] for p in propostas_de(out)] == ["expressao", "habito_mania"]


def test_contrato_recusa_sazonal_e_sem_por_que():
    with pytest.raises(ValidationError):
        PropostaTemas(temas=[{"categoria": "sazonal", "tema": "Por que tem quadrilha?"}], justificativa="x")
    with pytest.raises(ValidationError):
        PropostaTemas(temas=[{"categoria": "expressao", "tema": "Origem do pagar o pato"}], justificativa="x")


def test_pedido_temas_valida_e_sessao_efemera():
    d = pedido_temas(3, ["Por que o PIX se chama PIX?"], "2026-10-24")
    p = PedidoMotor.model_validate(d)
    assert p.sessao == "grade-temas-2026w43" and "PIX" in p.contexto and p.tarefa == "temas"


def test_parse_direto_descarta_invalidos():
    txt = 'ok: {"temas": [{"categoria": "expressao", "tema": "Por que se diz pagar o pato?"}, {"categoria": "sazonal", "tema": "Por que quadrilha?"}], "justificativa": "x"}'
    out = parse_direto(txt)
    assert [t.categoria for t in out.temas] == ["expressao"]
    assert parse_direto("sem json") is None


def test_portas_por_config():
    c = config()
    assert c["intelectual"] == "notebooklm" and c["video"] == "flow"
    m = motor_intelectual()
    assert isinstance(m, MotorIntelectual) and m.nome == "notebooklm"
    with pytest.raises(KeyError): motor_intelectual("inexistente")
    with pytest.raises(NotImplementedError): gerador_video()


def test_motor_falso_troca_sem_mudar_fluxo():
    class Falso:
        nome = "falso"
        def consultar(self, p): return RespostaMotor(motor="falso", sessao_id="s", texto='{"temas":[{"categoria":"expressao","tema":"Por que se diz caiu a ficha?"}]}')
    r = Falso().consultar(PedidoMotor.model_validate(pedido_temas(1, [], "2026-10-24")))
    assert isinstance(Falso(), MotorIntelectual) and parse_direto(r.texto).temas[0].tema.startswith("Por que")


def test_oito_papeis_com_persona_e_combo():
    from pqbr.kit.router9 import combo
    assert len(REGISTRO) == 8
    for p in REGISTRO:
        assert persona(p) and combo(p).startswith("core-")
