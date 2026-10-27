import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRIVERS_TOOL = ROOT / "config/includes.chroot/usr/local/bin/ruist-drivers"


class RuistDriversTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bindir = self.root / "bin"
        self.bindir.mkdir()
        self.log = self.root / "commands.log"
        self.install_stub("id", '#!/bin/sh\nprintf "0\\n"\n')
        self.install_stub("apt-get", '#!/bin/sh\nprintf "apt-get %s\\n" "$*" >> "$MOCK_LOG"\n')

    def install_stub(self, name, contents):
        path = self.bindir / name
        path.write_text(contents, encoding="utf-8")
        path.chmod(0o755)

    def run_tool(self, *args):
        env = os.environ.copy()
        env.update({"PATH": f"{self.bindir}:{env['PATH']}", "MOCK_LOG": str(self.log)})
        return subprocess.run([str(DRIVERS_TOOL), *args], env=env, text=True, capture_output=True, check=False)

    def test_rejects_unrecognized_package_without_running_apt(self):
        result = self.run_tool("paquetes", "--help")
        self.assertEqual(result.returncode, 2)
        self.assertIn("fuera de la lista permitida", result.stderr)
        self.assertFalse(self.log.exists())

    def test_rejects_both_vendor_microcodes(self):
        result = self.run_tool("paquetes", "intel-microcode", "amd64-microcode")
        self.assertEqual(result.returncode, 2)
        self.assertIn("No se pueden instalar microcódigos", result.stderr)
        self.assertFalse(self.log.exists())

    def test_apt_preview_confirmation_is_preserved(self):
        result = self.run_tool("nvidia", "nvidia-driver")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.log.read_text(encoding="utf-8").splitlines(),
            ["apt-get update", "apt-get install linux-headers-amd64 dkms nvidia-driver"],
        )

    def test_broadcom_dkms_gets_matching_kernel_headers(self):
        result = self.run_tool("paquetes", "broadcom-sta-dkms")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.log.read_text(encoding="utf-8").splitlines(),
            ["apt-get update", "apt-get install linux-headers-amd64 dkms broadcom-sta-dkms"],
        )


if __name__ == "__main__":
    unittest.main()
