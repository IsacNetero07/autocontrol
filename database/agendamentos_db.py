from database.database import conectar


def salvar_agendamento(cliente_id, veiculo_id, data, hora, descricao, status="Agendado"):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO agendamentos
        (cliente_id, veiculo_id, data, hora, descricao, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cliente_id, veiculo_id, data, hora, descricao, status))

    conexao.commit()

    id_agendamento = cursor.lastrowid

    conexao.close()

    return id_agendamento


def listar_agendamentos_por_data(data):
    """
    Retorna os agendamentos de um dia (formato dd/mm/aaaa).
    Cada item: (id, nome_cliente, placa, hora, descricao, status)
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            agendamentos.id,
            clientes.nome,
            veiculos.placa,
            agendamentos.hora,
            agendamentos.descricao,
            agendamentos.status

        FROM agendamentos

        LEFT JOIN clientes ON clientes.id = agendamentos.cliente_id
        LEFT JOIN veiculos ON veiculos.id = agendamentos.veiculo_id

        WHERE agendamentos.data = ?

        ORDER BY agendamentos.hora
    """, (data,))

    dados = cursor.fetchall()

    conexao.close()

    return dados


def listar_datas_com_agendamentos():
    """Retorna as datas (dd/mm/aaaa) que têm ao menos um agendamento."""
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT DISTINCT data
        FROM agendamentos
        WHERE data IS NOT NULL AND data != ''
    """)

    dados = cursor.fetchall()
    conexao.close()

    return [linha[0] for linha in dados]


def excluir_agendamento(id_agendamento):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM agendamentos WHERE id = ?", (id_agendamento,))

    conexao.commit()
    conexao.close()