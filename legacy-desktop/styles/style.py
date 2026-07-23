def botao_azul():
    return """
    QPushButton{
        background:#2563EB;
        color:white;
        border:none;
        border-radius:10px;
        padding:12px;
        font-size:15px;
        font-weight:bold;
    }

    QPushButton:hover{
        background:#1D4ED8;
    }

    QPushButton:pressed{
        background:#1E40AF;
    }
    """


def titulo():
    return """
    font-size:26px;
    font-weight:bold;
    """


def tabela():
    return """
    QHeaderView::section{
        background:#2563EB;
        color:white;
        font-weight:bold;
        padding:8px;
        border:none;
    }

    QTableWidget{
        gridline-color:#D1D5DB;
        font-size:13px;
        alternate-background-color:#F3F4F6;
    }
    """


def estilo_titulo():
    return """
    font-size:26px;
    font-weight:bold;
    """


def tema_claro():
    return """
    QWidget {
        background: #F8FAFC;
        color: #111827;
    }

    QMainWindow, QWidget#areaCentral {
        background: #F8FAFC;
    }

    QWidget#homeArea {
        background: #F8FAFC;
    }

    QLabel#homeTitulo {
        color: #1E293B;
    }

    QFrame#card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
    }

    QLabel#cardTitulo {
        color: #6B7280;
    }

    QLabel#cardValor {
        color: #1E293B;
    }

    QLineEdit, QComboBox {
        background: white;
        color: #111827;
        border: 1px solid #D1D5DB;
        border-radius: 6px;
        padding: 6px;
    }

    QLineEdit:focus, QComboBox:focus {
        border: 1px solid #3B82F6;
        background: white;
    }

    QComboBox QAbstractItemView {
        background: white;
        color: #111827;
        selection-background-color: #DBEAFE;
    }

    QTableWidget {
        background: white;
        color: #111827;
        gridline-color: #D1D5DB;
        alternate-background-color: #F3F4F6;
    }

    QWidget#topBar {
        background: white;
        border-bottom: 1px solid #D1D5DB;
    }

    QLabel#topBarTitulo {
        color: #1E293B;
    }

    QLabel#topBarUsuario {
        color: #374151;
    }

    QPushButton#botaoTopBar {
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        font-size: 16px;
        background: white;
    }

    QPushButton#botaoTopBar:hover {
        background: #F3F4F6;
    }
    """


def tema_escuro():
    return """
    QWidget {
        background: #0F172A;
        color: #E2E8F0;
    }

    QMainWindow, QWidget#areaCentral {
        background: #0F172A;
    }

    QWidget#homeArea {
        background: #0F172A;
    }

    QLabel#homeTitulo {
        color: #F1F5F9;
    }

    QFrame#card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
    }

    QLabel#cardTitulo {
        color: #94A3B8;
    }

    QLabel#cardValor {
        color: #F1F5F9;
    }

    QLineEdit, QComboBox {
        background: #1E293B;
        color: #E2E8F0;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 6px;
    }

    QLineEdit:focus, QComboBox:focus {
        border: 1px solid #3B82F6;
        background: #1E293B;
    }

    QComboBox QAbstractItemView {
        background: #1E293B;
        color: #E2E8F0;
        selection-background-color: #334155;
    }

    QTableWidget {
        background: #1E293B;
        color: #E2E8F0;
        gridline-color: #334155;
        alternate-background-color: #273449;
    }

    QWidget#topBar {
        background: #1E293B;
        border-bottom: 1px solid #334155;
    }

    QLabel#topBarTitulo {
        color: #F1F5F9;
    }

    QLabel#topBarUsuario {
        color: #CBD5E1;
    }

    QPushButton#botaoTopBar {
        border: 1px solid #334155;
        border-radius: 8px;
        font-size: 16px;
        background: #1E293B;
        color: #E2E8F0;
    }

    QPushButton#botaoTopBar:hover {
        background: #334155;
    }
    """