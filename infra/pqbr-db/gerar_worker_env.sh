#!/bin/sh
# Gera ~/.pqbr/worker.env (600) só com as senhas do pqbr_app e do pqbr_manutencao, copiadas do .env. Nada é impresso.
set -eu; cd "$(dirname "$0")"
umask 077; mkdir -p "$HOME/.pqbr"
grep -E '^PQBR_(APP|MANUT)_PASSWORD=' .env > "$HOME/.pqbr/worker.env"
chmod 600 "$HOME/.pqbr/worker.env"; echo "worker.env criado (600)"
