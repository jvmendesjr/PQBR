#!/usr/bin/env bash
# Wrapper do adapter opencode_local p/ Devs: roda o opencode num container isolado.
# Só enxerga: worktree dev (rw), .git (rw), repo PQBR (ro), HOME isolado (rw), config/skills/instruções PQBR (ro).
set -euo pipefail
CO=be3980d6-51ae-4cee-b85f-923b4568188c; R=/home/pc/Workspace/PQBR; I=/home/pc/.paperclip/instances/default
args=(); for v in $(env | cut -d= -f1 | grep -E '^(PAPERCLIP_|PQBR_|NINEROUTER_|OPENCODE_|XDG_CONFIG_HOME$|HOME$)'); do args+=(-e "$v"); done
exec docker run --rm -i --init --network host --user "$(id -u):$(id -g)" --name "pqbr-dev-${PAPERCLIP_RUN_ID:-$$}" \
  --cap-drop ALL --security-opt no-new-privileges --memory 4g --pids-limit 512 \
  -v "$R:$R:ro" -v "$R/.git:$R/.git" -v /home/pc/.pqbr/dev-worktree:/home/pc/.pqbr/dev-worktree \
  -v "$HOME:$HOME" -v /home/pc/.opencode/bin:/home/pc/.opencode/bin:ro \
  -v /home/pc/.local/share/uv/python:/home/pc/.local/share/uv/python:ro \
  -v "$I/skills/$CO:$I/skills/$CO:ro" -v "$I/companies/$CO:$I/companies/$CO:ro" \
  -w "$PWD" "${args[@]}" pqbr-dev:1 /home/pc/.opencode/bin/opencode "$@"
