#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dibuja el icono de la app web: una miniatura de autodefinido.

Escribe docs/iconos/icono-192.png, icono-512.png y apple-touch-icon.png.
Necesita cairosvg (pip install cairosvg).

Uso:
    python3 Tools/generar_iconos.py
"""

import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_ICONOS = os.path.join(RAIZ, "docs", "iconos")

FONDO = "#2F4858"
PISTA = "#E9E6DF"
LETRA = "#FFFFFF"
FLECHA = "#2F6F4F"
TINTA = "#2F4858"


def dibujo(lado):
    """Cuatro por cuatro casillas: dos de definición, el resto de letra."""
    margen = lado * 0.16
    util = lado - margen * 2
    celda = util / 4.0
    partes = ['<rect width="%g" height="%g" rx="%g" fill="%s"/>'
              % (lado, lado, lado * 0.22, FONDO)]

    # Casillas de definición: arriba a la izquierda y en el centro
    oscuras = {(0, 0), (2, 1)}
    for fila in range(4):
        for col in range(4):
            x = margen + col * celda
            y = margen + fila * celda
            oscura = (fila, col) in oscuras
            partes.append(
                '<rect x="%g" y="%g" width="%g" height="%g" fill="%s" '
                'stroke="%s" stroke-width="%g"/>'
                % (x, y, celda, celda, PISTA if oscura else LETRA,
                   TINTA, lado * 0.006)
            )

    # Las flechas que salen de cada casilla de definición
    for fila, col in sorted(oscuras):
        x = margen + col * celda
        y = margen + fila * celda
        punta = celda * 0.30
        partes.append(
            '<polygon points="%g,%g %g,%g %g,%g" fill="%s"/>'
            % (x + celda - punta, y + celda / 2 - punta / 2,
               x + celda, y + celda / 2,
               x + celda - punta, y + celda / 2 + punta / 2, FLECHA)
        )

    # Un par de letras, para que se lea como un autodefinido
    tam = celda * 0.62
    for (fila, col), letra in {(0, 1): "A", (0, 2): "R", (0, 3): "O"}.items():
        x = margen + col * celda + celda / 2
        y = margen + fila * celda + celda / 2 + tam * 0.35
        partes.append(
            '<text x="%g" y="%g" font-family="Georgia,serif" font-size="%g" '
            'font-weight="700" fill="%s" text-anchor="middle">%s</text>'
            % (x, y, tam, TINTA, letra)
        )

    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%g" '
            'viewBox="0 0 %g %g">%s</svg>'
            % (lado, lado, lado, lado, "".join(partes)))


def main():
    try:
        import cairosvg
    except ImportError:
        raise SystemExit("falta cairosvg: pip install cairosvg")

    os.makedirs(DIR_ICONOS, exist_ok=True)
    for nombre, lado in [("icono-192.png", 192),
                         ("icono-512.png", 512),
                         ("apple-touch-icon.png", 180)]:
        ruta = os.path.join(DIR_ICONOS, nombre)
        cairosvg.svg2png(bytestring=dibujo(512).encode("utf-8"),
                         write_to=ruta, output_width=lado, output_height=lado)
        print("escrito %s (%dx%d)" % (ruta, lado, lado))


if __name__ == "__main__":
    main()
