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
                if let siguiente = porDonde {
                    Section {
                        NavigationLink(value: siguiente) {
                            HStack(spacing: 12) {
                                Image(systemName: "bookmark.fill")
                                    .foregroundColor(.accentColor)
                                VStack(alignment: .leading, spacing: 2) {
                                    Text("Seguir por el \(siguiente.numero)")
                                    Text("\(progreso.totalResueltos) de \(biblioteca.fichas.count) resueltos")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                    }
                }

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

                ForEach(capitulos) { capitulo in
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
                    .environmentObject(biblioteca)
                    .environmentObject(progreso)
            }
        }
    }

    /// Primer autodefinido sin resolver: por donde se retoma el libro.
    private var porDonde: FichaPuzzle? {
        biblioteca.fichas.first { !progreso.resuelto($0.id) }
    }

    private var capitulos: [Capitulo] {
        biblioteca.capitulos().compactMap { capitulo in
            let fichas = filtro == "todos"
                ? capitulo.fichas
                : capitulo.fichas.filter { $0.dificultad == filtro }
            return fichas.isEmpty ? nil : Capitulo(titulo: capitulo.titulo, fichas: fichas)
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
