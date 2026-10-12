# Playbook `nlm-auth` — NotebookLM rejeita a sessão ("Authentication expired or invalid")

Decisão (t-nlm2, José): o NotebookLM usa a **reautenticação nativa do notebooklm-py**, com **sessão própria**
(perfil de navegador `~/.pqbr/notebooklm/profiles/pqbr/browser_profile` + `storage_state.json`). **Não** se copia
mais a sessão do Camofox para o NotebookLM (o keepalive só faz checkpoint e `chmod 600` do Camofox).

1. **Automático (notebooklm-py, nativo):** L1 renova token/CSRF; L2 rotaciona `__Secure-1PSIDTS` (RotateCookies,
   poke **ligado**); L3 re-login headless pelo perfil de navegador próprio (`NOTEBOOKLM_HEADLESS_REAUTH=1` no
   `pqbr-notebooklm-worker`).
2. **Automático (worker):** em erro de auth, `_cli` roda `notebooklm -p pqbr auth refresh` (mesma escada L1–L3) e
   repete o comando **uma vez**.
3. **Se continuar:** `auth check --test` mostra só NID/__Host-GAPS (sem SID/__Secure-1PSIDTS) = a sessão Google
   do perfil próprio acabou. Parar a fila do NotebookLM (não repetir pedidos), Telegram, ticket para o Diretor.
4. **Último degrau (José):** abrir o VNC do `pc` (x11vnc no display do Camofox, 5987/5988 só no IP da tailnet,
   com senha) e rodar, no mesmo display, `DISPLAY=:1 NOTEBOOKLM_HOME=~/.pqbr/notebooklm ~/.pqbr/notebooklm/venv/bin/notebooklm -p pqbr login --browser-timeout 3600`;
   o José entra na janela Chromium que abre. Depois `auth check --test` precisa mostrar SID e `__Secure-1PSIDTS`.
   Atenção: se o comando terminar sozinho em segundos com "Authentication saved" sem o José ter entrado, o
   arquivo saiu incompleto — rodar de novo (ou com `--fresh`).
5. Registrar a ocorrência no ticket; o Dev Corretor transforma em teste/correção se repetir.

Risco anotado: duas sessões da mesma conta (Camofox + NotebookLM) = dois dispositivos na conta; é o desenho
oficial do notebooklm-py e evita duas ferramentas rotacionando a **mesma** sessão (causa provável da queda de 12/10).
