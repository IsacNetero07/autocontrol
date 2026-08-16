window.App=window.App||{};App.views=App.views||{};
(function(){const el=App.ui.el;const icon=App.ui.icon;
 const today=()=>new Date().toISOString().slice(0,10);
 // Antes era "Bom dia" fixo, inclusive às 23h.
 const saudacao=()=>{const h=new Date().getHours();return h<12?"Bom dia":h<18?"Boa tarde":"Boa noite";};
 function render(c){App.ui.clear(c);const db=App.db,H=App.helpers;const clients=db.all("clientes"),cars=db.all("veiculos"),os=db.all("ordens"),fin=db.all("financeiro"),stock=db.all("estoque"),agenda=db.all("agendamentos");const rec=fin.filter(x=>x.tipo==="Receita").reduce((a,x)=>a+Number(x.valor||0),0),des=fin.filter(x=>x.tipo!=="Receita").reduce((a,x)=>a+Number(x.valor||0),0),low=stock.filter(x=>Number(x.quantidade)<=Number(x.quantidade_minima)),open=os.filter(x=>x.status!=="Finalizada"),todayAg=agenda.filter(x=>x.data===today()&&x.status!=="Cancelado");
  const head=el("div",{class:"dashboard-head"},[el("div",{},[el("span",{class:"eyebrow"},"VISÃO GERAL"),el("h1",{},`${saudacao()}, ${App.auth.atual()?.nome?.split(" ")[0]||"gestor"}`),el("p",{},"Resumo operacional da oficina hoje.")]),el("div",{class:"date-chip"},[icon("calendar"),new Intl.DateTimeFormat("pt-BR",{dateStyle:"full"}).format(new Date())])]);
  const kpis=el("div",{class:"kpi-grid"},[
   kpi("Veículos no pátio",new Set(open.map(x=>Number(x.veiculo_id)).filter(Boolean)).size,"Em atendimento agora","car","blue"),kpi("Ordens de serviço",os.length,`${os.filter(x=>x.status==="Finalizada").length} finalizadas`,"clipboard","green"),kpi("Agendamentos",todayAg.length,"Hoje","calendar","purple"),kpi("Receita acumulada",App.ui.money(rec),des?`${((rec-des)/Math.max(rec,1)*100).toFixed(1)}% líquido`:"Sem despesas","money","blue")]);
  const graph=el("div",{class:"panel chart-panel"},[el("div",{class:"panel-head"},[el("div",{},[el("strong",{},"Movimentação financeira"),el("span",{},"Últimos 6 meses")]),el("span",{class:"mini-badge"},"Receitas × despesas")]),el("div",{},[chartFinanceiro(fin),el("div",{class:"chart-legend"},[el("span",{},[el("i",{class:"dot revenue"}),"Receitas"]),el("span",{},[el("i",{class:"dot expense"}),"Despesas"])])])]);
  const finance=el("div",{class:"panel"},[el("div",{class:"panel-head"},[el("strong",{},"Resumo financeiro"),el("a",{href:"#/financeiro"},"Ver completo")]),metricRow("Receitas",App.ui.money(rec),"green","money"),metricRow("Despesas",App.ui.money(des),"red","money"),metricRow("Lucro",App.ui.money(rec-des),rec>=des?"green":"red","chart"),metricRow("Ticket médio",App.ui.money(os.length?os.reduce((a,x)=>a+Number(x.valor_total||0),0)/os.length:0),"blue","wallet")]);
  const alerts=el("div",{class:"panel"},[el("div",{class:"panel-head"},[el("strong",{},"Alertas importantes"),el("a",{href:"#/estoque"},"Ver todos")]),alertRow(os.filter(x=>x.status!=="Finalizada"&&Number(x.progresso||0)<25).length,"OS precisam de atenção","Revisar serviços em baixa progressão","red","clock"),alertRow(low.length,"Estoque crítico",`${low.length} item(ns) abaixo do mínimo`,low.length?"yellow":"green","box"),alertRow(todayAg.length,"Atendimentos hoje",`${todayAg.length} agendamento(s)`,"blue","calendar"),alertRow(agenda.filter(x=>x.status==="Agendado"&&x.data<today()).length,"Agendamentos atrasados","Confira a agenda","red","bell")]);
  const lower=el("div",{class:"two-col"},[el("div",{},[graph,patio(os,H)]),el("div",{},[finance,alerts,agendaPanel(todayAg,H)])]);
  const quick=el("div",{class:"panel quick-panel"},[el("div",{class:"panel-head"},[el("strong",{},"Ações rápidas"),el("span",{},"Atalhos para o dia a dia")]),el("div",{class:"quick-grid"},[
   quickBtn("Nova OS","#/ordens","clipboard"),quickBtn("Novo cliente","#/clientes","users"),quickBtn("Novo veículo","#/veiculos","car"),quickBtn("Agendar","#/agenda","calendar"),quickBtn("Comprar peça","#/estoque","box"),quickBtn("Financeiro","#/financeiro","money")])]);
  c.append(head,kpis,lower,quick);
 }
 /* --- gráfico de barras agrupadas: receitas × despesas por mês ------------
    Substitui a antiga ".fake-chart", que era decoração em CSS e não tinha
    relação nenhuma com os dados. As duas cores são as séries validadas para
    daltonismo (azul #4C90F0 × âmbar #C87619, ΔE 28.2 em protanopia); a
    identidade também está na legenda em texto, nunca só na cor. */
 const SVG="http://www.w3.org/2000/svg";
 function sv(tag,attrs,children){const n=document.createElementNS(SVG,tag);Object.entries(attrs||{}).forEach(([k,v])=>{if(v!=null)n.setAttribute(k,String(v));});(Array.isArray(children)?children:children!=null?[children]:[]).forEach(ch=>n.appendChild(ch instanceof Node?ch:document.createTextNode(String(ch))));return n;}
 // Barra com o topo arredondado e a base fixa na linha zero.
 function barra(x,y,w,h,cor,serie,valor){const r=Math.min(3,w/2,h);if(h<=0)return null;const d=`M${x} ${y+h}V${y+r}q0 ${-r} ${r} ${-r}h${w-2*r}q${r} 0 ${r} ${r}V${y+h}Z`;return sv("path",{d,fill:cor,class:"chart-bar","data-serie":serie,"data-valor":valor,"data-altura":h});}
 const mesesCurtos=["JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"];

 function chartFinanceiro(fin){
  // Últimos 6 meses corridos, mesmo os sem lançamento — buracos escondidos
  // distorcem a leitura de tendência.
  const hoje=new Date(), meses=[];
  for(let i=5;i>=0;i--){const d=new Date(hoje.getFullYear(),hoje.getMonth()-i,1);meses.push({chave:`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}`,rotulo:mesesCurtos[d.getMonth()],receita:0,despesa:0});}
  const porChave=new Map(meses.map(m=>[m.chave,m]));
  fin.forEach(x=>{const m=porChave.get(String(x.data||"").slice(0,7));if(!m)return;const v=Number(x.valor)||0;if(x.tipo==="Receita")m.receita+=v;else m.despesa+=v;});

  const W=560,H=190,ml=52,mr=8,mt=10,mb=24,pw=W-ml-mr,ph=H-mt-mb;
  const svg=sv("svg",{class:"chart",viewBox:`0 0 ${W} ${H}`,role:"img","aria-label":"Receitas e despesas dos últimos 6 meses"});

  const maximo=Math.max(...meses.map(m=>Math.max(m.receita,m.despesa)),0);
  if(!maximo){svg.appendChild(sv("text",{x:W/2,y:H/2,"text-anchor":"middle",class:"chart-empty"},"Sem lançamentos financeiros no período."));return svg;}
  // Topo "redondo" para o eixo não terminar num número quebrado.
  const passo=Math.pow(10,Math.floor(Math.log10(maximo)));
  const teto=Math.ceil(maximo/passo)*passo;
  const y=v=>mt+ph-(v/teto)*ph;
  const compacto=new Intl.NumberFormat("pt-BR",{notation:"compact",maximumFractionDigits:1});

  // Grade e eixo de valores (recessivos: só orientam a leitura).
  const grade=sv("g",{class:"chart-grid"});
  [0,.5,1].forEach(f=>{const vy=y(teto*f);grade.appendChild(sv("line",{x1:ml,y1:vy,x2:W-mr,y2:vy}));grade.appendChild(sv("text",{x:ml-8,y:vy+3,"text-anchor":"end",class:"chart-axis value"},compacto.format(teto*f)));});
  svg.appendChild(grade);

  const banda=pw/meses.length, grupo=banda*.62, larg=(grupo-2)/2; // 2px de respiro entre as barras
  meses.forEach((m,i)=>{
   const x0=ml+banda*i, xg=x0+(banda-grupo)/2;
   const g=sv("g",{class:"chart-col"});
   g.appendChild(sv("rect",{x:x0,y:mt,width:banda,height:ph,class:"chart-hover"}));
   const r=barra(xg,y(m.receita),larg,mt+ph-y(m.receita),"var(--series-1)","receita",m.receita);
   const d=barra(xg+larg+2,y(m.despesa),larg,mt+ph-y(m.despesa),"var(--series-2)","despesa",m.despesa);
   if(r)g.appendChild(r); if(d)g.appendChild(d);
   g.appendChild(sv("text",{x:x0+banda/2,y:H-8,"text-anchor":"middle",class:"chart-axis"},m.rotulo));
   // Tooltip nativo: identifica série e valor sem depender da cor.
   g.appendChild(sv("title",{},`${m.rotulo}\nReceitas: ${App.ui.money(m.receita)}\nDespesas: ${App.ui.money(m.despesa)}`));
   g.appendChild(sv("rect",{x:x0,y:mt,width:banda,height:ph,class:"chart-hit"}));
   svg.appendChild(g);
  });
  return svg;
 }
 function kpi(label,value,sub,ic,cls){return el("div",{class:"kpi"},[el("div",{class:`kpi-icon ${cls}`},icon(ic)),el("div",{},[el("span",{},label),el("strong",{},value),el("small",{},sub)])]);}
 function metricRow(label,val,cls,ic){return el("div",{class:"metric-row"},[el("span",{},[el("i",{class:`mini-icon ${cls}`},icon(ic)),label]),el("strong",{class:cls},val)]);}
 function alertRow(num,title,sub,cls,ic){return el("div",{class:"alert-row"},[el("span",{class:`alert-icon ${cls}`},icon(ic)),el("div",{},[el("strong",{},`${num} ${title}`),el("small",{},sub)])]);}
 function patio(os,H){const cols={"Aberta":[],"Em andamento":[],"Finalizada":[]};os.forEach(o=>{if(cols[o.status])cols[o.status].push(o)});return el("div",{class:"panel patio-panel"},[el("div",{class:"panel-head"},[el("div",{},[el("strong",{},"Pátio Digital"),el("span",{},"Visão geral da operação")]),el("a",{href:"#/patio"},"Abrir pátio →")]),el("div",{class:"mini-kanban"},[
   col("Novos",cols["Aberta"],"blue",H),col("Em serviço",cols["Em andamento"],"yellow",H),col("Pronto",cols["Finalizada"],"green",H)])]);}
 function col(title,items,cls,H){return el("div",{class:"kan-col"},[el("div",{class:"kan-title"},[el("span",{},title),el("b",{class:cls},items.length)]),...(items.slice(0,3).map(o=>el("button",{class:"kan-card",onclick:()=>location.hash=`#/os/${o.id}`},[el("strong",{},`OS #${String(o.id).padStart(4,"0")}`),el("span",{},H.veiculoLabel(o.veiculo_id)),el("small",{},H.clienteNome(o.cliente_id)),el("div",{class:"progress"},el("i",{style:`width:${Number(o.progresso||0)}%`}))])))]);}
 function agendaPanel(items,H){return el("div",{class:"panel"},[el("div",{class:"panel-head"},[el("strong",{},"Agenda de hoje"),el("a",{href:"#/agenda"},"Ver agenda")]),items.length?items.slice(0,5).map(a=>el("div",{class:"agenda-row"},[el("b",{},a.hora||"--:--"),el("div",{},[el("strong",{},H.clienteNome(a.cliente_id)),el("small",{},a.descricao||"Atendimento")])])):el("div",{class:"empty-state compact"},"Nenhum agendamento para hoje.")]);}
 function quickBtn(label,href,ic){return el("a",{class:"quick-btn",href},[el("span",{class:"quick-icon"},icon(ic)),el("span",{},label),icon("arrow")]);}
 App.views.dashboard={render};})();
