#!/usr/bin/env bash
# Pós-produção do Short PQBR (portado de yt-llm-bot/scripts/post-short.sh v4, perfil rede; t427).
# trim protegido (fail-closed: só corta após confirmar fim da locução) + auto-speed >85 s + logo bug (sup. dir.)
# + logo de canto (inf. dir.) + sting final (estático com fade, sem PIL). Uso: post-short.sh in.mp4 out.mp4 [trim=2.5]
# Saída: 1 linha "ok k=v ..." (parseada pela Activity pos_produzir). Logos: branding/overlay (mockup stickman v1 —
# substituir pelo logo 2D novo quando existir; trabalho de produção).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IN="${1:?uso: post-short.sh in.mp4 out.mp4 [trim]}"; OUT="${2:?}"; TRIM="${3:-2.5}"
OV="$REPO_ROOT/branding/overlay"
BUG="${LOGO_BUG:-$OV/logo-bug.png}"; CORNER="${LOGO_CORNER_BR:-$OV/logo-corner-br.png}"; STING="${LOGO_STING:-$OV/logo-sting.png}"
MARGIN_TR="${LOGO_MARGIN_TR:-24}"; MARGIN_BR="${LOGO_MARGIN_BR:-5}"; STING_SEC="${STING_SEC:-2.0}"
BUG_FRAC="${LOGO_BUG_FRAC:-0.055}"; COR_W="${LOGO_CORNER_W:-206}"
for f in "$IN" "$BUG" "$CORNER" "$STING"; do [[ -f "$f" ]] || { echo "faltando: $f" >&2; exit 1; }; done

read -r W H DUR < <(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -show_entries format=duration -of json "$IN" |
  python3 -c 'import json,sys;j=json.load(sys.stdin);v=j["streams"][0];print(int(v["width"]),int(v["height"]),float(j["format"]["duration"]))')
python3 -c "import sys; w,h=$W,$H; sys.exit(0 if abs(w/h-9/16)<0.02 else 1)" || { echo "não é 9:16 (${W}x${H})" >&2; exit 1; }

if [[ -n "${SPEECH_END_SEC:-}" ]]; then SPEECH_END="$SPEECH_END_SEC"; SRC=explicit
else
  SPEECH_END=$(ffmpeg -nostdin -hide_banner -nostats -i "$IN" -af "silencedetect=noise=-42dB:d=0.20" -f null - 2>&1 | python3 -c '
import re,sys
d=float(sys.argv[1]); t=sys.stdin.read()
s=[float(x) for x in re.findall(r"silence_start: ([0-9.]+)",t)]; e=[float(x) for x in re.findall(r"silence_end: ([0-9.]+)",t)]
if s and e and abs(e[-1]-d)<=0.25: print(s[-1])' "$DUR")
  [[ -n "$SPEECH_END" ]] || { echo "trim inseguro: fim da locução não confirmado; informe SPEECH_END_SEC" >&2; exit 1; }
  SRC=trailing-silence
fi
CUT=$(python3 -c "print(min($DUR, max(1.0, $SPEECH_END+0.35)))")   # fala íntegra + 0,35 s de respiro (loop)
SPEED=$(python3 -c "c=$CUT; print(round(c/65.0,4) if c>85.0 else 1.0)")
FINAL=$(python3 -c "c=$CUT; print(65.0 if c>85.0 else c)")
BUG_H=$(python3 -c "print(max(48,int($H*$BUG_FRAC)))")
ST0=$(python3 -c "print(max(0,$FINAL-$STING_SEC))")
VB="[0:v]setpts=PTS/${SPEED}[vb0];"; AB="[0:a]atempo=${SPEED}[a];"
FG="${VB}${AB}[1:v]scale=-1:${BUG_H},format=rgba[bug];[2:v]scale=${COR_W}:-1,format=rgba[cor];[3:v]scale=$((W/2)):-1,format=rgba,fade=t=in:st=0:d=0.4:alpha=1[st];[vb0][bug]overlay=W-w-${MARGIN_TR}:${MARGIN_TR}[v1];[v1][cor]overlay=W-w-${MARGIN_BR}:H-h-${MARGIN_BR}[v2];[v2][st]overlay=(W-w)/2:(H-h)/2:enable='gte(t,${ST0})'[v]"
ffmpeg -nostdin -y -hide_banner -loglevel error -i "$IN" -i "$BUG" -i "$CORNER" -loop 1 -itsoffset "$ST0" -i "$STING" -t "$FINAL" \
  -filter_complex "$FG" -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 -c:a aac -b:a 128k -movflags +faststart "$OUT"
echo "ok duracao_in=${DUR} duracao_final=${FINAL} velocidade=${SPEED} fim_fala=${SPEECH_END} fonte_fim=${SRC} saida=${OUT}"
