#!/bin/sh
# ADR-012 (t526): cria uma instância Camofox isolada para <conta>. Por padrão SÓ PREPARA (não instala nem inicia).
# Uso: sh deploy/camofox/criar_instancia.sh <conta> <porta> [--instalar]
#   sem --instalar: cria ~/.camofox-instancias/<conta>/ e <conta>.env (chaves geradas, chmod 600) — nada roda.
#   --instalar: copia o template para ~/.config/systemd/user e faz daemon-reload; continua DISABLED e PARADO.
#   Iniciar/habilitar é passo manual do runbook, com OK do José. Nunca usar para a conta pqbr (9387) fora da migração.
set -eu
C="${1:?conta}"; P="${2:?porta}"; R="$(cd "$(dirname "$0")/../.." && pwd)"
echo "$C" | grep -Eq '^[a-z0-9-]{2,30}$' || { echo "conta inválida"; exit 2; }
echo "$P" | grep -Eq '^9[0-9]{3}$' || { echo "porta fora de 9000-9999"; exit 2; }
[ "$P" = 9387 ] || [ "$P" = 9377 ] && { echo "porta em uso por instância existente"; exit 2; }
ss -ltn | grep -q ":$P " && { echo "porta $P ocupada"; exit 2; }
D="$HOME/.camofox-instancias"; E="$D/$C.env"
[ -e "$E" ] && { echo "já existe: $E"; exit 2; }
umask 077; mkdir -p "$D/$C/profiles" "$D/$C/cookies" "$D/$C/uploads" "$D/$C/traces"
gera() { python3 -c 'import secrets;print(secrets.token_urlsafe(32))'; }
sed -e "s/9397/$P/g" -e "s/<conta>/$C/g" "$R/deploy/camofox/instancia.env.exemplo" > "$E"
for K in API ACCESS ADMIN; do  # chaves geradas direto no arquivo, nunca exibidas
  V="$(gera)"; sed -i "s|^CAMOFOX_${K}_KEY.*|CAMOFOX_${K}_KEY=${V}|" "$E"
done
chmod 600 "$E"; echo "preparado: $E (chaves geradas, não exibidas)"
if [ "${3:-}" = "--instalar" ]; then
  cp "$R/deploy/camofox/camofox@.service" "$HOME/.config/systemd/user/camofox@.service"
  systemctl --user daemon-reload
  echo "unit camofox@$C instalado, DISABLED e PARADO. Próximo passo: runbook §3."
fi
