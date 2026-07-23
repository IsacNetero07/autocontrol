// Login/sessão. Guarda de acesso simples para um app 100% local.
// Observação: como todos os dados ficam no próprio aparelho, este login é um
// controle de acesso básico, não uma barreira de segurança de servidor.
window.App = window.App || {};

(function () {
  const SESSAO = "autocontrol:sessao";

  // cyrb53: hash rápido e determinístico. Suficiente para não guardar a senha em texto puro.
  function cyrb53(str) {
    let h1 = 0xdeadbeef, h2 = 0x41c6ce57;
    for (let i = 0; i < str.length; i++) {
      const ch = str.charCodeAt(i);
      h1 = Math.imul(h1 ^ ch, 2654435761);
      h2 = Math.imul(h2 ^ ch, 1597334677);
    }
    h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507);
    h1 ^= Math.imul(h2 ^ (h2 >>> 13), 3266489909);
    h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507);
    h2 ^= Math.imul(h1 ^ (h1 >>> 13), 3266489909);
    return (4294967296 * (2097151 & h2) + (h1 >>> 0)).toString(16);
  }

  function hashSenha(senha) {
    return cyrb53("autocontrol$" + String(senha));
  }

  function login(usuario, senha) {
    const achado = App.db.where("usuarios", (u) => u.usuario === usuario)[0];
    if (!achado) return null;
    if (achado.senha !== hashSenha(senha)) return null;
    const sessao = { id: achado.id, nome: achado.nome, usuario: achado.usuario, nivel: achado.nivel };
    localStorage.setItem(SESSAO, JSON.stringify(sessao));
    return sessao;
  }

  function logout() {
    localStorage.removeItem(SESSAO);
  }

  function atual() {
    try {
      return JSON.parse(localStorage.getItem(SESSAO));
    } catch (e) {
      return null;
    }
  }

  function ehAdmin() {
    const u = atual();
    return !!u && u.nivel === "admin";
  }

  App.auth = { hashSenha, login, logout, atual, ehAdmin };
})();
