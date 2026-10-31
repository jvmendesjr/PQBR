"""E2E dry-run nº1 (t463/t464): tema da grade → EpisodioWorkflow com roteirizar=True (NotebookLM-first), sem upload."""
import asyncio, json, sys
from pqbr.workflows.pacote import _banco
async def main():
    from pqbr.workflows.worker import client
    from pqbr.workflows.episodio import EpisodioWorkflow, PedidoEpisodioE2E, FILA_EPISODIO
    tid = int(sys.argv[1])
    with _banco() as c:
        tid, slug, tema, cat = c.execute("select id, slug, tema, categoria from pqbr.temas_pendentes where id=%s", (tid,)).fetchone()
        n = c.execute("select coalesce(max(substring(episodio_codigo from 8)::int),1000)+1 from pqbr.cadernos_episodio where episodio_codigo ~ '^PQBR-EP[0-9]+$'").fetchone()[0]
        c.execute("update pqbr.temas_pendentes set status='em_producao', fontes=%s where id=%s", (json.dumps(["(NotebookLM add-research)", "(NotebookLM add-research)"]), tid)); c.commit()
    codigo = sys.argv[2] if len(sys.argv) > 2 else f"PQBR-EP{n:04d}"
    briefing = (f"# Briefing do episódio {codigo}\n\nTema: {tema}\nCategoria: {cat}\n\nPúblico: brasileiros curiosos, Shorts de ~50 s. "
                "Explicar a origem/explicação mais aceita, citar ao menos 2 fontes do caderno e trazer o 'mas tem quem diga' quando houver versões.")
    p = PedidoEpisodioE2E(slug=slug[:60], codigo=codigo, roteiro_texto=briefing, n_cenas=8, dry_run=True, roteirizar=True, tema=tema,
                          tema_id=tid, espera_veredito_h=6)
    h = await (await client()).start_workflow(EpisodioWorkflow.run, p, id=f"e2e-{codigo}", task_queue=FILA_EPISODIO)
    print("iniciado", h.id, codigo, slug, tema)
asyncio.run(main())
