#!/bin/sh
# ADR-012 (t526/t528): cria uma instância Camofox isolada para <conta>. IDEMPOTENTE. Por padrão SÓ PREPARA.
# Uso: sh deploy/camofox/criar_instancia.sh <conta> <porta> [--instalar]
#   sem --instalar: cria $INST_DIR/<conta>/ e <conta>.env. Se o .env existe e está completo, não mexe;
#                   se tem placeholders <...>, completa só as chaves faltantes (valores nunca exibidos).
#   --instalar: copia o template para $SYSTEMD_DIR e faz daemon-reload (só no dir padrão); unit fica
#               DISABLED e PARADA. Pode ser rodado de novo a qualquer momento (segunda execução OK).
#   Iniciar/habilitar é passo manual do runbook, com OK do José.
# Variáveis (para teste): CAMOFOX_INSTANCIAS_DIR (padrão ~/.camofox-instancias),
#   SYSTEMD_DIR (padrão ~/.config/systemd/user; diferente do padrão → sem daemon-reload),
#   SKIP_PORT_CHECK=1 (não consulta ss).
set -eu
C="${1:?conta}"; P="${2:?porta}"; MODO="${3:-}"; R="$(cd "$(dirname "$0")/../.." && pwd)"
D="${CAMOFOX_INSTANCIAS_DIR:-$HOME/.camofox-instancias}"
SD_PADRAO="$HOME/.config/systemd/user"; SD="${SYSTEMD_DIR:-$SD_PADRAO}"
echo "$C" | grep -Eq '^[a-z0-9-]{2,30}$' || { echo "conta inválida"; exit 2; }
echo "$P" | grep -Eq '^9[0-9]{3}$' || { echo "porta fora de 9000-9999"; exit 2; }
case "$MODO" in ""|--instalar) ;; *) echo "opção desconhecida: $MODO"; exit 2;; esac
E="$D/$C.env"
umask 077; mkdir -p "$D/$C/profiles" "$D/$C/cookies" "$D/$C/uploads" "$D/$C/traces"
gera() { python3 -c 'import secrets;print(secrets.token_urlsafe(32))'; }

if [ ! -e "$E" ]; then
  if [ "$P" = 9387 ] || [ "$P" = 9377 ]; then echo "porta de instância existente; use o runbook §3"; exit 2; fi
  if [ "${SKIP_PORT_CHECK:-0}" != 1 ] && ss -ltn | grep -q ":$P "; then echo "porta $P ocupada"; exit 2; fi
  sed -e "s/9397/$P/g" -e "s/<conta>/$C/g" "$R/deploy/camofox/instancia.env.exemplo" > "$E"
  echo "criado: $E"
else
  grep -q "^CAMOFOX_PORT=$P\$" "$E" || { echo "$E existe com outra porta; abortando"; exit 2; }
  echo "já existe: $E"
fi
chmod 600 "$E"
N=0
for K in API ACCESS ADMIN; do  # completa só o que falta; valor vai direto ao arquivo
  if ! grep -q "^CAMOFOX_${K}_KEY=" "$E"; then
    echo "CAMOFOX_${K}_KEY=$(gera)" >> "$E"; N=$((N+1))
  elif grep -q "^CAMOFOX_${K}_KEY=\(<.*>\)\?\$" "$E"; then
    V="$(gera)"; sed -i "s|^CAMOFOX_${K}_KEY.*|CAMOFOX_${K}_KEY=${V}|" "$E"; N=$((N+1))
  fi
done
if grep -q '<[a-z]*>' "$E"; then echo "ainda há placeholders em $E (corrija à mão)"; exit 3; fi
echo "chaves geradas agora: $N (valores não exibidos); .env completo"

if [ "$MODO" = "--instalar" ]; then
  mkdir -p "$SD"
  if cmp -s "$R/deploy/camofox/camofox@.service" "$SD/camofox@.service"; then echo "template já instalado em $SD"
  else cp "$R/deploy/camofox/camofox@.service" "$SD/camofox@.service"; echo "template copiado para $SD"; fi
  if [ "$SD" = "$SD_PADRAO" ]; then systemctl --user daemon-reload; fi
  echo "unit camofox@$C DISABLED e PARADA (nada iniciado). Próximo passo: runbook."
fi
