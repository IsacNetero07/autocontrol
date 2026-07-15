"""
views/historico_veiculo/historico_veiculo.py

Tela de consulta: digita a placa e vê todas as OS já feitas naquele veículo.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)

from database.ordem_servico_db import historico_por_placa


class HistoricoVeiculoScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Histórico do Veículo")
        self._montar_ui()

    def _montar_ui(self):
        layout = QVBoxLayout(self)

        # ---------- Barra de busca ----------
        barra_busca = QHBoxLayout()

        barra_busca.addWidget(QLabel("Placa:"))

        self.placa_edit = QLineEdit()
        self.placa_edit.setPlaceholderText("Ex: ABC1D23")
        self.placa_edit.returnPressed.connect(self._buscar)
        barra_busca.addWidget(self.placa_edit)

        botao_buscar = QPushButton("Buscar")
        botao_buscar.clicked.connect(self._buscar)
        barra_busca.addWidget(botao_buscar)

        layout.addLayout(barra_busca)

        # ---------- Resumo ----------
        self.resumo_label = QLabel("")
        self.resumo_label.setStyleSheet("color: gray;")
        layout.addWidget(self.resumo_label)

        # ---------- Tabela de resultados ----------
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Data", "Mecânico", "Problema", "Serviços", "Status", "Valor"]
        )
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setColumnHidden(0, True)
        layout.addWidget(self.tabela)

    def _buscar(self):
        placa = self.placa_edit.text().strip()

        if not placa:
            QMessageBox.warning(self, "Atenção", "Digite uma placa pra buscar.")
            return

        resultados = historico_por_placa(placa)

        self.tabela.setRowCount(0)

        if not resultados:
            self.resumo_label.setText(f"Nenhuma OS encontrada para '{placa}'.")
            return

        total_gasto = sum(r[6] or 0 for r in resultados)
        self.resumo_label.setText(
            f"{len(resultados)} ordem(ns) de serviço encontrada(s) — total: R$ {total_gasto:.2f}"
        )

        for linha, ordem in enumerate(resultados):
            self.tabela.insertRow(linha)
            for coluna, valor in enumerate(ordem):
                texto = str(valor) if valor is not None else ""
                if coluna == 6 and valor is not None:
                    texto = f"R$ {valor:.2f}"
                self.tabela.setItem(linha, coluna, QTableWidgetItem(texto))