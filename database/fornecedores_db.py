from database.database import conectar


def salvar_fornecedor(nome, cnpj, telefone, email, endereco):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO fornecedores
        (nome, cnpj, telefone, email, endereco)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, cnpj, telefone, email, endereco))

    conexao.commit()
    conexao.close()


def listar_fornecedores():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, cnpj, telefone, email
        FROM fornecedores
        ORDER BY id DESC
    """)

    fornecedores = cursor.fetchall()

    conexao.close()

    return fornecedores


def pesquisar_fornecedores(nome):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, cnpj, telefone, email
        FROM fornecedores
        WHERE nome LIKE ?
        ORDER BY nome
    """, (f"%{nome}%",))

    fornecedores = cursor.fetchall()

    conexao.close()

    return fornecedores


def atualizar_fornecedor(id_fornecedor, nome, cnpj, telefone, email, endereco):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE fornecedores
        SET nome = ?,
            cnpj = ?,
            telefone = ?,
            email = ?,
            endereco = ?
        WHERE id = ?
    """, (nome, cnpj, telefone, email, endereco, id_fornecedor))

    conexao.commit()
    conexao.close()


def fornecedor_possui_vinculos(id_fornecedor):
    """
    Verifica se o fornecedor tem produtos vinculados no estoque.
    Retorna uma mensagem descrevendo o vínculo, ou None se não houver.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM estoque WHERE fornecedor_id = ?",
        (id_fornecedor,)
    )
    total_produtos = cursor.fetchone()[0]

    conexao.close()

    if total_produtos == 0:
        return None

    return f"{total_produtos} produto(s) no estoque"


def excluir_fornecedor(id_fornecedor):
    vinculos = fornecedor_possui_vinculos(id_fornecedor)

    if vinculos is not None:
        raise ValueError(
            f"Não é possível excluir este fornecedor: ele possui {vinculos} vinculado(s). "
            "Reatribua ou exclua esses produtos primeiro."
        )

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM fornecedores
        WHERE id = ?
    """, (id_fornecedor,))

    conexao.commit()
    conexao.close()