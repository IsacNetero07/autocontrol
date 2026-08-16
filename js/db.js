// Camada de dados.
//
// Regra central: nada que sai daqui é o objeto guardado internamente. all(),
// byId() e where() devolvem cópias. Quem quiser alterar um registro precisa
// passar por update(), que é o único ponto que grava.
//
// Antes as consultas devolviam a referência viva do store, então mexer no
// objeto retornado alterava a memória sem gravar no localStorage — e memória e
// disco divergiam em silêncio até o próximo reload.
//
// Este módulo é a única parte do app que conhece o localStorage. Trocar por
// IndexedDB ou por uma API remota significa reescrever só este arquivo,
// mantendo a mesma superfície pública.
window.App = window.App || {};

(function () {
  const KEY = "autocontrol:v1";
  const COLECOES = ["clientes","veiculos","ordens","estoque","fornecedores","financeiro","agendamentos","usuarios","logs","checklists"];

  const clonar = typeof structuredClone === "function"
    ? (v) => structuredClone(v)
    : (v) => (v === undefined ? v : JSON.parse(JSON.stringify(v)));

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

  // --- acesso interno: trabalha com as referências vivas -------------------
  function bruto(coll){ assertColl(coll); return load()[coll]; }
  function vivo(coll,id){ const n=Number(id); return bruto(coll).find(r=>Number(r.id)===n)||null; }
  function restaurar(alvo,antes){ Object.keys(alvo).forEach(k=>delete alvo[k]); Object.assign(alvo,antes); }

  // --- leitura pública: sempre cópias --------------------------------------
  function all(coll){ return bruto(coll).map(clonar); }
  function byId(coll,id){ const r=vivo(coll,id); return r?clonar(r):null; }
  function where(coll,fn){ return bruto(coll).filter(typeof fn==="function"?fn:()=>true).map(clonar); }
  function count(coll,fn){ return typeof fn==="function"?bruto(coll).filter(fn).length:bruto(coll).length; }

  function nextId(coll){
    const d=load(), lista=bruto(coll);
    const max=lista.reduce((m,r)=>Math.max(m,Number(r.id)||0),0);
    d._seq[coll]=Math.max(Number(d._seq[coll])||0,max)+1;
    return d._seq[coll];
  }

  function insert(coll,obj){
    const d=load(), lista=bruto(coll), seqAnterior=d._seq[coll];
    const rec=Object.assign({},clonar(obj)||{},{id:nextId(coll)});
    lista.push(rec);
    if(!save()){
      lista.pop();
      if(seqAnterior==null) delete d._seq[coll]; else d._seq[coll]=seqAnterior;
      return null;
    }
    return clonar(rec);
  }

  function update(coll,id,patch){
    const r=vivo(coll,id);
    if(!r) return null;
    // Cópia profunda: um Object.assign raso deixaria arrays e objetos aninhados
    // (fotos, timeline, checklist) apontando para os mesmos valores, e o
    // rollback não desfaria alterações feitas dentro deles.
    const antes=clonar(r);
    Object.assign(r,clonar(patch)||{});
    if(!save()){ restaurar(r,antes); return null; }
    return clonar(r);
  }

  function remove(coll,id){
    const lista=bruto(coll), n=Number(id), idx=lista.findIndex(r=>Number(r.id)===n);
    if(idx<0) return false;
    const [removido]=lista.splice(idx,1);
    if(!save()){ lista.splice(idx,0,removido); return false; }
    return true;
  }

  function invalidate(){ dados=null; return load(); }

  function reset(){
    try{
      localStorage.removeItem(KEY);
      localStorage.removeItem("autocontrol:seeded");
      localStorage.removeItem("autocontrol:sessao");
    } finally { dados=null; }
  }

  App.db={load,save,all,byId,where,insert,update,remove,count,nextId,reset,invalidate,clonar,KEY,COLECOES};
})();
