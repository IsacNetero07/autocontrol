// Helpers de interface: criação de DOM, formatação, toast, confirmação e formulário em modal.
window.App = window.App || {};

(function () {
  function el(tag, attrs, children) {
    const n = document.createElement(tag);
    if (attrs) {
      for (const k in attrs) {
        const val = attrs[k];
        if (val == null) continue;
        if (k === "class") n.className = val;
        else if (k === "html") n.innerHTML = val;
        else if (k === "text") n.textContent = val;
        else if (k.slice(0, 2) === "on" && typeof val === "function") n.addEventListener(k.slice(2).toLowerCase(), val);
        else n.setAttribute(k, val);
      }
    }
    if (children != null) {
      (Array.isArray(children) ? children : [children]).forEach((ch) => {
        if (ch == null || ch === false) return;
        n.appendChild(typeof ch === "object" ? ch : document.createTextNode(String(ch)));
      });
    }
    return n;
  }

  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); return node; }

  function money(v) {
    return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(v) || 0);
  }

  function fmtData(iso) {
    if (!iso) return "";
    const p = String(iso).split("-");
    if (p.length === 3) return p[2] + "/" + p[1] + "/" + p[0];
    return String(iso);
  }

  // ---------- Toast ----------
  function toast(msg, tipo) {
    let box = document.querySelector(".toasts");
    if (!box) { box = el("div", { class: "toasts" }); document.body.appendChild(box); }
    const t = el("div", { class: "toast " + (tipo || ""), text: msg });
    box.appendChild(t);
    setTimeout(() => { t.style.opacity = "0"; t.style.transition = "opacity .3s"; setTimeout(() => t.remove(), 300); }, 2600);
  }

  // ---------- Confirmação ----------
  function confirmar(msg, textoOk) {
    return new Promise((resolve) => {
      const fechar = (r) => { bg.remove(); document.removeEventListener("keydown", esc); resolve(r); };
      const esc = (e) => { if (e.key === "Escape") fechar(false); };
      const bg = el("div", { class: "modal-bg", onclick: (e) => { if (e.target === bg) fechar(false); } }, [
        el("div", { class: "modal" }, [
          el("div", { class: "body", html: "<p style='margin:0 0 4px'>" + msg + "</p>" }),
          el("footer", {}, [
            el("button", { class: "btn secondary", onclick: () => fechar(false) }, "Cancelar"),
            el("button", { class: "btn danger", onclick: () => fechar(true) }, textoOk || "Confirmar")
          ])
        ])
      ]);
      document.body.appendChild(bg);
      document.addEventListener("keydown", esc);
    });
  }

  // ---------- Formulário em modal ----------
  // campos: [{key,label,type,required,options,optionsFrom,optionLabel,placeholder,help,validate}]
  // tipos: text, number, date, time, textarea, select, password
  function modalForm(opcoes) {
    const campos = opcoes.campos || [];
    const valores = opcoes.valores || {};
    return new Promise((resolve) => {
      const inputs = {};
      const erros = {};

      function criarInput(campo) {
        const v = valores[campo.key];
        let input;
        if (campo.type === "textarea") {
          input = el("textarea", { placeholder: campo.placeholder || "" });
          input.value = v == null ? "" : v;
        } else if (campo.type === "select") {
          input = el("select");
          input.appendChild(el("option", { value: "" }, campo.placeholder || "-- selecione --"));
          let opts = campo.options || [];
          if (campo.optionsFrom) {
            opts = App.db.all(campo.optionsFrom).map((r) => ({
              value: r.id, label: campo.optionLabel ? campo.optionLabel(r) : r.nome
            }));
          }
          opts.forEach((o) => {
            const val = typeof o === "object" ? o.value : o;
            const lab = typeof o === "object" ? o.label : o;
            const op = el("option", { value: val }, lab);
            if (String(val) === String(v)) op.selected = true;
            input.appendChild(op);
          });
        } else {
          input = el("input", { type: campo.type || "text", placeholder: campo.placeholder || "" });
          input.value = v == null ? "" : v;
        }
        inputs[campo.key] = input;

        const erro = el("div", { class: "field-error" });
        erros[campo.key] = erro;
        return el("label", { class: "field" }, [
          el("span", { class: "lbl" }, campo.label + (campo.required ? " *" : "")),
          input,
          campo.help ? el("span", { class: "lbl", style: "margin-top:4px;font-weight:400" }, campo.help) : null,
          erro
        ]);
      }

      function fechar(r) { bg.remove(); document.removeEventListener("keydown", esc); resolve(r); }
      const esc = (e) => { if (e.key === "Escape") fechar(null); };

      function submeter() {
        const out = {};
        let ok = true;
        campos.forEach((c) => { erros[c.key].textContent = ""; });
        for (const c of campos) {
          let valor = inputs[c.key].value;
          if (typeof valor === "string") valor = valor.trim();
          out[c.key] = valor;
          if (c.required && (valor === "" || valor == null)) {
            erros[c.key].textContent = "Campo obrigatório";
            ok = false;
          }
        }
        if (ok) {
          for (const c of campos) {
            if (typeof c.validate === "function" && out[c.key] !== "") {
              const r = c.validate(out[c.key], out);
              if (r !== true && r != null && r !== undefined) {
                erros[c.key].textContent = typeof r === "string" ? r : "Valor inválido";
                ok = false;
              }
            }
          }
        }
        if (ok) fechar(out);
      }

      const form = el("div", { class: "body" }, campos.map(criarInput));
      const bg = el("div", { class: "modal-bg", onclick: (e) => { if (e.target === bg) fechar(null); } }, [
        el("div", { class: "modal" }, [
          el("header", {}, opcoes.titulo || "Formulário"),
          form,
          el("footer", {}, [
            el("button", { class: "btn secondary", onclick: () => fechar(null) }, "Cancelar"),
            el("button", { class: "btn", onclick: submeter }, "Salvar")
          ])
        ])
      ]);
      document.body.appendChild(bg);
      document.addEventListener("keydown", esc);
      const first = form.querySelector("input,select,textarea");
      if (first) setTimeout(() => first.focus(), 50);
    });
  }

  // ---------- Download (CSV) ----------
  function baixar(nomeArquivo, conteudo, tipo) {
    const blob = new Blob([conteudo], { type: (tipo || "text/plain") + ";charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = el("a", { href: url, download: nomeArquivo });
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { a.remove(); URL.revokeObjectURL(url); }, 100);
  }

  App.ui = { el, clear, money, fmtData, toast, confirmar, modalForm, baixar };
})();
