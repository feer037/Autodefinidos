/* Service worker: guarda el libro entero para que funcione sin conexión.
   La lista de ficheros y la versión vienen de precache.json, que escribe
   Tools/construir_web.py. */

var NOMBRE_BASE = "autodefinidos";
var cacheActual = null;

self.addEventListener("install", function (ev) {
  ev.waitUntil(
    fetch("precache.json", { cache: "no-cache" })
      .then(function (r) { return r.json(); })
      .then(function (lista) {
        cacheActual = NOMBRE_BASE + "-" + lista.version;
        return caches.open(cacheActual).then(function (cache) {
          // De diez en diez: quinientas peticiones a la vez ahogan el móvil.
          var ficheros = lista.ficheros.concat(["precache.json"]);
          return porTandas(ficheros, 10, function (tanda) {
            return cache.addAll(tanda).catch(function (e) {
              // Un fichero suelto que falle no debe tumbar la instalación.
              console.warn("no se pudo guardar", tanda, e);
            });
          });
        });
      })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (ev) {
  ev.waitUntil(
    fetch("precache.json", { cache: "no-cache" })
      .then(function (r) { return r.json(); })
      .then(function (lista) {
        var vigente = NOMBRE_BASE + "-" + lista.version;
        return caches.keys().then(function (nombres) {
          return Promise.all(nombres.map(function (n) {
            if (n.indexOf(NOMBRE_BASE) === 0 && n !== vigente) {
              return caches.delete(n);
            }
          }));
        });
      })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (ev) {
  var peticion = ev.request;
  if (peticion.method !== "GET") return;
  if (new URL(peticion.url).origin !== self.location.origin) return;

  // Primero lo guardado: la app es un libro cerrado, no cambia sola.
  ev.respondWith(
    caches.match(peticion, { ignoreSearch: true }).then(function (guardado) {
      if (guardado) return guardado;
      return fetch(peticion).then(function (respuesta) {
        if (respuesta && respuesta.ok && respuesta.type === "basic") {
          var copia = respuesta.clone();
          caches.keys().then(function (nombres) {
            var mia = nombres.filter(function (n) {
              return n.indexOf(NOMBRE_BASE) === 0;
            })[0];
            if (mia) caches.open(mia).then(function (c) { c.put(peticion, copia); });
          });
        }
        return respuesta;
      }).catch(function () {
        // Sin red y sin copia: al menos devolvemos la portada.
        if (peticion.mode === "navigate") return caches.match("index.html");
        throw new Error("sin conexión y sin copia de " + peticion.url);
      });
    })
  );
});

function porTandas(lista, tamano, hacer) {
  var i = 0;
  function siguiente() {
    if (i >= lista.length) return Promise.resolve();
    var tanda = lista.slice(i, i + tamano);
    i += tamano;
    return hacer(tanda).then(siguiente);
  }
  return siguiente();
}
