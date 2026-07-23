import sys
import os
import sqlite3
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database.database as database_module
from database.database import criar_tabelas
from database.clientes_db import (
    salvar_cliente,
    listar_clientes,
    pesquisar_clientes,
    atualizar_cliente,
    excluir_cliente,
    cliente_possui_vinculos,
)
from database.veiculos_db import (
    salvar_veiculo,
    listar_veiculos,
    obter_cliente_do_veiculo,
    listar_veiculos_por_cliente,
    atualizar_veiculo,
    excluir_veiculo,
    veiculo_possui_vinculos,
)
from database.estoque_db import (
    salvar_produto,
    listar_produtos,
    listar_estoque_baixo,
)
from database.ordem_servico_db import (
    salvar_ordem,
    listar_ordens,
    listar_ordens_por_data,
    listar_datas_com_ordens,
    listar_ordens_proximas,
)
from database.usuarios_db import (
    salvar_usuario,
    autenticar,
    listar_usuarios,
    excluir_usuario,
    atualizar_senha,
    verificar_senha,
)


@pytest.fixture
def banco_temporario(tmp_path, monkeypatch):
    """
    Substitui o caminho do banco por um arquivo temporário só para
    este teste, garantindo que o oficina.db real nunca é tocado.
    """
    caminho_temp = tmp_path / "teste.db"
    monkeypatch.setattr(database_module, "DB_PATH", caminho_temp)

    criar_tabelas()

    yield caminho_temp


class TestClientesDb:

    def test_salvar_e_listar_cliente(self, banco_temporario):
        id_cliente = salvar_cliente("João Silva", "11144477735", "11999999999", "joao@email.com", "Rua A, 123")

        clientes = listar_clientes()

        assert len(clientes) == 1
        assert clientes[0][0] == id_cliente
        assert clientes[0][1] == "João Silva"

    def test_pesquisar_cliente_por_nome_parcial(self, banco_temporario):
        salvar_cliente("Maria Souza", "", "", "", "")
        salvar_cliente("João Silva", "", "", "", "")

        resultado = pesquisar_clientes("maria")

        assert len(resultado) == 1
        assert resultado[0][1] == "Maria Souza"

    def test_atualizar_cliente(self, banco_temporario):
        id_cliente = salvar_cliente("Nome Antigo", "11144477735", "", "", "")

        atualizar_cliente(id_cliente, "Nome Novo", "11144477735", "11988887777", "novo@email.com", "Rua B")

        clientes = listar_clientes()
        assert clientes[0][1] == "Nome Novo"

    def test_excluir_cliente_sem_vinculos(self, banco_temporario):
        id_cliente = salvar_cliente("Cliente Solto", "", "", "", "")

        excluir_cliente(id_cliente)

        assert listar_clientes() == []

    def test_excluir_cliente_com_veiculo_vinculado_deve_falhar(self, banco_temporario):
        id_cliente = salvar_cliente("Cliente com Carro", "", "", "", "")
        salvar_veiculo("ABC1234", "Toyota", "Corolla", "2022", "Preto", "10000", id_cliente)

        with pytest.raises(ValueError):
            excluir_cliente(id_cliente)

        assert len(listar_clientes()) == 1

    def test_cliente_possui_vinculos_retorna_none_se_nao_houver(self, banco_temporario):
        id_cliente = salvar_cliente("Cliente Livre", "", "", "", "")

        assert cliente_possui_vinculos(id_cliente) is None


class TestVeiculosDb:

    def test_salvar_e_listar_veiculo(self, banco_temporario):
        id_cliente = salvar_cliente("Dono do Carro", "", "", "", "")
        id_veiculo = salvar_veiculo("XYZ9999", "Honda", "Civic", "2021", "Prata", "20000", id_cliente)

        veiculos = listar_veiculos()

        assert len(veiculos) == 1
        assert veiculos[0][0] == id_veiculo
        assert veiculos[0][1] == "XYZ9999"
        assert veiculos[0][5] == "Dono do Carro"  # nome do cliente via JOIN

    def test_obter_cliente_do_veiculo(self, banco_temporario):
        id_cliente = salvar_cliente("Fulano", "", "", "", "")
        id_veiculo = salvar_veiculo("AAA1111", "Fiat", "Uno", "2015", "Branco", "50000", id_cliente)

        assert obter_cliente_do_veiculo(id_veiculo) == id_cliente

    def test_obter_cliente_de_veiculo_inexistente_retorna_none(self, banco_temporario):
        assert obter_cliente_do_veiculo(9999) is None

    def test_listar_veiculos_por_cliente(self, banco_temporario):
        id_cliente_1 = salvar_cliente("Cliente 1", "", "", "", "")
        id_cliente_2 = salvar_cliente("Cliente 2", "", "", "", "")

        salvar_veiculo("CAR0001", "Toyota", "Corolla", "2020", "Preto", "1000", id_cliente_1)
        salvar_veiculo("CAR0002", "Toyota", "Hilux", "2020", "Branco", "2000", id_cliente_1)
        salvar_veiculo("CAR0003", "Fiat", "Argo", "2020", "Vermelho", "3000", id_cliente_2)

        veiculos_cliente_1 = listar_veiculos_por_cliente(id_cliente_1)

        assert len(veiculos_cliente_1) == 2
        placas = [v[1] for v in veiculos_cliente_1]
        assert "CAR0001" in placas and "CAR0002" in placas
        assert "CAR0003" not in placas

    def test_atualizar_veiculo(self, banco_temporario):
        id_cliente = salvar_cliente("Cliente", "", "", "", "")
        id_veiculo = salvar_veiculo("OLD0001", "Ford", "Ka", "2018", "Azul", "40000", id_cliente)

        atualizar_veiculo(id_veiculo, "NEW0001", "Ford", "Ka", "2018", "Azul", "45000", id_cliente)

        veiculos = listar_veiculos()
        assert veiculos[0][1] == "NEW0001"

    def test_excluir_veiculo_sem_vinculos(self, banco_temporario):
        id_cliente = salvar_cliente("Cliente", "", "", "", "")
        id_veiculo = salvar_veiculo("SOLTO01", "Chevrolet", "Onix", "2019", "Cinza", "30000", id_cliente)

        excluir_veiculo(id_veiculo)

        assert listar_veiculos() == []

    def test_excluir_veiculo_com_os_vinculada_deve_falhar(self, banco_temporario):
        id_cliente = salvar_cliente("Cliente", "", "", "", "")
        id_veiculo = salvar_veiculo("COMOS001", "VW", "Gol", "2017", "Prata", "60000", id_cliente)

        salvar_ordem(id_cliente, id_veiculo, "Mecânico X", "Barulho no motor", "Revisão geral", "Aberta", "500", "15/07/2026")

        with pytest.raises(ValueError):
            excluir_veiculo(id_veiculo)

        assert len(listar_veiculos()) == 1

    def test_veiculo_possui_vinculos_retorna_none_se_nao_houver(self, banco_temporario):
        id_cliente = salvar_cliente("Cliente", "", "", "", "")
        id_veiculo = salvar_veiculo("LIVRE001", "Renault", "Kwid", "2022", "Vermelho", "5000", id_cliente)

        assert veiculo_possui_vinculos(id_veiculo) is None


class TestEstoqueDb:

    def test_salvar_e_listar_produto(self, banco_temporario):
        salvar_produto("Óleo 5W30", "Lubrificantes", "10", "45.90", "Fornecedor A", "5")

        produtos = listar_produtos()

        assert len(produtos) == 1
        assert produtos[0][1] == "Óleo 5W30"
        assert produtos[0][3] == 10  # quantidade
        assert produtos[0][6] == 5   # quantidade_minima

    def test_listar_estoque_baixo_detecta_produto_abaixo_do_minimo(self, banco_temporario):
        salvar_produto("Filtro de Óleo", "Filtros", "2", "20.00", "Fornecedor B", "5")
        salvar_produto("Pastilha de Freio", "Freios", "50", "80.00", "Fornecedor C", "10")

        baixo = listar_estoque_baixo()

        nomes_baixo = [item[1] for item in baixo]
        assert "Filtro de Óleo" in nomes_baixo
        assert "Pastilha de Freio" not in nomes_baixo

    def test_listar_estoque_baixo_no_limite_exato_conta_como_baixo(self, banco_temporario):
        salvar_produto("Vela de Ignição", "Ignição", "5", "15.00", "Fornecedor D", "5")

        baixo = listar_estoque_baixo()

        assert len(baixo) == 1
        assert baixo[0][1] == "Vela de Ignição"


class TestOrdemServicoDb:

    def test_salvar_e_listar_ordem(self, banco_temporario):
        id_cliente = salvar_cliente("Cliente OS", "", "", "", "")
        id_veiculo = salvar_veiculo("OS00001", "Toyota", "Etios", "2020", "Prata", "10000", id_cliente)

        salvar_ordem(id_cliente, id_veiculo, "Mecânico A", "Ruído na suspensão", "Troca de amortecedor", "Aberta", "350", "15/07/2026")

        ordens = listar_ordens()

        assert len(ordens) == 1
        assert ordens[0][1] == "Cliente OS"
        assert ordens[0][3] == "Aberta"

    def test_listar_ordens_por_data(self, banco_temporario):
        id_cliente = salvar_cliente("Cliente Data", "", "", "", "")
        id_veiculo = salvar_veiculo("DATA0001", "Fiat", "Mobi", "2021", "Branco", "5000", id_cliente)

        salvar_ordem(id_cliente, id_veiculo, "Mecânico B", "Revisão", "Troca de óleo", "Aberta", "200", "15/07/2026")
        salvar_ordem(id_cliente, id_veiculo, "Mecânico B", "Revisão", "Troca de óleo", "Aberta", "200", "16/07/2026")

        ordens_dia_15 = listar_ordens_por_data("15/07/2026")

        assert len(ordens_dia_15) == 1

    def test_listar_datas_com_ordens(self, banco_temporario):
        id_cliente = salvar_cliente("Cliente", "", "", "", "")
        id_veiculo = salvar_veiculo("DATAX001", "Hyundai", "HB20", "2020", "Preto", "8000", id_cliente)

        salvar_ordem(id_cliente, id_veiculo, "Mecânico", "Problema", "Serviço", "Aberta", "100", "20/07/2026")

        datas = listar_datas_com_ordens()

        assert "20/07/2026" in datas

    def test_listar_ordens_proximas_ignora_finalizadas(self, banco_temporario):
        from datetime import datetime, timedelta

        id_cliente = salvar_cliente("Cliente", "", "", "", "")
        id_veiculo = salvar_veiculo("PROX0001", "Nissan", "Kicks", "2022", "Azul", "3000", id_cliente)

        amanha = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")

        salvar_ordem(id_cliente, id_veiculo, "Mecânico", "Problema 1", "Serviço 1", "Aberta", "100", amanha)
        salvar_ordem(id_cliente, id_veiculo, "Mecânico", "Problema 2", "Serviço 2", "Finalizada", "100", amanha)

        proximas = listar_ordens_proximas(dias=1)

        assert len(proximas) == 1
        assert proximas[0][3] == "Aberta"


class TestUsuariosDb:

    def test_salvar_e_autenticar_usuario(self, banco_temporario):
        salvar_usuario("Isac", "isac", "senha123", "admin")

        resultado = autenticar("isac", "senha123")

        assert resultado is not None
        id_usuario, nome, nivel = resultado
        assert nome == "Isac"
        assert nivel == "admin"

    def test_autenticar_com_senha_errada_retorna_none(self, banco_temporario):
        salvar_usuario("Isac", "isac", "senha123", "admin")

        assert autenticar("isac", "senha_errada") is None

    def test_autenticar_usuario_inexistente_retorna_none(self, banco_temporario):
        assert autenticar("ninguem", "123") is None

    def test_listar_usuarios(self, banco_temporario):
        salvar_usuario("Mecânico Teste", "mecanico1", "123456", "mecanico")
        salvar_usuario("Provedor Teste", "provedor1", "123456", "provedor")

        usuarios = listar_usuarios()

        assert len(usuarios) == 2

    def test_excluir_usuario(self, banco_temporario):
        salvar_usuario("Descartavel", "temp", "123456", "mecanico")
        usuarios = listar_usuarios()
        id_usuario = usuarios[0][0]

        excluir_usuario(id_usuario)

        assert listar_usuarios() == []

    def test_atualizar_senha_e_verificar(self, banco_temporario):
        salvar_usuario("Isac", "isac", "senhaAntiga", "admin")
        usuarios = listar_usuarios()
        id_usuario = usuarios[0][0]

        atualizar_senha(id_usuario, "senhaNova")

        assert verificar_senha(id_usuario, "senhaNova") is True
        assert verificar_senha(id_usuario, "senhaAntiga") is False

    def test_login_funciona_apos_troca_de_senha(self, banco_temporario):
        salvar_usuario("Isac", "isac", "senhaAntiga", "admin")
        usuarios = listar_usuarios()
        id_usuario = usuarios[0][0]

        atualizar_senha(id_usuario, "senhaNova")

        assert autenticar("isac", "senhaNova") is not None
        assert autenticar("isac", "senhaAntiga") is None