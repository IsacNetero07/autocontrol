from database.database import conectar


def salvar_produto(nome, categoria, quantidade, valor, fornecedor_id, quantidade_minima=5):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO estoque
        (nome, categoria, quantidade, valor, fornecedor_id, quantidade_minima)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        nome,
        categoria,
        quantidade,
        valor,
        fornecedor_id,
        quantidade_minima
    ))

    conexao.commit()
    conexao.close()


def listar_produtos():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            estoque.id,
            estoque.nome,
            estoque.categoria,
            estoque.quantidade,
            estoque.valor,
            fornecedores.nome,
            estoque.quantidade_minima
        FROM estoque
        LEFT JOIN fornecedores
            ON fornecedores.id = estoque.fornecedor_id
        ORDER BY estoque.id DESC
    """)

    dados = cursor.fetchall()

    conexao.close()

    return dados


def listar_estoque_baixo():
    """
    Retorna os produtos cuja quantidade está no nível mínimo ou abaixo.
    Cada item: (id, nome, quantidade, quantidade_minima)
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, quantidade, quantidade_minima
        FROM estoque
        WHERE CAST(quantidade AS INTEGER) <= CAST(quantidade_minima AS INTEGER)
        ORDER BY nome
    """)

    dados = cursor.fetchall()

    conexao.close()

    return dados