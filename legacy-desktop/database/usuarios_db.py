import bcrypt
from database.database import conectar


def salvar_usuario(nome, usuario, senha, nivel):
    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO usuarios
        (nome, usuario, senha, nivel)
        VALUES (?, ?, ?, ?)
    """, (nome, usuario, senha_hash, nivel))

    conexao.commit()
    conexao.close()


def autenticar(usuario, senha):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, nivel, senha
        FROM usuarios
        WHERE usuario = ?
    """, (usuario,))

    resultado = cursor.fetchone()
    conexao.close()

    if not resultado:
        return None

    id_usuario, nome, nivel, senha_hash = resultado

    # senha_hash pode vir como bytes ou str dependendo do driver do banco
    if isinstance(senha_hash, str):
        senha_hash = senha_hash.encode("utf-8")

    if bcrypt.checkpw(senha.encode("utf-8"), senha_hash):
        return (id_usuario, nome, nivel)

    return None


def listar_usuarios():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, usuario, nivel
        FROM usuarios
        ORDER BY id DESC
    """)

    usuarios = cursor.fetchall()

    conexao.close()

    return usuarios


def excluir_usuario(id_usuario):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM usuarios
        WHERE id = ?
    """, (id_usuario,))

    conexao.commit()
    conexao.close()


def atualizar_senha(id_usuario, nova_senha):
    """
    Atualiza a senha de um usuário, salvando já como hash bcrypt.
    """
    senha_hash = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt())

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET senha = ?
        WHERE id = ?
    """, (senha_hash, id_usuario))

    conexao.commit()
    conexao.close()


def verificar_senha(id_usuario, senha):
    """
    Verifica se a senha informada bate com o hash salvo para esse usuário.
    Retorna True/False. Não usa o campo 'usuario' — só o id.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT senha FROM usuarios WHERE id = ?
    """, (id_usuario,))

    resultado = cursor.fetchone()
    conexao.close()

    if not resultado:
        return False

    senha_hash = resultado[0]

    if isinstance(senha_hash, str):
        senha_hash = senha_hash.encode("utf-8")

    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash)