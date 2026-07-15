from database.database import conectar


def dados_relatorio_clientes():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT nome, cpf, telefone, email, endereco
        FROM clientes
        ORDER BY nome
    """)
    dados = cursor.fetchall()
    conexao.close()
    return dados


def dados_relatorio_veiculos():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT veiculos.placa, veiculos.marca, veiculos.modelo, veiculos.ano, clientes.nome
        FROM veiculos
        LEFT JOIN clientes ON clientes.id = veiculos.cliente_id
        ORDER BY veiculos.placa
    """)
    dados = cursor.fetchall()
    conexao.close()
    return dados


def dados_relatorio_ordens():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT os.id, clientes.nome, veiculos.placa, os.status, os.valor_total, os.data_entrada
        FROM ordens_servico os
        LEFT JOIN clientes ON clientes.id = os.cliente_id
        LEFT JOIN veiculos ON veiculos.id = os.veiculo_id
        ORDER BY os.id DESC
    """)
    dados = cursor.fetchall()
    conexao.close()
    return dados


def dados_relatorio_estoque():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT nome, categoria, quantidade, valor, fornecedor
        FROM estoque
        ORDER BY nome
    """)
    dados = cursor.fetchall()
    conexao.close()
    return dados


def dados_relatorio_financeiro():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT descricao, tipo, valor, data
        FROM financeiro
        ORDER BY data DESC
    """)
    dados = cursor.fetchall()
    conexao.close()
    return dados