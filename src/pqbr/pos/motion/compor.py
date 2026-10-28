"""Composição com FFmpeg: troca o trecho do porquê pelo bloco de tela cheia, aplica a camada "sobre" e
preserva a narração original (áudio copiado sem recodificar). Também gera folha de contato e teste a 360 px."""
from __future__ import annotations
import json, shlex, subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from ...contratos.motion import PlanoMotion

FFMPEG = "ffmpeg"


@dataclass
class ResultadoComposicao:
    saida: str
    comando: str
    bloco: tuple[float, float] | None
    clipes_substituidos: list[int]
    duracao_original_s: float


def _snap(t: float, fps: int) -> float: return round(round(t * fps) / fps, 6)


def duracao(video: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(video)], capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def comando_compor(plano: PlanoMotion, original: Path, pasta_render: Path, saida: Path, com_sobre: bool = True) -> list[str]:
    fps = plano.fps
    entradas = ["-i", str(original)]
    filtros, idx = [], 1
    if plano.bloco is not None:
        ini, fim = _snap(plano.bloco.inicio, fps), _snap(plano.bloco.fim, fps)
        entradas += ["-framerate", str(fps), "-i", str(pasta_render / "tela_cheia" / "q%05d.png")]
        filtros += [f"[0:v]trim=end={ini},setpts=PTS-STARTPTS[a]",
                    f"[{idx}:v]format=yuv420p,setsar=1[b]",
                    f"[0:v]trim=start={fim},setpts=PTS-STARTPTS[c]",
                    "[a][b][c]concat=n=3:v=1:a=0[v0]"]
        idx += 1
    else:
        filtros.append("[0:v]copy[v0]")
    if com_sobre:
        entradas += ["-framerate", str(fps), "-i", str(pasta_render / "sobre" / "q%05d.png")]
        filtros.append(f"[v0][{idx}:v]overlay=0:0:format=auto:shortest=0[v]")
    else:
        filtros.append("[v0]copy[v]")
    return [FFMPEG, "-y", *entradas, "-filter_complex", ";".join(filtros), "-map", "[v]", "-map", "0:a?",
            "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(fps), "-c:a", "copy", "-movflags", "+faststart", str(saida)]


def compor(plano: PlanoMotion, original: Path, pasta_render: Path, saida: Path, cortes: list[float] | None = None, com_sobre: bool = True) -> ResultadoComposicao:
    original, saida = Path(original), Path(saida)
    cmd = comando_compor(plano, original, pasta_render, saida, com_sobre)
    subprocess.run(cmd, check=True, capture_output=True)
    res = ResultadoComposicao(saida=str(saida), comando=shlex.join(cmd),
                              bloco=(plano.bloco.inicio, plano.bloco.fim) if plano.bloco else None,
                              clipes_substituidos=plano.clipes_substituidos(cortes or []), duracao_original_s=duracao(original))
    saida.with_suffix(".composicao.json").write_text(json.dumps(asdict(res), ensure_ascii=False, indent=1), encoding="utf-8")
    return res


def folha_contato(video: Path, saida_png: Path, cada_s: float = 1.0, colunas: int = 6, largura: int = 180) -> Path:
    """Um quadro a cada `cada_s` segundos, em grade. Serve para a autocrítica (§26) e para o Auditor."""
    n = max(1, int(duracao(Path(video)) / cada_s) + 1)
    linhas = -(-n // colunas)
    vf = f"fps=1/{cada_s},scale={largura}:-1,tile={colunas}x{linhas}:padding=4:margin=4:color=white"
    subprocess.run([FFMPEG, "-y", "-i", str(video), "-vf", vf, "-frames:v", "1", str(saida_png)], check=True, capture_output=True)
    return Path(saida_png)


def teste_360(video: Path, saida: Path) -> Path:
    """Cópia a 360 px de largura: se o texto não se lê aqui, não se lê no celular."""
    subprocess.run([FFMPEG, "-y", "-i", str(video), "-vf", "scale=360:-2", "-c:v", "libx264", "-crf", "23", "-preset", "fast", "-an", str(saida)], check=True, capture_output=True)
    return Path(saida)
