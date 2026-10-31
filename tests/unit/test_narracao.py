"""Testes da Activity TTS sem chamadas externas."""
from __future__ import annotations

import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from temporalio.exceptions import ApplicationError

from pqbr.integrations.elevenlabs import VOICE_CONFIG_PATH
from pqbr.workflows import narracao


class NarracaoActivityTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config_path = self.root / "voice.json"
        self.output_dir = self.root / "out"
        self.config = json.loads(VOICE_CONFIG_PATH.read_text(encoding="utf-8"))
        self.config["runtime_integrated"] = True
        self.config["generation_authorized"] = False
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")
        self.env = patch.dict(os.environ, {
            "PQBR_VOICE_CONFIG": str(self.config_path),
            "PQBR_TTS_DIR": str(self.output_dir),
            "ELEVENLABS_API_KEY": "fake-test-key",
        })
        self.env.start()
        self.addCleanup(self.env.stop)

    def tearDown(self):
        self.temp.cleanup()

    async def test_current_config_blocks_without_audio_or_network(self):
        with patch.object(narracao, "synthesize") as synthesize:
            with self.assertRaises(ApplicationError) as caught:
                await narracao.gerar_narracao("PQBR-EP0001", ["fala um", "fala dois"])
        self.assertEqual(caught.exception.type, "TTSDesautorizado")
        synthesize.assert_not_called()
        self.assertFalse(self.output_dir.exists())

    async def test_audio_saved_locally_and_reused_idempotently(self):
        self.config["generation_authorized"] = True
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")
        with patch.object(narracao, "synthesize", return_value=b"mock-audio-bytes") as synthesize:
            first = await narracao.gerar_narracao("PQBR-EP0002", ["fala um", "fala dois"])
            second = await narracao.gerar_narracao("PQBR-EP0002", ["fala um", "fala dois"])

        self.assertFalse(first.reutilizado)
        self.assertTrue(second.reutilizado)
        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(Path(first.arquivo).read_bytes(), b"mock-audio-bytes")
        self.assertEqual(stat.S_IMODE(Path(first.arquivo).stat().st_mode), 0o600)
        synthesize.assert_called_once()
        manifest = json.loads((self.output_dir / "PQBR-EP0002.json").read_text(encoding="utf-8"))
        self.assertNotIn("text", manifest)
        self.assertNotIn("fake-test-key", json.dumps(manifest))

    async def test_orphan_audio_requires_reconciliation_not_regeneration(self):
        self.config["generation_authorized"] = True
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")
        self.output_dir.mkdir(mode=0o700)
        (self.output_dir / "PQBR-EP0003.mp3").write_bytes(b"possibly-generated-audio")
        with patch.object(narracao, "synthesize") as synthesize:
            with self.assertRaises(ApplicationError) as caught:
                await narracao.gerar_narracao("PQBR-EP0003", ["fala um", "fala dois"])
        self.assertEqual(caught.exception.type, "TTSArtifactAmbiguous")
        synthesize.assert_not_called()

    async def test_invalid_episode_id_fails_closed(self):
        with patch.object(narracao, "synthesize") as synthesize:
            with self.assertRaises(ApplicationError) as caught:
                await narracao.gerar_narracao("../../bad", ["fala um"])
        self.assertEqual(caught.exception.type, "TTSInputInvalid")
        synthesize.assert_not_called()


if __name__ == "__main__":
    unittest.main()
