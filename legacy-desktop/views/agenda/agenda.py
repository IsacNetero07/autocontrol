from datetime import datetime

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QTextCharFormat, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QTimeEdit,
    QPushButton,
    QCalendarWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QGroupBox,
)

from database.agendamentos_db import (
    salvar_agendamento,
    listar_agendamentos_por_data,
    listar_datas_com_agendamentos,
    excluir_agendamento,
)
from database.clientes_db import listar_clientes
from database.veiculos_db import listar_veiculos_por_cliente
from database.sessao import nome_usuario_atual
from database.log_db import registrar_log


class TelaAgenda(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agenda")
        self._montar_ui()
        self._carregar_clientes()
        self._marcar_dias_com_agendamento()
        self._atualizar_lista()

    # ---------------------------------------------------------------
    # UI
    # ---------------------------------------------------------------
    def _montar_ui(self):
        layout_principal = QHBoxLayout(self)

        # ---------- Coluna esquerda: calendário + tabela do dia ----------
        coluna_esquerda = QVBoxLayout()

        self.calendario = QCalendarWidget()
        self.calendario.setSelectedDate(QDate.currentDate())
        self.calendario.selectionChanged.connect(self._atualizar_lista)
        coluna_esquerda.addWidget(self.calendario)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Cliente", "Placa", "Hora", "Descrição", "Status"]
        )
        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setColumnHidden(0, True)  # esconde a coluna ID
        coluna_esquerda.addWidget(self.tabela)

        botao_excluir = QPushButton("Excluir agendamento selecionado")
        botao_excluir.clicked.connect(self._excluir_selecionado)
        coluna_esquerda.addWidget(botao_excluir)

        layout_principal.addLayout(coluna_esquerda, stretch=2)

        # ---------- Coluna direita: formulário de novo agendamento ----------
        grupo_form = QGroupBox("Novo agendamento")
        form_layout = QFormLayout()

        self.combo_cliente = QComboBox()
        self.combo_cliente.currentIndexChanged.connect(self._carregar_veiculos)
        form_layout.addRow("Cliente:", self.combo_cliente)

        self.combo_veiculo = QComboBox()
        form_layout.addRow("Veículo:", self.combo_veiculo)

        self.hora_edit = QTimeEdit()
        self.hora_edit.setDisplayFormat("HH:mm")
        form_layout.addRow("Hora:", self.hora_edit)

        self.descricao_edit = QLineEdit()
        self.descricao_edit.setPlaceholderText("Ex: Troca de óleo, revisão...")
        form_layout.addRow("Descrição:", self.descricao_edit)

        botao_salvar = QPushButton("Salvar agendamento")
        botao_salvar.clicked.connect(self._salvar)
        form_layout.addRow(botao_salvar)

        grupo_form.setLayout(form_layout)

        coluna_direita = QVBoxLayout()
        coluna_direita.addWidget(grupo_form)
        coluna_direita.addStretch()

        layout_principal.addLayout(coluna_direita, stretch=1)

    # ---------------------------------------------------------------
    # Carregamento de dados
    # ---------------------------------------------------------------
    def _carregar_clientes(self):
        self.combo_cliente.clear()

        clientes = listar_clientes()

        if not clientes:
            self.combo_cliente.addItem("(nenhum cliente cadastrado)", None)
            return

        for cliente in clientes:
            cliente_id, nome = cliente[0], cliente[1]
            self.combo_cliente.addItem(nome, cliente_id)

        self._carregar_veiculos()

    def _carregar_veiculos(self):
        self.combo_veiculo.clear()
        cliente_id = self.combo_cliente.currentData()

        if cliente_id is None:
            self.combo_veiculo.addItem("(nenhum veículo)", None)
            return

        veiculos = listar_veiculos_por_cliente(cliente_id)
        if not veiculos:
            self.combo_veiculo.addItem("(nenhum veículo)", None)
            return

        for veiculo in veiculos:
            veiculo_id, placa = veiculo[0], veiculo[1]
            self.combo_veiculo.addItem(placa, veiculo_id)

    def _data_selecionada_str(self):
        """Retorna a data selecionada no calendário no formato dd/mm/aaaa."""
        qdate = self.calendario.selectedDate()
        return qdate.toString("dd/MM/yyyy")

    def _atualizar_lista(self):
        data = self._data_selecionada_str()
        agendamentos = listar_agendamentos_por_data(data)

        self.tabela.setRowCount(0)
        for linha, agendamento in enumerate(agendamentos):
            self.tabela.insertRow(linha)
            for coluna, valor in enumerate(agendamento):
                item = QTableWidgetItem(str(valor) if valor is not None else "")
                self.tabela.setItem(linha, coluna, item)

    def _marcar_dias_com_agendamento(self):
        formato = QTextCharFormat()
        formato.setBackground(QColor("#3B82F6"))
        formato.setForeground(QColor("white"))

        for data_str in listar_datas_com_agendamentos():
            try:
                data = datetime.strptime(data_str, "%d/%m/%Y")
                qdate = QDate(data.year, data.month, data.day)
                self.calendario.setDateTextFormat(qdate, formato)
            except ValueError:
                continue

    # ---------------------------------------------------------------
    # Ações
    # ---------------------------------------------------------------
    def _salvar(self):
        cliente_id = self.combo_cliente.currentData()
        veiculo_id = self.combo_veiculo.currentData()
        descricao = self.descricao_edit.text().strip()
        hora = self.hora_edit.time().toString("HH:mm")
        data = self._data_selecionada_str()

        if cliente_id is None:
            QMessageBox.warning(self, "Atenção", "Selecione um cliente.")
            return

        if not descricao:
            QMessageBox.warning(self, "Atenção", "Informe uma descrição.")
            return

        salvar_agendamento(cliente_id, veiculo_id, data, hora, descricao)

        registrar_log(
            nome_usuario_atual(),
            "Criar - Agendamento",
            f"{data} {hora} - {descricao}"
        )

        self.descricao_edit.clear()
        self._marcar_dias_com_agendamento()
        self._atualizar_lista()
        QMessageBox.information(self, "Sucesso", "Agendamento salvo!")

    def _excluir_selecionado(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um agendamento na tabela.")
            return

        agendamento_id = int(self.tabela.item(linha, 0).text())

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Tem certeza que deseja excluir este agendamento?",
        )
        if resposta == QMessageBox.Yes:
            excluir_agendamento(agendamento_id)

            registrar_log(
                nome_usuario_atual(),
                "Excluir - Agendamento",
                f"ID {agendamento_id}"
            )

            self._marcar_dias_com_agendamento()
            self._atualizar_lista()

    def showEvent(self, event):
        super().showEvent(event)
        self._carregar_clientes()
        self._marcar_dias_com_agendamento()
        self._atualizar_lista()