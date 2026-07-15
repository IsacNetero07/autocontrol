import shutil
import uuid
from datetime import datetime
from pathlib import Path

from database.database import conectar, DB_PATH


def _pasta_anexos(entidade_tipo, entidade_id):
    pasta = DB_PATH.parent / "anexos" / entidade_tipo / str(entidade_id)
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def adicionar_foto(entidade_tipo, entidade_id, caminho_origem):
    caminho_origem = Path(caminho_origem)
    pasta_destino = _pasta_anexos(entidade_tipo, entidade_id)

    extensao = caminho_origem.suffix
    nome_unico = f"{uuid.uuid4().hex}{extensao}"
    destino = pasta_destino / nome_unico

    shutil.copy2(caminho_origem, destino)

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        INSERT INTO fotos (entidade_tipo, entidade_id, caminho, data_adicao)
        VALUES (?, ?, ?, ?)
    """, (
        entidade_tipo,
        entidade_id,
        str(destino),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conexao.commit()
    conexao.close()

    return destino


def listar_fotos(entidade_tipo, entidade_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT id, caminho
        FROM fotos
        WHERE entidade_tipo = ? AND entidade_id = ?
        ORDER BY id DESC
    """, (entidade_tipo, entidade_id))
    dados = cursor.fetchall()
    conexao.close()
    return dados


def excluir_foto(foto_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT caminho FROM fotos WHERE id = ?", (foto_id,))
    resultado = cursor.fetchone()

    if resultado:
        caminho = Path(resultado[0])
        if caminho.exists():
            caminho.unlink()

    cursor.execute("DELETE FROM fotos WHERE id = ?", (foto_id,))
    conexao.commit()
    conexao.close()