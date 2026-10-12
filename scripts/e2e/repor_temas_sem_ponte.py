"""Teste t465 sem a ponte Paperclip (José 14:10): Líder Editorial via 9router (mesmo combo e contrato PropostaAgente)."""
import asyncio, json
from pqbr.kit.router9 import chat_papel
from pqbr.contratos import PropostaAgente
from pqbr.workflows.temas import temas_situacao, temas_inserir, ler_proposta, DESCRICAO, ALVO
SIS = open("company/agents/lider-editorial/AGENTS.md").read()[:6000] + "\nResponda só um JSON PropostaAgente."
async def main():
    rec = []
    for r in range(8):
        s = await temas_situacao()
        if not s["faltam"]: break
        t = chat_papel("lider-editorial", SIS, DESCRICAO.format(faltam=s["faltam"], alvo=ALVO, usados="\n".join(f"- {u}" for u in s["usados"][-120:]))
                       + '\nCampos: {"agente":"lider-editorial","tipo":"parametro","alvo":"tema","chave":"grade.reposicao","valor_proposto":"...","justificativa":"...","risco":"baixo"}', 1500)
        try:
            p = PropostaAgente.model_validate(json.loads(t[t.find("{"):t.rfind("}") + 1]))
        except Exception as e:
            print("rodada", r, "inválida", str(e)[:120]); continue
        res = await temas_inserir(ler_proposta(p.valor_proposto)); rec += res["recusas"]
        print("rodada", r, "inseridos", res["inseridos"], "recusas", len(res["recusas"]), flush=True)
    s = await temas_situacao(); print("abertos", s["abertos"], "faltam", s["faltam"], "recusas", [x["motivo"] for x in rec][:10])
asyncio.run(main())
