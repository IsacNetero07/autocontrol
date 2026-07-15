from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class Card(QFrame):

    def __init__(self, titulo, valor, emoji):
        super().__init__()

        self.setObjectName("card")
        self.setFixedSize(250, 140)

        # Sombra
        self.sombra = QGraphicsDropShadowEffect(self)
        self.sombra.setBlurRadius(15)
        self.sombra.setXOffset(0)
        self.sombra.setYOffset(4)
        self.sombra.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(self.sombra)

        layout = QVBoxLayout()

        titulo_label = QLabel(f"{emoji} {titulo}")
        titulo_label.setObjectName("cardTitulo")
        titulo_label.setStyleSheet("font-size:16px; font-weight:bold;")

        valor_label = QLabel(valor)
        valor_label.setObjectName("cardValor")
        valor_label.setAlignment(Qt.AlignCenter)
        valor_label.setStyleSheet("font-size:32px; font-weight:bold;")

        layout.addWidget(titulo_label)
        layout.addStretch()
        layout.addWidget(valor_label)

        self.setLayout(layout)

    def enterEvent(self, event):
        self.sombra.setBlurRadius(25)
        self.sombra.setYOffset(8)
        self.sombra.setColor(QColor(0, 0, 0, 70))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.sombra.setBlurRadius(15)
        self.sombra.setYOffset(4)
        self.sombra.setColor(QColor(0, 0, 0, 40))
        super().leaveEvent(event)