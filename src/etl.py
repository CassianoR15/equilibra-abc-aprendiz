
import pandas as pd
import unicodedata
import re

from collections import defaultdict

from src.padronizacao import (
    padronizar_nome,
    padronizar_sexo,
    padronizar_disponibilidade
)


# =====================================================
# 1. NORMALIZAÇÃO DOS NOMES DAS COLUNAS
# =====================================================

def normalizar_coluna(nome):

    nome = str(nome).strip().upper()

    nome = unicodedata.normalize(
        "NFKD", nome
    ).encode("ASCII", "ignore").decode("ASCII")

    nome = re.sub(r"\s+", " ", nome)

    return nome


# =====================================================
# 2. IDENTIFICAÇÃO DAS COLUNAS
# =====================================================

def identificar_coluna(df, alternativas, nome_campo):

    colunas = {
        normalizar_coluna(coluna): coluna
        for coluna in df.columns
    }

    for alternativa in alternativas:

        alternativa = normalizar_coluna(alternativa)

        if alternativa in colunas:
            return colunas[alternativa]

    raise ValueError(
        f"Coluna obrigatória não encontrada: {nome_campo}. "
        f"Colunas disponíveis: {list(df.columns)}"
    )


# =====================================================
# 3. LEITURA E VALIDAÇÃO DA ABA ALUNOS
# =====================================================

def processar_alunos(df):

    coluna_nome = identificar_coluna(
        df,
        [
            "NOME",
            "NOME DO ALUNO",
            "ALUNO",
            "RECEBI AS INSTÂNCIAS"
        ],
        "Nome do aluno"
    )

    coluna_sexo = identificar_coluna(
        df,
        ["SEXO", "GÊNERO"],
        "Sexo"
    )

    coluna_disponibilidade = identificar_coluna(
        df,
        ["DISPONIBILIDADE", "TURNO", "PERÍODO"],
        "Disponibilidade"
    )

    alunos = []
    inconsistencias = []

    duplicidades = defaultdict(list)

    for indice, linha in df.iterrows():

        numero_linha = indice + 2

        nome_original = linha[coluna_nome]

        sexo_original = linha[coluna_sexo]

        disponibilidade_original = linha[
            coluna_disponibilidade
        ]

        # ---------------------------------------------
        # Nome
        # ---------------------------------------------

        nome = padronizar_nome(nome_original)

        if not nome:

            inconsistencias.append({
                "linha": numero_linha,
                "aluno": "",
                "campo": "Nome",
                "problema": "Nome vazio",
                "tipo": "BLOQUEANTE"
            })

            continue

        # ---------------------------------------------
        # Sexo
        # ---------------------------------------------

        sexo = padronizar_sexo(sexo_original)

        if sexo not in ["M", "F"]:

            inconsistencias.append({
                "linha": numero_linha,
                "aluno": nome,
                "campo": "Sexo",
                "problema": f"Sexo inválido: {sexo_original}",
                "tipo": "BLOQUEANTE"
            })

            continue

        # ---------------------------------------------
        # Disponibilidade
        # ---------------------------------------------

        disponibilidade = padronizar_disponibilidade(
            disponibilidade_original
        )

        if disponibilidade not in ["MANHA", "TARDE"]:

            inconsistencias.append({
                "linha": numero_linha,
                "aluno": nome,
                "campo": "Disponibilidade",
                "problema": (
                    f"Disponibilidade inválida: "
                    f"{disponibilidade_original}"
                ),
                "tipo": "BLOQUEANTE"
            })

            continue

        # ---------------------------------------------
        # Identificação de duplicidades
        # ---------------------------------------------

        chave_nome = normalizar_coluna(nome)

        duplicidades[chave_nome].append({
            "linha": numero_linha,
            "nome": nome
        })

        # ---------------------------------------------
        # Cadastro do aluno
        # ---------------------------------------------

        alunos.append({
            "id": len(alunos) + 1,
            "linha": numero_linha,
            "nome": nome,
            "sexo": sexo,
            "disponibilidade": [disponibilidade]
        })

    # ---------------------------------------------
    # Alertas de nomes duplicados
    # ---------------------------------------------

    for registros in duplicidades.values():

        if len(registros) > 1:

            for registro in registros:

                inconsistencias.append({
                    "linha": registro["linha"],
                    "aluno": registro["nome"],
                    "campo": "Nome",
                    "problema": (
                        "Possível duplicidade de cadastro"
                    ),
                    "tipo": "ALERTA"
                })

    return alunos, inconsistencias


# =====================================================
# 4. LEITURA E VALIDAÇÃO DA ABA TURMAS
# =====================================================


def processar_turmas(df):

    turmas = []
    inconsistencias = []

    # A planilha possui duas colunas:
    # Recursos | Quantidade

    colunas = list(df.columns)

    if len(colunas) < 2:
        raise ValueError(
            "A aba Turmas precisa ter as colunas Recursos e Quantidade."
        )

    coluna_recurso = colunas[0]
    coluna_quantidade = colunas[1]

    recursos = {}

    for indice, linha in df.iterrows():

        recurso = str(
            linha[coluna_recurso]
        ).strip().lower()

        quantidade = pd.to_numeric(
            linha[coluna_quantidade],
            errors="coerce"
        )

        if recurso in ["nan", "none", ""]:
            continue

        recursos[recurso] = quantidade

    # Parâmetros da planilha

    configuracoes = [
        ("turmas_manha", "vagas_manha", "MANHA"),
        ("turmas_tarde", "vagas_tarde", "TARDE")
    ]

    id_turma = 1

    for recurso_turmas, recurso_vagas, turno in configuracoes:

        quantidade = recursos.get(recurso_turmas)
        capacidade = recursos.get(recurso_vagas)

        if (
            quantidade is None
            or capacidade is None
            or pd.isna(quantidade)
            or pd.isna(capacidade)
        ):

            inconsistencias.append({
                "linha": "",
                "aluno": "",
                "campo": "Turmas",
                "problema": (
                    f"Parâmetros ausentes para o turno {turno}"
                ),
                "tipo": "BLOQUEANTE"
            })

            continue

        if (
            quantidade <= 0
            or capacidade <= 0
            or quantidade % 1 != 0
            or capacidade % 1 != 0
        ):

            inconsistencias.append({
                "linha": "",
                "aluno": "",
                "campo": "Turmas",
                "problema": (
                    f"Quantidade de turmas e vagas "
                    f"devem ser inteiros positivos: {turno}"
                ),
                "tipo": "BLOQUEANTE"
            })

            continue

        for _ in range(int(quantidade)):

            turmas.append({
                "id": id_turma,
                "turno": turno,
                "capacidade": int(capacidade)
            })

            id_turma += 1

    return turmas, inconsistencias



# =====================================================
# 5. VALIDAÇÃO DA CAPACIDADE TOTAL
# =====================================================

def validar_capacidade(alunos, turmas):

    inconsistencias = []

    for turno in ["MANHA", "TARDE"]:

        total_alunos = sum(
            1
            for aluno in alunos
            if aluno["disponibilidade"] == [turno]
        )

        total_vagas = sum(
            turma["capacidade"]
            for turma in turmas
            if turma["turno"] == turno
        )

        if total_alunos > total_vagas:

            inconsistencias.append({
                "linha": "",
                "aluno": "",
                "campo": "Capacidade",
                "problema": (
                    f"{turno}: {total_alunos} alunos "
                    f"para {total_vagas} vagas disponíveis"
                ),
                "tipo": "BLOQUEANTE"
            })

    return inconsistencias


# =====================================================
# 6. FUNÇÃO PRINCIPAL DE LEITURA DO EXCEL
# =====================================================

def ler_excel(caminho):

    try:

        arquivo = pd.ExcelFile(caminho)

    except Exception as erro:

        raise ValueError(
            f"Não foi possível abrir o Excel: {erro}"
        )

    if "Alunos" not in arquivo.sheet_names:

        raise ValueError(
            "Aba obrigatória 'Alunos' não encontrada."
        )

    if "Turmas" not in arquivo.sheet_names:

        raise ValueError(
            "Aba obrigatória 'Turmas' não encontrada."
        )

    alunos_df = pd.read_excel(
        caminho,
        sheet_name="Alunos"
    )

    turmas_df = pd.read_excel(
        caminho,
        sheet_name="Turmas"
    )

    if alunos_df.empty:

        raise ValueError(
            "A aba Alunos não possui registros."
        )

    if turmas_df.empty:

        raise ValueError(
            "A aba Turmas não possui registros."
        )

    # Processamento dos dados

    alunos, erros_alunos = processar_alunos(
        alunos_df
    )

    turmas, erros_turmas = processar_turmas(
        turmas_df
    )

    inconsistencias = (
        erros_alunos
        + erros_turmas
    )

    # Verificação de capacidade

    if not any(
        item["tipo"] == "BLOQUEANTE"
        for item in inconsistencias
    ):

        inconsistencias.extend(
            validar_capacidade(alunos, turmas)
        )

    # Retorno dos dados

    bloqueantes = [
        item for item in inconsistencias
        if item["tipo"] == "BLOQUEANTE"
    ]

    if bloqueantes:

        raise ValueError(
            "Foram encontradas inconsistências "
            "que impedem o ensalamento."
        )

    return alunos, turmas
