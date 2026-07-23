// Painel inicial: números do negócio e listas rápidas.
window.App = window.App || {};
App.views = App.views || {};

(function () {
  const el = App.ui.el;

  function hojeISO() { return new Date().toISOString().slice(0, 10); }

  function render(container) {
    const db = App.db;
    const H = App.helpers;

    const clientes = db.all("clientes");
    const veiculos = db.all("veiculos");
    const ordens = db.all("ordens");
    const estoque = db.all("estoque");
    const financeiro = db.all("financeiro");
    const agendamentos = db.all("agendamentos");

    const ordensAbertas = ordens.filter((o) => o.status !== "Finalizada");
    let receita = 0, despesa = 0;
    financeiro.forEach((m) => { if (m.tipo === "Receita") receita += Number(m.valor) || 0; else despesa += Number(m.valor) || 0; });
    const saldo = receita - despesa;
    const estoqueBaixo = estoque.filter((e) => Number(e.quantidade) <= Number(e.quantidade_minima));
    const hoje = hojeISO();
    const proximos = agendamentos
      .filter((a) => String(a.data) >= hoje && a.status !== "Cancelado" && a.status !== "Concluído")
      .sort((a, b) => String(a.data).localeCompare(String(b.data)));

    const cards = el("div", { class: "cards" }, [
      H.card("Clientes", clientes.length, "accent"),
      H.card("Veículos", veiculos.length, "accent"),
      H.card("OS abertas", ordensAbertas.length, ordensAbertas.length ? "warn" : "ok"),
      H.card("Saldo", App.ui.money(saldo), saldo >= 0 ? "ok" : "danger"),
      H.card("Estoque baixo", estoqueBaixo.length, estoqueBaixo.length ? "danger" : "ok"),
      H.card("Agendamentos", proximos.length, "accent")
    ]);

    function painelLista(titulo, itens, render) {
      const lista = itens.length
        ? el("ul", { class: "list-mini" }, itens.map(render))
        : el("div", { class: "empty" }, "Nada por aqui.");
      return el("div", { class: "panel" }, [el("h2", {}, titulo), lista]);
    }

    const painelAgenda = painelLista("Próximos agendamentos", proximos.slice(0, 6), (a) =>
      el("li", {}, [
        el("span", {}, App.ui.fmtData(a.data) + (a.hora ? " " + a.hora : "") + " - " + H.clienteNome(a.cliente_id)),
        el("span", { class: "muted" }, a.descricao || "")
      ])
    );

    const painelEstoque = painelLista("Estoque baixo", estoqueBaixo.slice(0, 6), (p) =>
      el("li", {}, [
        el("span", {}, p.nome),
        el("span", { class: "muted" }, "Qtd " + p.quantidade + " / mín " + p.quantidade_minima)
      ])
    );

    const ultimas = ordens.slice().sort((a, b) => b.id - a.id).slice(0, 6);
    const painelOrdens = painelLista("Últimas ordens de serviço", ultimas, (o) =>
      el("li", {}, [
        el("span", {}, H.clienteNome(o.cliente_id) + " - " + H.veiculoLabel(o.veiculo_id)),
        el("span", { class: "muted" }, o.status + " - " + App.ui.money(o.valor_total))
      ])
    );

    App.ui.clear(container);
    container.appendChild(el("div", { class: "section-title" }, [el("h1", {}, "Painel")]));
    container.appendChild(cards);
    container.appendChild(painelAgenda);
    container.appendChild(painelEstoque);
    container.appendChild(painelOrdens);
  }

  App.views.dashboard = { render };
})();
