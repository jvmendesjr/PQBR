#!/usr/bin/env python3
"""Remonta um Short com voz dinâmica + CTA PERSONALIZADO do roteiro (lote-2510).

REGRA (José 25/10/2026, ERR-MON-02): cada Short fecha com o CTA do próprio
roteiro (última frase original de narracao.txt, ligada ao tema). O take B
cta-padrao-B.mp3 é só REFERÊNCIA DE ENTONAÇÃO; usá-lo como --cta aborta, salvo
--permitir-cta-generico (só quando o CTA original do roteiro for literalmente
"Segue o Porquê BR").
Áudio: corpo (opcionalmente acelerado via atempo, e/ou cortado em --corte-fim,
p.ex. antes do CTA antigo) + pausa ~0,3 s + CTA do tema (fades curtos de 30 ms).
Vídeo: mesmos clipes, cortes nas pausas da voz nova (silencedetect), sem quadro
congelado: cada corte <= duração do clipe; se o último segmento não couber no
clipe, vira um still (PNG) estendido.
Não sobrescreve arquivos existentes (aborta).
"""
import argparse, json, os, subprocess, sys

def sh(c, **k): return subprocess.run(c, check=True, capture_output=True, text=True, **k)
def dur(f): return float(sh(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).stdout)
def pausas(f, db=-40, d=0.2):
    err = subprocess.run(['ffmpeg','-hide_banner','-i',f,'-af',f'silencedetect=n={db}dB:d={d}','-f','null','-'],capture_output=True,text=True).stderr
    s=[];st=None
    for l in err.splitlines():
        if 'silence_start' in l: st=float(l.split('silence_start:')[1])
        elif 'silence_end' in l and st is not None:
            e=float(l.split('silence_end:')[1].split('|')[0]); s.append((st,e)); st=None
    return s

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dir',required=True); ap.add_argument('--corpo',required=True)
    ap.add_argument('--cta',required=True); ap.add_argument('--atempo',type=float,default=1.0)
    ap.add_argument('--corte-fim',type=float); ap.add_argument('--pausa',type=float,default=0.3)
    ap.add_argument('--segs',required=True,help='JSON [[arquivo,dur_original],...] (montar.cmd.json)')
    ap.add_argument('--still',default='c1.png'); ap.add_argument('--saida',required=True)
    ap.add_argument('--audio-saida',required=True)
    ap.add_argument('--permitir-cta-generico',action='store_true')
    a=ap.parse_args(); os.chdir(a.dir)
    if os.path.basename(a.cta).startswith('cta-padrao') and not a.permitir_cta_generico:
        sys.exit('CTA genérico recusado: use o CTA do roteiro (ERR-MON-02)')
    for f in (a.saida,a.audio_saida):
        if os.path.exists(f): sys.exit(f'existe, não sobrescrevo: {f}')
    segs=json.load(open(a.segs)) if os.path.exists(a.segs) else json.loads(a.segs)
    # 1) áudio
    af=[]
    if a.atempo!=1.0: af.append(f'atempo={a.atempo}')
    if a.corte_fim: af.append(f'atrim=0:{a.corte_fim}')
    af.append('silenceremove=stop_periods=-1:stop_threshold=-45dB:stop_duration=0.15:stop_silence=0.15' if False else 'anull')
    fc=(f"[0:a]{','.join(af)},aformat=sample_rates=44100:channel_layouts=mono,areverse,silenceremove=start_periods=1:start_threshold=-45dB,afade=t=in:d=0.03,areverse,apad=pad_dur={a.pausa}[c];"
        f"[1:a]aformat=sample_rates=44100:channel_layouts=mono,afade=t=in:d=0.03[t];[c][t]concat=n=2:v=0:a=1[a]")
    sh(['ffmpeg','-v','error','-i',a.corpo,'-i',a.cta,'-filter_complex',fc,'-map','[a]','-c:a','libmp3lame','-b:a','192k',a.audio_saida])
    T=dur(a.audio_saida); P=pausas(a.audio_saida)
    # 2) cortes
    Lc={}
    def L(fn):
        if fn.endswith('.png'): return 1e9
        if fn not in Lc: Lc[fn]=dur(fn)
        return Lc[fn]
    tot0=sum(d for _,d in segs); k=T/tot0
    mids=[(s+e)/2 for s,e in P if e<T-0.5]
    alvo=0; ini=0; out=[]
    for i,(fn,d0) in enumerate(segs[:-1]):
        alvo+=d0*k; lim=ini+L(fn)-0.05
        cand=[m for m in mids if ini+1.5<=m<=lim]
        fim=min(cand,key=lambda m:abs(m-alvo)) if cand else min(lim,alvo)
        out.append([fn,round(fim-ini,3)]); ini=fim
    fn=segs[-1][0]; resto=round(T-ini+0.05,3)
    if fn.endswith(".png") or resto>L(fn)-0.05:
        # reusa clipes (sem quadro congelado): um que caiba, senão encadeia os mais longos
        vids=sorted({f for f,_ in segs if not f.endswith('.png')},key=L,reverse=True)
        cab=[f for f in vids if L(f)-0.05>=resto]
        if cab: fn=cab[0]
        elif vids:
            prev=out[-1][0] if out else None; i=0
            while resto>0.05:
                f=vids[i%len(vids)]; i+=1
                if f==prev and len(vids)>1: continue
                d=round(min(resto,L(f)-0.05),3); out.append([f,d]); resto=round(resto-d,3); prev=f
            fn=None
        else: fn=a.still
    if fn: out.append([fn,resto])
    # 3) vídeo
    ins=[];f=[]
    for i,(fn,d) in enumerate(out):
        ins+=(['-loop','1','-t',str(d+0.5),'-i',fn] if fn.endswith('.png') else ['-i',fn])
        f.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,trim=duration={d},setpts=PTS-STARTPTS,setsar=1[v{i}]")
    n=len(out)
    fc=';'.join(f)+';'+''.join(f'[v{i}]' for i in range(n))+f'concat=n={n}:v=1:a=0[v]'
    sh(['ffmpeg','-v','error']+ins+['-i',a.audio_saida,'-filter_complex',fc,'-map','[v]','-map',f'{n}:a','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest',a.saida])
    print(json.dumps({'audio':a.audio_saida,'audio_s':round(T,2),'video':a.saida,'video_s':round(dur(a.saida),2),'cortes':out,'freeze':'nenhum (trim<=clipe)'},ensure_ascii=False))
main()
