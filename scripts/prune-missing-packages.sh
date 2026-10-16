#!/bin/bash
# prune-missing-packages.sh - quita de las listas los paquetes que no existen en trixie
# para que la compilación no se pare por un nombre equivocado.
# Hay que ejecutarlo en un sistema Debian trixie con "apt-get update" hecho
# y con contrib, non-free y non-free-firmware activados.
#
# Falla si falta alguno de los paquetes esenciales.

cd "$(dirname "$0")/.." || exit 1

ESENCIALES="linux-image-amd64 live-boot live-config xfce4-session xfwm4 lightdm calamares network-manager"

FALTAN=""
ESENCIALES_FALTAN=""

existe() {
    apt-cache policy "$1" 2>/dev/null | grep -q 'Candidate: [^(]'
}

for lista in config/package-lists/*.list.chroot; do
    TMP=$(mktemp)
    while IFS= read -r linea; do
        paquete=$(echo "$linea" | sed 's/#.*//' | tr -d '[:space:]')
        if [ -z "$paquete" ]; then
            echo "$linea" >> "$TMP"
            continue
        fi
        if existe "$paquete"; then
            echo "$linea" >> "$TMP"
        else
            FALTAN="$FALTAN $paquete"
            for e in $ESENCIALES; do
                [ "$e" = "$paquete" ] && ESENCIALES_FALTAN="$ESENCIALES_FALTAN $paquete"
            done
            echo "::warning::Paquete inexistente en trixie, se omite: $paquete ($lista)"
        fi
    done < "$lista"
    mv "$TMP" "$lista"
done

RESUMEN="${GITHUB_STEP_SUMMARY:-/dev/null}"
{
    echo "## Paquetes omitidos"
    if [ -z "$FALTAN" ]; then
        echo "Ninguno: todos los paquetes existen en trixie."
    else
        for p in $FALTAN; do echo "- \`$p\`"; done
    fi
} >> "$RESUMEN"

if [ -n "$ESENCIALES_FALTAN" ]; then
    echo "ERROR: faltan paquetes esenciales:$ESENCIALES_FALTAN"
    exit 1
fi
echo "Paquetes omitidos:${FALTAN:- ninguno}"
