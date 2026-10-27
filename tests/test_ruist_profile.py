import importlib.util
import json
from importlib.machinery import SourceFileLoader
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PROFILE_TOOL = ROOT / "config/includes.chroot/usr/local/bin/ruist-profile"
SPEC = importlib.util.spec_from_loader("ruist_profile", SourceFileLoader("ruist_profile", str(PROFILE_TOOL)))
profile = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(profile)


class RuistProfileTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.profile_dir = self.root / "profiles"
        self.state_dir = self.root / "state"
        self.profile_dir.mkdir()
        self.write_profile("gaming", "gamemode\nmangohud\n")
        self.write_profile("development", "gamemode\ngit\n")
        self.profile_paths = (
            patch.object(profile, "PROFILE_DIR", self.profile_dir),
            patch.object(profile, "STATE_DIR", self.state_dir),
        )
        for context in self.profile_paths:
            context.start()
            self.addCleanup(context.stop)

    def write_profile(self, name, contents):
        (self.profile_dir / f"{name}.list.chroot").write_text(contents, encoding="utf-8")

    def test_manifest_rejects_non_package_content(self):
        self.write_profile("gaming", "gamemode;touch /tmp/injected\n")
        with self.assertRaises(ValueError):
            profile.load_manifest("gaming")

    def test_install_records_only_missing_packages_as_owned(self):
        with patch.object(profile, "installed", side_effect=lambda pkg: pkg == "gamemode"), \
                patch.object(profile, "run_apt", return_value=0) as apt:
            self.assertEqual(profile.install_profiles(["gaming"]), 0)
        apt.assert_called_once_with("install", ["mangohud"])
        state = json.loads((self.state_dir / "gaming.json").read_text(encoding="utf-8"))
        self.assertEqual(state["active"], ["gamemode", "mangohud"])
        self.assertEqual(state["owned"], ["mangohud"])

    def test_shared_owned_package_transfers_to_remaining_profile(self):
        with patch.object(profile, "installed", side_effect=lambda pkg: pkg == "mangohud"), patch.object(profile, "run_apt", return_value=0):
            profile.install_profiles(["gaming"])
        with patch.object(profile, "installed", side_effect=lambda pkg: pkg != "git"), patch.object(profile, "run_apt", return_value=0):
            profile.install_profiles(["development"])

        with patch.object(profile, "installed", return_value=True), patch.object(profile, "run_apt", return_value=0) as apt:
            self.assertEqual(profile.remove_profile("gaming"), 0)
        apt.assert_not_called()
        development = json.loads((self.state_dir / "development.json").read_text(encoding="utf-8"))
        self.assertIn("gamemode", development["owned"])

        with patch.object(profile, "installed", return_value=True), patch.object(profile, "run_apt", return_value=0) as apt:
            self.assertEqual(profile.remove_profile("development"), 0)
        apt.assert_called_once_with("remove", ["gamemode", "git"])
        self.assertFalse((self.state_dir / "development.json").exists())


if __name__ == "__main__":
    unittest.main()
