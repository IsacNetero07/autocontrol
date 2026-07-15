from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QHBoxLayout,
    QAbstractItemView,
    QScrollArea
)
from PySide6.QtGui import QShortcut, QKeySequence

from utils.validacao import validar_obrigatorios
from utils.exportar import exportar_tabela_csv
from database.sessao import nome_usuario_atual
from database.log_db import registrar_log
from views.components.paginacao import PaginacaoWidget


class TelaCadastroBase(QWidget):
    """
    Classe base para telas de cadastro simples (formulário + pesquisa +
    tabela paginada + CRUD), como Clientes e Fornecedores.

    Cada subclasse define:
    - titulo_tela: texto do título (ex: "Cadastro de Clientes")
    - campos_config: lista de tuplas (chave, rótulo) na ordem do formulário
                      ex: [("nome", "Nome:"), ("cpf", "CPF:"), ...]
    - colunas_tabela: lista de rótulos das colunas da tabela
                      ex: ["ID", "Nome", "CPF", "Telefone", "Email"]
    - placeholder_pesquisa: texto do campo de busca
    - mostrar_mensagem_salvar: se True, mostra "Registro salvo!" ao salvar
                                (padrão True; Clientes usa False)
    - registros_por_pagina: quantos itens mostrar por página (padrão 20)

    E implementa os métodos de acesso ao banco:
    - funcao_salvar(**campos) -> None ou id do registro criado
    - funcao_listar() -> lista de tuplas
    - funcao_pesquisar(texto) -> lista de tuplas
    - funcao_atualizar(id, **campos) -> None
    - funcao_excluir(id) -> None

    Se precisar reagir depois de salvar (ex: emitir um Signal com o id
    criado), sobrescreva after_salvar(resultado).

    Atalhos de teclado incluídos: Ctrl+S (salvar), F5 (atualizar),
    Ctrl+F (focar na pesquisa).
    """

    titulo_tela = "Cadastro"
    campos_config = []       # [(chave, rótulo), ...]
    colunas_tabela = []      # ["ID", "Nome", ...]
    placeholder_pesquisa = "Pesquisar..."
    mostrar_mensagem_salvar = True
    registros_por_pagina = 20

    def __init__(self):
        super().__init__()

        self.id_selecionado = None
        self.campos = {}  # chave -> QLineEdit
        self.dados_completos = []  # lista completa (sem paginação) da última carga

        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        conteudo = QWidget()
        layout = QVBoxLayout(conteudo)

        titulo = QLabel(self.titulo_tela)
        titulo.setStyleSheet("font-size:26px; font-weight:bold;")
        layout.addWidget(titulo)

        # ---- Pesquisa ----
        pesquisa_layout = QHBoxLayout()
        self.pesquisa = QLineEdit()
        self.pesquisa.setPlaceholderText(self.placeholder_pesquisa)
        self.botao_pesquisar = QPushButton("Pesquisar")
        pesquisa_layout.addWidget(self.pesquisa)
        pesquisa_layout.addWidget(self.botao_pesquisar)
        layout.addLayout(pesquisa_layout)

        # ---- Formulário (gerado dinamicamente a partir de campos_config) ----
        formulario = QFormLayout()
        for chave, rotulo in self.campos_config:
            campo = QLineEdit()
            self.campos[chave] = campo
            formulario.addRow(rotulo, campo)
        layout.addLayout(formulario)

        # ---- Botões ----
        botoes = QHBoxLayout()
        self.botao_salvar = QPushButton("Salvar")
        self.botao_editar = QPushButton("Editar")
        self.botao_excluir = QPushButton("Excluir")
        self.botao_exportar = QPushButton("📤 Exportar CSV")

        self.botao_salvar.setToolTip("Ctrl+S")
        self.botao_salvar.setStyleSheet(
            "QPushButton{background:#2563EB;color:white;padding:10px;border-radius:8px;}"
        )
        self.botao_editar.setStyleSheet(
            "QPushButton{background:#F59E0B;color:white;padding:10px;border-radius:8px;}"
        )
        self.botao_excluir.setStyleSheet(
            "QPushButton{background:#DC2626;color:white;padding:10px;border-radius:8px;}"
        )

        botoes.addWidget(self.botao_salvar)
        botoes.addWidget(self.botao_editar)
        botoes.addWidget(self.botao_excluir)
        botoes.addWidget(self.botao_exportar)
        layout.addLayout(botoes)

        # ---- Tabela ----
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(len(self.colunas_tabela))
        self.tabela.setHorizontalHeaderLabels(self.colunas_tabela)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setMinimumHeight(200)
        self.tabela.setMaximumHeight(300)
        layout.addWidget(self.tabela)

        # ---- Paginação ----
        self.paginacao = PaginacaoWidget(tamanho_pagina=self.registros_por_pagina)
        self.paginacao.pagina_alterada.connect(self._renderizar_pagina_atual)
        layout.addWidget(self.paginacao)

        conteudo.setLayout(layout)
        scroll.setWidget(conteudo)
        layout_externo.addWidget(scroll)

        # ---- Conexões ----
        self.botao_salvar.clicked.connect(self.salvar)
        self.botao_pesquisar.clicked.connect(self.pesquisar)
        self.botao_editar.clicked.connect(self.editar)
        self.botao_excluir.clicked.connect(self.excluir)
        self.botao_exportar.clicked.connect(self.exportar_csv)
        self.tabela.cellClicked.connect(self.selecionar_linha)
        self.pesquisa.returnPressed.connect(self.pesquisar)

        self._configurar_atalhos()

        self.carregar_dados()

    # ==========================================================
    # Atalhos de teclado
    # ==========================================================

    def _configurar_atalhos(self):
        atalho_salvar = QShortcut(QKeySequence("Ctrl+S"), self)
        atalho_salvar.activated.connect(self.salvar)

        atalho_atualizar = QShortcut(QKeySequence("F5"), self)
        atalho_atualizar.activated.connect(self.carregar_dados)

        atalho_pesquisa = QShortcut(QKeySequence("Ctrl+F"), self)
        atalho_pesquisa.activated.connect(self._focar_pesquisa)

    def _focar_pesquisa(self):
        self.pesquisa.setFocus()
        self.pesquisa.selectAll()

    # ==========================================================
    # Métodos que a subclasse DEVE sobrescrever (acesso ao banco)
    # ==========================================================

    def funcao_salvar(self, **valores):
        raise NotImplementedError

    def funcao_listar(self):
        raise NotImplementedError

    def funcao_pesquisar(self, texto):
        raise NotImplementedError

    def funcao_atualizar(self, id_registro, **valores):
        raise NotImplementedError

    def funcao_excluir(self, id_registro):
        raise NotImplementedError

    # ==========================================================
    # Gancho opcional (ex: emitir Signal com o id criado)
    # ==========================================================

    def after_salvar(self, resultado):
        pass

    # ==========================================================
    # Lógica genérica (comum a todas as telas filhas)
    # ==========================================================

    def _identificador_principal(self, valores: dict) -> str:
        """Usa o primeiro campo (normalmente 'nome') como identificador nos logs."""
        if not self.campos_config:
            return ""
        primeira_chave = self.campos_config[0][0]
        return str(valores.get(primeira_chave, ""))

    def _renderizar_pagina_atual(self, _pagina=None):
        pagina_dados = self.paginacao.fatia_atual(self.dados_completos)

        self.tabela.setRowCount(len(pagina_dados))
        for linha, registro in enumerate(pagina_dados):
            for coluna, valor in enumerate(registro):
                self.tabela.setItem(linha, coluna, QTableWidgetItem(str(valor)))

    def preencher_tabela(self, dados, resetar_pagina=True):
        self.dados_completos = dados
        self.paginacao.definir_total(len(dados))

        if resetar_pagina:
            self.paginacao.resetar()

        self._renderizar_pagina_atual()

    def carregar_dados(self):
        self.preencher_tabela(self.funcao_listar())

    def pesquisar(self):
        texto = self.pesquisa.text().strip()
        if texto == "":
            self.carregar_dados()
            return
        self.preencher_tabela(self.funcao_pesquisar(texto))

    def selecionar_linha(self, linha, coluna):
        item_id = self.tabela.item(linha, 0)
        if item_id is None:
            return

        self.id_selecionado = int(item_id.text())

        for indice, (chave, _rotulo) in enumerate(self.campos_config):
            item = self.tabela.item(linha, indice + 1)
            if item is not None:
                self.campos[chave].setText(item.text())

    def obter_valores_formulario(self):
        return {
            chave: campo.text().strip()
            for chave, campo in self.campos.items()
        }

    def validar(self, valores: dict) -> bool:
        rotulos = {chave: rotulo.rstrip(":") for chave, rotulo in self.campos_config}
        return validar_obrigatorios(
            self,
            {rotulos[chave]: valor for chave, valor in valores.items()}
        )

    def salvar(self):
        valores = self.obter_valores_formulario()

        if not self.validar(valores):
            return

        resultado = self.funcao_salvar(**valores)

        registrar_log(
            nome_usuario_atual(),
            f"Criar - {self.titulo_tela}",
            self._identificador_principal(valores)
        )

        if self.mostrar_mensagem_salvar:
            QMessageBox.information(self, "Sucesso", "Registro salvo!")

        self.limpar_campos()
        self.carregar_dados()
        self.after_salvar(resultado)

    def editar(self):
        if self.id_selecionado is None:
            QMessageBox.warning(self, "Aviso", "Selecione um registro.")
            return

        valores = self.obter_valores_formulario()

        if not self.validar(valores):
            return

        self.funcao_atualizar(self.id_selecionado, **valores)

        registrar_log(
            nome_usuario_atual(),
            f"Editar - {self.titulo_tela}",
            f"ID {self.id_selecionado}: {self._identificador_principal(valores)}"
        )

        QMessageBox.information(self, "Sucesso", "Registro atualizado!")

        self.limpar_campos()
        self.carregar_dados()

    def excluir(self):
        if self.id_selecionado is None:
            QMessageBox.warning(self, "Aviso", "Selecione um registro.")
            return

        resposta = QMessageBox.question(
            self, "Excluir", "Deseja realmente excluir este registro?"
        )

        if resposta == QMessageBox.Yes:
            id_excluido = self.id_selecionado
            self.funcao_excluir(id_excluido)

            registrar_log(
                nome_usuario_atual(),
                f"Excluir - {self.titulo_tela}",
                f"ID {id_excluido}"
            )

            QMessageBox.information(self, "Sucesso", "Registro excluído!")
            self.limpar_campos()
            self.carregar_dados()

    def exportar_csv(self):
        """
        Exporta todos os registros (não só a página visível na tela),
        já que o CSV é pra uso externo, não é limitado pela paginação.
        """
        tabela_completa = QTableWidget()
        tabela_completa.setColumnCount(len(self.colunas_tabela))
        tabela_completa.setHorizontalHeaderLabels(self.colunas_tabela)
        tabela_completa.setRowCount(len(self.dados_completos))

        for linha, registro in enumerate(self.dados_completos):
            for coluna, valor in enumerate(registro):
                tabela_completa.setItem(linha, coluna, QTableWidgetItem(str(valor)))

        exportar_tabela_csv(
            self, tabela_completa,
            nome_sugerido=self.titulo_tela.lower().replace(" ", "_")
        )

    def limpar_campos(self):
        for campo in self.campos.values():
            campo.clear()
        self.id_selecionado = None