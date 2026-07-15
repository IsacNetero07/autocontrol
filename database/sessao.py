"""
Guarda os dados do usuário logado durante a execução do programa
(em memória — não persiste no banco). Permite que qualquer tela
registre logs de auditoria sem precisar receber o usuário por
parâmetro em cada construtor.
"""

_usuario_atual = {"id": None, "nome": None, "nivel": None}


def definir_usuario_logado(id_usuario, nome, nivel):
    _usuario_atual["id"] = id_usuario
    _usuario_atual["nome"] = nome
    _usuario_atual["nivel"] = nivel


def nome_usuario_atual() -> str:
    return _usuario_atual["nome"] or "Desconhecido"


def id_usuario_atual():
    return _usuario_atual["id"]