"""
views/widgets/estoque_baixo_widget.py

Card de alerta pra colocar na tela de Dashboard.
Uso (dentro do dashboard.py):

    from views.widgets.estoque_baixo_widget import EstoqueBaixoWidget
    ...
    layout.addWidget(EstoqueBaixoWidget())
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QFrame,
)

from database.dashboard_db import estoque_baixo


class EstoqueBaixoWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self._montar_ui()
        self.atualizar()

    def _montar_ui(self):
        layout = QVBoxLayout(self)

        self.titulo = QLabel("⚠ Estoque baixo")
        self.titulo.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.titulo)

        self.lista = QListWidget()
        layout.addWidget(self.lista)

    def atualizar(self):
        """Recarrega os dados. Chame isso sempre que reabrir o dashboard."""
        produtos = estoque_baixo()

        self.lista.clear()

        if not produtos:
            self.titulo.setText("✔ Estoque em dia")
            item = QListWidgetItem("Nenhum produto abaixo do mínimo.")
            self.lista.addItem(item)
            return

        self.titulo.setText(f"⚠ Estoque baixo ({len(produtos)})")
        for nome, quantidade, minimo in produtos:
            item = QListWidgetItem(f"{nome} — {quantidade} un. (mínimo: {minimo})")
            if quantidade == 0:
                item.setForeground(Qt.red)
            self.lista.addItem(item)