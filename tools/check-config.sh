#!/bin/bash
# Comprueba la configuración sin necesidad de red: sintaxis de scripts, XML y JSON.
# Uso: tools/check-config.sh

cd "$(dirname "$0")/.." || exit 1
ERRORES=0

fallo() {
    echo "ERROR: $1"
    ERRORES=$((ERRORES + 1))
}

echo "Comprobando scripts de shell..."
for f in config/hooks/live/*.hook.chroot config/includes.chroot/usr/local/bin/*; do
    [ -L "$f" ] && continue
    [ -f "$f" ] || continue
    case "$(head -n1 "$f")" in
        *bash*) bash -n "$f" || fallo "sintaxis en $f" ;;
        *)      sh -n "$f"   || fallo "sintaxis en $f" ;;
    esac
    [ -x "$f" ] || fallo "$f no es ejecutable"
done

echo "Comprobando XML..."
while IFS= read -r f; do
    python3 -c "import sys, xml.dom.minidom as m; m.parse(sys.argv[1])" "$f" 2>/dev/null \
        || fallo "XML mal formado en $f"
done < <(find config -name '*.xml')

echo "Comprobando JSON..."
while IFS= read -r f; do
    python3 -c "import sys, json; json.load(open(sys.argv[1]))" "$f" 2>/dev/null \
        || fallo "JSON mal formado en $f"
done < <(find config -name '*.json')

echo "Comprobando listas de paquetes..."
for f in config/package-lists/*.list.chroot; do
    if grep -nE '[[:space:]]' <(grep -vE '^\s*(#|$)' "$f") >/dev/null 2>&1; then
        fallo "$f tiene líneas con espacios (un paquete por línea)"
    fi
done

if [ "$ERRORES" -gt 0 ]; then
    echo "Se han encontrado $ERRORES problema(s)."
    exit 1
fi
echo "Todo correcto."
