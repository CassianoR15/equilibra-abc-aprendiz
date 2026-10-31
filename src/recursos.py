
"""
Módulo de preparação dos recursos do Equilibra.

Responsável por transformar as configurações da aba Turmas em
turmas individuais, com identificadores, turnos e capacidades.

Cada linha da planilha representa uma configuração de turno.
A quantidade de turmas define quantas turmas individuais serão criadas,
e a capacidade representa o número de vagas de cada turma.
"""

import math
import unicodedata

import pandas as pd


def padronizar_turno(turno):
    """Normaliza e valida o turno informado."""
    if not isinstance(turno, str):
        return None

    texto = unicodedata.normalize("NFKD", turno.strip())
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    texto = texto.upper()

    equivalencias = {
        "MANHA": "MANHÃ",
        "TARDE": "TARDE"
    }

    return equivalencias.get(texto)


def inteiro_positivo(valor):
    """Verifica se o valor representa um número inteiro positivo."""
    if isinstance(valor, bool):
        return False

    try:
        numero = float(valor)

        return (
            math.isfinite(numero)
            and numero > 0
            and numero.is_integer()
        )

    except (TypeError, ValueError):
        return False


def cadastrar_turmas(dados_turmas, capacidades_confirmadas=None):
    """
    Cria turmas individuais a partir das configurações da planilha.

    Parâmetros:
        dados_turmas: DataFrame com turno, quantidade_turmas e capacidade.
        capacidades_confirmadas: mantido por compatibilidade com chamadas
        antigas. Não é necessário informar confirmações nesta versão.

    Retorno:
        Dicionário com:
            sucesso: indica se a criação foi concluída.
            turmas: lista de turmas individuais.
            erros: lista de problemas encontrados.
            confirmacoes_pendentes: lista mantida por compatibilidade.
    """
    resultado = {
        "sucesso": False,
        "turmas": [],
        "erros": [],
        "confirmacoes_pendentes": []
    }

    if not isinstance(dados_turmas, pd.DataFrame):
        resultado["erros"].append(
            "Os dados das turmas devem ser fornecidos em um DataFrame."
        )
        return resultado

    colunas_obrigatorias = [
        "turno",
        "quantidade_turmas",
        "capacidade"
    ]

    colunas_faltantes = [
        coluna
        for coluna in colunas_obrigatorias
        if coluna not in dados_turmas.columns
    ]

    if colunas_faltantes:
        resultado["erros"].append(
            f"Colunas obrigatórias ausentes: {colunas_faltantes}"
        )
        return resultado

    turmas_geradas = []
    erros = []
    numero_turma = 1

    for indice, linha in dados_turmas.iterrows():
        linha_planilha = indice + 2

        turno_original = linha["turno"]
        quantidade = linha["quantidade_turmas"]
        capacidade = linha["capacidade"]

        turno = padronizar_turno(turno_original)

        if turno is None:
            erros.append(
                f"Linha {linha_planilha}: turno inválido. "
                "Informe MANHÃ ou TARDE."
            )
            continue

        if not inteiro_positivo(quantidade):
            erros.append(
                f"Linha {linha_planilha}: quantidade de turmas "
                "deve ser um número inteiro positivo."
            )
            continue

        if not inteiro_positivo(capacidade):
            erros.append(
                f"Linha {linha_planilha}: capacidade deve ser "
                "um número inteiro positivo."
            )
            continue

        quantidade = int(float(quantidade))
        capacidade = int(float(capacidade))

        for _ in range(quantidade):
            turmas_geradas.append({
                "id_turma": numero_turma,
                "identificacao": f"Turma {numero_turma}",
                "turno": turno,
                "capacidade": capacidade
            })

            numero_turma += 1

    if erros:
        resultado["erros"] = erros
        return resultado

    if not turmas_geradas:
        resultado["erros"].append(
            "Nenhuma turma foi criada. Verifique os dados da planilha."
        )
        return resultado

    resultado["sucesso"] = True
    resultado["turmas"] = turmas_geradas

    return resultado
