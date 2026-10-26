# Onboarding de agente externo (papel `mantenedor`) — t112u/t113u/t114u

Vale para qualquer cliente MCP (Cursor, Claude, opencode, Codex, script próprio). O servidor `pqbr-mcp` externo é **exclusivo do papel `mantenedor`** (t114u): os 8 papéis internos (Diretor, Auditor etc.) rodam dentro do sistema (Temporal/PydanticAI) e não entram por ele.

## O que o mantenedor pode
- **Lê:** todas as tags de conteúdo do Hindsight (bank `pqbr`): decisao, incidente, commit, licao, playbook, doc, editorial, pesquisa, publicacao, auditoria, compliance, seguranca, descarte, estado. Só `obsoleto_candidato` (marcação de descarte) fica fora.
- **Código (GitNexus):** o repo todo (`codigo: [""]`).
- **Grava memória:** decisao, incidente, licao, playbook, doc, estado.
- **Código/docs/mapa:** altera pelo git (branch de trabalho, nunca merge em main sem OK do José), seguindo o protocolo abaixo.
- Política: `config/politica_papeis.json` 1.4.0.

## Passo a passo
1. **Tailnet:** a máquina do agente precisa estar na tailnet do José. Fora dela o servidor não responde.
2. **Endereço:** `https://<host pc na tailnet>:8791/mcp` (HTTPS por `tailscale serve`, Streamable HTTP, POST JSON, sem SSE). O nome MagicDNS do host fica fora do repo; peça ao José. Saúde: `GET /saude`.
3. **Token:** José (ou o agente PQBR) cria com `python scripts/mcp/novo_cliente.py <nome-do-cliente> mantenedor`. O token fica em `~/.pqbr/secrets/mcp_token_<nome>` (600) e só o sha256 vai para `mcp_clientes.json`. Entregue o token ao agente por **variável de ambiente** (ex.: `PQBR_MCP_TOKEN`) ou cofre; nunca no chat, no repo ou em log. O cliente envia `Authorization: Bearer $PQBR_MCP_TOKEN`. Sem token ou token inválido ⇒ 401.
4. **Papel:** `PQBR_KIT_PAPEL=mantenedor`. No MCP HTTP o papel vem do token; se o cliente declarar papel (cabeçalho `X-PQBR-Papel`, espelho do `PQBR_KIT_PAPEL`), ele tem que ser `mantenedor`. Qualquer outro valor, ou token de outro papel ⇒ 403/401.
5. **Cadastro no cliente:** servidor MCP do tipo HTTP com a URL do passo 2 e o header `Authorization` lendo a variável do passo 3.
6. **Primeira mensagem sugerida:** "Conecte ao pqbr-mcp, rode `onboarding`, leia o ESTADO-ATUAL (`estado`), busque na memória (`buscar_memoria`) o contexto da tarefa e continue as pendências na ordem do ESTADO-ATUAL."

## Protocolo obrigatório
`onboarding` → `buscar_memoria` antes de agir → commit local + `docs/DECISOES-LOG.md`/`CHANGELOG.md` (SemVer) → `docs/ESTADO-ATUAL.md` (o pre-commit exige) → `registrar_alteracao` (com o commit) ou `registrar_memoria`.

## Construir e ligar um módulo novo (t113u)
1. **Contrato:** Pydantic v2 versionado em `src/pqbr/contratos/` (herda `Contrato`, campo/constante de versão SemVer); mudança incompatível sobe MAJOR.
2. **Porta/adaptador por config:** porta em `src/pqbr/motores/` ou `integrations/`, adaptador escolhido por `config/*.json` (ex.: `config/motores.json`). Nada de nome de modelo/combo fixo no código (`config/modelos_9router.json`).
3. **Temporal:** activity/workflow em `src/pqbr/workflows/` e registro no `worker_episodio.py` (`workflows=[...]`, `activities=[...]`), fila `episodio-pqbr`, ns `pqbr`.
4. **Agente (se houver):** persona em `company/agents/<papel>/AGENTS.md` + registro em `src/pqbr/agents/`; papel novo ⇒ entrada em `config/politica_papeis.json` (sobe versão).
5. **Testes:** unitários em `tests/unit/` e a suíte inteira verde (`PYTHONPATH=src .venv/bin/python -m pytest -q tests`).
6. **Docs e mapa:** ARQUITETURA, CHANGELOG, DECISOES-LOG, ESTADO-ATUAL e o `.mmd` em `docs/mapa/` (regerar com `scripts/mapa/gerar_index.py`).
7. **Registro:** `registrar_alteracao` com o commit.
8. **Exige OK do José:** ligar o módulo quando isso pedir reiniciar serviço (worker, MCP etc.), aplicar migração, mexer em rede, gastar dinheiro, publicar ou fazer merge em main. Nunca apagar docs (mover para `docs/_obsoleto/`), nunca expor segredos/.env.
