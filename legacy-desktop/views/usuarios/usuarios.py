from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QHBoxLayout,
    QAbstractItemView,
    QComboBox,
    QScrollArea
)

from database.usuarios_db import (
    salvar_usuario,
    listar_usuarios,
    excluir_usuario
)

from utils.validacao import validar_obrigatorios
from views.components.dialogs_senha import DialogRedefinirSenha
from views.components.paginacao import PaginacaoWidget
from database.sessao import nome_usuario_atual
from database.log_db import registrar_log


class TelaUsuarios(QWidget):

    def __init__(self):
        super().__init__()

        self.id_usuario = None
        self.dados_completos = []

        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        conteudo = QWidget()
        layout = QVBoxLayout(conteudo)

        titulo = QLabel("Cadastro de Mecânicos e Usuários")
        titulo.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
        """)
        layout.addWidget(titulo)

        # ==========================
        # FORMULÁRIO
        # ==========================

        formulario = QFormLayout()

        self.nome = QLineEdit()
        self.usuario = QLineEdit()
        self.senha = QLineEdit()
        self.senha.setEchoMode(QLineEdit.Password)

        self.nivel = QComboBox()
        self.nivel.addItems(["mecanico", "admin", "provedor"])

        formulario.addRow("Nome:", self.nome)
        formulario.addRow("Usuário:", self.usuario)
        formulario.addRow("Senha:", self.senha)
        formulario.addRow("Nível:", self.nivel)

        layout.addLayout(formulario)

        # ==========================
        # BOTÕES
        # ==========================

        botoes = QHBoxLayout()

        self.botao_salvar = QPushButton("Cadastrar")
        self.botao_redefinir_senha = QPushButton("🔑 Redefinir senha")
        self.botao_excluir = QPushButton("Excluir")

        self.botao_salvar.setStyleSheet("""
            QPushButton{
                background:#2563EB;
                color:white;
                padding:10px;
                border-radius:8px;
            }
        """)

        self.botao_redefinir_senha.setStyleSheet("""
            QPushButton{
                background:#F59E0B;
                color:white;
                padding:10px;
                border-radius:8px;
            }
        """)

        self.botao_excluir.setStyleSheet("""
            QPushButton{
                background:#DC2626;
                color:white;
                padding:10px;
                border-radius:8px;
            }
        """)

        botoes.addWidget(self.botao_salvar)
        botoes.addWidget(self.botao_redefinir_senha)
        botoes.addWidget(self.botao_excluir)

        layout.addLayout(botoes)

        # ==========================
        # TABELA
        # ==========================

        self.tabela = QTableWidget()

        self.tabela.setColumnCount(4)

        self.tabela.setHorizontalHeaderLabels([
            "ID",
            "Nome",
            "Usuário",
            "Nível"
        ])

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabela.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabela.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.tabela.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabela.setMinimumHeight(200)
        self.tabela.setMaximumHeight(300)

        layout.addWidget(self.tabela)

        # ---- Paginação ----
        self.paginacao = PaginacaoWidget(tamanho_pagina=20)
        self.paginacao.pagina_alterada.connect(self._renderizar_pagina_atual)
        layout.addWidget(self.paginacao)

        conteudo.setLayout(layout)
        scroll.setWidget(conteudo)

        layout_externo.addWidget(scroll)

        # Conexões
        self.botao_salvar.clicked.connect(self.salvar)
        self.botao_redefinir_senha.clicked.connect(self.redefinir_senha)
        self.botao_excluir.clicked.connect(self.excluir)

        self.tabela.cellClicked.connect(
            self.selecionar_usuario
        )

        self.carregar_usuarios()

    # =========================================

    def _renderizar_pagina_atual(self, _pagina=None):
        pagina_dados = self.paginacao.fatia_atual(self.dados_completos)

        self.tabela.setRowCount(len(pagina_dados))
        for linha, usuario in enumerate(pagina_dados):
            for coluna, dado in enumerate(usuario):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(dado))
                )

    def carregar_usuarios(self, resetar_pagina=True):
        self.dados_completos = listar_usuarios()
        self.paginacao.definir_total(len(self.dados_completos))

        if resetar_pagina:
            self.paginacao.resetar()

        self._renderizar_pagina_atual()

    # =========================================

    def salvar(self):

        nome = self.nome.text().strip()
        usuario = self.usuario.text().strip()
        senha = self.senha.text().strip()
        nivel = self.nivel.currentText()

        if not validar_obrigatorios(self, {
            "Nome": nome,
            "Usuário": usuario,
            "Senha": senha,
        }):
            return

        try:
            salvar_usuario(
                nome,
                usuario,
                senha,
                nivel
            )
        except Exception as erro:
            QMessageBox.critical(
                self,
                "Erro ao cadastrar",
                f"Não foi possível cadastrar o usuário:\n{erro}"
            )
            return

        registrar_log(
            nome_usuario_atual(),
            "Criar - Usuários",
            f"Usuário '{usuario}' ({nivel})"
        )

        QMessageBox.information(
            self,
            "Sucesso",
            "Usuário cadastrado!"
        )

        self.limpar_campos()

        self.carregar_usuarios(resetar_pagina=False)

    # =========================================

    def selecionar_usuario(self, linha, coluna):

        item_id = self.tabela.item(linha, 0)
        if item_id is None:
            return

        self.id_usuario = int(item_id.text())

    # =========================================

    def redefinir_senha(self):

        if self.id_usuario is None:
            QMessageBox.warning(
                self,
                "Aviso",
                "Selecione um usuário na tabela."
            )
            return

        linha_atual = self.tabela.currentRow()
        nome_usuario = (
            self.tabela.item(linha_atual, 1).text()
            if linha_atual >= 0 else "usuário selecionado"
        )

        dialogo = DialogRedefinirSenha(self.id_usuario, nome_usuario, parent=self)
        dialogo.exec()

    # =========================================

    def excluir(self):

        if self.id_usuario is None:
            QMessageBox.warning(
                self,
                "Aviso",
                "Selecione um usuário na tabela."
            )
            return

        resposta = QMessageBox.question(
            self,
            "Excluir",
            "Deseja realmente excluir este usuário?"
        )

        if resposta == QMessageBox.Yes:

            id_excluido = self.id_usuario
            excluir_usuario(id_excluido)

            registrar_log(
                nome_usuario_atual(),
                "Excluir - Usuários",
                f"ID {id_excluido}"
            )

            QMessageBox.information(
                self,
                "Sucesso",
                "Usuário excluído!"
            )

            self.limpar_campos()
            self.carregar_usuarios(resetar_pagina=False)

    # =========================================

    def limpar_campos(self):

        self.nome.clear()
        self.usuario.clear()
        self.senha.clear()
        self.nivel.setCurrentIndex(0)

        self.id_usuario = None