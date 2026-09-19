import Foundation

/// Estado de un autodefinido mientras se resuelve.
final class EstadoJuego: ObservableObject {
    let puzzle: Puzzle

    @Published var letras: [Posicion: Character] = [:]
    @Published var seleccion: Posicion?
    @Published var direccion: Direccion = .derecha
    @Published var resuelto: Bool = false
    @Published var acabaDeResolverse: Bool = false

    private let matriz: [[Character]]
    private let alGuardar: (ProgresoPuzzle) -> Void

    init(puzzle: Puzzle, guardado: ProgresoPuzzle, alGuardar: @escaping (ProgresoPuzzle) -> Void) {
        self.puzzle = puzzle
        self.matriz = puzzle.matriz
        self.alGuardar = alGuardar
        self.resuelto = guardado.resuelto
        for (clave, valor) in guardado.letras {
            let partes = clave.split(separator: ",")
            if partes.count == 2,
               let f = Int(partes[0]), let c = Int(partes[1]),
               let letra = valor.first {
                letras[Posicion(f: f, c: c)] = letra
            }
        }
        seleccion = primeraCasillaLibre()
    }

    // MARK: - Consultas de la rejilla

    func esLetra(_ posicion: Posicion) -> Bool {
        guard posicion.f >= 0, posicion.f < puzzle.filas,
              posicion.c >= 0, posicion.c < puzzle.columnas else { return false }
        return matriz[posicion.f][posicion.c] != "#"
    }

    func solucion(_ posicion: Posicion) -> Character? {
        guard esLetra(posicion) else { return nil }
        return matriz[posicion.f][posicion.c]
    }

    func letra(_ posicion: Posicion) -> Character? {
        letras[posicion]
    }

    func palabra(en posicion: Posicion, direccion: Direccion) -> Palabra? {
        puzzle.palabras.first { $0.direccion == direccion && $0.contiene(posicion) }
    }

    /// Casillas de la palabra que está resaltada ahora mismo.
    var casillasResaltadas: Set<Posicion> {
        guard let seleccion = seleccion,
              let palabra = palabra(en: seleccion, direccion: direccion) else { return [] }
        return Set(palabra.casillas)
    }

    // MARK: - Selección

    func seleccionar(_ posicion: Posicion) {
        guard esLetra(posicion) else { return }
        if seleccion == posicion {
            // Segundo toque en la misma casilla: se cambia de dirección
            let otra = direccion.contraria
            if palabra(en: posicion, direccion: otra) != nil {
                direccion = otra
            }
        } else {
            seleccion = posicion
            if palabra(en: posicion, direccion: direccion) == nil {
                direccion = direccion.contraria
            }
        }
    }

    private func primeraCasillaLibre() -> Posicion? {
        for f in 0..<puzzle.filas {
            for c in 0..<puzzle.columnas {
                let posicion = Posicion(f: f, c: c)
                if esLetra(posicion) && letras[posicion] == nil {
                    return posicion
                }
            }
        }
        for f in 0..<puzzle.filas {
            for c in 0..<puzzle.columnas where esLetra(Posicion(f: f, c: c)) {
                return Posicion(f: f, c: c)
            }
        }
        return nil
    }

    // MARK: - Escritura

    func escribir(_ letra: Character) {
        guard let posicion = seleccion, esLetra(posicion) else { return }
        letras[posicion] = letra
        guardar()
        comprobar()
        avanzar()
    }

    func borrar() {
        guard let posicion = seleccion else { return }
        if letras[posicion] != nil {
            letras[posicion] = nil
        } else {
            retroceder()
            if let anterior = seleccion {
                letras[anterior] = nil
            }
        }
        guardar()
    }

    func avanzar() {
        guard let posicion = seleccion else { return }
        let siguiente = direccion == .derecha
            ? Posicion(f: posicion.f, c: posicion.c + 1)
            : Posicion(f: posicion.f + 1, c: posicion.c)
        if esLetra(siguiente), casillasResaltadas.contains(siguiente) {
            seleccion = siguiente
        }
    }

    func retroceder() {
        guard let posicion = seleccion else { return }
        let anterior = direccion == .derecha
            ? Posicion(f: posicion.f, c: posicion.c - 1)
            : Posicion(f: posicion.f - 1, c: posicion.c)
        if esLetra(anterior), casillasResaltadas.contains(anterior) {
            seleccion = anterior
        }
    }

    /// Salta a la primera casilla libre de la siguiente palabra.
    func siguientePalabra() {
        guard let seleccion = seleccion,
              let actual = palabra(en: seleccion, direccion: direccion),
              let indice = puzzle.palabras.firstIndex(of: actual) else { return }
        let total = puzzle.palabras.count
        for salto in 1...total {
            let palabra = puzzle.palabras[(indice + salto) % total]
            let libre = palabra.casillas.first { letras[$0] == nil } ?? palabra.casillas[0]
            self.seleccion = libre
            self.direccion = palabra.direccion
            return
        }
    }

    // MARK: - Estado final

    private func comprobar() {
        for f in 0..<puzzle.filas {
            for c in 0..<puzzle.columnas {
                let posicion = Posicion(f: f, c: c)
                guard let esperada = solucion(posicion) else { continue }
                if letras[posicion] != esperada {
                    if resuelto { resuelto = false }
                    return
                }
            }
        }
        if !resuelto {
            resuelto = true
            acabaDeResolverse = true
            guardar()
        }
    }

    private func guardar() {
        var estado = ProgresoPuzzle()
        for (posicion, letra) in letras {
            estado.escribir(letra, en: posicion)
        }
        estado.resuelto = resuelto
        alGuardar(estado)
    }

    func reiniciar() {
        letras = [:]
        resuelto = false
        seleccion = primeraCasillaLibre()
        guardar()
    }

    /// Cuántas casillas de letra hay escritas, para la barra de avance.
    var proporcionEscrita: Double {
        var total = 0
        var escritas = 0
        for f in 0..<puzzle.filas {
            for c in 0..<puzzle.columnas {
                let posicion = Posicion(f: f, c: c)
                guard esLetra(posicion) else { continue }
                total += 1
                if letras[posicion] != nil { escritas += 1 }
            }
        }
        return total == 0 ? 0 : Double(escritas) / Double(total)
    }
}
