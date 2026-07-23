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
    QAbstractItemView
)

from database.fornecedores_db import (
    salvar_fornecedor,
    listar_fornecedores,
    pesquisar_fornecedores,
    atualizar_fornecedor,
    excluir_fornecedor
)


class TelaFornecedores(QWidget):

    def __init__(self):
        super().__init__()

        self.id_fornecedor = None

        layout = QVBoxLayout()

        titulo = QLabel("Cadastro de Fornecedores")
        titulo.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
        """)
        layout.addWidget(titulo)

        # ==========================
        # PESQUISA
        # ==========================

        pesquisa_layout = QHBoxLayout()

        self.pesquisa = QLineEdit()
        self.pesquisa.setPlaceholderText("Pesquisar fornecedor...")

        self.botao_pesquisar = QPushButton("Pesquisar")

        pesquisa_layout.addWidget(self.pesquisa)
        pesquisa_layout.addWidget(self.botao_pesquisar)

        layout.addLayout(pesquisa_layout)

        # ==========================
        # FORMULÁRIO
        # ==========================

        formulario = QFormLayout()

        self.nome = QLineEdit()
        self.cnpj = QLineEdit()
        self.telefone = QLineEdit()
        self.email = QLineEdit()
        self.endereco = QLineEdit()

        formulario.addRow("Nome:", self.nome)
        formulario.addRow("CNPJ:", self.cnpj)
        formulario.addRow("Telefone:", self.telefone)
        formulario.addRow("Email:", self.email)
        formulario.addRow("Endereço:", self.endereco)

        layout.addLayout(formulario)

        # ==========================
        # BOTÕES
        # ==========================

        botoes = QHBoxLayout()

        self.botao_salvar = QPushButton("Salvar")
        self.botao_editar = QPushButton("Editar")
        self.botao_excluir = QPushButton("Excluir")

        self.botao_salvar.setStyleSheet("""
            QPushButton{
                background:#2563EB;
                color:white;
                padding:10px;
                border-radius:8px;
            }
        """)

        self.botao_editar.setStyleSheet("""
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
        botoes.addWidget(self.botao_editar)
        botoes.addWidget(self.botao_excluir)

        layout.addLayout(botoes)

        # ==========================
        # TABELA
        # ==========================

        self.tabela = QTableWidget()

        self.tabela.setColumnCount(5)

        self.tabela.setHorizontalHeaderLabels([
            "ID",
            "Nome",
            "CNPJ",
            "Telefone",
            "Email"
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

        layout.addWidget(self.tabela)

        self.setLayout(layout)

        # Conexões
        self.botao_salvar.clicked.connect(self.salvar)
        self.botao_pesquisar.clicked.connect(self.pesquisar)
        self.botao_editar.clicked.connect(self.editar)
        self.botao_excluir.clicked.connect(self.excluir)

        self.tabela.cellClicked.connect(
            self.selecionar_fornecedor
        )

        self.carregar_fornecedores()

    # =========================================

    def carregar_fornecedores(self):

        fornecedores = listar_fornecedores()

        self.tabela.setRowCount(len(fornecedores))

        for linha, fornecedor in enumerate(fornecedores):

            for coluna, dado in enumerate(fornecedor):

                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(dado))
                )

    # =========================================

    def salvar(self):

        nome = self.nome.text().strip()
        cnpj = self.cnpj.text().strip()
        telefone = self.telefone.text().strip()
        email = self.email.text().strip()
        endereco = self.endereco.text().strip()

        if nome == "":
            QMessageBox.warning(
                self,
                "Erro",
                "Informe o nome."
            )
            return

        salvar_fornecedor(
            nome,
            cnpj,
            telefone,
            email,
            endereco
        )

        QMessageBox.information(
            self,
            "Sucesso",
            "Fornecedor salvo!"
        )

        self.limpar_campos()

        self.carregar_fornecedores()

    # =========================================

    def pesquisar(self):

        texto = self.pesquisa.text().strip()

        if texto == "":
            self.carregar_fornecedores()
            return

        fornecedores = pesquisar_fornecedores(texto)

        self.tabela.setRowCount(len(fornecedores))

        for linha, fornecedor in enumerate(fornecedores):

            for coluna, dado in enumerate(fornecedor):

                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(dado))
                )

    # =========================================

    def selecionar_fornecedor(self, linha, coluna):

        self.id_fornecedor = int(
            self.tabela.item(linha, 0).text()
        )

        self.nome.setText(
            self.tabela.item(linha, 1).text()
        )

        self.cnpj.setText(
            self.tabela.item(linha, 2).text()
        )

        self.telefone.setText(
            self.tabela.item(linha, 3).text()
        )

        self.email.setText(
            self.tabela.item(linha, 4).text()
        )

    # =========================================

    def editar(self):

        if self.id_fornecedor is None:
            QMessageBox.warning(
                self,
                "Aviso",
                "Selecione um fornecedor."
            )
            return

        atualizar_fornecedor(
            self.id_fornecedor,
            self.nome.text(),
            self.cnpj.text(),
            self.telefone.text(),
            self.email.text(),
            self.endereco.text()
        )

        QMessageBox.information(
            self,
            "Sucesso",
            "Fornecedor atualizado!"
        )

        self.limpar_campos()
        self.carregar_fornecedores()

    # =========================================

    def excluir(self):

        if self.id_fornecedor is None:
            QMessageBox.warning(
                self,
                "Aviso",
                "Selecione um fornecedor."
            )
            return

        resposta = QMessageBox.question(
            self,
            "Excluir",
            "Deseja realmente excluir este fornecedor?"
        )

        if resposta == QMessageBox.Yes:

            excluir_fornecedor(self.id_fornecedor)

            QMessageBox.information(
                self,
                "Sucesso",
                "Fornecedor excluído!"
            )

            self.limpar_campos()
            self.carregar_fornecedores()

    # =========================================

    def limpar_campos(self):

        self.nome.clear()
        self.cnpj.clear()
        self.telefone.clear()
        self.email.clear()
        self.endereco.clear()

        self.id_fornecedor = None