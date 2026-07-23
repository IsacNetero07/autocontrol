// Bootstrap: monta o layout, cuida da navegação (hash) e registra o service worker.
window.App = window.App || {};

(function () {
  const el = App.ui.el;

  const NAV = [
    { route: "dashboard", ic: "📊", label: "Painel" },
    { route: "clientes", ic: "👤", label: "Clientes" },
    { route: "veiculos", ic: "🚗", label: "Veículos" },
    { route: "ordens", ic: "🧾", label: "Ordens de Serviço" },
    { route: "agenda", ic: "📅", label: "Agenda" },
    { route: "estoque", ic: "📦", label: "Estoque" },
    { route: "financeiro", ic: "💰", label: "Financeiro" },
    { route: "fornecedores", ic: "🏭", label: "Fornecedores" },
    { route: "usuarios", ic: "🔑", label: "Usuários", adminOnly: true },
    { route: "logs", ic: "📜", label: "Auditoria", adminOnly: true }
  ];

  let deferredPrompt = null;

  function rotaAtual() {
    return location.hash.replace(/^#\/?/, "") || "dashboard";
  }

  function start() {
    const root = document.getElementById("app");
    if (!App.auth.atual()) {
      App.views.login.render(root, start);
      return;
    }
    renderShell(root);
  }

  function renderShell(root) {
    const admin = App.auth.ehAdmin();
    const sessao = App.auth.atual();

    const links = {};
    const navEls = NAV.filter((n) => !n.adminOnly || admin).map((n) => {
      const a = el("a", { href: "#/" + n.route }, [el("span", { class: "ic" }, n.ic), n.label]);
      links[n.route] = a;
      return a;
    });

    const sidebar = el("aside", { class: "sidebar" }, [
      el("div", { class: "brand" }, [
        el("img", { class: "logo", src: "./icons/icon-192.png", alt: "" }),
        el("div", {}, ["Auto", el("span", {}, "Control")])
      ]),
      el("nav", { class: "nav" }, navEls),
      el("div", { class: "sidebar-foot" }, [
        el("button", { class: "btn ghost small", style: "width:100%", onclick: zerarDados }, "Zerar dados")
      ])
    ]);

    const overlay = el("div", { class: "overlay", onclick: () => fecharMenu() });

    const btnInstalar = el("button", { class: "btn small", style: "display:none", onclick: instalar }, "Instalar");
    if (deferredPrompt) btnInstalar.style.display = "";

    const titulo = el("h1", {}, "Painel");
    const topbar = el("header", { class: "topbar" }, [
      el("button", { class: "hamburger", onclick: () => abrirMenu(), "aria-label": "Menu" }, "☰"),
      titulo,
      btnInstalar,
      el("div", { class: "user" }, [
        el("b", {}, sessao ? sessao.nome : ""),
        sessao ? sessao.nivel : ""
      ]),
      el("button", { class: "btn secondary small", onclick: sair }, "Sair")
    ]);

    const view = el("div", { class: "content" });
    const main = el("main", { class: "main" }, [topbar, view]);

    App.ui.clear(root);
    root.appendChild(el("div", { class: "shell" }, [sidebar, main, overlay]));

    function abrirMenu() { sidebar.classList.add("open"); overlay.classList.add("show"); }
    function fecharMenu() { sidebar.classList.remove("open"); overlay.classList.remove("show"); }

    // expõe o botão de instalar caso o evento chegue depois do render
    window.__mostrarInstalar = () => { btnInstalar.style.display = ""; };

    function renderRoute() {
      const route = rotaAtual();
      const navDef = NAV.find((n) => n.route === route);
      const entity = App.entities[route];
      const precisaAdmin = (navDef && navDef.adminOnly) || (entity && entity.adminOnly);
      if (precisaAdmin && !App.auth.ehAdmin()) {
        App.ui.toast("Acesso restrito a administradores.", "error");
        location.hash = "#/dashboard";
        return;
      }

      Object.keys(links).forEach((k) => links[k].classList.toggle("active", k === route));
      fecharMenu();
      App.ui.clear(view);

      if (route === "dashboard") { titulo.textContent = "Painel"; App.views.dashboard.render(view); return; }
      if (entity) { titulo.textContent = entity.titulo; App.crud(entity).render(view); return; }
      location.hash = "#/dashboard";
    }

    window.onhashchange = renderRoute;
    renderRoute();
  }

  function sair() {
    App.auth.logout();
    location.hash = "#/dashboard";
    start();
  }

  function zerarDados() {
    App.ui.confirmar("Isto apaga todos os dados deste aparelho e recria os dados de exemplo. Continuar?", "Zerar")
      .then((ok) => {
        if (!ok) return;
        App.db.reset();
        App.seed.ensure();
        App.auth.logout();
        App.ui.toast("Dados reiniciados.", "ok");
        start();
      });
  }

  function instalar() {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    deferredPrompt.userChoice.finally(() => { deferredPrompt = null; });
  }

  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (window.__mostrarInstalar) window.__mostrarInstalar();
  });

  function registrarSW() {
    if ("serviceWorker" in navigator) {
      window.addEventListener("load", () => {
        navigator.serviceWorker.register("./sw.js").catch(() => {});
      });
    }
  }

  function boot() {
    App.seed.ensure();
    registrarSW();
    start();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
