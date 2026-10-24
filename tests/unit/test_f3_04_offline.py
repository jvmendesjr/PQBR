"""Testes offline F3-04: somente dados sintéticos; nenhuma credencial."""
import hashlib
import importlib.util
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
CANDIDATO = Path(__file__).with_name("planejar.py")
SCRIPT = CANDIDATO if CANDIDATO.exists() else ROOT / "scripts/backup_offsite/planejar.py"
spec = importlib.util.spec_from_file_location("f3_04_planejar", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PlanejamentoOffline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="pqbr-f3-04-fixtures-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.arquivos = []
        for origem, prefixo in mod.ORIGENS.items():
            pasta = self.root / origem
            pasta.mkdir(mode=0o700)
            arquivo = pasta / f"{prefixo}-20261017-0345.dump"
            arquivo.write_bytes(b"F3-04 DADOS SINTETICOS SEM SQL OU SEGREDOS\n")
            arquivo.chmod(0o600)
            self.arquivos.append(arquivo)
        for alvo in ("socket.socket", "socket.create_connection", "subprocess.Popen", "subprocess.run", "os.system"):
            p = patch(alvo, side_effect=AssertionError("Efeito externo proibido"))
            p.start()
            self.addCleanup(p.stop)

    def plano(self):
        return mod.planejar(self.root)

    def test_duas_origens_e_hash(self):
        plano = self.plano()
        self.assertEqual(len(plano["itens"]), 2)
        self.assertEqual(plano["estado"], "PLANO_OFFLINE_NAO_AUTORIZA_ENVIO")
        for item in plano["itens"]:
            dado = (self.root / item["origem"] / item["nome"]).read_bytes()
            self.assertEqual(item["sha256"], hashlib.sha256(dado).hexdigest())
            self.assertEqual(item["bytes"], len(dado))
            self.assertEqual(item["destino_logico"], f'PQBR/backups-db/{item["origem"]}/{item["nome"]}')

    def test_sem_escrita_ou_exclusao(self):
        antes = {str(p): (p.read_bytes(), p.stat().st_mtime_ns, p.stat().st_mode) for p in self.arquivos}
        self.plano()
        depois = {str(p): (p.read_bytes(), p.stat().st_mtime_ns, p.stat().st_mode) for p in self.arquivos}
        self.assertEqual(antes, depois)
        self.assertEqual(len(list(self.root.rglob("*"))), 4)

    def test_repeticao_estavel(self):
        self.assertEqual(self.plano()["itens"], self.plano()["itens"])

    def test_retencao_nao_definida(self):
        self.assertEqual(self.plano()["retencao_remota"], "PENDENTE_JOSE_SEM_EXCLUSAO")

    def test_ignora_tmp_e_log(self):
        for nome in ("pqbr-20261017-0400.dump.tmp", "backup.log", ".env", "rclone.conf"):
            (self.root / "pqbr-db" / nome).write_text("NAO LER")
        self.assertEqual(len(self.plano()["itens"]), 2)

    def test_nao_le_arquivos_ignorados(self):
        link = self.root / "pqbr-db" / "ignorado.tmp"
        link.symlink_to("/arquivo-inexistente")
        self.assertEqual(len(self.plano()["itens"]), 2)

    def test_pasta_ausente(self):
        with self.assertRaises(OSError):
            mod.planejar(self.root / "ausente")

    def test_origem_ausente(self):
        self.arquivos[0].unlink()
        self.arquivos[0].parent.rmdir()
        with self.assertRaises(OSError):
            self.plano()

    def test_sem_dump_final(self):
        self.arquivos[0].rename(self.arquivos[0].with_suffix(".dump.tmp"))
        with self.assertRaises(ValueError):
            self.plano()

    def test_vazio(self):
        self.arquivos[0].write_bytes(b"")
        with self.assertRaises(ValueError):
            self.plano()

    def test_nome_invalido(self):
        self.arquivos[0].rename(self.arquivos[0].with_name("outro.dump"))
        with self.assertRaises(ValueError):
            self.plano()

    def test_data_invalida(self):
        self.arquivos[0].rename(self.arquivos[0].with_name("pqbr-20260230-0345.dump"))
        with self.assertRaises(ValueError):
            self.plano()

    def test_hora_invalida(self):
        self.arquivos[0].rename(self.arquivos[0].with_name("pqbr-20261017-2500.dump"))
        with self.assertRaises(ValueError):
            self.plano()

    def test_prefixo_de_outra_origem(self):
        self.arquivos[0].rename(self.arquivos[0].with_name("hindsight-20261017-0345.dump"))
        with self.assertRaises(ValueError):
            self.plano()

    def test_arquivo_publico(self):
        self.arquivos[0].chmod(0o644)
        with self.assertRaises(ValueError):
            self.plano()

    def test_pasta_publica(self):
        self.arquivos[0].parent.chmod(0o755)
        with self.assertRaises(ValueError):
            self.plano()

    def test_raiz_publica(self):
        self.root.chmod(0o755)
        with self.assertRaises(ValueError):
            self.plano()

    def test_link_arquivo(self):
        self.arquivos[0].unlink()
        self.arquivos[0].symlink_to(self.arquivos[1])
        with self.assertRaises(ValueError):
            self.plano()

    def test_link_pasta(self):
        outra = self.root / "pqbr-db-real"
        (self.root / "pqbr-db").rename(outra)
        (self.root / "pqbr-db").symlink_to(outra, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.plano()

    def test_link_ancestral(self):
        link = self.root / "atalho"
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            mod.planejar(link)

    def test_diretorio_com_nome_dump(self):
        self.arquivos[0].unlink()
        self.arquivos[0].mkdir(mode=0o700)
        with self.assertRaises(ValueError):
            self.plano()

    def test_dono_divergente(self):
        with patch.object(mod.os, "getuid", return_value=os.getuid() + 1):
            with self.assertRaises(ValueError):
                self.plano()

    def test_mudanca_durante_leitura(self):
        original = mod.hashlib.sha256
        arquivo = self.arquivos[0]
        class Mutante:
            def __init__(self):
                self.real = original()
            def update(self, bloco):
                self.real.update(bloco)
                with arquivo.open("ab") as saida:
                    saida.write(b"alterado")
            def hexdigest(self):
                return self.real.hexdigest()
        # Mutar uma vez evita crescimento infinito durante a leitura.
        objeto = Mutante()
        original_update = objeto.update
        def uma_vez(bloco):
            objeto.update = objeto.real.update
            original_update(bloco)
        objeto.update = uma_vez
        with patch.object(mod.hashlib, "sha256", return_value=objeto):
            with self.assertRaises(ValueError):
                self.plano()

    def test_manifesto_nao_contem_payload_ou_caminho_absoluto(self):
        import json
        texto = json.dumps(self.plano())
        self.assertNotIn("DADOS SINTETICOS", texto)
        self.assertNotIn(str(self.root), texto)


if __name__ == "__main__":
    unittest.main()
