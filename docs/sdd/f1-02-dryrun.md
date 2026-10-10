# F1-02 — dry-run do import da org PQBR (10/10/2026, t376)

Comando: `paperclipai company import ./company --target new --new-company-name PQBR --include company,agents --dry-run --json`

- Plano: `companyAction: create`; 6 agentes `create` (dev-manutencao, pqbr-assistente, prod-analista, prod-compliance, prod-comunidade, prod-director).
- `warnings: []`, `errors: []`, `envInputs: []` (nenhum segredo pedido).
- Manifesto de cada agente: `adapterType: process` (stub), `heartbeat.enabled: false`, `budgetMonthlyCents: 0`, sem criar agentes nem skills; só director e assistente atribuem tarefas.
- Nenhuma empresa criada (4 antes, 4 depois).
- **Atenção:** o pacote não carrega o status `paused`; depois do import real, pausar todos (`company/README.md`).
- **Pendente — portão do José:** autorizar a criação real; liberar qualquer agente é decisão separada. Depois: reapontar o `pqbr` (ARQUITETURA §10) e revogar a chave da PQBR-TESTE.
