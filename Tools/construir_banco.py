#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye el banco de palabras/pistas a partir de Tools/banco/*.txt.

Formato de cada linea de los ficheros fuente:

    PALABRA|Pista del autodefinido

Las lineas vacias y las que empiezan por '#' se ignoran. La categoria de
cada entrada se deduce del nombre del fichero (001_animales.txt -> animales).

La salida es Tools/banco.json, ya normalizado para la rejilla: mayusculas,
sin tildes, con enye, solo A-Z y N con virgulilla. Ese fichero lo lee el
generador; la app no lo necesita, porque cada autodefinido ya lleva dentro
sus definiciones.
"""

import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_BANCO = os.path.join(RAIZ, "Tools", "banco")
SALIDA = os.path.join(RAIZ, "Tools", "banco.json")

LONGITUD_MIN = 3
LONGITUD_MAX = 12
VALIDA = re.compile("^[A-ZÑ]+$")

# La enye es la unica letra con marca diacritica que se conserva en la
# rejilla; el resto de tildes y la dieresis se eliminan.
def normalizar_palabra(texto):
    texto = texto.strip().upper()
    texto = texto.replace("Ñ", "\u0001")
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = texto.replace("\u0001", "Ñ")
    texto = texto.replace("-", "").replace(" ", "").replace(".", "")
    return texto


def limpiar_pista(texto):
    texto = " ".join(texto.split())
    return texto.strip(" .;")


def contiene_solucion(pista, palabra):
    """La solucion no puede aparecer como palabra suelta dentro de la pista."""
    texto = normalizar_palabra(pista.replace(" ", "\u0002"))
    texto = texto.replace("\u0002", " ")
    for trozo in re.split(r"[^A-ZÑ]+", texto):
        if trozo == palabra:
            return True
    return False


def categoria_de_fichero(nombre):
    base = os.path.splitext(os.path.basename(nombre))[0]
    partes = base.split("_", 1)
    return partes[1] if len(partes) == 2 else base


def cargar(verbose=True):
    ficheros = sorted(
        os.path.join(DIR_BANCO, f)
        for f in os.listdir(DIR_BANCO)
        if f.endswith(".txt")
    )
    entradas = {}          # palabra -> {"c": [pistas], "cat": categoria}
    problemas = []
    repetidas = Counter()
    total_lineas = 0

    for ruta in ficheros:
        categoria = categoria_de_fichero(ruta)
        with open(ruta, encoding="utf-8") as fh:
            for numero, linea in enumerate(fh, 1):
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                total_lineas += 1
                if "|" not in linea:
                    problemas.append("%s:%d sin separador |" % (ruta, numero))
                    continue
                bruta, pista = linea.split("|", 1)
                palabra = normalizar_palabra(bruta)
                pista = limpiar_pista(pista)
                if not VALIDA.match(palabra):
                    problemas.append(
                        "%s:%d palabra invalida %r" % (ruta, numero, bruta.strip())
                    )
                    continue
                if not (LONGITUD_MIN <= len(palabra) <= LONGITUD_MAX):
                    problemas.append(
                        "%s:%d longitud %d fuera de rango (%s)"
                        % (ruta, numero, len(palabra), palabra)
                    )
                    continue
                if len(pista) < 3:
                    problemas.append("%s:%d pista demasiado corta" % (ruta, numero))
                    continue
                if contiene_solucion(pista, palabra):
                    problemas.append(
                        "%s:%d la pista contiene la solucion (%s)"
                        % (ruta, numero, palabra)
                    )
                    continue
                if palabra in entradas:
                    repetidas[palabra] += 1
                    if pista not in entradas[palabra]["c"]:
                        entradas[palabra]["c"].append(pista)
                else:
                    entradas[palabra] = {"c": [pista], "cat": categoria}

    if verbose:
        print("ficheros leidos      : %d" % len(ficheros))
        print("lineas procesadas    : %d" % total_lineas)
        print("palabras unicas      : %d" % len(entradas))
        print("palabras repetidas   : %d" % len(repetidas))
        print("lineas descartadas   : %d" % len(problemas))
        for p in problemas[:40]:
            print("   ! " + p)
        if len(problemas) > 40:
            print("   ... y %d mas" % (len(problemas) - 40))
    return entradas, problemas


def histograma(entradas):
    por_longitud = Counter(len(p) for p in entradas)
    return dict(sorted(por_longitud.items()))


def main():
    entradas, problemas = cargar()
    print("\npor longitud:")
    for longitud, cuantas in histograma(entradas).items():
        print("  %2d letras: %5d" % (longitud, cuantas))

    por_categoria = Counter(v["cat"] for v in entradas.values())
    print("\npor categoria: %d categorias" % len(por_categoria))

    datos = {
        "version": 1,
        "idioma": "es",
        "palabras": [
            {"p": palabra, "c": datos_p["c"], "t": datos_p["cat"]}
            for palabra, datos_p in sorted(entradas.items())
        ],
    }
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as fh:
        json.dump(datos, fh, ensure_ascii=False, separators=(",", ":"))
    tam = os.path.getsize(SALIDA) / 1024.0
    print("\nescrito %s (%.0f KB, %d palabras)" % (SALIDA, tam, len(entradas)))

    if "--estricto" in sys.argv and problemas:
        sys.exit(1)


if __name__ == "__main__":
    main()
