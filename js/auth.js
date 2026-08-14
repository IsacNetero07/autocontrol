window.App=window.App||{};
(function(){
 const SESSAO="autocontrol:sessao";
 function hashSenha(s){let h1=0xdeadbeef,h2=0x41c6ce57;s=String(s);for(let i=0;i<s.length;i++){const c=s.charCodeAt(i);h1=Math.imul(h1^c,2654435761);h2=Math.imul(h2^c,1597334677);}h1=Math.imul(h1^(h1>>>16),2246822507);h1^=Math.imul(h2^(h2>>>13),3266489909);h2=Math.imul(h2^(h2>>>16),2246822507);h2^=Math.imul(h1^(h1>>>13),3266489909);return(4294967296*(2097151&h2)+(h1>>>0)).toString(16);}
 function login(usuario,senha){const u=App.db.where("usuarios",x=>String(x.usuario).toLowerCase()===String(usuario).trim().toLowerCase())[0];if(!u||u.senha!==hashSenha(senha))return null;const s={id:u.id,nome:u.nome,usuario:u.usuario,nivel:u.nivel};try{localStorage.setItem(SESSAO,JSON.stringify(s));}catch(e){return null;}return s;}
 const logout=()=>localStorage.removeItem(SESSAO);const atual=()=>{try{return JSON.parse(localStorage.getItem(SESSAO))||null}catch(e){return null}};const ehAdmin=()=>atual()?.nivel==="admin";
 App.auth={hashSenha,login,logout,atual,ehAdmin};
})();
