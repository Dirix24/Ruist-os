import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_TOOL = ROOT / "config/includes.chroot/usr/local/bin/ruist-desktop"
OPTIONS = {
    "fondo": "xfdesktop-settings",
    "apariencia": "xfce4-appearance-settings",
    "efectos": "xfwm4-tweaks-settings",
    "pantalla": "xfce4-display-settings",
}


class RuistDesktopTests(unittest.TestCase):
    def test_menu_actions_open_the_matching_xfce_settings_tool(self):
        for option, command in OPTIONS.items():
            with self.subTest(option=option), tempfile.TemporaryDirectory() as temporary:
                bindir = Path(temporary)
                zenity = bindir / "zenity"
                zenity.write_text("#!/bin/sh\nprintf '%s\\n' \"$RUIST_DESKTOP_OPTION\"\n", encoding="utf-8")
                zenity.chmod(0o755)
                action = bindir / command
                action.write_text("#!/bin/sh\nprintf '%s\\n' \"${0##*/}\" > \"$RUIST_DESKTOP_LOG\"\n", encoding="utf-8")
                action.chmod(0o755)
                log = bindir / "launched-tool"
                env = os.environ.copy()
                env.update({
                    "PATH": f"{bindir}:{env['PATH']}",
                    "RUIST_DESKTOP_OPTION": option,
                    "RUIST_DESKTOP_LOG": str(log),
                })

                result = subprocess.run([str(DESKTOP_TOOL)], env=env, text=True, capture_output=True, check=False)

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(log.read_text(encoding="utf-8").strip(), command)


if __name__ == "__main__":
    unittest.main()
