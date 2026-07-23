// Camada de dados sobre localStorage. Espelha o esquema do banco SQLite original
// (clientes, veiculos, ordens, estoque, fornecedores, financeiro, agendamentos, usuarios, logs).
window.App = window.App || {};

(function () {
  const KEY = "autocontrol:v1";
  const COLECOES = [
    "clientes", "veiculos", "ordens", "estoque",
    "fornecedores", "financeiro", "agendamentos", "usuarios", "logs"
  ];

  function vazio() {
    const d = { _seq: {} };
    COLECOES.forEach((c) => (d[c] = []));
    return d;
  }

  let dados = null;

  function load() {
    if (dados) return dados;
    try {
      dados = JSON.parse(localStorage.getItem(KEY)) || vazio();
    } catch (e) {
      dados = vazio();
    }
    if (!dados._seq) dados._seq = {};
    COLECOES.forEach((c) => { if (!Array.isArray(dados[c])) dados[c] = []; });
    return dados;
  }

  function save() {
    localStorage.setItem(KEY, JSON.stringify(load()));
  }

  function nextId(coll) {
    const d = load();
    d._seq[coll] = (d._seq[coll] || 0) + 1;
    return d._seq[coll];
  }

  function all(coll) {
    return load()[coll].slice();
  }

  function byId(coll, id) {
    id = Number(id);
    return load()[coll].find((r) => r.id === id) || null;
  }

  function where(coll, fn) {
    return load()[coll].filter(fn);
  }

  function insert(coll, obj) {
    const d = load();
    const rec = Object.assign({}, obj, { id: nextId(coll) });
    d[coll].push(rec);
    save();
    return rec;
  }

  function update(coll, id, patch) {
    const r = byId(coll, id);
    if (!r) return null;
    Object.assign(r, patch);
    save();
    return r;
  }

  function remove(coll, id) {
    const d = load();
    id = Number(id);
    d[coll] = d[coll].filter((r) => r.id !== id);
    save();
  }

  function count(coll, fn) {
    return fn ? where(coll, fn).length : all(coll).length;
  }

  function reset() {
    localStorage.removeItem(KEY);
    localStorage.removeItem("autocontrol:seeded");
    dados = null;
  }

  App.db = { load, save, all, byId, where, insert, update, remove, count, nextId, reset, KEY, COLECOES };
})();
