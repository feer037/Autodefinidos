import SwiftUI

@main
struct AutodefinidosApp: App {
    @StateObject private var biblioteca = Biblioteca()
    @StateObject private var progreso = Progreso()

    var body: some Scene {
        WindowGroup {
            IndiceView()
                .environmentObject(biblioteca)
                .environmentObject(progreso)
        }
    }
}
