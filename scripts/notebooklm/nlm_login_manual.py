"""Contorno do falso "Already logged in" do notebooklm-py 0.8.4 (deslogado cai em notebook.google.com/trynow,
mesmo host). Abre o Chromium do Playwright com o perfil persistente do próprio notebooklm-py, na página de login
do Google; espera o José entrar (cookie SID + __Secure-1PSIDTS) e fecha. Depois `notebooklm -p pqbr login`
(sem --fresh) captura a sessão real desse perfil. Uso: DISPLAY=:1 python nlm_login_manual.py"""
import time, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
PERFIL = Path.home() / ".pqbr/notebooklm/profiles/pqbr/browser_profile"
URL = "https://accounts.google.com/ServiceLogin?continue=https://notebook.google.com/"
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(str(PERFIL), headless=False, viewport={"width": 1200, "height": 680})
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    pg.goto(URL)
    fim = time.time() + 3600
    while time.time() < fim:
        nomes = {c["name"] for c in ctx.cookies("https://notebook.google.com")}
        if {"SID", "__Secure-1PSIDTS"} <= nomes and "notebook.google.com" in pg.url and "trynow" not in pg.url:
            print("login ok", flush=True); time.sleep(5); break
        time.sleep(3)
    else:
        print("timeout", flush=True); sys.exit(1)
    ctx.close()
