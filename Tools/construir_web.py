#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepara los datos de la versión web (docs/) a partir del libro ya generado.

Hace tres cosas:

  * parte los 500 autodefinidos en bloques de cincuenta, para no bajar dos
    megas de golpe ni pedir quinientos ficheros sueltos
  * copia los dibujos de las pistas con imagen
  * escribe precache.json: la lista de todo lo que el service worker guarda
    para que la app funcione sin conexión, con una versión que cambia cuando
    cambia el contenido

Uso:
    python3 Tools/construir_web.py
"""

import hashlib
import json
import os
import shutil

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_PUZZLES = os.path.join(RAIZ, "Autodefinidos", "Recursos", "Puzzles")
INDICE = os.path.join(RAIZ, "Autodefinidos", "Recursos", "indice.json")
DIR_SVG = os.path.join(RAIZ, "Tools", "imagenes", "svg")

DIR_WEB = os.path.join(RAIZ, "docs")
DIR_DATOS = os.path.join(DIR_WEB, "datos")
DIR_IMG = os.path.join(DIR_WEB, "img")

POR_BLOQUE = 50

# Ficheros de la propia app, los que el service worker guarda siempre.
ARMAZON = [
    "./",
    "index.html",
    "app.css",
    "app.js",
    "manifest.webmanifest",
    "iconos/icono-192.png",
    "iconos/icono-512.png",
    "iconos/apple-touch-icon.png",
]


def bloque_de(numero):
    """Bloque al que pertenece un autodefinido (1-50 -> 0, 51-100 -> 1...)."""
    return (numero - 1) // POR_BLOQUE


def main():
    if not os.path.isdir(DIR_PUZZLES):
        raise SystemExit("no hay autodefinidos generados; ejecuta generar_puzzles.py")

    os.makedirs(DIR_DATOS, exist_ok=True)
    os.makedirs(DIR_IMG, exist_ok=True)

    with open(INDICE, encoding="utf-8") as fh:
        indice = json.load(fh)

    # 1. Los autodefinidos, en bloques de cincuenta
    bloques = {}
    for nombre in sorted(os.listdir(DIR_PUZZLES)):
        if not nombre.endswith(".json"):
            continue
        with open(os.path.join(DIR_PUZZLES, nombre), encoding="utf-8") as fh:
            puzzle = json.load(fh)
        bloques.setdefault(bloque_de(puzzle["numero"]), {})[puzzle["id"]] = puzzle

    for viejo in os.listdir(DIR_DATOS):
        os.remove(os.path.join(DIR_DATOS, viejo))

    rutas_datos = []
    for numero_bloque in sorted(bloques):
        nombre = "bloque-%02d.json" % numero_bloque
        with open(os.path.join(DIR_DATOS, nombre), "w", encoding="utf-8") as fh:
            json.dump(bloques[numero_bloque], fh, ensure_ascii=False,
                      separators=(",", ":"))
        rutas_datos.append("datos/" + nombre)

    # El índice lleva dentro en qué bloque está cada autodefinido.
    for ficha in indice["puzzles"]:
        ficha["bloque"] = bloque_de(ficha["numero"])
    indice["porBloque"] = POR_BLOQUE
    with open(os.path.join(DIR_DATOS, "indice.json"), "w", encoding="utf-8") as fh:
        json.dump(indice, fh, ensure_ascii=False, separators=(",", ":"))
    rutas_datos.insert(0, "datos/indice.json")

    # 2. Los dibujos de las pistas con imagen
    for viejo in os.listdir(DIR_IMG):
        os.remove(os.path.join(DIR_IMG, viejo))
    rutas_img = []
    for nombre in sorted(os.listdir(DIR_SVG)):
        if not nombre.endswith(".svg"):
            continue
        shutil.copyfile(os.path.join(DIR_SVG, nombre),
                        os.path.join(DIR_IMG, nombre))
        rutas_img.append("img/" + nombre)

    # 3. La lista para el service worker, con una versión que depende de todo
    ficheros = ARMAZON + rutas_datos + rutas_img
    resumen = hashlib.sha256()
    for ruta in rutas_datos + rutas_img:
        with open(os.path.join(DIR_WEB, ruta), "rb") as fh:
            resumen.update(fh.read())
    for ruta in ARMAZON:
        completa = os.path.join(DIR_WEB, ruta)
        if os.path.isfile(completa):
            with open(completa, "rb") as fh:
                resumen.update(fh.read())

    with open(os.path.join(DIR_WEB, "precache.json"), "w", encoding="utf-8") as fh:
        json.dump({"version": resumen.hexdigest()[:12], "ficheros": ficheros},
                  fh, ensure_ascii=False, separators=(",", ":"))

    total = sum(
        os.path.getsize(os.path.join(DIR_WEB, r)) for r in rutas_datos + rutas_img
    )
    print("bloques de datos : %d" % len(rutas_datos))
    print("dibujos copiados : %d" % len(rutas_img))
    print("peso de los datos: %.1f MB" % (total / 1e6))
    print("escrito %s" % os.path.join(DIR_WEB, "precache.json"))


if __name__ == "__main__":
    main()
