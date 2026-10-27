#!/usr/bin/env python3
"""Convierte el logo de Ruist OS en arte ASCII para fastfetch.

Usa medios bloques (▀ ▄ █) para tener el doble de resolución vertical.
El resultado va a config/includes.chroot/usr/share/ruist/logo.txt

Uso: python3 tools/make-ascii-logo.py [logo.png] [salida.txt]
Necesita: pillow.
"""
import sys

from PIL import Image

ANCHO = 48  # columnas; la altura sale sola (2 píxeles por fila de texto)
UMBRAL = 125  # luminosidad a partir de la cual un píxel cuenta como "luz"


def main(entrada, salida):
    source = Image.open(entrada).convert("RGBA")
    fondo = Image.new("RGBA", source.size, (0, 0, 0, 255))
    img = Image.alpha_composite(fondo, source).convert("L").resize((ANCHO, ANCHO), Image.Resampling.LANCZOS)
    px = img.load()

    def luz(x, y):
        return px[x, y] > UMBRAL

    lineas = []
    for y in range(0, ANCHO, 2):
        fila = ""
        for x in range(ANCHO):
            arriba, abajo = luz(x, y), luz(x, y + 1)
            fila += "█" if arriba and abajo else "▀" if arriba else "▄" if abajo else " "
        lineas.append(fila.rstrip())

    while lineas and not lineas[-1]:
        lineas.pop()

    # "$1" activa el color 1 definido en la configuración de fastfetch
    with open(salida, "w", encoding="utf-8") as f:
        f.write("$1" + "\n".join(lineas) + "\n")
    print("\n".join(lineas))
    print("Guardado", salida)


if __name__ == "__main__":
    entrada = sys.argv[1] if len(sys.argv) > 1 else "branding/ruist-logo-mark.png"
    salida = sys.argv[2] if len(sys.argv) > 2 else "config/includes.chroot/usr/share/ruist/logo.txt"
    main(entrada, salida)
