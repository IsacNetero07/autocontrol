const fs=require('fs'),vm=require('vm'),assert=require('assert');
function makeCtx(){const store=new Map();let fail=false;const localStorage={getItem:k=>store.has(k)?store.get(k):null,setItem:(k,v)=>{if(fail)throw new Error('quota');store.set(k,String(v))},removeItem:k=>store.delete(k)};const ctx={window:null,localStorage,console,App:{ui:{toast(){}}},Intl,Date,JSON,Number,String,Math};ctx.window=ctx;vm.createContext(ctx);for(const f of ['js/validation.js','js/db.js','js/auth.js','js/seed.js'])vm.runInContext(fs.readFileSync(f,'utf8'),ctx,{filename:f});return {ctx,store,setFail:v=>fail=v};}
let {ctx,store,setFail}=makeCtx();
ctx.App.seed.ensure();
assert(ctx.App.db.count('clientes')>=3);assert(ctx.App.db.count('ordens')>=3);assert(ctx.App.auth.login('ISAC','123456'));assert(ctx.App.auth.ehAdmin());assert(!ctx.App.auth.login('isac','errada'));
for(const [k,v] of Object.entries({clientes:'x',veiculos:null,ordens:{}})){store.set('autocontrol:v1',JSON.stringify({[k]:v}));ctx.App.db.reset();ctx.App.db.load();assert(Array.isArray(ctx.App.db.all(k)));}
ctx.App.db.reset();ctx.App.seed.ensure();const before=ctx.App.db.count('clientes');const seqBefore=ctx.App.db.load()._seq.clientes;setFail(true);assert.strictEqual(ctx.App.db.insert('clientes',{nome:'quota'}),null);setFail(false);assert.strictEqual(ctx.App.db.count('clientes'),before);assert.strictEqual(ctx.App.db.load()._seq.clientes,seqBefore);
ctx.App.db.reset();ctx.App.seed.ensure();const id=ctx.App.db.insert('clientes',{nome:'remove'}).id;setFail(true);assert.strictEqual(ctx.App.db.remove('clientes',id),false);setFail(false);assert(ctx.App.db.byId('clientes',id));
assert(ctx.App.validation.cpfValido('52998224725'));assert(!ctx.App.validation.cpfValido('11111111111'));assert(ctx.App.validation.cnpjValido('11222333000181'));assert(!ctx.App.validation.cnpjValido('11111111111111'));
console.log('PASS: hardening, corruption, quota rollback, auth, validation');
