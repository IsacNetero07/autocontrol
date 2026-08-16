window.App = window.App || {}; App.views = App.views || {};

(function () {
  const el = App.ui.el;

  function render(root, start) {
    App.ui.clear(root);
    const form = el("form", { class: "login-card" });
    form.innerHTML = `<div class="login-brand"><img class="login-logo" src="./icons/autocontrol.svg" alt="AutoControl"><div><strong>AUTO<span>CONTROL</span></strong><small>GESTÃO DE OFICINAS</small></div></div><div class="login-copy"><span class="eyebrow">ACESSO SEGURO</span><h1>Bem-vindo de volta</h1><p>Controle sua oficina de qualquer lugar, no computador ou no iPhone.</p></div>`;

    const user = el("input", { type: "text", placeholder: "Usuário", autocomplete: "username", required: true });
    const pass = el("input", { type: "password", placeholder: "Senha", autocomplete: "current-password", required: true });
    form.append(
      el("label", { class: "login-field" }, [el("span", {}, "Usuário"), user]),
      el("label", { class: "login-field" }, [el("span", {}, "Senha"), pass])
    );

    const msg = el("div", { class: "login-error", role: "alert" });
    const btn = App.ui.button("Entrar", () => {}, { icon: "arrow" });
    btn.type = "submit";
    form.append(msg, btn);

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      msg.textContent = "";
      btn.disabled = true;
      const s = await App.auth.login(user.value, pass.value);
      btn.disabled = false;
      if (!s) { msg.textContent = "Usuário ou senha inválidos."; pass.focus(); return; }
      location.hash = "#/dashboard";
      start();
    });

    root.append(el("div", { class: "login-screen" }, [el("div", { class: "login-glow" }), form]));
  }

  App.views.login = { render };
})();
