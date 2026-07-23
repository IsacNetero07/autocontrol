import sys
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QFont
from PySide6.QtCore import Qt, QTimer

from database.database import criar_tabelas
from views.login.login import TelaLogin


def criar_splash_pixmap():
    """Gera a imagem do splash na hora, sem precisar de arquivo externo."""
    largura, altura = 420, 280
    pixmap = QPixmap(largura, altura)
    pixmap.fill(Qt.transparent)

    pintor = QPainter(pixmap)
    pintor.setRenderHint(QPainter.Antialiasing)

    # Fundo em gradiente (mesmo estilo da tela de login)
    gradiente = QLinearGradient(0, 0, 0, altura)
    gradiente.setColorAt(0.0, QColor("#1e1e2f"))
    gradiente.setColorAt(1.0, QColor("#2a2a4a"))
    pintor.setBrush(gradiente)
    pintor.setPen(Qt.NoPen)
    pintor.drawRoundedRect(0, 0, largura, altura, 20, 20)

    # Ícone
    fonte_icone = QFont()
    fonte_icone.setPointSize(40)
    pintor.setFont(fonte_icone)
    pintor.setPen(QColor("#5b8def"))
    pintor.drawText(pixmap.rect().adjusted(0, 40, 0, 0), Qt.AlignHCenter | Qt.AlignTop, "🛠")

    # Título
    fonte_titulo = QFont()
    fonte_titulo.setPointSize(22)
    fonte_titulo.setBold(True)
    pintor.setFont(fonte_titulo)
    pintor.setPen(QColor("#5b8def"))
    pintor.drawText(pixmap.rect().adjusted(0, 100, 0, 0), Qt.AlignHCenter | Qt.AlignTop, "AutoControl")

    # Subtítulo
    fonte_sub = QFont()
    fonte_sub.setPointSize(10)
    pintor.setFont(fonte_sub)
    pintor.setPen(QColor("#a0a0b8"))
    pintor.drawText(pixmap.rect().adjusted(0, 140, 0, 0), Qt.AlignHCenter | Qt.AlignTop, "Carregando o sistema...")

    pintor.end()
    return pixmap


def main():
    app = QApplication(sys.argv)

    splash = QSplashScreen(criar_splash_pixmap())
    splash.setWindowFlag(Qt.FramelessWindowHint)
    splash.show()

    app.processEvents()

    # Trabalho real de inicialização (garante que o banco existe)
    criar_tabelas()

    janela_login = TelaLogin()

    def abrir_login():
        janela_login.show()
        splash.finish(janela_login)

    # Mantém o splash visível por pelo menos 1.5s, mesmo se criar_tabelas() for rápido
    QTimer.singleShot(1500, abrir_login)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()