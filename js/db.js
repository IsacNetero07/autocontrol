window.App = window.App || {};
(function () {
  const KEY = "autocontrol:v1";
  const COLECOES = ["clientes","veiculos","ordens","estoque","fornecedores","financeiro","agendamentos","usuarios","logs","checklists"];
  function vazio(){ const d={_seq:{}}; COLECOES.forEach(c=>d[c]=[]); return d; }
  function normalizar(raw){
    const d = raw && typeof raw === "object" && !Array.isArray(raw) ? raw : vazio();
    if(!d._seq || typeof d._seq !== "object" || Array.isArray(d._seq)) d._seq={};
    COLECOES.forEach(c=>{ if(!Array.isArray(d[c])) d[c]=[]; });
    return d;
  }
  let dados = null;
  function load(){
    if(dados) return dados;
    try { dados = normalizar(JSON.parse(localStorage.getItem(KEY))); } catch(e){ dados=vazio(); }
    return dados;
  }
  function save(){
    try { localStorage.setItem(KEY, JSON.stringify(load())); return true; }
    catch(e){ App.ui && App.ui.toast("Não foi possível salvar: armazenamento cheio ou indisponível.","error"); return false; }
  }
  function assertColl(coll){ if(!COLECOES.includes(coll)) throw new Error(`Coleção inválida: ${coll}`); }
  function nextId(coll){ assertColl(coll); const d=load(); const max=d[coll].reduce((m,r)=>Math.max(m,Number(r.id)||0),0); d._seq[coll]=Math.max(Number(d._seq[coll])||0,max)+1; return d._seq[coll]; }
  function all(coll){ assertColl(coll); return load()[coll].slice(); }
  function byId(coll,id){ assertColl(coll); id=Number(id); return load()[coll].find(r=>Number(r.id)===id)||null; }
  function where(coll,fn){ assertColl(coll); return load()[coll].filter(typeof fn === "function" ? fn : ()=>true); }
  function insert(coll,obj){
    assertColl(coll); const d=load(); const previousSeq=d._seq[coll];
    const rec=Object.assign({},obj||{},{id:nextId(coll)}); d[coll].push(rec);
    if(!save()){ d[coll].pop(); if(previousSeq==null) delete d._seq[coll]; else d._seq[coll]=previousSeq; return null; }
    return rec;
  }
  function update(coll,id,patch){ assertColl(coll); const r=byId(coll,id); if(!r) return null; const before=Object.assign({},r); Object.assign(r,patch||{}); if(!save()){Object.keys(r).forEach(k=>delete r[k]);Object.assign(r,before);return null;} return r; }
  function remove(coll,id){ assertColl(coll); const d=load(), n=Number(id), idx=d[coll].findIndex(r=>Number(r.id)===n); if(idx<0)return false; const [removed]=d[coll].splice(idx,1); if(!save()){d[coll].splice(idx,0,removed);return false;} return true; }
  function count(coll,fn){ return fn?where(coll,fn).length:all(coll).length; }
  function invalidate(){dados=null;return load();}
  function reset(){ try{localStorage.removeItem(KEY);localStorage.removeItem("autocontrol:seeded");localStorage.removeItem("autocontrol:sessao");}finally{dados=null;} }
  App.db={load,save,all,byId,where,insert,update,remove,count,nextId,reset,invalidate,KEY,COLECOES};
})();
