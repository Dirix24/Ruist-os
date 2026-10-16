#!/bin/bash
# check-config.sh - comprueba la configuración de Ruist OS sin compilar nada.
# Uso: ./scripts/check-config.sh   (desde la raíz del repositorio)

cd "$(dirname "$0")/.." || exit 1
ERRORES=0

fallo() {
    echo "ERROR: $1"
    ERRORES=$((ERRORES + 1))
}

echo "== Scripts de shell =="
for f in config/hooks/live/*.hook.chroot config/includes.chroot/usr/local/bin/*; do
    [ -L "$f" ] && continue
    [ -f "$f" ] || continue
    interprete=$(head -n1 "$f")
    case "$interprete" in
        *bash*) bash -n "$f" || fallo "sintaxis: $f" ;;
        *sh*)   sh -n "$f"   || fallo "sintaxis: $f" ;;
        *)      fallo "sin shebang: $f" ;;
    esac
    [ -x "$f" ] || fallo "no es ejecutable: $f"
done

echo "== XML y JSON =="
while IFS= read -r f; do
    python3 -c "import sys, xml.dom.minidom as m; m.parse(sys.argv[1])" "$f" 2>/dev/null \
        || fallo "XML inválido: $f"
done < <(find config -name '*.xml')
while IFS= read -r f; do
    python3 -c "import sys, json; json.load(open(sys.argv[1]))" "$f" 2>/dev/null \
        || fallo "JSON inválido: $f"
done < <(find config -name '*.json')

echo "== Listas de paquetes =="
for f in config/package-lists/*.list.chroot; do
    grep -v '^[[:space:]]*#' "$f" | grep -v '^[[:space:]]*$' | while read -r linea; do
        case "$linea" in
            *[[:space:]]*) echo "ERROR: espacio en nombre de paquete en $f: $linea" ;;
        esac
    done | grep -q ERROR && fallo "nombre de paquete con espacios en $f"
done

echo "== Archivos obligatorios =="
for f in config/bootstrap config/chroot config/binary config/common \
         config/archives/debian.list.chroot \
         config/includes.chroot/etc/calamares/settings.conf; do
    [ -f "$f" ] || fallo "falta $f"
done

if [ "$ERRORES" -eq 0 ]; then
    echo "Todo correcto."
else
    echo "$ERRORES error(es)."
    exit 1
fi
