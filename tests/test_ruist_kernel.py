import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KERNEL_TOOL = ROOT / "config/includes.chroot/usr/local/bin/ruist-kernel"


class RuistKernelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bindir = self.root / "bin"
        self.bindir.mkdir()
        self.log = self.root / "commands.log"
        self.install_stub("id", '#!/bin/sh\nprintf "%s\\n" "$MOCK_UID"\n')
        self.install_stub("dpkg", '#!/bin/sh\nif [ "$1" = "--print-architecture" ]; then echo "${MOCK_ARCH:-amd64}"; fi\n')
        self.install_stub("apt-cache", '#!/bin/sh\necho "  Candidate: ${MOCK_CANDIDATE:-6.12.999}"\n')
        self.install_stub("apt-get", '#!/bin/sh\nprintf "apt-get %s\\n" "$*" >> "$MOCK_LOG"\n')

    def install_stub(self, name, source):
        path = self.bindir / name
        path.write_text(source, encoding="utf-8")
        path.chmod(0o755)

    def run_tool(self, *args, **extra):
        env = os.environ.copy()
        env.update({"PATH": f"{self.bindir}:{env['PATH']}", "MOCK_UID": "0", "MOCK_LOG": str(self.log)})
        env.update(extra)
        return subprocess.run([str(KERNEL_TOOL), *args], env=env, text=True, capture_output=True, check=False)

    def test_installs_only_debian_stable_meta_package_and_does_not_remove_older_kernels(self):
        result = self.run_tool("install")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("no se eliminarán", result.stdout)
        self.assertEqual(self.log.read_text(encoding="utf-8").splitlines(), ["apt-get install linux-image-amd64"])

    def test_refuses_when_no_stable_candidate_exists(self):
        result = self.run_tool("install", MOCK_CANDIDATE="(none)")
        self.assertEqual(result.returncode, 1)
        self.assertFalse(self.log.exists())

    def test_rejects_unknown_architecture(self):
        result = self.run_tool("install", MOCK_ARCH="arm64")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.log.exists())


if __name__ == "__main__":
    unittest.main()
