from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class SideBar(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedWidth(220)

        self.setStyleSheet("""
            background-color:#1f2937;
        """)

        layout = QVBoxLayout()

        self.btn_dashboard = QPushButton("🏠 Dashboard")
        self.btn_clientes = QPushButton("👤 Clientes")
        self.btn_veiculos = QPushButton("🚗 Veículos")
        self.btn_ordem_servico = QPushButton("🔧 Ordem de Serviço")
        self.btn_agenda = QPushButton("📅 Agenda")
        self.btn_estoque = QPushButton("📦 Estoque")
        self.btn_fornecedores = QPushButton("🏭 Fornecedores")
        self.btn_financeiro = QPushButton("💰 Financeiro")
        self.btn_relatorios = QPushButton("📊 Relatórios")
        self.btn_usuarios = QPushButton("🧑‍🔧 Usuários")
        self.btn_log_auditoria = QPushButton("📝 Log de Auditoria")

        botoes = [
            self.btn_dashboard,
            self.btn_clientes,
            self.btn_veiculos,
            self.btn_ordem_servico,
            self.btn_agenda,
            self.btn_estoque,
            self.btn_fornecedores,
            self.btn_financeiro,
            self.btn_relatorios,
            self.btn_usuarios,
            self.btn_log_auditoria
        ]

        for botao in botoes:
            botao.setStyleSheet("""
                QPushButton{
                    color:white;
                    border:none;
                    text-align:left;
                    padding:15px;
                    font-size:15px;
                }

                QPushButton:hover{
                    background:#374151;
                }
            """)
            layout.addWidget(botao)

        layout.addStretch()
        self.setLayout(layout)