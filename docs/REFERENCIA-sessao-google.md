# REFERÊNCIA — Sessão Google persistente em automação (Camofox/Camoufox + notebooklm-py)

> **Documento vivo.** Atualizar a cada mudança no login, na renovação ou nos consumidores da sessão Google; registrar no changelog abaixo e no DECISOES-LOG. Reutilizável em outros projetos (trocar só caminhos, userId e domínios).

## Changelog
| Data | Mudança | Commit |
|---|---|---|
| 12/10/2026 | Criação. Camofox = única fonte e único renovador; notebooklm-py só lê via `NOTEBOOKLM_REFRESH_CMD`; Chromium e cópia do Chrome aposentados. | `0206a36` |
| 12/10/2026 | Regra de comportamento humano (helpers `camofox_humano`, keepalive com jitter). | `c8a3335` |
| 12/10/2026 | Rebrand Gemini Notebook (`notebook.google.com`): `CSRF token not found` = cópia velha da sessão → `nlm-sync.sh` resolve (o `_cli` faz sozinho). | `d88de95` |
| 12/10/2026 13:27 | **Logout da sessão global (aprovado pelo José):** crons `keepalive-session-guardian.py` (yt-llm-bot; importava cookies no userId `porquebr` do Camofox global :9377 a cada 15 min) e `notebooklm auth refresh` (~/.notebooklm) **comentados** (backup `~/Backups/crontab-20261012-1327.bak`). Movidos para `~/Backups` (600/700): storage do `porquebr` da 9377, `~/.notebooklm/profiles/default/storage_state.json`, `~/.mp32/notebooklm/profiles/juniormoedavirtual/storage_state.json` e perfil Chrome `PorqueBR`. Nenhum logout no Google; PQBR (9387) intacta. | (este commit) |

## 0. Consumidores proibidos (12/10)
A conta juniormoedavirtual só existe na PQBR (Camofox 9387 `userId=pqbr` + notebooklm-py PQBR). Desligados/arquivados: Camofox global :9377 `porquebr`, `~/.notebooklm` global, MP32 `juniormoedavirtual`, Chrome do servidor perfil `PorqueBR`, cron `keepalive-session-guardian.py`. Reativar exige OK do José. Skills do `rede` que usavam `porquebr` na 9377 ficam sem sessão **de propósito** (José 13:29): nenhuma ligação PQBR↔rede (sem fila, sem acesso à 9387, sem adaptador).

## 1. Problema
- Conta Google de produção (`juniormoedavirtual`) usada por **YouTube Studio, NotebookLM e Gemini Web**.
- Antes havia **duas identidades de navegador** para a mesma conta: Camofox (Camoufox/Firefox) e o Chromium "Chrome for Testing" do notebooklm-py, além de cookies copiados do Chrome local do servidor.
- Em 12/10 o Google encerrou a sessão (até dentro do Camofox); a fila do NotebookLM passou a rejeitar pedidos por auth expirada.

## 2. Por que acontece (justificativa)
1. **Dois renovadores da mesma sessão.** O Google rotaciona `__Secure-1PSIDTS`/`SIDCC`. Se dois clientes renovam em paralelo, a cópia de um fica velha; uso concorrente de cookies rotacionados de fingerprints diferentes parece sequestro de sessão e o Google revoga.
2. **DBSC (Device Bound Session Credentials).** O Google prende a sessão ao aparelho (chave em TPM) no Chrome 146+; GA para contas pessoais e Workspace desde mai/2026 (Windows; macOS a seguir). "Alterações manuais em cookies podem impedir o DBSC" e forçam novo login → cookie copiado do Chrome é caminho frágil daqui para frente. No servidor Linux provavelmente ainda não se aplica, mas é a direção.
3. **Login no Chrome for Testing é ruim.** Navegador de automação tende a ser recusado/desafiado; observado em 12/10: deslogado, `notebook.google.com` cai em `/trynow` e o `notebooklm login` acusa falso "Already logged in" (salva só NID/`__Host-GAPS`). Camoufox existe justamente para logar via Firefox anti-detect.
4. **Fingerprints diferentes** (Firefox anti-detect × Chromium) na mesma conta aumentam desafios de verificação.

## 3. Desenho adotado (testado)
**Uma identidade, um renovador, consumidores só leem.**
- **Fonte única:** `pqbr-camofox` (127.0.0.1:9387), `userId=pqbr`, `MAX_SESSIONS=1`, plugin `persistence` com `indexedDB: true`, perfil `~/.pqbr/camofox/profiles/66e057673effe4afdd963a2bd6a45a2a/storage-state.json` (SHA-256 do userId). Login só aqui (VNC), com ritmo humano.
- **Renovador único:** `~/.pqbr/camofox/keepalive.sh` (unit `pqbr-camofox-keepalive`): aba do Studio tocada ~1/min (jitter 50–75 s), checkpoint a cada 5 ciclos, e a cada 15 ciclos abre `notebooklm.google.com` numa aba própria, espera 18–45 s, salva (import vazio de cookies = checkpoint) e fecha. Log: `~/.pqbr/logs/camofox-keepalive.log`.
- **Consumidor NotebookLM (só leitura):** worker `pqbr-notebooklm-worker` com drop-in `10-sessao-camofox.conf`:
  `NOTEBOOKLM_REFRESH_CMD=/home/pc/.pqbr/camofox/nlm-sync.sh`, `NOTEBOOKLM_REFRESH_CMD_MIDSESSION=1`, `NOTEBOOKLM_DISABLE_KEEPALIVE_POKE=1`, `NOTEBOOKLM_HEADLESS_REAUTH=0`. O worker, em erro de auth, roda o mesmo script e repete.
- **`nlm-sync.sh`:** pede checkpoint ao Camofox, lê o storage-state persistido, mantém só domínios `google.com`, `google.com.br`, `googleusercontent.com`, exige `SID` + `__Secure-1PSIDTS`, grava atômico com 600 em `NOTEBOOKLM_REFRESH_STORAGE_PATH`. Nunca imprime valores. (O `GET /sessions/:userId/storage_state` do camofox 1.6.0 só existe com o plugin VNC ligado; por isso lê o arquivo.)
- **Aposentados (não apagados):** perfil Chromium `~/.pqbr/notebooklm/profiles/pqbr/browser_profile.aposentado-20261012`; `scripts/aposentado/sync_cookies_chrome.py`, `scripts/aposentado/login_jose.sh`; `keepalive.sh.bak-20261012`.

## 4. Evidência dos testes (12/10, PT)
- `nlm-sync.sh` → 43 cookies Google, arquivo 600; `notebooklm -p pqbr auth check --test` → **Authentication is valid**.
- 1 chat pela fila `notebooklm-pqbr` (caderno `Short - t430-estilo-2d`) → `ok=True`, uso 5 chats/dia, janelas 0% / 1,4%.
- Recheque ~25 min depois (11:16): keepalive registrou renovação + checkpoint às 11:14:52; `camofox_saude` → ok, autenticado; `auth check --test` válido antes e depois de novo sync.

## 5. Recuperação (escada)
1. Erro de auth no NotebookLM → `~/.pqbr/camofox/nlm-sync.sh` e `auth check --test` (o worker já faz isso sozinho).
2. Falhou com "sem SID/__Secure-1PSIDTS" ou `camofox_saude` não autenticado → a sessão do **Camofox** caiu: ver `camofox-keepalive.log`, reiniciar só `pqbr-camofox-keepalive`; se preciso, `pqbr-camofox` (restaura o mesmo storage-state).
3. Ainda deslogado → login manual **no Camofox** pelo VNC (único lugar de login), com ritmo humano; depois `nlm-sync.sh`.
4. Nunca: logar no Chromium do notebooklm-py, copiar cookies do Chrome, rodar `notebooklm auth refresh`/keepalive poke, criar outro userId/perfil.

## 6. Regra de comportamento humano (REGRAS §157)
Toda automação de navegador simula humano: Camoufox com `humanize: true` (cursor humano; fixo no `server.js`); clicar só por `/click`; texto curto digitado com cadência variável (70–190 ms/tecla, por palavra); texto longo (≥ 80 caracteres) colado (`fill`) após clicar no campo; pausas sorteadas entre ações; keepalive com jitter. Código: `src/pqbr/workflows/camofox_humano.py`.

## 7. Riscos e pendências
- notebooklm-py faz chamadas HTTP com cookies vindos do Firefox: outro cliente, menor risco que dois renovadores, mas pode haver desafio. Monitorar.
- Se o Google passar a exigir DBSC no Linux/Firefox, o desenho precisa ser revisto.
- **Fallback `notebooklm login --master-token` (gpsoauth):** token durável, porém credencial forte e outro risco de conta — **só com aprovação do José**.
- `camofox_humano.py` ainda não tem consumidor real (validar no primeiro fluxo de Studio).
- Ainda não validado ao longo de dias; acompanhar o log do keepalive nos relatórios do Observador.

## 8. Fontes
- notebooklm-py: [SKILL.md](https://github.com/teng-lin/notebooklm-py/blob/HEAD/SKILL.md), [configuration.md (NOTEBOOKLM_REFRESH_CMD)](https://github.com/teng-lin/notebooklm-py/blob/main/docs/configuration.md), [troubleshooting.md](https://github.com/teng-lin/notebooklm-py/blob/main/docs/troubleshooting.md), [issue #367 (Firefox containers)](https://github.com/teng-lin/notebooklm-py/issues/367)
- camofox-browser: [README (persistência, cookie import, storage_state)](https://github.com/jo-inc/camofox-browser/blob/4e64ee50/README.md), [plugin persistence (indexedDB)](https://cdn.jsdelivr.net/npm/@askjo/camofox-browser@1.14.0/plugins/persistence/README.md)
- DBSC: [Workspace Updates mai/2026](https://workspaceupdates.googleblog.com/2026/05/prevent-account-takeovers-with-DBSC-now-generally-available-in-the-Chrome-browser-for-Windows.html), [Google blog](https://blog.google/security/protecting-cookies-with-device-bound-session-credentials/), [Workspace Help: session binding](https://knowledge.workspace.google.com/admin/security/prevent-cookie-theft-with-session-binding), [Chrome for Developers](https://developer.chrome.com/docs/web-platform/device-bound-session-credentials)
- 12/10 16:17 PT: sessão do Camofox caiu. Causa: a CLI notebooklm-py rotacionou o `__Secure-1PSIDTS` (scripts manuais sem DISABLE_KEEPALIVE_POKE). Mesmo SID, mesmo perfil; não foi logout global nem revogação.
- 12/10 17:25 PT: restaurada sem login pelo passo 2 (import dos cookies do notebooklm-py, 43 cookies Google); Gemini e NotebookLM logados. Pedido #1 fechado pelo `AcessosWorkflow`.
- 12/10 17:26: sequência canônica 1–4 (ver playbook `camofox-sessao`) + regra "nenhum script fora do repo/contratos em produção".
- 12/10 18:09 PT (auto, evento #1): notebooklm queda: error": true,
  "code": "UNEXPECTED_ERROR",
  "message": "Unexpected error: CSRF token not found in HTML. Final URL: https://notebook.google.com/\nThis may indicate the page structure has changed."
}

- 12/10 18:09 PT (auto, evento #2): paperclip_cli queda: paperclip cli falhou (company list): API error 400: Request failed with status 400

- 12/10 18:10 PT (auto, evento #3): notebooklm queda: error": true,
  "code": "UNEXPECTED_ERROR",
  "message": "Unexpected error: CSRF token not found in HTML. Final URL: https://notebook.google.com/\nThis may indicate the page structure has changed."
}

- 12/10 18:10 PT (auto, evento #4): paperclip_cli queda: paperclip cli falhou (company list): API error 400: Request failed with status 400

- 12/10 18:12 PT (auto, evento #5): notebooklm queda: error": true,
  "code": "UNEXPECTED_ERROR",
  "message": "Unexpected error: CSRF token not found in HTML. Final URL: https://notebook.google.com/\nThis may indicate the page structure has changed."
}

- 12/10 18:12 PT (auto, evento #6): paperclip_cli queda: paperclip cli falhou (company list): API error 400: Request failed with status 400

- 12/10 18:13 PT (auto, evento #7): notebooklm queda: error": true,
  "code": "UNEXPECTED_ERROR",
  "message": "Unexpected error: CSRF token not found in HTML. Final URL: https://notebook.google.com/\nThis may indicate the page structure has changed."
}

- 12/10 18:13 PT (auto, evento #8): paperclip_cli queda: paperclip cli falhou (company list): API error 400: Request failed with status 400

- 12/10 18:13 PT (auto, evento #9): notebooklm queda: error": true,
  "code": "UNEXPECTED_ERROR",
  "message": "Unexpected error: CSRF token not found in HTML. Final URL: https://notebook.google.com/\nThis may indicate the page structure has changed."
}

- 12/10 18:13 PT (auto, evento #10): paperclip_cli queda: paperclip cli falhou (company list): API error 400: Request failed with status 400

- 12/10 18:13 PT (auto, evento #11): notebooklm queda: error": true,
  "code": "UNEXPECTED_ERROR",
  "message": "Unexpected error: CSRF token not found in HTML. Final URL: https://notebook.google.com/\nThis may indicate the page structure has changed."
}

- 12/10 18:13 PT (auto, evento #12): paperclip_cli queda: paperclip cli falhou (company list): API error 400: Request failed with status 400

- 12/10 18:46 PT (auto, evento #13): notebooklm normalizado: pedido pendente resolvido → ok
- 12/10 18:46 PT (auto, evento #14): paperclip_cli queda: paperclip cli falhou (company list): API error 400: Request failed with status 400

- 12/10 19:10 PT (auto, evento #15): paperclip_cli queda: paperclip cli falhou (company list): API error 400: Request failed with status 400

- 12/10 19:59 PT: rede ? serve 3100 ? Paperclip 3101 corrigido (n?o afeta a sess?o Google). 19:35 crash do pc; Camofox/keepalive voltaram com o boot (conferir pqbr-acessos).
