"""Teste de 3 estilos (José 16:09): mesmo roteiro/fontes do EP1002, 3 cadernos de teste, steering novo. Só CLI notebooklm-py."""
import json, re, subprocess, sys, time, random
from pathlib import Path
HOME = Path.home() / ".pqbr/notebooklm"; CLI = str(HOME / "venv/bin/notebooklm")
OUT = Path.home() / ".pqbr/estilos-teste"; OUT.mkdir(parents=True, exist_ok=True)
def cli(*a, t=600):
    env = {"NOTEBOOKLM_HOME": str(HOME), "PATH": "/usr/bin:/bin"}
    for _ in range(2):
        r = subprocess.run([CLI, "-p", "pqbr", "--quiet", *a], capture_output=True, text=True, timeout=t, env=env)
        if r.returncode == 0: return r.stdout
        if "csrf" in (r.stderr + r.stdout).lower(): subprocess.run([str(Path.home() / ".pqbr/camofox/nlm-sync.sh")], capture_output=True); continue
        raise RuntimeError(f"{a[0]} {a[1] if len(a)>1 else ''}: {(r.stderr or r.stdout)[-300:]}")
    raise RuntimeError("csrf persistente")
def js(s): s = s.strip(); return json.loads(s[min(i for i in (s.find("{"), s.find("[")) if i >= 0):])
COMUM = ("Movimento cinematográfico do início ao fim: câmera sempre em movimento (zoom in e zoom out lentos, pan lateral, travelling), "
         "cortes dinâmicos a cada 2 a 3 segundos e variação de planos (close, plano médio, plano geral). "
         "O personagem principal não precisa aparecer em todas as cenas; sempre que aparecer, mantenha-o consistente: mesmo rosto, cabelo, "
         "óculos, roupa e cores. Sem nenhum texto escrito dentro da imagem (sem letreiros, placas, rótulos ou balões). Formato vertical 9:16.")
ESTILOS = {
 "A": "Estilo visual: cartum 2D colorido e vibrante, como série de animação de TV: contornos pretos marcados, cores saturadas e alegres, formas arredondadas, expressões exageradas, cenários luminosos e cheios de detalhe. ",
 "B": "Estilo visual: ilustração editorial vetorial com textura: formas geométricas limpas e simplificadas, paleta harmoniosa de tons saturados sobre fundos escuros ou degradês suaves, granulação sutil de papel, luz suave com brilhos, composição de vídeo explicativo, personagens simples e expressivos. ",
 "C": "Estilo visual: colagem recortada (cutout): fotos e gravuras de época em preto e branco ou sépia recortadas com bordas de papel, combinadas com elementos 2D coloridos desenhados à mão, textura de papel e fita adesiva, camadas sobrepostas que se movem em paralaxe. Sem rosto de pessoa real reconhecível. ",
}
def main():
    rot = json.loads(Path(sys.argv[1]).read_text())
    bv = rot["bloco_visual"]
    fonte = (f"# {rot['titulo']}\n\n## Falas (narrador único)\n" + "\n".join(f"{i+1}. {f}" for i, f in enumerate(rot["falas"])) +
             f"\n\n## Personagem principal (quando aparecer)\n{bv['personagem']}\n\n## Cenas\n" +
             "\n".join(f"S{i+1:02d} — fala: {c['fala']} | ação: {c['acao']} | ambiente: {c['ambiente']}" for i, c in enumerate(bv["cenas"])))
    (OUT / "roteiro-teste.md").write_text(fonte)
    pers = Path.home() / "Workspace/PQBR/templates/notebooklm/persona-pqbr.txt"
    persona = "\n".join(("Estilo: siga o direcionamento visual do pedido de vídeo (teste de estilos 12/10)." if l.startswith("Estilo padrão") else l)
                        for l in pers.read_text().splitlines())
    urls = sys.argv[2:]
    est = {}
    for k, s in ESTILOS.items():
        tit = f"PQBR teste estilo {k} 20261012"
        ex = [n["id"] for n in js(cli("list", "--json")).get("notebooks", []) if n["title"] == tit]
        if ex: nb = ex[0]
        else:
            nb = js(cli("create", tit, "--json")); nb = nb.get("id") or nb["notebook"]["id"]
        tem = {x.get("url") or x.get("title") for x in js(cli("source", "list", "-n", nb, "--json")).get("sources", [])}
        cli("configure", "-n", nb, "--persona", persona)
        time.sleep(random.uniform(2, 5))
        if "roteiro-teste.md" not in tem: cli("source", "add", "-n", nb, "--type", "file", "--title", "roteiro-teste.md", str(OUT / "roteiro-teste.md"), "--json")
        for u in [u for u in urls if u not in tem]: cli("source", "add", "-n", nb, u, "--json"); time.sleep(random.uniform(2, 4))
        cli("source", "wait", "-n", nb, "--timeout", "300", t=360) if False else time.sleep(40)
        steer = s + COMUM
        cli("generate", "video", "-n", nb, "--format", "short", "--language", "pt_BR", "--no-wait", "--json", steer, t=300)
        est[k] = {"caderno": nb, "steering": steer}; print(k, nb, flush=True)
        (OUT / "estado.json").write_text(json.dumps(est, ensure_ascii=False, indent=1))
    t0 = time.time()
    while time.time() - t0 < 3600 and any("arquivo" not in v for v in est.values()):
        time.sleep(60)
        for k, v in est.items():
            if "arquivo" in v: continue
            a = js(cli("artifact", "list", "-n", v["caderno"], "--type", "video", "--json"))["artifacts"]
            if a and a[0]["status"] == "completed":
                raw = OUT / f"{k}_raw.mp4"; cli("download", "video", str(raw), "-n", v["caderno"], "-a", a[0]["id"], t=900)
                o = subprocess.run([str(Path.home() / "Workspace/PQBR/scripts/pos/post-short.sh"), str(raw), str(OUT / f"{k}.mp4"), "2.5"],
                                   capture_output=True, text=True)
                v["arquivo"] = str(OUT / f"{k}.mp4"); v["pos"] = o.stdout.strip().splitlines()[-1:] ; v["min"] = round((time.time() - t0) / 60, 1)
                print(k, "pronto", v["min"], "min", flush=True)
            elif a and "fail" in a[0]["status"]: v["arquivo"] = None; v["erro"] = a[0]["status"]
        (OUT / "estado.json").write_text(json.dumps(est, ensure_ascii=False, indent=1))
if __name__ == "__main__": main()
