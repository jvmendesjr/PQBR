"""E2E dry-run nº1 (t463), parte 1: tema → roteiro → compliance/guardião → SEO → inicia EpisodioWorkflow (dry_run)."""
import json, re, sys, time, asyncio
from datetime import date
from pqbr.kit.router9 import chat
from pqbr.pipeline.grade import checar_repeticao, bloqueio_absoluto, normalizar
from pqbr.contratos import RoteiroShort, PacoteSEO, TemaPendente, ESTILO_PADRAO_2D, CTA
from pqbr.seguranca.barreira import exigir_limpo
from pqbr.workflows.pacote import _banco
T = {}; LOG = {}
def marca(k, t0, **kw): LOG[k] = {"s": round(time.time() - t0, 1), **kw}; print(k, LOG[k], flush=True)
def js(t):
    t = re.sub(r"^```(json)?|```$", "", t.strip(), flags=re.M).strip(); return json.loads(t[t.find("{"):t.rfind("}") + 1])
def gerar(modelo, sis, usr, valida, tent=3, mt=3500):
    erro = ""
    for i in range(tent):
        r = chat(modelo, sis, usr + (f"\n\nA tentativa anterior falhou na validação: {erro}. Corrija." if erro else ""), max_tokens=mt)
        try: return valida(js(r)), i + 1
        except Exception as e: erro = str(e)[:500]
    raise RuntimeError("falhou validação: " + erro)
# 1 tema
t0 = time.time()
with _banco() as c:
    usados = [r[0] for r in c.execute("select tema from pqbr.temas union all select tema from pqbr.temas_pendentes").fetchall()]
cands, _ = gerar("core-medio", "Você é o Pesquisador de Origem do canal Porquê BR (Shorts de curiosidades). Responda só JSON.",
    "Proponha 8 temas de curiosidade/cultura popular brasileira (≥80% origem de expressões populares ou curiosidades inúteis que prendem a atenção), "
    "no formato pergunta 'Por que ...?' curta. Evite política, religião, tragédia, marcas e pessoas reais. "
    'JSON: {"temas":[{"tema":"...","categoria":"expressao|habito_mania|curiosidade_cultura_pop"}]}', lambda d: d["temas"])
escolhido = None
for c_ in cands:
    if bloqueio_absoluto(c_["tema"]): continue
    if checar_repeticao(c_["tema"], usados).repetido: continue
    escolhido = c_; break
assert escolhido, "nenhum tema livre"
marca("tema", t0, tema=escolhido["tema"], categoria=escolhido["categoria"])
# 2 roteiro
t0 = time.time()
slug = re.sub(r"[^a-z0-9]+", "-", normalizar(escolhido["tema"]).replace("por que ", ""))[:50].strip("-")
ag = open("company/agents/roteirista/AGENTS.md").read()
contrato = open("docs/CONTRATO-EDITORIAL.md").read()
i16 = contrato.find("## 16"); sec16 = contrato[i16:i16 + 9000] if i16 >= 0 else ""
def val_rot(d):
    d["bloco_visual"]["estilo"] = ESTILO_PADRAO_2D
    r = RoteiroShort.model_validate({k: d[k] for k in ("episodio_id", "titulo", "falas", "entidades_cena", "bloco_visual")})
    if len(r.bloco_visual.cenas) != len(r.falas) - 0 and len(r.bloco_visual.cenas) < 6: raise ValueError("poucas cenas")
    if len(d.get("fontes", [])) < 2: raise ValueError("≥ 2 fontes (URLs) obrigatórias")
    if not 35 <= r.duracao_estimada_s <= 70: raise ValueError(f"duração {r.duracao_estimada_s}s; alvo ~50 s")
    return r, d["fontes"]
(rot, fontes), tent = gerar("core-alto", ag + "\n\nResponda só JSON.",
    f"Tema: {escolhido['tema']}\nepisodio_id: {slug}\n\nRegras do contrato (§16):\n{sec16}\n\n"
    f"Escreva o RoteiroShort: narrador único, gancho até 3 s com a imagem literal, versão mais aceita + 'mas tem quem diga', "
    f"~50 s (115 palavras), última fala exatamente \"{CTA}\". bloco_visual: personagem (frase-ficha detalhada, sem nome, 1 personagem), "
    f"cenas (uma por fala, cena 1 literal, última retoma a 1ª; cada cena com fala, acao, enquadramento, ambiente). Inclua 'fontes': ≥ 2 URLs reais confiáveis. "
    'JSON: {"episodio_id","titulo","falas":[...],"entidades_cena":[...],"bloco_visual":{"personagem","cenas":[{"fala","acao","enquadramento","ambiente"}]},"fontes":[...]}',
    val_rot, mt=6000)
marca("roteirista", t0, tentativas=tent, falas=len(rot.falas), duracao_s=rot.duracao_estimada_s, fontes=fontes)
# 3 compliance + guardião
t0 = time.time()
comp = json.loads(open("company/agents/lider-compliance/AGENTS.md").read()[:0] or "{}")
txt = json.dumps(rot.model_dump(), ensure_ascii=False)
ver, _ = gerar("core-revisao", "Você é o Líder de Compliance do Porquê BR. Confira o roteiro contra o contrato editorial (segurança: pessoa real, marca real, "
    "estereótipo ofensivo, política/religião/tragédia, afirmação falsa sem 'mas tem quem diga', pedido de comentário). Responda só JSON.",
    f"Contrato §16:\n{sec16[:5000]}\n\nRoteiro:\n{txt}\nFontes: {fontes}\n" + 'JSON: {"aprovado":true|false,"motivos":[...],"ressalvas":[...]}',
    lambda d: d if isinstance(d.get("aprovado"), bool) else (_ for _ in ()).throw(ValueError("aprovado")))
exigir_limpo(rot.model_dump(), "roteiro")   # Guardião: sem segredo/injeção no texto que vai ao NotebookLM
marca("compliance_guardiao", t0, aprovado=ver["aprovado"], motivos=ver.get("motivos"), ressalvas=ver.get("ressalvas"))
if not ver["aprovado"]: sys.exit("compliance reprovou")
# 4 SEO
t0 = time.time()
seo, _ = gerar("core-medio", "Você é o Especialista de SEO do Porquê BR (YouTube Shorts, pt-BR). Responda só JSON.",
    f"Roteiro: {txt}\nGere titulo (≤ 70 car., pergunta curiosa), descricao (2–3 frases + fontes {fontes} + hashtags), tags (≤ 12), hashtags (3–5, incluir #shorts). "
    'JSON: {"titulo","descricao","tags":[...],"hashtags":[...]}', lambda d: PacoteSEO.model_validate(d))
marca("seo", t0, titulo=seo.titulo, categoria=seo.categoria_id, sintetica=seo.contem_midia_sintetica)
# registro do tema + código
with _banco() as c:
    n = c.execute("select coalesce(max(substring(episodio_codigo from 8)::int),0)+1 from pqbr.cadernos_episodio where episodio_codigo ~ '^PQBR-EP[0-9]+$'").fetchone()[0]
    codigo = f"PQBR-EP{max(n, 1001):04d}"
    tp = TemaPendente(slug=slug, tema=escolhido["tema"], tema_normalizado=normalizar(escolhido["tema"]), categoria=escolhido["categoria"],
                      status="em_producao", fontes=fontes, bloco_visual=rot.bloco_visual, data_prevista=date.today(),
                      metadados={"codigo": codigo, "e2e": "t463-dryrun"}, criado_por="e2e-t463")
    c.execute("insert into pqbr.temas_pendentes (canal_id, slug, tema, tema_normalizado, categoria, status, fontes, bloco_visual, metadados, data_prevista, criado_por) "
              "values ('pqbr',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (tp.slug, tp.tema, tp.tema_normalizado, tp.categoria, tp.status, json.dumps(fontes),
              json.dumps(rot.bloco_visual.model_dump(), ensure_ascii=False), json.dumps(tp.metadados), tp.data_prevista, tp.criado_por)); c.commit()
bv = rot.bloco_visual
roteiro_texto = (f"# {rot.titulo}\n\n## Falas (narrador único)\n" + "\n".join(f"{i+1}. {f}" for i, f in enumerate(rot.falas)) +
    f"\n\n## Bloco visual\n[ESTILO] {bv.estilo}\n[PERSONAGEM] {bv.personagem}\n[CENAS]\n" +
    "\n".join(f"S{i+1:02d} — fala: {c.fala} | ação: {c.acao} | enquadramento: {c.enquadramento} | ambiente: {c.ambiente}" for i, c in enumerate(bv.cenas)) +
    "\n\n## Fontes\n" + "\n".join(fontes))
steering = f"[ESTILO] {bv.estilo} [PERSONAGEM] {bv.personagem}"
json.dump({"codigo": codigo, "slug": slug, "tema": escolhido, "roteiro": rot.model_dump(), "fontes": fontes, "compliance": ver,
           "seo": seo.model_dump(), "roteiro_texto": roteiro_texto, "steering": steering, "log": LOG},
          open(f"/home/pc/.pqbr/e2e-{codigo}.json", "w"), ensure_ascii=False, indent=1)
# 5 inicia workflow
async def iniciar():
    from pqbr.workflows.worker import client
    from pqbr.workflows.episodio import EpisodioWorkflow, PedidoEpisodioE2E, FILA_EPISODIO
    cl = await client()
    p = PedidoEpisodioE2E(slug=slug, codigo=codigo, roteiro_texto=roteiro_texto, n_cenas=len(bv.cenas), titulo=seo.titulo,
                          descricao=seo.descricao, tags=seo.tags[:15], dry_run=True, steering=steering[:4000], espera_veredito_h=6)
    h = await cl.start_workflow(EpisodioWorkflow.run, p, id=f"e2e-{codigo}", task_queue=FILA_EPISODIO)
    print("workflow", h.id, flush=True)
asyncio.run(iniciar())
