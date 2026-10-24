"""Cliente backend, sem retry, para a API pública de Text-to-Speech da ElevenLabs.

A voz e os parâmetros vêm de config/voz_narracao.json. A chave só é lida de
ELEVENLABS_API_KEY no processo servidor; nunca é retornada, gravada ou logada.
"""
from __future__ import annotations

import json
import math
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
VOICE_CONFIG_PATH = ROOT / "config" / "voz_narracao.json"
VOICE_CONFIG_ENV = "PQBR_VOICE_CONFIG"
CREDENTIAL_ENV = "ELEVENLABS_API_KEY"
API_ROOT = "https://api.elevenlabs.io/v1/text-to-speech/"
OUTPUT_FORMAT = "mp3_44100_128"


class ElevenLabsError(RuntimeError):
    """Falha sanitizada do cliente; não contém chave nem corpo de resposta."""


class VoiceConfigError(ElevenLabsError):
    """Configuração versionada ausente ou inválida."""


class SynthesisNotAuthorized(ElevenLabsError):
    """A síntese está desabilitada pelo gate local de autorização."""


@dataclass(frozen=True)
class VoiceConfig:
    provider: str
    status: str
    runtime_integrated: bool
    generation_authorized: bool
    publication_authorized: bool
    voice_name: str
    voice_id: str
    language: str
    model_id: str
    seed: int
    voice_settings: dict[str, float | bool]


def voice_config_path() -> Path:
    return Path(os.environ.get(VOICE_CONFIG_ENV, str(VOICE_CONFIG_PATH)))


def load_voice_config(path: str | Path | None = None) -> VoiceConfig:
    """Carrega e valida a seleção versionada; não aplica defaults de voz."""
    config_path = Path(path) if path is not None else voice_config_path()
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise VoiceConfigError("Configuração de voz indisponível ou inválida") from None
    if not isinstance(raw, dict):
        raise VoiceConfigError("Configuração de voz deve ser um objeto JSON")

    voice = raw.get("voice")
    tts = raw.get("tts")
    if not isinstance(voice, dict) or not isinstance(tts, dict):
        raise VoiceConfigError("Configuração de voz incompleta")
    settings = tts.get("voice_settings")
    if not isinstance(settings, dict):
        raise VoiceConfigError("Parâmetros voice_settings ausentes")

    required_settings = {
        "stability", "similarity_boost", "style", "use_speaker_boost", "speed"
    }
    if set(settings) != required_settings:
        raise VoiceConfigError("Parâmetros voice_settings inesperados ou incompletos")
    numeric_settings: dict[str, float | bool] = {}
    for key in ("stability", "similarity_boost", "style", "speed"):
        value = settings[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise VoiceConfigError(f"Parâmetro de voz inválido: {key}")
        numeric_settings[key] = float(value)
    for key in ("stability", "similarity_boost", "style"):
        if not 0.0 <= numeric_settings[key] <= 1.0:
            raise VoiceConfigError(f"Parâmetro de voz fora do intervalo: {key}")
    if not 0.0 < numeric_settings["speed"] <= 2.0:
        raise VoiceConfigError("Parâmetro de voz fora do intervalo: speed")
    speaker_boost = settings["use_speaker_boost"]
    if not isinstance(speaker_boost, bool):
        raise VoiceConfigError("Parâmetro de voz inválido: use_speaker_boost")
    numeric_settings["use_speaker_boost"] = speaker_boost

    flags = ("runtime_integrated", "generation_authorized", "publication_authorized")
    if any(not isinstance(raw.get(flag), bool) for flag in flags):
        raise VoiceConfigError("Gates de voz devem ser booleanos explícitos")
    voice_id = voice.get("voice_id")
    model_id = tts.get("model_id")
    voice_name = voice.get("name")
    language = voice.get("language")
    if not isinstance(voice_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", voice_id):
        raise VoiceConfigError("voice_id ausente ou inválido")
    if not isinstance(model_id, str) or not model_id.strip():
        raise VoiceConfigError("model_id ausente")
    if not isinstance(voice_name, str) or not voice_name.strip():
        raise VoiceConfigError("Nome da voz ausente")
    if not isinstance(language, str) or not language.strip():
        raise VoiceConfigError("Idioma da voz ausente")
    seed = tts.get("seed")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise VoiceConfigError("seed ausente ou inválida")
    if raw.get("provider") != "elevenlabs" or raw.get("status") != "selected":
        raise VoiceConfigError("A configuração não seleciona uma voz ElevenLabs")

    return VoiceConfig(
        provider=raw["provider"],
        status=raw["status"],
        runtime_integrated=raw["runtime_integrated"],
        generation_authorized=raw["generation_authorized"],
        publication_authorized=raw["publication_authorized"],
        voice_name=voice_name,
        voice_id=voice_id,
        language=language,
        model_id=model_id,
        seed=seed,
        voice_settings=numeric_settings,
    )


def synthesize(
    text: str,
    *,
    config_path: str | Path | None = None,
    timeout: float = 60.0,
    transport: Callable[..., Any] | None = None,
) -> bytes:
    """Solicita um único áudio. Sem retry e sem escrita/upload do resultado."""
    config = load_voice_config(config_path)
    if not config.runtime_integrated or not config.generation_authorized:
        raise SynthesisNotAuthorized("Síntese TTS bloqueada pelo gate de autorização")
    if not isinstance(text, str) or not text.strip():
        raise ElevenLabsError("Texto de narração vazio")
    credential = os.environ.get(CREDENTIAL_ENV, "").strip()
    if not credential:
        raise ElevenLabsError("ELEVENLABS_API_KEY não está configurada no backend")

    url = API_ROOT + urllib.parse.quote(config.voice_id, safe="") + "?" + urllib.parse.urlencode(
        {"output_format": OUTPUT_FORMAT}
    )
    payload = {
        "text": text,
        "model_id": config.model_id,
        "voice_settings": config.voice_settings,
        "seed": config.seed,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "xi-api-key": credential,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    open_url = transport or urllib.request.urlopen
    try:
        with open_url(request, timeout=timeout) as response:
            audio = response.read()
    except urllib.error.HTTPError as error:
        # Não leia nem propague o corpo da resposta: ele não é necessário para diagnóstico.
        raise ElevenLabsError(f"ElevenLabs retornou HTTP {error.code}; sem retry automático") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        # O resultado remoto pode ser ambíguo; a Activity também usa uma tentativa única.
        raise ElevenLabsError("Falha de transporte ElevenLabs; reconciliação necessária, sem retry") from None
    if not audio:
        raise ElevenLabsError("ElevenLabs retornou áudio vazio")
    return audio
