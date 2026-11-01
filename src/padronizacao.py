
import re
import unicodedata
import pandas as pd

from src.validacao import normalizar_colunas


def limpar_espacos(valor):
    if isinstance(valor, str):
        return re.sub(r"\s+", " ", valor.strip())
    return valor


def remover_acentos(valor):
    if not isinstance(valor, str):
        return valor

    texto = unicodedata.normalize("NFKD", valor)

    return "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )


def padronizar_texto(valor):
    if isinstance(valor, str):
        return remover_acentos(
            limpar_espacos(valor)
        ).upper()

    return valor


def padronizar_alunos(df):
    df = df.copy()

    # Reconhece o nome original da coluna da planilha.
    df = df.rename(columns={
        "Recebi as instâncias": "nome",
        "Recebi as instâncias ": "nome",
    })

    df = normalizar_colunas(df)

    if "nome" in df.columns:
        df["nome"] = df["nome"].map(limpar_espacos)

    if "sexo" in df.columns:
        df["sexo"] = df["sexo"].map(
            lambda x: {
                "F": "F",
                "FEMININO": "F",
                "FEM": "F",
                "M": "M",
                "MASCULINO": "M",
                "MASC": "M",
            }.get(padronizar_texto(x), padronizar_texto(x))
        )

    if "disponibilidade" in df.columns:
        df["disponibilidade"] = df["disponibilidade"].map(
            lambda x: {
                "MANHA": "MANHÃ",
                "TARDE": "TARDE",
            }.get(padronizar_texto(x), padronizar_texto(x))
        )

    return df


def padronizar_turmas(df):
    df = df.copy()

    # A planilha original utiliza uma tabela de recursos.
    df = df.rename(columns={
        "Recursos": "recursos",
        "Quantidade": "quantidade",
    })

    df = normalizar_colunas(df)

    if "recursos" not in df.columns or "quantidade" not in df.columns:
        return df

    dados = {}

    for _, linha in df.iterrows():
        recurso = padronizar_texto(linha["recursos"])
        quantidade = linha["quantidade"]

        if isinstance(recurso, str):
            dados[recurso] = quantidade

    configuracoes = []

    for turno in ["MANHA", "TARDE"]:
        quantidade_turmas = dados.get(f"TURMAS_{turno}")
        capacidade = dados.get(f"VAGAS_{turno}")

        if quantidade_turmas is not None and capacidade is not None:
            configuracoes.append({
                "turno": turno,
                "quantidade_turmas": quantidade_turmas,
                "capacidade": capacidade,
            })

    return pd.DataFrame(configuracoes)


def padronizar_dados(dados):

    if isinstance(dados, pd.DataFrame):
        return padronizar_alunos(dados)

    if not isinstance(dados, dict):
        raise TypeError(
            "Os dados devem ser um DataFrame ou dicionário."
        )

    return {
        "alunos": padronizar_alunos(dados["alunos"]),
        "turmas": padronizar_turmas(dados["turmas"]),
    }
