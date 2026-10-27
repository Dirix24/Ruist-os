#!/bin/bash
# Comprueba que todos los paquetes de las listas existen en Debian trixie.
# Hay que ejecutarlo en un Debian trixie con contrib y non-free activados
# y la caché de apt actualizada (apt-get update).
# Uso: tools/check-packages.sh

cd "$(dirname "$0")/.." || exit 1

FALTAN=0
for lista in config/package-lists/*.list.chroot config/includes.chroot/usr/share/ruist/profiles/*.list.chroot config/includes.chroot/usr/share/ruist/store/apt-packages.list; do
    [ -f "$lista" ] || continue
    while IFS= read -r paquete; do
        paquete="${paquete%%#*}"
        paquete="$(echo "$paquete" | xargs)"
        [ -z "$paquete" ] && continue
        if ! apt-cache show --no-all-versions "$paquete" >/dev/null 2>&1; then
            echo "FALTA: $paquete   (en $lista)"
            FALTAN=$((FALTAN + 1))
        fi
    done < "$lista"
done

if [ "$FALTAN" -gt 0 ]; then
    echo
    echo "$FALTAN paquete(s) no existen en trixie. Corrige o quita esas líneas."
    exit 1
fi
echo "Todos los paquetes existen en trixie."
