# company — pacote Paperclip da PQBR (agentcompanies/v1, F1-01)

- `COMPANY.md`: empresa PQBR (schema `agentcompanies/v1`).
- `agents/<slug>/AGENTS.md`: prod-director, prod-analista, prod-comunidade, prod-compliance, pqbr-assistente, dev-manutencao.
- `.paperclip.yaml`: adaptador `process` (stub `scripts/paperclip/agente_pausado.sh`, sem `hermes_local`/`--yolo`), heartbeat desligado, orçamento 0, sem segredos.

Dry-run (não cria nada):

    paperclipai company import ./company --target new --new-company-name PQBR --include company,agents --dry-run --json

Criação (portão do José, F1-02) — depois de aplicar, **pausar** cada agente, porque o pacote não carrega status:

    paperclipai company import ./company --target new --new-company-name PQBR --include company,agents --yes
    for a in $(paperclipai agent list -C <novo-id> --json | jq -r '.[].id'); do paperclipai agent pause "$a"; done
