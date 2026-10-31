# Índice — GitNexus preservado (migração para codebase-memory-mcp, 2026-10-29)

Nada foi apagado. O GitNexus 1.6.12 foi **preservado, não desinstalado**, até ordem expressa posterior do José (decisão do Passo 2, aprovada em 2026-10-29 com os recomendados do plano em `docs/sdd/PLANO-migracao-codebase-memory-mcp.md`).

## Onde foi parar cada coisa

| Item original | Destino da preservação |
|---|---|
| `~/Workspace/PQBR/.gitnexus/` (índice do repo principal, 215 MB, ignorado pelo git) | `~/.local/share/_obsoleto/gitnexus-pqbr-1.6.12/.gitnexus/` (fora do repo, para não inflar o git) |
| `~/.local/bin/gitnexus` (wrapper: node 22 + `~/.local/opt/node22/bin/gitnexus`) | `~/.local/bin/_obsoleto/gitnexus` |
| `src/pqbr/integrations/gitnexus.py` (adaptador antigo, só `query/context/impact`) | `scripts/_obsoleto/gitnexus.py` (neste repo) |
| `scripts/gitnexus/verificar.sh` e `scripts/gitnexus/hook-post-commit.sh` | `scripts/_obsoleto/gitnexus/verificar.sh` e `scripts/_obsoleto/gitnexus/hook-post-commit.sh` (neste repo) |
| `.githooks/post-commit` antigo (chamava o hook do GitNexus) | Substituído pelo hook do CBM; a versão antiga está no histórico do git e o script antigo está em `scripts/_obsoleto/gitnexus/hook-post-commit.sh` |

## O que NÃO foi tocado (e por quê)

- **Pacote npm do GitNexus** (`~/.local/opt/node22/lib/node_modules/gitnexus` + `~/.local/opt/node22/bin/gitnexus`): intacto. Mover o wrapper não desinstala nada; o rollback só precisa restaurar o wrapper.
- **Registry global** (`~/.gitnexus/registry.json`): intacto, com as 2 entradas (repo principal PQBR e a cópia em `~/.pqbr/proposta-ferramentas-agentes/`, que está fora do escopo desta migração e não foi tocada).
- **Node 22** (`~/.local/opt/node22`, v22.23.4) e **node v20 do sistema**: intactos.
- **Licença**: GitNexus 1.6.12 usa PolyForm Noncommercial — motivo da migração. O substituto é o codebase-memory-mcp 0.12.1, licença MIT (cópia do `LICENSE` e do `THIRD_PARTY_NOTICES.md` da release fixada guardadas em `~/cbm-install-v0.12.1/`, fora do repo; o hash SHA-256 do tarball conferido foi `8453015145f072c1b9b019cbdd02cea8cc6f18cc5e116036dd20992631c638c7`).

## Substituto (para referência rápida)

- Binário: `~/.local/opt/codebase-memory-mcp/codebase-memory-mcp` (0.12.1, instalado com `--skip-config`, sem setup de clientes, Lens desligada com `ui_enabled=false`, sem porta).
- Índice: `~/.cache/codebase-memory-mcp/` (projeto `PQBR`, 83.108 nós, 105.840 arestas, status ready em 2026-10-29).
- Adaptador novo: `src/pqbr/integrations/codebase_memory.py`; política 1.6.0 (`codigo_consultar`); vigia com entrada `codebase-memory-mcp` + leitor de versão de binário; verificação em `scripts/codebase-memory/verificar.sh`; post-commit em `scripts/codebase-memory/hook-post-commit.sh`.

## Rollback (resumo; o procedimento completo está no §7 do plano)

1. Restaurar o wrapper: `mv ~/.local/bin/_obsoleto/gitnexus ~/.local/bin/gitnexus`.
2. Restaurar o índice: `mv ~/.local/share/_obsoleto/gitnexus-pqbr-1.6.12/.gitnexus ~/Workspace/PQBR/.gitnexus`.
3. Restaurar no git o adaptador, os scripts e o post-commit antigos (estão no histórico e em `scripts/_obsoleto/`), e a política 1.5.0 (`gitnexus_consultar`).
4. Conferir `scripts/_obsoleto/gitnexus/verificar.sh` verde (binário, versão ≥ 1.6.12, índice registrado).
5. Reiniciar **só** a unit `pqbr-mcp` (nunca o gateway do Hermes) e rodar os probes no lado GitNexus.
6. Manter o índice CBM até o José decidir; registrar o rollback em DECISOES-LOG + CHANGELOG e avisar pelo mesmo canal.
