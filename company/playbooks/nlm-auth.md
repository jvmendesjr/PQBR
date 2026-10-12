# Playbook `nlm-auth` — NotebookLM rejeita a sessão ("Authentication expired or invalid")

Dono: Observador detecta (ticket) · execução automática no worker `notebooklm-pqbr` · José só no último degrau.

1. **Automático no worker:** em erro de auth, `_cli` roda `~/.pqbr/camofox/nlm-sync.sh` (checkpoint do Camofox + cópia 600/atômica para `~/.pqbr/notebooklm/profiles/pqbr/storage_state.json`) e repete o comando **uma vez**. O notebooklm-py também chama o mesmo script (`NOTEBOOKLM_REFRESH_CMD`, inclusive no meio da sessão).
2. **Camofox é o único rotacionador:** o worker roda com `NOTEBOOKLM_DISABLE_KEEPALIVE_POKE=1` (o notebooklm-py não rotaciona cookies por conta própria; evita duas cópias da sessão divergindo).
3. **Se repetir:** conferir a sessão no próprio Camofox (aba `notebooklm.google.com` com `userId=pqbr`). Se cair em `accounts.google.com/.../accountchooser`, a **sessão Google foi encerrada** (não é cópia velha): parar a fila do NotebookLM (não repetir pedidos), aviso no Telegram, ticket para o Diretor.
4. **Último degrau (José):** login manual pelo VNC (F4C-04, `infra/pqbr-camofox`). Depois: `nlm-sync.sh` e `pqbr-notebooklm auth check --test`.
5. Registrar a ocorrência (data, passo que resolveu) no ticket; o Dev Corretor transforma em teste/correção se repetir.
