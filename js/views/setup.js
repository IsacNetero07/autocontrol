// Primeiro acesso: o dono da oficina cria o próprio administrador.
// Substitui o usuário padrão "isac / 123456" que vinha no seed.
window.App = window.App || {}; App.views = App.views || {};

(function () {
  const el = App.ui.el;

  function render(root, start) {
    App.ui.clear(root);
    const form = el("form", { class: "login-card" });
    form.innerHTML = `<div class="login-brand"><img class="login-logo" src="./icons/autocontrol.svg" alt="AutoControl"><div><strong>AUTO<span>CONTROL</span></strong><small>GESTÃO DE OFICINAS</small></div></div><div class="login-copy"><span class="eyebrow">PRIMEIRO ACESSO</span><h1>Crie seu administrador</h1><p>Defina as credenciais da sua oficina. Elas ficam apenas neste dispositivo.</p></div>`;

    const nome = el("input", { type: "text", placeholder: "Ex.: Isac Neto", autocomplete: "name", required: true });
    const user = el("input", { type: "text", placeholder: "Ex.: isac", autocomplete: "username", required: true });
    const pass = el("input", { type: "password", placeholder: "Mínimo 8 caracteres", autocomplete: "new-password", required: true });
    const pass2 = el("input", { type: "password", placeholder: "Repita a senha", autocomplete: "new-password", required: true });
    const demo = el("input", { type: "checkbox" });

    form.append(
      el("label", { class: "login-field" }, [el("span", {}, "Seu nome"), nome]),
      el("label", { class: "login-field" }, [el("span", {}, "Usuário"), user]),
      el("label", { class: "login-field" }, [el("span", {}, "Senha"), pass]),
      el("label", { class: "login-field" }, [el("span", {}, "Confirmar senha"), pass2]),
      el("label", { class: "login-field inline" }, [demo, el("span", {}, "Incluir dados de demonstração para explorar o sistema")])
    );

    const msg = el("div", { class: "login-error", role: "alert" });
    const btn = App.ui.button("Criar administrador", () => {}, { icon: "arrow" });
    btn.type = "submit";
    form.append(msg, btn);

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      msg.textContent = "";
      if (pass.value !== pass2.value) { msg.textContent = "As senhas não conferem."; pass2.focus(); return; }
      const erro = App.auth.validarCredenciais(user.value, pass.value);
      if (erro) { msg.textContent = erro; pass.focus(); return; }
      btn.disabled = true;
      try {
        const criado = await App.auth.criarAdmin(nome.value, user.value, pass.value);
        if (!criado) { msg.textContent = "Não foi possível salvar: armazenamento cheio ou indisponível."; btn.disabled = false; return; }
        if (demo.checked) App.seed.demo();
        const sessao = await App.auth.login(user.value, pass.value);
        if (!sessao) { msg.textContent = "Usuário criado, mas a sessão falhou. Recarregue e faça login."; btn.disabled = false; return; }
        location.hash = "#/dashboard";
        start();
      } catch (err) {
        msg.textContent = err.message || "Falha ao criar o administrador.";
        btn.disabled = false;
      }
    });

    root.append(el("div", { class: "login-screen" }, [el("div", { class: "login-glow" }), form]));
    setTimeout(() => nome.focus(), 50);
  }

  App.views.setup = { render };
})();
