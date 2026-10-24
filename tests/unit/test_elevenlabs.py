"""Testes sem rede para o cliente da ElevenLabs."""
from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from pqbr.integrations.elevenlabs import (
    CREDENTIAL_ENV,
    VOICE_CONFIG_PATH,
    ElevenLabsError,
    SynthesisNotAuthorized,
    load_voice_config,
    synthesize,
)


class MockResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return self.body


class ElevenLabsClientTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp.name) / "voice.json"
        self.config = json.loads(VOICE_CONFIG_PATH.read_text(encoding="utf-8"))
        self.config["runtime_integrated"] = True
        self.config["generation_authorized"] = True
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_runtime_gate_blocks_before_transport(self):
        self.config["generation_authorized"] = False
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")
        transport = Mock()
        with patch.dict(os.environ, {CREDENTIAL_ENV: "fake-test-key"}):
            with self.assertRaises(SynthesisNotAuthorized):
                synthesize("Texto de teste", config_path=self.config_path, transport=transport)
        transport.assert_not_called()

    def test_request_uses_only_the_selected_voice_model_and_settings(self):
        response = MockResponse(b"mock-mp3-data")
        transport = Mock(return_value=response)
        with patch.dict(os.environ, {CREDENTIAL_ENV: "fake-test-key"}):
            audio = synthesize(
                "Olá, Brasil!", config_path=self.config_path, transport=transport
            )

        self.assertEqual(audio, b"mock-mp3-data")
        request, = transport.call_args.args
        self.assertEqual(request.get_method(), "POST")
        self.assertTrue(request.full_url.startswith(
            "https://api.elevenlabs.io/v1/text-to-speech/xcNJswC7UcxsIiCuih19?"
        ))
        self.assertEqual(request.headers.get("Xi-api-key"), "fake-test-key")
        self.assertEqual(request.headers.get("Accept"), "audio/mpeg")
        self.assertNotIn("fake-test-key", request.full_url)
        query = request.full_url.split("?", 1)[1]
        self.assertEqual(query, "output_format=mp3_44100_128")
        body = json.loads(request.data)
        self.assertEqual(body["text"], "Olá, Brasil!")
        self.assertEqual(body["model_id"], "eleven_v3")
        self.assertEqual(body["seed"], 42)
        self.assertEqual(body["voice_settings"], {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
            "speed": 1.0,
        })

    def test_missing_key_fails_without_transport(self):
        transport = Mock()
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ElevenLabsError, "não está configurada"):
                synthesize("Texto", config_path=self.config_path, transport=transport)
        transport.assert_not_called()

    def test_http_error_is_sanitized_and_not_retried(self):
        error = HTTPError(
            "https://api.elevenlabs.io/v1/text-to-speech/id",
            401,
            "Unauthorized",
            {},
            io.BytesIO(b"provider response fake-test-key"),
        )
        transport = Mock(side_effect=error)
        with patch.dict(os.environ, {CREDENTIAL_ENV: "fake-test-key"}):
            with self.assertRaises(ElevenLabsError) as caught:
                synthesize("Texto", config_path=self.config_path, transport=transport)
        self.assertEqual(str(caught.exception), "ElevenLabs retornou HTTP 401; sem retry automático")
        self.assertNotIn("fake-test-key", str(caught.exception))
        self.assertNotIn("provider response", str(caught.exception))
        transport.assert_called_once()

    def test_invalid_voice_config_is_rejected(self):
        self.config["voice"]["voice_id"] = ""
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")
        with self.assertRaises(ElevenLabsError):
            load_voice_config(self.config_path)


if __name__ == "__main__":
    unittest.main()
