// Dados iniciais: cria o usuário administrador e um conjunto de exemplo
// na primeira vez, para o app não abrir vazio no celular.
window.App = window.App || {};

(function () {
  function hoje(offsetDias) {
    const d = new Date();
    d.setDate(d.getDate() + (offsetDias || 0));
    return d.toISOString().slice(0, 10); // yyyy-mm-dd
  }

  function ensure() {
    const db = App.db;

    // Usuário administrador padrão (sempre garante que exista um jeito de entrar).
    if (db.count("usuarios") === 0) {
      db.insert("usuarios", {
        nome: "Isac",
        usuario: "isac",
        senha: App.auth.hashSenha("123456"),
        nivel: "admin"
      });
    }

    // Dados de exemplo, só uma vez.
    if (!localStorage.getItem("autocontrol:seeded")) {
      localStorage.setItem("autocontrol:seeded", "1");

      const f1 = db.insert("fornecedores", { nome: "Auto Peças Central", cnpj: "11222333000181", telefone: "1133334444", email: "vendas@apcentral.com", endereco: "Av. Brasil, 1000" });
      const f2 = db.insert("fornecedores", { nome: "Distribuidora Motor", cnpj: "", telefone: "1144445555", email: "", endereco: "" });

      const c1 = db.insert("clientes", { nome: "João Silva", cpf: "11144477735", telefone: "11999990000", email: "joao@email.com", endereco: "Rua A, 123" });
      const c2 = db.insert("clientes", { nome: "Maria Souza", cpf: "", telefone: "11988887777", email: "maria@email.com", endereco: "Rua B, 45" });

      const v1 = db.insert("veiculos", { placa: "ABC1D23", marca: "Toyota", modelo: "Corolla", ano: "2020", cor: "Prata", quilometragem: "45000", cliente_id: c1.id });
      const v2 = db.insert("veiculos", { placa: "XYZ9K88", marca: "Honda", modelo: "Civic", ano: "2019", cor: "Preto", quilometragem: "62000", cliente_id: c2.id });

      db.insert("ordens", { cliente_id: c1.id, veiculo_id: v1.id, mecanico: "Carlos", problema: "Barulho no freio", servicos: "Troca de pastilhas", status: "Aberta", valor_total: 350, data_entrada: hoje(-1) });
      db.insert("ordens", { cliente_id: c2.id, veiculo_id: v2.id, mecanico: "Carlos", problema: "Revisão", servicos: "Troca de óleo e filtros", status: "Finalizada", valor_total: 480, data_entrada: hoje(-5) });

      db.insert("estoque", { nome: "Óleo 5W30", categoria: "Lubrificantes", quantidade: 12, valor: 45.9, fornecedor_id: f1.id, quantidade_minima: 5 });
      db.insert("estoque", { nome: "Filtro de Óleo", categoria: "Filtros", quantidade: 3, valor: 20, fornecedor_id: f1.id, quantidade_minima: 5 });
      db.insert("estoque", { nome: "Pastilha de Freio", categoria: "Freios", quantidade: 8, valor: 80, fornecedor_id: f2.id, quantidade_minima: 4 });

      db.insert("financeiro", { descricao: "Serviço - Revisão Civic", tipo: "Receita", valor: 480, data: hoje(-5) });
      db.insert("financeiro", { descricao: "Compra de peças", tipo: "Despesa", valor: 220, data: hoje(-3) });

      db.insert("agendamentos", { cliente_id: c1.id, veiculo_id: v1.id, data: hoje(2), hora: "09:00", descricao: "Alinhamento e balanceamento", status: "Agendado" });
    }
  }

  App.seed = { ensure };
})();
