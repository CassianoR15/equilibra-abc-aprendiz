
"""
Módulo de validação estrutural e dos dados do Equilibra.

Responsabilidades:
- Verificar as colunas obrigatórias das abas Alunos e Turmas.
- Identificar campos vazios e valores inválidos.
- Validar sexo e disponibilidade dos alunos.
- Validar turnos, quantidade de turmas e capacidade.
- Verificar a capacidade total disponível.
"""


import math
import unicodedata
import pandas as pd


# Colunas obrigatórias de cada aba
COLUNAS_ALUNOS = [
    "nome",
    "sexo",
    "disponibilidade"
]

COLUNAS_TURMAS = [
    "turno",
    "quantidade_turmas",
    "capacidade"
]


# Normaliza os nomes das colunas
def normalizar_colunas(df):

    df = df.copy()

    df.columns = [
        str(coluna).strip().lower().replace(" ", "_")
        for coluna in df.columns
    ]

    # Aceita algumas variações de escrita
    equivalencias = {
        "quantidade_de_turmas": "quantidade_turmas",
        "qtd_turmas": "quantidade_turmas",
        "qtd_turma": "quantidade_turmas"
    }

    df = df.rename(columns=equivalencias)

    return df


# Verifica as colunas obrigatórias
def validar_colunas(dados):

    # Mantém compatibilidade com a validação antiga de um DataFrame
    if isinstance(dados, pd.DataFrame):

        df = normalizar_colunas(dados)

        colunas_faltantes = [
            coluna for coluna in COLUNAS_ALUNOS
            if coluna not in df.columns
        ]

        return [
            f"Na aba Alunos, coluna obrigatória ausente: {coluna}"
            for coluna in colunas_faltantes
        ]

    # Verifica se as duas abas foram recebidas
    if not isinstance(dados, dict):
        return ["Os dados devem conter as abas Alunos e Turmas."]

    if "alunos" not in dados or "turmas" not in dados:
        return ["As abas Alunos e Turmas são obrigatórias."]

    erros = []

    # Verifica as colunas de cada aba
    abas = [
        ("alunos", COLUNAS_ALUNOS, "Alunos"),
        ("turmas", COLUNAS_TURMAS, "Turmas")
    ]

    for chave, colunas_obrigatorias, nome_aba in abas:

        df = normalizar_colunas(dados[chave])

        colunas_faltantes = [
            coluna for coluna in colunas_obrigatorias
            if coluna not in df.columns
        ]

        for coluna in colunas_faltantes:
            erros.append(
                f"Na aba {nome_aba}, coluna obrigatória ausente: {coluna}"
            )

    return erros


# Verifica se um valor é um número inteiro positivo
def inteiro_positivo(valor):

    if isinstance(valor, bool):
        return False

    try:
        numero = float(valor)

    except (TypeError, ValueError):
        return False

    return (
        math.isfinite(numero)
        and numero > 0
        and numero.is_integer()
    )


# Verifica os dados dos alunos
def validar_dados_alunos(df):

    df = normalizar_colunas(df)

    erros = []

    for indice, linha in df.iterrows():

        numero_linha = indice + 2

        nome = linha.get("nome")
        sexo = linha.get("sexo")
        disponibilidade = linha.get("disponibilidade")

        # Verifica o nome
        if pd.isna(nome) or not str(nome).strip():

            erros.append(
                f"Linha {numero_linha}: nome não preenchido."
            )

        # Verifica o sexo
        sexo_normalizado = (
            str(sexo).strip().upper()
            if not pd.isna(sexo) else ""
        )

        if sexo_normalizado not in {
            "F", "M", "FEM", "MASC",
            "FEMININO", "MASCULINO"
        }:

            erros.append(
                f"Linha {numero_linha}: sexo inválido. "
                "Informe F ou M."
            )

        # Verifica a disponibilidade
        disponibilidade_normalizada = ""

        if not pd.isna(disponibilidade):

            disponibilidade_normalizada = unicodedata.normalize(
                "NFKD",
                str(disponibilidade).strip().upper()
            )

            disponibilidade_normalizada = "".join(
                caractere
                for caractere in disponibilidade_normalizada
                if not unicodedata.combining(caractere)
            )

        if disponibilidade_normalizada not in {
            "MANHA",
            "TARDE"
        }:

            erros.append(
                f"Linha {numero_linha}: disponibilidade inválida. "
                "Informe MANHÃ ou TARDE."
            )

    return erros


# Verifica os dados das turmas
def validar_dados_turmas(df):

    df = normalizar_colunas(df)

    erros = []

    for indice, linha in df.iterrows():

        numero_linha = indice + 2

        turno = linha.get("turno")
        quantidade = linha.get("quantidade_turmas")
        capacidade = linha.get("capacidade")

        # Verifica o turno
        turno_normalizado = ""

        if not pd.isna(turno):

            turno_normalizado = unicodedata.normalize(
                "NFKD",
                str(turno).strip().upper()
            )

            turno_normalizado = "".join(
                caractere
                for caractere in turno_normalizado
                if not unicodedata.combining(caractere)
            )

        if turno_normalizado not in {"MANHA", "TARDE"}:

            erros.append(
                f"Linha {numero_linha}: turno inválido. "
                "Informe MANHÃ ou TARDE."
            )

        # Verifica a quantidade de turmas
        if not inteiro_positivo(quantidade):

            erros.append(
                f"Linha {numero_linha}: quantidade_turmas "
                "deve ser um número inteiro positivo."
            )

        # Verifica a capacidade
        if not inteiro_positivo(capacidade):

            erros.append(
                f"Linha {numero_linha}: capacidade "
                "deve ser um número inteiro positivo."
            )

    return erros


# Calcula e verifica a capacidade total disponível
def validar_capacidade_total(alunos, turmas):

    total_alunos = len(alunos)

    total_vagas = 0

    for _, linha in turmas.iterrows():

        quantidade = int(float(linha["quantidade_turmas"]))
        capacidade = int(float(linha["capacidade"]))

        total_vagas += quantidade * capacidade

    if total_vagas < total_alunos:

        return [
            f"Capacidade insuficiente: existem {total_alunos} alunos "
            f"e apenas {total_vagas} vagas disponíveis."
        ]

    return []


# Executa todas as validações
def validar_arquivo(dados):

    erros = validar_colunas(dados)

    # Interrompe se faltarem colunas obrigatórias
    if erros:
        return erros

    alunos = normalizar_colunas(dados["alunos"])
    turmas = normalizar_colunas(dados["turmas"])

    # Valida os dados de cada aba
    erros.extend(validar_dados_alunos(alunos))
    erros.extend(validar_dados_turmas(turmas))

    # Calcula a capacidade somente se os dados das turmas forem válidos
    erros_turmas = validar_dados_turmas(turmas)

    if not erros_turmas:
        erros.extend(
            validar_capacidade_total(alunos, turmas)
        )

    return erros
