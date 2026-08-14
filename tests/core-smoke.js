const fs=require('fs'), vm=require('vm'), assert=require('assert');
const store=new Map();
const localStorage={getItem:k=>store.has(k)?store.get(k):null,setItem:(k,v)=>store.set(k,String(v)),removeItem:k=>store.delete(k)};
const ctx={window:null,localStorage,console,App:{ui:{toast(){}}},Intl,Date,JSON,Number,String,Math};ctx.window=ctx;vm.createContext(ctx);
for(const f of ['js/validation.js','js/db.js','js/auth.js','js/seed.js']) vm.runInContext(fs.readFileSync(f,'utf8'),ctx,{filename:f});
ctx.App.seed.ensure();
assert(ctx.App.db.count('clientes')>=3); assert(ctx.App.db.count('ordens')>=3);
assert(ctx.App.auth.login('isac','123456')); assert(!ctx.App.auth.login('isac','errada'));
const before=ctx.App.db.count('clientes'); const c=ctx.App.db.insert('clientes',{nome:'Teste'}); assert(c&&c.id); assert.equal(ctx.App.db.count('clientes'),before+1);
assert(ctx.App.db.update('clientes',c.id,{nome:'Teste 2'})); assert.equal(ctx.App.db.byId('clientes',c.id).nome,'Teste 2');
assert(ctx.App.db.remove('clientes',c.id)); assert.equal(ctx.App.db.byId('clientes',c.id),null);
// corrupt storage: loader must recover collections instead of crashing
store.set('autocontrol:v1','{"clientes":"quebrado","ordens":null}');
ctx.App.db.reset(); ctx.App.db.load(); assert(Array.isArray(ctx.App.db.all('clientes'))); assert(Array.isArray(ctx.App.db.all('ordens')));
// quota failure must not leave phantom inserted records
let fail=false; const oldSet=localStorage.setItem; localStorage.setItem=(k,v)=>{if(k==='autocontrol:v1'&&fail)throw new Error('quota'); oldSet(k,v)}; fail=true;
const n=ctx.App.db.count('clientes'); assert.equal(ctx.App.db.insert('clientes',{nome:'Quota'}),null); assert.equal(ctx.App.db.count('clientes'),n); fail=false;
console.log('PASS: seed/auth/db/validation smoke + corruption + quota');
