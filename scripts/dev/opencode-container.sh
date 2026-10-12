#!/usr/bin/env bash
# Wrapper do adapter opencode_local p/ Devs: roda o opencode num container isolado.
# Só enxerga: worktree dev (rw), .git (rw), repo PQBR (ro), HOME isolado (rw), config/skills/instruções PQBR (ro).
# Rede: pqbr-dev-int (interna, sem internet); saída só via relay pqbr-dev-egress -> 9router/Temporal/Paperclip. Sem segredos montados.
set -euo pipefail
CO=be3980d6-51ae-4cee-b85f-923b4568188c; R=/home/pc/Workspace/PQBR; I=/home/pc/.paperclip/instances/default
args=(); for v in $(env | cut -d= -f1 | grep -E '^(PAPERCLIP_|PQBR_|NINEROUTER_|OPENCODE_|XDG_CONFIG_HOME$|HOME$)'); do args+=(-e "$v"); done; args+=(-e XDG_CONFIG_HOME=/home/pc/.pqbr/dev-home/.config -e PQBR_PAPERCLIP_API=http://172.31.250.1:3100 -e TEMPORAL_ADDRESS=172.31.250.1:7233 -e PAPERCLIP_API_URL=http://172.31.250.1:3100)
mkdir -p /home/pc/.pqbr/dev-home/.config/opencode && install -m 600 "$R/company/opencode-config-dev/opencode/opencode.json" /home/pc/.pqbr/dev-home/.config/opencode/opencode.json
exec docker run --rm -i --init --network pqbr-dev-int --user "$(id -u):$(id -g)" --name "pqbr-dev-${PAPERCLIP_RUN_ID:-$$}" \
  --cap-drop ALL --security-opt no-new-privileges --memory 4g --pids-limit 512 \
  -v "$R:$R:ro" -v "$R/.git:$R/.git" -v /home/pc/.pqbr/dev-worktree:/home/pc/.pqbr/dev-worktree \
  -v "$HOME:$HOME" -v /home/pc/.opencode/bin:/home/pc/.opencode/bin:ro \
  -v /home/pc/.local/share/uv/python:/home/pc/.local/share/uv/python:ro \
  -v "$I/skills/$CO:$I/skills/$CO:ro" -v "$I/companies/$CO:$I/companies/$CO:ro" \
  -w "$PWD" "${args[@]}" pqbr-dev:1 /home/pc/.opencode/bin/opencode "$@"
