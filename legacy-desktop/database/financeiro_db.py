from database.database import conectar


def salvar_movimento(descricao, tipo, valor, data):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO financeiro
        (descricao, tipo, valor, data)
        VALUES (?, ?, ?, ?)
    """, (descricao, tipo, valor, data))

    conexao.commit()
    conexao.close()


def listar_movimentos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            descricao,
            tipo,
            valor,
            data
        FROM financeiro
        ORDER BY id DESC
    """)

    dados = cursor.fetchall()

    conexao.close()

    return dados


def total_receitas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(valor), 0)
        FROM financeiro
        WHERE tipo = 'Receita'
    """)

    total = cursor.fetchone()[0]

    conexao.close()

    return total


def total_despesas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(valor), 0)
        FROM financeiro
        WHERE tipo = 'Despesa'
    """)

    total = cursor.fetchone()[0]

    conexao.close()

    return total


def total_lucro():
    return total_receitas() - total_despesas()