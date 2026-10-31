# Camofox 24/7 (ADR-008)
- `pqbr-camofox` e `pqbr-camofox-worker`: `Restart=always`, `RestartSec=10`, sem limite (drop-in `restart-always.conf`, t395).
- Guardião de sessão em código (~20 min com variação; extra 30 min antes de publicar): `CamofoxSaudeWorkflow`.
1. Serviço caiu → systemd reinicia sozinho. Observador conta reinícios (`NRestarts`).
2. > 3 reinícios em 24 h → issue `tipo:incidente` ao Dev Corretor (memória, versão, logs).
3. Voltou sem sessão → `camofox-sessao.md`.
