
"""
Módulo de padronização dos dados do Equilibra.

Responsável por limpar espaços, normalizar nomes de colunas e
padronizar os valores das abas Alunos e Turmas antes da validação
e do envio dos dados ao modelo de otimização.
"""

import re
import unicodedata

from src.validacao import normalizar_colunas


def limpar_espacos(valor):
    """Remove espaços extras no início, fim e entre palavras."""
    if isinstance(valor, str):
        valor = valor.strip()
        valor = re.sub(r"\s+", " ", valor)

    return valor


def remover_acentos(valor):
    """Remove acentos de um texto para facilitar a comparação."""
    if not isinstance(valor, str):
        return valor

    texto = unicodedata.normalize("NFKD", valor)
    return "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )


def padronizar_texto(valor):
    """Limpa espaços, remove acentos e converte o texto para maiúsculas."""
    if isinstance(valor, str):
        valor = limpar_espacos(valor)
        valor = remover_acentos(valor)
        valor = valor.upper()

    return valor


def padronizar_alunos(df):
    """Padroniza os dados da aba Alunos."""
    df = normalizar_colunas(df.copy())

    colunas_texto = ["nome", "sexo", "disponibilidade"]

    for coluna in colunas_texto:
        if coluna in df.columns:
            df[coluna] = df[coluna].map(limpar_espacos)

    if "nome" in df.columns:
        df["nome"] = df["nome"].map(
            lambda valor: valor.title() if isinstance(valor, str) else valor
        )

    equivalencia_sexo = {
        "F": "F",
        "FEM": "F",
        "FEMININO": "F",
        "M": "M",
        "MASC": "M",
        "MASCULINO": "M",
    }

    if "sexo" in df.columns:
        df["sexo"] = df["sexo"].map(
            lambda valor: equivalencia_sexo.get(
                padronizar_texto(valor),
                padronizar_texto(valor)
            )
        )

    equivalencia_turno = {
        "MANHA": "MANHÃ",
        "TARDE": "TARDE",
    }

    if "disponibilidade" in df.columns:
        df["disponibilidade"] = df["disponibilidade"].map(
            lambda valor: equivalencia_turno.get(
                padronizar_texto(valor),
                padronizar_texto(valor)
            )
        )

    return df


def padronizar_turmas(df):
    """Padroniza os dados da aba Turmas."""
    df = normalizar_colunas(df.copy())

    if "turno" in df.columns:
        equivalencia_turno = {
            "MANHA": "MANHÃ",
            "TARDE": "TARDE",
        }

        df["turno"] = df["turno"].map(
            lambda valor: equivalencia_turno.get(
                padronizar_texto(valor),
                padronizar_texto(valor)
            )
        )

    return df


def padronizar_dados(dados):
    """
    Padroniza as duas abas recebidas pela leitura da planilha.

    Também mantém compatibilidade com chamadas antigas que enviam
    diretamente um DataFrame de alunos.
    """
    if hasattr(dados, "columns"):
        return padronizar_alunos(dados)

    if not isinstance(dados, dict):
        raise TypeError(
            "Os dados devem ser um DataFrame ou um dicionário com as abas."
        )

    if "alunos" not in dados or "turmas" not in dados:
        raise ValueError(
            "Os dados devem conter as abas 'alunos' e 'turmas'."
        )

    return {
        "alunos": padronizar_alunos(dados["alunos"]),
        "turmas": padronizar_turmas(dados["turmas"]),
    }
