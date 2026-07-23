// Configuração de cada módulo. O motor (crud.js) faz o resto.
window.App = window.App || {};

(function () {
  const el = App.ui.el;
  const V = App.validation;

  function clienteNome(id) { const c = App.db.byId("clientes", id); return c ? c.nome : "-"; }
  function veiculoLabel(id) { const v = App.db.byId("veiculos", id); return v ? v.placa + " - " + (v.modelo || "") : "-"; }
  function fornecedorNome(id) { const f = App.db.byId("fornecedores", id); return f ? f.nome : "-"; }

  function statusOS(s) {
    if (s === "Aberta") return "aberta";
    if (s === "Em andamento") return "andamento";
    if (s === "Finalizada") return "finalizada";
    return "aberta";
  }
  function statusAgenda(s) {
    if (s === "Concluído") return "finalizada";
    if (s === "Cancelado") return "despesa";
    return "aberta";
  }
  function fmtDataHora(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    if (isNaN(d.getTime())) return String(iso);
    return d.toLocaleString("pt-BR");
  }
  function card(k, v, cls) {
    return el("div", { class: "card " + (cls || "") }, [
      el("div", { class: "k" }, k),
      el("div", { class: "v" }, String(v))
    ]);
  }

  const entities = {
    clientes: {
      coll: "clientes", titulo: "Clientes", singular: "Cliente", rotulo: "nome",
      buscaKeys: ["nome", "cpf", "telefone", "email"],
      colunas: [
        { key: "nome", label: "Nome" },
        { key: "cpf", label: "CPF", format: V.formatCpf },
        { key: "telefone", label: "Telefone" },
        { key: "email", label: "E-mail" }
      ],
      campos: [
        { key: "nome", label: "Nome", required: true },
        { key: "cpf", label: "CPF", validate: (v) => V.cpfValido(v) ? true : "CPF inválido" },
        { key: "telefone", label: "Telefone" },
        { key: "email", label: "E-mail" },
        { key: "endereco", label: "Endereço" }
      ],
      antesDeExcluir: (id) => {
        const nv = App.db.count("veiculos", (v) => v.cliente_id === id);
        const no = App.db.count("ordens", (o) => o.cliente_id === id);
        if (nv || no) {
          const p = [];
          if (nv) p.push(nv + " veículo(s)");
          if (no) p.push(no + " ordem(ns)");
          throw new Error("Não é possível excluir: cliente possui " + p.join(" e ") + ".");
        }
      }
    },

    veiculos: {
      coll: "veiculos", titulo: "Veículos", singular: "Veículo", rotulo: "placa",
      buscaKeys: ["placa", "marca", "modelo"],
      colunas: [
        { key: "placa", label: "Placa" },
        { key: "marca", label: "Marca" },
        { key: "modelo", label: "Modelo" },
        { key: "ano", label: "Ano" },
        { key: "cliente_id", label: "Cliente", resolve: (r) => clienteNome(r.cliente_id) }
      ],
      campos: [
        { key: "placa", label: "Placa", required: true },
        { key: "marca", label: "Marca" },
        { key: "modelo", label: "Modelo" },
        { key: "ano", label: "Ano" },
        { key: "cor", label: "Cor" },
        { key: "quilometragem", label: "Quilometragem" },
        { key: "cliente_id", label: "Cliente", type: "select", required: true, optionsFrom: "clientes", optionLabel: (c) => c.nome }
      ],
      antesDeExcluir: (id) => {
        const no = App.db.count("ordens", (o) => o.veiculo_id === id);
        const na = App.db.count("agendamentos", (a) => a.veiculo_id === id);
        if (no || na) {
          const p = [];
          if (no) p.push(no + " ordem(ns)");
          if (na) p.push(na + " agendamento(s)");
          throw new Error("Não é possível excluir: veículo possui " + p.join(" e ") + ".");
        }
      }
    },

    ordens: {
      coll: "ordens", titulo: "Ordens de Serviço", singular: "Ordem", rotulo: "problema",
      buscaKeys: ["mecanico", "problema", "servicos", "status"],
      colunas: [
        { key: "cliente_id", label: "Cliente", resolve: (r) => clienteNome(r.cliente_id) },
        { key: "veiculo_id", label: "Veículo", resolve: (r) => veiculoLabel(r.veiculo_id) },
        { key: "mecanico", label: "Mecânico" },
        { key: "status", label: "Status", tag: (r) => statusOS(r.status) },
        { key: "valor_total", label: "Valor", format: App.ui.money },
        { key: "data_entrada", label: "Entrada", format: App.ui.fmtData }
      ],
      campos: [
        { key: "cliente_id", label: "Cliente", type: "select", required: true, optionsFrom: "clientes", optionLabel: (c) => c.nome },
        { key: "veiculo_id", label: "Veículo", type: "select", required: true, optionsFrom: "veiculos", optionLabel: (v) => v.placa + " - " + (v.modelo || "") },
        { key: "mecanico", label: "Mecânico" },
        { key: "problema", label: "Problema relatado", type: "textarea" },
        { key: "servicos", label: "Serviços", type: "textarea" },
        { key: "status", label: "Status", type: "select", required: true, options: ["Aberta", "Em andamento", "Finalizada"] },
        { key: "valor_total", label: "Valor total (R$)", type: "number" },
        { key: "data_entrada", label: "Data de entrada", type: "date", required: true }
      ]
    },

    estoque: {
      coll: "estoque", titulo: "Estoque", singular: "Produto", rotulo: "nome",
      buscaKeys: ["nome", "categoria"],
      colunas: [
        { key: "nome", label: "Produto" },
        { key: "categoria", label: "Categoria" },
        { key: "quantidade", label: "Qtd" },
        { key: "quantidade_minima", label: "Mín" },
        { key: "valor", label: "Valor", format: App.ui.money },
        { key: "fornecedor_id", label: "Fornecedor", resolve: (r) => fornecedorNome(r.fornecedor_id) }
      ],
      campos: [
        { key: "nome", label: "Nome", required: true },
        { key: "categoria", label: "Categoria" },
        { key: "quantidade", label: "Quantidade", type: "number", required: true },
        { key: "quantidade_minima", label: "Quantidade mínima", type: "number", padrao: 5 },
        { key: "valor", label: "Valor unitário (R$)", type: "number" },
        { key: "fornecedor_id", label: "Fornecedor", type: "select", optionsFrom: "fornecedores", optionLabel: (f) => f.nome }
      ],
      rowClass: (r) => Number(r.quantidade) <= Number(r.quantidade_minima) ? "baixo" : "",
      resumo: (rows) => {
        const baixos = rows.filter((r) => Number(r.quantidade) <= Number(r.quantidade_minima));
        return el("div", { class: "cards" }, [
          card("Itens cadastrados", rows.length, "accent"),
          card("Estoque baixo", baixos.length, baixos.length ? "danger" : "ok")
        ]);
      }
    },

    financeiro: {
      coll: "financeiro", titulo: "Financeiro", singular: "Movimento", rotulo: "descricao",
      buscaKeys: ["descricao", "tipo"],
      colunas: [
        { key: "descricao", label: "Descrição" },
        { key: "tipo", label: "Tipo", tag: (r) => r.tipo === "Receita" ? "receita" : "despesa" },
        { key: "valor", label: "Valor", format: App.ui.money },
        { key: "data", label: "Data", format: App.ui.fmtData }
      ],
      campos: [
        { key: "descricao", label: "Descrição", required: true },
        { key: "tipo", label: "Tipo", type: "select", required: true, options: ["Receita", "Despesa"] },
        { key: "valor", label: "Valor (R$)", type: "number", required: true },
        { key: "data", label: "Data", type: "date", required: true }
      ],
      resumo: (rows) => {
        let rec = 0, des = 0;
        rows.forEach((r) => { if (r.tipo === "Receita") rec += Number(r.valor) || 0; else des += Number(r.valor) || 0; });
        const saldo = rec - des;
        return el("div", { class: "cards" }, [
          card("Receitas", App.ui.money(rec), "ok"),
          card("Despesas", App.ui.money(des), "danger"),
          card("Saldo", App.ui.money(saldo), saldo >= 0 ? "accent" : "danger")
        ]);
      }
    },

    fornecedores: {
      coll: "fornecedores", titulo: "Fornecedores", singular: "Fornecedor", rotulo: "nome",
      buscaKeys: ["nome", "cnpj", "telefone", "email"],
      colunas: [
        { key: "nome", label: "Nome" },
        { key: "cnpj", label: "CNPJ", format: V.formatCnpj },
        { key: "telefone", label: "Telefone" },
        { key: "email", label: "E-mail" }
      ],
      campos: [
        { key: "nome", label: "Nome", required: true },
        { key: "cnpj", label: "CNPJ", validate: (v) => V.cnpjValido(v) ? true : "CNPJ inválido" },
        { key: "telefone", label: "Telefone" },
        { key: "email", label: "E-mail" },
        { key: "endereco", label: "Endereço" }
      ],
      antesDeExcluir: (id) => {
        const n = App.db.count("estoque", (e) => e.fornecedor_id === id);
        if (n) throw new Error("Não é possível excluir: " + n + " produto(s) usam este fornecedor.");
      }
    },

    agenda: {
      coll: "agendamentos", titulo: "Agenda", singular: "Agendamento", rotulo: "descricao",
      buscaKeys: ["descricao", "status"],
      colunas: [
        { key: "data", label: "Data", format: App.ui.fmtData },
        { key: "hora", label: "Hora" },
        { key: "cliente_id", label: "Cliente", resolve: (r) => clienteNome(r.cliente_id) },
        { key: "veiculo_id", label: "Veículo", resolve: (r) => veiculoLabel(r.veiculo_id) },
        { key: "descricao", label: "Descrição" },
        { key: "status", label: "Status", tag: (r) => statusAgenda(r.status) }
      ],
      campos: [
        { key: "cliente_id", label: "Cliente", type: "select", required: true, optionsFrom: "clientes", optionLabel: (c) => c.nome },
        { key: "veiculo_id", label: "Veículo", type: "select", optionsFrom: "veiculos", optionLabel: (v) => v.placa + " - " + (v.modelo || "") },
        { key: "data", label: "Data", type: "date", required: true },
        { key: "hora", label: "Hora", type: "time" },
        { key: "descricao", label: "Descrição", type: "textarea" },
        { key: "status", label: "Status", type: "select", options: ["Agendado", "Concluído", "Cancelado"] }
      ],
      ordenar: (a, b) => (String(a.data)).localeCompare(String(b.data)) || (String(a.hora)).localeCompare(String(b.hora))
    },

    usuarios: {
      coll: "usuarios", titulo: "Usuários", singular: "Usuário", rotulo: "nome", adminOnly: true,
      buscaKeys: ["nome", "usuario", "nivel"],
      colunas: [
        { key: "nome", label: "Nome" },
        { key: "usuario", label: "Usuário" },
        { key: "nivel", label: "Nível" }
      ],
      campos: [
        { key: "nome", label: "Nome", required: true },
        { key: "usuario", label: "Usuário (login)", required: true },
        { key: "senha", label: "Senha", type: "password", requiredOnCreate: true, help: "Ao editar, deixe em branco para manter a senha atual.", transform: App.auth.hashSenha },
        { key: "nivel", label: "Nível", type: "select", required: true, options: ["admin", "mecanico", "atendente"] }
      ],
      antesDeExcluir: (id) => {
        const atual = App.auth.atual();
        if (atual && atual.id === id) throw new Error("Você não pode excluir o próprio usuário logado.");
        const alvo = App.db.byId("usuarios", id);
        const admins = App.db.count("usuarios", (u) => u.nivel === "admin");
        if (alvo && alvo.nivel === "admin" && admins <= 1) throw new Error("Não é possível excluir o último administrador.");
      }
    },

    logs: {
      coll: "logs", titulo: "Log de Auditoria", somenteLeitura: true, adminOnly: true,
      buscaKeys: ["usuario", "acao"],
      colunas: [
        { key: "data_hora", label: "Data / Hora", format: fmtDataHora },
        { key: "usuario", label: "Usuário" },
        { key: "acao", label: "Ação" }
      ],
      ordenar: (a, b) => b.id - a.id
    }
  };

  App.entities = entities;
  App.helpers = { clienteNome, veiculoLabel, fornecedorNome, statusOS, card };
})();
