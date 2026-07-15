from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFormLayout,
    QPushButton,
    QComboBox,
    QTextEdit,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QScrollArea
)

from database.clientes_db import listar_clientes
from database.veiculos_db import listar_veiculos, obter_cliente_do_veiculo
from database.ordem_servico_db import (
    salvar_ordem,
    listar_ordens
)

from styles.style import (
    botao_azul,
    estilo_titulo,
    tabela
)

from utils.exportar import exportar_tabela_csv
from database.sessao import nome_usuario_atual
from database.log_db import registrar_log
from views.components.paginacao import PaginacaoWidget

from views.components.galeria_fotos import GaleriaFotos


class TelaOrdemServico(QWidget):

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

        titulo = QLabel("Ordem de Serviço")
        titulo.setStyleSheet(estilo_titulo())
        layout.addWidget(titulo)

        formulario = QFormLayout()

        self.cliente = QComboBox()
        self.veiculo = QComboBox()

        self.mecanico = QLineEdit()

        self.problema = QTextEdit()
        self.servicos = QTextEdit()

        self.status = QComboBox()
        self.status.addItems([
            "Aberta",
            "Em andamento",
            "Finalizada"
        ])

        self.valor = QLineEdit()

        self.data = QLineEdit()
        self.data.setPlaceholderText("13/07/2026")

        formulario.addRow("Cliente:", self.cliente)
        formulario.addRow("Veículo:", self.veiculo)
        formulario.addRow("Mecânico:", self.mecanico)
        formulario.addRow("Problema:", self.problema)
        formulario.addRow("Serviços:", self.servicos)
        formulario.addRow("Status:", self.status)
        formulario.addRow("Valor:", self.valor)
        formulario.addRow("Data:", self.data)

        layout.addLayout(formulario)

        self.botao = QPushButton("Salvar Ordem")
        self.botao.setStyleSheet(botao_azul())

        layout.addWidget(self.botao)

        self.tabela = QTableWidget()

        self.tabela.setColumnCount(6)

        self.tabela.setHorizontalHeaderLabels([
            "ID",
            "Cliente",
            "Veículo",
            "Status",
            "Valor",
            "Data"
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

        # Botão de exportação
        linha_exportar = QHBoxLayout()
        self.botao_exportar = QPushButton("📤 Exportar CSV")
        linha_exportar.addStretch()
        linha_exportar.addWidget(self.botao_exportar)
        layout.addLayout(linha_exportar)

        # Galeria de fotos da OS selecionada
        dica_galeria = QLabel("Selecione uma ordem na tabela acima para ver/anexar fotos:")
        dica_galeria.setStyleSheet("color:#6B7280; font-size:12px; margin-top:8px;")
        layout.addWidget(dica_galeria)

        self.galeria = GaleriaFotos()
        layout.addWidget(self.galeria)

        conteudo.setLayout(layout)
        scroll.setWidget(conteudo)

        layout_externo.addWidget(scroll)

        self.botao.clicked.connect(self.salvar)
        self.botao_exportar.clicked.connect(self.exportar_csv)
        self.tabela.itemSelectionChanged.connect(self.selecionar_ordem)

        self.carregar_clientes()
        self.carregar_veiculos()
        self.carregar_ordens()

    def carregar_clientes(self):
        self.cliente.clear()
        for cliente in listar_clientes():
            self.cliente.addItem(cliente[1], cliente[0])

    def carregar_veiculos(self):
        self.veiculo.clear()
        for veiculo in listar_veiculos():
            self.veiculo.addItem(veiculo[1], veiculo[0])

    def selecionar_veiculo(self, id_veiculo):
        """
        Pré-seleciona o veículo (e o cliente dono dele) quando se chega
        nesta tela vinda do fluxo de cadastro de veículo.
        """
        self.carregar_clientes()
        self.carregar_veiculos()

        indice_veiculo = self.veiculo.findData(id_veiculo)

        if indice_veiculo != -1:
            self.veiculo.setCurrentIndex(indice_veiculo)

        id_cliente = obter_cliente_do_veiculo(id_veiculo)

        if id_cliente is not None:
            indice_cliente = self.cliente.findData(id_cliente)

            if indice_cliente != -1:
                self.cliente.setCurrentIndex(indice_cliente)

        self.mecanico.setFocus()

    def _renderizar_pagina_atual(self, _pagina=None):
        pagina_dados = self.paginacao.fatia_atual(self.dados_completos)

        self.tabela.setRowCount(len(pagina_dados))
        for linha, ordem in enumerate(pagina_dados):
            for coluna, dado in enumerate(ordem):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(dado))
                )

    def carregar_ordens(self, resetar_pagina=True):
        self.dados_completos = listar_ordens()
        self.paginacao.definir_total(len(self.dados_completos))

        if resetar_pagina:
            self.paginacao.resetar()

        self._renderizar_pagina_atual()

    def exportar_csv(self):
        tabela_completa = QTableWidget()
        tabela_completa.setColumnCount(6)
        tabela_completa.setHorizontalHeaderLabels([
            "ID", "Cliente", "Veículo", "Status", "Valor", "Data"
        ])
        tabela_completa.setRowCount(len(self.dados_completos))

        for linha, ordem in enumerate(self.dados_completos):
            for coluna, dado in enumerate(ordem):
                tabela_completa.setItem(linha, coluna, QTableWidgetItem(str(dado)))

        exportar_tabela_csv(self, tabela_completa, nome_sugerido="ordens_servico")

    def selecionar_ordem(self):
        linha_atual = self.tabela.currentRow()

        if linha_atual < 0:
            return

        item_id = self.tabela.item(linha_atual, 0)
        if item_id is None:
            return

        os_id = int(item_id.text())

        self.galeria.definir_entidade("ordem_servico", os_id, rotulo=f"— OS #{os_id}")

    def salvar(self):
        cliente_id = self.cliente.currentData()
        veiculo_id = self.veiculo.currentData()

        if cliente_id is None:
            QMessageBox.warning(
                self,
                "Erro",
                "Nenhum cliente disponível. Cadastre um cliente antes de continuar."
            )
            return

        if veiculo_id is None:
            QMessageBox.warning(
                self,
                "Erro",
                "Nenhum veículo disponível. Cadastre um veículo antes de continuar."
            )
            return

        mecanico = self.mecanico.text().strip()
        valor = self.valor.text().strip()
        data = self.data.text().strip()

        if mecanico == "":
            QMessageBox.warning(self, "Erro", "Informe o mecânico responsável.")
            return

        if valor != "" and not valor.replace(",", ".").replace(".", "", 1).isdigit():
            QMessageBox.warning(self, "Erro", "Valor inválido.")
            return

        salvar_ordem(
            cliente_id,
            veiculo_id,
            mecanico,
            self.problema.toPlainText().strip(),
            self.servicos.toPlainText().strip(),
            self.status.currentText(),
            valor,
            data
        )

        registrar_log(
            nome_usuario_atual(),
            "Criar - Ordem de Serviço",
            f"Mecânico {mecanico} - Status {self.status.currentText()} - Data {data}"
        )

        QMessageBox.information(
            self,
            "Sucesso",
            "Ordem cadastrada!"
        )

        self.mecanico.clear()
        self.problema.clear()
        self.servicos.clear()
        self.valor.clear()
        self.data.clear()

        self.carregar_ordens(resetar_pagina=False)