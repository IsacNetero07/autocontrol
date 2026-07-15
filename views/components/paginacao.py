from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal


class PaginacaoWidget(QWidget):
    """
    Widget de navegação entre páginas. Não busca dados sozinho —
    quem usa esse widget deve chamar definir_total(...) quando os
    dados mudarem, e escutar o sinal pagina_alterada para redesenhar
    a página pedida.
    """

    pagina_alterada = Signal(int)  # emite o novo número de página (0-indexado)

    def __init__(self, tamanho_pagina=20, parent=None):
        super().__init__(parent)

        self.tamanho_pagina = tamanho_pagina
        self.pagina_atual = 0
        self.total_registros = 0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)

        layout.addStretch()

        self.botao_anterior = QPushButton("← Anterior")
        self.botao_anterior.clicked.connect(self.pagina_anterior)
        layout.addWidget(self.botao_anterior)

        self.label_info = QLabel("Página 1 de 1")
        self.label_info.setStyleSheet("padding: 0 12px;")
        layout.addWidget(self.label_info)

        self.botao_proxima = QPushButton("Próxima →")
        self.botao_proxima.clicked.connect(self.proxima_pagina)
        layout.addWidget(self.botao_proxima)

        layout.addStretch()

        self._atualizar_botoes()

    def total_paginas(self) -> int:
        if self.total_registros == 0:
            return 1
        return (self.total_registros - 1) // self.tamanho_pagina + 1

    def definir_total(self, total_registros: int):
        """Chame sempre que o conjunto de dados mudar (nova busca, novo cadastro, etc.)."""
        self.total_registros = total_registros

        maximo = self.total_paginas() - 1
        if self.pagina_atual > maximo:
            self.pagina_atual = maximo

        self._atualizar_botoes()

    def resetar(self):
        """Volta para a primeira página (útil ao trocar de filtro/busca)."""
        self.pagina_atual = 0
        self._atualizar_botoes()

    def pagina_anterior(self):
        if self.pagina_atual > 0:
            self.pagina_atual -= 1
            self._atualizar_botoes()
            self.pagina_alterada.emit(self.pagina_atual)

    def proxima_pagina(self):
        if self.pagina_atual < self.total_paginas() - 1:
            self.pagina_atual += 1
            self._atualizar_botoes()
            self.pagina_alterada.emit(self.pagina_atual)

    def fatia_atual(self, lista):
        """Retorna só os itens da página atual, a partir da lista completa."""
        inicio = self.pagina_atual * self.tamanho_pagina
        fim = inicio + self.tamanho_pagina
        return lista[inicio:fim]

    def _atualizar_botoes(self):
        total = self.total_paginas()
        self.label_info.setText(f"Página {self.pagina_atual + 1} de {total}")
        self.botao_anterior.setEnabled(self.pagina_atual > 0)
        self.botao_proxima.setEnabled(self.pagina_atual < total - 1)