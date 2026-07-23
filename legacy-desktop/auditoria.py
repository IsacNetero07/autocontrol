from database.database import conectar


def auditar_clientes():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, cpf, telefone, email, endereco
        FROM clientes
        WHERE nome = '' OR cpf = '' OR telefone = '' OR email = '' OR endereco = ''
           OR nome IS NULL OR cpf IS NULL OR telefone IS NULL OR email IS NULL OR endereco IS NULL
    """)

    resultado = cursor.fetchall()
    conexao.close()
    return resultado


def auditar_veiculos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, placa, marca, modelo, ano, cor, quilometragem, cliente_id
        FROM veiculos
        WHERE placa = '' OR marca = '' OR modelo = '' OR ano = '' OR cor = '' OR quilometragem = ''
           OR placa IS NULL OR marca IS NULL OR modelo IS NULL OR ano IS NULL
           OR cor IS NULL OR quilometragem IS NULL OR cliente_id IS NULL
    """)

    resultado = cursor.fetchall()
    conexao.close()
    return resultado


def auditar_fornecedores():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, cnpj, telefone, email, endereco
        FROM fornecedores
        WHERE nome = '' OR cnpj = '' OR telefone = '' OR email = '' OR endereco = ''
           OR nome IS NULL OR cnpj IS NULL OR telefone IS NULL OR email IS NULL OR endereco IS NULL
    """)

    resultado = cursor.fetchall()
    conexao.close()
    return resultado


def auditar_estoque():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, categoria, quantidade, valor, fornecedor
        FROM estoque
        WHERE nome = '' OR categoria = '' OR quantidade = '' OR valor = '' OR fornecedor = ''
           OR nome IS NULL OR categoria IS NULL OR quantidade IS NULL
           OR valor IS NULL OR fornecedor IS NULL
    """)

    resultado = cursor.fetchall()
    conexao.close()
    return resultado


def imprimir_relatorio(titulo, dados, colunas):
    print(f"\n{'=' * 60}")
    print(f"{titulo} — {len(dados)} registro(s) incompleto(s)")
    print("=" * 60)

    if not dados:
        print("Nenhum problema encontrado. ✅")
        return

    for linha in dados:
        print(f"\nID {linha[0]}:")
        for nome_coluna, valor in zip(colunas, linha):
            marcador = " ⚠️ VAZIO" if (valor is None or valor == "") else ""
            print(f"  {nome_coluna}: {valor}{marcador}")


if __name__ == "__main__":
    print("Iniciando auditoria do banco de dados AutoControl...")

    imprimir_relatorio(
        "CLIENTES",
        auditar_clientes(),
        ["ID", "Nome", "CPF", "Telefone", "Email", "Endereço"]
    )

    imprimir_relatorio(
        "VEÍCULOS",
        auditar_veiculos(),
        ["ID", "Placa", "Marca", "Modelo", "Ano", "Cor", "Quilometragem", "Cliente ID"]
    )

    imprimir_relatorio(
        "FORNECEDORES",
        auditar_fornecedores(),
        ["ID", "Nome", "CNPJ", "Telefone", "Email", "Endereço"]
    )

    imprimir_relatorio(
        "ESTOQUE",
        auditar_estoque(),
        ["ID", "Nome", "Categoria", "Quantidade", "Valor", "Fornecedor"]
    )

    print(f"\n{'=' * 60}")
    print("Auditoria concluída.")
    print("=" * 60)