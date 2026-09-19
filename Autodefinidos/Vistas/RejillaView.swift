import SwiftUI

/// Dibuja la rejilla completa del autodefinido.
struct RejillaView: View {
    @ObservedObject var juego: EstadoJuego
    let lado: CGFloat

    var body: some View {
        let resaltadas = juego.casillasResaltadas
        let tapadas = juego.casillasBajoImagen
        let definicionActual = juego.palabraActual.map { juego.casillaDefinicion(de: $0) }

        ZStack(alignment: .topLeading) {
            ForEach(0..<juego.puzzle.filas, id: \.self) { fila in
                ForEach(0..<juego.puzzle.columnas, id: \.self) { columna in
                    let posicion = Posicion(f: fila, c: columna)
                    if !tapadas.contains(posicion) {
                        celda(posicion, resaltadas: resaltadas, definicion: definicionActual)
                            .offset(x: CGFloat(columna) * lado, y: CGFloat(fila) * lado)
                    }
                }
            }

            ForEach(Array(juego.puzzle.imagenes.enumerated()), id: \.offset) { _, imagen in
                CeldaImagen(imagen: imagen,
                            lado: lado,
                            destacada: esImagenActual(imagen))
                    .offset(x: CGFloat(imagen.c) * lado, y: CGFloat(imagen.f) * lado)
            }
        }
        .frame(width: CGFloat(juego.puzzle.columnas) * lado,
               height: CGFloat(juego.puzzle.filas) * lado,
               alignment: .topLeading)
        .background(Color(.systemBackground))
    }

    @ViewBuilder
    private func celda(_ posicion: Posicion,
                       resaltadas: Set<Posicion>,
                       definicion: Posicion?) -> some View {
        if juego.esLetra(posicion) {
            CeldaLetra(letra: juego.letra(posicion),
                       lado: lado,
                       seleccionada: juego.seleccion == posicion,
                       resaltada: resaltadas.contains(posicion))
                .contentShape(Rectangle())
                .onTapGesture { juego.seleccionar(posicion) }
        } else {
            CeldaPista(pista: juego.pista(en: posicion),
                       lado: lado,
                       destacada: definicion == posicion)
        }
    }

    private func esImagenActual(_ imagen: CasillaImagen) -> Bool {
        guard let palabra = juego.palabraActual else { return false }
        return juego.imagen(de: palabra) == imagen
    }
}
