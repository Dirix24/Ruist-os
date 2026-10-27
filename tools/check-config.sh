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
for f in config/hooks/live/*.hook.chroot config/includes.chroot/usr/local/bin/*; do
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
for f in config/package-lists/*.list.chroot config/includes.chroot/usr/share/ruist/profiles/*.list.chroot; do
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
         config/includes.chroot/etc/calamares/modules/packages.conf \
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
for clave in update_db update_system; do
    if ! grep -Eq "^[[:space:]]*$clave:[[:space:]]*false([[:space:]]*(#.*)?)?$" config/includes.chroot/etc/calamares/modules/packages.conf; then
        fallo "packages.conf debe mantener $clave: false para permitir la instalación esencial offline"
    fi
done

if [ "$ERRORES" -gt 0 ]; then
    printf 'Se han encontrado %s problema(s).\n' "$ERRORES"
    exit 1
fi

echo "Todo correcto."
