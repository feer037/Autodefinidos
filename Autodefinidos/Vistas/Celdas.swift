import SwiftUI

/// Triángulo que indica hacia dónde sale la palabra.
struct Flecha: Shape {
    let direccion: Direccion

    func path(in rect: CGRect) -> Path {
        var camino = Path()
        switch direccion {
        case .derecha:
            camino.move(to: CGPoint(x: rect.minX, y: rect.minY))
            camino.addLine(to: CGPoint(x: rect.maxX, y: rect.midY))
            camino.addLine(to: CGPoint(x: rect.minX, y: rect.maxY))
        case .abajo:
            camino.move(to: CGPoint(x: rect.minX, y: rect.minY))
            camino.addLine(to: CGPoint(x: rect.midX, y: rect.maxY))
            camino.addLine(to: CGPoint(x: rect.maxX, y: rect.minY))
        }
        camino.closeSubpath()
        return camino
    }
}

/// Casilla blanca donde se escribe una letra.
struct CeldaLetra: View {
    let letra: Character?
    let lado: CGFloat
    let seleccionada: Bool
    let resaltada: Bool

    var body: some View {
        ZStack {
            Rectangle()
                .fill(fondo)
            Rectangle()
                .stroke(Color.primary.opacity(0.35), lineWidth: 0.6)
            if let letra = letra {
                Text(String(letra))
                    .font(.system(size: lado * 0.58, weight: .semibold, design: .rounded))
                    .foregroundColor(.primary)
                    .minimumScaleFactor(0.5)
            }
        }
        .frame(width: lado, height: lado)
    }

    private var fondo: Color {
        if seleccionada { return Color.accentColor.opacity(0.45) }
        if resaltada { return Color.accentColor.opacity(0.16) }
        return Color(.secondarySystemBackground)
    }
}

/// Casilla oscura con una o dos definiciones y sus flechas.
struct CeldaPista: View {
    let pista: CasillaPista?
    let lado: CGFloat
    let destacada: Bool

    var body: some View {
        ZStack {
            Rectangle()
                .fill(destacada ? Color.accentColor.opacity(0.35) : Color(.tertiarySystemFill))
            Rectangle()
                .stroke(Color.primary.opacity(0.35), lineWidth: 0.6)

            if let pista = pista, !pista.textos.isEmpty {
                VStack(spacing: 0) {
                    ForEach(Array(pista.textos.enumerated()), id: \.offset) { _, texto in
                        Text(texto.t)
                            .font(.system(size: tamanoLetra(pista.textos.count)))
                            .lineLimit(pista.textos.count == 1 ? 4 : 2)
                            .minimumScaleFactor(0.4)
                            .multilineTextAlignment(.center)
                            .foregroundColor(.primary)
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .padding(.horizontal, 1)
                    }
                }
                .padding(1)

                ForEach(Array(pista.textos.enumerated()), id: \.offset) { indice, texto in
                    flecha(para: texto.direccion,
                           banda: indice,
                           bandas: pista.textos.count)
                }
            }
        }
        .frame(width: lado, height: lado)
    }

    private func tamanoLetra(_ cuantas: Int) -> CGFloat {
        cuantas == 1 ? lado * 0.20 : lado * 0.165
    }

    @ViewBuilder
    private func flecha(para direccion: Direccion, banda: Int, bandas: Int) -> some View {
        let tamano = lado * 0.16
        let centroBanda = bandas == 1
            ? lado / 2
            : lado * (banda == 0 ? 0.25 : 0.75)

        Flecha(direccion: direccion)
            .fill(Color.accentColor)
            .frame(width: tamano, height: tamano)
            .position(
                x: direccion == .derecha ? lado - tamano * 0.5 : lado / 2,
                y: direccion == .derecha ? centroBanda : lado - tamano * 0.5
            )
    }
}

/// Pista con imagen: ocupa un bloque de 2x2 casillas.
struct CeldaImagen: View {
    let imagen: CasillaImagen
    let lado: CGFloat
    let destacada: Bool

    var body: some View {
        let ancho = lado * CGFloat(imagen.ancho)
        let alto = lado * CGFloat(imagen.alto)
        let tamanoFlecha = lado * 0.16

        ZStack {
            Rectangle()
                .fill(destacada ? Color.accentColor.opacity(0.35) : Color(.tertiarySystemFill))
            Image(imagen.activo)
                .resizable()
                .scaledToFit()
                .padding(lado * 0.10)
            Rectangle()
                .stroke(Color.primary.opacity(0.35), lineWidth: 0.6)

            Flecha(direccion: imagen.direccion)
                .fill(Color.accentColor)
                .frame(width: tamanoFlecha, height: tamanoFlecha)
                .position(
                    x: imagen.direccion == .derecha ? ancho - tamanoFlecha * 0.5 : ancho / 2,
                    y: imagen.direccion == .derecha ? alto - lado / 2 : alto - tamanoFlecha * 0.5
                )
        }
        .frame(width: ancho, height: alto)
    }
}
