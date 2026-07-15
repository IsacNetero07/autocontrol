from database.fornecedores_db import (
    salvar_fornecedor,
    listar_fornecedores,
    pesquisar_fornecedores,
    atualizar_fornecedor,
    excluir_fornecedor
)
from utils.validacao import validar_cnpj
from views.components.tela_cadastro_base import TelaCadastroBase


class TelaFornecedores(TelaCadastroBase):

    titulo_tela = "Cadastro de Fornecedores"
    placeholder_pesquisa = "Pesquisar fornecedor..."
    campos_config = [
        ("nome", "Nome:"),
        ("cnpj", "CNPJ:"),
        ("telefone", "Telefone:"),
        ("email", "Email:"),
        ("endereco", "Endereço:"),
    ]
    colunas_tabela = ["ID", "Nome", "CNPJ", "Telefone", "Email"]

    def funcao_salvar(self, **valores):
        salvar_fornecedor(
            valores["nome"], valores["cnpj"], valores["telefone"],
            valores["email"], valores["endereco"]
        )

    def funcao_listar(self):
        return listar_fornecedores()

    def funcao_pesquisar(self, texto):
        return pesquisar_fornecedores(texto)

    def funcao_atualizar(self, id_registro, **valores):
        atualizar_fornecedor(
            id_registro, valores["nome"], valores["cnpj"],
            valores["telefone"], valores["email"], valores["endereco"]
        )

    def funcao_excluir(self, id_registro):
        excluir_fornecedor(id_registro)

    def validar(self, valores: dict) -> bool:
        if not super().validar(valores):
            return False

        return validar_cnpj(self, "CNPJ", valores["cnpj"])