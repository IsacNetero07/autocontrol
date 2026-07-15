from datetime import datetime
from database.database import conectar


def salvar_orcamento(
    cliente_id,
    veiculo_id,
    mecanico,
    problema,
    servicos_previstos,
    valor_estimado,
):
    conexao = conectar()
    cursor = conexao.cursor()

    data_criacao = datetime.now().strftime("%d/%m/%Y")

    cursor.execute("""
        INSERT INTO orcamentos
        (cliente_id, veiculo_id, mecanico, problema, servicos_previstos,
         valor_estimado, status, data_criacao)
        VALUES (?, ?, ?, ?, ?, ?, 'Pendente', ?)
    """, (
        cliente_id, veiculo_id, mecanico, problema,
        servicos_previstos, valor_estimado, data_criacao
    ))

    conexao.commit()
    orcamento_id = cursor.lastrowid
    conexao.close()
    return orcamento_id


def listar_orcamentos(status=None):
    """Lista orçamentos. Se status for informado, filtra (ex: 'Pendente')."""
    conexao = conectar()
    cursor = conexao.cursor()

    query = """
        SELECT
            orc.id, clientes.nome, veiculos.placa, orc.problema,
            orc.valor_estimado, orc.status, orc.data_criacao
        FROM orcamentos orc
        LEFT JOIN clientes ON clientes.id = orc.cliente_id
        LEFT JOIN veiculos ON veiculos.id = orc.veiculo_id
    """
    parametros = ()

    if status:
        query += " WHERE orc.status = ?"
        parametros = (status,)

    query += " ORDER BY orc.id DESC"

    cursor.execute(query, parametros)
    dados = cursor.fetchall()
    conexao.close()
    return dados


def buscar_orcamento(orcamento_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, cliente_id, veiculo_id, mecanico, problema,
               servicos_previstos, valor_estimado, status, data_criacao
        FROM orcamentos
        WHERE id = ?
    """, (orcamento_id,))

    dado = cursor.fetchone()
    conexao.close()
    return dado


def rejeitar_orcamento(orcamento_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "UPDATE orcamentos SET status = 'Rejeitado' WHERE id = ?",
        (orcamento_id,)
    )
    conexao.commit()
    conexao.close()


def excluir_orcamento(orcamento_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM orcamentos WHERE id = ?", (orcamento_id,))
    conexao.commit()
    conexao.close()


def aprovar_orcamento(orcamento_id):
    """
    Aprova um orçamento e gera a Ordem de Serviço correspondente.
    Retorna o id da nova OS.

    Levanta ValueError se o orçamento não existir ou já tiver sido processado.
    """
    orcamento = buscar_orcamento(orcamento_id)

    if orcamento is None:
        raise ValueError("Orçamento não encontrado.")

    (
        _id, cliente_id, veiculo_id, mecanico, problema,
        servicos_previstos, valor_estimado, status, _data_criacao
    ) = orcamento

    if status != "Pendente":
        raise ValueError(f"Este orçamento já está com status '{status}'.")

    data_entrada = datetime.now().strftime("%d/%m/%Y")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO ordens_servico
        (cliente_id, veiculo_id, mecanico, problema, servicos,
         status, valor_total, data_entrada)
        VALUES (?, ?, ?, ?, ?, 'Aberta', ?, ?)
    """, (
        cliente_id, veiculo_id, mecanico, problema,
        servicos_previstos, valor_estimado, data_entrada
    ))

    ordem_servico_id = cursor.lastrowid

    cursor.execute("""
        UPDATE orcamentos
        SET status = 'Aprovado', ordem_servico_id = ?
        WHERE id = ?
    """, (ordem_servico_id, orcamento_id))

    conexao.commit()
    conexao.close()

    return ordem_servico_id