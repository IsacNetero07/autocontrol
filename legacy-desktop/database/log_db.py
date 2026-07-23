from datetime import datetime
from database.database import conectar


def registrar_log(usuario, acao, detalhes=""):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO log_auditoria (usuario, acao, detalhes, data_hora)
        VALUES (?, ?, ?, ?)
    """, (
        usuario,
        acao,
        detalhes,
        datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ))

    conexao.commit()
    conexao.close()


def listar_logs(limite=300):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, usuario, acao, detalhes, data_hora
        FROM log_auditoria
        ORDER BY id DESC
        LIMIT ?
    """, (limite,))

    dados = cursor.fetchall()
    conexao.close()

    return dados