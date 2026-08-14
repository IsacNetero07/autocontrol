const CACHE = "autocontrol-blue-v5";
const ASSETS = [
  "./", "./index.html", "./manifest.webmanifest", "./css/styles.css",
  "./js/validation.js", "./js/db.js", "./js/auth.js", "./js/seed.js", "./js/ui.js",
  "./js/crud.js", "./js/entities.js", "./js/app.js",
  "./js/views/login.js", "./js/views/dashboard.js", "./js/views/workshop.js",
  "./js/views/os-detail.js", "./js/views/mechanic.js", "./js/views/central.js",
  "./icons/favicon-32.png", "./icons/apple-touch-icon.png", "./icons/icon-192.png", "./icons/icon-512.png"
];
self.addEventListener("install", e => e.waitUntil(caches.open(CACHE).then(async c => { for(const asset of ASSETS){ try{ await c.add(asset); }catch(err){ console.warn("Cache ignorado:",asset); } } }).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(caches.match(e.request).then(cached => cached || fetch(e.request).then(r => {
    const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return r;
  }).catch(() => caches.match("./index.html"))));
});
