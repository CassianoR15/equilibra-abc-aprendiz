"""
Responsável pela leitura de planilhas Excel (.xlsx e .xls).

Verifica o recebimento, o caminho, o formato e o conteúdo do
arquivo. Retorna os dados em um DataFrame do Pandas para as
próximas etapas do ETL.

Preparado para receber arquivos enviados pela interface.
"""
import os
import pandas as pd


# Realiza a leitura do arquivo Excel
def ler_planilha(arquivo):

    # 1. Verifica se o arquivo foi informado
    if arquivo is None:
        raise ValueError("Nenhum arquivo foi enviado.")

    # 2. Verifica a existência e o tipo, caso seja um caminho
    if isinstance(arquivo, (str, os.PathLike)):

        if not os.path.exists(arquivo):
            raise FileNotFoundError(
                "O arquivo informado não foi encontrado."
            )

        if not os.path.isfile(arquivo):
            raise ValueError(
                "O caminho informado não corresponde a um arquivo."
            )

    # 3. Identifica o nome e a extensão do arquivo
    nome_arquivo = getattr(arquivo, "name", arquivo)

    extensao = os.path.splitext(nome_arquivo)[1].lower()

    if extensao not in [".xlsx", ".xls"]:
        raise ValueError(
            "Formato inválido. Envie um arquivo Excel (.xlsx ou .xls)."
        )

    # 4. Tenta ler o arquivo Excel
    try:
        df = pd.read_excel(arquivo)

    except Exception as erro:
        raise ValueError(
            f"Não foi possível ler o arquivo: {erro}"
        ) from erro

    # 5. Verifica se a planilha possui dados
    if df.empty:
        raise ValueError("A planilha não possui dados.")

    # 6. Retorna os dados carregados
    return df
