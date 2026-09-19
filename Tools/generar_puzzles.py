#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera el libro de autodefinidos a partir del banco de palabras.

Un autodefinido es un crucigrama en el que las definiciones viven dentro
de la propia rejilla: cada casilla oscura lleva una o dos definiciones y
una flecha que indica donde empieza la palabra (a la derecha o abajo).

El generador trabaja en tres fases:

  1. PATRON   Decide que casillas son de definicion y cuales de letra,
              reservando ademas bloques 2x2 para las pistas con imagen.
  2. RELLENO  Resuelve la rejilla como un problema de restricciones
              (backtracking con MRV) usando el banco de palabras.
  3. MONTAJE  Reparte las definiciones en sus casillas y exporta el JSON
              que consume la app.

Uso:
    python3 Tools/generar_puzzles.py --cantidad 500
"""

import argparse
import json
import os
import random
import sys
from collections import Counter, defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANCO = os.path.join(RAIZ, "Tools", "banco.json")
MANIFIESTO_IMAGENES = os.path.join(RAIZ, "Tools", "imagenes", "manifiesto.json")
DIR_PUZZLES = os.path.join(RAIZ, "Autodefinidos", "Recursos", "Puzzles")
INDICE = os.path.join(RAIZ, "Autodefinidos", "Recursos", "indice.json")

LETRA = "L"
DEFINICION = "C"

# (filas, columnas, definiciones con imagen, etiqueta)
FORMATOS = [
    (11, 9, 1, "facil"),
    (13, 11, 1, "medio"),
    (15, 11, 2, "dificil"),
]


# ---------------------------------------------------------------- banco


class Banco(object):
    def __init__(self, ruta):
        with open(ruta, encoding="utf-8") as fh:
            datos = json.load(fh)
        self.pistas = {}
        self.categoria = {}
        for fila in datos["palabras"]:
            self.pistas[fila["p"]] = fila["c"]
            self.categoria[fila["p"]] = fila.get("t", "")
        self.por_longitud = defaultdict(list)
        for palabra in self.pistas:
            self.por_longitud[len(palabra)].append(palabra)
        # indice[(longitud, posicion, letra)] -> set de palabras
        self.indice = defaultdict(set)
        for palabra in self.pistas:
            largo = len(palabra)
            for posicion, letra in enumerate(palabra):
                self.indice[(largo, posicion, letra)].add(palabra)
        self.conjunto_longitud = {
            largo: set(lista) for largo, lista in self.por_longitud.items()
        }
        self.usos = Counter()

    def candidatas(self, largo, fijas):
        """Palabras de 'largo' letras compatibles con [(posicion, letra)]."""
        conjunto = self.conjunto_longitud.get(largo)
        if not conjunto:
            return set()
        if not fijas:
            return set(conjunto)
        fijas = sorted(fijas, key=lambda pl: len(self.indice[(largo, pl[0], pl[1])]))
        resultado = set(self.indice[(largo, fijas[0][0], fijas[0][1])])
        for posicion, letra in fijas[1:]:
            resultado &= self.indice[(largo, posicion, letra)]
            if not resultado:
                break
        return resultado


# --------------------------------------------------------------- patron


LARGO_MAX = 7
DENSIDAD_OBJETIVO = 0.26


class Patron(object):
    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        self.tipo = [[LETRA] * columnas for _ in range(filas)]
        self.protegidas = set()      # casillas de letra intocables
        self.fijas = set()           # casillas de definicion intocables
        self.regiones = []           # pistas con imagen ya colocadas
        for c in range(columnas):
            self.tipo[0][c] = DEFINICION
            self.fijas.add((0, c))
        for f in range(filas):
            self.tipo[f][0] = DEFINICION
            self.fijas.add((f, 0))

    def dentro(self, f, c):
        return 0 <= f < self.filas and 0 <= c < self.columnas

    def es_letra(self, f, c):
        return self.dentro(f, c) and self.tipo[f][c] == LETRA

    def bloquear(self, f, c):
        if self.dentro(f, c) and (f, c) not in self.protegidas:
            self.tipo[f][c] = DEFINICION

    def largo_serie(self, f, c, df, dc):
        """Longitud de la serie de letras que contiene a (f, c)."""
        if not self.es_letra(f, c):
            return 0
        total = 1
        ff, cc = f - df, c - dc
        while self.es_letra(ff, cc):
            total += 1
            ff, cc = ff - df, cc - dc
        ff, cc = f + df, c + dc
        while self.es_letra(ff, cc):
            total += 1
            ff, cc = ff + df, cc + dc
        return total

    def medidas(self):
        """Longitud de la serie horizontal y vertical de cada casilla."""
        filas, columnas = self.filas, self.columnas
        horizontal = [[0] * columnas for _ in range(filas)]
        vertical = [[0] * columnas for _ in range(filas)]
        for f in range(filas):
            c = 0
            while c < columnas:
                if self.tipo[f][c] != LETRA:
                    c += 1
                    continue
                inicio = c
                while c < columnas and self.tipo[f][c] == LETRA:
                    c += 1
                largo = c - inicio
                for cc in range(inicio, c):
                    horizontal[f][cc] = largo
        for c in range(columnas):
            f = 0
            while f < filas:
                if self.tipo[f][c] != LETRA:
                    f += 1
                    continue
                inicio = f
                while f < filas and self.tipo[f][c] == LETRA:
                    f += 1
                largo = f - inicio
                for ff in range(inicio, f):
                    vertical[ff][c] = largo
        return horizontal, vertical

    def coste(self):
        """Cuanto se aparta la rejilla de un autodefinido bien formado.

        Penaliza series de dos letras, palabras demasiado largas, casillas
        sueltas sin cruce y densidades de definicion fuera de lo habitual.
        """
        horizontal, vertical = self.medidas()
        total = 0.0
        blancas = 0
        cruzadas = 0
        ultima_fila = self.filas - 1
        ultima_columna = self.columnas - 1
        for f in range(self.filas):
            fila_h = horizontal[f]
            fila_v = vertical[f]
            siguiente_v = vertical[f + 1] if f < ultima_fila else None
            for c in range(self.columnas):
                h = fila_h[c]
                v = fila_v[c]
                if h == 0:
                    # Casilla oscura: molesta si no define ninguna palabra.
                    sirve = c < ultima_columna and fila_h[c + 1] >= 3
                    if not sirve and siguiente_v is not None:
                        sirve = siguiente_v[c] >= 3
                    if not sirve:
                        total += 1.30
                    continue
                blancas += 1
                if h == 2:
                    total += 1.0
                elif h > LARGO_MAX:
                    total += (h - LARGO_MAX) * 2.0
                elif h == LARGO_MAX:
                    total += 0.10
                if v == 2:
                    total += 1.0
                elif v > LARGO_MAX:
                    total += (v - LARGO_MAX) * 2.0
                elif v == LARGO_MAX:
                    total += 0.10
                if h == 1 and v == 1:
                    total += 4.0
                elif h == 1 or v == 1:
                    total += 0.15
                else:
                    cruzadas += 1
        celdas = float(self.filas * self.columnas)
        densidad = 1.0 - blancas / celdas
        total += abs(densidad - DENSIDAD_OBJETIVO) * 24.0
        self._blancas = blancas
        self._cruzadas = cruzadas
        return total

    def valida(self):
        horizontal, vertical = self.medidas()
        for f in range(self.filas):
            for c in range(self.columnas):
                h = horizontal[f][c]
                v = vertical[f][c]
                if h == 0:
                    continue
                if h == 2 or v == 2 or h > LARGO_MAX or v > LARGO_MAX:
                    return False
                if h == 1 and v == 1:
                    return False
        return True

    def sembrar(self, rng):
        """Punto de partida: una retícula regular de casillas de definicion."""
        modulo = rng.choice([4, 5, 5, 6])
        coprimos = [k for k in range(1, modulo) if _mcd(k, modulo) == 1]
        a = rng.choice(coprimos)
        b = rng.choice(coprimos)
        k = rng.randrange(modulo)
        for f in range(1, self.filas):
            for c in range(1, self.columnas):
                if (f, c) in self.protegidas or (f, c) in self.fijas:
                    continue
                self.tipo[f][c] = (
                    DEFINICION if (a * f + b * c) % modulo == k else LETRA
                )

    def afinar(self, rng, vueltas=3400):
        """Recocido simple: mueve casillas hasta que la rejilla es correcta."""
        libres = [
            (f, c)
            for f in range(1, self.filas)
            for c in range(1, self.columnas)
            if (f, c) not in self.protegidas and (f, c) not in self.fijas
        ]
        if not libres:
            return False
        actual = self.coste()
        temperatura = 0.9
        for vuelta in range(vueltas):
            if actual <= 0.0001 and vuelta > vueltas // 3:
                break
            f, c = libres[rng.randrange(len(libres))]
            previo = self.tipo[f][c]
            self.tipo[f][c] = LETRA if previo == DEFINICION else DEFINICION
            nuevo = self.coste()
            delta = nuevo - actual
            if delta <= 0 or rng.random() < temperatura * 0.08:
                actual = nuevo
            else:
                self.tipo[f][c] = previo
            temperatura *= 0.9985
        return self.valida()

    def huecos(self):
        """Lista de palabras a rellenar: (fila, columna, direccion, largo)."""
        resultado = []
        for f in range(self.filas):
            for c in range(self.columnas):
                if self.tipo[f][c] != LETRA:
                    continue
                if not self.es_letra(f, c - 1) and self.largo_serie(f, c, 0, 1) >= 3:
                    resultado.append((f, c, "D", self.largo_serie(f, c, 0, 1)))
                if not self.es_letra(f - 1, c) and self.largo_serie(f, c, 1, 0) >= 3:
                    resultado.append((f, c, "B", self.largo_serie(f, c, 1, 0)))
        return resultado

    def proporcion_cruces(self):
        cruzadas = 0
        blancas = 0
        for f in range(self.filas):
            for c in range(self.columnas):
                if self.tipo[f][c] != LETRA:
                    continue
                blancas += 1
                if self.largo_serie(f, c, 0, 1) >= 3 and self.largo_serie(f, c, 1, 0) >= 3:
                    cruzadas += 1
        if blancas == 0:
            return 0.0
        return float(cruzadas) / blancas


def _mcd(a, b):
    while b:
        a, b = b, a % b
    return a


def colocar_imagen(patron, largo_respuesta, rng):
    """Reserva un bloque 2x2 de definicion con una unica flecha a la derecha.

    Las casillas contiguas al bloque se bloquean para que la imagen no
    pueda definir mas de una palabra, y la palabra que arranca a su
    derecha se fija a la longitud de la respuesta.
    """
    posiciones = [
        (f, c)
        for f in range(1, patron.filas - 2)
        for c in range(1, patron.columnas - 3)
    ]
    rng.shuffle(posiciones)
    for f, c in posiciones:
        inicio_c = c + 2
        fin_c = inicio_c + largo_respuesta - 1
        if fin_c > patron.columnas - 1:
            continue
        bloque = [(f, c), (f, c + 1), (f + 1, c), (f + 1, c + 1)]
        serie = [(f + 1, cc) for cc in range(inicio_c, fin_c + 1)]
        margen = bloque + serie + [
            (f - 1, c), (f - 1, c + 1), (f + 2, c), (f + 2, c + 1),
            (f, c + 2), (f + 2, c + 2),
        ]
        if any(
            (celda in patron.protegidas)
            or (patron.dentro(celda[0], celda[1]) and patron.tipo[celda[0]][celda[1]] != LETRA)
            for celda in bloque
        ):
            continue
        if any(celda in patron.protegidas for celda in margen):
            continue
        # el bloque de imagen no puede tocar el borde superior o izquierdo
        # del area util porque ahi ya hay casillas de definicion
        for celda in bloque:
            patron.tipo[celda[0]][celda[1]] = DEFINICION
            patron.fijas.add(celda)
        for celda in serie:
            patron.tipo[celda[0]][celda[1]] = LETRA
            patron.protegidas.add(celda)
        for celda in ((f, c + 2), (f + 2, c), (f + 2, c + 1), (f + 1, fin_c + 1)):
            patron.bloquear(celda[0], celda[1])
            if patron.dentro(celda[0], celda[1]):
                patron.fijas.add(celda)
        patron.regiones.append(
            {"f": f, "c": c, "ancho": 2, "alto": 2,
             "inicio": (f + 1, inicio_c), "largo": largo_respuesta}
        )
        return True
    return False


def generar_patron(filas, columnas, imagenes_largos, rng):
    patron = Patron(filas, columnas)
    for largo in imagenes_largos:
        if not colocar_imagen(patron, largo, rng):
            return None

    patron.sembrar(rng)
    if not patron.afinar(rng):
        return None
    if patron.proporcion_cruces() < 0.62:
        return None
    for region in patron.regiones:
        f, c = region["inicio"]
        if patron.largo_serie(f, c, 0, 1) != region["largo"]:
            return None
        if patron.es_letra(f, c - 1):
            return None
    huecos = patron.huecos()
    if len(huecos) < 18:
        return None
    return patron, huecos


# -------------------------------------------------------------- relleno


class Relleno(object):
    def __init__(self, patron, huecos, banco, fijos, rng, ramas=14):
        self.patron = patron
        self.banco = banco
        self.rng = rng
        self.ramas = ramas
        self.huecos = huecos
        self.fijos = fijos            # indice de hueco -> palabra obligatoria
        self.letras = {}
        self.asignadas = [None] * len(huecos)
        self.usadas = set()
        self.nodos = 0
        self.celdas = []
        for f, c, direccion, largo in huecos:
            df, dc = (0, 1) if direccion == "D" else (1, 0)
            self.celdas.append([(f + df * i, c + dc * i) for i in range(largo)])
        self.cruces = defaultdict(list)
        for indice, celdas in enumerate(self.celdas):
            for posicion, celda in enumerate(celdas):
                self.cruces[celda].append((indice, posicion))

    def preparar(self):
        """Lista inicial de candidatas de cada hueco y huecos que se cruzan."""
        self.vecinos = [set() for _ in self.huecos]
        for celda, lista in self.cruces.items():
            for i, _ in lista:
                for j, _ in lista:
                    if i != j:
                        self.vecinos[i].add(j)
        self.vecinos = [sorted(v) for v in self.vecinos]

        self.opciones = []
        for indice, (f, c, direccion, largo) in enumerate(self.huecos):
            if indice in self.fijos:
                self.opciones.append([self.fijos[indice]])
            else:
                self.opciones.append(list(self.banco.por_longitud.get(largo, ())))
            if not self.opciones[indice]:
                return False

        # las palabras impuestas por las imagenes fijan letras de salida
        for indice, palabra in self.fijos.items():
            for posicion, celda in enumerate(self.celdas[indice]):
                self.letras[celda] = palabra[posicion]
        for indice in list(self.fijos):
            for vecino in self.vecinos[indice]:
                self.opciones[vecino] = self._filtrar(vecino, self.opciones[vecino])
                if not self.opciones[vecino]:
                    return False
        return True

    def _filtrar(self, indice, lista):
        celdas = self.celdas[indice]
        marcas = []
        for posicion, celda in enumerate(celdas):
            letra = self.letras.get(celda)
            if letra is not None:
                marcas.append((posicion, letra))
        if not marcas:
            return lista
        salida = []
        for palabra in lista:
            for posicion, letra in marcas:
                if palabra[posicion] != letra:
                    break
            else:
                salida.append(palabra)
        return salida

    def ordenar(self, opciones):
        usos = self.banco.usos
        libres = [p for p in opciones if p not in self.usadas]
        libres.sort(key=lambda p: (usos[p], self.rng.random()))
        return libres[: self.ramas]

    def resolver(self, limite=60000):
        if not self.preparar():
            return False
        pendientes = [i for i in range(len(self.huecos))]
        return self._paso(pendientes, limite)

    def _paso(self, pendientes, limite):
        if not pendientes:
            return True
        self.nodos += 1
        if self.nodos > limite:
            return False

        mejor = min(pendientes, key=lambda i: len(self.opciones[i]))
        restantes = [i for i in pendientes if i != mejor]
        vecinos = [j for j in self.vecinos[mejor] if j in restantes]

        for palabra in self.ordenar(self.opciones[mejor]):
            escritas = []
            for posicion, celda in enumerate(self.celdas[mejor]):
                if celda not in self.letras:
                    self.letras[celda] = palabra[posicion]
                    escritas.append(celda)
            copia = {j: self.opciones[j] for j in vecinos}
            viable = True
            for j in vecinos:
                self.opciones[j] = self._filtrar(j, copia[j])
                if not self.opciones[j]:
                    viable = False
                    break
            if viable:
                self.asignadas[mejor] = palabra
                self.usadas.add(palabra)
                if self._paso(restantes, limite):
                    return True
                self.usadas.discard(palabra)
                self.asignadas[mejor] = None
            for j, lista in copia.items():
                self.opciones[j] = lista
            for celda in escritas:
                del self.letras[celda]
            if self.nodos > limite:
                return False
        return False


# -------------------------------------------------------------- montaje


LARGO_COMODO = 38


def elegir_definicion(opciones, giro):
    """Escoge una variante de la definicion que quepa bien en la casilla.

    Entre las que caben se va rotando, para que la misma palabra no salga
    siempre con la misma pista a lo largo del libro.
    """
    comodas = [texto for texto in opciones if len(texto) <= LARGO_COMODO]
    if comodas:
        return comodas[giro % len(comodas)]
    return min(opciones, key=len)


def montar(patron, huecos, relleno, banco, imagenes_asignadas, identificador,
           numero, dificultad, rng):
    filas, columnas = patron.filas, patron.columnas
    solucion = []
    for f in range(filas):
        fila = []
        for c in range(columnas):
            if patron.tipo[f][c] == LETRA:
                fila.append(relleno.letras[(f, c)])
            else:
                fila.append("#")
        solucion.append("".join(fila))

    # casilla de definicion de cada palabra
    definiciones = defaultdict(list)
    palabras = []
    inicios_imagen = {tuple(r["inicio"]): i for i, r in enumerate(patron.regiones)}

    for indice, (f, c, direccion, largo) in enumerate(huecos):
        palabra = relleno.asignadas[indice]
        palabras.append({"f": f, "c": c, "d": direccion, "n": largo, "p": palabra})
        if (f, c) in inicios_imagen and direccion == "D":
            continue  # la define una imagen
        casilla = (f, c - 1) if direccion == "D" else (f - 1, c)
        texto = elegir_definicion(banco.pistas[palabra], numero + indice)
        definiciones[casilla].append({"t": texto, "d": direccion})
        banco.usos[palabra] += 1

    pistas = []
    for casilla in sorted(definiciones):
        textos = sorted(definiciones[casilla], key=lambda x: 0 if x["d"] == "D" else 1)
        pistas.append({"f": casilla[0], "c": casilla[1], "textos": textos})

    imagenes = []
    for posicion, region in enumerate(patron.regiones):
        activo = imagenes_asignadas[posicion]
        imagenes.append({
            "f": region["f"],
            "c": region["c"],
            "ancho": region["ancho"],
            "alto": region["alto"],
            "activo": activo["archivo"],
            "pie": activo["pie"],
            "d": "D",
        })
        banco.usos[activo["respuesta"]] += 1

    return {
        "id": identificador,
        "numero": numero,
        "titulo": "Autodefinido %d" % numero,
        "dificultad": dificultad,
        "filas": filas,
        "columnas": columnas,
        "solucion": solucion,
        "pistas": pistas,
        "imagenes": imagenes,
        "palabras": palabras,
    }


# ---------------------------------------------------------------- libro


def cargar_imagenes(banco):
    if not os.path.exists(MANIFIESTO_IMAGENES):
        return []
    with open(MANIFIESTO_IMAGENES, encoding="utf-8") as fh:
        datos = json.load(fh)
    validas = []
    for item in datos["imagenes"]:
        respuesta = item["respuesta"]
        if respuesta in banco.pistas:
            validas.append(item)
        else:
            print("  aviso: %s no esta en el banco" % respuesta)
    return validas


def generar_uno(numero, banco, imagenes, rng):
    """Monta el autodefinido; si se atasca, reintenta con menos imagenes."""
    filas, columnas, cuantas, dificultad = FORMATOS[(numero - 1) % len(FORMATOS)]
    if not imagenes:
        cuantas = 0
    for tope in range(cuantas, -1, -1):
        salida = _intentar(numero, banco, imagenes, rng, filas, columnas, tope,
                           dificultad)
        if salida is not None:
            return salida
    return None


def _intentar(numero, banco, imagenes, rng, filas, columnas, cuantas_imagenes,
              dificultad):
    for _ in range(40):
        elegidas = []
        for _ in range(cuantas_imagenes):
            candidatas = [
                i for i in imagenes
                if len(i["respuesta"]) <= columnas - 3
                and i not in elegidas
            ]
            if not candidatas:
                break
            candidatas.sort(key=lambda i: (banco.usos[i["respuesta"]], rng.random()))
            elegidas.append(candidatas[0])
        largos = [len(i["respuesta"]) for i in elegidas]

        resultado = generar_patron(filas, columnas, largos, rng)
        if resultado is None:
            continue
        patron, huecos = resultado

        indice_hueco = {(h[0], h[1], h[2]): i for i, h in enumerate(huecos)}
        fijos = {}
        correcto = True
        for posicion, region in enumerate(patron.regiones):
            f, c = region["inicio"]
            clave = (f, c, "D")
            if clave not in indice_hueco:
                correcto = False
                break
            fijos[indice_hueco[clave]] = elegidas[posicion]["respuesta"]
        if not correcto:
            continue

        relleno = Relleno(patron, huecos, banco, fijos, rng)
        if relleno.resolver():
            return patron, huecos, relleno, elegidas, dificultad
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cantidad", type=int, default=500)
    parser.add_argument("--semilla", type=int, default=20260918)
    parser.add_argument("--desde", type=int, default=1)
    parser.add_argument("--largo", type=int, default=0,
                        help="longitud maxima de palabra en la rejilla")
    parser.add_argument("--salida", default="",
                        help="carpeta alternativa donde escribir (pruebas)")
    args = parser.parse_args()

    if args.largo:
        globals()["LARGO_MAX"] = args.largo
    if args.salida:
        globals()["DIR_PUZZLES"] = args.salida
        globals()["INDICE"] = os.path.join(args.salida, "indice.json")

    banco = Banco(BANCO)
    imagenes = cargar_imagenes(banco)
    print("banco: %d palabras, %d imagenes" % (len(banco.pistas), len(imagenes)))

    rng = random.Random(args.semilla)
    os.makedirs(DIR_PUZZLES, exist_ok=True)
    indice = []
    fallos = 0

    for numero in range(args.desde, args.desde + args.cantidad):
        salida = generar_uno(numero, banco, imagenes, rng)
        if salida is None:
            fallos += 1
            print("  ! no se pudo generar el numero %d" % numero)
            continue
        patron, huecos, relleno, elegidas, dificultad = salida
        identificador = "p%03d" % numero
        puzzle = montar(patron, huecos, relleno, banco, elegidas, identificador,
                        numero, dificultad, rng)
        ruta = os.path.join(DIR_PUZZLES, identificador + ".json")
        with open(ruta, "w", encoding="utf-8") as fh:
            json.dump(puzzle, fh, ensure_ascii=False, separators=(",", ":"))
        indice.append({
            "id": identificador,
            "numero": numero,
            "titulo": puzzle["titulo"],
            "dificultad": dificultad,
            "filas": puzzle["filas"],
            "columnas": puzzle["columnas"],
            "palabras": len(puzzle["palabras"]),
            "imagenes": len(puzzle["imagenes"]),
        })
        if numero % 25 == 0:
            distintas = sum(1 for p, n in banco.usos.items() if n > 0)
            print("  %d autodefinidos | %d palabras distintas usadas"
                  % (numero, distintas))

    with open(INDICE, "w", encoding="utf-8") as fh:
        json.dump({"version": 1, "puzzles": indice}, fh,
                  ensure_ascii=False, separators=(",", ":"))

    distintas = sum(1 for p, n in banco.usos.items() if n > 0)
    print("\ngenerados %d autodefinidos (%d fallos)" % (len(indice), fallos))
    print("palabras distintas usadas: %d de %d" % (distintas, len(banco.pistas)))
    if not indice:
        sys.exit(1)


if __name__ == "__main__":
    main()
