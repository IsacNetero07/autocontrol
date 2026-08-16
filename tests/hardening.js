// Hardening: rollback em falha de storage, corrupção por coleção, validações,
// regras de senha e migração de hash legado.
const assert = require("assert");
const { criarContexto, comAdmin } = require("./context");

(async () => {
  // --- corrupção por coleção ----------------------------------------------
  {
    const { ctx, store } = criarContexto();
    for (const [k, v] of Object.entries({ clientes: "x", veiculos: null, ordens: {} })) {
      store.set("autocontrol:v1", JSON.stringify({ [k]: v }));
      ctx.App.db.reset();
      ctx.App.db.load();
      assert(Array.isArray(ctx.App.db.all(k)), `colecao ${k} deve virar array`);
    }
  }

  // --- coleção inválida é rejeitada ---------------------------------------
  {
    const { ctx } = criarContexto();
    assert.throws(() => ctx.App.db.all("naoexiste"), /Cole/, "colecao invalida deve lancar");
  }

  // --- insert falho faz rollback da sequência ------------------------------
  {
    const { ctx, setFail } = await comAdmin();
    ctx.App.seed.demo();
    const before = ctx.App.db.count("clientes");
    const seqBefore = ctx.App.db.load()._seq.clientes;
    setFail(true);
    assert.strictEqual(ctx.App.db.insert("clientes", { nome: "quota" }), null);
    setFail(false);
    assert.strictEqual(ctx.App.db.count("clientes"), before);
    assert.strictEqual(ctx.App.db.load()._seq.clientes, seqBefore, "seq nao pode avancar");
  }

  // --- remove falho preserva o registro ------------------------------------
  {
    const { ctx, setFail } = await comAdmin();
    const id = ctx.App.db.insert("clientes", { nome: "remove" }).id;
    setFail(true);
    assert.strictEqual(ctx.App.db.remove("clientes", id), false);
    setFail(false);
    assert(ctx.App.db.byId("clientes", id), "registro deve continuar apos falha");
  }

  // --- validação CPF/CNPJ --------------------------------------------------
  {
    const { ctx } = criarContexto();
    const v = ctx.App.validation;
    assert(v.cpfValido("52998224725"));
    assert(!v.cpfValido("11111111111"));
    assert(!v.cpfValido("123"));
    assert(v.cnpjValido("11222333000181"));
    assert(!v.cnpjValido("11111111111111"));
  }

  // --- regras de senha -----------------------------------------------------
  {
    const { ctx } = criarContexto();
    const val = ctx.App.auth.validarCredenciais;
    assert(val("ab", "senha-forte-123"), "usuario curto e rejeitado");
    assert(val("admin", "curta"), "senha curta e rejeitada");
    assert(val("admin", "12345678901"), "senha so de numeros e rejeitada");
    assert.strictEqual(val("admin", "senha-forte-123"), null, "credencial valida passa");
  }

  // --- senha não é gravada em texto puro nem em hash legado ---------------
  {
    const { ctx, senha } = await comAdmin();
    const u = ctx.App.db.all("usuarios")[0];
    assert(!String(u.senha).includes(senha), "senha nunca em texto puro");
    assert(String(u.senha).startsWith("pbkdf2$"), "deve usar PBKDF2");
    const [, iter] = String(u.senha).split("$");
    assert(Number(iter) >= 100000, "iteracoes suficientes");
  }

  // --- hash legado ainda autentica e migra para PBKDF2 ---------------------
  {
    const { ctx } = criarContexto();
    ctx.App.db.insert("usuarios", {
      nome: "Antigo", usuario: "antigo",
      senha: ctx.App.auth.hashSenha("123456"), nivel: "admin",
    });
    assert(await ctx.App.auth.login("antigo", "123456"), "instalacao antiga continua entrando");
    const u = ctx.App.db.all("usuarios")[0];
    assert(String(u.senha).startsWith("pbkdf2$"), "hash legado deve migrar no login");
    assert(await ctx.App.auth.login("antigo", "123456"), "login continua valido apos migracao");
    assert.strictEqual(await ctx.App.auth.login("antigo", "outra"), null);
  }

  // --- troca de senha ------------------------------------------------------
  {
    const { ctx, senha } = await comAdmin();
    const u = ctx.App.db.all("usuarios")[0];
    assert.strictEqual(await ctx.App.auth.trocarSenha(u.id, "errada", "nova-senha-456"), null);
    assert(await ctx.App.auth.trocarSenha(u.id, senha, "nova-senha-456"));
    assert.strictEqual(await ctx.App.auth.login("admin", senha), null, "senha antiga nao vale mais");
    assert(await ctx.App.auth.login("admin", "nova-senha-456"));
  }

  console.log("PASS: hardening, corrupcao, rollback de quota, senhas, migracao de hash");
})().catch((e) => { console.error(e); process.exit(1); });
