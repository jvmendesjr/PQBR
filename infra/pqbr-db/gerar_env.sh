#!/bin/sh
# Gera infra/pqbr-db/.env com senhas aleatórias (não sobrescreve). Nada é impresso.
set -eu; cd "$(dirname "$0")"
[ -f .env ] && { echo ".env já existe; nada feito"; exit 0; }
umask 077
{ echo "COMPOSE_PROJECT_NAME=pqbr-db"
  for v in POSTGRES_PASSWORD PQBR_APP_PASSWORD PQBR_LEITURA_PASSWORD; do echo "$v=$(openssl rand -hex 24)"; done; } > .env
chmod 600 .env; echo ".env criado (600)"
