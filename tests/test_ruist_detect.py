import importlib.util
from importlib.machinery import SourceFileLoader
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
MODULE_PATH = ROOT / "config/includes.chroot/usr/local/bin/ruist-detect"
SPEC = importlib.util.spec_from_loader("ruist_detect", SourceFileLoader("ruist_detect", str(MODULE_PATH)))
detect = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(detect)


class RuistDetectTests(unittest.TestCase):
    def test_cpu_and_memory_parsers(self):
        with tempfile.TemporaryDirectory() as temporary:
            cpu = Path(temporary) / "cpuinfo"
            cpu.write_text("model name\t: Example CPU\nflags\t: sse sse2 avx\n", encoding="utf-8")
            mem = Path(temporary) / "meminfo"
            mem.write_text("MemTotal:       4096 kB\nMemAvailable:   1024 kB\n", encoding="utf-8")

            self.assertEqual(detect.cpu_info(cpu)["model"], "Example CPU")
            self.assertEqual(detect.cpu_info(cpu)["flags"], ["avx", "sse", "sse2"])
            self.assertEqual(detect.memory_info(mem), {"total_bytes": 4194304, "available_bytes": 1048576})

    def test_pci_graphics_reports_driver_states_separately(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pci = root / "pci" / "0000:01:00.0"
            pci.mkdir(parents=True)
            (pci / "class").write_text("0x030000", encoding="utf-8")
            (pci / "vendor").write_text("0x10de", encoding="utf-8")
            (pci / "device").write_text("0x1c03", encoding="utf-8")
            (root / "drivers/nouveau").mkdir(parents=True)
            (pci / "driver").symlink_to(root / "drivers/nouveau", target_is_directory=True)
            modules = root / "modules/nouveau"
            modules.mkdir(parents=True)

            def fake_run(args, timeout=8):
                if args[0] == "lspci":
                    return "0000:01:00.0 VGA compatible controller [0300]: NVIDIA Example [10de:1c03]\nKernel modules: nouveau, nvidia"
                if args[0] == "modinfo":
                    return "filename: /lib/modules/example/nouveau.ko"
                return None

            with patch.object(detect, "run", side_effect=fake_run), patch.object(detect.shutil, "which", return_value="/sbin/modinfo"):
                devices = detect.pci_devices(root / "pci", root / "modules")

            self.assertEqual(len(devices), 1)
            gpu = devices[0]
            self.assertTrue(gpu["detected"])
            self.assertEqual(gpu["driver_active"], "nouveau")
            self.assertTrue(gpu["module_loaded"])
            self.assertEqual(gpu["driver_candidates"], ["nouveau", "nvidia"])
            self.assertEqual(gpu["driver_module_status"]["nouveau"], "present_for_running_kernel")

    def test_empty_report_format_is_explicit(self):
        report = {
            "system": {"architecture": "x86_64", "kernel": "test"},
            "cpu": {"model": None},
            "memory": {"total_bytes": None},
            "graphics": [],
            "graphics_verification": {"opengl": "tool_unavailable", "vulkan": "tool_unavailable"},
            "network": [],
            "wireless": {"interfaces": [], "bluetooth_controllers": []},
            "audio": {"pipewire_status": "tool_unavailable", "pulse_server_status": "tool_unavailable"},
        }
        text = detect.format_report(report)
        self.assertIn("No se detectó una GPU", text)
        self.assertIn("detección no equivale a funcionalidad verificada", text)

    def test_software_vulkan_is_not_reported_as_hardware_acceleration(self):
        def fake_run(args, timeout=8):
            if args[0] == "glxinfo":
                return "direct rendering: Yes\nOpenGL renderer string: llvmpipe"
            if args[0] == "vulkaninfo":
                return "deviceType = PHYSICAL_DEVICE_TYPE_CPU\ndeviceName = llvmpipe"
            return None

        with patch.object(detect, "run", side_effect=fake_run), patch.object(detect.shutil, "which", return_value="/usr/bin/tool"):
            result = detect.verify_graphics()
        self.assertEqual(result["opengl"], "not_verified")
        self.assertEqual(result["vulkan"], "software_only")


if __name__ == "__main__":
    unittest.main()
