// Tela de login.
window.App = window.App || {};
App.views = App.views || {};

(function () {
  const el = App.ui.el;

  function render(container, aoEntrar) {
    const usuario = el("input", { type: "text", placeholder: "Usuário", autocomplete: "username" });
    const senha = el("input", { type: "password", placeholder: "Senha", autocomplete: "current-password" });
    const erro = el("div", { class: "field-error", style: "text-align:center;margin-bottom:6px" });

    function entrar() {
      erro.textContent = "";
      const sess = App.auth.login(usuario.value.trim(), senha.value);
      if (!sess) { erro.textContent = "Usuário ou senha inválidos."; return; }
      App.ui.toast("Bem-vindo, " + sess.nome, "ok");
      aoEntrar();
    }

    senha.addEventListener("keydown", (e) => { if (e.key === "Enter") entrar(); });
    usuario.addEventListener("keydown", (e) => { if (e.key === "Enter") senha.focus(); });

    const box = el("div", { class: "login-box" }, [
      el("img", { class: "logo-big", src: "./icons/icon-192.png", alt: "AutoControl" }),
      el("h1", {}, ["Auto", el("span", {}, "Control")]),
      el("div", { class: "sub" }, "Gestão de oficina mecânica"),
      el("label", { class: "field" }, [el("span", { class: "lbl" }, "Usuário"), usuario]),
      el("label", { class: "field" }, [el("span", { class: "lbl" }, "Senha"), senha]),
      erro,
      el("button", { class: "btn", onclick: entrar }, "Entrar"),
      el("div", { class: "login-hint" }, "Acesso padrão: isac / 123456")
    ]);

    App.ui.clear(container);
    container.appendChild(el("div", { class: "login-wrap" }, [box]));
    setTimeout(() => usuario.focus(), 60);
  }

  App.views.login = { render };
})();
