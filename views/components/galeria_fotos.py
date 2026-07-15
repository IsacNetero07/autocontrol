from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFileDialog, QMessageBox, QGridLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from database.fotos_db import adicionar_foto, listar_fotos, excluir_foto


class GaleriaFotos(QWidget):

    def __init__(self, entidade_tipo=None, entidade_id=None):
        super().__init__()

        self.entidade_tipo = entidade_tipo
        self.entidade_id = entidade_id

        layout = QVBoxLayout()
        self.setLayout(layout)

        topo = QHBoxLayout()
        self.titulo = QLabel("📷 Fotos")
        self.titulo.setStyleSheet("font-size:14px; font-weight:bold; color:#1E293B;")

        btn_adicionar = QPushButton("+ Adicionar fotos")
        btn_adicionar.setStyleSheet("""
            QPushButton {
                background:#3B82F6; color:white; border-radius:6px;
                padding:6px 12px; font-size:12px;
            }
            QPushButton:hover { background:#2563EB; }
        """)
        btn_adicionar.clicked.connect(self.adicionar_fotos)

        topo.addWidget(self.titulo)
        topo.addStretch()
        topo.addWidget(btn_adicionar)
        layout.addLayout(topo)

        self.area_rolagem = QScrollArea()
        self.area_rolagem.setWidgetResizable(True)
        self.area_rolagem.setFixedHeight(160)

        self.container = QWidget()
        self.grid = QGridLayout()
        self.container.setLayout(self.grid)
        self.area_rolagem.setWidget(self.container)

        layout.addWidget(self.area_rolagem)

        if self.entidade_id is not None:
            self.carregar_fotos()

    def definir_entidade(self, entidade_tipo, entidade_id, rotulo=""):
        self.entidade_tipo = entidade_tipo
        self.entidade_id = entidade_id
        self.titulo.setText(f"📷 Fotos {rotulo}".strip())
        self.carregar_fotos()

    def carregar_fotos(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if self.entidade_id is None:
            vazio = QLabel("Nenhum registro selecionado.")
            vazio.setStyleSheet("color:#9CA3AF; font-size:12px;")
            self.grid.addWidget(vazio, 0, 0)
            return

        fotos = listar_fotos(self.entidade_tipo, self.entidade_id)

        if not fotos:
            vazio = QLabel("Nenhuma foto anexada ainda.")
            vazio.setStyleSheet("color:#9CA3AF; font-size:12px;")
            self.grid.addWidget(vazio, 0, 0)
            return

        for indice, (foto_id, caminho) in enumerate(fotos):
            miniatura = self.criar_miniatura(foto_id, caminho)
            linha = indice // 4
            coluna = indice % 4
            self.grid.addWidget(miniatura, linha, coluna)

    def criar_miniatura(self, foto_id, caminho):
        bloco = QWidget()
        bloco_layout = QVBoxLayout()
        bloco_layout.setContentsMargins(2, 2, 2, 2)
        bloco.setLayout(bloco_layout)

        imagem = QLabel()
        pixmap = QPixmap(caminho)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            imagem.setPixmap(pixmap)
        else:
            imagem.setText("Erro ao\ncarregar")
        imagem.setFixedSize(100, 100)
        imagem.setStyleSheet("border:1px solid #D1D5DB; border-radius:4px; background:#F8FAFC;")
        imagem.setAlignment(Qt.AlignCenter)

        btn_remover = QPushButton("Remover")
        btn_remover.setStyleSheet("""
            QPushButton {
                font-size:10px; color:#EF4444; border:none; background:transparent;
            }
            QPushButton:hover { text-decoration: underline; }
        """)
        btn_remover.clicked.connect(lambda: self.remover_foto(foto_id))

        bloco_layout.addWidget(imagem)
        bloco_layout.addWidget(btn_remover)

        return bloco

    def adicionar_fotos(self):
        if self.entidade_id is None:
            QMessageBox.warning(self, "Atenção", "Selecione um registro antes de adicionar fotos.")
            return

        arquivos, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar fotos",
            "",
            "Imagens (*.png *.jpg *.jpeg *.webp)"
        )

        if not arquivos:
            return

        for arquivo in arquivos:
            try:
                adicionar_foto(self.entidade_tipo, self.entidade_id, arquivo)
            except Exception as erro:
                QMessageBox.critical(self, "Erro", f"Erro ao adicionar foto:\n{erro}")

        self.carregar_fotos()

    def remover_foto(self, foto_id):
        resposta = QMessageBox.question(
            self, "Remover foto", "Deseja remover esta foto?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if resposta == QMessageBox.Yes:
            excluir_foto(foto_id)
            self.carregar_fotos()