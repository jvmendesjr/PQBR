# company — pacote Paperclip da PQBR (agentcompanies/v1, v4.3 / t396)

15 agentes: os 14 de `docs/AGENTES.md` + `pqbr-assistente` (identidade do canal Hermes `pqbr`).
- `agents/<slug>/AGENTS.md`: instruções (versionadas no git; o bundle do Paperclip não tem histórico).
- `skills/`: `pqbr-contrato` (comum) + skills das trilhas.
- `projects/`: trilhas (labels `lane:<slug>`). `tasks/`: rotinas (`recurring`), com cron em `.paperclip.yaml` (America/Fortaleza).
- `.paperclip.yaml`: adapters `process` (texto; stub até o script do kit) e `opencode_local` (`/home/pc/.opencode/bin/opencode`, modelo `9router/...`, `dangerouslySkipPermissions: false`).
- `opencode-config/`: XDG_CONFIG_HOME só da PQBR (provider 9router, permissões negadas). A chave vem por `NINEROUTER_API_KEY` (secret_ref, criado pelo José). Não toca no config do José.
- Orçamento: 2000 c/mês por agente, **warn-only** (`hardStopEnabled: false`, 80%).
- Todos nascem pausados até o MCP `pqbr-kit` e os scripts do kit existirem.
