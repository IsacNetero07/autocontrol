from datetime import datetime
from database.database import conectar


def _converter_data_sql(campo):
    """Converte um campo dd/mm/aaaa em aaaa-mm-dd, usável dentro de strftime()."""
    return f"substr({campo},7,4) || '-' || substr({campo},4,2) || '-' || substr({campo},1,2)"


def total_clientes():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total = cursor.fetchone()[0]
    conexao.close()
    return total


def total_veiculos():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT COUNT(*) FROM veiculos")
    total = cursor.fetchone()[0]
    conexao.close()
    return total


def total_produtos():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT COUNT(*) FROM estoque")
    total = cursor.fetchone()[0]
    conexao.close()
    return total


def total_ordens_abertas():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM ordens_servico
        WHERE status != 'Finalizada'
    """)
    total = cursor.fetchone()[0]
    conexao.close()
    return total


def receita_mes():
    conexao = conectar()
    cursor = conexao.cursor()

    hoje = datetime.now()
    ano_mes = hoje.strftime("%Y-%m")

    cursor.execute(f"""
        SELECT COALESCE(SUM(valor), 0)
        FROM financeiro
        WHERE tipo = 'Receita'
          AND strftime('%Y-%m', {_converter_data_sql("data")}) = ?
    """, (ano_mes,))

    total = cursor.fetchone()[0]
    conexao.close()
    return total


def despesas_mes():
    conexao = conectar()
    cursor = conexao.cursor()

    hoje = datetime.now()
    ano_mes = hoje.strftime("%Y-%m")

    cursor.execute(f"""
        SELECT COALESCE(SUM(valor), 0)
        FROM financeiro
        WHERE tipo = 'Despesa'
          AND strftime('%Y-%m', {_converter_data_sql("data")}) = ?
    """, (ano_mes,))

    total = cursor.fetchone()[0]
    conexao.close()
    return total


def receita_por_mes(meses=6):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(f"""
        SELECT
            strftime('%Y-%m', {_converter_data_sql("data")}) AS mes,
            SUM(valor)
        FROM financeiro
        WHERE tipo = 'Receita'
        GROUP BY mes
        ORDER BY mes DESC
        LIMIT ?
    """, (meses,))

    dados = cursor.fetchall()
    conexao.close()
    return list(reversed(dados))


def ordens_por_mes(meses=6):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(f"""
        SELECT
            strftime('%Y-%m', {_converter_data_sql("data_entrada")}) AS mes,
            COUNT(*)
        FROM ordens_servico
        GROUP BY mes
        ORDER BY mes DESC
        LIMIT ?
    """, (meses,))

    dados = cursor.fetchall()
    conexao.close()
    return list(reversed(dados))


def ultimas_ordens():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            ordens_servico.id,
            clientes.nome,
            veiculos.placa,
            ordens_servico.status
        FROM ordens_servico
        LEFT JOIN clientes ON clientes.id = ordens_servico.cliente_id
        LEFT JOIN veiculos ON veiculos.id = ordens_servico.veiculo_id
        ORDER BY ordens_servico.id DESC
        LIMIT 5
    """)

    dados = cursor.fetchall()
    conexao.close()
    return dados


def estoque_baixo():
    """Retorna produtos cuja quantidade está no limite mínimo (ou abaixo)."""
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT nome, quantidade, COALESCE(quantidade_minima, 5) AS minimo
        FROM estoque
        WHERE quantidade <= COALESCE(quantidade_minima, 5)
        ORDER BY quantidade ASC
    """)

    dados = cursor.fetchall()
    conexao.close()
    return dados


def pesquisa_global(termo):
    termo_like = f"%{termo}%"

    conexao = conectar()
    cursor = conexao.cursor()

    resultados = {
        "clientes": [],
        "veiculos": [],
        "ordens": [],
        "produtos": []
    }

    cursor.execute("""
        SELECT id, nome FROM clientes WHERE nome LIKE ? LIMIT 10
    """, (termo_like,))
    resultados["clientes"] = cursor.fetchall()

    cursor.execute("""
        SELECT veiculos.id, placa, marca, modelo
        FROM veiculos
        WHERE placa LIKE ? OR marca LIKE ? OR modelo LIKE ?
        LIMIT 10
    """, (termo_like, termo_like, termo_like))
    resultados["veiculos"] = cursor.fetchall()

    cursor.execute("""
        SELECT os.id, clientes.nome, veiculos.placa, os.status
        FROM ordens_servico os
        LEFT JOIN clientes ON clientes.id = os.cliente_id
        LEFT JOIN veiculos ON veiculos.id = os.veiculo_id
        WHERE os.status LIKE ?
           OR os.problema LIKE ?
           OR clientes.nome LIKE ?
        LIMIT 10
    """, (termo_like, termo_like, termo_like))
    resultados["ordens"] = cursor.fetchall()

    cursor.execute("""
        SELECT id, nome, quantidade FROM estoque WHERE nome LIKE ? LIMIT 10
    """, (termo_like,))
    resultados["produtos"] = cursor.fetchall()

    conexao.close()
    return resultados