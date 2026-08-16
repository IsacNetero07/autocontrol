# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [2.7.0] — 2026-08-16

### Corrigido

- Exportação CSV perdia colunas. O cabeçalho vinha de `Object.keys(rows[0])`,
  então um registro salvo com menos campos — se caísse em primeiro — apagava
  aquelas colunas para todas as linhas. Agora usa a união das chaves.
- Células de CSV começando com `=`, `+`, `-` ou `@` eram gravadas cruas, e
  Excel e Google Sheets as executam como fórmula ao abrir o arquivo. Passam a
  ser prefixadas com aspa simples, sem alterar o texto exibido.
- Rollback de `update()` não cobria campos aninhados. O snapshot era uma cópia
  rasa, então uma falha de gravação deixava arrays e objetos internos (fotos,
  timeline, checklist) com a alteração aplicada em memória mesmo depois do
  "desfazer".

### Alterado

- `js/db.js` virou uma camada de dados de verdade: `all()`, `byId()` e
  `where()` devolvem cópias, e `insert()`/`update()` copiam o que recebem.
  Antes as consultas entregavam a referência viva do store — mexer no objeto
  retornado alterava a memória sem gravar no disco, e os dois divergiam em
  silêncio até o próximo reload. Agora o único caminho de escrita é `update()`.
  Isso também isola o `localStorage` num arquivo só: trocar por IndexedDB ou
  por uma API remota passa a significar reescrever apenas `js/db.js`.
- `App.ui` ganhou `csv()`, `csvCelula()` e `chavesDe()`, usados pelas duas
  telas que exportam, que antes duplicavam a montagem do arquivo.

## [2.6.0] — 2026-08-16

### Segurança

- Removido o usuário padrão `isac / 123456`, que estava no seed, no README e
  impresso na tela de login.
- Primeiro acesso agora abre uma tela de setup onde o dono da oficina cria o
  próprio administrador.
- Senhas passam a usar PBKDF2-HMAC-SHA256 com 210 mil iterações e salt de 16
  bytes por usuário. O hash anterior (mix de 64 bits, não criptográfico) segue
  validando instalações existentes e é migrado no primeiro login válido.
- Regras mínimas de senha: 8+ caracteres e não apenas números.
- Sem WebCrypto (`file://`), o app avisa no console em vez de rebaixar o hash
  em silêncio, e reporta o estado em *Central de Operações → Diagnóstico*.

### Corrigido

- Formulário de cadastro não fechava e roubava cliques. `modalForm` anexava ao
  body o `<form>` em vez do overlay `.modal-bg`, então o formulário ficava sem
  fundo escurecido nem centralização, os botões Fechar/Cancelar/Salvar chamavam
  `remove()` num elemento que nunca esteve no documento, e cada abertura
  empilhava outro formulário — os antigos continuavam clicáveis e podiam engolir
  o clique em Salvar sem gravar nada. Afetava todos os cadastros.
- Checklist de inspeção da OS não respondia ao clique. `render()` do detalhe da
  OS não limpava o container antes de redesenhar, então cada ação empilhava
  outra cópia inteira da tela abaixo da anterior — e a cópia antiga,
  desatualizada, continuava visível no topo. O clique salvava o estado, mas a
  tela parecia inerte. Afetava também os botões de progresso, o envio de fotos
  e a edição da OS.

### Adicionado

- `package.json` com scripts de teste e servidor de desenvolvimento.
- Suíte de testes de DOM em jsdom, cobrindo o fluxo de primeiro acesso, login e
  todas as rotas principais.
- Verificação automática de que `index.html` e `sw.js` listam os mesmos
  scripts, e de que nenhuma credencial de exemplo voltou para o código.
- Servidor estático próprio (`npm start`), sem depender de Python.
- `.gitattributes` normalizando fim de linha.

### Alterado

- Dados de demonstração deixam de ser automáticos e viram opt-in — no setup ou
  em *Configurações*. Uma oficina real não deve encontrar "João Silva" no
  cadastro dela.
- `App.auth.login` tornou-se assíncrono; o formulário genérico de CRUD aguarda
  `transform()`, de modo que usuários criados pela tela de Usuários também
  recebem PBKDF2.
- README único, descrevendo instalação, testes, estrutura e os limites reais da
  versão local. `README-2.1-BLUE.md` e `README-2.5.md` foram absorvidos aqui.
- `.gitignore` reescrito: cobre `node_modules/` e corrige caminhos que ainda
  apontavam para a estrutura anterior à mudança para `legacy-desktop/`.

### Removido

- 13 arquivos `.js` duplicados na raiz e um `styles.css` órfão. Nenhum era
  carregado pelo `index.html` nem constava no cache do service worker, e todos
  divergiam das versões ativas em `js/` — inclusive na chave de sessão e na
  função de hash, o que tornava fácil depurar o arquivo errado.

## [2.5.1] — 2026-08-14

- Central de Operações, backup/restauração em JSON, indicador online/offline,
  central de notificações e diagnóstico das coleções locais.

## [2.1.0] — Blue Edition

- Redesenho da PWA: identidade azul/navy, dashboard operacional, pátio digital
  em kanban com drag-and-drop, detalhamento de OS com checklist, timeline e
  fotos, relatórios com exportação CSV e navegação para iOS.

## [2.0.0]

- Reescrita do desktop (PyQt/SQLite) como PWA em HTML/CSS/JS, com os dados em
  `localStorage`. O app original foi arquivado em `legacy-desktop/`.
