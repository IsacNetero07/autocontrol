"""
views/orcamento/orcamento.py

Tela de Orçamentos: cria orçamento, e só quando o cliente aprova
é que ele vira Ordem de Serviço de verdade (evita "fechar" serviço
que ainda tá em negociação).

Mesma observação do agenda.py: assumi listar_clientes() e
listar_veiculos_por_cliente(cliente_id) em database/cliente_db.py e
database/veiculo_db.py. Ajuste os imports abaixo se os nomes forem outros.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QDoubleSpinBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QGroupBox,
)

from database.orcamento_db import (
    salvar_orcamento,
    listar_orcamentos,
    aprovar_orcamento,
    rejeitar_orcamento,
    excluir_orcamento,
)

try:
    from database.cliente_db import listar_clientes
except ImportError:
    listar_clientes = None

try:
    from database.veiculo_db import listar_veiculos_por_cliente
except ImportError:
    listar_veiculos_por_cliente = None


class OrcamentoScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orçamentos")
        self._montar_ui()
        self._carregar_clientes()
        self._atualizar_lista()

    # ---------------------------------------------------------------
    # UI
    # ---------------------------------------------------------------
    def _montar_ui(self):
        layout_principal = QHBoxLayout(self)

        # ---------- Coluna esquerda: lista de orçamentos ----------
        coluna_esquerda = QVBoxLayout()

        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos", "Pendente", "Aprovado", "Rejeitado"])
        self.filtro_status.currentIndexChanged.connect(self._atualizar_lista)
        coluna_esquerda.addWidget(self.filtro_status)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Cliente", "Placa", "Problema", "Valor estimado", "Status", "Data"]
        )
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setColumnHidden(0, True)
        coluna_esquerda.addWidget(self.tabela)

        linha_botoes = QHBoxLayout()

        botao_aprovar = QPushButton("✔ Aprovar (gera OS)")
        botao_aprovar.clicked.connect(self._aprovar_selecionado)
        linha_botoes.addWidget(botao_aprovar)

        botao_rejeitar = QPushButton("✘ Rejeitar")
        botao_rejeitar.clicked.connect(self._rejeitar_selecionado)
        linha_botoes.addWidget(botao_rejeitar)

        botao_excluir = QPushButton("Excluir")
        botao_excluir.clicked.connect(self._excluir_selecionado)
        linha_botoes.addWidget(botao_excluir)

        coluna_esquerda.addLayout(linha_botoes)

        layout_principal.addLayout(coluna_esquerda, stretch=2)

        # ---------- Coluna direita: formulário de novo orçamento ----------
        grupo_form = QGroupBox("Novo orçamento")
        form_layout = QFormLayout()

        self.combo_cliente = QComboBox()
        self.combo_cliente.currentIndexChanged.connect(self._carregar_veiculos)
        form_layout.addRow("Cliente:", self.combo_cliente)

        self.combo_veiculo = QComboBox()
        form_layout.addRow("Veículo:", self.combo_veiculo)

        self.mecanico_edit = QLineEdit()
        form_layout.addRow("Mecânico:", self.mecanico_edit)

        self.problema_edit = QLineEdit()
        form_layout.addRow("Problema relatado:", self.problema_edit)

        self.servicos_edit = QTextEdit()
        self.servicos_edit.setPlaceholderText("Serviços previstos...")
        self.servicos_edit.setFixedHeight(80)
        form_layout.addRow("Serviços previstos:", self.servicos_edit)

        self.valor_spin = QDoubleSpinBox()
        self.valor_spin.setMaximum(999999.99)
        self.valor_spin.setPrefix("R$ ")
        self.valor_spin.setDecimals(2)
        form_layout.addRow("Valor estimado:", self.valor_spin)

        botao_salvar = QPushButton("Salvar orçamento")
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

        if listar_clientes is None:
            self.combo_cliente.addItem("(cadastre clientes primeiro)", None)
            return

        clientes = listar_clientes()
        if not clientes:
            self.combo_cliente.addItem("(nenhum cliente cadastrado)", None)
            return

        for cliente_id, nome in clientes:
            self.combo_cliente.addItem(nome, cliente_id)

        self._carregar_veiculos()

    def _carregar_veiculos(self):
        self.combo_veiculo.clear()
        cliente_id = self.combo_cliente.currentData()

        if listar_veiculos_por_cliente is None or cliente_id is None:
            self.combo_veiculo.addItem("(nenhum veículo)", None)
            return

        veiculos = listar_veiculos_por_cliente(cliente_id)
        if not veiculos:
            self.combo_veiculo.addItem("(nenhum veículo)", None)
            return

        for veiculo in veiculos:
            veiculo_id, placa = veiculo[0], veiculo[1]
            self.combo_veiculo.addItem(placa, veiculo_id)

    def _atualizar_lista(self):
        status = self.filtro_status.currentText()
        status = None if status == "Todos" else status

        orcamentos = listar_orcamentos(status)

        self.tabela.setRowCount(0)
        for linha, orc in enumerate(orcamentos):
            self.tabela.insertRow(linha)
            for coluna, valor in enumerate(orc):
                texto = str(valor) if valor is not None else ""
                if coluna == 4 and valor is not None:
                    texto = f"R$ {valor:.2f}"
                self.tabela.setItem(linha, coluna, QTableWidgetItem(texto))

    def _linha_selecionada_id(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um orçamento na tabela.")
            return None
        return int(self.tabela.item(linha, 0).text())

    # ---------------------------------------------------------------
    # Ações
    # ---------------------------------------------------------------
    def _salvar(self):
        cliente_id = self.combo_cliente.currentData()
        veiculo_id = self.combo_veiculo.currentData()
        mecanico = self.mecanico_edit.text().strip()
        problema = self.problema_edit.text().strip()
        servicos = self.servicos_edit.toPlainText().strip()
        valor = self.valor_spin.value()

        if cliente_id is None:
            QMessageBox.warning(self, "Atenção", "Selecione um cliente.")
            return

        if not problema:
            QMessageBox.warning(self, "Atenção", "Descreva o problema relatado.")
            return

        salvar_orcamento(cliente_id, veiculo_id, mecanico, problema, servicos, valor)

        self.mecanico_edit.clear()
        self.problema_edit.clear()
        self.servicos_edit.clear()
        self.valor_spin.setValue(0)

        self._atualizar_lista()
        QMessageBox.information(self, "Sucesso", "Orçamento salvo!")

    def _aprovar_selecionado(self):
        orcamento_id = self._linha_selecionada_id()
        if orcamento_id is None:
            return

        try:
            ordem_servico_id = aprovar_orcamento(orcamento_id)
        except ValueError as erro:
            QMessageBox.warning(self, "Não foi possível aprovar", str(erro))
            return

        self._atualizar_lista()
        QMessageBox.information(
            self,
            "Orçamento aprovado",
            f"OS #{ordem_servico_id} criada com sucesso a partir deste orçamento."
        )

    def _rejeitar_selecionado(self):
        orcamento_id = self._linha_selecionada_id()
        if orcamento_id is None:
            return

        rejeitar_orcamento(orcamento_id)
        self._atualizar_lista()

    def _excluir_selecionado(self):
        orcamento_id = self._linha_selecionada_id()
        if orcamento_id is None:
            return

        resposta = QMessageBox.question(
            self, "Confirmar exclusão", "Tem certeza que deseja excluir este orçamento?"
        )
        if resposta == QMessageBox.Yes:
            excluir_orcamento(orcamento_id)
            self._atualizar_lista()