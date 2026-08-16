window.App=window.App||{};
(function(){
  function el(tag,attrs,children){
    const n=document.createElement(tag); attrs=attrs||{};
    Object.keys(attrs).forEach(k=>{const v=attrs[k]; if(v==null)return; if(k==="class")n.className=v; else if(k==="html")n.innerHTML=v; else if(k==="text")n.textContent=v; else if(k.startsWith("on")&&typeof v==="function")n.addEventListener(k.slice(2).toLowerCase(),v); else if(k==="value")n.value=v; else n.setAttribute(k,v);});
    const append = c => { if(c==null||c===false) return; if(Array.isArray(c)){ c.forEach(append); return; } n.appendChild(c instanceof Node ? c : document.createTextNode(String(c))); };
    if(children!=null) append(children);
    return n;
  }
  const clear=n=>{while(n.firstChild)n.removeChild(n.firstChild);return n;};
  const money=v=>new Intl.NumberFormat("pt-BR",{style:"currency",currency:"BRL"}).format(Number(v)||0);
  const fmtData=v=>{if(!v)return "—";const p=String(v).slice(0,10).split("-");return p.length===3?`${p[2]}/${p[1]}/${p[0]}`:String(v);};
  const initials=s=>String(s||"?").trim().split(/\s+/).slice(0,2).map(x=>x[0]).join("").toUpperCase();
  const icon=(name,label="")=>{const paths={
    dashboard:'<path d="M3 13h8V3H3v10Zm10 8h8V3h-8v18ZM3 21h8v-6H3v6Z"/>',
    car:'<path d="m5 16-1 3h2l1-2h10l1 2h2l-1-3 1-4-2-5H6l-2 5 1 4Zm2-7h10l1 3H6l1-3Zm0 7a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Zm10 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Z"/>',
    clipboard:'<path d="M9 4h6v3H9V4Zm-3 1h2v3h8V5h2v15H6V5Zm3 7h6v2H9v-2Zm0 4h4v2H9v-2Z"/>',
    calendar:'<path d="M6 2v3m12-3v3M4 9h16M5 4h14a1 1 0 0 1 1 1v14H4V5a1 1 0 0 1 1-1Zm3 9h3v3H8v-3Z"/>',
    users:'<path d="M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm-7 9a7 7 0 0 1 14 0H2Zm15-8a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm-1 2a6 6 0 0 1 5 3h-5v-3Z"/>',
    box:'<path d="m12 3 8 4-8 4-8-4 8-4Zm-8 8 8 4 8-4v9l-8 4-8-4v-9Zm8 4v9"/>',
    money:'<path d="M4 6h16v12H4V6Zm3 3h10m-7 5h4M8 9a3 3 0 0 0 0 6"/>',
    truck:'<path d="M3 6h11v10H3V6Zm11 4h4l3 3v3h-7v-6Zm-8 8a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm10 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"/>',
    chart:'<path d="M4 19V5m0 14h17M7 15l4-5 3 3 5-7"/>',
    wrench:'<path d="m14 6 4 4m-9 9-5-5 9-9a5 5 0 0 0 6 6l-9 9Zm-5-2 3 3"/>',
    search:'<circle cx="11" cy="11" r="6"/><path d="m16 16 5 5"/>',
    bell:'<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9ZM10 21h4"/>',
    plus:'<path d="M12 5v14M5 12h14"/>',
    settings:'<path d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Zm0-6 1 3 3 1 2-2 2 2-2 2 1 3 3 1v3l-3 1-1 3 2 2-2 2-2-2-3 1-1 3H9l-1-3-3-1-2 2-2-2 2-2-1-3-3-1v-3l3-1 1-3-2-2 2-2 2 2 3-1 1-3h3Z"/>',
    report:'<path d="M6 3h12v18H6V3Zm3 4h6m-6 4h6m-6 4h4"/>',
    check:'<path d="m5 12 4 4L19 6"/>',
    logout:'<path d="M10 5H5v14h5m5-4 4-3-4-3m4 3H9"/>',
    menu:'<path d="M4 7h16M4 12h16M4 17h16"/>',
    close:'<path d="m6 6 12 12M18 6 6 18"/>',
    eye:'<path d="M2 12s3-6 10-6 10 6 10 6-3 6-10 6S2 12 2 12Zm10 3a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/>',
    edit:'<path d="m4 16-.8 4.8L8 20l11-11-4-4L4 16Zm9-9 4 4"/>',
    trash:'<path d="M5 7h14m-9 4v6m4-6v6M9 7V4h6v3m-9 0 1 14h10l1-14"/>',
    filter:'<path d="M4 5h16l-6 7v6l-4 2v-8L4 5Z"/>',
    camera:'<path d="M4 7h4l2-2h4l2 2h4v12H4V7Zm8 9a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z"/>',
    arrow:'<path d="M5 12h14m-6-6 6 6-6 6"/>',
    download:'<path d="M12 3v12m0 0 5-5m-5 5-5-5M4 20h16"/>',
    phone:'<path d="M6 3h3l2 5-2 2a14 14 0 0 0 5 5l2-2 5 2v3c0 1-1 2-2 2C10 20 4 14 4 5c0-1 1-2 2-2Z"/>',
    clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    wallet:'<path d="M4 6h16v13H4V6Zm0 3h16M16 13h4"/>',
    help:'<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 4 2c-1 .7-1.5 1.2-1.5 2.5M12 17h.01"/>',
    moon:'<path d="M20 15.5A8 8 0 0 1 8.5 4 8 8 0 1 0 20 15.5Z"/>'
  }; const svg=document.createElementNS("http://www.w3.org/2000/svg","svg");svg.setAttribute("viewBox","0 0 24 24");svg.setAttribute("aria-hidden",label?"false":"true");svg.setAttribute("class","icon");if(label)svg.setAttribute("aria-label",label);svg.innerHTML=paths[name]||paths.dashboard;return svg;};
  function button(label,action,opts={}){const b=el("button",{class:`btn ${opts.variant||""} ${opts.small?"small":""}`,type:"button",title:opts.title||label,onclick:action},[]); if(opts.icon)b.append(icon(opts.icon)); b.append(el("span",{},label)); return b;}
  function toast(msg,type="") { let box=document.querySelector(".toasts"); if(!box){box=el("div",{class:"toasts"});document.body.append(box);} const t=el("div",{class:`toast ${type}`},msg);box.append(t);setTimeout(()=>{t.classList.add("hide");setTimeout(()=>t.remove(),250);},2800); }
  function confirmar(msg,okLabel="Confirmar"){return new Promise(resolve=>{const bg=el("div",{class:"modal-bg"});const close=r=>{bg.remove();resolve(r);};bg.append(el("div",{class:"modal"},[el("div",{class:"modal-head"},[el("strong",{},"Confirmar ação"),button("Fechar",()=>close(false),{variant:"icon-only",icon:"close",title:"Fechar"})]),el("div",{class:"modal-body"},el("p",{class:"confirm-text"},msg)),el("div",{class:"modal-foot"},[button("Cancelar",()=>close(false),{variant:"secondary"}),button(okLabel,()=>close(true),{variant:"danger"})])]));document.body.append(bg);});}
  function modalForm({titulo,campos=[],valores={}}){return new Promise(resolve=>{const bg=el("div",{class:"modal-bg"});const form=el("form",{class:"modal"});const body=el("div",{class:"modal-body"});const inputs={};const errors={};
    form.append(el("div",{class:"modal-head"},[el("strong",{},titulo),button("Fechar",()=>{bg.remove();resolve(null);},{variant:"icon-only",icon:"close",title:"Fechar"})]));
    campos.forEach(c=>{const wrap=el("label",{class:"field"});wrap.append(el("span",{class:"field-label"},[c.label,c.required?el("b",{class:"required"}," *"):null]));let input;
      if(c.type==="textarea"){input=el("textarea",{name:c.key,placeholder:c.placeholder||"",rows:"4"},valores[c.key]??"");}
      else if(c.type==="select"){input=el("select",{name:c.key});input.append(el("option",{value:""},c.placeholder||"Selecione..."));let opts=c.options||[];if(c.optionsFrom)opts=App.db.all(c.optionsFrom).map(r=>({value:r.id,label:c.optionLabel?c.optionLabel(r):String(r.nome||r.id)}));opts.forEach(o=>{const value=typeof o==="object"?o.value:o;const label=typeof o==="object"? (typeof o.label==="function"?o.label():o.label):o;input.append(el("option",{value:String(value)},label));});input.value=valores[c.key]==null?"":String(valores[c.key]);}
      else {input=el("input",{name:c.key,type:c.type||"text",placeholder:c.placeholder||"",min:c.min,max:c.max,step:c.step});input.value=valores[c.key]==null?"":String(valores[c.key]);}
      if(c.required)input.required=true; wrap.append(input); if(c.help)wrap.append(el("small",{class:"field-help"},c.help));const er=el("small",{class:"field-error"});wrap.append(er);errors[c.key]=er;inputs[c.key]=input;body.append(wrap);});
    form.append(body,el("div",{class:"modal-foot"},[button("Cancelar",()=>{bg.remove();resolve(null);},{variant:"secondary"}),button("Salvar",()=>{const out={};let ok=true;campos.forEach(c=>{const v=inputs[c.key].value.trim();let err="";if(c.required&&!v)err="Preencha este campo.";if(!err&&c.validate&&!(c.skipValidationIfEmpty&&v==="")){const r=c.validate(v);if(r!==true)err=String(r||"Valor inválido.");}errors[c.key].textContent=err;if(err)ok=false;out[c.key]=v;});if(!ok){const first=body.querySelector(".field-error:not(:empty)");if(first)first.previousElementSibling?.focus();return;}bg.remove();resolve(out);})]));
    // O modal precisa ficar DENTRO de .modal-bg: é o overlay que escurece o fundo,
    // centraliza o formulário e sustenta o clique-fora. Sem isso os handlers de
    // fechar chamavam bg.remove() num elemento que nunca esteve no documento, e
    // cada formulário aberto ficava empilhado no fim do body — inclusive roubando
    // os cliques dos formulários seguintes.
    form.addEventListener("submit",e=>e.preventDefault());
    bg.append(form);
    bg.addEventListener("click",e=>{if(e.target===bg){bg.remove();resolve(null);}});document.body.append(bg);setTimeout(()=>body.querySelector("input,select,textarea")?.focus(),50);});}
  // Excel e Google Sheets executam como fórmula qualquer célula que comece com
  // = + - @ (ou tab/CR). Um cliente cadastrado como "=1+1" viraria conta, e a
  // planilha aberta por terceiros vira vetor de execução. Prefixar com aspa
  // simples neutraliza sem alterar o que a pessoa lê.
  function csvCelula(v){const s=String(v==null?"":v);const risco=/^[=+\-@\t\r]/.test(s);return `"${(risco?"'":"")+s.replace(/"/g,'""')}"`;}
  // BOM na frente para o Excel abrir UTF-8 corretamente.
  function csv(linhas){return "\uFEFF"+linhas.map(l=>l.map(csvCelula).join(";")).join("\r\n");}
  // União das chaves de todos os registros: usar só as do primeiro faz sumir
  // colunas quando um registro foi salvo com menos campos que os demais.
  function chavesDe(registros,ignorar=[]){const vistas=[];registros.forEach(r=>Object.keys(r).forEach(k=>{if(!vistas.includes(k)&&!ignorar.includes(k))vistas.push(k);}));return vistas;}
  function baixar(nome,texto,type="text/plain"){const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([texto],{type}));a.download=nome;document.body.append(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},1000);}
  function iconButton(iconName,label,action,variant="secondary"){return el("button",{class:`icon-btn ${variant}`,type:"button",title:label,"aria-label":label,onclick:action},icon(iconName,label));}
  App.ui={el,clear,money,fmtData,initials,icon,button,toast,confirmar,modalForm,baixar,iconButton,csv,csvCelula,chavesDe};
})();
