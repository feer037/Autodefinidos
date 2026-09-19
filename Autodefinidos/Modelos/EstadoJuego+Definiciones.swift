import Foundation

extension EstadoJuego {
    /// Casilla de definición que manda sobre una palabra.
    func casillaDefinicion(de palabra: Palabra) -> Posicion {
        palabra.direccion == .derecha
            ? Posicion(f: palabra.f, c: palabra.c - 1)
            : Posicion(f: palabra.f - 1, c: palabra.c)
    }

    /// Texto de la definición que corresponde a una palabra, si lo hay.
    func texto(de palabra: Palabra) -> String? {
        let casilla = casillaDefinicion(de: palabra)
        guard let pista = puzzle.pistas.first(where: { $0.f == casilla.f && $0.c == casilla.c })
        else { return nil }
        return pista.textos.first(where: { $0.direccion == palabra.direccion })?.t
    }

    /// Pista con imagen que manda sobre una palabra, si la define una imagen.
    func imagen(de palabra: Palabra) -> CasillaImagen? {
        puzzle.imagenes.first { imagen in
            let inicio: Posicion
            if imagen.direccion == .derecha {
                inicio = Posicion(f: imagen.f + imagen.alto - 1, c: imagen.c + imagen.ancho)
            } else {
                inicio = Posicion(f: imagen.f + imagen.alto, c: imagen.c + imagen.ancho - 1)
            }
            return inicio.f == palabra.f && inicio.c == palabra.c
                && imagen.direccion == palabra.direccion
        }
    }

    /// Palabra sobre la que está trabajando el lector.
    var palabraActual: Palabra? {
        guard let seleccion = seleccion else { return nil }
        return palabra(en: seleccion, direccion: direccion)
    }

    /// Casillas oscuras que quedan tapadas por una pista con imagen.
    var casillasBajoImagen: Set<Posicion> {
        var salida: Set<Posicion> = []
        for imagen in puzzle.imagenes {
            for f in imagen.f..<(imagen.f + imagen.alto) {
                for c in imagen.c..<(imagen.c + imagen.ancho) {
                    salida.insert(Posicion(f: f, c: c))
                }
            }
        }
        return salida
    }

    func pista(en posicion: Posicion) -> CasillaPista? {
        puzzle.pistas.first { $0.f == posicion.f && $0.c == posicion.c }
    }
}
