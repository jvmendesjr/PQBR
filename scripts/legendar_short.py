#!/usr/bin/env python3
"""Legenda gravada para Shorts PQBR usando Whisper local (faster-whisper, CPU).
Uso: ~/.venvs/whisper/bin/python scripts/legendar_short.py --video V.mp4 --texto narracao.txt --saida V-legendado.mp4 [--audio narracao.mp3] [--modelo small]
Gera <saida>.ass e <saida>.srt ao lado. Nunca sobrescreve o vídeo de entrada.
Texto final = narracao.txt (fonte da verdade); o Whisper só fornece os tempos por palavra."""
import argparse, difflib, json, re, subprocess, sys, unicodedata
from pathlib import Path

def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))

def transcrever(audio, modelo):
    from faster_whisper import WhisperModel
    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    import numpy as np  # decodifica com ffmpeg (evita incompatibilidade do PyAV)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    pcm = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    segs, _ = m.transcribe(pcm, language="pt", word_timestamps=True, vad_filter=False)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words if w.word.strip()]

def alinhar(texto_words, wh):
    a = [norm(w) for w in texto_words]; b = [norm(w[0]) for w in wh]
    t = [None] * len(texto_words)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        tag, i1, i2, j1, j2 = blk
        if tag == "equal":
            for k in range(i2 - i1): t[i1 + k] = (wh[j1 + k][1], wh[j1 + k][2])
        elif tag == "replace" and j2 > j1:
            s, e = wh[j1][1], wh[j2 - 1][2]; n = i2 - i1
            for k in range(n): t[i1 + k] = (s + (e - s) * k / n, s + (e - s) * (k + 1) / n)
    # interpola faltantes
    for i in range(len(t)):
        if t[i] is None:
            p = next((t[j][1] for j in range(i - 1, -1, -1) if t[j]), 0.0)
            q = next((t[j][0] for j in range(i + 1, len(t)) if t[j]), p + 0.3)
            gap = [j for j in range(i, len(t)) if t[j] is None]
            run = len([j for j in range(i, len(t)) if t[j] is None and all(t[x] is None for x in range(i, j + 1))])
            for k in range(run): t[i + k] = (p + (q - p) * k / run, p + (q - p) * (k + 1) / run)
    return t

def blocos(words, times, maxw=3):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        fim = re.search(r"[.,!?;:…]$", w)
        curto = sum(len(words[j]) for j in cur) <= 14
        if fim or len(cur) >= (4 if curto else maxw) or (i + 1 < len(words) and times[i + 1][0] - times[i][1] > 0.6):
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out

def ts_ass(s): h=int(s//3600); m=int(s%3600//60); return f"{h}:{m:02d}:{s%60:05.2f}"
def ts_srt(s): ms=int(round(s*1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
def esc(w): return w.replace("{", "(").replace("}", ")")

ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Short,{fonte},{tam},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,2,2,80,80,{margem},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
AMARELO = r"{\c&H2BC8FF&}"; BRANCO = r"{\c&HFFFFFF&}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True); ap.add_argument("--texto", required=True)
    ap.add_argument("--saida", required=True); ap.add_argument("--audio")
    ap.add_argument("--modelo", default="small"); ap.add_argument("--fonte", default="DejaVu Sans")
    ap.add_argument("--tam", type=int, default=86); ap.add_argument("--margem", type=int, default=560)
    a = ap.parse_args()
    v, s = Path(a.video).resolve(), Path(a.saida).resolve()
    if v == s or s.exists(): sys.exit(f"recuso sobrescrever: {s}")
    words = Path(a.texto).read_text(encoding="utf-8").split()
    wh = transcrever(a.audio or v, a.modelo)
    t = alinhar(words, wh)
    ok = sum(1 for x in difflib.SequenceMatcher(None, [norm(w) for w in words], [norm(w[0]) for w in wh], autojunk=False).get_matching_blocks()) and \
         sum(b.size for b in difflib.SequenceMatcher(None, [norm(w) for w in words], [norm(w[0]) for w in wh], autojunk=False).get_matching_blocks())
    ass = [ASS_HEAD.format(fonte=a.fonte, tam=a.tam, margem=a.margem)]; srt = []
    for n, bl in enumerate(blocos(words, t), 1):
        ini, fim = t[bl[0]][0], t[bl[-1]][1]
        srt.append(f"{n}\n{ts_srt(ini)} --> {ts_srt(fim)}\n{' '.join(words[i] for i in bl)}\n")
        for k, i in enumerate(bl):
            s0 = ini if k == 0 else t[i][0]; e0 = fim if k == len(bl) - 1 else t[bl[k + 1]][0]
            txt = " ".join((AMARELO + esc(words[j]) + BRANCO) if j == i else esc(words[j]) for j in bl)
            ass.append(f"Dialogue: 0,{ts_ass(s0)},{ts_ass(e0)},Short,,0,0,0,,{txt}")
    pa, ps = s.with_suffix(".ass"), s.with_suffix(".srt")
    pa.write_text("\n".join(ass) + "\n", encoding="utf-8"); ps.write_text("\n".join(srt), encoding="utf-8")
    Path(s.with_suffix(".whisper.json")).write_text(json.dumps(wh, ensure_ascii=False), encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-n", "-i", str(v), "-vf", f"ass={pa}", "-c:v", "libx264", "-crf", "20",
                    "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", str(s)], check=True)
    print(json.dumps({"saida": str(s), "ass": str(pa), "srt": str(ps), "palavras_texto": len(words),
                      "palavras_whisper": len(wh), "casadas": ok, "modelo": a.modelo}, ensure_ascii=False))

if __name__ == "__main__": main()
