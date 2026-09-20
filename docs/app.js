/* Autodefinidos — libro de quinientos autodefinidos en castellano.
   Sin pistas, sin comprobar, sin revelar. */

(function () {
  "use strict";

  var CLAVE_PROGRESO = "autodefinidos.progreso";
  var CLAVE_ULTIMO = "autodefinidos.ultimo";
  var LETRAS = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ";

  var indice = null;          // fichas de los 500
  var porBloque = 50;
  var bloques = {};           // numero de bloque -> { id: puzzle }
  var progreso = cargarProgreso();
  var filtro = "todas";

  // Partida en curso
  var juego = null;

  // ----------------------------------------------------------- guardado

  function cargarProgreso() {
    try {
      var crudo = localStorage.getItem(CLAVE_PROGRESO);
      return crudo ? JSON.parse(crudo) : {};
    } catch (e) {
      return {};
    }
  }

  function guardarProgreso() {
    try {
      localStorage.setItem(CLAVE_PROGRESO, JSON.stringify(progreso));
    } catch (e) {
      /* Sin espacio o en navegación privada: se sigue jugando sin guardar. */
    }
  }

  function recordarUltimo(id) {
    try { localStorage.setItem(CLAVE_ULTIMO, id); } catch (e) {}
  }

  function ultimoAbierto() {
    try { return localStorage.getItem(CLAVE_ULTIMO); } catch (e) { return null; }
  }

  // -------------------------------------------------------- carga de datos

  function traer(ruta) {
    return fetch(ruta).then(function (r) {
      if (!r.ok) throw new Error("no se pudo leer " + ruta);
      return r.json();
    });
  }

  function cargarBloque(numero) {
    if (bloques[numero]) return Promise.resolve(bloques[numero]);
    var nombre = "datos/bloque-" + (numero < 10 ? "0" : "") + numero + ".json";
    return traer(nombre).then(function (datos) {
      bloques[numero] = datos;
      return datos;
    });
  }

  // ------------------------------------------------------------- pantallas

  function mostrar(cual) {
    ["pantallaIndice", "pantallaPuzzle", "pantallaAjustes"].forEach(function (id) {
      document.getElementById(id).classList.toggle("oculta", id !== cual);
    });
  }

  // --------------------------------------------------------------- índice

  function estadoDe(id) {
    return progreso[id] || { letras: {}, resuelto: false };
  }

  function pintarIndice() {
    var contenedor = document.getElementById("capitulos");
    contenedor.textContent = "";

    var fichas = indice.puzzles.filter(function (f) {
      return filtro === "todas" || f.dificultad === filtro;
    });

    for (var desde = 0; desde < fichas.length; desde += porBloque) {
      var trozo = fichas.slice(desde, desde + porBloque);
      var detalle = document.createElement("details");
      detalle.className = "capitulo";
      if (desde === 0) detalle.open = true;

      var titulo = document.createElement("summary");
      titulo.textContent = "Del " + trozo[0].numero + " al " +
                           trozo[trozo.length - 1].numero;
      var hechos = trozo.filter(function (f) { return estadoDe(f.id).resuelto; }).length;
      if (hechos) {
        titulo.textContent += "  ·  " + hechos +
          (hechos === 1 ? " resuelto" : " resueltos");
      }
      detalle.appendChild(titulo);

      var malla = document.createElement("div");
      malla.className = "rejilla-fichas";
      trozo.forEach(function (ficha) { malla.appendChild(botonFicha(ficha)); });
      detalle.appendChild(malla);
      contenedor.appendChild(detalle);
    }

    pintarSeguir();
  }

  function botonFicha(ficha) {
    var estado = estadoDe(ficha.id);
    var boton = document.createElement("button");
    boton.className = "ficha";
    boton.type = "button";

    var numero = document.createElement("span");
    numero.className = "numero";
    numero.textContent = ficha.numero;
    boton.appendChild(numero);

    var detalle = document.createElement("span");
    detalle.className = "detalle";
    detalle.textContent = etiquetaDificultad(ficha.dificultad) + " · " +
                          ficha.columnas + "×" + ficha.filas;
    boton.appendChild(detalle);

    if (estado.resuelto) {
      var marca = document.createElement("span");
      marca.className = "marca";
      marca.textContent = "✓";
      boton.appendChild(marca);
    } else {
      var escritas = Object.keys(estado.letras || {}).length;
      if (escritas > 0) {
        var barra = document.createElement("div");
        barra.className = "barra-avance";
        var relleno = document.createElement("i");
        // Aproximado: no hace falta abrir el autodefinido para pintarlo.
        var hueco = Math.round(ficha.filas * ficha.columnas * 0.62);
        relleno.style.width = Math.min(100, (escritas / hueco) * 100) + "%";
        barra.appendChild(relleno);
        boton.appendChild(barra);
      }
    }

    boton.addEventListener("click", function () { abrir(ficha); });
    return boton;
  }

  function etiquetaDificultad(d) {
    if (d === "facil") return "Fácil";
    if (d === "medio") return "Medio";
    return "Difícil";
  }

  function pintarSeguir() {
    var boton = document.getElementById("seguir");
    var id = ultimoAbierto();
    var ficha = id && indice.puzzles.filter(function (f) { return f.id === id; })[0];
    if (!ficha) { boton.hidden = true; return; }
    boton.hidden = false;
    boton.textContent = "Seguir por el " + ficha.numero;
    boton.onclick = function () { abrir(ficha); };
  }

  // ------------------------------------------------- abrir un autodefinido

  function abrir(ficha) {
    cargarBloque(ficha.bloque).then(function (datos) {
      var puzzle = datos[ficha.id];
      if (!puzzle) throw new Error("falta " + ficha.id);
      recordarUltimo(ficha.id);
      // La pantalla se muestra antes de medir: si sigue oculta, el ancho
      // disponible es cero y la rejilla saldría del tamaño mínimo.
      mostrar("pantallaPuzzle");
      empezar(puzzle, ficha);
    }).catch(function (e) {
      alert("No se pudo abrir el autodefinido. " +
            "Si es la primera vez, conéctate para que se descargue.");
      console.error(e);
    });
  }

  function empezar(puzzle, ficha) {
    var estado = estadoDe(puzzle.id);
    juego = {
      puzzle: puzzle,
      ficha: ficha,
      matriz: puzzle.solucion.map(function (f) { return f.split(""); }),
      letras: Object.assign({}, estado.letras),
      seleccion: null,
      direccion: "D",
      resuelto: !!estado.resuelto,
      // Mapas para no recorrer listas todo el rato
      pistaEn: {},
      imagenEn: {},
      tapada: {},
      inicioImagen: {}
    };

    puzzle.pistas.forEach(function (p) { juego.pistaEn[p.f + "," + p.c] = p; });
    puzzle.imagenes.forEach(function (im) {
      juego.imagenEn[im.f + "," + im.c] = im;
      for (var f = im.f; f < im.f + im.alto; f++) {
        for (var c = im.c; c < im.c + im.ancho; c++) {
          juego.tapada[f + "," + c] = im;
        }
      }
      var f0 = im.d === "D" ? im.f + im.alto - 1 : im.f + im.alto;
      var c0 = im.d === "D" ? im.c + im.ancho : im.c + im.ancho - 1;
      juego.inicioImagen[f0 + "," + c0 + "," + im.d] = im;
    });

    document.getElementById("tituloPuzzle").textContent = puzzle.titulo;
    juego.seleccion = primeraLibre();
    ajustarDireccion();
    construirRejilla();
    refrescar();
  }

  function esLetra(f, c) {
    return f >= 0 && f < juego.puzzle.filas &&
           c >= 0 && c < juego.puzzle.columnas &&
           juego.matriz[f][c] !== "#";
  }

  function primeraLibre() {
    var p = juego.puzzle;
    for (var f = 0; f < p.filas; f++) {
      for (var c = 0; c < p.columnas; c++) {
        if (esLetra(f, c) && !juego.letras[f + "," + c]) return { f: f, c: c };
      }
    }
    for (var f2 = 0; f2 < p.filas; f2++) {
      for (var c2 = 0; c2 < p.columnas; c2++) {
        if (esLetra(f2, c2)) return { f: f2, c: c2 };
      }
    }
    return null;
  }

  // ------------------------------------------------------------- palabras

  function palabraEn(pos, direccion) {
    if (!pos) return null;
    var lista = juego.puzzle.palabras;
    for (var i = 0; i < lista.length; i++) {
      var w = lista[i];
      if (w.d !== direccion) continue;
      if (w.d === "D" && w.f === pos.f && pos.c >= w.c && pos.c < w.c + w.n) return w;
      if (w.d === "B" && w.c === pos.c && pos.f >= w.f && pos.f < w.f + w.n) return w;
    }
    return null;
  }

  function casillasDe(w) {
    var salida = [];
    for (var i = 0; i < w.n; i++) {
      salida.push(w.d === "D" ? { f: w.f, c: w.c + i } : { f: w.f + i, c: w.c });
    }
    return salida;
  }

  function palabraActual() {
    return palabraEn(juego.seleccion, juego.direccion);
  }

  function ajustarDireccion() {
    if (!palabraEn(juego.seleccion, juego.direccion)) {
      juego.direccion = juego.direccion === "D" ? "B" : "D";
    }
  }

  /** La definición de una palabra: o una casilla de texto, o una imagen. */
  function definicionDe(w) {
    if (!w) return null;
    var porImagen = juego.inicioImagen[w.f + "," + w.c + "," + w.d];
    if (porImagen) return { imagen: porImagen };
    var clave = w.d === "D" ? w.f + "," + (w.c - 1) : (w.f - 1) + "," + w.c;
    var pista = juego.pistaEn[clave];
    if (!pista) return null;
    for (var i = 0; i < pista.textos.length; i++) {
      if (pista.textos[i].d === w.d) {
        return { texto: pista.textos[i].t, casilla: clave };
      }
    }
    return null;
  }

  // -------------------------------------------------------- pintar rejilla

  function construirRejilla() {
    var p = juego.puzzle;
    var rejilla = document.getElementById("rejilla");
    rejilla.textContent = "";
    rejilla.style.width = "calc(var(--lado) * " + p.columnas + ")";
    rejilla.style.height = "calc(var(--lado) * " + p.filas + ")";

    juego.nodos = {};

    for (var f = 0; f < p.filas; f++) {
      for (var c = 0; c < p.columnas; c++) {
        var clave = f + "," + c;
        var tapada = juego.tapada[clave];
        if (tapada && !(tapada.f === f && tapada.c === c)) continue;

        var celda = document.createElement("div");
        celda.style.left = "calc(var(--lado) * " + c + ")";
        celda.style.top = "calc(var(--lado) * " + f + ")";

        if (tapada) {
          celda.className = "celda imagen";
          celda.style.width = "calc(var(--lado) * " + tapada.ancho + ")";
          celda.style.height = "calc(var(--lado) * " + tapada.alto + ")";
          var img = document.createElement("img");
          img.src = "img/" + tapada.activo + ".svg";
          img.alt = tapada.pie;
          celda.appendChild(img);
          celda.appendChild(punta(tapada.d));
          juego.nodos[clave] = celda;
        } else {
          celda.style.width = "var(--lado)";
          celda.style.height = "var(--lado)";
          if (esLetra(f, c)) {
            celda.className = "celda letra";
            celda.dataset.f = f;
            celda.dataset.c = c;
          } else {
            celda.className = "celda definicion";
            var pista = juego.pistaEn[clave];
            if (pista) {
              pista.textos.forEach(function (t) {
                var banda = document.createElement("div");
                banda.className = "banda";
                banda.dataset.base = pista.textos.length === 1 ? 0.19 : 0.155;
                banda.textContent = t.t;
                banda.appendChild(punta(t.d));
                celda.appendChild(banda);
              });
            }
          }
          juego.nodos[clave] = celda;
        }
        rejilla.appendChild(celda);
      }
    }

    escala = 1;
    aplicarLado();
    encajarTextos();
  }

  /** Encoge la definición que no quepa en su casilla.
      El factor se guarda una vez y luego el zoom lo escala solo. */
  function encajarTextos() {
    var bandas = document.querySelectorAll("#rejilla .banda");
    for (var i = 0; i < bandas.length; i++) {
      var banda = bandas[i];
      var factor = parseFloat(banda.dataset.base);
      banda.style.fontSize = "calc(var(--lado) * " + factor + ")";
      // Ocho intentos bastan para bajar de 0.19 a 0.09.
      for (var intento = 0; intento < 8; intento++) {
        if (banda.scrollHeight <= banda.clientHeight &&
            banda.scrollWidth <= banda.clientWidth) break;
        factor *= 0.9;
        banda.style.fontSize = "calc(var(--lado) * " + factor + ")";
      }
    }
  }

  function punta(direccion) {
    var p = document.createElement("i");
    p.className = "punta " + (direccion === "D" ? "derecha" : "abajo");
    return p;
  }

  /** Repinta letras, resaltes y cabecera sin reconstruir la rejilla. */
  function refrescar() {
    var w = palabraActual();
    var dentro = {};
    if (w) casillasDe(w).forEach(function (pos) { dentro[pos.f + "," + pos.c] = true; });

    var elegida = juego.seleccion
      ? juego.seleccion.f + "," + juego.seleccion.c : null;

    for (var clave in juego.nodos) {
      var nodo = juego.nodos[clave];
      if (nodo.classList.contains("letra")) {
        nodo.textContent = juego.letras[clave] || "";
        nodo.classList.toggle("resaltada", !!dentro[clave] && clave !== elegida);
        nodo.classList.toggle("elegida", clave === elegida);
      }
    }

    // La casilla de la definición en curso también se destaca
    var def = definicionDe(w);
    for (var clave2 in juego.nodos) {
      var n2 = juego.nodos[clave2];
      if (n2.classList.contains("definicion") || n2.classList.contains("imagen")) {
        var esta = def && (
          (def.casilla && def.casilla === clave2) ||
          (def.imagen && def.imagen.f + "," + def.imagen.c === clave2)
        );
        n2.classList.toggle("destacada", !!esta);
      }
    }

    pintarCabecera(w, def);
  }

  function pintarCabecera(w, def) {
    var caja = document.getElementById("cabeceraPista");
    caja.textContent = "";

    if (!w || !def) {
      var vacio = document.createElement("span");
      vacio.className = "sin-seleccion";
      vacio.textContent = "Toca una casilla para empezar";
      caja.appendChild(vacio);
      return;
    }

    if (def.imagen) {
      var img = document.createElement("img");
      img.src = "img/" + def.imagen.activo + ".svg";
      img.alt = "";
      caja.appendChild(img);
    } else {
      var flecha = document.createElement("span");
      flecha.className = "flecha-actual";
      flecha.textContent = w.d === "D" ? "→" : "↓";
      caja.appendChild(flecha);
    }

    var texto = document.createElement("div");
    texto.className = "texto";
    var linea = document.createElement("div");
    linea.className = "definicion";
    linea.textContent = def.imagen ? def.imagen.pie : def.texto;
    texto.appendChild(linea);
    var cuantas = document.createElement("div");
    cuantas.className = "cuantas";
    cuantas.textContent = w.n + " letras";
    texto.appendChild(cuantas);
    caja.appendChild(texto);
  }

  // --------------------------------------------------------- interacción

  function seleccionar(f, c) {
    if (!esLetra(f, c)) return;
    if (juego.seleccion && juego.seleccion.f === f && juego.seleccion.c === c) {
      var otra = juego.direccion === "D" ? "B" : "D";
      if (palabraEn({ f: f, c: c }, otra)) juego.direccion = otra;
    } else {
      juego.seleccion = { f: f, c: c };
      ajustarDireccion();
    }
    refrescar();
  }

  function escribir(letra) {
    if (!juego || !juego.seleccion) return;
    juego.letras[juego.seleccion.f + "," + juego.seleccion.c] = letra;
    comprobar();
    guardar();
    avanzar();
    refrescar();
  }

  function borrar() {
    if (!juego || !juego.seleccion) return;
    var clave = juego.seleccion.f + "," + juego.seleccion.c;
    if (juego.letras[clave]) {
      delete juego.letras[clave];
    } else {
      retroceder();
      delete juego.letras[juego.seleccion.f + "," + juego.seleccion.c];
    }
    if (juego.resuelto) { juego.resuelto = false; }
    guardar();
    refrescar();
  }

  function avanzar() {
    var w = palabraActual();
    if (!w || !juego.seleccion) return;
    var siguiente = juego.direccion === "D"
      ? { f: juego.seleccion.f, c: juego.seleccion.c + 1 }
      : { f: juego.seleccion.f + 1, c: juego.seleccion.c };
    if (dentroDe(w, siguiente)) juego.seleccion = siguiente;
  }

  function retroceder() {
    var w = palabraActual();
    if (!w || !juego.seleccion) return;
    var anterior = juego.direccion === "D"
      ? { f: juego.seleccion.f, c: juego.seleccion.c - 1 }
      : { f: juego.seleccion.f - 1, c: juego.seleccion.c };
    if (dentroDe(w, anterior)) juego.seleccion = anterior;
  }

  function dentroDe(w, pos) {
    if (w.d === "D") return pos.f === w.f && pos.c >= w.c && pos.c < w.c + w.n;
    return pos.c === w.c && pos.f >= w.f && pos.f < w.f + w.n;
  }

  function siguientePalabra() {
    var w = palabraActual();
    var lista = juego.puzzle.palabras;
    var desde = w ? lista.indexOf(w) : -1;
    for (var salto = 1; salto <= lista.length; salto++) {
      var cand = lista[(desde + salto + lista.length) % lista.length];
      var libres = casillasDe(cand).filter(function (pos) {
        return !juego.letras[pos.f + "," + pos.c];
      });
      if (libres.length || salto === lista.length) {
        juego.seleccion = libres[0] || casillasDe(cand)[0];
        juego.direccion = cand.d;
        break;
      }
    }
    refrescar();
  }

  /** Sin botón de comprobar: sólo mira si ya está entera y bien. */
  function comprobar() {
    var p = juego.puzzle;
    for (var f = 0; f < p.filas; f++) {
      for (var c = 0; c < p.columnas; c++) {
        if (!esLetra(f, c)) continue;
        if (juego.letras[f + "," + c] !== juego.matriz[f][c]) {
          juego.resuelto = false;
          return;
        }
      }
    }
    if (!juego.resuelto) {
      juego.resuelto = true;
      var aviso = document.getElementById("avisoResuelto");
      aviso.classList.remove("oculta");
    }
  }

  function guardar() {
    progreso[juego.puzzle.id] = {
      letras: juego.letras,
      resuelto: juego.resuelto
    };
    guardarProgreso();
  }

  function reiniciarPuzzle() {
    if (!confirm("Se borrará todo lo que hayas escrito en este autodefinido.")) return;
    juego.letras = {};
    juego.resuelto = false;
    juego.seleccion = primeraLibre();
    ajustarDireccion();
    guardar();
    refrescar();
  }

  // --------------------------------------------------------------- teclado

  function construirTeclado() {
    var filas = ["QWERTYUIOP", "ASDFGHJKLÑ", "ZXCVBNM"];
    var caja = document.getElementById("teclado");
    caja.textContent = "";

    filas.forEach(function (fila, i) {
      var div = document.createElement("div");
      div.className = "fila-teclas";

      if (i === 2) {
        div.appendChild(tecla("Saltar", "ancha", siguientePalabra));
      }
      fila.split("").forEach(function (letra) {
        div.appendChild(tecla(letra, "", function () { escribir(letra); }));
      });
      if (i === 2) {
        div.appendChild(tecla("⌫", "ancha", borrar));
      }
      caja.appendChild(div);
    });
  }

  function tecla(rotulo, extra, alPulsar) {
    var boton = document.createElement("button");
    boton.type = "button";
    boton.className = "tecla" + (extra ? " " + extra : "");
    boton.textContent = rotulo;
    boton.addEventListener("click", function (ev) {
      ev.preventDefault();
      alPulsar();
    });
    return boton;
  }

  // ------------------------------------------------------ zoom y tamaño

  var escala = 1;

  /** Casilla que hace que la rejilla entera quepa en pantalla. */
  function ladoBase() {
    if (!juego) return 34;
    var zona = document.getElementById("zonaRejilla");
    var ancho = zona.clientWidth - 16;
    var alto = zona.clientHeight - 16;
    if (ancho <= 0 || alto <= 0) return 34;
    return Math.max(20, Math.floor(Math.min(
      ancho / juego.puzzle.columnas,
      alto / juego.puzzle.filas
    )));
  }

  function aplicarLado() {
    var lado = Math.round(ladoBase() * escala);
    document.documentElement.style.setProperty("--lado", lado + "px");
  }

  function prepararZoom() {
    var zona = document.getElementById("zonaRejilla");
    var partida = 0;

    zona.addEventListener("touchstart", function (ev) {
      if (ev.touches.length === 2) partida = distancia(ev.touches);
    }, { passive: true });

    zona.addEventListener("touchmove", function (ev) {
      if (ev.touches.length !== 2 || !partida) return;
      ev.preventDefault();
      var factor = distancia(ev.touches) / partida;
      escala = Math.min(3, Math.max(1, escala * factor));
      partida = distancia(ev.touches);
      aplicarLado();
    }, { passive: false });

    zona.addEventListener("touchend", function (ev) {
      if (ev.touches.length < 2) partida = 0;
    }, { passive: true });
  }

  function distancia(toques) {
    var dx = toques[0].clientX - toques[1].clientX;
    var dy = toques[0].clientY - toques[1].clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  // --------------------------------------------------------------- ajustes

  function pintarAjustes() {
    var hechos = 0, empezados = 0;
    indice.puzzles.forEach(function (f) {
      var e = estadoDe(f.id);
      if (e.resuelto) hechos++;
      else if (Object.keys(e.letras || {}).length) empezados++;
    });

    var caja = document.getElementById("resumen");
    caja.textContent = "";
    var titulo = document.createElement("h2");
    titulo.textContent = "El libro";
    caja.appendChild(titulo);
    var lista = document.createElement("dl");
    [["Autodefinidos", indice.puzzles.length],
     ["Resueltos", hechos],
     ["Empezados", empezados]].forEach(function (par) {
      var dt = document.createElement("dt");
      dt.textContent = par[0];
      var dd = document.createElement("dd");
      dd.textContent = par[1];
      lista.appendChild(dt);
      lista.appendChild(dd);
    });
    caja.appendChild(lista);

    var estado = document.getElementById("estadoOffline");
    if (!("serviceWorker" in navigator)) {
      estado.textContent = "Este navegador no guarda la app para usarla sin conexión.";
    } else if (navigator.serviceWorker.controller) {
      estado.textContent = "El libro está guardado en el móvil.";
    } else {
      estado.textContent = "Guardando el libro… déjala abierta un momento.";
    }
  }

  // ----------------------------------------------------------------- arranque

  function conectarBotones() {
    document.getElementById("volver").addEventListener("click", function () {
      pintarIndice();
      mostrar("pantallaIndice");
    });
    document.getElementById("reiniciar").addEventListener("click", reiniciarPuzzle);
    document.getElementById("botonAjustes").addEventListener("click", function () {
      pintarAjustes();
      mostrar("pantallaAjustes");
    });
    document.getElementById("cerrarAjustes").addEventListener("click", function () {
      pintarIndice();
      mostrar("pantallaIndice");
    });
    document.getElementById("cerrarAviso").addEventListener("click", function () {
      document.getElementById("avisoResuelto").classList.add("oculta");
    });
    document.getElementById("borrarTodo").addEventListener("click", function () {
      if (!confirm("¿Borrar lo escrito en los quinientos autodefinidos?")) return;
      progreso = {};
      guardarProgreso();
      try { localStorage.removeItem(CLAVE_ULTIMO); } catch (e) {}
      pintarAjustes();
      alert("Progreso borrado.");
    });

    document.querySelectorAll(".filtro").forEach(function (boton) {
      boton.addEventListener("click", function () {
        document.querySelectorAll(".filtro").forEach(function (o) {
          o.classList.remove("activo");
        });
        boton.classList.add("activo");
        filtro = boton.dataset.dificultad;
        pintarIndice();
      });
    });

    document.getElementById("rejilla").addEventListener("click", function (ev) {
      var celda = ev.target.closest(".celda.letra");
      if (!celda) return;
      seleccionar(Number(celda.dataset.f), Number(celda.dataset.c));
    });

    document.addEventListener("keydown", function (ev) {
      if (document.getElementById("pantallaPuzzle").classList.contains("oculta")) return;
      var tecla = ev.key.toUpperCase();
      if (LETRAS.indexOf(tecla) !== -1 && tecla.length === 1) {
        escribir(tecla);
      } else if (ev.key === "Backspace") {
        ev.preventDefault();
        borrar();
      } else if (ev.key === "Tab") {
        ev.preventDefault();
        siguientePalabra();
      }
    });

    window.addEventListener("resize", function () {
      if (juego) aplicarLado();
    });
  }

  function arrancar() {
    traer("datos/indice.json").then(function (datos) {
      indice = datos;
      porBloque = datos.porBloque || 50;
      construirTeclado();
      conectarBotones();
      prepararZoom();
      pintarIndice();
      document.getElementById("cargando").classList.add("oculta");
      mostrar("pantallaIndice");
    }).catch(function (e) {
      document.getElementById("cargando").textContent =
        "No se pudo cargar el libro. Comprueba la conexión y vuelve a entrar.";
      console.error(e);
    });

    if ("serviceWorker" in navigator) {
      window.addEventListener("load", function () {
        navigator.serviceWorker.register("sw.js").catch(function (e) {
          console.warn("sin modo sin conexión:", e);
        });
      });
    }
  }

  arrancar();
})();
