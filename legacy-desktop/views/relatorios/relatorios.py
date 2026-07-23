import os
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)

from styles.style import botao_azul, estilo_titulo
from database.dashboard_db import receita_por_mes, ordens_por_mes
from views.components.grafico_matplotlib import GraficoBarras

from database.relatorios_db import (
    dados_relatorio_clientes,
    dados_relatorio_veiculos,
    dados_relatorio_ordens,
    dados_relatorio_estoque,
    dados_relatorio_financeiro,
)
from utils.pdf_generator import gerar_relatorio_pdf


class TelaRelatorios(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        titulo = QLabel("Relatórios")
        titulo.setStyleSheet(estilo_titulo())
        layout.addWidget(titulo)

        subtitulo_graficos = QLabel("Análise Visual")
        subtitulo_graficos.setStyleSheet("""
            font-size:16px;
            font-weight:bold;
            color:#1E293B;
            margin-top:10px;
        """)
        layout.addWidget(subtitulo_graficos)

        graficos_layout = QHBoxLayout()

        self.grafico_receita = GraficoBarras("Receita por mês (últimos 6 meses)", cor="#22C55E")
        self.grafico_ordens = GraficoBarras("Ordens de Serviço por mês (últimos 6 meses)", cor="#3B82F6")

        graficos_layout.addWidget(self.grafico_receita)
        graficos_layout.addWidget(self.grafico_ordens)

        layout.addLayout(graficos_layout)

        subtitulo_relatorios = QLabel("Relatórios Detalhados (PDF)")
        subtitulo_relatorios.setStyleSheet("""
            font-size:16px;
            font-weight:bold;
            color:#1E293B;
            margin-top:15px;
        """)
        layout.addWidget(subtitulo_relatorios)

        self.btn_clientes = QPushButton("📄 Relatório de Clientes")
        self.btn_veiculos = QPushButton("🚗 Relatório de Veículos")
        self.btn_ordens = QPushButton("🔧 Relatório de Ordens")
        self.btn_estoque = QPushButton("📦 Relatório de Estoque")
        self.btn_financeiro = QPushButton("💰 Relatório Financeiro")

        for botao in [
            self.btn_clientes,
            self.btn_veiculos,
            self.btn_ordens,
            self.btn_estoque,
            self.btn_financeiro,
        ]:
            botao.setStyleSheet(botao_azul())
            botao.setMinimumHeight(45)
            layout.addWidget(botao)

        layout.addStretch()

        self.setLayout(layout)

        self.atualizar_graficos()

        # Conectar botões de PDF
        self.btn_clientes.clicked.connect(self.gerar_pdf_clientes)
        self.btn_veiculos.clicked.connect(self.gerar_pdf_veiculos)
        self.btn_ordens.clicked.connect(self.gerar_pdf_ordens)
        self.btn_estoque.clicked.connect(self.gerar_pdf_estoque)
        self.btn_financeiro.clicked.connect(self.gerar_pdf_financeiro)

    def atualizar_graficos(self):
        dados_receita = receita_por_mes(6)
        labels_r = [m for m, v in dados_receita]
        valores_r = [v for m, v in dados_receita]
        self.grafico_receita.atualizar(labels_r, valores_r)

        dados_ordens = ordens_por_mes(6)
        labels_o = [m for m, v in dados_ordens]
        valores_o = [v for m, v in dados_ordens]
        self.grafico_ordens.atualizar(labels_o, valores_o)

    def showEvent(self, event):
        super().showEvent(event)
        self.atualizar_graficos()

    def _abrir_pdf(self, caminho):
        resposta = QMessageBox.question(
            self,
            "Relatório gerado",
            f"PDF salvo em:\n{caminho}\n\nDeseja abrir agora?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if resposta == QMessageBox.Yes:
            os.startfile(str(caminho))

    def gerar_pdf_clientes(self):
        dados = dados_relatorio_clientes()
        colunas = ["Nome", "CPF", "Telefone", "E-mail", "Endereço"]
        caminho = gerar_relatorio_pdf("Relatório de Clientes", colunas, dados, "relatorio_clientes.pdf")
        self._abrir_pdf(caminho)

    def gerar_pdf_veiculos(self):
        dados = dados_relatorio_veiculos()
        colunas = ["Placa", "Marca", "Modelo", "Ano", "Cliente"]
        caminho = gerar_relatorio_pdf("Relatório de Veículos", colunas, dados, "relatorio_veiculos.pdf")
        self._abrir_pdf(caminho)

    def gerar_pdf_ordens(self):
        dados = dados_relatorio_ordens()
        colunas = ["Nº OS", "Cliente", "Placa", "Status", "Valor", "Data"]
        caminho = gerar_relatorio_pdf("Relatório de Ordens de Serviço", colunas, dados, "relatorio_ordens.pdf")
        self._abrir_pdf(caminho)

    def gerar_pdf_estoque(self):
        dados = dados_relatorio_estoque()
        colunas = ["Produto", "Categoria", "Qtd", "Valor", "Fornecedor"]
        caminho = gerar_relatorio_pdf("Relatório de Estoque", colunas, dados, "relatorio_estoque.pdf")
        self._abrir_pdf(caminho)

    def gerar_pdf_financeiro(self):
        dados = dados_relatorio_financeiro()
        colunas = ["Descrição", "Tipo", "Valor", "Data"]
        caminho = gerar_relatorio_pdf("Relatório Financeiro", colunas, dados, "relatorio_financeiro.pdf")
        self._abrir_pdf(caminho)