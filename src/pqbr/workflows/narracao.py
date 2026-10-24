"""Activity Temporal do TTS PQBR: artefatos locais, gate fail-closed e sem retry."""
from __future__ import annotations

import asyncio
import fcntl
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict
from temporalio import activity
from temporalio.exceptions import ApplicationError

from ..integrations.elevenlabs import (
    ElevenLabsError,
    SynthesisNotAuthorized,
    VoiceConfigError,
    load_voice_config,
    synthesize,
    voice_config_path,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = ROOT / "runtime" / "narracoes"
OUTPUT_DIR_ENV = "PQBR_TTS_DIR"


class ResultadoNarracao(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    episodio_id: str
    arquivo: str
    sha256: str
    size_bytes: int
    voice_id: str
    model_id: str
    reutilizado: bool = False


def _request_hash(episodio_id: str, text: str, config: Any) -> str:
    payload = {
        "episodio_id": episodio_id,
        "text": text,
        "provider": config.provider,
        "voice_id": config.voice_id,
        "model_id": config.model_id,
        "seed": config.seed,
        "voice_settings": config.voice_settings,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _manifest_result(manifest_path: Path, audio_path: Path, expected_request_hash: str, episodio_id: str, config: Any) -> ResultadoNarracao:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        audio = audio_path.read_bytes()
    except (OSError, json.JSONDecodeError):
        raise ApplicationError(
            "Artefato TTS incompleto ou inválido; reconciliação manual necessária",
            type="TTSArtifactAmbiguous",
            non_retryable=True,
        ) from None
    actual_hash = hashlib.sha256(audio).hexdigest()
    if (
        manifest.get("request_sha256") != expected_request_hash
        or manifest.get("voice_id") != config.voice_id
        or manifest.get("model_id") != config.model_id
        or manifest.get("audio_sha256") != actual_hash
        or manifest.get("size_bytes") != len(audio)
    ):
        raise ApplicationError(
            "Artefato TTS não corresponde à solicitação; reconciliação manual necessária",
            type="TTSArtifactAmbiguous",
            non_retryable=True,
        )
    return ResultadoNarracao(
        episodio_id=episodio_id,
        arquivo=str(audio_path),
        sha256=actual_hash,
        size_bytes=len(audio),
        voice_id=config.voice_id,
        model_id=config.model_id,
        reutilizado=True,
    )


def _atomic_write(path: Path, content: bytes) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _gerar_sync(episodio_id: str, falas: list[str]) -> ResultadoNarracao:
    if not re.fullmatch(r"PQBR-EP\d{4}", episodio_id):
        raise ApplicationError("episodio_id inválido para narração", type="TTSInputInvalid", non_retryable=True)
    if not isinstance(falas, list) or not falas or any(not isinstance(fala, str) for fala in falas):
        raise ApplicationError("falas inválidas para narração", type="TTSInputInvalid", non_retryable=True)
    text = "\n".join(falas).strip()
    if not text:
        raise ApplicationError("roteiro sem texto para narração", type="TTSInputInvalid", non_retryable=True)

    config_path = voice_config_path()
    try:
        config = load_voice_config(config_path)
    except VoiceConfigError as error:
        raise ApplicationError(str(error), type="TTSConfigInvalid", non_retryable=True) from None

    base_dir = Path(os.environ.get(OUTPUT_DIR_ENV, str(OUTPUT_DIR)))
    audio_path = base_dir / f"{episodio_id}.mp3"
    manifest_path = base_dir / f"{episodio_id}.json"
    expected_request_hash = _request_hash(episodio_id, text, config)

    if manifest_path.exists():
        return _manifest_result(manifest_path, audio_path, expected_request_hash, episodio_id, config)
    if audio_path.exists():
        raise ApplicationError(
            "Áudio TTS sem manifesto; reconciliação manual necessária",
            type="TTSArtifactAmbiguous",
            non_retryable=True,
        )
    if not config.runtime_integrated or not config.generation_authorized:
        raise ApplicationError(
            "Síntese TTS bloqueada pelo gate de autorização",
            type="TTSDesautorizado",
            non_retryable=True,
        )

    base_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(base_dir, 0o700)
    lock_path = base_dir / f".{episodio_id}.lock"
    with lock_path.open("a+b") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        # A segunda execução concorrente reaproveita o artefato sem nova chamada paga.
        if manifest_path.exists():
            return _manifest_result(manifest_path, audio_path, expected_request_hash, episodio_id, config)
        if audio_path.exists():
            raise ApplicationError(
                "Áudio TTS sem manifesto; reconciliação manual necessária",
                type="TTSArtifactAmbiguous",
                non_retryable=True,
            )
        try:
            audio = synthesize(text, config_path=config_path)
        except SynthesisNotAuthorized as error:
            raise ApplicationError(str(error), type="TTSDesautorizado", non_retryable=True) from None
        except VoiceConfigError as error:
            raise ApplicationError(str(error), type="TTSConfigInvalid", non_retryable=True) from None
        except ElevenLabsError as error:
            raise ApplicationError(str(error), type="ElevenLabsFailure", non_retryable=True) from None
        except OSError:
            raise ApplicationError(
                "Falha ao persistir resposta TTS; reconciliação necessária",
                type="TTSArtifactAmbiguous",
                non_retryable=True,
            ) from None

        audio_sha256 = hashlib.sha256(audio).hexdigest()
        manifest = {
            "episodio_id": episodio_id,
            "provider": config.provider,
            "voice_id": config.voice_id,
            "model_id": config.model_id,
            "request_sha256": expected_request_hash,
            "audio_sha256": audio_sha256,
            "size_bytes": len(audio),
        }
        try:
            _atomic_write(audio_path, audio)
            _atomic_write(manifest_path, json.dumps(manifest, sort_keys=True).encode("utf-8"))
        except OSError:
            raise ApplicationError(
                "Falha ao persistir resposta TTS; reconciliação necessária",
                type="TTSArtifactAmbiguous",
                non_retryable=True,
            ) from None
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    return ResultadoNarracao(
        episodio_id=episodio_id,
        arquivo=str(audio_path),
        sha256=audio_sha256,
        size_bytes=len(audio),
        voice_id=config.voice_id,
        model_id=config.model_id,
        reutilizado=False,
    )


@activity.defn
async def gerar_narracao(episodio_id: str, falas: list[str]) -> ResultadoNarracao:
    """Gera somente após os gates; erros/ambiguidades nunca são repetidos automaticamente."""
    return await asyncio.to_thread(_gerar_sync, episodio_id, falas)
