#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rehace indice.json a partir de los autodefinidos que hay en disco.

Hace falta cuando el libro se genera por tramos en paralelo.
"""

import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_PUZZLES = os.path.join(RAIZ, "Autodefinidos", "Recursos", "Puzzles")
INDICE = os.path.join(RAIZ, "Autodefinidos", "Recursos", "indice.json")

fichas = []
for nombre in sorted(os.listdir(DIR_PUZZLES)):
    if not nombre.endswith(".json"):
        continue
    with open(os.path.join(DIR_PUZZLES, nombre), encoding="utf-8") as fh:
        puzzle = json.load(fh)
    fichas.append({
        "id": puzzle["id"],
        "numero": puzzle["numero"],
        "titulo": puzzle["titulo"],
        "dificultad": puzzle["dificultad"],
        "filas": puzzle["filas"],
        "columnas": puzzle["columnas"],
        "palabras": len(puzzle["palabras"]),
        "imagenes": len(puzzle["imagenes"]),
    })

fichas.sort(key=lambda f: f["numero"])
with open(INDICE, "w", encoding="utf-8") as fh:
    json.dump({"version": 1, "puzzles": fichas}, fh,
              ensure_ascii=False, separators=(",", ":"))
print("indice con %d autodefinidos" % len(fichas))
