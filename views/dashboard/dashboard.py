import sys
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QMessageBox,
    QApplication,
    QFileDialog,
)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QShortcut, QKeySequence

from views.components.sidebar import SideBar
from views.components.topbar import TopBar
from views.components.dialogs_senha import DialogTrocarSenha
from views.financeiro.financeiro import TelaFinanceiro
from views.relatorios.relatorios import TelaRelatorios

from views.dashboard.home import HomePage
from views.clientes.clientes import TelaClientes
from views.veiculos.veiculos import TelaVeiculos
from views.ordem_servico.ordem_servico import TelaOrdemServico
from views.agenda.agenda import TelaAgenda
from views.estoque.estoque import TelaEstoque
from views.fornecedores.fornecedores import TelaFornecedores
from views.usuarios.usuarios import TelaUsuarios
from views.log_auditoria.log_auditoria import TelaLogAuditoria

from database.dashboard_db import pesquisa_global
from database.backup_db import fazer_backup, restaurar_backup
from database.database import DB_PATH
from database.estoque_db import listar_estoque_baixo
from database.ordem_servico_db import listar_ordens_proximas
from database.sessao import nome_usuario_atual
from database.log_db import registrar_log
from styles.style import tema_claro, tema_escuro


class Dashboard(QMainWindow):

    def __init__(self, nivel="admin", id_usuario=None, nome_usuario="Usuário"):
        super().__init__()

        self.setWindowTitle("AutoControl")
        self.resize(1300, 750)

        self.modo_escuro = False
        self.nivel = nivel
        self.id_usuario = id_usuario
        self.nome_usuario = nome_usuario

        central = QWidget()
        self.setCentralWidget(central)

        layout_principal = QHBoxLayout()
        central.setLayout(layout_principal)

        # Sidebar
        self.sidebar = SideBar()
        layout_principal.addWidget(self.sidebar)

        # Área da direita
        area_direita = QVBoxLayout()
        layout_principal.addLayout(area_direita)

        # TopBar
        self.topbar = TopBar(nome_usuario=self.nome_usuario)
        area_direita.addWidget(self.topbar)

        # Área das telas
        self.paginas = QStackedWidget()

        # Páginas
        self.home = HomePage()
        self.clientes = TelaClientes()
        self.veiculos = TelaVeiculos()
        self.ordem_servico = TelaOrdemServico()
        self.agenda = TelaAgenda()
        self.estoque = TelaEstoque()
        self.fornecedores = TelaFornecedores()
        self.financeiro = TelaFinanceiro()
        self.relatorios = TelaRelatorios()
        self.usuarios = TelaUsuarios()
        self.log_auditoria = TelaLogAuditoria()

        self.paginas.addWidget(self.home)
        self.paginas.addWidget(self.clientes)
        self.paginas.addWidget(self.veiculos)
        self.paginas.addWidget(self.ordem_servico)
        self.paginas.addWidget(self.agenda)
        self.paginas.addWidget(self.estoque)
        self.paginas.addWidget(self.fornecedores)
        self.paginas.addWidget(self.financeiro)
        self.paginas.addWidget(self.relatorios)
        self.paginas.addWidget(self.usuarios)
        self.paginas.addWidget(self.log_auditoria)

        # Tela inicial
        self.paginas.setCurrentWidget(self.home)

        area_direita.addWidget(self.paginas)

        # Conectar botões
        self.sidebar.btn_dashboard.clicked.connect(self.abrir_dashboard)
        self.sidebar.btn_clientes.clicked.connect(self.abrir_clientes)
        self.sidebar.btn_veiculos.clicked.connect(self.abrir_veiculos)
        self.sidebar.btn_ordem_servico.clicked.connect(self.abrir_ordem_servico)
        self.sidebar.btn_agenda.clicked.connect(self.abrir_agenda)
        self.sidebar.btn_estoque.clicked.connect(self.abrir_estoque)
        self.sidebar.btn_fornecedores.clicked.connect(self.abrir_fornecedores)
        self.sidebar.btn_financeiro.clicked.connect(self.abrir_financeiro)
        self.sidebar.btn_relatorios.clicked.connect(self.abrir_relatorios)
        self.sidebar.btn_usuarios.clicked.connect(self.abrir_usuarios)
        self.sidebar.btn_log_auditoria.clicked.connect(self.abrir_log_auditoria)

        # Conectar busca global
        self.topbar.pesquisar.connect(self.executar_pesquisa)

        # Conectar alternância de tema
        self.topbar.alternar_tema.connect(self.alternar_tema)

        # Conectar backup/restauração
        self.topbar.fazer_backup.connect(self.executar_backup)
        self.topbar.restaurar_backup.connect(self.executar_restauracao)

        # Conectar notificações
        self.topbar.abrir_notificacoes.connect(self.mostrar_notificacoes)

        # Conectar troca de senha do usuário logado
        self.topbar.trocar_senha.connect(self.abrir_trocar_senha)

        # Conectar fluxo de atendimento: Cliente -> Veículo
        self.clientes.cliente_cadastrado.connect(
            self.perguntar_cadastrar_veiculo
        )

        # Conectar fluxo de atendimento: Veículo -> Ordem de Serviço
        self.veiculos.veiculo_cadastrado.connect(
            self.perguntar_criar_ordem_servico
        )

        # Aplicar permissões de acordo com o nível do usuário
        self.aplicar_permissoes()

        # Notificações: calcula na abertura e a cada 60s
        self._estoque_baixo_atual = []
        self._ordens_proximas_atual = []
        self.atualizar_notificacoes()

        self.timer_notificacoes = QTimer(self)
        self.timer_notificacoes.timeout.connect(self.atualizar_notificacoes)
        self.timer_notificacoes.start(60000)

        # Atalhos de teclado para navegação
        self._configurar_atalhos_navegacao()

    def aplicar_permissoes(self):
        permissoes = {
            "admin": [
                "btn_dashboard", "btn_clientes", "btn_veiculos",
                "btn_ordem_servico", "btn_agenda", "btn_estoque",
                "btn_fornecedores", "btn_financeiro", "btn_relatorios",
                "btn_usuarios", "btn_log_auditoria"
            ],
            "mecanico": [
                "btn_dashboard", "btn_clientes",
                "btn_veiculos", "btn_ordem_servico", "btn_agenda"
            ],
            "provedor": [
                "btn_dashboard", "btn_estoque", "btn_fornecedores"
            ],
        }

        self._permitidos = permissoes.get(self.nivel, permissoes["mecanico"])

        todos_botoes = [
            "btn_dashboard", "btn_clientes", "btn_veiculos",
            "btn_ordem_servico", "btn_agenda", "btn_estoque",
            "btn_fornecedores", "btn_financeiro", "btn_relatorios",
            "btn_usuarios", "btn_log_auditoria"
        ]

        for nome_botao in todos_botoes:
            botao = getattr(self.sidebar, nome_botao)
            botao.setVisible(nome_botao in self._permitidos)

        pagina_atual = self.paginas.currentWidget()
        mapa_paginas = {
            "btn_clientes": self.clientes,
            "btn_veiculos": self.veiculos,
            "btn_ordem_servico": self.ordem_servico,
            "btn_agenda": self.agenda,
            "btn_estoque": self.estoque,
            "btn_fornecedores": self.fornecedores,
            "btn_financeiro": self.financeiro,
            "btn_relatorios": self.relatorios,
            "btn_usuarios": self.usuarios,
            "btn_log_auditoria": self.log_auditoria,
        }
        for nome_botao, pagina in mapa_paginas.items():
            if pagina_atual is pagina and nome_botao not in self._permitidos:
                self.paginas.setCurrentWidget(self.home)
                break

    # ---------- Atalhos de teclado ----------

    def _configurar_atalhos_navegacao(self):
        # Cada entrada: tecla -> (nome_do_botao_na_sidebar, função_que_abre_a_tela)
        mapa_teclas = {
            "Ctrl+1": ("btn_dashboard", self.abrir_dashboard),
            "Ctrl+2": ("btn_clientes", self.abrir_clientes),
            "Ctrl+3": ("btn_veiculos", self.abrir_veiculos),
            "Ctrl+4": ("btn_ordem_servico", self.abrir_ordem_servico),
            "Ctrl+5": ("btn_agenda", self.abrir_agenda),
            "Ctrl+6": ("btn_estoque", self.abrir_estoque),
            "Ctrl+7": ("btn_fornecedores", self.abrir_fornecedores),
            "Ctrl+8": ("btn_financeiro", self.abrir_financeiro),
            "Ctrl+9": ("btn_relatorios", self.abrir_relatorios),
        }

        self._atalhos_navegacao = []  # mantém referência viva (evita coleta de lixo)

        for tecla, (nome_botao, acao) in mapa_teclas.items():
            atalho = QShortcut(QKeySequence(tecla), self)
            atalho.activated.connect(
                lambda nome=nome_botao, funcao=acao: self._navegar_com_permissao(nome, funcao)
            )
            self._atalhos_navegacao.append(atalho)

    def _navegar_com_permissao(self, nome_botao, funcao_abrir):
        if nome_botao in self._permitidos:
            funcao_abrir()

    def abrir_dashboard(self):
        self.paginas.setCurrentWidget(self.home)

    def abrir_clientes(self):
        self.paginas.setCurrentWidget(self.clientes)

    def abrir_veiculos(self):
        self.paginas.setCurrentWidget(self.veiculos)

    def abrir_ordem_servico(self):
        self.paginas.setCurrentWidget(self.ordem_servico)
        self.atualizar_notificacoes()

    def abrir_agenda(self):
        self.paginas.setCurrentWidget(self.agenda)

    def abrir_estoque(self):
        self.paginas.setCurrentWidget(self.estoque)
        self.atualizar_notificacoes()

    def abrir_fornecedores(self):
        self.paginas.setCurrentWidget(self.fornecedores)

    def abrir_financeiro(self):
        self.paginas.setCurrentWidget(self.financeiro)

    def abrir_relatorios(self):
        self.paginas.setCurrentWidget(self.relatorios)

    def abrir_usuarios(self):
        self.paginas.setCurrentWidget(self.usuarios)

    def abrir_log_auditoria(self):
        self.paginas.setCurrentWidget(self.log_auditoria)

    def perguntar_cadastrar_veiculo(self, id_cliente):
        resposta = QMessageBox.question(
            self,
            "Cliente cadastrado",
            "Cliente salvo com sucesso!\n\nDeseja cadastrar um veículo para esse cliente agora?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if resposta == QMessageBox.Yes:
            self.veiculos.selecionar_cliente(id_cliente)
            self.paginas.setCurrentWidget(self.veiculos)

    def perguntar_criar_ordem_servico(self, id_veiculo):
        resposta = QMessageBox.question(
            self,
            "Veículo cadastrado",
            "Veículo salvo com sucesso!\n\nDeseja abrir uma Ordem de Serviço para esse veículo agora?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if resposta == QMessageBox.Yes:
            self.ordem_servico.selecionar_veiculo(id_veiculo)
            self.paginas.setCurrentWidget(self.ordem_servico)

    def executar_pesquisa(self, termo):
        resultados = pesquisa_global(termo)

        texto = ""

        if resultados["clientes"]:
            texto += "👤 Clientes:\n"
            for c in resultados["clientes"]:
                texto += f"  • {c[1]}\n"
            texto += "\n"

        if resultados["veiculos"]:
            texto += "🚗 Veículos:\n"
            for v in resultados["veiculos"]:
                texto += f"  • {v[1]} - {v[2]} {v[3]}\n"
            texto += "\n"

        if resultados["ordens"]:
            texto += "🔧 Ordens de Serviço:\n"
            for o in resultados["ordens"]:
                texto += f"  • OS #{o[0]} - {o[1]} - {o[2]} ({o[3]})\n"
            texto += "\n"

        if resultados["produtos"]:
            texto += "📦 Produtos:\n"
            for p in resultados["produtos"]:
                texto += f"  • {p[1]} (qtd: {p[2]})\n"

        if texto == "":
            texto = "Nenhum resultado encontrado."

        QMessageBox.information(self, f"Resultados para '{termo}'", texto)

    def alternar_tema(self):
        self.modo_escuro = not self.modo_escuro

        app = QApplication.instance()

        if self.modo_escuro:
            app.setStyleSheet(tema_escuro())
            self.topbar.botao_tema.setText("☀️")
        else:
            app.setStyleSheet(tema_claro())
            self.topbar.botao_tema.setText("🌙")

        self.home.grafico_receita.aplicar_tema(self.modo_escuro)
        self.home.grafico_ordens.aplicar_tema(self.modo_escuro)

    def executar_backup(self):
        try:
            caminho = fazer_backup()

            registrar_log(
                nome_usuario_atual(),
                "Backup",
                f"Backup criado em {caminho}"
            )

            QMessageBox.information(
                self,
                "Backup concluído",
                f"Backup salvo com sucesso em:\n{caminho}"
            )
        except Exception as erro:
            QMessageBox.critical(
                self,
                "Erro ao fazer backup",
                f"Não foi possível criar o backup:\n{erro}"
            )

    def executar_restauracao(self):
        pasta_backups = DB_PATH.parent / "backups"

        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecione o backup para restaurar",
            str(pasta_backups),
            "Banco de dados (*.db)"
        )

        if not arquivo:
            return

        resposta = QMessageBox.warning(
            self,
            "Confirmar restauração",
            "Isso vai substituir todos os dados atuais pelos dados do backup selecionado.\n\n"
            "Um backup de segurança do estado atual será criado automaticamente antes.\n\n"
            "Deseja continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if resposta != QMessageBox.Yes:
            return

        try:
            restaurar_backup(arquivo)

            registrar_log(
                nome_usuario_atual(),
                "Restauração de backup",
                f"Restaurou a partir de {arquivo}"
            )

            QMessageBox.information(
                self,
                "Restauração concluída",
                "Backup restaurado com sucesso!\n\nReinicie o programa para ver os dados atualizados."
            )
        except Exception as erro:
            QMessageBox.critical(
                self,
                "Erro ao restaurar",
                f"Não foi possível restaurar o backup:\n{erro}"
            )

    def abrir_trocar_senha(self):
        if self.id_usuario is None:
            QMessageBox.warning(
                self,
                "Indisponível",
                "Não foi possível identificar o usuário logado."
            )
            return

        dialogo = DialogTrocarSenha(self.id_usuario, parent=self)
        dialogo.exec()

    # ---------- Notificações ----------

    def atualizar_notificacoes(self):
        self._estoque_baixo_atual = listar_estoque_baixo()
        self._ordens_proximas_atual = listar_ordens_proximas(dias=1)

        total = len(self._estoque_baixo_atual) + len(self._ordens_proximas_atual)
        self.topbar.atualizar_notificacoes(total)

    def mostrar_notificacoes(self):
        texto = ""

        if self._estoque_baixo_atual:
            texto += "📦 Estoque baixo:\n"
            for _id, nome, quantidade, minimo in self._estoque_baixo_atual:
                texto += f"  • {nome}: {quantidade} (mínimo: {minimo})\n"
            texto += "\n"

        if self._ordens_proximas_atual:
            texto += "🔧 Ordens de Serviço agendadas (hoje/amanhã):\n"
            for os_id, cliente, placa, status, valor, data in self._ordens_proximas_atual:
                texto += f"  • OS #{os_id} - {cliente} ({placa}) - {data} - {status}\n"

        if texto == "":
            texto = "Nenhum alerta no momento. Tudo em ordem! ✅"

        QMessageBox.information(self, "Notificações", texto)