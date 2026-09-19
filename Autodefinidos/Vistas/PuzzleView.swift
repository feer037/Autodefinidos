import SwiftUI

/// Pantalla de un autodefinido: cabecera con la definición, rejilla y teclado.
struct PuzzleView: View {
    @StateObject private var juego: EstadoJuego
    @State private var escala: CGFloat = 1
    @State private var escalaGesto: CGFloat = 1
    @State private var mostrarReinicio = false

    private let ficha: FichaPuzzle

    init(puzzle: Puzzle, ficha: FichaPuzzle, progreso: Progreso) {
        self.ficha = ficha
        let id = puzzle.id
        _juego = StateObject(wrappedValue: EstadoJuego(
            puzzle: puzzle,
            guardado: progreso.estado(de: id),
            alGuardar: { estado in progreso.actualizar(id, con: estado) }
        ))
    }

    var body: some View {
        VStack(spacing: 0) {
            cabecera
            Divider()
            rejilla
            Divider()
            TecladoView(
                alPulsar: { juego.escribir($0) },
                alBorrar: { juego.borrar() },
                alSaltar: { juego.siguientePalabra() }
            )
        }
        .navigationTitle(ficha.titulo)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    mostrarReinicio = true
                } label: {
                    Image(systemName: "arrow.counterclockwise")
                }
            }
        }
        .alert("¿Empezar de nuevo?", isPresented: $mostrarReinicio) {
            Button("Cancelar", role: .cancel) { }
            Button("Borrar todo", role: .destructive) { juego.reiniciar() }
        } message: {
            Text("Se borrará todo lo que hayas escrito en este autodefinido.")
        }
        .overlay(alignment: .bottom) {
            if juego.acabaDeResolverse {
                aviso
            }
        }
    }

    // MARK: - Cabecera con la definición en la que se está

    private var cabecera: some View {
        HStack(alignment: .center, spacing: 12) {
            if let palabra = juego.palabraActual {
                if let imagen = juego.imagen(de: palabra) {
                    Image(imagen.activo)
                        .resizable()
                        .scaledToFit()
                        .frame(width: 66, height: 44)
                        .cornerRadius(4)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(imagen.pie)
                            .font(.subheadline)
                        Text("\(palabra.n) letras")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                } else {
                    Image(systemName: palabra.direccion == .derecha
                          ? "arrow.right" : "arrow.down")
                        .foregroundColor(.accentColor)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(juego.texto(de: palabra) ?? "")
                            .font(.subheadline)
                            .lineLimit(3)
                        Text("\(palabra.n) letras")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            } else {
                Text("Toca una casilla para empezar")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            Spacer(minLength: 0)
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
        .frame(maxWidth: .infinity, minHeight: 64, alignment: .leading)
        .background(Color(.systemGroupedBackground))
    }

    // MARK: - Rejilla con desplazamiento y zoom

    private var rejilla: some View {
        GeometryReader { geometria in
            let base = ladoBase(ancho: geometria.size.width)
            let lado = base * escala * escalaGesto

            ScrollView([.horizontal, .vertical], showsIndicators: false) {
                RejillaView(juego: juego, lado: lado)
                    .padding(8)
                    .frame(minWidth: geometria.size.width,
                           minHeight: geometria.size.height,
                           alignment: .center)
            }
            .gesture(
                MagnificationGesture()
                    .onChanged { valor in escalaGesto = valor }
                    .onEnded { valor in
                        escala = min(max(escala * valor, 1), 3)
                        escalaGesto = 1
                    }
            )
        }
    }

    private func ladoBase(ancho: CGFloat) -> CGFloat {
        let disponible = max(ancho - 16, 100)
        return disponible / CGFloat(juego.puzzle.columnas)
    }

    // MARK: - Aviso de resuelto

    private var aviso: some View {
        HStack(spacing: 10) {
            Image(systemName: "checkmark.seal.fill")
                .foregroundColor(.green)
            Text("¡Autodefinido resuelto!")
                .font(.headline)
            Spacer()
            Button("Vale") { juego.acabaDeResolverse = false }
        }
        .padding()
        .background(.ultraThinMaterial)
        .cornerRadius(12)
        .shadow(radius: 6)
        .padding(.horizontal, 16)
        .padding(.bottom, 12)
        .transition(.move(edge: .bottom))
    }
}
