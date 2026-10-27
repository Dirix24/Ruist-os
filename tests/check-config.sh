#!/bin/bash
# Regression checks for tools/check-config.sh. No root privileges or network needed.

set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
TEMP=$(mktemp -d)
trap 'rm -rf "$TEMP"' EXIT
FIXTURE="$TEMP/repo"

mkdir -p "$FIXTURE/tools" "$FIXTURE/scripts" \
    "$FIXTURE/config/package-lists" \
    "$FIXTURE/config/archives" \
    "$FIXTURE/config/includes.chroot/etc/calamares"
cp "$ROOT/tools/check-config.sh" "$FIXTURE/tools/check-config.sh"
cp "$ROOT/scripts/check-config.sh" "$FIXTURE/scripts/check-config.sh"
touch "$FIXTURE/config/bootstrap" "$FIXTURE/config/chroot" \
    "$FIXTURE/config/binary" "$FIXTURE/config/common" \
    "$FIXTURE/config/source" \
    "$FIXTURE/config/archives/debian.list.chroot" \
    "$FIXTURE/config/includes.chroot/etc/calamares/settings.conf"

printf 'bash\n' > "$FIXTURE/config/package-lists/base.list.chroot"

if ! "$FIXTURE/tools/check-config.sh" >/dev/null; then
    echo "FAIL: la configuración mínima válida fue rechazada" >&2
    exit 1
fi
if ! "$FIXTURE/scripts/check-config.sh" >/dev/null; then
    echo "FAIL: el wrapper histórico no delega correctamente" >&2
    exit 1
fi

rm "$FIXTURE/config/package-lists/base.list.chroot"
if "$FIXTURE/tools/check-config.sh" >/dev/null 2>&1; then
    echo "FAIL: se aceptó una configuración sin listas de paquetes" >&2
    exit 1
fi

printf 'paquete invalido\n' > "$FIXTURE/config/package-lists/base.list.chroot"
if "$FIXTURE/tools/check-config.sh" >/dev/null 2>&1; then
    echo "FAIL: se aceptó una entrada de paquete con espacios" >&2
    exit 1
fi

echo "OK: validación mínima, wrapper y entradas de paquetes"
