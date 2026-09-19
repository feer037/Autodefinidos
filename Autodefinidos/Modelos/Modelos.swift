import Foundation

// MARK: - Datos que vienen del generador

/// Una definición escrita dentro de una casilla oscura.
struct TextoPista: Decodable, Hashable {
    let t: String       // texto de la definición
    let d: String       // "D" = la palabra sale a la derecha, "B" = hacia abajo

    var direccion: Direccion { d == "B" ? .abajo : .derecha }
}

/// Casilla oscura con una o dos definiciones.
struct CasillaPista: Decodable, Hashable {
    let f: Int
    let c: Int
    let textos: [TextoPista]
}

/// Bloque de 2x2 casillas ocupado por una pista con imagen.
struct CasillaImagen: Decodable, Hashable {
    let f: Int
    let c: Int
    let ancho: Int
    let alto: Int
    let activo: String     // nombre de la imagen en el catálogo
    let pie: String        // texto de apoyo: "¿De qué país es esta bandera?"
    let d: String

    var direccion: Direccion { d == "B" ? .abajo : .derecha }
}

/// Una palabra colocada en la rejilla.
struct Palabra: Decodable, Hashable {
    let f: Int
    let c: Int
    let d: String
    let n: Int
    let p: String

    var direccion: Direccion { d == "B" ? .abajo : .derecha }

    /// Casillas que ocupa, de la primera a la última.
    var casillas: [Posicion] {
        (0..<n).map { i in
            direccion == .derecha ? Posicion(f: f, c: c + i) : Posicion(f: f + i, c: c)
        }
    }

    func contiene(_ posicion: Posicion) -> Bool {
        casillas.contains(posicion)
    }
}

enum Direccion: String, Hashable {
    case derecha
    case abajo

    var contraria: Direccion { self == .derecha ? .abajo : .derecha }
}

struct Posicion: Hashable {
    let f: Int
    let c: Int
}

/// Un autodefinido completo.
struct Puzzle: Decodable, Identifiable, Hashable {
    let id: String
    let numero: Int
    let titulo: String
    let dificultad: String
    let filas: Int
    let columnas: Int
    let solucion: [String]
    let pistas: [CasillaPista]
    let imagenes: [CasillaImagen]
    let palabras: [Palabra]

    /// Rejilla de solución en forma de matriz de caracteres.
    var matriz: [[Character]] {
        solucion.map { Array($0) }
    }
}

/// Ficha de un autodefinido en el índice del libro.
struct FichaPuzzle: Decodable, Identifiable, Hashable {
    let id: String
    let numero: Int
    let titulo: String
    let dificultad: String
    let filas: Int
    let columnas: Int
    let palabras: Int
    let imagenes: Int

    var etiquetaDificultad: String {
        switch dificultad {
        case "facil": return "Fácil"
        case "medio": return "Medio"
        default: return "Difícil"
        }
    }
}

struct Indice: Decodable {
    let version: Int
    let puzzles: [FichaPuzzle]
}
