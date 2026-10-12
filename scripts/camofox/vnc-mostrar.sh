#!/bin/sh
# PQBR: mostra o Camofox PQBR (Xvfb do pqbr-camofox) na tela física do pc (:0) para o José logar.
# Uso: vnc-mostrar.sh start | stop | status.  NÃO loga nada sozinho; não mexe no Camofox nem no perfil.
# Mesmo desenho do login de 12/10 02:19: x11vnc preso ao IP da tailnet, porta 5988, senha em vnc-login.passwd (600).
set -eu
PW="$HOME/.pqbr/camofox/vnc-login.passwd"; PORTA=5988; LOG=/tmp/pqbr-x11vnc-$PORTA.log
IPT=$(tailscale ip -4 2>/dev/null | head -1)
disp() {  # DISPLAY do camoufox-bin filho do pqbr-camofox (o Xvfb muda a cada início do serviço)
  P=$(systemctl --user show -p MainPID --value pqbr-camofox)
  for x in $(pgrep -P "$P" camoufox-bin); do tr "\\0" "\\n" < /proc/$x/environ | sed -n "s/^DISPLAY=//p" | head -1; return; done
}
case "${1:-status}" in
  start)
    D=$(disp); [ -n "$D" ] || { echo "display do Camofox não encontrado"; exit 1; }
    pgrep -f "rfbport $PORTA" >/dev/null || x11vnc -display "$D" -listen "$IPT" -noipv6 -rfbport $PORTA -rfbauth "$PW" -forever -shared -noxdamage -quiet -bg -o "$LOG"
    sleep 1
    ( set -a; . "$HOME/.pqbr/camofox/.env"; set +a   # aba de login visível (o José digita; nada é preenchido aqui)
      curl -s -m 20 -o /dev/null -X POST -H "Authorization: Bearer ${CAMOFOX_API_KEY}" -H "Content-Type: application/json" \
        -d url:https://accounts.google.com/ServiceLogin?continue=https://gemini.google.com/app http://127.0.0.1:9387/tabs )
    ( set -a; . "$HOME/.pqbr/camofox/.env"; set +a   # aba de login visível (o José digita; nada é preenchido aqui)
      curl -s -m 20 -o /dev/null -X POST -H "Authorization: Bearer ${CAMOFOX_API_KEY}" -H "Content-Type: application/json" \
        -d sessionKey:login-jose http://127.0.0.1:9387/tabs )
    ( set -a; . "$HOME/.pqbr/camofox/.env"; set +a   # aba de login visível (o José digita; nada é preenchido aqui)
      curl -s -m 20 -o /dev/null -X POST -H "Authorization: Bearer ${CAMOFOX_API_KEY}" -H "Content-Type: application/json" \
        -d userId:pqbr http://127.0.0.1:9387/tabs )
    DISPLAY=:0 XAUTHORITY="$HOME/.Xauthority" nohup xtigervncviewer -passwd "$PW" -geometry 1300x760+40+40 "$IPT::$PORTA" >/tmp/pqbr-vncviewer.log 2>&1 &
    echo "VNC ligado: Camofox $D → tela :0 (e $IPT:$PORTA na tailnet)";;
  stop) pkill -f "xtigervncviewer.*$PORTA" || true; pkill -f "x11vnc.*rfbport $PORTA" || true; echo "VNC desligado";;
  status) echo "display Camofox: $(disp)"; pgrep -af "rfbport $PORTA|xtigervncviewer" || echo "VNC desligado";;
esac
