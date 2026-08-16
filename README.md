# AutoControl

PWA de gestão para oficinas mecânicas: clientes, veículos, ordens de serviço,
pátio digital, agenda, estoque, fornecedores, financeiro e relatórios.

Funciona no computador e no celular, instalável como aplicativo, e continua
operando offline. Todos os dados ficam no próprio dispositivo.

## Rodando localmente

O app precisa de uma origem HTTP real. Abrir o `index.html` direto pelo
sistema de arquivos (`file://`) desativa o service worker e a WebCrypto —
`localhost` já conta como contexto seguro.

```bash
npm install     # só para rodar os testes
npm start       # http://localhost:8000
```

Sem Node instalado, qualquer servidor estático serve:

```bash
python -m http.server 8000
```

### Primeiro acesso

Não existe usuário padrão. Na primeira vez, o app abre uma tela de **Primeiro
acesso** onde você cria o próprio administrador e escolhe se quer carregar
dados de demonstração para explorar o sistema.

## Testes

```bash
npm test              # suíte completa
npm run check         # sintaxe, referências do index.html, cache do SW
npm run test:core     # dados, seed, autenticação, validações
npm run test:hardening# storage corrompido, quota, regras de senha
npm run test:dom      # fluxo ponta a ponta em jsdom
```

A suíte de DOM carrega os mesmos arquivos que o `index.html`, na mesma ordem,
percorre as rotas principais e falha se qualquer uma escrever em
`console.error`.

## Estrutura

```
index.html              carrega os scripts na ordem
sw.js                   service worker (cache offline)
manifest.webmanifest    metadados do PWA
css/styles.css          estilos
js/
  db.js                 persistência em localStorage (coleções, CRUD, ids)
  auth.js               sessão e senhas
  seed.js               dados de exemplo e migrações de schema
  validation.js         CPF/CNPJ e formatação
  ui.js                 helpers de DOM, modais, toasts, ícones
  crud.js               telas de listagem/formulário genéricas
  entities.js           definição declarativa de cada cadastro
  views/                telas específicas (setup, login, dashboard, pátio, OS…)
  app.js                rotas, shell, relatórios, indicadores, configurações
tests/                  suíte em Node
legacy-desktop/         app desktop original em PyQt + SQLite (arquivado)
```

Os dados vivem no `localStorage`, na chave `autocontrol:v1`.

## Limites da versão local

Vale ser explícito sobre o que este estágio do projeto **não** é:

- **Os dados existem só neste navegador.** Limpar os dados do site, trocar de
  aparelho ou reinstalar o sistema apaga tudo. Use a exportação de backup em
  *Central de Operações* com regularidade.
- **O login não é uma fronteira de segurança.** Como tudo roda no navegador,
  qualquer pessoa com acesso ao aparelho pode alterar os dados pelo DevTools,
  inclusive o próprio perfil de acesso. As senhas são guardadas com
  PBKDF2-HMAC-SHA256 (210k iterações, salt por usuário), o que protege a senha
  em si — não o conteúdo.
- **Perfis e permissões são organizacionais, não impositivos.** Eles evitam
  erro de operação, não impedem acesso deliberado.
- **Não há sincronização.** Dois aparelhos são duas bases independentes.

Cada um desses limites cai quando existir um backend com banco real,
autenticação de servidor e validação por requisição.

## Próximos passos

O salto técnico que destrava o resto é sair do `localStorage` para uma API com
banco real, autenticação de servidor e sincronização entre dispositivos. Só
depois disso faz sentido falar em múltiplas oficinas, planos ou integrações.

## Histórico

Mudanças por versão em [CHANGELOG.md](CHANGELOG.md).

`legacy-desktop/` guarda a primeira versão do projeto, em Python/PyQt com
SQLite. Está arquivada para referência e não é mais executada.
