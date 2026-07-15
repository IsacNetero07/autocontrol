from PySide6.QtCore import Signal

from database.clientes_db import (
    salvar_cliente,
    listar_clientes,
    pesquisar_clientes,
    atualizar_cliente,
    excluir_cliente
)
from utils.validacao import validar_cpf
from views.components.tela_cadastro_base import TelaCadastroBase


class TelaClientes(TelaCadastroBase):

    cliente_cadastrado = Signal(int)

    titulo_tela = "Cadastro de Clientes"
    placeholder_pesquisa = "Pesquisar cliente..."
    mostrar_mensagem_salvar = False  # comportamento original: não avisa ao salvar
    campos_config = [
        ("nome", "Nome:"),
        ("cpf", "CPF:"),
        ("telefone", "Telefone:"),
        ("email", "Email:"),
        ("endereco", "Endereço:"),
    ]
    colunas_tabela = ["ID", "Nome", "CPF", "Telefone", "Email"]

    def funcao_salvar(self, **valores):
        return salvar_cliente(
            valores["nome"], valores["cpf"], valores["telefone"],
            valores["email"], valores["endereco"]
        )

    def funcao_listar(self):
        return listar_clientes()

    def funcao_pesquisar(self, texto):
        return pesquisar_clientes(texto)

    def funcao_atualizar(self, id_registro, **valores):
        atualizar_cliente(
            id_registro, valores["nome"], valores["cpf"],
            valores["telefone"], valores["email"], valores["endereco"]
        )

    def funcao_excluir(self, id_registro):
        excluir_cliente(id_registro)

    def validar(self, valores: dict) -> bool:
        if not super().validar(valores):
            return False

        return validar_cpf(self, "CPF", valores["cpf"])

    def after_salvar(self, resultado):
        self.cliente_cadastrado.emit(resultado)