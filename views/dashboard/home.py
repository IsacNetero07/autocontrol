from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout,
)
from database.dashboard_db import (
    total_clientes,
    total_veiculos,
    total_produtos,
    total_ordens_abertas,
    receita_mes,
    receita_por_mes,
    ordens_por_mes,
)
from views.components.card import Card
from views.components.grafico_matplotlib import GraficoBarras


class HomePage(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("homeArea")

        layout = QVBoxLayout()

        titulo = QLabel("Bem-vindo ao AutoControl!")
        titulo.setObjectName("homeTitulo")
        titulo.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)
        layout.addWidget(titulo)

        self.grid = QGridLayout()
        layout.addLayout(self.grid)

        # Gráficos compactos
        graficos_layout = QHBoxLayout()

        self.grafico_receita = GraficoBarras("Receita por mês", cor="#22C55E", compacto=True)
        self.grafico_ordens = GraficoBarras("OS por mês", cor="#3B82F6", compacto=True)

        graficos_layout.addWidget(self.grafico_receita)
        graficos_layout.addWidget(self.grafico_ordens)

        layout.addLayout(graficos_layout)

        layout.addStretch()

        self.setLayout(layout)

        self.atualizar_dados()

    def atualizar_dados(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.grid.addWidget(Card("Clientes", str(total_clientes()), "👤"), 0, 0)
        self.grid.addWidget(Card("Veículos", str(total_veiculos()), "🚗"), 0, 1)
        self.grid.addWidget(Card("OS Abertas", str(total_ordens_abertas()), "🔧"), 1, 0)
        self.grid.addWidget(Card("Produtos", str(total_produtos()), "📦"), 1, 1)
        self.grid.addWidget(
            Card("Receita do Mês", self.formatar_moeda(receita_mes()), "💰"),
            2, 0, 1, 2
        )

        # Atualiza os gráficos
        dados_receita = receita_por_mes(6)
        labels_r = [m for m, v in dados_receita]
        valores_r = [v for m, v in dados_receita]
        self.grafico_receita.atualizar(labels_r, valores_r)

        dados_ordens = ordens_por_mes(6)
        labels_o = [m for m, v in dados_ordens]
        valores_o = [v for m, v in dados_ordens]
        self.grafico_ordens.atualizar(labels_o, valores_o)

    def formatar_moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def showEvent(self, event):
        super().showEvent(event)
        self.atualizar_dados()