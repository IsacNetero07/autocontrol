# AutoControl — Blue Edition

Versão web/PWA redesenhada sobre a estrutura existente do AutoControl.

## Destaques

- Identidade visual azul/navy e ícones SVG.
- Dashboard operacional com KPIs, financeiro, alertas, agenda e Pátio Digital.
- Kanban de ordens com drag-and-drop.
- Detalhamento da OS com progresso, checklist, timeline e fotos/câmera.
- CRUD de clientes, veículos, OS, agenda, estoque, financeiro, fornecedores, usuários e checklists.
- Relatórios e indicadores com exportação CSV.
- Navegação inferior e safe-area para iPhone/iOS.
- PWA com manifest e service worker.
- Dados mantidos em `localStorage` na chave `autocontrol:v1`.
- `legacy-desktop/` preservado.

## Acesso de demonstração

- Usuário: `isac`
- Senha: `123456`

Troque a senha antes de usar em produção. Este projeto continua sendo um app local: o login não substitui autenticação de servidor.

## Validações realizadas

- Sintaxe de todos os JavaScripts com Node.js.
- Verificação de referências de arquivos do `index.html`.
- Manifesto e service worker verificados.
- Smoke test de login, dashboard, CRUD, Pátio, OS, mobile e paginação.
- Testes de dados corrompidos/malformados, validação de campos, proteção contra HTML inserido em registros, exclusão de registros vinculados, rota de OS inexistente e 250+ registros.
- Teste de todas as rotas principais sem `pageerror` no navegador automatizado.
