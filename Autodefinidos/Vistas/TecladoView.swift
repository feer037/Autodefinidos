import SwiftUI

/// Teclado propio con la eñe incluida y sin nada que dé pistas.
struct TecladoView: View {
    let alPulsar: (Character) -> Void
    let alBorrar: () -> Void
    let alSaltar: () -> Void

    private let filas = [
        Array("QWERTYUIOP"),
        Array("ASDFGHJKLÑ"),
        Array("ZXCVBNM")
    ]

    var body: some View {
        VStack(spacing: 6) {
            ForEach(Array(filas.enumerated()), id: \.offset) { indice, fila in
                HStack(spacing: 5) {
                    if indice == 2 {
                        boton(sistema: "arrow.turn.down.right", accion: alSaltar)
                    }
                    ForEach(Array(fila.enumerated()), id: \.offset) { _, letra in
                        Button {
                            alPulsar(letra)
                        } label: {
                            Text(String(letra))
                                .font(.system(size: 20, weight: .medium, design: .rounded))
                                .frame(maxWidth: .infinity, minHeight: 44)
                                .background(Color(.secondarySystemBackground))
                                .cornerRadius(6)
                        }
                        .buttonStyle(.plain)
                    }
                    if indice == 2 {
                        boton(sistema: "delete.left", accion: alBorrar)
                    }
                }
            }
        }
        .padding(.horizontal, 5)
        .padding(.vertical, 8)
        .background(Color(.systemGroupedBackground))
    }

    private func boton(sistema: String, accion: @escaping () -> Void) -> some View {
        Button(action: accion) {
            Image(systemName: sistema)
                .font(.system(size: 18, weight: .medium))
                .frame(width: 52, minHeight: 44)
                .background(Color(.tertiarySystemFill))
                .cornerRadius(6)
        }
        .buttonStyle(.plain)
    }
}
