window.App=window.App||{};App.views=App.views||{};
(function(){
  const el=App.ui.el, icon=App.ui.icon;
  const collections=App.db.COLECOES;
  const labels={clientes:'Clientes',veiculos:'Veículos',ordens:'Ordens de Serviço',estoque:'Estoque',fornecedores:'Fornecedores',financeiro:'Financeiro',agendamentos:'Agenda',usuarios:'Usuários',logs:'Auditoria',checklists:'Checklists'};
  const today=()=>new Date().toISOString().slice(0,10);
  function snapshot(){return JSON.stringify({version:2,exportedAt:new Date().toISOString(),data:App.db.load()},null,2);}
  function downloadBackup(){App.ui.baixar(`autocontrol-backup-${today()}.json`,snapshot(),'application/json');App.ui.toast('Backup completo exportado.','ok');}
  function validateBackup(raw){
    if(!raw||typeof raw!=='object'||Array.isArray(raw))throw new Error('Arquivo inválido.');
    const data=raw.data&&typeof raw.data==='object'?raw.data:raw;
    if(!data||typeof data!=='object'||Array.isArray(data))throw new Error('Estrutura de dados inválida.');
    for(const c of collections)if(data[c]!=null&&!Array.isArray(data[c]))throw new Error(`A coleção ${c} é inválida.`);
    return data;
  }
  function restoreBackup(file){
    const reader=new FileReader();reader.onload=()=>{
      try{
        const raw=JSON.parse(reader.result);const data=validateBackup(raw);
        const normalized={_seq:{}};collections.forEach(c=>normalized[c]=Array.isArray(data[c])?data[c]:[]);
        const seq=data._seq&&typeof data._seq==='object'?data._seq:{};normalized._seq=Object.fromEntries(collections.map(c=>[c,Math.max(Number(seq[c])||0,...normalized[c].map(r=>Number(r.id)||0),0)]));
        const previous=localStorage.getItem(App.db.KEY);localStorage.setItem(App.db.KEY,JSON.stringify(normalized));
        try{App.db.invalidate();}catch(e){if(previous===null)localStorage.removeItem(App.db.KEY);else localStorage.setItem(App.db.KEY,previous);App.db.invalidate();throw e;}
        App.ui.toast('Backup restaurado. O aplicativo será recarregado.','ok');setTimeout(()=>location.reload(),500);
      }catch(e){App.ui.toast(`Não foi possível restaurar: ${e.message||'arquivo inválido'}`,'error');}
    };reader.onerror=()=>App.ui.toast('Falha ao ler o arquivo.','error');reader.readAsText(file);
  }
  function importBackup(){const input=el('input',{type:'file',accept:'.json,application/json',hidden:'true'});input.addEventListener('change',()=>{if(input.files[0])restoreBackup(input.files[0]);});document.body.append(input);input.click();setTimeout(()=>input.remove(),1000);}
  function systemHealth(){const d=App.db.load();const tests=[];tests.push(['Banco local',!!d&&typeof d==='object']);tests.push(['Coleções',collections.every(c=>Array.isArray(d[c]))]);tests.push(['Sessão',!!App.auth.atual()]);tests.push(['PWA','serviceWorker' in navigator]);tests.push(['Criptografia de senha',App.auth.criptoForte()]);tests.push(['Conexão',navigator.onLine]);tests.push(['Dados de exemplo',!!localStorage.getItem('autocontrol:seeded')]);return tests;}
  function notifications(){
    const low=App.db.all('estoque').filter(x=>Number(x.quantidade)<=Number(x.quantidade_minima));
    const late=App.db.all('agendamentos').filter(x=>x.status==='Agendado'&&x.data<today());
    const urgent=App.db.all('ordens').filter(x=>x.status!=='Finalizada'&&Number(x.progresso||0)<25);
    const rows=[...low.map(x=>({ic:'box',title:`Estoque crítico: ${x.nome}`,desc:`${x.quantidade} unidade(s), mínimo ${x.quantidade_minima}`,href:'#/estoque',cls:'warning'})),...late.map(x=>({ic:'calendar',title:`Agendamento atrasado`,desc:`${x.data} · ${x.descricao||'Atendimento'}`,href:'#/agenda',cls:'danger'})),...urgent.map(x=>({ic:'clock',title:`OS #${String(x.id).padStart(4,'0')} precisa de atenção`,desc:`Progresso em ${Number(x.progresso||0)}%`,href:`#/os/${x.id}`,cls:'danger'}))];
    const bg=el('div',{class:'modal-bg'}), modal=el('div',{class:'modal notification-modal'});
    modal.append(el('div',{class:'modal-head'},[el('div',{},[el('strong',{},'Central de notificações'),el('span',{},`${rows.length} alerta(s) encontrado(s)`) ]),App.ui.iconButton('close','Fechar',()=>bg.remove(),'secondary')]));
    const body=el('div',{class:'modal-body notification-list'});if(!rows.length)body.append(el('div',{class:'empty-state'},[icon('checkcircle'),el('strong',{},'Tudo em ordem'),el('span',{},'Não há alertas operacionais no momento.') ]));else rows.slice(0,30).forEach(r=>body.append(el('a',{class:`notification-item ${r.cls}`,href:r.href,onclick:()=>bg.remove()},[el('span',{class:'notification-item-icon'},icon(r.ic)),el('span',{},[el('strong',{},r.title),el('small',{},r.desc)]),icon('arrow')])));
    modal.append(body,el('div',{class:'modal-foot'},[App.ui.button('Ir para a Central',()=>{bg.remove();location.hash='#/central'},{variant:'secondary',icon:'zap'}),App.ui.button('Fechar',()=>bg.remove())]));bg.append(modal);document.body.append(bg);
  }
  function render(c){
    const d=App.db.load(), health=systemHealth(), total=collections.reduce((a,k)=>a+d[k].length,0), os=App.db.all('ordens'), low=App.db.all('estoque').filter(x=>Number(x.quantidade)<=Number(x.quantidade_minima));
    const head=el('div',{class:'page-head'},[el('div',{},[el('span',{class:'eyebrow'},'CENTRAL DE OPERAÇÕES'),el('h1',{},'Ferramentas & Segurança'),el('p',{},'Backup, manutenção, diagnóstico e atalhos para manter a oficina funcionando.')]),el('div',{class:'page-actions'},[App.ui.button('Novo backup',downloadBackup,{icon:'download'}),App.ui.button('Restaurar',importBackup,{variant:'secondary',icon:'upload'})])]);
    const cards=el('div',{class:'summary-grid'},[metric('Registros locais',total,'database','blue'),metric('OS em aberto',os.filter(x=>x.status!=='Finalizada').length,'clipboard','yellow'),metric('Estoque crítico',low.length,'box',low.length?'red':'green'),metric('Status',navigator.onLine?'Online':'Offline','wifi',navigator.onLine?'green':'red')]);
    const healthPanel=el('div',{class:'panel'},[el('div',{class:'panel-head'},[el('div',{},[el('strong',{},'Diagnóstico do sistema'),el('span',{},'Verificação rápida antes de publicar uma nova versão.')]),el('span',{class:'mini-badge'},'LOCAL')])]);
    health.forEach(([label,ok])=>healthPanel.append(el('div',{class:'health-row'},[el('span',{},[icon(ok?'checkcircle':'info'),label]),el('strong',{class:ok?'ok':'bad'},ok?'OK':'ATENÇÃO')])));
    const tools=el('div',{class:'panel'},[el('div',{class:'panel-head'},[el('strong',{},'Ferramentas essenciais'),el('span',{},'Operações seguras e reversíveis quando possível.')]),el('div',{class:'tool-grid'},[
      tool('Backup completo','Salva clientes, veículos, OS, financeiro, estoque e configurações locais.','download',downloadBackup),
      tool('Restaurar backup','Importa um JSON do AutoControl e recarrega o aplicativo.','upload',()=>App.ui.confirmar('Restaurar substitui os dados locais atuais. Faça um backup antes. Continuar?','Escolher arquivo').then(ok=>ok&&importBackup())),
      tool('Exportar tudo','Gera um arquivo JSON legível para auditoria e migração.','file',downloadBackup),
      tool('Notificações','Veja estoque crítico, OS atrasadas e agendamentos vencidos.','bell',notifications),
      tool('Instalar aplicativo','Adiciona o AutoControl à tela inicial quando o navegador permitir.','zap',async()=>{const ok=await App.pwa?.install?.();if(ok)App.ui.toast('AutoControl instalado.','ok');}),
      tool('Recarregar sistema','Atualiza a interface sem apagar os dados locais.','refresh',()=>location.reload())
    ])]);
    const tips=el('div',{class:'panel'},[el('div',{class:'panel-head'},[el('strong',{},'Boas práticas'),el('span',{},'Recomendado para uso profissional')]),el('div',{class:'tips-grid'},[
      tip('Backup semanal','Exporte um backup antes de grandes alterações ou testes.'),tip('Celular','Use HTTPS para instalar como PWA e acessar câmera/recursos do iPhone.'),tip('Privacidade','O modo atual guarda dados no dispositivo. Para equipes, o próximo passo é sincronização com servidor.'),tip('Auditoria','Use a área de logs para investigar alterações e manter rastreabilidade.')
    ])]);
    c.append(head,cards,el('div',{class:'two-col'},[healthPanel,tools]),tips);
  }
  function metric(label,value,ic,cls){return el('div',{class:'metric-card '+cls},[el('span',{class:'metric-icon'},icon(ic)),el('span',{class:'metric-label'},label),el('strong',{},value)]);}
  function tool(title,desc,ic,action){return el('button',{class:'tool-card',type:'button',onclick:action},[el('span',{class:'tool-icon'},icon(ic)),el('span',{},[el('strong',{},title),el('small',{},desc)]),icon('arrow')]);}
  function tip(t,d){return el('div',{class:'tip-card'},[el('span',{class:'tip-icon'},icon('shield')),el('div',{},[el('strong',{},t),el('p',{},d)])]);}
  App.views.central={render,notificacoes:notifications};
})();
