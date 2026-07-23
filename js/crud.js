// Motor genérico de CRUD. Cada módulo (clientes, veículos, etc.) é só uma configuração.
window.App = window.App || {};

(function () {
  const el = App.ui.el;

  function crud(cfg) {
    function getCell(row, col) {
      if (col.resolve) return col.resolve(row);
      const v = row[col.key];
      if (col.format) return col.format(v, row);
      return v == null ? "" : String(v);
    }

    function linhas(filtro) {
      let rows = App.db.all(cfg.coll);
      rows.sort(cfg.ordenar || ((a, b) => b.id - a.id));
      if (filtro) {
        const q = filtro.toLowerCase();
        rows = rows.filter((r) => {
          const hay = [];
          (cfg.buscaKeys || []).forEach((k) => hay.push(r[k]));
          cfg.colunas.forEach((c) => hay.push(getCell(r, c)));
          return hay.some((x) => x != null && String(x).toLowerCase().indexOf(q) !== -1);
        });
      }
      return rows;
    }

    function registrarLog(acao) {
      if (cfg.coll === "logs") return;
      const u = App.auth.atual() || {};
      App.db.insert("logs", {
        usuario: u.nome || "-",
        acao: acao + " " + (cfg.singular || cfg.coll),
        detalhes: "",
        data_hora: new Date().toISOString()
      });
    }

    function abrirForm(rec, repint) {
      const valores = rec ? Object.assign({}, rec) : {};
      cfg.campos.forEach((c) => { if (c.type === "password") valores[c.key] = ""; });

      // Alguns campos só são obrigatórios ao criar (ex.: senha de usuário novo).
      const campos = cfg.campos.map((c) =>
        c.requiredOnCreate && !rec ? Object.assign({}, c, { required: true }) : c
      );

      App.ui.modalForm({
        titulo: (rec ? "Editar " : "Novo ") + (cfg.singular || ""),
        campos: campos,
        valores: valores
      }).then((res) => {
        if (!res) return;
        const dados = {};
        for (const c of cfg.campos) {
          let v = res[c.key];
          if (c.type === "password") {
            if (v === "" && rec) continue;      // manter senha atual
            dados[c.key] = c.transform ? c.transform(v) : v;
            continue;
          }
          if (c.type === "number") v = v === "" ? (c.padrao != null ? c.padrao : 0) : Number(v);
          else if (c.optionsFrom) v = v === "" ? null : Number(v);
          if (c.transform) v = c.transform(v);
          dados[c.key] = v;
        }

        let salvo;
        if (rec) { salvo = App.db.update(cfg.coll, rec.id, dados); registrarLog("editar"); }
        else { salvo = App.db.insert(cfg.coll, dados); registrarLog("criar"); }
        if (cfg.aoSalvar) cfg.aoSalvar(salvo, rec ? "editar" : "criar");
        App.ui.toast(rec ? "Atualizado com sucesso" : "Cadastrado com sucesso", "ok");
        repint();
      });
    }

    function excluir(rec, repint) {
      const rotulo = rec[cfg.rotulo || "nome"] || ("#" + rec.id);
      App.ui.confirmar('Excluir "' + rotulo + '"?', "Excluir").then((ok) => {
        if (!ok) return;
        if (cfg.antesDeExcluir) {
          try { cfg.antesDeExcluir(rec.id); }
          catch (e) { App.ui.toast(e.message, "error"); return; }
        }
        App.db.remove(cfg.coll, rec.id);
        registrarLog("excluir");
        App.ui.toast("Excluído", "ok");
        repint();
      });
    }

    function campoCsv(v) {
      v = v == null ? "" : String(v);
      if (/[";\n]/.test(v)) v = '"' + v.replace(/"/g, '""') + '"';
      return v;
    }

    function exportar(filtro) {
      const rows = linhas(filtro);
      const header = cfg.colunas.map((c) => c.label);
      const corpo = rows.map((r) => cfg.colunas.map((c) => getCell(r, c)));
      const csv = [header].concat(corpo).map((cols) => cols.map(campoCsv).join(";")).join("\r\n");
      App.ui.baixar(cfg.coll + ".csv", "﻿" + csv, "text/csv");
    }

    function tabela(rows, repint) {
      if (rows.length === 0) return el("div", { class: "empty" }, "Nenhum registro encontrado.");
      const cabecalho = cfg.colunas.map((c) => el("th", {}, c.label));
      if (!cfg.somenteLeitura) cabecalho.push(el("th", { class: "actions" }, "Ações"));

      const corpo = rows.map((r) => {
        const celulas = cfg.colunas.map((c) => {
          const texto = getCell(r, c);
          if (c.tag) return el("td", {}, el("span", { class: "tag " + c.tag(r) }, texto));
          return el("td", {}, texto);
        });
        if (!cfg.somenteLeitura) {
          celulas.push(el("td", { class: "actions" }, [
            el("button", { class: "btn small secondary", onclick: () => abrirForm(r, repint) }, "Editar"),
            el("span", { text: " " }),
            el("button", { class: "btn small danger", onclick: () => excluir(r, repint) }, "Excluir")
          ]));
        }
        const tr = el("tr", {}, celulas);
        if (cfg.rowClass) { const cl = cfg.rowClass(r); if (cl) tr.className = cl; }
        return tr;
      });

      return el("div", { class: "table-wrap" }, [
        el("table", {}, [el("thead", {}, el("tr", {}, cabecalho)), el("tbody", {}, corpo)])
      ]);
    }

    function render(container) {
      const estado = { q: "" };
      const badge = el("span", { class: "count-badge" });
      const areaResumo = el("div");
      const areaTabela = el("div");

      function repint() {
        const rows = linhas(estado.q);
        badge.textContent = App.db.count(cfg.coll) + " no total";
        App.ui.clear(areaResumo);
        if (cfg.resumo) areaResumo.appendChild(cfg.resumo(App.db.all(cfg.coll)));
        App.ui.clear(areaTabela);
        areaTabela.appendChild(tabela(rows, repint));
      }

      const busca = el("input", {
        class: "search", type: "search", placeholder: "Buscar...",
        oninput: (e) => { estado.q = e.target.value; repint(); }
      });

      const toolbar = el("div", { class: "toolbar" }, [
        busca,
        el("button", { class: "btn ghost small", onclick: () => exportar(estado.q) }, "Exportar CSV"),
        cfg.somenteLeitura ? null : el("button", { class: "btn", onclick: () => abrirForm(null, repint) }, "+ Novo")
      ]);

      container.appendChild(el("div", { class: "section-title" }, [
        el("h1", {}, cfg.titulo), badge
      ]));
      container.appendChild(toolbar);
      container.appendChild(areaResumo);
      container.appendChild(areaTabela);
      repint();
    }

    return { render };
  }

  App.crud = crud;
})();
