import json, os, subprocess, sys
from pqbr.kit.mcp_kit import PAPEIS, _docs_ler
from pqbr.kit.agente_texto import _json, _slug
from pqbr.contratos import PropostaAgente


def test_docs_bloqueia_arquivo():
    assert _docs_ler("arquivo/ENTREGA-core-eng-PQBR.md").startswith("negado")
    assert _docs_ler("../.env").startswith("negado")


def test_papel_sem_lista_nao_tem_ferramentas():
    # t428: o Roteirista ganhou NotebookLM; papel desconhecido continua sem ferramentas.
    p = subprocess.run([sys.executable, "-m", "pqbr.kit.mcp_kit"], input='{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n',
                       capture_output=True, text=True, env={**os.environ, "PQBR_KIT_PAPEL": "papel-inexistente"})
    assert json.loads(p.stdout)["result"]["tools"] == []
    assert "notebooklm_enfileirar" in PAPEIS["lider-editorial"]


def test_observador_tem_camofox_saude_e_nao_seguranca():
    assert "camofox_saude" in PAPEIS["observador"] and "seguranca_varrer" not in PAPEIS["observador"]


def test_proposta_valida():
    d = _json('x {"agente":"auditor","tipo":"melhoria","alvo":"parametro","chave":"k","valor_proposto":"v","justificativa":"porque sim","risco":"baixo"} y')
    PropostaAgente.model_validate(d)
    assert _slug("Líder Editorial") == "lider-editorial"

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"): f(); print("ok", n)
