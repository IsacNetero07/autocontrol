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
    QComboBox,
    QAbstractItemView,
    QScrollArea
)
from PySide6.QtCore import Signal

from database.veiculos_db import (
    salvar_veiculo,
    listar_veiculos,
    excluir_veiculo,
    atualizar_veiculo
)

from database.clientes_db import listar_clientes

from styles.style import botao_azul, estilo_titulo, tabela

from utils.validacao import validar_obrigatorios, validar_numero_inteiro
from utils.exportar import exportar_tabela_csv
from database.sessao import nome_usuario_atual
from database.log_db import registrar_log
from views.components.paginacao import PaginacaoWidget


class TelaVeiculos(QWidget):

    veiculo_cadastrado = Signal(int)

    def __init__(self):
        super().__init__()

        self.editando_id = None
        self.dados_completos = []

        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        conteudo = QWidget()
        layout = QVBoxLayout(conteudo)

        lbl_titulo = QLabel("Cadastro de Veículos")
        lbl_titulo.setStyleSheet(estilo_titulo())

        layout.addWidget(lbl_titulo)

        formulario = QFormLayout()

        self.placa = QLineEdit()
        self.placa.setPlaceholderText("Ex: ABC1D23")

        self.marca = QLineEdit()
        self.marca.setPlaceholderText("Ex: Toyota")

        self.modelo = QLineEdit()
        self.modelo.setPlaceholderText("Ex: Corolla")

        self.ano = QLineEdit()
        self.ano.setPlaceholderText("Ex: 2022")

        self.cor = QLineEdit()
        self.cor.setPlaceholderText("Ex: Preto")

        self.quilometragem = QLineEdit()
        self.quilometragem.setPlaceholderText("Ex: 50000")

        for campo in [
            self.placa,
            self.marca,
            self.modelo,
            self.ano,
            self.cor,
            self.quilometragem,
        ]:
            campo.setMinimumHeight(35)

        self.cliente = QComboBox()
        self.cliente.setMinimumHeight(35)

        formulario.addRow("Placa:", self.placa)
        formulario.addRow("Marca:", self.marca)
        formulario.addRow("Modelo:", self.modelo)
        formulario.addRow("Ano:", self.ano)
        formulario.addRow("Cor:", self.cor)
        formulario.addRow("Quilometragem:", self.quilometragem)
        formulario.addRow("Cliente:", self.cliente)

        layout.addLayout(formulario)

        linha_botoes = QHBoxLayout()

        self.botao_salvar = QPushButton("💾 Salvar Veículo")
        self.botao_salvar.setStyleSheet(botao_azul())

        self.botao_cancelar = QPushButton("✖ Cancelar edição")
        self.botao_cancelar.setVisible(False)

        linha_botoes.addWidget(self.botao_salvar)
        linha_botoes.addWidget(self.botao_cancelar)

        layout.addLayout(linha_botoes)

        self.tabela = QTableWidget()
        self.tabela.setStyleSheet(tabela())

        self.tabela.setAlternatingRowColors(True)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)

        self.tabela.setColumnCount(6)

        self.tabela.setHorizontalHeaderLabels([
            "ID",
            "Placa",
            "Marca",
            "Modelo",
            "Ano",
            "Cliente"
        ])

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabela.setMinimumHeight(200)
        self.tabela.setMaximumHeight(300)

        layout.addWidget(self.tabela)

        # ---- Paginação ----
        self.paginacao = PaginacaoWidget(tamanho_pagina=20)
        self.paginacao.pagina_alterada.connect(self._renderizar_pagina_atual)
        layout.addWidget(self.paginacao)

        linha_acoes_tabela = QHBoxLayout()

        self.botao_editar = QPushButton("✏️ Editar selecionado")
        self.botao_excluir = QPushButton("🗑️ Excluir selecionado")
        self.botao_exportar = QPushButton("📤 Exportar CSV")

        self.botao_excluir.setStyleSheet("""
            QPushButton {
                background:#DC2626;
                color:white;
                border:none;
                border-radius:10px;
                padding:10px;
                font-size:14px;
                font-weight:bold;
            }
            QPushButton:hover {
                background:#B91C1C;
            }
        """)

        linha_acoes_tabela.addWidget(self.botao_editar)
        linha_acoes_tabela.addWidget(self.botao_excluir)
        linha_acoes_tabela.addWidget(self.botao_exportar)

        layout.addLayout(linha_acoes_tabela)

        conteudo.setLayout(layout)
        scroll.setWidget(conteudo)

        layout_externo.addWidget(scroll)

        self.botao_salvar.clicked.connect(self.salvar)
        self.botao_cancelar.clicked.connect(self.cancelar_edicao)
        self.botao_editar.clicked.connect(self.carregar_para_edicao)
        self.botao_excluir.clicked.connect(self.excluir)
        self.botao_exportar.clicked.connect(self.exportar_csv)

        self.carregar_clientes()
        self.carregar_veiculos()

    def carregar_clientes(self):
        self.cliente.clear()

        clientes = listar_clientes()

        for cliente in clientes:
            self.cliente.addItem(
                cliente[1],
                cliente[0]
            )

    def _renderizar_pagina_atual(self, _pagina=None):
        pagina_dados = self.paginacao.fatia_atual(self.dados_completos)

        self.tabela.setRowCount(len(pagina_dados))
        for linha, veiculo in enumerate(pagina_dados):
            for coluna, dado in enumerate(veiculo):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(dado))
                )

    def carregar_veiculos(self, resetar_pagina=True):
        self.dados_completos = listar_veiculos()
        self.paginacao.definir_total(len(self.dados_completos))

        if resetar_pagina:
            self.paginacao.resetar()

        self._renderizar_pagina_atual()

    def exportar_csv(self):
        tabela_completa = QTableWidget()
        tabela_completa.setColumnCount(6)
        tabela_completa.setHorizontalHeaderLabels([
            "ID", "Placa", "Marca", "Modelo", "Ano", "Cliente"
        ])
        tabela_completa.setRowCount(len(self.dados_completos))

        for linha, veiculo in enumerate(self.dados_completos):
            for coluna, dado in enumerate(veiculo):
                tabela_completa.setItem(linha, coluna, QTableWidgetItem(str(dado)))

        exportar_tabela_csv(self, tabela_completa, nome_sugerido="veiculos")

    def linha_selecionada(self):
        linha_atual = self.tabela.currentRow()

        if linha_atual < 0:
            QMessageBox.warning(
                self,
                "Nenhum veículo selecionado",
                "Selecione um veículo na tabela primeiro."
            )
            return None

        item_id = self.tabela.item(linha_atual, 0)

        if item_id is None:
            return None

        return int(item_id.text())

    def carregar_para_edicao(self):
        veiculo_id = self.linha_selecionada()

        if veiculo_id is None:
            return

        linha_atual = self.tabela.currentRow()

        self.placa.setText(self.tabela.item(linha_atual, 1).text())
        self.marca.setText(self.tabela.item(linha_atual, 2).text())
        self.modelo.setText(self.tabela.item(linha_atual, 3).text())
        self.ano.setText(self.tabela.item(linha_atual, 4).text())

        nome_cliente = self.tabela.item(linha_atual, 5).text()
        indice_cliente = self.cliente.findText(nome_cliente)
        if indice_cliente != -1:
            self.cliente.setCurrentIndex(indice_cliente)

        self.editando_id = veiculo_id
        self.botao_salvar.setText("💾 Atualizar Veículo")
        self.botao_cancelar.setVisible(True)

    def cancelar_edicao(self):
        self.editando_id = None
        self.botao_salvar.setText("💾 Salvar Veículo")
        self.botao_cancelar.setVisible(False)

        self.placa.clear()
        self.marca.clear()
        self.modelo.clear()
        self.ano.clear()
        self.cor.clear()
        self.quilometragem.clear()
        self.cliente.setCurrentIndex(0)

    def excluir(self):
        veiculo_id = self.linha_selecionada()

        if veiculo_id is None:
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Tem certeza que deseja excluir este veículo? Essa ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if resposta != QMessageBox.Yes:
            return

        excluir_veiculo(veiculo_id)

        registrar_log(
            nome_usuario_atual(),
            "Excluir - Veículos",
            f"ID {veiculo_id}"
        )

        QMessageBox.information(self, "Excluído", "Veículo excluído com sucesso!")

        if self.editando_id == veiculo_id:
            self.cancelar_edicao()

        self.carregar_veiculos(resetar_pagina=False)

    def validar_campos(self, placa, marca, modelo, ano, cor, quilometragem, cliente_id):

        if not validar_obrigatorios(self, {
            "Placa": placa,
            "Marca": marca,
            "Modelo": modelo,
            "Ano": ano,
            "Cor": cor,
            "Quilometragem": quilometragem,
        }):
            return False

        if not validar_numero_inteiro(self, "Ano", ano):
            return False

        if not validar_numero_inteiro(self, "Quilometragem", quilometragem):
            return False

        if cliente_id is None:
            QMessageBox.warning(
                self,
                "Erro",
                "Nenhum cliente disponível. Cadastre um cliente antes de continuar."
            )
            return False

        return True

    def salvar(self):
        placa = self.placa.text().strip()
        marca = self.marca.text().strip()
        modelo = self.modelo.text().strip()
        ano = self.ano.text().strip()
        cor = self.cor.text().strip()
        quilometragem = self.quilometragem.text().strip()

        cliente_id = self.cliente.currentData()

        if not self.validar_campos(placa, marca, modelo, ano, cor, quilometragem, cliente_id):
            return

        if self.editando_id is None:
            id_veiculo = salvar_veiculo(
                placa, marca, modelo, ano, cor, quilometragem, cliente_id
            )

            registrar_log(
                nome_usuario_atual(),
                "Criar - Veículos",
                f"Placa {placa}"
            )

            QMessageBox.information(self, "Sucesso", "Veículo cadastrado!")

            self.veiculo_cadastrado.emit(id_veiculo)
        else:
            atualizar_veiculo(
                self.editando_id,
                placa, marca, modelo, ano, cor, quilometragem, cliente_id
            )

            registrar_log(
                nome_usuario_atual(),
                "Editar - Veículos",
                f"ID {self.editando_id}: Placa {placa}"
            )

            QMessageBox.information(self, "Sucesso", "Veículo atualizado!")
            self.cancelar_edicao()

        self.placa.clear()
        self.marca.clear()
        self.modelo.clear()
        self.ano.clear()
        self.cor.clear()
        self.quilometragem.clear()
        self.cliente.setCurrentIndex(0)
        self.placa.setFocus()

        self.carregar_veiculos(resetar_pagina=False)