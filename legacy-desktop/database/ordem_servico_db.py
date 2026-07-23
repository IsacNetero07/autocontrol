from database.database import conectar


def salvar_ordem(
    cliente_id,
    veiculo_id,
    mecanico,
    problema,
    servicos,
    status,
    valor_total,
    data_entrada
):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO ordens_servico
        (
            cliente_id,
            veiculo_id,
            mecanico,
            problema,
            servicos,
            status,
            valor_total,
            data_entrada
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cliente_id,
        veiculo_id,
        mecanico,
        problema,
        servicos,
        status,
        valor_total,
        data_entrada
    ))

    conexao.commit()
    conexao.close()


def listar_ordens():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            os.id,
            clientes.nome,
            veiculos.placa,
            os.status,
            os.valor_total,
            os.data_entrada

        FROM ordens_servico os

        LEFT JOIN clientes
            ON clientes.id = os.cliente_id

        LEFT JOIN veiculos
            ON veiculos.id = os.veiculo_id

        ORDER BY os.id DESC
    """)

    dados = cursor.fetchall()

    conexao.close()

    return dados


def ordens_por_data(data):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT os.id, clientes.nome, veiculos.placa, os.status
        FROM ordens_servico os
        LEFT JOIN clientes ON clientes.id = os.cliente_id
        LEFT JOIN veiculos ON veiculos.id = os.veiculo_id
        WHERE os.data_entrada = ?
    """, (data,))

    dados = cursor.fetchall()
    conexao.close()
    return dados


def listar_ordens_por_data(data):
    """
    Alias de ordens_por_data — mantido por compatibilidade com
    testes e código que use esse nome mais descritivo.
    """
    return ordens_por_data(data)


def listar_datas_com_ordens():
    """
    Retorna a lista de datas (dd/mm/aaaa) que têm ao menos uma
    ordem de serviço registrada. Útil para destacar dias com
    movimento num calendário/agenda.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT DISTINCT data_entrada
        FROM ordens_servico
        WHERE data_entrada IS NOT NULL AND data_entrada != ''
    """)

    dados = [linha[0] for linha in cursor.fetchall()]
    conexao.close()

    return dados


def listar_ordens_proximas(dias=7):
    """
    Retorna ordens de serviço com data de entrada nos próximos `dias`
    dias a partir de hoje, ignorando as que já estão Finalizadas.
    """
    from datetime import datetime, timedelta

    conexao = conectar()
    cursor = conexao.cursor()

    hoje = datetime.now()
    datas_permitidas = [
        (hoje + timedelta(days=i)).strftime("%d/%m/%Y")
        for i in range(dias + 1)
    ]

    marcadores = ",".join("?" for _ in datas_permitidas)

    cursor.execute(f"""
        SELECT
            os.id,
            clientes.nome,
            veiculos.placa,
            os.status,
            os.data_entrada
        FROM ordens_servico os
        LEFT JOIN clientes ON clientes.id = os.cliente_id
        LEFT JOIN veiculos ON veiculos.id = os.veiculo_id
        WHERE os.data_entrada IN ({marcadores})
          AND os.status != 'Finalizada'
        ORDER BY os.data_entrada
    """, datas_permitidas)

    dados = cursor.fetchall()
    conexao.close()

    return dados