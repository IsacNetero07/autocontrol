import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.validacao import (
    cpf_valido,
    cnpj_valido,
)


class TestCpfValido:

    def test_cpf_valido_com_formatacao(self):
        assert cpf_valido("111.444.777-35") is True

    def test_cpf_valido_sem_formatacao(self):
        assert cpf_valido("11144477735") is True

    def test_cpf_todos_digitos_iguais_invalido(self):
        assert cpf_valido("111.111.111-11") is False

    def test_cpf_digito_verificador_errado(self):
        assert cpf_valido("111.444.777-36") is False

    def test_cpf_tamanho_errado(self):
        assert cpf_valido("123456789") is False

    def test_cpf_vazio_invalido(self):
        assert cpf_valido("") is False

    def test_cpf_com_letras_invalido(self):
        assert cpf_valido("abc.def.ghi-jk") is False


class TestCnpjValido:

    def test_cnpj_valido_com_formatacao(self):
        assert cnpj_valido("11.222.333/0001-81") is True

    def test_cnpj_valido_sem_formatacao(self):
        assert cnpj_valido("11222333000181") is True

    def test_cnpj_todos_digitos_iguais_invalido(self):
        assert cnpj_valido("11.111.111/1111-11") is False

    def test_cnpj_digito_verificador_errado(self):
        assert cnpj_valido("11.222.333/0001-82") is False

    def test_cnpj_tamanho_errado(self):
        assert cnpj_valido("123456") is False

    def test_cnpj_vazio_invalido(self):
        assert cnpj_valido("") is False