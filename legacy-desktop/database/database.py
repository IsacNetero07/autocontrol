import sys
import sqlite3
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

DB_PATH = BASE_DIR / "oficina.db"


def conectar():
    return sqlite3.connect(DB_PATH)


def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT,
        telefone TEXT,
        email TEXT,
        endereco TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS veiculos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        placa TEXT NOT NULL,
        marca TEXT,
        modelo TEXT,
        ano TEXT,
        cor TEXT,
        quilometragem TEXT,
        cliente_id INTEGER,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ordens_servico(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        veiculo_id INTEGER,
        mecanico TEXT,
        problema TEXT,
        servicos TEXT,
        status TEXT,
        valor_total REAL,
        data_entrada TEXT,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(veiculo_id) REFERENCES veiculos(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fornecedores(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cnpj TEXT,
        telefone TEXT,
        email TEXT,
        endereco TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT,
        quantidade INTEGER,
        valor REAL,
        fornecedor TEXT,
        fornecedor_id INTEGER,
        FOREIGN KEY(fornecedor_id) REFERENCES fornecedores(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        tipo TEXT NOT NULL,
        valor REAL NOT NULL,
        data TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        nivel TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS log_auditoria(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        acao TEXT NOT NULL,
        detalhes TEXT,
        data_hora TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        veiculo_id INTEGER,
        data TEXT NOT NULL,
        hora TEXT,
        descricao TEXT,
        status TEXT DEFAULT 'Agendado',
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(veiculo_id) REFERENCES veiculos(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fotos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entidade_tipo TEXT NOT NULL,
        entidade_id INTEGER NOT NULL,
        caminho TEXT NOT NULL,
        data_adicao TEXT
    )
    """)

    # Migrações para bancos já existentes (adiciona colunas novas sem apagar dados)
    try:
        cursor.execute(
            "ALTER TABLE estoque ADD COLUMN quantidade_minima INTEGER DEFAULT 5"
        )
    except sqlite3.OperationalError:
        pass  # coluna já existe

    try:
        cursor.execute(
            "ALTER TABLE estoque ADD COLUMN fornecedor_id INTEGER REFERENCES fornecedores(id)"
        )
    except sqlite3.OperationalError:
        pass  # coluna já existe

    # Índices para acelerar buscas e joins conforme o banco cresce
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_veiculos_cliente
        ON veiculos(cliente_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_veiculos_placa
        ON veiculos(placa)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ordens_cliente
        ON ordens_servico(cliente_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ordens_veiculo
        ON ordens_servico(veiculo_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ordens_status
        ON ordens_servico(status)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_agendamentos_data
        ON agendamentos(data)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_agendamentos_cliente
        ON agendamentos(cliente_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_estoque_fornecedor
        ON estoque(fornecedor_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_fotos_entidade
        ON fotos(entidade_tipo, entidade_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_financeiro_tipo_data
        ON financeiro(tipo, data)
    """)

    conexao.commit()
    conexao.close()


if __name__ == "__main__":
    criar_tabelas()
    print("Banco criado com sucesso!")