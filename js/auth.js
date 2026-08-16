// Autenticação local.
//
// AVISO DE SEGURANÇA: enquanto o AutoControl for 100% client-side, esta camada
// NÃO é uma fronteira de segurança. Os dados vivem no localStorage e qualquer
// pessoa com acesso ao navegador pode editá-los pelo DevTools — inclusive o
// campo `nivel` da sessão. O hash abaixo protege a senha contra leitura casual
// (e contra reuso da mesma senha em outros serviços), não contra um atacante
// local. Perfis e permissões só passam a valer de verdade com um servidor
// validando cada requisição. Ver README.md → "Limites da versão local".
window.App = window.App || {};

(function () {
  const SESSAO = "autocontrol:sessao";
  const ITERACOES = 210000; // OWASP 2023 para PBKDF2-HMAC-SHA256
  const subtle = (typeof crypto !== "undefined" && crypto.subtle) || null;

  const bytesParaB64 = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf)));
  const b64ParaBytes = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));

  // Hash legado (2.x): mix de 64 bits, não criptográfico. Mantido apenas para
  // validar senhas de instalações antigas e migrá-las no próximo login.
  function hashSenha(s) {
    let h1 = 0xdeadbeef, h2 = 0x41c6ce57;
    s = String(s);
    for (let i = 0; i < s.length; i++) {
      const c = s.charCodeAt(i);
      h1 = Math.imul(h1 ^ c, 2654435761);
      h2 = Math.imul(h2 ^ c, 1597334677);
    }
    h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507);
    h1 ^= Math.imul(h2 ^ (h2 >>> 13), 3266489909);
    h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507);
    h2 ^= Math.imul(h1 ^ (h1 >>> 13), 3266489909);
    return (4294967296 * (2097151 & h2) + (h1 >>> 0)).toString(16);
  }

  async function pbkdf2(senha, salt, iteracoes) {
    const chave = await subtle.importKey(
      "raw", new TextEncoder().encode(String(senha)), "PBKDF2", false, ["deriveBits"]
    );
    const bits = await subtle.deriveBits(
      { name: "PBKDF2", hash: "SHA-256", salt, iterations: iteracoes }, chave, 256
    );
    return bytesParaB64(bits);
  }

  // Formato: pbkdf2$<iteracoes>$<salt b64>$<hash b64>
  async function criarHash(senha) {
    if (!subtle) {
      // Só acontece fora de contexto seguro (ex.: abrir o index.html via file://).
      // Servido por HTTP(S) ou em localhost, todo navegador atual tem WebCrypto.
      console.warn(
        "[AutoControl] WebCrypto indisponível — usando hash fraco de compatibilidade. " +
        "Abra o app por http://localhost ou HTTPS para que as senhas usem PBKDF2."
      );
      return hashSenha(senha);
    }
    const salt = crypto.getRandomValues(new Uint8Array(16));
    const hash = await pbkdf2(senha, salt, ITERACOES);
    return `pbkdf2$${ITERACOES}$${bytesParaB64(salt)}$${hash}`;
  }

  async function conferirHash(senha, guardado) {
    if (typeof guardado !== "string" || !guardado) return false;
    if (!guardado.startsWith("pbkdf2$")) return hashSenha(senha) === guardado;
    if (!subtle) return false;
    const [, iteracoes, salt, hash] = guardado.split("$");
    return (await pbkdf2(senha, b64ParaBytes(salt), Number(iteracoes))) === hash;
  }

  const ehLegado = (guardado) => typeof guardado === "string" && !guardado.startsWith("pbkdf2$");

  const usuarioPorNome = (usuario) =>
    App.db.where("usuarios", (x) =>
      String(x.usuario).toLowerCase() === String(usuario).trim().toLowerCase()
    )[0] || null;

  async function login(usuario, senha) {
    const u = usuarioPorNome(usuario);
    if (!u || !(await conferirHash(senha, u.senha))) return null;
    // Migra silenciosamente hashes legados para PBKDF2 no primeiro login válido.
    if (ehLegado(u.senha) && subtle) {
      App.db.update("usuarios", u.id, { senha: await criarHash(senha) });
    }
    const s = { id: u.id, nome: u.nome, usuario: u.usuario, nivel: u.nivel };
    try {
      localStorage.setItem(SESSAO, JSON.stringify(s));
    } catch (e) {
      return null;
    }
    return s;
  }

  // Primeiro acesso: nenhum usuário cadastrado ainda.
  const precisaSetup = () => App.db.count("usuarios") === 0;

  async function criarAdmin(nome, usuario, senha) {
    if (!precisaSetup()) throw new Error("Já existe um usuário cadastrado.");
    const erro = validarCredenciais(usuario, senha);
    if (erro) throw new Error(erro);
    return App.db.insert("usuarios", {
      nome: String(nome).trim() || String(usuario).trim(),
      usuario: String(usuario).trim(),
      senha: await criarHash(senha),
      nivel: "admin",
    });
  }

  function validarSenha(senha) {
    if (String(senha || "").length < 8) return "A senha precisa de ao menos 8 caracteres.";
    if (/^\d+$/.test(String(senha))) return "A senha não pode ser apenas números.";
    return null;
  }

  function validarCredenciais(usuario, senha) {
    if (!String(usuario || "").trim()) return "Informe um nome de usuário.";
    if (String(usuario).trim().length < 3) return "O usuário precisa de ao menos 3 caracteres.";
    return validarSenha(senha);
  }

  async function trocarSenha(id, senhaAtual, senhaNova) {
    const u = App.db.byId("usuarios", id);
    if (!u || !(await conferirHash(senhaAtual, u.senha))) return null;
    const erro = validarCredenciais(u.usuario, senhaNova);
    if (erro) throw new Error(erro);
    return App.db.update("usuarios", id, { senha: await criarHash(senhaNova) });
  }

  const logout = () => localStorage.removeItem(SESSAO);
  const atual = () => {
    try { return JSON.parse(localStorage.getItem(SESSAO)) || null; } catch (e) { return null; }
  };
  const ehAdmin = () => atual()?.nivel === "admin";

  App.auth = {
    login, logout, atual, ehAdmin,
    precisaSetup, criarAdmin, trocarSenha, validarCredenciais, validarSenha,
    criarHash, conferirHash, hashSenha,
    // Diagnóstico: false = contexto inseguro, senhas caem no hash de compatibilidade.
    criptoForte: () => !!subtle,
  };
})();
