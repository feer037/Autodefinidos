#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que el libro generado es coherente con lo que espera la app.

Revisa, autodefinido por autodefinido:
  * que cada palabra coincida con las letras de la solucion
  * que cada palabra tenga su definicion (texto o imagen) en la casilla justa
  * que las casillas de la imagen sean oscuras y su flecha apunte a la palabra
  * que no queden series de letras sin palabra ni palabras sin definir
  * que las imagenes existan en el catalogo

Uso:
    python3 Tools/validar.py
"""

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_PUZZLES = os.path.join(RAIZ, "Autodefinidos", "Recursos", "Puzzles")
INDICE = os.path.join(RAIZ, "Autodefinidos", "Recursos", "indice.json")
CATALOGO = os.path.join(RAIZ, "Autodefinidos", "Recursos", "Assets.xcassets", "Pistas")
BANCO = os.path.join(RAIZ, "Tools", "banco.json")


def revisar(puzzle, imagenes_catalogo, banco):
    fallos = []
    filas, columnas = puzzle["filas"], puzzle["columnas"]
    rejilla = [list(f) for f in puzzle["solucion"]]

    if len(rejilla) != filas or any(len(f) != columnas for f in rejilla):
        fallos.append("la solucion no mide %dx%d" % (filas, columnas))
        return fallos

    def es_letra(f, c):
        return 0 <= f < filas and 0 <= c < columnas and rejilla[f][c] != "#"

    # 1. Las palabras coinciden con la rejilla
    for palabra in puzzle["palabras"]:
        f, c, largo, texto = palabra["f"], palabra["c"], palabra["n"], palabra["p"]
        if len(texto) != largo:
            fallos.append("%s dice medir %d" % (texto, largo))
            continue
        for i, letra in enumerate(texto):
            ff = f + i if palabra["d"] == "B" else f
            cc = c + i if palabra["d"] == "D" else c
            if not es_letra(ff, cc) or rejilla[ff][cc] != letra:
                fallos.append("%s no encaja en (%d,%d)" % (texto, f, c))
                break
        if texto not in banco:
            fallos.append("%s no esta en el banco" % texto)

    # 2. Cada palabra tiene su definicion en la casilla anterior
    pistas = {(p["f"], p["c"]): p for p in puzzle["pistas"]}
    inicios_imagen = {}
    for imagen in puzzle["imagenes"]:
        if imagen["d"] == "D":
            inicio = (imagen["f"] + imagen["alto"] - 1, imagen["c"] + imagen["ancho"])
        else:
            inicio = (imagen["f"] + imagen["alto"], imagen["c"] + imagen["ancho"] - 1)
        inicios_imagen[(inicio[0], inicio[1], imagen["d"])] = imagen

    for palabra in puzzle["palabras"]:
        clave = (palabra["f"], palabra["c"], palabra["d"])
        if clave in inicios_imagen:
            continue
        casilla = ((palabra["f"], palabra["c"] - 1) if palabra["d"] == "D"
                   else (palabra["f"] - 1, palabra["c"]))
        pista = pistas.get(casilla)
        if pista is None:
            fallos.append("%s no tiene definicion" % palabra["p"])
            continue
        if not any(t["d"] == palabra["d"] for t in pista["textos"]):
            fallos.append("%s no tiene flecha en su definicion" % palabra["p"])

    # 3. Ninguna definicion sobra ni lleva mas de dos textos
    for pista in puzzle["pistas"]:
        if len(pista["textos"]) > 2:
            fallos.append("una casilla lleva %d definiciones" % len(pista["textos"]))
        for texto in pista["textos"]:
            inicio = ((pista["f"], pista["c"] + 1) if texto["d"] == "D"
                      else (pista["f"] + 1, pista["c"]))
            existe = any(p["f"] == inicio[0] and p["c"] == inicio[1]
                         and p["d"] == texto["d"] for p in puzzle["palabras"])
            if not existe:
                fallos.append("definicion sin palabra en (%d,%d)" % (pista["f"], pista["c"]))

    # 4. Las imagenes tapan casillas oscuras y existen en el catalogo
    for imagen in puzzle["imagenes"]:
        for f in range(imagen["f"], imagen["f"] + imagen["alto"]):
            for c in range(imagen["c"], imagen["c"] + imagen["ancho"]):
                if es_letra(f, c):
                    fallos.append("la imagen %s tapa una casilla de letra"
                                  % imagen["activo"])
        if imagen["activo"] not in imagenes_catalogo:
            fallos.append("falta la imagen %s en el catalogo" % imagen["activo"])
        clave = None
        for posible, dato in inicios_imagen.items():
            if dato is imagen:
                clave = posible
        if clave is None or not any(
                p["f"] == clave[0] and p["c"] == clave[1] and p["d"] == clave[2]
                for p in puzzle["palabras"]):
            fallos.append("la imagen %s no define ninguna palabra" % imagen["activo"])

    # 5. Toda serie de letras de tres o mas es una palabra
    palabras = {(p["f"], p["c"], p["d"]) for p in puzzle["palabras"]}
    for f in range(filas):
        for c in range(columnas):
            if not es_letra(f, c):
                continue
            if not es_letra(f, c - 1):
                largo = 0
                while es_letra(f, c + largo):
                    largo += 1
                if largo >= 3 and (f, c, "D") not in palabras:
                    fallos.append("serie horizontal sin palabra en (%d,%d)" % (f, c))
            if not es_letra(f - 1, c):
                largo = 0
                while es_letra(f + largo, c):
                    largo += 1
                if largo >= 3 and (f, c, "B") not in palabras:
                    fallos.append("serie vertical sin palabra en (%d,%d)" % (f, c))

    return fallos


def main():
    if not os.path.isdir(DIR_PUZZLES):
        print("todavia no hay autodefinidos generados")
        sys.exit(1)

    imagenes_catalogo = {
        nombre[: -len(".imageset")]
        for nombre in os.listdir(CATALOGO)
        if nombre.endswith(".imageset")
    }
    with open(BANCO, encoding="utf-8") as fh:
        banco = {fila["p"] for fila in json.load(fh)["palabras"]}

    ficheros = sorted(f for f in os.listdir(DIR_PUZZLES) if f.endswith(".json"))
    total_fallos = 0
    for nombre in ficheros:
        with open(os.path.join(DIR_PUZZLES, nombre), encoding="utf-8") as fh:
            puzzle = json.load(fh)
        fallos = revisar(puzzle, imagenes_catalogo, banco)
        if fallos:
            total_fallos += len(fallos)
            print("%s:" % nombre)
            for fallo in fallos[:6]:
                print("   - %s" % fallo)

    if os.path.exists(INDICE):
        with open(INDICE, encoding="utf-8") as fh:
            indice = json.load(fh)
        ids = {p["id"] for p in indice["puzzles"]}
        en_disco = {n[:-5] for n in ficheros}
        if ids != en_disco:
            print("el indice y los ficheros no coinciden (%d vs %d)"
                  % (len(ids), len(en_disco)))
            total_fallos += 1

    print("revisados %d autodefinidos, %d fallos" % (len(ficheros), total_fallos))
    sys.exit(1 if total_fallos else 0)


if __name__ == "__main__":
    main()
