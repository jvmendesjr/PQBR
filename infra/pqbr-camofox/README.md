# Camofox isolado da PQBR (F4C-01..03, t375)
- Código: `/home/pc/.pqbr/camofox/app` (clone de `~/camofox-browser`, fixado no commit 2c0036a, `npm ci --omit=dev`).
- Navegador: cópia própria do Camoufox em `/home/pc/.pqbr/camofox/cache/camoufox` (`CAMOUFOX_EXECUTABLE_PATH`).
- Config: `/home/pc/.pqbr/camofox/.env` (600; nunca no git): porta 9387 só em 127.0.0.1, `NODE_ENV=production`, `CAMOFOX_API_KEY`/`ACCESS_KEY`/`ADMIN_KEY` gerados no servidor, pastas próprias (profiles, cookies, uploads, traces), `MAX_SESSIONS=1`, VNC desligado, sem relatório de falhas.
- Serviços de usuário: `pqbr-camofox.service` (MemoryMax 900M) e `pqbr-camofox-worker.service` (fila Temporal `camofox-pqbr`, concorrência 1).
- Teste: `sh scripts/camofox/verificar.sh`.
- Rollback: `systemctl --user disable --now pqbr-camofox-worker pqbr-camofox && rm ~/.config/systemd/user/pqbr-camofox*.service && systemctl --user daemon-reload && rm -rf /home/pc/.pqbr/camofox`. O Camofox compartilhado (9377) não depende disso.
