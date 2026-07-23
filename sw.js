// Service worker do AutoControl. Cache do app shell para funcionar offline.
// Ao mudar arquivos, suba a versão (CACHE) para forçar atualização.
const CACHE = "autocontrol-v1";

const ARQUIVOS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./css/styles.css",
  "./js/validation.js",
  "./js/db.js",
  "./js/auth.js",
  "./js/seed.js",
  "./js/ui.js",
  "./js/crud.js",
  "./js/entities.js",
  "./js/views/login.js",
  "./js/views/dashboard.js",
  "./js/app.js",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/apple-touch-icon.png",
  "./icons/favicon-32.png"
];

self.addEventListener("install", (evento) => {
  evento.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ARQUIVOS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (evento) => {
  evento.waitUntil(
    caches.keys().then((chaves) =>
      Promise.all(chaves.filter((c) => c !== CACHE).map((c) => caches.delete(c)))
    )
  );
  self.clients.claim();
});

// Cache-first: rápido e funciona offline. Se não achar no cache, busca na rede.
self.addEventListener("fetch", (evento) => {
  if (evento.request.method !== "GET") return;
  evento.respondWith(
    caches.match(evento.request).then((resposta) => {
      if (resposta) return resposta;
      return fetch(evento.request)
        .then((rede) => {
          const copia = rede.clone();
          caches.open(CACHE).then((cache) => cache.put(evento.request, copia));
          return rede;
        })
        .catch(() => caches.match("./index.html"));
    })
  );
});
