// Fluxo ponta a ponta num DOM headless (jsdom): carrega os mesmos arquivos que
// o index.html carrega, na mesma ordem, e exercita primeiro acesso, login e as
// rotas principais — falhando se qualquer uma escrever no console.error.
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const assert = require("assert");
const { JSDOM } = require("jsdom");

const RAIZ = path.join(__dirname, "..");

// Mesma ordem do index.html. Se divergir, o teste de sincronia abaixo acusa.
const ORDEM = [
  "js/validation.js", "js/db.js", "js/auth.js", "js/seed.js", "js/ui.js",
  "js/crud.js", "js/entities.js",
  "js/views/setup.js", "js/views/login.js", "js/views/dashboard.js",
  "js/views/workshop.js", "js/views/os-detail.js", "js/views/mechanic.js",
  "js/views/central.js", "js/app.js",
];

const erros = [];

function novoDom() {
  const dom = new JSDOM(`<!doctype html><html><body><div id="app"></div></body></html>`, {
    url: "http://localhost:8000/", runScripts: "outside-only", pretendToBeVisual: true,
  });
  const ctx = dom.getInternalVMContext();
  // jsdom expõe window.crypto sem .subtle (e sem TextEncoder no contexto do vm).
  // Navegadores reais têm ambos; aqui precisamos injetar para o PBKDF2 rodar.
  const globais = { crypto: require("crypto").webcrypto, TextEncoder, TextDecoder };
  for (const [k, v] of Object.entries(globais)) {
    Object.defineProperty(dom.window, k, { value: v, configurable: true, writable: true });
  }
  if (!dom.window.crypto.subtle) throw new Error("harness: crypto.subtle ausente");
  dom.window.addEventListener("error", (e) => erros.push("window.error: " + e.message));
  const origErr = dom.window.console.error;
  dom.window.console.error = (...a) => { erros.push("console.error: " + a.join(" ")); origErr(...a); };
  for (const f of ORDEM) {
    vm.runInContext(fs.readFileSync(path.join(RAIZ, f), "utf8"), ctx, { filename: f });
  }
  return dom;
}

const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  // ---- 0. a ordem acima bate com o index.html? ----------------------------
  {
    const html = fs.readFileSync(path.join(RAIZ, "index.html"), "utf8");
    const noHtml = [...html.matchAll(/<script src="\.\/([^"]+)"/g)].map((m) => m[1]);
    assert.deepStrictEqual(noHtml, ORDEM, "index.html e o teste divergiram na lista de scripts");
    const sw = fs.readFileSync(path.join(RAIZ, "sw.js"), "utf8");
    for (const f of ORDEM) assert(sw.includes(`"./${f}"`), `${f} nao esta no cache do service worker`);
    console.log("ok  index.html e sw.js listam os mesmos " + ORDEM.length + " scripts");
  }

  // ---- 1. primeiro acesso mostra a tela de setup -------------------------
  let dom = novoDom();
  let doc = dom.window.document;
  await esperar(120);
  let texto = doc.body.textContent;

  assert(texto.includes("Crie seu administrador"), "deveria abrir a tela de setup");
  assert(texto.includes("PRIMEIRO ACESSO"), "faltou o rotulo de primeiro acesso");
  assert(!texto.includes("123456"), "credencial padrao ainda aparece na tela");
  assert(!/\bisac\b/.test(texto), "usuario padrao ainda aparece na tela");
  assert.strictEqual(doc.querySelectorAll(".login-card input").length, 5, "5 campos no setup");
  console.log("ok  tela de primeiro acesso renderiza, sem credencial padrao");

  const [nome, user, senha, senha2, demo] = doc.querySelectorAll(".login-card input");
  const form = doc.querySelector("form.login-card");
  const erroTexto = () => doc.querySelector(".login-error")?.textContent ?? "(tela trocou)";
  const submeter = async () => {
    form.dispatchEvent(new dom.window.Event("submit", { bubbles: true, cancelable: true }));
    await esperar(400);
  };

  // ---- 2. senha fraca e confirmacao divergente sao bloqueadas ------------
  nome.value = "Isac Neto"; user.value = "isac"; senha.value = "123"; senha2.value = "123";
  await submeter();
  assert(erroTexto().includes("8 caracteres"), "senha curta deve ser rejeitada");

  senha.value = "12345678901"; senha2.value = "12345678901";
  await submeter();
  assert(erroTexto().includes("apenas números"), "senha so de numeros deve ser rejeitada");

  senha.value = "oficina-forte-2026"; senha2.value = "outra-coisa";
  await submeter();
  assert(erroTexto().includes("não conferem"), "confirmacao deve bater");
  console.log("ok  senha fraca, so-numeros e confirmacao divergente rejeitadas");

  // ---- 3. criacao valida entra no app ------------------------------------
  senha2.value = "oficina-forte-2026";
  demo.checked = true;
  await submeter();
  assert(doc.querySelector(".shell"),
    `deveria ter entrado no app. erro na tela: ${JSON.stringify(erroTexto())}; ` +
    `usuarios=${dom.window.App.db.count("usuarios")}; sessao=${dom.window.localStorage.getItem("autocontrol:sessao")}`);
  assert(doc.body.textContent.includes("Isac Neto"), "nome do usuario no perfil");
  console.log("ok  admin criado, sessao iniciada, app renderizou");

  // ---- 4. como a senha foi persistida ------------------------------------
  const salvo = JSON.parse(dom.window.localStorage.getItem("autocontrol:v1"));
  assert(String(salvo.usuarios[0].senha).startsWith("pbkdf2$"), "senha deve estar em PBKDF2");
  assert(!JSON.stringify(salvo).includes("oficina-forte-2026"), "senha em texto puro no storage");
  assert(salvo.clientes.length >= 3, "dados de exemplo carregados pelo checkbox");
  console.log("ok  senha em PBKDF2, nada em texto puro, demo sob demanda");

  // ---- 5. todas as rotas renderizam sem erro -----------------------------
  const rotas = ["dashboard", "patio", "ordens", "clientes", "veiculos", "agenda",
    "financeiro", "estoque", "fornecedores", "relatorios", "indicadores",
    "usuarios", "configuracoes", "central", "checklists", "logs"];
  let falhas = 0;
  for (const r of rotas) {
    const antes = erros.length;
    dom.window.location.hash = "#/" + r;
    dom.window.__renderRoute && dom.window.__renderRoute();
    await esperar(30);
    if (erros.length > antes) { console.log(`FAIL rota ${r}: ${erros.slice(antes).join(" | ")}`); falhas++; }
  }
  assert.strictEqual(falhas, 0, `${falhas} rota(s) com erro`);
  console.log("ok  " + rotas.length + " rotas renderizadas sem erro");

  // ---- 6. com usuario cadastrado, vai para o login -----------------------
  const dump = dom.window.localStorage.getItem("autocontrol:v1");
  dom = novoDom();
  dom.window.localStorage.setItem("autocontrol:v1", dump);
  const ctx2 = dom.getInternalVMContext();
  vm.runInContext("App.db.invalidate(); App.auth.logout();", ctx2);
  vm.runInContext(fs.readFileSync(path.join(RAIZ, "js/app.js"), "utf8"), ctx2, { filename: "js/app.js" });
  await esperar(120);
  const t2 = dom.window.document.body.textContent;
  assert(t2.includes("Bem-vindo de volta"), "com usuario cadastrado deve ir para o login");
  assert(!t2.includes("Crie seu administrador"), "nao deve voltar ao setup");
  assert(!t2.includes("123456"), "login nao pode sugerir credencial");
  console.log("ok  com usuario existente vai para o login, sem dica de credencial");

  if (erros.length) {
    console.log("\n--- erros de console capturados ---");
    erros.forEach((e) => console.log("  " + e));
    process.exit(1);
  }
  console.log("PASS: fluxo completo no DOM, sem erros de console");
})().catch((e) => {
  console.error("\nFALHOU:", e.message);
  erros.forEach((x) => console.error("  " + x));
  process.exit(1);
});
