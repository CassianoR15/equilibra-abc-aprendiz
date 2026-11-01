
"""
Módulo principal de ETL do Equilibra.

Realiza leitura, padronização e validação dos dados.
A otimização só é liberada quando todas as verificações passam.
"""

from src.leitura import ler_planilha
from src.validacao import (
    validar_colunas,
    validar_dados_alunos,
    validar_dados_turmas,
    validar_capacidade_total
)
from src.padronizacao import padronizar_dados
from src.inconsistencias import identificar_inconsistencias
from src.recursos import cadastrar_turmas


def converter_erros(resultado):
    """Padroniza os diferentes formatos de retorno das validações."""

    if resultado is None:
        return []

    if isinstance(resultado, tuple):
        sucesso, mensagem = resultado

        if sucesso:
            return []

        if isinstance(mensagem, list):
            return [str(erro) for erro in mensagem]

        return [str(mensagem)]

    if isinstance(resultado, list):
        return [str(erro) for erro in resultado]

    if isinstance(resultado, dict):
        if resultado.get("sucesso", False):
            return []

        return [
            str(erro)
            for erro in resultado.get("erros", [])
        ]

    if isinstance(resultado, bool):
        return [] if resultado else ["Falha na validação dos dados."]

    return [str(resultado)]


def criar_retorno(
    status,
    mensagem,
    alunos=None,
    turmas=None,
    inconsistencias=None,
    erros=None
):
    return {
        "status": status,
        "mensagem": mensagem,
        "alunos": alunos,
        "turmas": turmas,
        "inconsistencias": inconsistencias,
        "erros": erros or []
    }


def main(arquivo):

    # 1. Leitura da planilha
    try:
        dados = ler_planilha(arquivo)

    except (ValueError, TypeError, OSError) as erro:
        return criar_retorno(
            "erro",
            "Não foi possível ler a planilha.",
            erros=[str(erro)]
        )

    # 2. Padronização
    try:
        dados = padronizar_dados(dados)

    except (ValueError, TypeError, KeyError) as erro:
        return criar_retorno(
            "erro",
            "Não foi possível padronizar os dados.",
            erros=[str(erro)]
        )

    alunos = dados["alunos"]
    configuracoes_turmas = dados["turmas"]

    # 3. Validação estrutural
    erros_colunas = converter_erros(
        validar_colunas(dados)
    )

    if erros_colunas:
        return criar_retorno(
            "erro",
            "Problemas na estrutura da planilha.",
            erros=erros_colunas
        )

    # 4. Identificação de inconsistências
    inconsistencias = identificar_inconsistencias(alunos)

    # 5. Validação dos alunos
    erros_alunos = converter_erros(
        validar_dados_alunos(alunos)
    )

    if erros_alunos or inconsistencias is not None:

        return criar_retorno(
            "inconsistencias",
            "Foram encontrados problemas nos dados. Corrija a planilha antes de continuar.",
            alunos=alunos,
            inconsistencias=inconsistencias,
            erros=erros_alunos
        )

    # 6. Validação das configurações das turmas
    erros_turmas = converter_erros(
        validar_dados_turmas(configuracoes_turmas)
    )

    if erros_turmas:
        return criar_retorno(
            "erro",
            "Existem problemas nas configurações das turmas.",
            alunos=alunos,
            erros=erros_turmas
        )

    # 7. Verificação da capacidade total
    erros_capacidade = converter_erros(
        validar_capacidade_total(
            alunos,
            configuracoes_turmas
        )
    )

    if erros_capacidade:
        return criar_retorno(
            "erro",
            "A capacidade total das turmas é insuficiente.",
            alunos=alunos,
            erros=erros_capacidade
        )

    # 8. Preparação das turmas
    resultado_turmas = cadastrar_turmas(
        configuracoes_turmas
    )

    if not resultado_turmas["sucesso"]:
        return criar_retorno(
            "erro",
            "Não foi possível preparar as turmas.",
            alunos=alunos,
            erros=resultado_turmas["erros"]
        )

    # 9. Liberação dos dados para otimização
    return criar_retorno(
        "sucesso",
        "Dados validados e preparados para otimização.",
        alunos=alunos,
        turmas=resultado_turmas["turmas"]
    )


def validar_planilha(arquivo):
    """Valida a planilha antes da execução da otimização."""
    return main(arquivo)
