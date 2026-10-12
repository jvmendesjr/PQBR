# Sessão do Camofox caiu (ADR-008, t395: reautenticação autônoma por qualquer meio)
Fila `camofox-pqbr`, concorrência 1; cada passo → log (`pqbr.acoes`) + aviso no Telegram.
1. Renovar na própria instância `pqbr-camofox` (recarregar Studio na mesma tela; aguardar 5–15 min sorteados).
2. Sincronizar cookies do Chrome **só do perfil `PorqueBR`** para a sessão `pqbr`: `scripts/camofox/sync_cookies_chrome.py` (sem `--dry-run`). Só contagens vão para `~/.pqbr/logs/cookies-sync.log`; nenhum valor em issue, log ou memória. Depois, rodar `CamofoxSaudeWorkflow` para confirmar.
3. Outro caminho previsto (reabrir aba, limpar só o estado da aba, sessão nova no mesmo perfil `porquebr`).
4. Esgotou: publicação fica em espera; Diretor → Telegram → José (noVNC/2FA). Guardião confere se não há sinal de comprometimento.

**Perfil único (ADR-008, 12/10):** sempre `userId=pqbr` no `pqbr-camofox` (9387); nunca outro userId, perfil efêmero, `--fresh` ou segundo processo. Se aparecer outra pasta em `~/.pqbr/camofox/profiles/`, é desvio: ticket para o Guardião.
