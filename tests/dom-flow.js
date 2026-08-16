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

  // ---- 6. detalhe da OS: acoes nao podem duplicar a tela -----------------
  {
    const os = dom.window.App.db.all("ordens")[0];
    dom.window.location.hash = "#/os/" + os.id;
    dom.window.__renderRoute();
    await esperar(60);

    const conta = (sel) => doc.querySelectorAll(sel).length;
    assert.strictEqual(conta(".check-grid"), 1, "deveria haver um unico checklist");

    // marca o primeiro item do checklist
    const antes = doc.querySelectorAll(".check-item")[0];
    const rotulo = antes.textContent;
    antes.dispatchEvent(new dom.window.Event("click", { bubbles: true }));
    await esperar(60);

    assert.strictEqual(conta(".check-grid"), 1,
      `clicar no checklist duplicou a tela: ${conta(".check-grid")} checklists, ${conta(".big-progress")} barras de progresso`);
    const depois = [...doc.querySelectorAll(".check-item")].find((x) => x.textContent === rotulo);
    assert(depois.classList.contains("checked"), "o item deveria ficar marcado na tela");
    assert(dom.window.App.db.byId("ordens", os.id).checklist[rotulo.trim()], "e persistido");

    // desmarcar volta ao estado anterior
    depois.dispatchEvent(new dom.window.Event("click", { bubbles: true }));
    await esperar(60);
    assert.strictEqual(conta(".check-grid"), 1, "desmarcar tambem nao pode duplicar");
    assert(![...doc.querySelectorAll(".check-item")].find((x) => x.textContent === rotulo).classList.contains("checked"),
      "o item deveria desmarcar");

    // botoes de progresso re-renderizam do mesmo jeito
    doc.querySelectorAll(".progress-btn")[2].dispatchEvent(new dom.window.Event("click", { bubbles: true }));
    await esperar(60);
    assert.strictEqual(conta(".big-progress"), 1, "botao de progresso duplicou a tela");
    assert.strictEqual(dom.window.App.db.byId("ordens", os.id).progresso, 50, "progresso salvo");
    console.log("ok  checklist e progresso da OS atualizam sem duplicar a tela");
  }

  // ---- 7. formulario modal abre com overlay, fecha e salva ---------------
  {
    dom.window.location.hash = "#/clientes";
    dom.window.__renderRoute();
    await esperar(60);
    const clique = (n) => n.dispatchEvent(new dom.window.Event("click", { bubbles: true }));
    const abrir = () => clique([...doc.querySelectorAll("button")].find((b) => /Novo Cliente/i.test(b.textContent)));
    const conta = () => ({ bg: doc.querySelectorAll(".modal-bg").length, modal: doc.querySelectorAll(".modal").length });

    abrir();
    await esperar(80);
    assert.deepStrictEqual(conta(), { bg: 1, modal: 1 }, "modal deve abrir dentro do overlay .modal-bg");
    assert(![...doc.body.children].some((x) => x.classList.contains("modal")),
      "o modal nao pode ser filho direto do body: sem overlay ele nao centraliza nem escurece o fundo");

    clique([...doc.querySelectorAll(".modal-foot button")].find((b) => /Cancelar/i.test(b.textContent)));
    await esperar(80);
    assert.deepStrictEqual(conta(), { bg: 0, modal: 0 }, "Cancelar deve remover o modal do DOM");

    const antes = dom.window.App.db.count("clientes");
    abrir();
    await esperar(80);
    doc.querySelectorAll(".modal-body input")[0].value = "Cliente De Teste";
    clique([...doc.querySelectorAll(".modal-foot button")].find((b) => /Salvar/i.test(b.textContent)));
    await esperar(150);
    assert.deepStrictEqual(conta(), { bg: 0, modal: 0 }, "Salvar deve remover o modal do DOM");
    assert.strictEqual(dom.window.App.db.count("clientes"), antes + 1, "o cliente deveria ter sido criado");
    assert(dom.window.App.db.all("clientes").some((c) => c.nome === "Cliente De Teste"), "com o nome informado");
    console.log("ok  formulario modal abre com overlay, fecha em Cancelar/Salvar e persiste");
  }

  // ---- 8. exportacao CSV: injecao de formula e uniao de colunas ----------
  {
    const ui = dom.window.App.ui;

    // Excel/Sheets executam celulas que comecam com = + - @
    for (const perigoso of ["=1+1", "+cmd", "-2+3", "@SUM(A1)"]) {
      const saida = ui.csvCelula(perigoso);
      assert(saida.startsWith(`"'`), `celula perigosa nao neutralizada: ${perigoso} -> ${saida}`);
      assert(saida.includes(perigoso), "o texto original precisa continuar legivel");
    }
    assert.strictEqual(ui.csvCelula("Joao Silva"), '"Joao Silva"', "texto normal nao ganha prefixo");
    assert.strictEqual(ui.csvCelula('a "b" c'), '"a ""b"" c"', "aspas continuam escapadas");
    assert.strictEqual(ui.csvCelula(null), '""', "nulo vira vazio");

    // cabecalho e a uniao das chaves, nao as do primeiro registro
    const registros = [{ nome: "So nome", id: 1 }, { nome: "Completo", cpf: "x", email: "y", id: 2 }];
    // Array.from: o retorno vem do realm do jsdom, e deepStrictEqual compara protótipos.
    assert.deepStrictEqual(Array.from(ui.chavesDe(registros)), ["nome", "id", "cpf", "email"],
      "colunas de registros posteriores nao podem sumir");
    assert.deepStrictEqual(Array.from(ui.chavesDe(registros, ["id"])), ["nome", "cpf", "email"], "ignora as chaves pedidas");

    const texto = ui.csv([["a", "b"], [1, "=2"]]);
    assert(texto.startsWith("﻿"), "BOM na frente para o Excel ler UTF-8");
    assert(texto.includes("\r\n"), "quebra de linha CRLF");
    console.log("ok  CSV neutraliza formula, escapa aspas e usa a uniao das colunas");
  }

  // ---- 9. com usuario cadastrado, vai para o login -----------------------
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
