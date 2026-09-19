import Foundation

/// Lo que el lector lleva escrito en un autodefinido.
struct ProgresoPuzzle: Codable {
    /// Letras escritas, indexadas por "fila,columna".
    var letras: [String: String] = [:]
    var resuelto: Bool = false
    var segundos: Int = 0

    func letra(_ posicion: Posicion) -> Character? {
        letras["\(posicion.f),\(posicion.c)"]?.first
    }

    mutating func escribir(_ letra: Character?, en posicion: Posicion) {
        let clave = "\(posicion.f),\(posicion.c)"
        if let letra = letra {
            letras[clave] = String(letra)
        } else {
            letras.removeValue(forKey: clave)
        }
    }
}

/// Guarda el progreso de todo el libro en un único fichero JSON.
final class Progreso: ObservableObject {
    @Published private(set) var porPuzzle: [String: ProgresoPuzzle] = [:]

    private let url: URL

    init() {
        let carpeta = FileManager.default.urls(for: .applicationSupportDirectory,
                                               in: .userDomainMask)[0]
        try? FileManager.default.createDirectory(at: carpeta,
                                                 withIntermediateDirectories: true)
        url = carpeta.appendingPathComponent("progreso.json")
        cargar()
    }

    private func cargar() {
        guard let datos = try? Data(contentsOf: url),
              let leido = try? JSONDecoder().decode([String: ProgresoPuzzle].self,
                                                    from: datos) else { return }
        porPuzzle = leido
    }

    private func guardar() {
        guard let datos = try? JSONEncoder().encode(porPuzzle) else { return }
        try? datos.write(to: url, options: .atomic)
    }

    func estado(de id: String) -> ProgresoPuzzle {
        porPuzzle[id] ?? ProgresoPuzzle()
    }

    func actualizar(_ id: String, con estado: ProgresoPuzzle) {
        porPuzzle[id] = estado
        guardar()
    }

    func resuelto(_ id: String) -> Bool {
        porPuzzle[id]?.resuelto ?? false
    }

    func empezado(_ id: String) -> Bool {
        !(porPuzzle[id]?.letras.isEmpty ?? true)
    }

    var totalResueltos: Int {
        porPuzzle.values.filter { $0.resuelto }.count
    }

    func borrarTodo() {
        porPuzzle = [:]
        guardar()
    }

    func borrar(_ id: String) {
        porPuzzle.removeValue(forKey: id)
        guardar()
    }
}
