import runpy
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


CHROOT = Path(__file__).resolve().parents[1] / "config/includes.chroot"
PREFERENCES = runpy.run_path(str(CHROOT / "usr/local/libexec/ruist-install-preferences"))


class InstallerPreferencesTests(unittest.TestCase):
    def test_light_theme_applies_to_installed_xfce_defaults(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            xfce = Path("etc/xdg/xfce4")
            shutil.copytree(CHROOT / xfce, root / xfce)

            PREFERENCES["set_appearance"](root, "claro")

            channels = root / xfce / "xfconf/xfce-perchannel-xml"
            gtk = ET.parse(channels / "xsettings.xml")
            self.assertEqual(gtk.find(".//property[@name='ThemeName']").get("value"), "Arc")
            panel = ET.parse(root / xfce / "panel/default.xml")
            self.assertEqual(panel.find(".//property[@name='dark-mode']").get("value"), "false")

    def test_selects_only_installed_x11_session_and_falls_back_to_xfce(self):
        for session in ("xfce", "plasmax11", "lxqt"):
            with self.subTest(session=session), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                sessions = root / "usr/share/xsessions"
                sessions.mkdir(parents=True)
                if session != "xfce":
                    (sessions / f"{session}.desktop").touch()
                config = root / "etc/lightdm/lightdm.conf.d"
                config.mkdir(parents=True)

                PREFERENCES["set_session"](root)

                self.assertEqual(
                    (config / "90-ruist-session.conf").read_text(encoding="utf-8"),
                    f"[Seat:*]\nuser-session={session}\n",
                )
