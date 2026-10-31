#!/bin/sh
# Gera infra/pqbr-db/.env com senhas aleatórias (não sobrescreve). Nada é impresso.
set -eu; cd "$(dirname "$0")"
umask 077
if [ -f .env ]; then  # só acrescenta variáveis novas (ex.: PQBR_MANUT_PASSWORD, t369)
  [ -z "$(tail -c1 .env)" ] || echo >> .env
  grep -q "^PQBR_MANUT_PASSWORD=" .env || echo "PQBR_MANUT_PASSWORD=$(openssl rand -hex 24)" >> .env
  chmod 600 .env; echo ".env existente completado (600)"; exit 0
fi
{ echo "COMPOSE_PROJECT_NAME=pqbr-db"
  for v in POSTGRES_PASSWORD PQBR_APP_PASSWORD PQBR_LEITURA_PASSWORD PQBR_MANUT_PASSWORD; do echo "$v=$(openssl rand -hex 24)"; done; } > .env
chmod 600 .env; echo ".env criado (600)"
