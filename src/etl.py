
"""
Módulo principal de ETL do Equilibra.

Integra a leitura, padronização, validação e preparação dos dados
das abas Alunos e Turmas.

O processamento só é concluído quando os dados estruturais estão
válidos e a capacidade total das turmas é suficiente para atender
a quantidade de alunos.

As inconsistências de cadastro são apresentadas em relatório.
Nenhum aluno é excluído automaticamente.
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
    """
    Converte diferentes formatos de retorno das validações
    em uma lista de mensagens de erro.
    """
    if resultado is None:
        return []

    if isinstance(resultado, tuple):
        sucesso, mensagem = resultado

        if sucesso:
            return []

        if isinstance(mensagem, list):
            return mensagem

        return [str(mensagem)]

    if isinstance(resultado, list):
        return [str(erro) for erro in resultado]

    if isinstance(resultado, dict):
        if resultado.get("sucesso", False):
            return []

        erros = resultado.get("erros", [])
        return [str(erro) for erro in erros]

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
    """Padroniza o retorno do processamento do ETL."""
    return {
        "status": status,
        "mensagem": mensagem,
        "alunos": alunos,
        "turmas": turmas,
        "inconsistencias": inconsistencias,
        "erros": erros or []
    }


def main(arquivo):
    """
    Executa o fluxo completo de ETL.

    Parâmetros:
        arquivo: caminho ou objeto do arquivo Excel.

    Retorno:
        Dicionário contendo o status do processamento,
        os dados preparados, inconsistências e erros.
    """

    # 1. Leitura das duas abas
    try:
        dados = ler_planilha(arquivo)

    except (ValueError, TypeError, OSError) as erro:
        return criar_retorno(
            "erro",
            "Não foi possível ler a planilha.",
            erros=[str(erro)]
        )

    # 2. Padronização dos dados
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

    # 3. Validação estrutural das colunas
    erros = converter_erros(validar_colunas(dados))

    if erros:
        return criar_retorno(
            "erro",
            "A planilha possui problemas na estrutura das colunas.",
            erros=erros
        )

    # 4. Validação dos dados dos alunos
    erros_alunos = converter_erros(
        validar_dados_alunos(alunos)
    )

    if erros_alunos:
        return criar_retorno(
            "erro",
            "A aba Alunos possui dados inválidos.",
            alunos=alunos,
            erros=erros_alunos
        )

    # 5. Validação das configurações das turmas
    erros_turmas = converter_erros(
        validar_dados_turmas(configuracoes_turmas)
    )

    if erros_turmas:
        return criar_retorno(
            "erro",
            "A aba Turmas possui dados inválidos.",
            alunos=alunos,
            erros=erros_turmas
        )

    # 6. Verificação da capacidade total
    erros_capacidade = converter_erros(
        validar_capacidade_total(alunos, configuracoes_turmas)
    )

    if erros_capacidade:
        return criar_retorno(
            "erro",
            "A capacidade total das turmas é insuficiente.",
            alunos=alunos,
            erros=erros_capacidade
        )

    # 7. Identificação de inconsistências nos alunos
    inconsistencias = identificar_inconsistencias(alunos)

    # 8. Geração das turmas individuais
    resultado_turmas = cadastrar_turmas(configuracoes_turmas)

    if not resultado_turmas["sucesso"]:
        return criar_retorno(
            "erro",
            "Não foi possível preparar as turmas.",
            alunos=alunos,
            inconsistencias=inconsistencias,
            erros=resultado_turmas["erros"]
        )

    turmas = resultado_turmas["turmas"]

    # 9. Retorno dos dados preparados
    return criar_retorno(
        "sucesso",
        "Dados validados e preparados para a otimização.",
        alunos=alunos,
        turmas=turmas,
        inconsistencias=inconsistencias
    )
