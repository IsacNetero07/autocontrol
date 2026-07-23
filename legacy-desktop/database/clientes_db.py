from database.database import conectar


def salvar_cliente(nome, cpf, telefone, email, endereco):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO clientes
        (nome, cpf, telefone, email, endereco)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, cpf, telefone, email, endereco))

    conexao.commit()

    id_cliente = cursor.lastrowid

    conexao.close()

    return id_cliente


def listar_clientes():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, cpf, telefone, email
        FROM clientes
        ORDER BY id DESC
    """)

    clientes = cursor.fetchall()

    conexao.close()

    return clientes


def pesquisar_clientes(nome):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, cpf, telefone, email
        FROM clientes
        WHERE nome LIKE ?
        ORDER BY nome
    """, (f"%{nome}%",))

    clientes = cursor.fetchall()

    conexao.close()

    return clientes


def atualizar_cliente(id_cliente, nome, cpf, telefone, email, endereco):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE clientes
        SET nome = ?,
            cpf = ?,
            telefone = ?,
            email = ?,
            endereco = ?
        WHERE id = ?
    """, (nome, cpf, telefone, email, endereco, id_cliente))

    conexao.commit()
    conexao.close()


def cliente_possui_vinculos(id_cliente):
    """
    Verifica se o cliente tem veículos ou ordens de serviço vinculados.
    Retorna uma mensagem descrevendo os vínculos, ou None se não houver nenhum.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM veiculos WHERE cliente_id = ?",
        (id_cliente,)
    )
    total_veiculos = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM ordens_servico WHERE cliente_id = ?",
        (id_cliente,)
    )
    total_ordens = cursor.fetchone()[0]

    conexao.close()

    if total_veiculos == 0 and total_ordens == 0:
        return None

    partes = []
    if total_veiculos > 0:
        partes.append(f"{total_veiculos} veículo(s)")
    if total_ordens > 0:
        partes.append(f"{total_ordens} ordem(ns) de serviço")

    return " e ".join(partes)


def excluir_cliente(id_cliente):
    vinculos = cliente_possui_vinculos(id_cliente)

    if vinculos is not None:
        raise ValueError(
            f"Não é possível excluir este cliente: ele possui {vinculos} vinculado(s). "
            "Exclua ou reatribua esses registros primeiro."
        )

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM clientes
        WHERE id = ?
    """, (id_cliente,))

    conexao.commit()
    conexao.close()