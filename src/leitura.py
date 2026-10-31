
"""
Módulo de leitura das planilhas do Equilibra.

Responsabilidades:
- Receber um arquivo Excel (.xlsx ou .xls).
- Verificar a existência das abas obrigatórias: Alunos e Turmas.
- Ler os dados das duas abas utilizando Pandas.
- Retornar os dados separados para as próximas etapas do ETL.
"""

import os
import pandas as pd


# Abas obrigatórias do arquivo Excel
ABAS_OBRIGATORIAS = ["Alunos", "Turmas"]


def ler_planilha(arquivo):
    """
    Realiza a leitura das abas Alunos e Turmas.

    Parâmetro:
        arquivo: caminho ou objeto de arquivo Excel.

    Retorno:
        Dicionário contendo dois DataFrames:
        - alunos: dados da aba Alunos.
        - turmas: dados da aba Turmas.
    """

    # 1. Verifica se o arquivo foi informado
    if arquivo is None:
        raise ValueError("Nenhum arquivo foi enviado.")

    # 2. Verifica a existência e o tipo do arquivo, caso seja um caminho
    if isinstance(arquivo, (str, os.PathLike)):

        if not os.path.exists(arquivo):
            raise FileNotFoundError(
                "O arquivo informado não foi encontrado."
            )

        if not os.path.isfile(arquivo):
            raise ValueError(
                "O caminho informado não corresponde a um arquivo."
            )

    # 3. Verifica a extensão do arquivo
    nome_arquivo = getattr(arquivo, "name", arquivo)
    extensao = os.path.splitext(str(nome_arquivo))[1].lower()

    if extensao not in [".xlsx", ".xls"]:
        raise ValueError(
            "Formato inválido. Envie um arquivo Excel (.xlsx ou .xls)."
        )

    # 4. Lê todas as abas do arquivo
    try:
        planilhas = pd.read_excel(
            arquivo,
            sheet_name=None
        )

    except Exception as erro:
        raise ValueError(
            f"Não foi possível ler o arquivo Excel: {erro}"
        ) from erro

    # 5. Identifica as abas ignorando diferenças de maiúsculas e espaços
    abas_encontradas = {
        str(nome).strip().lower(): nome
        for nome in planilhas.keys()
    }

    # 6. Verifica se as duas abas obrigatórias existem
    abas_faltantes = [
        aba for aba in ABAS_OBRIGATORIAS
        if aba.lower() not in abas_encontradas
    ]

    if abas_faltantes:
        raise ValueError(
            f"Abas obrigatórias ausentes: {abas_faltantes}. "
            "O arquivo deve conter as abas Alunos e Turmas."
        )

    # 7. Separa os dados de cada aba
    df_alunos = planilhas[
        abas_encontradas["alunos"]
    ].copy()

    df_turmas = planilhas[
        abas_encontradas["turmas"]
    ].copy()

    # 8. Verifica se as abas possuem dados
    if df_alunos.empty:
        raise ValueError(
            "A aba Alunos não possui dados."
        )

    if df_turmas.empty:
        raise ValueError(
            "A aba Turmas não possui dados."
        )

    # 9. Retorna os dados separados
    return {
        "alunos": df_alunos,
        "turmas": df_turmas
    }
