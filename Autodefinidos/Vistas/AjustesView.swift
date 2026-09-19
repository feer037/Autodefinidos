import SwiftUI

struct AjustesView: View {
    @EnvironmentObject private var biblioteca: Biblioteca
    @EnvironmentObject private var progreso: Progreso
    @Environment(\.dismiss) private var cerrar
    @State private var confirmarBorrado = false

    var body: some View {
        NavigationStack {
            List {
                Section("Tu libro") {
                    fila("Autodefinidos", "\(biblioteca.fichas.count)")
                    fila("Resueltos", "\(progreso.totalResueltos)")
                }

                Section("Cómo se juega") {
                    Text("Toca una casilla y escribe. Un segundo toque en la misma casilla cambia entre la palabra horizontal y la vertical.")
                    Text("La flecha de cada definición indica por dónde empieza la palabra.")
                    Text("No hay ayudas ni comprobaciones: cuando la rejilla queda bien resuelta, el autodefinido se marca solo.")
                }

                Section {
                    Button(role: .destructive) {
                        confirmarBorrado = true
                    } label: {
                        Text("Borrar todo el progreso")
                    }
                }
            }
            .navigationTitle("Ajustes")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Listo") { cerrar() }
                }
            }
            .alert("¿Borrar el progreso?", isPresented: $confirmarBorrado) {
                Button("Cancelar", role: .cancel) { }
                Button("Borrar", role: .destructive) { progreso.borrarTodo() }
            } message: {
                Text("Se perderá lo escrito en todos los autodefinidos.")
            }
        }
    }

    private func fila(_ titulo: String, _ valor: String) -> some View {
        HStack {
            Text(titulo)
            Spacer()
            Text(valor).foregroundColor(.secondary)
        }
    }
}
