from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QScrollArea
)

from database.estoque_db import (
    salvar_produto,
    listar_produtos
)

from styles.style import (
    botao_azul,
    estilo_titulo,
    tabela
)

from utils.validacao import (
    validar_obrigatorios,
    validar_numero_inteiro,
    validar_numero_decimal
)
from utils.exportar import exportar_tabela_csv
from database.sessao import nome_usuario_atual
from database.log_db import registrar_log
from views.components.paginacao import PaginacaoWidget


class TelaEstoque(QWidget):

    def __init__(self):
        super().__init__()

        self.dados_completos = []

        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        conteudo = QWidget()
        layout = QVBoxLayout(conteudo)

        titulo = QLabel("Controle de Estoque")
        titulo.setStyleSheet(estilo_titulo())

        layout.addWidget(titulo)

        formulario = QFormLayout()

        self.nome = QLineEdit()
        self.categoria = QLineEdit()
        self.quantidade = QLineEdit()
        self.valor = QLineEdit()
        self.fornecedor = QLineEdit()
        self.quantidade_minima = QLineEdit()
        self.quantidade_minima.setPlaceholderText("Ex: 5 (padrão se deixar vazio)")

        formulario.addRow("Produto:", self.nome)
        formulario.addRow("Categoria:", self.categoria)
        formulario.addRow("Quantidade:", self.quantidade)
        formulario.addRow("Qtd. mínima:", self.quantidade_minima)
        formulario.addRow("Valor:", self.valor)
        formulario.addRow("Fornecedor:", self.fornecedor)

        layout.addLayout(formulario)

        linha_botoes = QHBoxLayout()

        self.botao_salvar = QPushButton("Salvar Produto")
        self.botao_salvar.setStyleSheet(botao_azul())
        self.botao_exportar = QPushButton("📤 Exportar CSV")

        linha_botoes.addWidget(self.botao_salvar)
        linha_botoes.addWidget(self.botao_exportar)

        layout.addLayout(linha_botoes)

        self.tabela = QTableWidget()

        self.tabela.setColumnCount(7)

        self.tabela.setHorizontalHeaderLabels([
            "ID",
            "Produto",
            "Categoria",
            "Quantidade",
            "Valor",
            "Fornecedor",
            "Mín."
        ])

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabela.setStyleSheet(tabela())

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

        self.botao_salvar.clicked.connect(self.salvar)
        self.botao_exportar.clicked.connect(self.exportar_csv)

        self.carregar_produtos()

    def _renderizar_pagina_atual(self, _pagina=None):
        pagina_dados = self.paginacao.fatia_atual(self.dados_completos)

        self.tabela.setRowCount(len(pagina_dados))
        for linha, produto in enumerate(pagina_dados):
            for coluna, dado in enumerate(produto):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(dado))
                )

    def carregar_produtos(self, resetar_pagina=True):
        self.dados_completos = listar_produtos()
        self.paginacao.definir_total(len(self.dados_completos))

        if resetar_pagina:
            self.paginacao.resetar()

        self._renderizar_pagina_atual()

    def exportar_csv(self):
        tabela_completa = QTableWidget()
        tabela_completa.setColumnCount(7)
        tabela_completa.setHorizontalHeaderLabels([
            "ID", "Produto", "Categoria", "Quantidade", "Valor", "Fornecedor", "Mín."
        ])
        tabela_completa.setRowCount(len(self.dados_completos))

        for linha, produto in enumerate(self.dados_completos):
            for coluna, dado in enumerate(produto):
                tabela_completa.setItem(linha, coluna, QTableWidgetItem(str(dado)))

        exportar_tabela_csv(self, tabela_completa, nome_sugerido="estoque")

    def salvar(self):

        nome = self.nome.text().strip()
        categoria = self.categoria.text().strip()
        quantidade = self.quantidade.text().strip()
        valor = self.valor.text().strip()
        fornecedor = self.fornecedor.text().strip()
        quantidade_minima = self.quantidade_minima.text().strip() or "5"

        if not validar_obrigatorios(self, {
            "Produto": nome,
            "Categoria": categoria,
            "Quantidade": quantidade,
            "Valor": valor,
            "Fornecedor": fornecedor,
        }):
            return

        if not validar_numero_inteiro(self, "Quantidade", quantidade):
            return

        if not validar_numero_inteiro(self, "Quantidade mínima", quantidade_minima):
            return

        if not validar_numero_decimal(self, "Valor", valor):
            return

        salvar_produto(
            nome,
            categoria,
            quantidade,
            valor,
            fornecedor,
            quantidade_minima
        )

        registrar_log(
            nome_usuario_atual(),
            "Criar - Estoque",
            f"Produto {nome}"
        )

        QMessageBox.information(
            self,
            "Sucesso",
            "Produto cadastrado!"
        )

        self.nome.clear()
        self.categoria.clear()
        self.quantidade.clear()
        self.valor.clear()
        self.fornecedor.clear()
        self.quantidade_minima.clear()

        self.carregar_produtos(resetar_pagina=False)