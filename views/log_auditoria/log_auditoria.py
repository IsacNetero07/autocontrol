from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)

from database.log_db import listar_logs
from styles.style import estilo_titulo, tabela
from utils.exportar import exportar_tabela_csv
from views.components.paginacao import PaginacaoWidget


class TelaLogAuditoria(QWidget):

    def __init__(self):
        super().__init__()

        self.dados_completos = []

        layout = QVBoxLayout(self)

        cabecalho = QHBoxLayout()

        titulo = QLabel("Log de Auditoria")
        titulo.setStyleSheet(estilo_titulo())
        cabecalho.addWidget(titulo)

        cabecalho.addStretch()

        self.botao_atualizar = QPushButton("🔄 Atualizar")
        self.botao_exportar = QPushButton("📤 Exportar CSV")
        cabecalho.addWidget(self.botao_atualizar)
        cabecalho.addWidget(self.botao_exportar)

        layout.addLayout(cabecalho)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Usuário", "Ação", "Detalhes", "Data/Hora"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setStyleSheet(tabela())
        layout.addWidget(self.tabela)

        # ---- Paginação ----
        self.paginacao = PaginacaoWidget(tamanho_pagina=20)
        self.paginacao.pagina_alterada.connect(self._renderizar_pagina_atual)
        layout.addWidget(self.paginacao)

        self.botao_atualizar.clicked.connect(self.carregar_logs)
        self.botao_exportar.clicked.connect(self.exportar_csv)

        self.carregar_logs()

    def _renderizar_pagina_atual(self, _pagina=None):
        pagina_dados = self.paginacao.fatia_atual(self.dados_completos)

        self.tabela.setRowCount(len(pagina_dados))
        for linha, registro in enumerate(pagina_dados):
            for coluna, valor in enumerate(registro):
                self.tabela.setItem(linha, coluna, QTableWidgetItem(str(valor)))

    def carregar_logs(self, resetar_pagina=True):
        self.dados_completos = listar_logs()
        self.paginacao.definir_total(len(self.dados_completos))

        if resetar_pagina:
            self.paginacao.resetar()

        self._renderizar_pagina_atual()

    def exportar_csv(self):
        tabela_completa = QTableWidget()
        tabela_completa.setColumnCount(5)
        tabela_completa.setHorizontalHeaderLabels([
            "ID", "Usuário", "Ação", "Detalhes", "Data/Hora"
        ])
        tabela_completa.setRowCount(len(self.dados_completos))

        for linha, registro in enumerate(self.dados_completos):
            for coluna, valor in enumerate(registro):
                tabela_completa.setItem(linha, coluna, QTableWidgetItem(str(valor)))

        exportar_tabela_csv(self, tabela_completa, nome_sugerido="log_auditoria")

    def showEvent(self, event):
        super().showEvent(event)
        self.carregar_logs(resetar_pagina=False)