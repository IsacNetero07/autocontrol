// Servidor estático de desenvolvimento. O app precisa de uma origem http real:
// service worker e crypto.subtle não funcionam abrindo o index.html via file://.
// localhost conta como contexto seguro em todos os navegadores atuais.
const http = require("http");
const fs = require("fs");
const path = require("path");

const RAIZ = path.join(__dirname, "..");
const PORTA = Number(process.env.PORT) || 8000;
const TIPOS = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".webmanifest": "application/manifest+json; charset=utf-8",
  ".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon",
};

http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split("?")[0]);
  let rel = url === "/" ? "index.html" : url.replace(/^\/+/, "");
  const alvo = path.join(RAIZ, rel);

  // Não serve nada fora da raiz do projeto.
  if (!alvo.startsWith(RAIZ)) { res.writeHead(403).end("Forbidden"); return; }

  fs.readFile(alvo, (err, buf) => {
    if (err) { res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" }).end("404 " + rel); return; }
    res.writeHead(200, {
      "Content-Type": TIPOS[path.extname(alvo)] || "application/octet-stream",
      // Sem cache: o service worker já cacheia, e cache duplo atrapalha o dev.
      "Cache-Control": "no-store",
    });
    res.end(buf);
  });
}).listen(PORTA, () => {
  console.log(`AutoControl em http://localhost:${PORTA}`);
  console.log("Ctrl+C para parar.");
});
