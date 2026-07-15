from database.database import conectar


def salvar_veiculo(
    placa,
    marca,
    modelo,
    ano,
    cor,
    quilometragem,
    cliente_id
):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO veiculos
        (placa, marca, modelo, ano, cor, quilometragem, cliente_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        placa,
        marca,
        modelo,
        ano,
        cor,
        quilometragem,
        cliente_id
    ))

    conexao.commit()

    id_veiculo = cursor.lastrowid

    conexao.close()

    return id_veiculo


def listar_veiculos():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            veiculos.id,
            placa,
            marca,
            modelo,
            ano,
            nome
        FROM veiculos

        LEFT JOIN clientes
        ON clientes.id = veiculos.cliente_id

        ORDER BY veiculos.id DESC
    """)

    dados = cursor.fetchall()

    conexao.close()

    return dados


def listar_veiculos_por_cliente(id_cliente):
    """
    Retorna todos os veículos de um cliente específico.
    Usado para mostrar o histórico de veículos ao montar uma Ordem de Serviço.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            veiculos.id,
            placa,
            marca,
            modelo,
            ano,
            nome
        FROM veiculos
        LEFT JOIN clientes ON clientes.id = veiculos.cliente_id
        WHERE veiculos.cliente_id = ?
        ORDER BY veiculos.id DESC
    """, (id_cliente,))

    dados = cursor.fetchall()
    conexao.close()

    return dados


def obter_cliente_do_veiculo(id_veiculo):
    """
    Retorna o cliente_id associado a um veículo, ou None se não houver.
    Usado para pré-selecionar cliente + veículo ao abrir a Ordem de Serviço.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT cliente_id
        FROM veiculos
        WHERE id = ?
    """, (id_veiculo,))

    resultado = cursor.fetchone()

    conexao.close()

    if resultado:
        return resultado[0]

    return None


def veiculo_possui_vinculos(id_veiculo):
    """
    Verifica se o veículo tem ordens de serviço vinculadas.
    Retorna uma mensagem descrevendo o vínculo, ou None se não houver.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM ordens_servico WHERE veiculo_id = ?",
        (id_veiculo,)
    )
    total_ordens = cursor.fetchone()[0]

    conexao.close()

    if total_ordens == 0:
        return None

    return f"{total_ordens} ordem(ns) de serviço"


def excluir_veiculo(id_veiculo):
    vinculos = veiculo_possui_vinculos(id_veiculo)

    if vinculos is not None:
        raise ValueError(
            f"Não é possível excluir este veículo: ele possui {vinculos} vinculada(s). "
            "Exclua essas ordens de serviço primeiro."
        )

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM veiculos WHERE id = ?", (id_veiculo,))

    conexao.commit()
    conexao.close()


def atualizar_veiculo(
    id_veiculo,
    placa,
    marca,
    modelo,
    ano,
    cor,
    quilometragem,
    cliente_id
):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE veiculos
        SET placa = ?,
            marca = ?,
            modelo = ?,
            ano = ?,
            cor = ?,
            quilometragem = ?,
            cliente_id = ?
        WHERE id = ?
    """, (
        placa,
        marca,
        modelo,
        ano,
        cor,
        quilometragem,
        cliente_id,
        id_veiculo
    ))

    conexao.commit()
    conexao.close()