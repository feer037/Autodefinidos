#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dibuja un autodefinido en SVG, tal como se verá en la app.

Sirve para revisar el libro sin abrir Xcode.

Uso:
    python3 Tools/vista_previa.py p001            # rejilla vacía
    python3 Tools/vista_previa.py p001 --resuelto # con las soluciones
"""

import argparse
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_PUZZLES = os.path.join(RAIZ, "Autodefinidos", "Recursos", "Puzzles")
DIR_SVG = os.path.join(RAIZ, "Tools", "imagenes", "svg")
SALIDA = os.path.join(RAIZ, "Tools", "vistas")

LADO = 74.0
MARGEN = 16.0


def escapar(texto):
    return (texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def partir(texto, por_linea):
    palabras = texto.split()
    lineas, actual = [], ""
    for palabra in palabras:
        prueba = (actual + " " + palabra).strip()
        if len(prueba) <= por_linea:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def flecha(x, y, direccion, tamano):
    if direccion == "D":
        puntos = "%g,%g %g,%g %g,%g" % (x, y - tamano / 2, x + tamano, y,
                                        x, y + tamano / 2)
    else:
        puntos = "%g,%g %g,%g %g,%g" % (x - tamano / 2, y, x, y + tamano,
                                        x + tamano / 2, y)
    return '<polygon points="%s" fill="#2f6f4f"/>' % puntos


def incrustar(nombre):
    """Devuelve el contenido del SVG de una pista con imagen, sin cabecera."""
    ruta = os.path.join(DIR_SVG, nombre + ".svg")
    if not os.path.exists(ruta):
        return None
    contenido = open(ruta, encoding="utf-8").read()
    cuerpo = re.sub(r"^<svg[^>]*>", "", contenido).replace("</svg>", "")
    return cuerpo


def dibujar(puzzle, resuelto=False):
    filas, columnas = puzzle["filas"], puzzle["columnas"]
    ancho = columnas * LADO + 2 * MARGEN
    alto = filas * LADO + 2 * MARGEN + 34
    partes = ['<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%g" '
              'viewBox="0 0 %g %g">' % (ancho, alto, ancho, alto)]
    partes.append('<rect width="%g" height="%g" fill="#ffffff"/>' % (ancho, alto))
    partes.append('<text x="%g" y="26" font-family="Helvetica" font-size="17" '
                  'font-weight="bold" fill="#333">%s · %s</text>'
                  % (MARGEN, escapar(puzzle["titulo"]), puzzle["dificultad"]))

    desplazamiento = MARGEN + 34
    rejilla = puzzle["solucion"]
    tapadas = set()
    for imagen in puzzle["imagenes"]:
        for f in range(imagen["f"], imagen["f"] + imagen["alto"]):
            for c in range(imagen["c"], imagen["c"] + imagen["ancho"]):
                tapadas.add((f, c))

    pistas = {(p["f"], p["c"]): p for p in puzzle["pistas"]}

    for f in range(filas):
        for c in range(columnas):
            if (f, c) in tapadas:
                continue
            x = MARGEN + c * LADO
            y = desplazamiento + f * LADO
            if rejilla[f][c] != "#":
                partes.append('<rect x="%g" y="%g" width="%g" height="%g" '
                              'fill="#ffffff" stroke="#444" stroke-width="1"/>'
                              % (x, y, LADO, LADO))
                if resuelto:
                    partes.append('<text x="%g" y="%g" font-family="Helvetica" '
                                  'font-size="%g" text-anchor="middle" fill="#111">%s</text>'
                                  % (x + LADO / 2, y + LADO * 0.72, LADO * 0.55,
                                     rejilla[f][c]))
            else:
                partes.append('<rect x="%g" y="%g" width="%g" height="%g" '
                              'fill="#e9e6df" stroke="#444" stroke-width="1"/>'
                              % (x, y, LADO, LADO))
                pista = pistas.get((f, c))
                if not pista:
                    continue
                bandas = len(pista["textos"])
                for indice, texto in enumerate(pista["textos"]):
                    alto_banda = LADO / bandas
                    arriba = y + indice * alto_banda
                    lineas = partir(texto["t"], 13 if bandas == 1 else 12)
                    lineas = lineas[:4 if bandas == 1 else 3]
                    tamano = 9.5 if bandas == 1 else 8.0
                    inicio = arriba + alto_banda / 2 - (len(lineas) - 1) * tamano * 0.55
                    for numero, linea in enumerate(lineas):
                        partes.append('<text x="%g" y="%g" font-family="Helvetica" '
                                      'font-size="%g" text-anchor="middle" '
                                      'fill="#222">%s</text>'
                                      % (x + LADO / 2 - 3,
                                         inicio + numero * tamano * 1.15,
                                         tamano, escapar(linea)))
                    if texto["d"] == "D":
                        partes.append(flecha(x + LADO - 9, arriba + alto_banda / 2,
                                             "D", 8))
                    else:
                        partes.append(flecha(x + LADO / 2, y + LADO - 9, "B", 8))

    for imagen in puzzle["imagenes"]:
        x = MARGEN + imagen["c"] * LADO
        y = desplazamiento + imagen["f"] * LADO
        ancho_img = imagen["ancho"] * LADO
        alto_img = imagen["alto"] * LADO
        partes.append('<rect x="%g" y="%g" width="%g" height="%g" fill="#e9e6df" '
                      'stroke="#444" stroke-width="1"/>'
                      % (x, y, ancho_img, alto_img))
        cuerpo = incrustar(imagen["activo"])
        if cuerpo:
            escala = min((ancho_img - 16) / 300.0, (alto_img - 16) / 200.0)
            partes.append('<g transform="translate(%g,%g) scale(%g)">%s</g>'
                          % (x + 8, y + (alto_img - 200 * escala) / 2, escala, cuerpo))
        if imagen["d"] == "D":
            partes.append(flecha(x + ancho_img - 9, y + alto_img - LADO / 2, "D", 8))
        else:
            partes.append(flecha(x + ancho_img - LADO / 2, y + alto_img - 9, "B", 8))

    partes.append("</svg>")
    return "".join(partes)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("puzzle", nargs="?", default="p001")
    parser.add_argument("--resuelto", action="store_true")
    args = parser.parse_args()

    ruta = os.path.join(DIR_PUZZLES, args.puzzle + ".json")
    with open(ruta, encoding="utf-8") as fh:
        puzzle = json.load(fh)

    os.makedirs(SALIDA, exist_ok=True)
    nombre = "%s%s.svg" % (args.puzzle, "_resuelto" if args.resuelto else "")
    destino = os.path.join(SALIDA, nombre)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write(dibujar(puzzle, args.resuelto))
    print(destino)


if __name__ == "__main__":
    main()
