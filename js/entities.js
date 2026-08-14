window.App = window.App || {};
(function () {
  const V = App.validation;
  const el = App.ui.el;
  const clienteNome = id => App.db.byId("clientes", id)?.nome || "—";
  const veiculoLabel = id => { const v = App.db.byId("veiculos", id); return v ? `${v.placa} · ${v.modelo || v.marca || ""}` : "—"; };
  const fornecedorNome = id => App.db.byId("fornecedores", id)?.nome || "—";
  const statusOS = s => s === "Finalizada" ? "finalizada" : s === "Em andamento" ? "andamento" : "aberta";
  const statusAgenda = s => s === "Concluído" ? "finalizada" : s === "Cancelado" ? "despesa" : "aberta";
  const card = (k, v, cls = "") => el("div", { class: `metric-card ${cls}` }, [el("span", { class: "metric-label" }, k), el("strong", {}, v)]);
  const clienteSelect = { type: "select", optionsFrom: "clientes", optionLabel: c => c.nome, required: true };
  const veiculoSelect = { type: "select", optionsFrom: "veiculos", optionLabel: v => `${v.placa} — ${v.modelo || v.marca || ""}`, required: true };

  const entities = {
    clientes: {
      coll: "clientes", titulo: "Clientes", grupo: "GESTÃO", descricao: "Controle e acompanhamento de clientes.", singular: "Cliente", rotulo: "nome",
      buscaKeys: ["nome", "cpf", "telefone", "email"],
      colunas: [
        { key: "nome", label: "Cliente" }, { key: "telefone", label: "Telefone" }, { key: "email", label: "E-mail" }, { key: "cpf", label: "CPF", format: V.formatCpf }
      ],
      campos: [
        { key: "nome", label: "Nome completo", required: true }, { key: "cpf", label: "CPF", validate: v => !v || V.cpfValido(v) || "CPF inválido" },
        { key: "telefone", label: "Telefone" }, { key: "email", label: "E-mail", type: "email" }, { key: "endereco", label: "Endereço" }
      ],
      resumo: r => [
        card("Total de clientes", r.length, "blue"), card("Clientes ativos", r.length, "green"), card("Novos este mês", Math.min(r.length, 12), "purple"),
        card("Faturamento (mês)", App.ui.money(App.db.all("financeiro").filter(x => x.tipo === "Receita").reduce((a, x) => a + Number(x.valor || 0), 0)), "blue")
      ]
      ,antesDeExcluir: id => {
        const vehicles = App.db.count("veiculos", v => Number(v.cliente_id) === Number(id));
        const orders = App.db.count("ordens", o => Number(o.cliente_id) === Number(id));
        if (vehicles || orders) throw new Error(`Não é possível excluir: cliente possui ${vehicles} veículo(s) e ${orders} ordem(ns) vinculada(s).`);
      }
    },
    veiculos: {
      coll: "veiculos", titulo: "Veículos", grupo: "GESTÃO", descricao: "Histórico e cadastro dos veículos atendidos.", singular: "Veículo", rotulo: "placa",
      buscaKeys: ["placa", "marca", "modelo", "cor"],
      colunas: [
        { key: "placa", label: "Placa" }, { key: "marca", label: "Marca" }, { key: "modelo", label: "Modelo" }, { key: "ano", label: "Ano" },
        { key: "cliente_id", label: "Cliente", resolve: r => clienteNome(r.cliente_id) }
      ],
      campos: [
        { key: "placa", label: "Placa", required: true, transform: v => String(v).trim().toUpperCase(), validate: (v, rec) => !App.db.count("veiculos", x => Number(x.id)!==Number(rec?.id) && String(x.placa||"").replace(/[^A-Z0-9]/gi,"").toUpperCase() === String(v||"").replace(/[^A-Z0-9]/gi,"").toUpperCase()) || "Esta placa já está cadastrada." }, { key: "marca", label: "Marca" }, { key: "modelo", label: "Modelo" }, { key: "ano", label: "Ano", type: "number" },
        { key: "cor", label: "Cor" }, { key: "quilometragem", label: "Quilometragem", type: "number" }, { ...clienteSelect, key: "cliente_id", label: "Cliente" }
      ],
      antesDeExcluir: id => { if (App.db.count("ordens", o => Number(o.veiculo_id) === Number(id))) throw new Error("Este veículo possui ordens de serviço vinculadas."); }
    },
    ordens: {
      coll: "ordens", titulo: "Ordens de Serviço", grupo: "OPERAÇÃO", descricao: "Acompanhe serviços, responsáveis e progresso.", singular: "OS", rotulo: "problema",
      buscaKeys: ["mecanico", "problema", "servicos", "status"],
      colunas: [
        { key: "id", label: "OS", format: v => `#${String(v).padStart(4, "0")}` }, { key: "cliente_id", label: "Cliente", resolve: r => clienteNome(r.cliente_id) },
        { key: "veiculo_id", label: "Veículo", resolve: r => veiculoLabel(r.veiculo_id) }, { key: "mecanico", label: "Mecânico" },
        { key: "status", label: "Status", tag: r => statusOS(r.status) }, { key: "valor_total", label: "Valor", format: App.ui.money }
      ],
      campos: [
        { ...clienteSelect, key: "cliente_id", label: "Cliente" }, { ...veiculoSelect, key: "veiculo_id", label: "Veículo" }, { key: "mecanico", label: "Mecânico" },
        { key: "problema", label: "Problema relatado", type: "textarea" }, { key: "servicos", label: "Serviços", type: "textarea" },
        { key: "status", label: "Status", type: "select", options: ["Aberta", "Em andamento", "Finalizada"], required: true },
        { key: "valor_total", label: "Valor total", type: "number", step: "0.01", min: "0", validate: v => Number.isFinite(Number(v)) && Number(v) >= 0 || "Informe um valor válido." }, { key: "data_entrada", label: "Entrada", type: "date", required: true }
      ],
      onView: r => { location.hash = `#/os/${r.id}`; },
      antesDeExcluir: id => { if(App.db.byId("ordens",id)?.status !== "Finalizada") throw new Error("Finalize ou cancele a OS antes de excluí-la."); }
    },
    agenda: {
      coll: "agendamentos", titulo: "Agenda", grupo: "GESTÃO", descricao: "Organize os atendimentos do dia e os próximos horários.", singular: "Agendamento", rotulo: "descricao",
      buscaKeys: ["descricao", "status"],
      colunas: [
        { key: "data", label: "Data", format: App.ui.fmtData }, { key: "hora", label: "Hora" }, { key: "cliente_id", label: "Cliente", resolve: r => clienteNome(r.cliente_id) },
        { key: "veiculo_id", label: "Veículo", resolve: r => veiculoLabel(r.veiculo_id) }, { key: "descricao", label: "Serviço" }, { key: "status", label: "Status", tag: r => statusAgenda(r.status) }
      ],
      campos: [
        { ...clienteSelect, key: "cliente_id", label: "Cliente" }, { ...veiculoSelect, key: "veiculo_id", label: "Veículo", required: false },
        { key: "data", label: "Data", type: "date", required: true }, { key: "hora", label: "Hora", type: "time" }, { key: "descricao", label: "Descrição", type: "textarea" },
        { key: "status", label: "Status", type: "select", options: ["Agendado", "Concluído", "Cancelado"] }
      ]
    },
    estoque: {
      coll: "estoque", titulo: "Estoque", grupo: "GESTÃO", descricao: "Peças, níveis mínimos e fornecedores.", singular: "Produto", rotulo: "nome",
      buscaKeys: ["nome", "categoria"],
      colunas: [
        { key: "nome", label: "Produto" }, { key: "categoria", label: "Categoria" }, { key: "quantidade", label: "Qtd" }, { key: "quantidade_minima", label: "Mínimo" },
        { key: "valor", label: "Valor", format: App.ui.money }, { key: "fornecedor_id", label: "Fornecedor", resolve: r => fornecedorNome(r.fornecedor_id) }
      ],
      campos: [
        { key: "nome", label: "Produto", required: true }, { key: "categoria", label: "Categoria" }, { key: "quantidade", label: "Quantidade", type: "number", required: true, min: "0", validate: v => Number.isFinite(Number(v)) && Number(v) >= 0 || "Informe uma quantidade válida." },
        { key: "quantidade_minima", label: "Mínimo", type: "number", min: "0", validate: v => !v || (Number.isFinite(Number(v)) && Number(v) >= 0) || "Informe um mínimo válido." }, { key: "valor", label: "Valor unitário", type: "number", step: "0.01", min: "0", validate: v => !v || (Number.isFinite(Number(v)) && Number(v) >= 0) || "Informe um valor válido." },
        { key: "fornecedor_id", label: "Fornecedor", type: "select", optionsFrom: "fornecedores", optionLabel: f => f.nome }
      ],
      resumo: r => { const low = r.filter(x => Number(x.quantidade) <= Number(x.quantidade_minima)); return [card("Itens cadastrados", r.length, "blue"), card("Estoque crítico", low.length, low.length ? "red" : "green"), card("Valor em estoque", App.ui.money(r.reduce((a, x) => a + (Number(x.quantidade) || 0) * (Number(x.valor) || 0), 0)), "purple")]; }
    },
    financeiro: {
      coll: "financeiro", titulo: "Financeiro", grupo: "GESTÃO", descricao: "Receitas, despesas e resultado da oficina.", singular: "Movimento", rotulo: "descricao",
      buscaKeys: ["descricao", "tipo"], colunas: [
        { key: "descricao", label: "Descrição" }, { key: "tipo", label: "Tipo", tag: r => r.tipo === "Receita" ? "receita" : "despesa" }, { key: "valor", label: "Valor", format: App.ui.money }, { key: "data", label: "Data", format: App.ui.fmtData }
      ],
      campos: [
        { key: "descricao", label: "Descrição", required: true }, { key: "tipo", label: "Tipo", type: "select", options: ["Receita", "Despesa"], required: true },
        { key: "valor", label: "Valor", type: "number", step: "0.01", required: true }, { key: "data", label: "Data", type: "date", required: true }
      ],
      resumo: r => { const rec = r.filter(x => x.tipo === "Receita").reduce((a, x) => a + Number(x.valor || 0), 0); const des = r.filter(x => x.tipo !== "Receita").reduce((a, x) => a + Number(x.valor || 0), 0); return [card("Receitas", App.ui.money(rec), "green"), card("Despesas", App.ui.money(des), "red"), card("Saldo", App.ui.money(rec - des), rec >= des ? "blue" : "red")]; }
    },
    fornecedores: {
      coll: "fornecedores", titulo: "Fornecedores", grupo: "GESTÃO", descricao: "Parceiros e contatos de fornecimento.", singular: "Fornecedor", rotulo: "nome",
      buscaKeys: ["nome", "cnpj", "telefone", "email"], colunas: [{ key: "nome", label: "Fornecedor" }, { key: "cnpj", label: "CNPJ", format: V.formatCnpj }, { key: "telefone", label: "Telefone" }, { key: "email", label: "E-mail" }],
      campos: [{ key: "nome", label: "Nome", required: true }, { key: "cnpj", label: "CNPJ", validate: v => !v || V.cnpjValido(v) || "CNPJ inválido" }, { key: "telefone", label: "Telefone" }, { key: "email", label: "E-mail", type: "email" }, { key: "endereco", label: "Endereço" }]
    },
    usuarios: {
      coll: "usuarios", titulo: "Usuários", grupo: "CONFIGURAÇÕES", descricao: "Controle de acessos locais.", singular: "Usuário", rotulo: "nome", adminOnly: true,
      buscaKeys: ["nome", "usuario", "nivel"], colunas: [{ key: "nome", label: "Nome" }, { key: "usuario", label: "Login" }, { key: "nivel", label: "Perfil" }],
      campos: [{ key: "nome", label: "Nome", required: true }, { key: "usuario", label: "Login", required: true, validate: (v, rec) => !App.db.count("usuarios", u => Number(u.id)!==Number(rec?.id) && String(u.usuario||"").toLowerCase() === v.trim().toLowerCase()) || "Este login já está em uso." }, { key: "senha", label: "Senha", type: "password", requiredOnCreate: true, validate: v => v.length >= 6 || "A senha deve ter pelo menos 6 caracteres.", transform: App.auth.hashSenha }, { key: "nivel", label: "Perfil", type: "select", options: ["admin", "mecanico", "atendente"], required: true }]
      ,antesDeExcluir: id => {
        const current = App.auth.atual();
        if (current && Number(current.id) === Number(id)) throw new Error("Você não pode excluir o usuário que está conectado.");
        const target = App.db.byId("usuarios", id);
        if (target?.nivel === "admin" && App.db.count("usuarios", u => u.nivel === "admin") <= 1) throw new Error("Não é possível excluir o último administrador.");
      }
    },
    logs: {
      coll: "logs", titulo: "Auditoria", grupo: "RELATÓRIOS", descricao: "Histórico das alterações feitas no aplicativo.", singular: "Registro", adminOnly: true, somenteLeitura: true,
      buscaKeys: ["usuario", "acao"], colunas: [{ key: "data_hora", label: "Data / hora", format: v => new Date(v).toLocaleString("pt-BR") }, { key: "usuario", label: "Usuário" }, { key: "acao", label: "Ação" }]
    },
    checklists: {
      coll: "checklists", titulo: "Checklists", grupo: "OPERAÇÃO", descricao: "Modelos de inspeção para padronizar a oficina.", singular: "Checklist", rotulo: "titulo",
      buscaKeys: ["titulo", "descricao"], colunas: [{ key: "titulo", label: "Checklist" }, { key: "descricao", label: "Descrição" }, { key: "itens", label: "Itens", format: v => Array.isArray(v) ? v.length : v ? 1 : 0 }],
      campos: [{ key: "titulo", label: "Título", required: true }, { key: "descricao", label: "Descrição", type: "textarea" }, { key: "itens", label: "Itens (separe por vírgula)", help: "Ex.: pneus, freios, luzes, fluidos" }],
      aoSalvar: r => { if (typeof r.itens === "string") App.db.update("checklists", r.id, { itens: r.itens.split(",").map(x => x.trim()).filter(Boolean) }); }
    }
  };
  App.entities = entities;
  App.helpers = { clienteNome, veiculoLabel, fornecedorNome, statusOS, card };
})();
