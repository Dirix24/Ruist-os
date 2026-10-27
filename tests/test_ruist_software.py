import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_TOOL = ROOT / "config/includes.chroot/usr/local/bin/ruist-software"


class RuistSoftwareTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bindir = self.root / "bin"
        self.bindir.mkdir()
        self.log = self.root / "commands.log"
        self.catalog = self.root / "apt-packages.list"
        self.catalog.write_text(
            (ROOT / "config/includes.chroot/usr/share/ruist/store/apt-packages.list").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        self.install_stub("id", '#!/bin/sh\nprintf "%s\\n" "$MOCK_UID"\n')
        self.install_stub("flatpak", '#!/bin/sh\nprintf "flatpak %s\\n" "$*" >> "$MOCK_LOG"\n')
        self.install_stub("apt-get", '#!/bin/sh\nprintf "apt-get %s\\n" "$*" >> "$MOCK_LOG"\n')

    def install_stub(self, name, source):
        path = self.bindir / name
        path.write_text(source, encoding="utf-8")
        path.chmod(0o755)

    def environment(self, uid):
        env = os.environ.copy()
        env.update({
            "PATH": f"{self.bindir}:{env['PATH']}",
            "MOCK_UID": str(uid),
            "MOCK_LOG": str(self.log),
            "RUIST_APT_CATALOG": str(self.catalog),
        })
        return env

    def run_store(self, *args, uid=1000):
        return subprocess.run([str(STORE_TOOL), *args], env=self.environment(uid), text=True, capture_output=True, check=False)

    def test_flatpak_rejects_shell_metacharacters_before_any_package_operation(self):
        result = self.run_store("flatpak", "org.example.App;touch", "/tmp/ruist-store-injected")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Identificador Flatpak inválido", result.stderr)
        self.assertFalse(self.log.exists())

    def test_valid_flatpak_id_is_passed_as_an_argument(self):
        result = self.run_store("flatpak", "org.example.App")
        self.assertEqual(result.returncode, 0, result.stderr)
        commands = self.log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(commands), 2)
        self.assertTrue(commands[0].startswith("flatpak remote-add "))
        self.assertEqual(commands[1], "flatpak install --user flathub org.example.App")

    def test_apt_catalog_rejects_options_outside_the_store_allowlist(self):
        result = self.run_store("apt", "--help", uid=0)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Paquete fuera del catálogo", result.stderr)
        self.assertFalse(self.log.exists())

    def test_apt_removal_is_allowlisted_and_leaves_confirmation_to_apt(self):
        result = self.run_store("apt-remove", "vlc", uid=0)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.log.read_text(encoding="utf-8").splitlines(), ["apt-get remove vlc"])

    def test_flatpak_removal_is_user_scoped_and_validated(self):
        result = self.run_store("flatpak-remove", "org.example.App")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.log.read_text(encoding="utf-8").splitlines(), ["flatpak uninstall --user org.example.App"])

        self.log.unlink()
        result = self.run_store("flatpak-remove", "org.example.App;false")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.log.exists())


if __name__ == "__main__":
    unittest.main()
