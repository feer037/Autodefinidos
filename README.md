# Autodefinidos

Un libro de autodefinidos en castellano para iPhone. Nada más: rejillas,
definiciones dentro de la propia rejilla y un teclado. **Sin pistas, sin
comprobaciones, sin ayudas de ningún tipo.**

## Qué hay dentro

| Pieza | Dónde | Qué es |
|---|---|---|
| App iOS | `Autodefinidos/` | SwiftUI, iOS 16 o superior |
| Proyecto | `Autodefinidos.xcodeproj` | Ábrelo y dale a ejecutar |
| Banco de palabras | `Tools/banco/*.txt` | 19.820 palabras con 24.735 definiciones |
| Imágenes | `Tools/imagenes/` | 91 dibujos vectoriales (banderas y objetos) |
| Generador | `Tools/*.py` | Construye el banco y arma los autodefinidos |
| Libro | `Autodefinidos/Recursos/` | 500 autodefinidos ya generados, en JSON |

El libro reparte 16.715 palabras (6.220 distintas) y 439 pistas con imagen
entre 500 rejillas, a partes iguales fáciles, medias y difíciles. Por longitud:
16% de tres letras, 24% de cuatro, 21% de cinco, 17% de seis, 14% de siete y
8% de ocho.

## Abrir la app

```bash
open Autodefinidos.xcodeproj
```

Necesita Xcode 16 o posterior (el proyecto usa grupos sincronizados con el
sistema de archivos, así que no hay que añadir ficheros a mano: todo lo que
esté dentro de `Autodefinidos/` entra solo). Si prefieres regenerar el
proyecto, hay un `project.yml` para XcodeGen.

## Cómo se juega

- Toca una casilla y escribe con el teclado de abajo.
- Un segundo toque en la misma casilla cambia entre la palabra horizontal y
  la vertical.
- La flecha de cada definición dice por dónde arranca la palabra.
- Arriba se ve entera la definición de la palabra en la que estás, porque en
  una pantalla de móvil la letra de la casilla se queda pequeña.
- Pellizca para acercar la rejilla.
- No hay botón de comprobar ni de revelar. Cuando la rejilla queda bien
  resuelta, el autodefinido se marca solo en el índice.

Lo escrito se guarda solo, autodefinido por autodefinido, en
`Application Support/progreso.json`.

## Las pistas con imagen

Algunos autodefinidos llevan una pista con imagen: un bloque de 2×2 casillas
con un dibujo y una flecha. La respuesta es lo que se ve (el país de la
bandera, el objeto dibujado).

Los dibujos son **vectoriales y generados aquí mismo** (`Tools/generar_imagenes.py`),
no fotografías. La idea original era el clásico "¿quién es este actor?", pero
para eso harían falta fotos de personas reales, que no se pueden distribuir en
una app sin licencia. El mecanismo, en cambio, está montado y admite cualquier
imagen: ver más abajo.

### Añadir tus propias imágenes (por ejemplo, un pack de caras)

1. Mete la imagen en `Autodefinidos/Recursos/Assets.xcassets/Pistas/` como un
   `imageset` (arrástrala en Xcode al catálogo, dentro de la carpeta `Pistas`).
2. Añade una entrada en `Tools/imagenes/manifiesto.json`:

   ```json
   { "archivo": "act_ejemplo",
     "respuesta": "APELLIDO",
     "pie": "¿Quién es?",
     "familia": "personas" }
   ```

   `respuesta` tiene que existir en el banco de palabras (añádela en
   `Tools/banco/` si hace falta) y solo puede llevar letras de la A a la Z y
   la eñe, sin espacios ni tildes.
3. Vuelve a generar el libro:

   ```bash
   python3 Tools/construir_banco.py
   python3 Tools/generar_puzzles.py --cantidad 500
   ```

## Regenerar todo

```bash
python3 Tools/construir_banco.py      # Tools/banco/*.txt  -> Tools/banco.json
python3 Tools/generar_imagenes.py     # dibuja los SVG y el catálogo de Xcode
python3 Tools/generar_puzzles.py --cantidad 500 --largo 8
python3 Tools/validar.py              # repasa que el libro sea coherente
```

Armar los 500 lleva un buen rato en un solo proceso. Con cuatro núcleos sale
mucho más a cuenta repartir el trabajo y rehacer el índice al final:

```bash
for i in 0 1 2 3; do
  python3 Tools/generar_puzzles.py --desde $((1 + i*125)) --cantidad 125 \
      --semilla $((2000+i)) --largo 8 &
done
wait
python3 Tools/rehacer_indice.py
```

`--largo` es la palabra más larga que se admite en la rejilla (8 por defecto en
este libro). Subirlo a 9 también funciona, pero el relleno tarda unas tres veces
más y apenas gana variedad.

El generador trabaja en tres fases:

1. **Patrón.** Decide qué casillas son de definición mediante un recocido
   simple: penaliza series de dos letras, palabras demasiado largas, casillas
   sueltas sin cruce y densidades raras, y va moviendo casillas hasta que la
   rejilla es correcta.
2. **Relleno.** Resuelve la rejilla como un problema de restricciones
   (backtracking con la heurística de menos candidatas primero y poda hacia
   delante). Prefiere las palabras menos usadas, para que el libro entero
   reparta el vocabulario.
3. **Montaje.** Reparte las definiciones en sus casillas, coloca las flechas y
   escribe el JSON que lee la app.

Cada autodefinido va en su propio fichero (`Recursos/Puzzles/pNNN.json`) y la
app solo carga el que se abre.

## El banco de palabras

Los ficheros de `Tools/banco/` son texto plano, una línea por entrada:

```
PALABRA|Definición que se lee en la rejilla
```

`construir_banco.py` normaliza (mayúsculas, sin tildes, con eñe), descarta lo
que no sirve (longitudes fuera de 3-12 letras, definiciones que contienen la
solución) y junta las definiciones repetidas de una misma palabra como
variantes, de modo que la misma palabra no salga siempre con la misma pista.

Para ampliarlo basta con añadir líneas a cualquier fichero o crear uno nuevo
en esa carpeta y volver a construir.

De las 19.820 palabras, 13.709 miden entre 3 y 8 letras y son las que pueden
caer en la rejilla; las más largas están en el banco para cuando se suba
`--largo`, y para que las definiciones puedan apoyarse en ellas.
