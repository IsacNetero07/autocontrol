window.App=window.App||{};App.views=App.views||{};
(function(){
 const el=App.ui.el,icon=App.ui.icon;
 function render(c,id){
  const o=App.db.byId("ordens",id);
  if(!o){App.ui.toast("Ordem de serviço não encontrada.","error");location.hash="#/patio";return;}
  const H=App.helpers, client=App.db.byId("clientes",o.cliente_id), car=App.db.byId("veiculos",o.veiculo_id);
  const photos=Array.isArray(o.fotos)?o.fotos:[], checklist=o.checklist&&typeof o.checklist==="object"?o.checklist:{};
  const head=el("div",{class:"page-head"},[
   el("div",{},[el("a",{class:"back-link",href:"#/patio"},"← Voltar ao pátio"),el("span",{class:"eyebrow"},"ORDEM DE SERVIÇO"),el("h1",{},`OS #${String(o.id).padStart(4,"0")}`),el("p",{},`${H.veiculoLabel(o.veiculo_id)} · ${H.clienteNome(o.cliente_id)}`)]),
   el("div",{class:"page-actions"},[App.ui.button("Editar",()=>editOS(o),{variant:"secondary",icon:"edit"}),App.ui.button("Imprimir",()=>window.print(),{variant:"secondary",icon:"report"})])
  ]);
  const summary=el("div",{class:"os-detail-grid"},[
   panel("Veículo",[line("Modelo",H.veiculoLabel(o.veiculo_id)),line("Placa",car?.placa||"—"),line("Quilometragem",car?.quilometragem?`${car.quilometragem} km`:"—")]),
   panel("Cliente",[line("Nome",client?.nome||"—"),line("Telefone",client?.telefone||"—"),line("E-mail",client?.email||"—")]),
   panel("Serviço",[line("Responsável",o.mecanico||"Não definido"),line("Entrada",App.ui.fmtData(o.data_entrada)),line("Valor",App.ui.money(o.valor_total))])
  ]);
  const progressButtons=[0,25,50,75,100].map(n=>el("button",{class:"progress-btn",type:"button",onclick:()=>{const status=n===100?"Finalizada":n>0?"Em andamento":"Aberta";App.db.update("ordens",o.id,{progresso:n,status});App.ui.toast("Progresso atualizado.","ok");render(c,id);}},`${n}%`));
  const progress=el("div",{class:"panel"},[
   el("div",{class:"panel-head"},[el("strong",{},"Progresso do serviço"),el("span",{class:`status-pill ${H.statusOS(o.status)}`},o.status)]),
   el("div",{class:"big-progress"},el("i",{style:`width:${Number(o.progresso||0)}%`})),
   el("div",{class:"progress-controls"},progressButtons)
  ]);
  const items=["Pneus","Freios","Luzes","Fluidos","Lataria"];
  const check=el("div",{class:"panel"},[el("div",{class:"panel-head"},[el("strong",{},"Checklist de inspeção"),el("span",{},"Toque para marcar")]),el("div",{class:"check-grid"},items.map(item=>{const checked=!!checklist[item];return el("button",{class:`check-item ${checked?"checked":""}`,type:"button",onclick:()=>{checklist[item]=!checklist[item];App.db.update("ordens",o.id,{checklist});render(c,id);}},[el("span",{class:"check-circle"},checked?icon("check"):""),item]);}))]);
  const photoInput=el("input",{type:"file",accept:"image/*",capture:"environment",multiple:true,hidden:true,onchange:e=>{Array.from(e.target.files||[]).slice(0,4).forEach(file=>{const reader=new FileReader();reader.onload=()=>{const data=String(reader.result||"");if(data.length>650_000){App.ui.toast("Foto muito grande. Escolha uma imagem menor.","error");return;}const arr=Array.isArray(o.fotos)?o.fotos:[];arr.push(data);if(!App.db.update("ordens",o.id,{fotos:arr.slice(-4)})){App.ui.toast("Não foi possível salvar a foto. O armazenamento pode estar cheio.","error");return;}render(c,id);};reader.onerror=()=>App.ui.toast("Não foi possível ler a foto.","error");reader.readAsDataURL(file);});}});
  const photosPanel=el("div",{class:"panel"},[el("div",{class:"panel-head"},[el("strong",{},"Fotos do veículo"),App.ui.button("Adicionar foto",()=>photoInput.click(),{variant:"secondary",icon:"camera"})]),photoInput,photos.length?el("div",{class:"photo-grid"},photos.map(src=>el("img",{src,alt:"Foto do veículo"}))):el("div",{class:"empty-state compact"},"Nenhuma foto adicionada. No iPhone, o botão pode abrir a câmera quando disponível. Até 4 fotos são mantidas por OS.")]);
  const timeline=el("div",{class:"panel"},[el("div",{class:"panel-head"},el("strong",{},"Linha do tempo")),el("div",{class:"timeline"},(Array.isArray(o.timeline)?o.timeline:[]).map(t=>el("div",{class:"timeline-item"},[el("i",{}),el("div",{},[el("strong",{},t.texto||"Atualização"),el("small",{},t.data||"")])])))]);
  c.append(
   head,
   summary,
   progress,
   el("div", { class: "two-col" }, [
    el("div", {}, [check, photosPanel]),
    el("div", {}, [
     timeline,
     panel("Resumo", [
      el("p", {}, o.problema || "Sem problema relatado."),
      el("p", {}, o.servicos || "Nenhum serviço informado.")
     ])
    ])
   ])
  );
 }
 function line(k,v){return el("div",{class:"detail-line"},[el("span",{},k),el("strong",{},v)]);}
 function panel(t,children){return el("div",{class:"panel"},[el("div",{class:"panel-head"},el("strong",{},t)),...children]);}
 function editOS(o){const cfg=App.entities.ordens;App.ui.modalForm({titulo:`Editar OS #${String(o.id).padStart(4,"0")}`,campos:cfg.campos,valores:o}).then(res=>{if(!res)return;const nextStatus=res.status;const nextProgress=nextStatus!==o.status?(nextStatus==="Finalizada"?100:nextStatus==="Em andamento"?60:10):(Number.isFinite(Number(o.progresso))?Math.max(0,Math.min(100,Number(o.progresso))):0);const d={...res,cliente_id:Number(res.cliente_id),veiculo_id:Number(res.veiculo_id),valor_total:Number(res.valor_total||0),progresso:nextProgress,checklist:o.checklist||{},fotos:o.fotos||[],timeline:Array.isArray(o.timeline)?o.timeline:[]};if(d.status!==o.status)d.timeline.push({texto:`Status alterado para ${d.status}`,data:new Date().toISOString()});const saved=App.db.update("ordens",o.id,d);if(!saved){App.ui.toast("Não foi possível atualizar a OS.","error");return;}App.ui.toast("OS atualizada.","ok");render(document.querySelector(".content"),o.id);});}
 App.views.osDetail={render};
})();
