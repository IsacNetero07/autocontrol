# AutoControl

Sistema de gestão para oficina mecânica, agora como **PWA** (aplicativo web instalável).
Funciona no celular, offline, e é hospedado direto pelo GitHub Pages. Não precisa de
servidor, banco de dados externo, nem instalar nada.

> Feito com HTML, CSS e JavaScript puro. Sem build, sem npm, sem framework.

## Acesso

- **Usuário:** `isac`
- **Senha:** `123456`

Na primeira vez, o app cria esse administrador e alguns dados de exemplo.

## Como testar no celular

1. Ative o GitHub Pages (passo abaixo).
2. Abra o endereço no navegador do celular:
   `https://isacnetero07.github.io/autocontrol/`
3. No Android (Chrome): toque em **Instalar** no topo, ou no menu do navegador use
   **Adicionar à tela inicial**.
4. No iPhone (Safari): botão **Compartilhar** → **Adicionar à Tela de Início**.

Depois de instalado, ele abre como um app normal e funciona sem internet.

## Ativar o GitHub Pages

No GitHub do repositório:

1. **Settings** → **Pages**.
2. Em **Build and deployment**, escolha **Deploy from a branch**.
3. Branch: **main**, pasta: **/ (root)**. Salve.
4. Aguarde ~1 minuto. O endereço aparece na mesma página.

## Onde ficam os dados

Tudo é salvo no próprio aparelho, no `localStorage` do navegador. Cada celular tem os
próprios dados. Não há servidor central. O botão **Zerar dados** (canto inferior do menu)
apaga tudo e recria os dados de exemplo.

Como o app é 100% local, o login é um controle de acesso simples, não uma barreira de
segurança de servidor.

## Módulos

- **Painel** com os números do negócio e listas rápidas.
- **Clientes**, **Veículos**, **Fornecedores** (cadastro, busca, edição).
- **Ordens de Serviço** ligadas a cliente e veículo, com status e valor.
- **Agenda** de agendamentos.
- **Estoque** com alerta de estoque baixo.
- **Financeiro** com receitas, despesas e saldo.
- **Usuários** e **Log de Auditoria** (apenas administrador).
- Validação de **CPF** e **CNPJ**, e **exportar CSV** em cada lista.

## Estrutura

```
index.html              página principal (carrega os scripts)
manifest.webmanifest    dados do PWA (nome, ícones, cores)
sw.js                   service worker (funciona offline)
css/styles.css          tema escuro, responsivo
icons/                  ícones do app
js/
  validation.js         CPF/CNPJ e formatação
  db.js                 dados no localStorage
  auth.js               login e sessão
  seed.js               usuário padrão + dados de exemplo
  ui.js                 componentes (modal, toast, tabela)
  crud.js               motor genérico de cadastro
  entities.js           configuração de cada módulo
  views/login.js        tela de login
  views/dashboard.js    painel inicial
  app.js                layout, navegação e registro do service worker
legacy-desktop/         versão original em Python/PySide6 (preservada)
```

## Rodar localmente (opcional)

Não é obrigatório. Se quiser testar no computador, sirva a pasta por HTTP
(o service worker não funciona abrindo o arquivo direto):

```
python3 -m http.server 8000
```

Depois abra `http://localhost:8000/`.
