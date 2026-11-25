#!/bin/bash
# Valida la configuración de Ruist OS sin compilar la ISO ni necesitar red.
# Uso: tools/check-config.sh

set -u
cd "$(dirname "$0")/.." || exit 1
ERRORES=0

fallo() {
    printf 'ERROR: %s\n' "$1"
    ERRORES=$((ERRORES + 1))
}

echo "Comprobando scripts de shell..."
for f in config/hooks/live/*.hook.chroot config/includes.chroot/usr/local/bin/* config/includes.chroot/usr/local/libexec/*; do
    [ -f "$f" ] || continue
    [ -L "$f" ] && continue
    interprete=$(head -n 1 "$f")
    case "$interprete" in
        *bash*) bash -n "$f" || fallo "sintaxis en $f" ;;
        *"/bin/sh"*|*" sh"*) sh -n "$f" || fallo "sintaxis en $f" ;;
        *python3*) python3 -c 'import ast, pathlib, sys; ast.parse(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))' "$f" \
            || fallo "sintaxis Python en $f" ;;
        *) fallo "shebang no reconocido o ausente en $f" ;;
    esac
    [ -x "$f" ] || fallo "$f no es ejecutable"
done

echo "Comprobando XML..."
while IFS= read -r -d '' f; do
    python3 -c 'import sys, xml.dom.minidom as m; m.parse(sys.argv[1])' "$f" 2>/dev/null \
        || fallo "XML mal formado en $f"
done < <(find config -type f -name '*.xml' -print0)

echo "Comprobando JSON..."
while IFS= read -r -d '' f; do
    python3 -c 'import sys, json; json.load(open(sys.argv[1], encoding="utf-8"))' "$f" 2>/dev/null \
        || fallo "JSON mal formado en $f"
done < <(find config -type f -name '*.json' -print0)

echo "Comprobando listas de paquetes..."
if ! find config/package-lists -maxdepth 1 -type f -name '*.list.chroot' -print -quit | grep -q .; then
    fallo "no hay listas *.list.chroot en config/package-lists"
fi
for f in config/package-lists/*.list.chroot config/includes.chroot/usr/share/ruist/profiles/*.list.chroot config/includes.chroot/usr/share/ruist/store/apt-packages.list; do
    [ -f "$f" ] || continue
    if awk '/^[[:space:]]*#/ || /^[[:space:]]*$/ { next }
            /[[:space:]]/ { found=1; exit }
            END { exit !found }' "$f"; then
        fallo "$f contiene espacios en una línea de paquete (usa un paquete por línea)"
    fi
done

echo "Comprobando archivos obligatorios..."
for f in config/bootstrap config/chroot config/binary config/common config/source \
         config/archives/debian.list.chroot \
         config/includes.chroot/etc/calamares/settings.conf \
         config/includes.chroot/etc/calamares/modules/packages-extra.conf \
         config/includes.chroot/etc/calamares/modules/desktop-choice.conf \
         config/includes.chroot/usr/local/bin/ruist-kernel \
         config/includes.chroot/usr/share/ruist/store/apt-packages.list \
         config/includes.chroot/usr/share/ruist/profiles/universal.list.chroot \
         config/includes.chroot/usr/share/ruist/profiles/gaming.list.chroot \
         config/includes.chroot/usr/share/ruist/profiles/development.list.chroot \
         config/includes.chroot/usr/share/ruist/profiles/architecture.list.chroot \
         config/includes.chroot/usr/share/ruist/profiles/productivity.list.chroot \
         config/includes.chroot/usr/share/ruist/profiles/desktop-plasma.list.chroot \
         config/includes.chroot/usr/share/ruist/profiles/desktop-lxqt.list.chroot; do
    [ -f "$f" ] || fallo "falta $f"
done
[ -d config/package-lists ] || fallo "falta el directorio config/package-lists"

echo "Comprobando instalación offline de Calamares..."
for modulo in packagechooser@desktop packagechooser@appearance packagechooser@applications shellprocess@cleanup shellprocess@preferences packages@optional; do
    grep -Fq -- "$modulo" config/includes.chroot/etc/calamares/settings.conf \
        || fallo "settings.conf debe incluir el módulo $modulo"
done
for clave in skip_if_no_internet update_db update_system; do
    grep -Eq "^[[:space:]]*$clave:" config/includes.chroot/etc/calamares/modules/packages-extra.conf \
        || fallo "packages-extra.conf debe definir $clave"
done
grep -Eq '^[[:space:]]*skip_if_no_internet:[[:space:]]*true([[:space:]]*(#.*)?)?$' \
    config/includes.chroot/etc/calamares/modules/packages-extra.conf \
    || fallo "packages-extra.conf debe omitir instalaciones opcionales cuando no haya Internet"
grep -Eq '^[[:space:]]*update_db:[[:space:]]*true([[:space:]]*(#.*)?)?$' \
    config/includes.chroot/etc/calamares/modules/packages-extra.conf \
    || fallo "packages-extra.conf debe actualizar los índices APT para los escritorios opcionales"

if [ "${RUIST_SKIP_YAML_VALIDATION:-0}" = 1 ]; then
    echo "Validación YAML completa omitida en la fixture de regresión."
elif python3 -c 'import yaml' >/dev/null 2>&1; then
    python3 - <<'PY' || fallo "configuración YAML o selección de escritorio de Calamares no válida"
from pathlib import Path
import yaml

root = Path("config/includes.chroot/etc/calamares")
settings = yaml.safe_load((root / "settings.conf").read_text(encoding="utf-8"))
optional = yaml.safe_load((root / "modules/packages-extra.conf").read_text(encoding="utf-8"))
chooser = yaml.safe_load((root / "modules/desktop-choice.conf").read_text(encoding="utf-8"))
assert optional["skip_if_no_internet"] is True and optional["update_db"] is True
assert optional["update_system"] is False
instances = {(item["module"], item["id"]): item["config"] for item in settings["instances"]}
assert instances[("packagechooser", "desktop")] == "desktop-choice.conf"
assert instances[("packages", "optional")] == "packages-extra.conf"
phases = settings["sequence"]
assert instances[("packagechooser", "appearance")] == "appearance-choice.conf"
assert instances[("packagechooser", "applications")] == "application-choice.conf"
assert instances[("shellprocess", "cleanup")] == "ruist-cleanup.conf"
assert instances[("shellprocess", "preferences")] == "ruist-preferences.conf"
show = phases[0]["show"]
for choice in ("desktop", "appearance", "applications"):
    assert show.index(f"packagechooser@{choice}") < show.index("partition")
jobs = phases[1]["exec"]
assert jobs.index("unpackfs") < jobs.index("shellprocess@cleanup") < jobs.index("users")
assert jobs.index("sources-final") < jobs.index("packages@optional") < jobs.index("shellprocess@preferences")
welcome = yaml.safe_load((root / "modules/welcome.conf").read_text(encoding="utf-8"))["requirements"]
assert "internet" in welcome["check"] and "internet" not in welcome["required"]
appearance = yaml.safe_load((root / "modules/appearance-choice.conf").read_text(encoding="utf-8"))
assert appearance["method"] == "legacy" and appearance["default"] == "oscuro"
assert {item["id"] for item in appearance["items"]} == {"oscuro", "claro"}
applications = yaml.safe_load((root / "modules/application-choice.conf").read_text(encoding="utf-8"))
assert applications["method"] == "packages" and applications["mode"] == "optionalmultiple"
assert all(item["packages"] for item in applications["items"])
assert chooser["method"] == "packages" and chooser["default"] == "xfce"
items = {item["id"]: item for item in chooser["items"]}
assert set(items) == {"xfce", "plasma", "lxqt"}
assert items["xfce"]["packages"] == []
for desktop in ("plasma", "lxqt"):
    manifest = Path(f"config/includes.chroot/usr/share/ruist/profiles/desktop-{desktop}.list.chroot")
    packages = [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.lstrip().startswith("#")]
    assert items[desktop]["packages"] == packages
PY
else
    echo "PyYAML no está instalado; se aplican las comprobaciones estáticas de Calamares."
fi

if [ "$ERRORES" -gt 0 ]; then
    printf 'Se han encontrado %s problema(s).\n' "$ERRORES"
    exit 1
fi

echo "Todo correcto."
