import Foundation

/// Carga el libro: el índice completo y cada autodefinido a demanda.
final class Biblioteca: ObservableObject {
    @Published private(set) var fichas: [FichaPuzzle] = []

    private var cache: [String: Puzzle] = [:]

    init() {
        cargarIndice()
    }

    private func cargarIndice() {
        guard let url = Bundle.main.url(forResource: "indice", withExtension: "json"),
              let datos = try? Data(contentsOf: url) else {
            assertionFailure("No se encontró indice.json en el bundle")
            return
        }
        do {
            let indice = try JSONDecoder().decode(Indice.self, from: datos)
            fichas = indice.puzzles.sorted { $0.numero < $1.numero }
        } catch {
            assertionFailure("indice.json ilegible: \(error)")
        }
    }

    /// Devuelve el autodefinido pedido, leyéndolo del bundle la primera vez.
    func puzzle(_ id: String) -> Puzzle? {
        if let guardado = cache[id] { return guardado }
        guard let url = Bundle.main.url(forResource: id, withExtension: "json"),
              let datos = try? Data(contentsOf: url),
              let puzzle = try? JSONDecoder().decode(Puzzle.self, from: datos) else {
            return nil
        }
        cache[id] = puzzle
        return puzzle
    }

    /// Capítulos de cincuenta autodefinidos, para no dar una lista interminable.
    func capitulos() -> [(titulo: String, fichas: [FichaPuzzle])] {
        guard !fichas.isEmpty else { return [] }
        var salida: [(String, [FichaPuzzle])] = []
        var bloque: [FichaPuzzle] = []
        for ficha in fichas {
            bloque.append(ficha)
            if bloque.count == 50 {
                salida.append((tituloCapitulo(bloque), bloque))
                bloque = []
            }
        }
        if !bloque.isEmpty {
            salida.append((tituloCapitulo(bloque), bloque))
        }
        return salida
    }

    private func tituloCapitulo(_ bloque: [FichaPuzzle]) -> String {
        guard let primero = bloque.first, let ultimo = bloque.last else { return "" }
        return "Del \(primero.numero) al \(ultimo.numero)"
    }
}
