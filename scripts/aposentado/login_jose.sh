#!/bin/sh
export NOTEBOOKLM_HOME=$HOME/.pqbr/notebooklm DISPLAY=${DISPLAY:-:1}
B=$HOME/.pqbr/notebooklm/venv/bin
$B/python $HOME/Workspace/PQBR/scripts/notebooklm/nlm_login_manual.py && $B/notebooklm -p pqbr login --browser-timeout 10800 && $B/notebooklm -p pqbr auth check --test
