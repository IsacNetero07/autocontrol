from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QMessageBox,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSettings, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QLinearGradient, QPalette, QBrush

from database.usuarios_db import autenticar
from database.sessao import definir_usuario_logado
from database.log_db import registrar_log
from views.dashboard.dashboard import Dashboard


class TelaLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - AutoControl")
        self.resize(380, 480)

        self.settings = QSettings("AutoControl", "Login")

        self.aplicar_fundo_gradiente()
        self.montar_interface()
        self.carregar_usuario_lembrado()
        self.centralizar_janela()
        self.animar_entrada()

    # ---------- Fundo em gradiente ----------
    def aplicar_fundo_gradiente(self):
        gradiente = QLinearGradient(0, 0, 0, self.height())
        gradiente.setColorAt(0.0, QColor("#1e1e2f"))
        gradiente.setColorAt(1.0, QColor("#2a2a4a"))

        paleta = QPalette()
        paleta.setBrush(QPalette.Window, QBrush(gradiente))
        self.setAutoFillBackground(True)
        self.setPalette(paleta)

    def resizeEvent(self, event):
        self.aplicar_fundo_gradiente()
        super().resizeEvent(event)

    # ---------- Interface ----------
    def montar_interface(self):
        self.setStyleSheet("""
            QWidget {
                color: #f0f0f0;
                font-size: 14px;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 15);
                border: 1px solid #3d3d55;
                border-radius: 8px;
                padding: 10px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #5b8def;
                background-color: rgba(255, 255, 255, 25);
            }
            QPushButton#botaoEntrar {
                background-color: #5b8def;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton#botaoEntrar:hover {
                background-color: #4a75d1;
            }
            QPushButton#botaoEntrar:pressed {
                background-color: #3a63bd;
            }
            QPushButton#botaoOlho {
                background-color: transparent;
                border: none;
                font-size: 18px;
            }
            QCheckBox {
                color: #c0c0d8;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(45, 40, 45, 40)

        # ---------- Logo estilizado (sem imagem) ----------
        logo_container = QVBoxLayout()
        logo_container.setSpacing(4)

        icone = QLabel("🛠")
        icone.setAlignment(Qt.AlignCenter)
        icone.setStyleSheet("font-size: 42px;")
        logo_container.addWidget(icone)

        titulo = QLabel("AutoControl")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #5b8def;
        """)
        logo_container.addWidget(titulo)

        subtitulo = QLabel("Faça login para continuar")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("color: #a0a0b8; font-size: 12px;")
        logo_container.addWidget(subtitulo)

        layout.addLayout(logo_container)
        layout.addSpacing(10)

        # ---------- Campo usuário ----------
        label_usuario = QLabel("👤 Usuário")
        layout.addWidget(label_usuario)
        self.campo_usuario = QLineEdit()
        self.campo_usuario.setPlaceholderText("Digite seu usuário")
        layout.addWidget(self.campo_usuario)

        # ---------- Campo senha ----------
        label_senha = QLabel("🔒 Senha")
        layout.addWidget(label_senha)
        senha_layout = QHBoxLayout()

        self.campo_senha = QLineEdit()
        self.campo_senha.setPlaceholderText("Digite sua senha")
        self.campo_senha.setEchoMode(QLineEdit.Password)
        senha_layout.addWidget(self.campo_senha)

        self.botao_olho = QPushButton("👁")
        self.botao_olho.setObjectName("botaoOlho")
        self.botao_olho.setFixedWidth(32)
        self.botao_olho.setCheckable(True)
        self.botao_olho.clicked.connect(self.alternar_senha)
        senha_layout.addWidget(self.botao_olho)

        layout.addLayout(senha_layout)

        # ---------- Lembrar usuário ----------
        self.checkbox_lembrar = QCheckBox("Lembrar usuário")
        layout.addWidget(self.checkbox_lembrar)

        # ---------- Botão Entrar ----------
        self.botao_entrar = QPushButton("Entrar")
        self.botao_entrar.setObjectName("botaoEntrar")
        self.botao_entrar.setCursor(Qt.PointingHandCursor)

        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(20)
        sombra.setColor(QColor(91, 141, 239, 160))
        sombra.setOffset(0, 4)
        self.botao_entrar.setGraphicsEffect(sombra)

        layout.addWidget(self.botao_entrar)

        # ---------- Rodapé ----------
        rodape = QLabel("AutoControl © 2026")
        rodape.setAlignment(Qt.AlignCenter)
        rodape.setStyleSheet("color: #6a6a85; font-size: 10px;")
        layout.addWidget(rodape)

        self.setLayout(layout)

        # ---------- Conexões ----------
        self.botao_entrar.clicked.connect(self.fazer_login)
        self.campo_usuario.returnPressed.connect(self.fazer_login)
        self.campo_senha.returnPressed.connect(self.fazer_login)

    # ---------- Animação de entrada ----------
    def animar_entrada(self):
        self.setWindowOpacity(0)
        self.animacao = QPropertyAnimation(self, b"windowOpacity")
        self.animacao.setDuration(500)
        self.animacao.setStartValue(0)
        self.animacao.setEndValue(1)
        self.animacao.setEasingCurve(QEasingCurve.InOutQuad)
        self.animacao.start()

    # ---------- Funções auxiliares ----------
    def alternar_senha(self):
        if self.botao_olho.isChecked():
            self.campo_senha.setEchoMode(QLineEdit.Normal)
            self.botao_olho.setText("🙈")
        else:
            self.campo_senha.setEchoMode(QLineEdit.Password)
            self.botao_olho.setText("👁")

    def centralizar_janela(self):
        tela = self.screen().availableGeometry()
        x = (tela.width() - self.width()) // 2
        y = (tela.height() - self.height()) // 2
        self.move(x, y)

    def carregar_usuario_lembrado(self):
        usuario_salvo = self.settings.value("usuario_lembrado", "")
        if usuario_salvo:
            self.campo_usuario.setText(usuario_salvo)
            self.checkbox_lembrar.setChecked(True)

    def salvar_usuario_lembrado(self, usuario):
        if self.checkbox_lembrar.isChecked():
            self.settings.setValue("usuario_lembrado", usuario)
        else:
            self.settings.setValue("usuario_lembrado", "")

    def fazer_login(self):
        usuario = self.campo_usuario.text()
        senha = self.campo_senha.text()

        dados = autenticar(usuario, senha)

        if dados:
            id_usuario, nome, nivel = dados

            definir_usuario_logado(id_usuario, nome, nivel)
            registrar_log(nome, "Login", f"Usuário '{usuario}' entrou no sistema")

            self.salvar_usuario_lembrado(usuario)
            self.dashboard = Dashboard(nivel, id_usuario=id_usuario, nome_usuario=nome)
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.warning(
                self,
                "Erro",
                "Usuário ou senha inválidos."
            )