# Sessão do Camofox caiu (ADR-008, t395: reautenticação autônoma por qualquer meio)
Fila `camofox-pqbr`, concorrência 1; cada passo → log (`pqbr.acoes`) + aviso no Telegram.
1. Renovar na própria instância `pqbr-camofox` (recarregar Studio na mesma tela; aguardar 5–15 min sorteados).
2. Sincronizar cookies do Chrome **só do perfil `PorqueBR`** para a sessão `pqbr`: `scripts/camofox/sync_cookies_chrome.py` (sem `--dry-run`). Só contagens vão para `~/.pqbr/logs/cookies-sync.log`; nenhum valor em issue, log ou memória. Depois, rodar `CamofoxSaudeWorkflow` para confirmar.
3. Outro caminho previsto (reabrir aba, limpar só o estado da aba, sessão nova no mesmo perfil `porquebr`).
4. Esgotou: publicação fica em espera; Diretor → Telegram → José (noVNC/2FA). Guardião confere se não há sinal de comprometimento.

**Perfil único (ADR-008, 12/10):** sempre `userId=pqbr` no `pqbr-camofox` (9387); nunca outro userId, perfil efêmero, `--fresh` ou segundo processo. Se aparecer outra pasta em `~/.pqbr/camofox/profiles/`, é desvio: ticket para o Guardião.

**Aprendizados do `rede` (12/10):**
- **Abas órfãs:** antes de abrir aba nova, listar `/tabs?userId=pqbr` e fechar (`DELETE /tabs/:id`) as que não pertencem a um pedido ativo; manter só a aba permanente do Studio (`sessionKey=sessao`). Aba aberta demais pesa na memória (houve OOM com 900 MB).
- **Timeouts do cliente HTTP:** toda chamada ao Camofox com timeout explícito (curl `-m`, urllib `timeout=`): 20–40 s para abrir aba/navegar, 10–20 s para evaluate/stats; nunca chamada sem prazo.
- **Re-sincronizar depois de reiniciar:** após reiniciar o `pqbr-camofox`, conferir no log `restoring persisted storage state`, abrir Studio e NotebookLM e verificar a conta; se cair, restaurar o último backup de `~/Backups/pqbr-camofox/` no `storage-state.json` (600) e reiniciar uma vez.
- **Fonte de cookies do Chrome não existe mais:** o José saiu da conta no Chrome do servidor (12/10). O degrau "sincronizar cookies do Chrome" (`sync_cookies_chrome.py`) está sem fonte; a escada vai direto de "renovar no Camofox" para login manual pelo VNC.
