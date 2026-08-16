// Smoke: seed, CRUD, autenticação, validação, corrupção de storage e quota.
const assert = require("assert");
const { criarContexto, comAdmin } = require("./context");

(async () => {
  // --- setup de primeiro acesso -------------------------------------------
  {
    const { ctx } = criarContexto();
    assert(ctx.App.auth.precisaSetup(), "app novo deve exigir setup");
    assert.strictEqual(await ctx.App.auth.login("isac", "123456"), null, "nao pode existir usuario padrao");
    await ctx.App.auth.criarAdmin("Admin Teste", "admin", "senha-forte-123");
    assert(!ctx.App.auth.precisaSetup(), "apos criar admin nao exige mais setup");
  }

  // --- dados de exemplo sao opt-in ----------------------------------------
  {
    const { ctx } = await comAdmin();
    assert.strictEqual(ctx.App.db.count("clientes"), 0, "sem demo, base comeca vazia");
    ctx.App.seed.demo();
    assert(ctx.App.db.count("clientes") >= 3);
    assert(ctx.App.db.count("ordens") >= 3);
    assert.strictEqual(ctx.App.seed.demo(), false, "demo nao duplica");
  }

  // --- login --------------------------------------------------------------
  {
    const { ctx, senha } = await comAdmin();
    assert(await ctx.App.auth.login("admin", senha), "login valido");
    assert(await ctx.App.auth.login("ADMIN", senha), "usuario e case-insensitive");
    assert.strictEqual(await ctx.App.auth.login("admin", "errada"), null, "senha errada");
    assert.strictEqual(await ctx.App.auth.login("ninguem", senha), null, "usuario inexistente");
    assert(ctx.App.auth.ehAdmin());
    ctx.App.auth.logout();
    assert.strictEqual(ctx.App.auth.atual(), null);
  }

  // --- CRUD ---------------------------------------------------------------
  {
    const { ctx } = await comAdmin();
    ctx.App.seed.demo();
    const before = ctx.App.db.count("clientes");
    const c = ctx.App.db.insert("clientes", { nome: "Teste" });
    assert(c && c.id);
    assert.strictEqual(ctx.App.db.count("clientes"), before + 1);
    assert(ctx.App.db.update("clientes", c.id, { nome: "Teste 2" }));
    assert.strictEqual(ctx.App.db.byId("clientes", c.id).nome, "Teste 2");
    assert(ctx.App.db.remove("clientes", c.id));
    assert.strictEqual(ctx.App.db.byId("clientes", c.id), null);
  }

  // --- storage corrompido deve recuperar, nao quebrar ---------------------
  {
    const { ctx, store } = criarContexto();
    store.set("autocontrol:v1", '{"clientes":"quebrado","ordens":null}');
    ctx.App.db.reset();
    ctx.App.db.load();
    assert(Array.isArray(ctx.App.db.all("clientes")));
    assert(Array.isArray(ctx.App.db.all("ordens")));
  }

  // --- falha de quota nao deixa registro fantasma -------------------------
  {
    const { ctx, setFail } = await comAdmin();
    const n = ctx.App.db.count("clientes");
    setFail(true);
    assert.strictEqual(ctx.App.db.insert("clientes", { nome: "Quota" }), null);
    setFail(false);
    assert.strictEqual(ctx.App.db.count("clientes"), n);
  }

  console.log("PASS: setup/seed/auth/db/validation smoke + corrupcao + quota");
})().catch((e) => { console.error(e); process.exit(1); });
