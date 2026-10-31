"""F3-05/RF-44/TS-11: diagnóstico estático, sem importar/iniciar Workers.

XFAIL estritos são lacunas abertas, não aceite nem comprovação de concorrência.
O teste de task_queue exige revisão se o desenho de roteamento for alterado.
"""
import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def tree(name):
    return ast.parse((ROOT / "src/pqbr/workflows" / name).read_text())


def calls(module, name):
    return [node for node in ast.walk(tree(module))
            if isinstance(node, ast.Call)
            and ((isinstance(node.func, ast.Name) and node.func.id == name)
                 or (isinstance(node.func, ast.Attribute) and node.func.attr == name))]


def worker_options(module):
    workers = calls(module, "Worker")
    assert len(workers) == 1, "Revisar diagnóstico: construção dos Workers mudou"
    return {kw.arg: kw.value for kw in workers[0].keywords}


def intervention_calls():
    result = [call for call in calls("correcao.py", "execute_activity")
              if call.args and isinstance(call.args[0], ast.Name)
              and call.args[0].id == "intervir_agente"]
    assert len(result) == 1, "Revisar diagnóstico: caminho de intervenção mudou"
    return result


def names(node):
    return {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}


def constant(module, name):
    values = [node.value for node in tree(module).body
              if isinstance(node, ast.Assign)
              and any(isinstance(target, ast.Name) and target.id == name
                      for target in node.targets)]
    assert len(values) == 1
    return ast.literal_eval(values[0])


def test_worker_camofox_declara_fila_da_sessao_e_limite_um():
    options = worker_options("worker_camofox.py")
    assert isinstance(options["task_queue"], ast.Name)
    assert options["task_queue"].id == "FILA_CAMOFOX"
    assert constant("camofox.py", "FILA_CAMOFOX") == "camofox-pqbr"
    assert ast.literal_eval(options["max_concurrent_activities"]) == 1


def test_workflow_e_intervencao_ainda_registrados_no_worker_principal():
    options = worker_options("worker.py")
    assert "CorrecaoAutonomaWorkflow" in names(options["workflows"])
    assert "intervir_agente" in names(options["activities"])
    assert options["task_queue"].id == "FILA"
    assert constant("worker.py", "FILA") == "pqbr-episodio"


def test_politica_intervencao_permanece_uma_execucao_por_activity():
    options = {kw.arg: kw.value for kw in intervention_calls()[0].keywords}
    policy = options["retry_policy"]
    assert isinstance(policy, ast.Call) and policy.func.id == "RetryPolicy"
    assert {kw.arg: ast.literal_eval(kw.value) for kw in policy.keywords} == {
        "maximum_attempts": 1,
    }


@pytest.mark.xfail(strict=True, reason=(
    "F3-05/G4 aberto: intervenção herda fila do workflow; não há task_queue explícita. "
    "Não comprova nem corrige roteamento por ferramenta/sessão."
))
def test_contrato_intervencao_tem_roteamento_explicito_para_fila_da_ferramenta():
    assert "task_queue" in {kw.arg for kw in intervention_calls()[0].keywords}


@pytest.mark.xfail(strict=True, reason=(
    "F3-05/G4 aberto: Worker camofox-pqbr não registra intervir_agente. "
    "Limite local de um Worker não garante exclusão global por sessão."
))
def test_contrato_worker_da_sessao_registra_intervencao():
    options = worker_options("worker_camofox.py")
    assert "intervir_agente" in names(options["activities"])
