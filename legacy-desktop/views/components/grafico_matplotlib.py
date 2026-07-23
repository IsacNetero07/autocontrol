from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class GraficoBarras(QWidget):

    CORES_CLARO = {
        "fundo": "#F8FAFC",
        "texto_titulo": "#1E293B",
        "eixos": "#374151",
    }

    CORES_ESCURO = {
        "fundo": "#1E293B",
        "texto_titulo": "#F1F5F9",
        "eixos": "#CBD5E1",
    }

    def __init__(self, titulo="", cor="#3B82F6", compacto=False):
        super().__init__()

        self.cor = cor
        self.titulo = titulo
        self.modo_escuro = False

        self.ultimos_labels = []
        self.ultimos_valores = []

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        tamanho = (4, 2.3) if compacto else (6, 3.5)
        self.figure = Figure(figsize=tamanho, dpi=90)

        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)

        self.aplicar_tema(escuro=False)

    def atualizar(self, labels, valores):
        self.ultimos_labels = labels
        self.ultimos_valores = valores
        self._desenhar()

    def aplicar_tema(self, escuro: bool):
        self.modo_escuro = escuro
        cores = self.CORES_ESCURO if escuro else self.CORES_CLARO

        self.figure.patch.set_facecolor(cores["fundo"])
        self.ax.set_facecolor(cores["fundo"])

        self._cores_atuais = cores
        self._desenhar()

    def _desenhar(self):
        cores = getattr(self, "_cores_atuais", self.CORES_CLARO)

        self.ax.clear()
        self.ax.set_facecolor(cores["fundo"])

        self.ax.bar(self.ultimos_labels, self.ultimos_valores, color=self.cor)
        self.ax.set_title(
            self.titulo, fontsize=11, fontweight="bold", color=cores["texto_titulo"]
        )
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_color(cores["eixos"])
        self.ax.spines["bottom"].set_color(cores["eixos"])
        self.ax.tick_params(axis="x", rotation=30, labelsize=8, colors=cores["eixos"])
        self.ax.tick_params(axis="y", labelsize=8, colors=cores["eixos"])

        self.figure.tight_layout()
        self.canvas.draw()