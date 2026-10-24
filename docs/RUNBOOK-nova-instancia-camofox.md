# RUNBOOK — nova instância Camofox isolada (ADR-012) e migração do PQBR

Status 24/10/2026 (t526): **preparado, nada instalado nem rodando.** O PQBR segue na instalação individual `pqbr-camofox.service` (127.0.0.1:9387). Gatilho da migração: **próxima integração de projeto**. Requer OK explícito do José para cada passo que inicia serviço.

## 0. Peças no repo
| Arquivo | Papel |
|---|---|
| `deploy/camofox/camofox@.service` | template systemd (user): env em `~/.camofox-instancias/%i.env`, app único `~/camofox-browser`, bind 127.0.0.1, MemoryMax 2200M |
| `deploy/camofox/instancia.env.exemplo` | só nomes de chaves + placeholders |
| `deploy/camofox/criar_instancia.sh` | prepara diretórios e `.env` (chaves geradas, chmod 600, nunca exibidas); `--instalar` copia o unit mas deixa **disabled e parado** |
| `config/camofox_instancias.json` | registro: `pqbr` 9387 *individual*; `proxima` 9397 *reservada* |
| `src/pqbr/motores/navegador.py` + contratos `InstanciaNavegador`/`SaudeNavegador` 1.0.0 | porta `NavegadorIdentidade` (não ligada em `acesso.py`) |

Reserva = nome + porta + diretórios definidos; nenhum processo, nenhuma memória.

## 1. Pré-checagem
1. `ss -ltn | grep :<porta>` vazio; RAM disponível ≥ 1,5 GB (`free -m`).
2. Camofox global saudável (`curl -s 127.0.0.1:9377/health`) e versão igual a `instalacao` no JSON.
3. Máximo 3 instâncias ativas (`limite_simultaneas`).

## 2. Criar instância nova (conta nova, ex.: próximo projeto)
1. Renomear `proxima` no JSON para o nome real da conta (mantém 9397); commit.
2. `sh deploy/camofox/criar_instancia.sh <conta> 9397` → confere `~/.camofox-instancias/<conta>.env` (só `stat`, não `cat`).
3. Com OK do José: `sh deploy/camofox/criar_instancia.sh <conta> 9397 --instalar`. O script é idempotente (t528): `.env` completo é mantido, placeholders/chaves faltantes são completados sem exibir valores, e o template é copiado + `daemon-reload`; unit fica disabled e parada. Pode ser repetido. Teste sem tocar o sistema: `CAMOFOX_INSTANCIAS_DIR=/tmp/x SYSTEMD_DIR=/tmp/y SKIP_PORT_CHECK=1` (ver `tests/unit/test_criar_instancia.py`).
4. Com OK: `systemctl --user start camofox@<conta>`; `curl -s 127.0.0.1:9397/health`; teste de aba (POST/GET snapshot/DELETE em example.com).
5. Login Google da conta **só** nessa instância (regra: nada de login em outros navegadores). Depois `enable`.
6. JSON: `estado` → `ativa`; teste `tests/unit/test_navegador.py`; mapa 08 + DECISOES-LOG.

## 3. Migrar o PQBR (9387 → `camofox@pqbr`)
1. Backup frio: `systemctl --user stop pqbr-camofox-keepalive pqbr-camofox` → `tar` de `~/.pqbr/camofox/{profiles,cookies}` em `~/backups/`.
2. Criar `~/.camofox-instancias/pqbr.env` com **porta 9387**, chaves atuais (copiar via arquivo, sem echo) e `CAMOFOX_PROFILE_DIR`/`COOKIES_DIR` apontando para o **mesmo perfil** atual (sem mover).
3. `systemctl --user disable pqbr-camofox` (não desinstalar); instalar drop-ins equivalentes (`memory.conf`, restart) no diretório de drop-ins da unit `camofox@pqbr`.
4. `start camofox@pqbr` → health → NotebookLM abre logado (juniormoedavirtual) → `nlm-sync.sh` OK → keepalive apontando para a nova unit.
5. Ligar `NavegadorIdentidade` em `acesso.py`/`camofox.py` (PR próprio, testes).
6. Instalação antiga parada 7 dias; depois `git mv` de docs antigas e remoção de `~/.pqbr/camofox/app` + cache (1,3 GB) com OK.

## 4. Rollback (≤ 5 min)
`systemctl --user stop camofox@pqbr; systemctl --user enable --now pqbr-camofox pqbr-camofox-keepalive` — perfil é o mesmo, porta a mesma; se o perfil corromper, restaurar o tar do passo 3.1.

## 5. Riscos
- Mudança de versão Camoufox (v1.15→v1.18.1) pode invalidar a sessão Google → janela de re-login com o José; rollback acima.
- Dois processos no mesmo perfil corrompem → nunca rodar `pqbr-camofox` e `camofox@pqbr` juntos.
- Global ainda escuta em todas as interfaces (⚠, mudança de rede exige OK do José); instâncias novas sempre 127.0.0.1.
- Atualizar a instalação única afeta todas as contas → canário diário + travar versão no JSON.
- RAM: ~1 GB por instância ativa; reservada consome 0.
