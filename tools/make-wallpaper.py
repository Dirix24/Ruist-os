#!/usr/bin/env python3
"""Genera el fondo de pantalla de Ruist OS: formas geométricas en azules oscuros.

Es un diseño propio (triángulos con degradados suaves). Cambia SEMILLA para obtener
otra composición o los colores de abajo para otro tono.

Uso: python3 tools/make-wallpaper.py [salida.png]
Necesita: pillow y numpy.
"""
import sys

import numpy as np
from PIL import Image

ANCHO, ALTO = 1920, 1080
SEMILLA = 24
COLS, FILAS = 6, 4

NEGRO_AZULADO = np.array([0, 3, 18], dtype=float)
AZUL_PROFUNDO = np.array([0, 72, 170], dtype=float)


def main(salida):
    rng = np.random.default_rng(SEMILLA)

    # Rejilla de puntos con ruido: de ahí salen los triángulos
    xs = np.linspace(-0.15 * ANCHO, 1.15 * ANCHO, COLS + 1)
    ys = np.linspace(-0.15 * ALTO, 1.15 * ALTO, FILAS + 1)
    puntos = np.zeros((FILAS + 1, COLS + 1, 2))
    for j in range(FILAS + 1):
        for i in range(COLS + 1):
            dx = rng.uniform(-0.45, 0.45) * ANCHO / COLS
            dy = rng.uniform(-0.45, 0.45) * ALTO / FILAS
            puntos[j, i] = (xs[i] + dx, ys[j] + dy)

    def cercania_centro(px, py):
        """1 en el centro-derecha de la imagen y 0 en las esquinas."""
        d = np.hypot((px - 0.55 * ANCHO) / ANCHO, (py - 0.6 * ALTO) / ALTO)
        return 1 - min(1, d * 1.5)

    img = np.zeros((ALTO, ANCHO, 3), dtype=float)
    img[:] = NEGRO_AZULADO

    yy, xx = np.mgrid[0:ALTO, 0:ANCHO]

    def triangulo(p0, p1, p2, l0, l1, l2):
        minx = max(int(np.floor(min(p0[0], p1[0], p2[0]))), 0)
        maxx = min(int(np.ceil(max(p0[0], p1[0], p2[0]))), ANCHO - 1)
        miny = max(int(np.floor(min(p0[1], p1[1], p2[1]))), 0)
        maxy = min(int(np.ceil(max(p0[1], p1[1], p2[1]))), ALTO - 1)
        if minx >= maxx or miny >= maxy:
            return
        x = xx[miny:maxy + 1, minx:maxx + 1]
        y = yy[miny:maxy + 1, minx:maxx + 1]
        det = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1])
        if abs(det) < 1e-6:
            return
        a = ((p1[1] - p2[1]) * (x - p2[0]) + (p2[0] - p1[0]) * (y - p2[1])) / det
        b = ((p2[1] - p0[1]) * (x - p2[0]) + (p0[0] - p2[0]) * (y - p2[1])) / det
        c = 1 - a - b
        dentro = (a >= 0) & (b >= 0) & (c >= 0)
        v = np.clip(a * l0 + b * l1 + c * l2, 0, 1) ** 1.6
        color = NEGRO_AZULADO + (AZUL_PROFUNDO - NEGRO_AZULADO) * v[..., None]
        zona = img[miny:maxy + 1, minx:maxx + 1]
        zona[dentro] = color[dentro]

    def con_brillo(p0, p1, p2):
        centro = (np.array(p0) + np.array(p1) + np.array(p2)) / 3
        base = np.clip(0.15 + 0.55 * cercania_centro(*centro) + rng.uniform(-0.3, 0.3), 0.02, 0.95)
        # Cada vértice se desvía de la base: da un degradado distinto en cada cara
        niveles = np.clip(base + rng.uniform(-0.4, 0.4, size=3), 0, 1)
        triangulo(p0, p1, p2, *niveles)

    for j in range(FILAS):
        for i in range(COLS):
            a, b = puntos[j, i], puntos[j, i + 1]
            c, d = puntos[j + 1, i], puntos[j + 1, i + 1]
            # Cada celda se divide en dos triángulos; la diagonal alterna
            if (i + j) % 2 == 0:
                con_brillo(a, b, c)
                con_brillo(b, d, c)
            else:
                con_brillo(a, b, d)
                con_brillo(a, d, c)

    # Viñeta suave para oscurecer los bordes
    vx = (xx - ANCHO / 2) / (ANCHO / 2)
    vy = (yy - ALTO / 2) / (ALTO / 2)
    vineta = 1 - 0.25 * np.clip(vx ** 2 + vy ** 2, 0, 1.5)
    img *= vineta[..., None]

    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(salida, optimize=True)
    print("Guardado", salida)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ruist-wallpaper.png")
