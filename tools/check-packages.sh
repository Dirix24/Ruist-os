#!/bin/bash
# Run with Debian Trixie indexes for main, contrib, non-free and non-free-firmware.

set -eu
cd "$(dirname "$0")/.."

python3 - <<'PYAML'
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sources = defaultdict(list)
config = Path("config")
ruist = config / "includes.chroot/usr/share/ruist"
paths = [
    *sorted((config / "package-lists").glob("*.list.chroot")),
    *sorted((ruist / "profiles").glob("*.list.chroot")),
    ruist / "store/apt-packages.list",
]
for path in paths:
    for line in path.read_text(encoding="utf-8").splitlines():
        package = line.split("#", 1)[0].strip()
        if package:
            sources[package].append(path.name)

modules = config / "includes.chroot/etc/calamares/modules"
for name in ("desktop-choice.conf", "application-choice.conf"):
    choices = yaml.safe_load((modules / name).read_text(encoding="utf-8"))
    for item in choices["items"]:
        for package in item["packages"]:
            sources[package].append(name)

for package in sources:
    if not re.fullmatch(r"[a-z0-9][a-z0-9+.-]*", package):
        sys.exit(f"Nombre de paquete no válido: {package}")

# One call reads the indexes once. Compare exact names since APT can also
# resolve virtual packages and patterns that are absent from the indexes.
result = subprocess.run(
    ["apt-cache", "show", "--no-all-versions", "--", *sorted(sources)],
    text=True, capture_output=True, check=False,
)
available = set(re.findall(r"^Package: (\S+)$", result.stdout, re.MULTILINE))
missing = sorted(sources.keys() - available)
for package in missing:
    print(f"FALTA: {package} (en {', '.join(sources[package])})")
if missing or result.returncode:
    if not available or not missing:
        print(result.stderr, file=sys.stderr, end="")
    sys.exit(1)
print("Todos los paquetes existen en Trixie.")
PYAML
