import SwiftUI

/// Índice del libro: todos los autodefinidos, por capítulos.
struct IndiceView: View {
    @EnvironmentObject private var biblioteca: Biblioteca
    @EnvironmentObject private var progreso: Progreso
    @State private var filtro: String = "todos"
    @State private var mostrarAjustes = false

    var body: some View {
        NavigationStack {
            List {
                Section {
                    Picker("Dificultad", selection: $filtro) {
                        Text("Todos").tag("todos")
                        Text("Fáciles").tag("facil")
                        Text("Medios").tag("medio")
                        Text("Difíciles").tag("dificil")
                    }
                    .pickerStyle(.segmented)
                    .listRowInsets(EdgeInsets(top: 8, leading: 12, bottom: 8, trailing: 12))
                }

                ForEach(capitulos, id: \.titulo) { capitulo in
                    Section(capitulo.titulo) {
                        ForEach(capitulo.fichas) { ficha in
                            NavigationLink(value: ficha) {
                                fila(ficha)
                            }
                        }
                    }
                }
            }
            .listStyle(.insetGrouped)
            .navigationTitle("Autodefinidos")
            .navigationDestination(for: FichaPuzzle.self) { ficha in
                destino(ficha)
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        mostrarAjustes = true
                    } label: {
                        Image(systemName: "gearshape")
                    }
                }
            }
            .sheet(isPresented: $mostrarAjustes) {
                AjustesView()
            }
        }
    }

    private var capitulos: [(titulo: String, fichas: [FichaPuzzle])] {
        biblioteca.capitulos().compactMap { capitulo in
            let fichas = filtro == "todos"
                ? capitulo.fichas
                : capitulo.fichas.filter { $0.dificultad == filtro }
            return fichas.isEmpty ? nil : (capitulo.titulo, fichas)
        }
    }

    private func fila(_ ficha: FichaPuzzle) -> some View {
        HStack(spacing: 12) {
            Text("\(ficha.numero)")
                .font(.system(.body, design: .rounded).weight(.semibold))
                .frame(width: 44, alignment: .leading)
                .foregroundColor(.secondary)

            VStack(alignment: .leading, spacing: 2) {
                Text(ficha.titulo)
                Text("\(ficha.etiquetaDificultad) · \(ficha.filas)×\(ficha.columnas) · \(ficha.palabras) palabras")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()

            if progreso.resuelto(ficha.id) {
                Image(systemName: "checkmark.circle.fill")
                    .foregroundColor(.green)
            } else if progreso.empezado(ficha.id) {
                Image(systemName: "pencil.circle")
                    .foregroundColor(.orange)
            }
        }
    }

    @ViewBuilder
    private func destino(_ ficha: FichaPuzzle) -> some View {
        if let puzzle = biblioteca.puzzle(ficha.id) {
            PuzzleView(puzzle: puzzle, ficha: ficha, progreso: progreso)
        } else {
            Text("No se ha podido abrir este autodefinido.")
                .foregroundColor(.secondary)
        }
    }
}
