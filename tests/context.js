// Carrega os módulos do app num contexto isolado, simulando o navegador.
// Injeta as intrínsecas do host (crypto, TextEncoder, Uint8Array) para que
// PBKDF2 em js/auth.js funcione sem falha de brand-check entre realms.
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const RAIZ = path.join(__dirname, "..");
const MODULOS = ["js/validation.js", "js/db.js", "js/auth.js", "js/seed.js"];

function criarContexto() {
  const store = new Map();
  let falharStorage = false;
  const localStorage = {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => { if (falharStorage) throw new Error("quota"); store.set(k, String(v)); },
    removeItem: (k) => store.delete(k),
  };
  const ctx = {
    window: null, localStorage, console,
    App: { ui: { toast() {} } },
    Intl, Date, JSON, Number, String, Math,
    crypto, TextEncoder, TextDecoder, Uint8Array, btoa, atob,
  };
  ctx.window = ctx;
  vm.createContext(ctx);
  for (const f of MODULOS) {
    vm.runInContext(fs.readFileSync(path.join(RAIZ, f), "utf8"), ctx, { filename: f });
  }
  return { ctx, store, setFail: (v) => { falharStorage = v; } };
}

// Atalho: contexto já com um administrador criado.
async function comAdmin(senha = "senha-forte-123") {
  const h = criarContexto();
  await h.ctx.App.auth.criarAdmin("Admin Teste", "admin", senha);
  return { ...h, senha };
}

module.exports = { criarContexto, comAdmin, MODULOS, RAIZ };
