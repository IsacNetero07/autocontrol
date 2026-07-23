from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Signal


class TopBar(QWidget):

    pesquisar = Signal(str)
    alternar_tema = Signal()
    fazer_backup = Signal()
    restaurar_backup = Signal()
    abrir_notificacoes = Signal()
    trocar_senha = Signal()

    def __init__(self, nome_usuario="Usuário"):
        super().__init__()

        self.setObjectName("topBar")
        self.setFixedHeight(60)

        layout = QHBoxLayout()

        titulo = QLabel("🚗 AutoControl")
        titulo.setObjectName("topBarTitulo")
        titulo.setStyleSheet("font-size:22px; font-weight:bold;")

        self.busca = QLineEdit()
        self.busca.setPlaceholderText("🔍 Pesquisar cliente, veículo, ordem ou produto...")
        self.busca.setFixedWidth(350)
        self.busca.setFixedHeight(36)
        self.busca.setStyleSheet("""
            QLineEdit {
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
            }
        """)
        self.busca.returnPressed.connect(self.disparar_pesquisa)

        self.botao_backup = QPushButton("💾")
        self.botao_backup.setObjectName("botaoTopBar")
        self.botao_backup.setToolTip("Fazer backup do banco de dados")
        self.botao_backup.setFixedSize(36, 36)
        self.botao_backup.clicked.connect(self.fazer_backup.emit)

        self.botao_restaurar = QPushButton("📂")
        self.botao_restaurar.setObjectName("botaoTopBar")
        self.botao_restaurar.setToolTip("Restaurar backup")
        self.botao_restaurar.setFixedSize(36, 36)
        self.botao_restaurar.clicked.connect(self.restaurar_backup.emit)

        self.botao_notificacoes = QPushButton("🔔")
        self.botao_notificacoes.setObjectName("botaoTopBar")
        self.botao_notificacoes.setToolTip("Ver alertas de estoque baixo e serviços agendados")
        self.botao_notificacoes.setFixedHeight(36)
        self.botao_notificacoes.clicked.connect(self.abrir_notificacoes.emit)

        self.botao_tema = QPushButton("🌙")
        self.botao_tema.setObjectName("botaoTopBar")
        self.botao_tema.setFixedSize(36, 36)
        self.botao_tema.clicked.connect(self.alternar_tema.emit)

        usuario = QLabel(f"👤 {nome_usuario}")
        usuario.setObjectName("topBarUsuario")
        usuario.setStyleSheet("font-size:16px;")

        self.botao_trocar_senha = QPushButton("🔑")
        self.botao_trocar_senha.setObjectName("botaoTopBar")
        self.botao_trocar_senha.setToolTip("Trocar minha senha")
        self.botao_trocar_senha.setFixedSize(32, 32)
        self.botao_trocar_senha.clicked.connect(self.trocar_senha.emit)

        layout.addWidget(titulo)
        layout.addStretch()
        layout.addWidget(self.busca)
        layout.addStretch()
        layout.addWidget(self.botao_backup)
        layout.addWidget(self.botao_restaurar)
        layout.addWidget(self.botao_notificacoes)
        layout.addWidget(self.botao_tema)
        layout.addWidget(usuario)
        layout.addWidget(self.botao_trocar_senha)

        self.setLayout(layout)

    def disparar_pesquisa(self):
        termo = self.busca.text().strip()
        if termo:
            self.pesquisar.emit(termo)

    def atualizar_notificacoes(self, quantidade):
        if quantidade > 0:
            self.botao_notificacoes.setText(f"🔔 {quantidade}")
        else:
            self.botao_notificacoes.setText("🔔")