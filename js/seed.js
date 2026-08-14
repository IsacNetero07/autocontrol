window.App=window.App||{};
(function(){
 const hoje=(off=0)=>{const d=new Date();d.setDate(d.getDate()+off);return d.toISOString().slice(0,10)};
 function ensure(){const db=App.db;
  if(!db.count("usuarios")){
   const admin=db.insert("usuarios",{nome:"Isac Admin",usuario:"isac",senha:App.auth.hashSenha("123456"),nivel:"admin"});
   if(!admin) return;
  }
  if(!localStorage.getItem("autocontrol:seeded")){
   const f1=db.insert("fornecedores",{nome:"Auto Peças Central",cnpj:"11222333000181",telefone:"(87) 3333-4444",email:"vendas@apcentral.com",endereco:"Av. Brasil, 1000"});
   const f2=db.insert("fornecedores",{nome:"Distribuidora Motor",cnpj:"",telefone:"(87) 4444-5555",email:"compras@motor.com",endereco:"Rua das Oficinas, 45"});
   if(!f1||!f2){localStorage.removeItem("autocontrol:seeded");return;}
   const c1=db.insert("clientes",{nome:"João Silva",cpf:"11144477735",telefone:"(87) 99999-0000",email:"joao@email.com",endereco:"Rua A, 123"});
   const c2=db.insert("clientes",{nome:"Maria Souza",cpf:"",telefone:"(87) 98888-7777",email:"maria@email.com",endereco:"Rua B, 45"});
   const c3=db.insert("clientes",{nome:"AutoTech Ltda",cpf:"",telefone:"(87) 3771-1111",email:"contato@autotech.com.br",endereco:"Av. Central, 900"});
   const v1=db.insert("veiculos",{placa:"ABC1D23",marca:"Toyota",modelo:"Corolla",ano:"2020",cor:"Prata",quilometragem:"45000",cliente_id:c1.id});
   const v2=db.insert("veiculos",{placa:"XYZ9K88",marca:"Honda",modelo:"Civic",ano:"2019",cor:"Preto",quilometragem:"62000",cliente_id:c2.id});
   const v3=db.insert("veiculos",{placa:"BRA2E25",marca:"Volkswagen",modelo:"Gol",ano:"2021",cor:"Branco",quilometragem:"32000",cliente_id:c3.id});
   db.insert("ordens",{cliente_id:c1.id,veiculo_id:v1.id,mecanico:"Carlos",problema:"Barulho no freio",servicos:"Troca de pastilhas",status:"Aberta",valor_total:350,data_entrada:hoje(-1),progresso:15});
   db.insert("ordens",{cliente_id:c2.id,veiculo_id:v2.id,mecanico:"Carlos",problema:"Revisão periódica",servicos:"Óleo, filtros e inspeção",status:"Em andamento",valor_total:780,data_entrada:hoje(-2),progresso:65});
   db.insert("ordens",{cliente_id:c3.id,veiculo_id:v3.id,mecanico:"Rafael",problema:"Diagnóstico elétrico",servicos:"Scanner e teste de bateria",status:"Finalizada",valor_total:480,data_entrada:hoje(-5),progresso:100});
   db.insert("estoque",{nome:"Óleo 5W30",categoria:"Lubrificantes",quantidade:12,valor:45.9,fornecedor_id:f1.id,quantidade_minima:5});
   db.insert("estoque",{nome:"Filtro de Óleo",categoria:"Filtros",quantidade:3,valor:20,fornecedor_id:f1.id,quantidade_minima:5});
   db.insert("estoque",{nome:"Pastilha de Freio",categoria:"Freios",quantidade:8,valor:80,fornecedor_id:f2.id,quantidade_minima:4});
   db.insert("financeiro",{descricao:"Serviço — Revisão Civic",tipo:"Receita",valor:780,data:hoje(-2)});db.insert("financeiro",{descricao:"Compra de peças",tipo:"Despesa",valor:220,data:hoje(-3)});
   db.insert("agendamentos",{cliente_id:c1.id,veiculo_id:v1.id,data:hoje(0),hora:"09:00",descricao:"Revisão completa",status:"Agendado"});
   db.insert("agendamentos",{cliente_id:c2.id,veiculo_id:v2.id,data:hoje(0),hora:"11:30",descricao:"Troca de óleo",status:"Agendado"});
   db.insert("agendamentos",{cliente_id:c3.id,veiculo_id:v3.id,data:hoje(0),hora:"14:00",descricao:"Diagnóstico elétrico",status:"Agendado"});
   db.insert("checklists",{titulo:"Entrada padrão",descricao:"Inspeção inicial do veículo",itens:["Pneus","Freios","Luzes","Fluidos","Lataria"]});
   try{localStorage.setItem("autocontrol:seeded","1");}catch(e){localStorage.removeItem("autocontrol:seeded");}
  }
  // Migra dados antigos sem apagar nada.
  db.all("ordens").forEach(o=>{const patch={};if(o.progresso==null)patch.progresso=o.status==="Finalizada"?100:o.status==="Em andamento"?60:10;if(!o.timeline)patch.timeline=[{texto:"OS criada",data:o.data_entrada||hoje(0)}];if(!o.checklist)patch.checklist={};if(!o.fotos)patch.fotos=[];if(Object.keys(patch).length)db.update("ordens",o.id,patch);});
 }
 App.seed={ensure};
})();
