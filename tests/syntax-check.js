// Confere que todo JS do app é sintaticamente válido e que index.html / sw.js
// não referenciam arquivos inexistentes (nem esquecem arquivos que existem).
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const RAIZ = path.join(__dirname, "..");
const IGNORAR = ["legacy-desktop", "node_modules", ".git"];

function listarJs(dir, saida = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (IGNORAR.includes(e.name)) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) listarJs(p, saida);
    else if (e.name.endsWith(".js")) saida.push(p);
  }
  return saida;
}

let falhas = 0;
const arquivos = listarJs(RAIZ);

for (const f of arquivos) {
  const rel = path.relative(RAIZ, f).replace(/\\/g, "/");
  try {
    new vm.Script(fs.readFileSync(f, "utf8"), { filename: rel });
  } catch (e) {
    console.log(`FAIL sintaxe  ${rel}: ${e.message}`);
    falhas++;
  }
}
console.log(`ok  ${arquivos.length} arquivos .js com sintaxe valida`);

// index.html só pode apontar para arquivos que existem.
const html = fs.readFileSync(path.join(RAIZ, "index.html"), "utf8");
const refs = [...html.matchAll(/(?:src|href)="\.\/([^"]+)"/g)].map((m) => m[1]);
for (const r of refs) {
  if (!fs.existsSync(path.join(RAIZ, r))) { console.log(`FAIL index.html aponta para ${r}, que nao existe`); falhas++; }
}
console.log(`ok  ${refs.length} referencias do index.html existem`);

// Todo JS carregado pelo index.html precisa estar no cache do service worker,
// senão o app quebra offline logo depois de instalar.
const sw = fs.readFileSync(path.join(RAIZ, "sw.js"), "utf8");
for (const r of refs.filter((x) => x.endsWith(".js"))) {
  if (!sw.includes(`"./${r}"`)) { console.log(`FAIL ${r} carregado no index.html mas ausente do cache em sw.js`); falhas++; }
}
console.log("ok  service worker cobre todos os scripts do index.html");

// Nenhuma credencial de exemplo pode voltar para o código do app.
for (const f of arquivos.filter((x) => !x.includes("tests"))) {
  const txt = fs.readFileSync(f, "utf8");
  if (/["']123456["']/.test(txt)) {
    console.log(`FAIL credencial padrao encontrada em ${path.relative(RAIZ, f)}`);
    falhas++;
  }
}
console.log("ok  nenhuma credencial padrao no codigo do app");

if (falhas) { console.log(`\n${falhas} problema(s).`); process.exit(1); }
console.log("PASS: sintaxe, referencias e cache do service worker");
