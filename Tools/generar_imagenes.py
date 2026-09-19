#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dibuja las pistas con imagen del libro y su manifiesto.

Las imagenes son vectoriales (SVG) y se generan aqui, sin depender de
fotografias con derechos. Hay dos familias:

  * banderas   -> la respuesta es el nombre del pais
  * objetos    -> la respuesta es el nombre de la cosa dibujada

Cada SVG se copia ademas al catalogo de recursos de la app como un
imageset, de modo que Xcode lo trate como imagen vectorial.

Uso:
    python3 Tools/generar_imagenes.py
"""

import json
import os
import shutil

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_SVG = os.path.join(RAIZ, "Tools", "imagenes", "svg")
MANIFIESTO = os.path.join(RAIZ, "Tools", "imagenes", "manifiesto.json")
CATALOGO = os.path.join(RAIZ, "Autodefinidos", "Recursos", "Assets.xcassets", "Pistas")

ANCHO = 300
ALTO = 200


def svg(cuerpo, ancho=ANCHO, alto=ALTO):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'width="%d" height="%d">%s</svg>' % (ancho, alto, ancho, alto, cuerpo)
    )


def rect(x, y, ancho, alto, color):
    return '<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (
        x, y, ancho, alto, color)


def marco():
    return ('<rect x="0.5" y="0.5" width="%g" height="%g" fill="none" '
            'stroke="#00000022" stroke-width="1"/>' % (ANCHO - 1, ALTO - 1))


# ------------------------------------------------------------- banderas


def vertical(colores):
    ancho = float(ANCHO) / len(colores)
    piezas = [rect(i * ancho, 0, ancho, ALTO, c) for i, c in enumerate(colores)]
    return "".join(piezas)


def horizontal(colores):
    alto = float(ALTO) / len(colores)
    piezas = [rect(0, i * alto, ANCHO, alto, c) for i, c in enumerate(colores)]
    return "".join(piezas)


def franjas(colores, proporciones):
    total = float(sum(proporciones))
    piezas = []
    y = 0.0
    for color, parte in zip(colores, proporciones):
        alto = ALTO * parte / total
        piezas.append(rect(0, y, ANCHO, alto, color))
        y += alto
    return "".join(piezas)


def cruz_nordica(fondo, cruz, borde=None):
    piezas = [rect(0, 0, ANCHO, ALTO, fondo)]
    cx, cy, grosor = 110.0, ALTO / 2.0, 34.0
    if borde:
        piezas.append(rect(0, cy - grosor / 2 - 8, ANCHO, grosor + 16, borde))
        piezas.append(rect(cx - grosor / 2 - 8, 0, grosor + 16, ALTO, borde))
    piezas.append(rect(0, cy - grosor / 2, ANCHO, grosor, cruz))
    piezas.append(rect(cx - grosor / 2, 0, grosor, ALTO, cruz))
    return "".join(piezas)


def circulo(cx, cy, r, color, extra=""):
    return '<circle cx="%g" cy="%g" r="%g" fill="%s" %s/>' % (cx, cy, r, color, extra)


def estrella(cx, cy, radio, color, puntas=5):
    import math
    puntos = []
    for i in range(puntas * 2):
        r = radio if i % 2 == 0 else radio * 0.4
        ang = math.pi / 2 * 3 + i * math.pi / puntas
        puntos.append("%.2f,%.2f" % (cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return '<polygon points="%s" fill="%s"/>' % (" ".join(puntos), color)


BANDERAS = [
    ("francia", "FRANCIA", vertical(["#0055A4", "#FFFFFF", "#EF4135"])),
    ("italia", "ITALIA", vertical(["#009246", "#FFFFFF", "#CE2B37"])),
    ("irlanda", "IRLANDA", vertical(["#169B62", "#FFFFFF", "#FF883E"])),
    ("belgica", "BELGICA", vertical(["#2D2926", "#FAE042", "#ED2939"])),
    ("rumania", "RUMANIA", vertical(["#002B7F", "#FCD116", "#CE1126"])),
    ("chad", "CHAD", vertical(["#002664", "#FECB00", "#C60C30"])),
    ("nigeria", "NIGERIA", vertical(["#008751", "#FFFFFF", "#008751"])),
    ("peru", "PERU", vertical(["#D91023", "#FFFFFF", "#D91023"])),
    ("canada", "CANADA", vertical(["#FF0000", "#FFFFFF", "#FF0000"])),
    ("alemania", "ALEMANIA", horizontal(["#000000", "#DD0000", "#FFCE00"])),
    ("holanda", "HOLANDA", horizontal(["#AE1C28", "#FFFFFF", "#21468B"])),
    ("rusia", "RUSIA", horizontal(["#FFFFFF", "#0039A6", "#D52B1E"])),
    ("hungria", "HUNGRIA", horizontal(["#CD2A3E", "#FFFFFF", "#436F4D"])),
    ("bulgaria", "BULGARIA", horizontal(["#FFFFFF", "#00966E", "#D62612"])),
    ("austria", "AUSTRIA", horizontal(["#ED2939", "#FFFFFF", "#ED2939"])),
    ("letonia", "LETONIA", franjas(["#9E3039", "#FFFFFF", "#9E3039"], [2, 1, 2])),
    ("espana", "ESPANA", franjas(["#AA151B", "#F1BF00", "#AA151B"], [1, 2, 1])),
    ("colombia", "COLOMBIA", franjas(["#FCD116", "#003893", "#CE1126"], [2, 1, 1])),
    ("polonia", "POLONIA", horizontal(["#FFFFFF", "#DC143C"])),
    ("ucrania", "UCRANIA", horizontal(["#0057B7", "#FFD700"])),
    ("indonesia", "INDONESIA", horizontal(["#FF0000", "#FFFFFF"])),
    ("monaco", "MONACO", horizontal(["#CE1126", "#FFFFFF"])),
    ("suecia", "SUECIA", cruz_nordica("#006AA7", "#FECC02")),
    ("noruega", "NORUEGA", cruz_nordica("#BA0C2F", "#00205B", "#FFFFFF")),
    ("dinamarca", "DINAMARCA", cruz_nordica("#C8102E", "#FFFFFF")),
    ("finlandia", "FINLANDIA", cruz_nordica("#FFFFFF", "#003580")),
    ("islandia", "ISLANDIA", cruz_nordica("#02529C", "#DC1E35", "#FFFFFF")),
    ("suiza", "SUIZA", rect(0, 0, ANCHO, ALTO, "#FF0000")
        + rect(ANCHO / 2 - 15, 45, 30, 110, "#FFFFFF")
        + rect(95, ALTO / 2 - 15, 110, 30, "#FFFFFF")),
    ("japon", "JAPON", rect(0, 0, ANCHO, ALTO, "#FFFFFF")
        + circulo(ANCHO / 2, ALTO / 2, 55, "#BC002D")),
    ("bangladesh", "BANGLADESH", rect(0, 0, ANCHO, ALTO, "#006A4E")
        + circulo(ANCHO / 2 - 12, ALTO / 2, 50, "#F42A41")),
    ("marruecos", "MARRUECOS", rect(0, 0, ANCHO, ALTO, "#C1272D")
        + estrella(ANCHO / 2, ALTO / 2, 45, "#006233")),
    ("vietnam", "VIETNAM", rect(0, 0, ANCHO, ALTO, "#DA251D")
        + estrella(ANCHO / 2, ALTO / 2, 48, "#FFFF00")),
    ("somalia", "SOMALIA", rect(0, 0, ANCHO, ALTO, "#4189DD")
        + estrella(ANCHO / 2, ALTO / 2, 48, "#FFFFFF")),
    ("turquia", "TURQUIA", rect(0, 0, ANCHO, ALTO, "#E30A17")
        + circulo(130, ALTO / 2, 46, "#FFFFFF")
        + circulo(146, ALTO / 2, 38, "#E30A17")
        + estrella(192, ALTO / 2, 22, "#FFFFFF")),
    ("tunez", "TUNEZ", rect(0, 0, ANCHO, ALTO, "#E70013")
        + circulo(ANCHO / 2, ALTO / 2, 50, "#FFFFFF")
        + circulo(ANCHO / 2 + 10, ALTO / 2, 38, "#E70013")
        + estrella(ANCHO / 2 + 16, ALTO / 2, 20, "#FFFFFF")),
    ("grecia", "GRECIA", "".join(
        rect(0, i * (ALTO / 9.0), ANCHO, ALTO / 9.0,
             "#0D5EAF" if i % 2 == 0 else "#FFFFFF") for i in range(9))
        + rect(0, 0, ALTO * 5 / 9.0, ALTO * 5 / 9.0, "#0D5EAF")
        + rect(0, ALTO * 2 / 9.0, ALTO * 5 / 9.0, ALTO / 9.0, "#FFFFFF")
        + rect(ALTO * 2 / 9.0, 0, ALTO / 9.0, ALTO * 5 / 9.0, "#FFFFFF")),
    ("portugal", "PORTUGAL", rect(0, 0, ANCHO * 0.4, ALTO, "#046A38")
        + rect(ANCHO * 0.4, 0, ANCHO * 0.6, ALTO, "#DA291C")
        + circulo(ANCHO * 0.4, ALTO / 2, 34, "#FFE900")
        + circulo(ANCHO * 0.4, ALTO / 2, 24, "#DA291C")),
    ("brasil", "BRASIL", rect(0, 0, ANCHO, ALTO, "#009B3A")
        + '<polygon points="150,18 282,100 150,182 18,100" fill="#FEDF00"/>'
        + circulo(150, 100, 40, "#002776")),
    ("argentina", "ARGENTINA", horizontal(["#74ACDF", "#FFFFFF", "#74ACDF"])
        + circulo(ANCHO / 2, ALTO / 2, 22, "#F6B40E")),
    ("mexico", "MEXICO", vertical(["#006847", "#FFFFFF", "#CE1126"])
        + circulo(ANCHO / 2, ALTO / 2, 30, "#8B5A2B")),
    ("israel", "ISRAEL", rect(0, 0, ANCHO, ALTO, "#FFFFFF")
        + rect(0, 26, ANCHO, 22, "#0038B8") + rect(0, ALTO - 48, ANCHO, 22, "#0038B8")
        + estrella(ANCHO / 2, ALTO / 2, 42, "#0038B8", puntas=6)),
    ("china", "CHINA", rect(0, 0, ANCHO, ALTO, "#DE2910")
        + estrella(70, 60, 30, "#FFDE00")
        + estrella(120, 30, 12, "#FFDE00")
        + estrella(140, 58, 12, "#FFDE00")
        + estrella(140, 92, 12, "#FFDE00")
        + estrella(118, 118, 12, "#FFDE00")),
    ("jamaica", "JAMAICA", rect(0, 0, ANCHO, ALTO, "#009B3A")
        + '<polygon points="0,0 150,100 0,200" fill="#000000"/>'
        + '<polygon points="300,0 150,100 300,200" fill="#000000"/>'
        + '<polygon points="0,0 300,0 300,14 0,14" fill="#FED100" opacity="0"/>'
        + '<path d="M0,0 L300,200 M300,0 L0,200" stroke="#FED100" stroke-width="22"/>'),
    ("cuba", "CUBA", "".join(
        rect(0, i * (ALTO / 5.0), ANCHO, ALTO / 5.0,
             "#002A8F" if i % 2 == 0 else "#FFFFFF") for i in range(5))
        + '<polygon points="0,0 120,100 0,200" fill="#CF142B"/>'
        + estrella(38, 100, 24, "#FFFFFF")),
    ("chile", "CHILE", rect(0, 0, ANCHO, ALTO / 2, "#FFFFFF")
        + rect(0, ALTO / 2, ANCHO, ALTO / 2, "#D52B1E")
        + rect(0, 0, 100, ALTO / 2, "#0039A6")
        + estrella(50, 50, 26, "#FFFFFF")),
    ("uruguay", "URUGUAY", "".join(
        rect(0, i * (ALTO / 9.0), ANCHO, ALTO / 9.0,
             "#FFFFFF" if i % 2 == 0 else "#0038A8") for i in range(9))
        + rect(0, 0, 120, ALTO * 4 / 9.0, "#FFFFFF")
        + circulo(60, 44, 26, "#FCD116")),
    ("venezuela", "VENEZUELA", franjas(["#FFCC00", "#00247D", "#CF142B"], [1, 1, 1])
        + "".join(estrella(90 + i * 30, 100, 10, "#FFFFFF") for i in range(5))),
]


# -------------------------------------------------------------- objetos


def objeto_sol():
    import math
    rayos = []
    for i in range(12):
        ang = i * math.pi / 6
        x1 = 150 + 52 * math.cos(ang)
        y1 = 100 + 52 * math.sin(ang)
        x2 = 150 + 76 * math.cos(ang)
        y2 = 100 + 76 * math.sin(ang)
        rayos.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                     'stroke="#E8A317" stroke-width="9" stroke-linecap="round"/>'
                     % (x1, y1, x2, y2))
    return circulo(150, 100, 42, "#F6C244") + "".join(rayos)


OBJETOS = [
    ("sol", "SOL", objeto_sol()),
    ("luna", "LUNA", '<path d="M185,32 A72,72 0 1 0 185,168 A58,58 0 1 1 185,32 Z" '
        'fill="#E8C86B"/>'),
    ("estrella", "ESTRELLA", estrella(150, 100, 74, "#F0C419")),
    ("corazon", "CORAZON", '<path d="M150,168 C60,110 78,42 118,42 C138,42 150,58 '
        '150,58 C150,58 162,42 182,42 C222,42 240,110 150,168 Z" fill="#D94C4C"/>'),
    ("casa", "CASA", '<polygon points="150,34 262,110 38,110" fill="#B4543A"/>'
        + rect(62, 110, 176, 66, "#E3C9A8")
        + rect(128, 130, 44, 46, "#7A5230")
        + rect(80, 124, 32, 28, "#8FB8D8")),
    ("arbol", "ARBOL", rect(140, 108, 20, 66, "#7A5230")
        + circulo(150, 84, 52, "#4F8A4C")
        + circulo(112, 104, 34, "#5C9C58")
        + circulo(188, 104, 34, "#5C9C58")),
    ("flor", "FLOR", '<line x1="150" y1="96" x2="150" y2="178" stroke="#4F8A4C" '
        'stroke-width="8"/>'
        + "".join(circulo(150 + 34 * c[0], 80 + 34 * c[1], 24, "#D96BA0")
                  for c in ((0, -1), (1, 0), (0, 1), (-1, 0)))
        + circulo(150, 80, 18, "#F0C419")),
    ("pez", "PEZ", '<path d="M96,100 C120,58 200,58 226,100 C200,142 120,142 96,100 Z" '
        'fill="#4E9AC4"/>'
        + '<polygon points="96,100 58,72 58,128" fill="#3C7FA6"/>'
        + circulo(196, 90, 7, "#FFFFFF")),
    ("ancla", "ANCLA", circulo(150, 44, 14, "none",
        'stroke="#48607A" stroke-width="9"')
        + '<line x1="150" y1="58" x2="150" y2="164" stroke="#48607A" stroke-width="11"/>'
        + '<line x1="112" y1="80" x2="188" y2="80" stroke="#48607A" stroke-width="10"/>'
        + '<path d="M84,118 C84,168 216,168 216,118" fill="none" stroke="#48607A" '
        'stroke-width="12" stroke-linecap="round"/>'),
    ("llave", "LLAVE", circulo(96, 100, 32, "none",
        'stroke="#C7A249" stroke-width="14"')
        + rect(126, 92, 108, 16, "#C7A249")
        + rect(206, 108, 14, 24, "#C7A249")
        + rect(178, 108, 14, 20, "#C7A249")),
    ("reloj", "RELOJ", circulo(150, 100, 70, "#FFFFFF",
        'stroke="#48607A" stroke-width="10"')
        + '<line x1="150" y1="100" x2="150" y2="58" stroke="#33414F" stroke-width="8" '
        'stroke-linecap="round"/>'
        + '<line x1="150" y1="100" x2="188" y2="118" stroke="#33414F" stroke-width="7" '
        'stroke-linecap="round"/>'
        + circulo(150, 100, 7, "#33414F")),
    ("paraguas", "PARAGUAS", '<path d="M56,112 A94,94 0 0 1 244,112 Z" fill="#C0453F"/>'
        + '<line x1="150" y1="112" x2="150" y2="166" stroke="#5A4632" stroke-width="9"/>'
        + '<path d="M150,166 A16,16 0 0 0 182,166" fill="none" stroke="#5A4632" '
        'stroke-width="9"/>'),
    ("taza", "TAZA", '<path d="M88,66 H196 V126 A54,54 0 0 1 88,126 Z" fill="#FFFFFF" '
        'stroke="#48607A" stroke-width="8"/>'
        + '<path d="M196,84 A26,26 0 0 1 196,136" fill="none" stroke="#48607A" '
        'stroke-width="9"/>'
        + rect(74, 170, 140, 10, "#48607A")),
    ("gafas", "GAFAS", circulo(104, 104, 36, "none",
        'stroke="#33414F" stroke-width="9"')
        + circulo(196, 104, 36, "none", 'stroke="#33414F" stroke-width="9"')
        + '<line x1="140" y1="104" x2="160" y2="104" stroke="#33414F" stroke-width="9"/>'
        + '<line x1="68" y1="96" x2="44" y2="82" stroke="#33414F" stroke-width="8"/>'
        + '<line x1="232" y1="96" x2="256" y2="82" stroke="#33414F" stroke-width="8"/>'),
    ("tijeras", "TIJERAS", circulo(96, 152, 20, "none",
        'stroke="#48607A" stroke-width="9"')
        + circulo(150, 152, 20, "none", 'stroke="#48607A" stroke-width="9"')
        + '<line x1="104" y1="136" x2="212" y2="44" stroke="#9AA7B4" stroke-width="10" '
        'stroke-linecap="round"/>'
        + '<line x1="142" y1="136" x2="34" y2="44" stroke="#9AA7B4" stroke-width="10" '
        'stroke-linecap="round"/>'),
    ("martillo", "MARTILLO", rect(140, 78, 20, 100, "#8A6237")
        + '<path d="M96,44 H204 V74 H176 L168,86 H132 L124,74 H96 Z" fill="#7C8894"/>'),
    ("copa", "COPA", '<path d="M108,44 H192 L172,104 H128 Z" fill="#B23A48"/>'
        + '<line x1="150" y1="104" x2="150" y2="158" stroke="#9AA7B4" '
        'stroke-width="8"/>'
        + rect(112, 158, 76, 10, "#9AA7B4")),
    ("campana", "CAMPANA", '<path d="M100,140 C100,84 118,60 150,52 C182,60 200,84 '
        '200,140 Z" fill="#C7A249"/>' + rect(92, 140, 116, 14, "#B08C36")
        + circulo(150, 164, 12, "#B08C36")),
    ("maleta", "MALETA", rect(66, 76, 168, 96, "#8A5A3B")
        + rect(66, 110, 168, 14, "#6E452C")
        + '<path d="M122,76 V58 H178 V76" fill="none" stroke="#6E452C" '
        'stroke-width="10"/>'),
    ("guitarra", "GUITARRA", circulo(118, 128, 46, "#C58B4A")
        + circulo(168, 118, 36, "#C58B4A")
        + rect(190, 104, 84, 16, "#8A5A3B")
        + rect(262, 92, 16, 40, "#6E452C")
        + circulo(124, 128, 15, "#5A3B21")),
    ("barco", "BARCO", '<path d="M56,140 H244 L216,176 H84 Z" fill="#48607A"/>'
        + '<line x1="150" y1="34" x2="150" y2="140" stroke="#5A4632" stroke-width="8"/>'
        + '<polygon points="156,44 214,126 156,126" fill="#E8E8E8"/>'
        + '<polygon points="144,56 94,126 144,126" fill="#D8D8D8"/>'),
    ("avion", "AVION", '<path d="M40,104 L200,88 L246,60 L262,70 L232,104 L262,138 '
        'L246,148 L200,120 L40,104 Z" fill="#7C8894"/>'
        + '<polygon points="130,100 96,54 118,52 162,96" fill="#5F6B78"/>'),
    ("coche", "COCHE", '<path d="M50,140 L64,104 H110 L134,76 H190 L206,104 H246 '
        'L252,140 Z" fill="#C0453F"/>'
        + circulo(96, 146, 22, "#33414F") + circulo(210, 146, 22, "#33414F")
        + circulo(96, 146, 9, "#9AA7B4") + circulo(210, 146, 9, "#9AA7B4")),
    ("bicicleta", "BICICLETA", circulo(84, 132, 40, "none",
        'stroke="#33414F" stroke-width="8"')
        + circulo(216, 132, 40, "none", 'stroke="#33414F" stroke-width="8"')
        + '<path d="M84,132 L134,74 L188,74 L216,132 L146,132 Z" fill="none" '
        'stroke="#C0453F" stroke-width="8"/>'),
    ("llave_inglesa", "ALICATES", '<path d="M110,170 L160,86" stroke="#7C8894" '
        'stroke-width="14" stroke-linecap="round" fill="none"/>'
        + '<path d="M170,170 L120,86" stroke="#7C8894" stroke-width="14" '
        'stroke-linecap="round" fill="none"/>'
        + circulo(140, 120, 10, "#5F6B78")),
    ("libro", "LIBRO", rect(66, 56, 168, 110, "#B23A48")
        + rect(80, 68, 140, 86, "#F7F1E3")
        + '<line x1="150" y1="68" x2="150" y2="154" stroke="#C9BFAA" '
        'stroke-width="4"/>'),
    ("lapiz", "LAPIZ", '<polygon points="46,160 66,102 232,44 246,74 84,142 Z" '
        'fill="#E0B34C"/>'
        + '<polygon points="46,160 66,102 84,142 Z" fill="#E8DCC0"/>'
        + '<polygon points="46,160 56,132 70,150 Z" fill="#33414F"/>'),
    ("gota", "GOTA", '<path d="M150,36 C196,96 186,152 150,166 C114,152 104,96 '
        '150,36 Z" fill="#4E9AC4"/>'),
    ("nube", "NUBE", circulo(114, 116, 36, "#C9D6E2")
        + circulo(156, 96, 46, "#D9E3EC")
        + circulo(200, 120, 32, "#C9D6E2")
        + rect(114, 120, 86, 32, "#D9E3EC")),
    ("montana", "MONTANA", '<polygon points="30,168 118,54 176,124 214,80 272,168" '
        'fill="#7A8B7A"/>'
        + '<polygon points="92,90 118,54 144,90" fill="#FFFFFF"/>'),
    ("copo", "NIEVE", "".join(
        '<line x1="150" y1="100" x2="%.1f" y2="%.1f" stroke="#8FB8D8" '
        'stroke-width="8" stroke-linecap="round"/>'
        % (150 + 68 * __import__("math").cos(i * 3.14159 / 3),
           100 + 68 * __import__("math").sin(i * 3.14159 / 3)) for i in range(6))),
    ("huevo", "HUEVO", '<ellipse cx="150" cy="106" rx="52" ry="66" fill="#F4E7D3"/>'),
    ("pera", "PERA", '<path d="M150,44 C160,72 196,88 196,124 C196,156 172,174 150,174 '
        'C128,174 104,156 104,124 C104,88 140,72 150,44 Z" fill="#B9C94A"/>'
        + '<line x1="150" y1="44" x2="150" y2="26" stroke="#6E452C" stroke-width="7"/>'),
    ("manzana", "MANZANA", circulo(150, 116, 56, "#C0453F")
        + '<line x1="150" y1="60" x2="150" y2="40" stroke="#6E452C" stroke-width="7"/>'
        + '<path d="M150,50 C176,34 192,44 186,58 C178,72 158,66 150,50 Z" '
        'fill="#5C9C58"/>'),
    ("uva", "UVAS", "".join(circulo(150 + dx, 96 + dy, 17, "#7B4B8A")
        for dx, dy in ((0, 0), (-34, 0), (34, 0), (-17, 30), (17, 30), (0, 60),
                       (-17, -30), (17, -30)))
        + '<line x1="150" y1="40" x2="164" y2="18" stroke="#6E452C" stroke-width="6"/>'),
    ("zanahoria", "ZANAHORIA", '<polygon points="150,176 118,66 182,66" '
        'fill="#D9782D"/>'
        + circulo(134, 58, 16, "#5C9C58") + circulo(166, 58, 16, "#5C9C58")
        + circulo(150, 44, 16, "#5C9C58")),
    ("pastel", "TARTA", '<path d="M70,166 V110 H230 V166 Z" fill="#E8C7A0"/>'
        + '<path d="M70,110 C70,84 230,84 230,110 Z" fill="#C0453F"/>'
        + "".join(rect(94 + i * 34, 52, 6, 32, "#F0C419") for i in range(4))),
    ("sombrero", "SOMBRERO", '<ellipse cx="150" cy="140" rx="98" ry="22" '
        'fill="#4A3A2A"/>'
        + '<path d="M104,140 V84 A46,30 0 0 1 196,84 V140 Z" fill="#5A4632"/>'
        + rect(104, 116, 92, 16, "#33281C")),
    ("zapato", "ZAPATO", '<path d="M56,150 V108 H112 L150,132 H236 A14,14 0 0 1 '
        '236,150 Z" fill="#4A3A2A"/>'
        + rect(56, 150, 180, 12, "#2E241A")),
    ("candado", "CANDADO", rect(96, 100, 108, 76, "#C7A249")
        + '<path d="M120,100 V78 A30,30 0 0 1 180,78 V100" fill="none" '
        'stroke="#9AA7B4" stroke-width="13"/>'
        + circulo(150, 134, 11, "#7A6224")),
    ("sobre", "SOBRE", rect(58, 66, 184, 118, "#F1E7D6")
        + '<polygon points="58,66 150,140 242,66" fill="none" stroke="#B9A98E" '
        'stroke-width="7"/>'),
    ("bandera", "BANDERA", '<line x1="86" y1="30" x2="86" y2="178" stroke="#5A4632" '
        'stroke-width="9"/>'
        + '<path d="M90,40 H222 L200,74 L222,108 H90 Z" fill="#C0453F"/>'),
    ("tambor", "TAMBOR", '<ellipse cx="150" cy="76" rx="76" ry="22" fill="#E8DCC0"/>'
        + '<path d="M74,76 V132 A76,22 0 0 0 226,132 V76" fill="#B23A48"/>'
        + '<path d="M74,90 L226,120 M226,90 L74,120" stroke="#E8DCC0" '
        'stroke-width="6"/>'),
    ("trompeta", "TROMPETA", rect(70, 92, 126, 16, "#C7A249")
        + '<polygon points="196,72 250,48 250,152 196,128" fill="#C7A249"/>'
        + "".join(rect(96 + i * 26, 76, 10, 16, "#9A7A2C") for i in range(3))),
]


def escribir():
    os.makedirs(DIR_SVG, exist_ok=True)
    if os.path.isdir(CATALOGO):
        shutil.rmtree(CATALOGO)
    os.makedirs(CATALOGO)
    with open(os.path.join(CATALOGO, "Contents.json"), "w", encoding="utf-8") as fh:
        json.dump({"info": {"author": "xcode", "version": 1}}, fh, indent=2)

    entradas = []
    for familia, pie in (("banderas", "¿De qué país es esta bandera?"),
                         ("objetos", "¿Qué es lo que se ve?")):
        lista = BANDERAS if familia == "banderas" else OBJETOS
        for nombre, respuesta, cuerpo in lista:
            archivo = "%s_%s" % (familia[:3], nombre)
            contenido = svg(cuerpo + marco())
            ruta = os.path.join(DIR_SVG, archivo + ".svg")
            with open(ruta, "w", encoding="utf-8") as fh:
                fh.write(contenido)

            destino = os.path.join(CATALOGO, archivo + ".imageset")
            os.makedirs(destino, exist_ok=True)
            shutil.copy(ruta, os.path.join(destino, archivo + ".svg"))
            with open(os.path.join(destino, "Contents.json"), "w",
                      encoding="utf-8") as fh:
                json.dump({
                    "images": [{
                        "filename": archivo + ".svg",
                        "idiom": "universal",
                    }],
                    "info": {"author": "xcode", "version": 1},
                    "properties": {
                        "preserves-vector-representation": True,
                        "template-rendering-intent": "original",
                    },
                }, fh, indent=2)

            entradas.append({
                "archivo": archivo,
                "respuesta": respuesta,
                "pie": pie,
                "familia": familia,
            })

    with open(MANIFIESTO, "w", encoding="utf-8") as fh:
        json.dump({"version": 1, "imagenes": entradas}, fh,
                  ensure_ascii=False, indent=1)
    print("generadas %d imagenes en %s" % (len(entradas), DIR_SVG))
    print("catalogo: %s" % CATALOGO)


if __name__ == "__main__":
    escribir()
