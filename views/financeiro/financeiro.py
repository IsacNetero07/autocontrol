from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QAbstractItemView,
    QScrollArea,
)
from PySide6.QtCore import QDate

from database.financeiro_db import (
    salvar_movimento,
    listar_movimentos,
    total_receitas,
    total_despesas,
    total_lucro,
)

from views.components.card import Card
from styles.style import botao_azul, estilo_titulo, tabela
from utils.exportar import exportar_tabela_csv


class TelaFinanceiro(QWidget):

    def __init__(self):
        super().__init__()

        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        conteudo = QWidget()
        layout = QVBoxLayout(conteudo)

        lbl_titulo = QLabel("Financeiro")
        lbl_titulo.setStyleSheet(estilo_titulo())
        layout.addWidget(lbl_titulo)

        # Cards de resumo
        self.linha_cards = QHBoxLayout()
        layout.addLayout(self.linha_cards)

        # Formulário
        formulario = QFormLayout()

        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Ex: Pagamento OS #12")
        self.descricao.setMinimumHeight(35)

        self.tipo = QComboBox()
        self.tipo.addItems(["Receita", "Despesa"])
        self.tipo.setMinimumHeight(35)

        self.valor = QLineEdit()
        self.valor.setPlaceholderText("Ex: 350.00")
        self.valor.setMinimumHeight(35)

        formulario.addRow("Descrição:", self.descricao)
        formulario.addRow("Tipo:", self.tipo)
        formulario.addRow("Valor (R$):", self.valor)

        layout.addLayout(formulario)

        linha_botoes = QHBoxLayout()

        self.botao_salvar = QPushButton("💾 Salvar Movimentação")
        self.botao_salvar.setStyleSheet(botao_azul())

        self.botao_exportar = QPushButton("📤 Exportar CSV")
        self.botao_exportar.setStyleSheet("""
            QPushButton {
                background:#059669;
                color:white;
                border:none;
                border-radius:10px;
                padding:10px;
                font-size:14px;
                font-weight:bold;
            }
            QPushButton:hover {
                background:#047857;
            }
        """)

        linha_botoes.addWidget(self.botao_salvar)
        linha_botoes.addWidget(self.botao_exportar)

        layout.addLayout(linha_botoes)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setStyleSheet(tabela())

        self.tabela.setAlternatingRowColors(True)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)

        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels([
            "ID",
            "Descrição",
            "Tipo",
            "Valor",
            "Data",
        ])

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabela.setMinimumHeight(200)
        self.tabela.setMaximumHeight(300)

        layout.addWidget(self.tabela)

        conteudo.setLayout(layout)
        scroll.setWidget(conteudo)

        layout_externo.addWidget(scroll)

        self.botao_salvar.clicked.connect(self.salvar)
        self.botao_exportar.clicked.connect(self.exportar_csv)

        self.atualizar_cards()
        self.carregar_movimentos()

    def atualizar_cards(self):
        while self.linha_cards.count():
            item = self.linha_cards.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        receitas = total_receitas()
        despesas = total_despesas()
        lucro = total_lucro()

        self.linha_cards.addWidget(
            Card("Receitas", f"R$ {receitas:,.2f}", "💰")
        )
        self.linha_cards.addWidget(
            Card("Despesas", f"R$ {despesas:,.2f}", "📉")
        )
        self.linha_cards.addWidget(
            Card("Lucro", f"R$ {lucro:,.2f}", "💵")
        )

    def carregar_movimentos(self):
        dados = listar_movimentos()

        self.tabela.setRowCount(len(dados))

        for linha, movimento in enumerate(dados):
            for coluna, dado in enumerate(movimento):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(dado))
                )

    def exportar_csv(self):
        exportar_tabela_csv(
            self,
            ["ID", "Descrição", "Tipo", "Valor", "Data"],
            listar_movimentos(),
            "financeiro.csv"
        )

    def salvar(self):
        descricao = self.descricao.text().strip()
        tipo = self.tipo.currentText()
        valor_texto = self.valor.text().strip().replace(",", ".")

        if descricao == "":
            QMessageBox.warning(self, "Erro", "Informe a descrição.")
            return

        if valor_texto == "":
            QMessageBox.warning(self, "Erro", "Informe o valor.")
            return

        try:
            valor = float(valor_texto)
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valor inválido.")
            return

        if valor <= 0:
            QMessageBox.warning(self, "Erro", "O valor deve ser maior que zero.")
            return

        data = QDate.currentDate().toString("dd/MM/yyyy")

        salvar_movimento(descricao, tipo, valor, data)

        QMessageBox.information(self, "Sucesso", "Movimentação registrada!")

        self.descricao.clear()
        self.tipo.setCurrentIndex(0)
        self.valor.clear()
        self.descricao.setFocus()

        self.atualizar_cards()
        self.carregar_movimentos()

    def showEvent(self, event):
        super().showEvent(event)
        self.atualizar_cards()
        self.carregar_movimentos()