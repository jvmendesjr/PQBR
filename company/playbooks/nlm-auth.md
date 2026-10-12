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

**Contorno do login (12/10, notebooklm-py 0.8.4, última versão no PyPI):** deslogado, `notebook.google.com` (e o legado `notebooklm.google.com`) cai em `notebook.google.com/trynow`, mesmo host → o `login` acusa "Already logged in" e salva só NID/__Host-GAPS. `NOTEBOOKLM_BASE_URL` não resolve. Usar `scripts/notebooklm/login_jose.sh`: abre o Chromium do perfil persistente do notebooklm-py na página de login do Google (DISPLAY=:1, visível no VNC), espera SID + `__Secure-1PSIDTS`, fecha e roda `notebooklm -p pqbr login` (sem `--fresh`) + `auth check --test`. Log em `~/.pqbr/notebooklm/logs-login.txt`.

**Atualização 12/10 (José):** supera L1–L3 nativos. NotebookLM só LÊ a sessão do Camofox via `NOTEBOOKLM_REFRESH_CMD=~/.pqbr/camofox/nlm-sync.sh` (`DISABLE_KEEPALIVE_POKE=1`, `HEADLESS_REAUTH=0`, sem perfil Chromium, sem `auth refresh`). Falha de auth → rodar `nlm-sync.sh`; se a sessão do Camofox caiu → playbook camofox-sessao (login no Camofox pelo VNC, com ritmo humano).
