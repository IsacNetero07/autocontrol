from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox
)

from database.usuarios_db import atualizar_senha, verificar_senha
from database.sessao import nome_usuario_atual
from database.log_db import registrar_log


class DialogTrocarSenha(QDialog):
    """Usado pelo próprio usuário logado para trocar a sua senha."""

    def __init__(self, id_usuario, parent=None):
        super().__init__(parent)

        self.id_usuario = id_usuario

        self.setWindowTitle("Trocar minha senha")
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)

        titulo = QLabel("🔑 Trocar minha senha")
        titulo.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(titulo)

        formulario = QFormLayout()

        self.senha_atual = QLineEdit()
        self.senha_atual.setEchoMode(QLineEdit.Password)

        self.senha_nova = QLineEdit()
        self.senha_nova.setEchoMode(QLineEdit.Password)

        self.senha_confirmar = QLineEdit()
        self.senha_confirmar.setEchoMode(QLineEdit.Password)

        formulario.addRow("Senha atual:", self.senha_atual)
        formulario.addRow("Nova senha:", self.senha_nova)
        formulario.addRow("Confirmar nova senha:", self.senha_confirmar)

        layout.addLayout(formulario)

        botoes = QHBoxLayout()

        self.botao_confirmar = QPushButton("Confirmar")
        self.botao_confirmar.setStyleSheet(
            "QPushButton{background:#2563EB;color:white;padding:8px;border-radius:8px;}"
        )
        self.botao_cancelar = QPushButton("Cancelar")

        botoes.addWidget(self.botao_confirmar)
        botoes.addWidget(self.botao_cancelar)
        layout.addLayout(botoes)

        self.botao_confirmar.clicked.connect(self.confirmar)
        self.botao_cancelar.clicked.connect(self.reject)

    def confirmar(self):
        atual = self.senha_atual.text()
        nova = self.senha_nova.text()
        confirmar = self.senha_confirmar.text()

        if atual == "" or nova == "" or confirmar == "":
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        if not verificar_senha(self.id_usuario, atual):
            QMessageBox.warning(self, "Erro", "Senha atual incorreta.")
            return

        if len(nova) < 4:
            QMessageBox.warning(self, "Erro", "A nova senha deve ter pelo menos 4 caracteres.")
            return

        if nova != confirmar:
            QMessageBox.warning(self, "Erro", "A confirmação não confere com a nova senha.")
            return

        atualizar_senha(self.id_usuario, nova)

        registrar_log(
            nome_usuario_atual(),
            "Trocar senha",
            "Usuário trocou a própria senha"
        )

        QMessageBox.information(self, "Sucesso", "Senha alterada com sucesso!")
        self.accept()


class DialogRedefinirSenha(QDialog):
    """Usado pelo admin para redefinir a senha de outro usuário, sem precisar da senha antiga."""

    def __init__(self, id_usuario, nome_usuario, parent=None):
        super().__init__(parent)

        self.id_usuario = id_usuario
        self.nome_usuario_alvo = nome_usuario

        self.setWindowTitle("Redefinir senha")
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)

        titulo = QLabel(f"🔑 Redefinir senha de {nome_usuario}")
        titulo.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(titulo)

        formulario = QFormLayout()

        self.senha_nova = QLineEdit()
        self.senha_nova.setEchoMode(QLineEdit.Password)

        self.senha_confirmar = QLineEdit()
        self.senha_confirmar.setEchoMode(QLineEdit.Password)

        formulario.addRow("Nova senha:", self.senha_nova)
        formulario.addRow("Confirmar nova senha:", self.senha_confirmar)

        layout.addLayout(formulario)

        botoes = QHBoxLayout()

        self.botao_confirmar = QPushButton("Confirmar")
        self.botao_confirmar.setStyleSheet(
            "QPushButton{background:#2563EB;color:white;padding:8px;border-radius:8px;}"
        )
        self.botao_cancelar = QPushButton("Cancelar")

        botoes.addWidget(self.botao_confirmar)
        botoes.addWidget(self.botao_cancelar)
        layout.addLayout(botoes)

        self.botao_confirmar.clicked.connect(self.confirmar)
        self.botao_cancelar.clicked.connect(self.reject)

    def confirmar(self):
        nova = self.senha_nova.text()
        confirmar = self.senha_confirmar.text()

        if nova == "" or confirmar == "":
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        if len(nova) < 4:
            QMessageBox.warning(self, "Erro", "A nova senha deve ter pelo menos 4 caracteres.")
            return

        if nova != confirmar:
            QMessageBox.warning(self, "Erro", "A confirmação não confere com a nova senha.")
            return

        atualizar_senha(self.id_usuario, nova)

        registrar_log(
            nome_usuario_atual(),
            "Redefinir senha",
            f"Redefiniu a senha de '{self.nome_usuario_alvo}' (ID {self.id_usuario})"
        )

        QMessageBox.information(self, "Sucesso", "Senha redefinida com sucesso!")
        self.accept()