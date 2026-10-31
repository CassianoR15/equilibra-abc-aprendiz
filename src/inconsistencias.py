
"""
Módulo de identificação de inconsistências do Equilibra.

Analisa os dados dos alunos, identifica problemas de preenchimento,
tipos, valores inválidos, possíveis duplicidades e conflitos de cadastro.

As inconsistências são organizadas em um relatório para que o usuário
possa corrigir os dados antes da execução da otimização.

Este módulo não exclui nem altera registros automaticamente.
"""

import re
import unicodedata

import pandas as pd


COLUNAS_ALUNOS = ["nome", "sexo", "disponibilidade"]


def valor_ausente(valor):
    """Verifica se um valor está vazio, considerando NaN, None e textos vazios."""
    if valor is None:
        return True

    if isinstance(valor, str):
        return valor.strip() == ""

    try:
        return bool(pd.isna(valor))
    except (TypeError, ValueError):
        return False


def verificar_nome_suspeito(nome):
    """Verifica se o nome possui pelo menos uma letra."""
    if not isinstance(nome, str):
        return False

    return not any(letra.isalpha() for letra in nome)


def normalizar_nome_comparacao(nome):
    """Normaliza o nome apenas para comparar possíveis duplicidades."""
    if not isinstance(nome, str):
        return nome

    nome = nome.strip().lower()
    nome = re.sub(r"\s+", " ", nome)

    nome = unicodedata.normalize("NFD", nome)
    nome = "".join(
        caractere
        for caractere in nome
        if unicodedata.category(caractere) != "Mn"
    )

    return nome


def verificar_tipos(df):
    """Identifica valores com tipos diferentes do esperado."""
    problemas = []

    for coluna in COLUNAS_ALUNOS:
        if coluna not in df.columns:
            continue

        for indice, valor in df[coluna].items():
            if not valor_ausente(valor) and not isinstance(valor, str):
                problemas.append({
                    "linha": indice + 2,
                    "coluna": coluna,
                    "valor": valor,
                    "problema": "Tipo incorreto: esperado texto (string)"
                })

    return problemas


def verificar_ausentes(df):
    """Identifica campos obrigatórios ausentes em linhas parcialmente preenchidas."""
    problemas = []

    colunas_existentes = [
        coluna for coluna in COLUNAS_ALUNOS
        if coluna in df.columns
    ]

    if not colunas_existentes:
        return problemas

    for indice, linha in df.iterrows():

        # Linhas totalmente vazias são tratadas em outra verificação.
        if all(valor_ausente(linha[coluna]) for coluna in colunas_existentes):
            continue

        for coluna in colunas_existentes:
            if valor_ausente(linha[coluna]):
                problemas.append({
                    "linha": indice + 2,
                    "coluna": coluna,
                    "valor": linha[coluna],
                    "problema": "Valor ausente"
                })

    return problemas


def verificar_valores_invalidos(df):
    """Verifica se sexo e disponibilidade possuem valores permitidos."""
    problemas = []

    valores_sexo = ["F", "M"]
    valores_disponibilidade = ["MANHÃ", "TARDE"]

    for indice, linha in df.iterrows():

        if "sexo" in df.columns:
            sexo = linha["sexo"]

            if isinstance(sexo, str) and not valor_ausente(sexo):
                if sexo not in valores_sexo:
                    problemas.append({
                        "linha": indice + 2,
                        "coluna": "sexo",
                        "valor": sexo,
                        "problema": "Valor de sexo inválido"
                    })

        if "disponibilidade" in df.columns:
            disponibilidade = linha["disponibilidade"]

            if (
                isinstance(disponibilidade, str)
                and not valor_ausente(disponibilidade)
            ):
                if disponibilidade not in valores_disponibilidade:
                    problemas.append({
                        "linha": indice + 2,
                        "coluna": "disponibilidade",
                        "valor": disponibilidade,
                        "problema": "Disponibilidade inválida"
                    })

    return problemas


def verificar_nomes_suspeitos(df):
    """Identifica nomes preenchidos apenas com números ou caracteres especiais."""
    problemas = []

    if "nome" not in df.columns:
        return problemas

    for indice, nome in df["nome"].items():

        if isinstance(nome, str) and not valor_ausente(nome):
            if verificar_nome_suspeito(nome):
                problemas.append({
                    "linha": indice + 2,
                    "coluna": "nome",
                    "valor": nome,
                    "problema": (
                        "Nome sem letras ou preenchido apenas "
                        "com números/caracteres especiais"
                    )
                })

    return problemas


def verificar_linhas_vazias(df):
    """Identifica linhas totalmente vazias na aba de alunos."""
    problemas = []

    colunas_existentes = [
        coluna for coluna in COLUNAS_ALUNOS
        if coluna in df.columns
    ]

    if not colunas_existentes:
        return problemas

    for indice, linha in df.iterrows():

        if all(valor_ausente(linha[coluna]) for coluna in colunas_existentes):
            problemas.append({
                "linha": indice + 2,
                "coluna": "todas",
                "valor": None,
                "problema": "Linha totalmente vazia"
            })

    return problemas


def verificar_duplicados_exatos(df):
    """
    Identifica registros exatamente repetidos.

    Os registros são apenas sinalizados. Nenhum aluno é removido.
    """
    problemas = []

    if not all(coluna in df.columns for coluna in COLUNAS_ALUNOS):
        return problemas

    mascara = df[COLUNAS_ALUNOS].apply(
        lambda linha: all(
            isinstance(valor, str) and not valor_ausente(valor)
            for valor in linha
        ),
        axis=1
    )

    dados = df.loc[mascara, COLUNAS_ALUNOS].copy()

    dados["nome"] = dados["nome"].map(normalizar_nome_comparacao)
    duplicados = dados.duplicated(keep=False)

    grupos = dados[duplicados].groupby(
        ["nome", "sexo", "disponibilidade"],
        dropna=False
    )

    for _, grupo in grupos:

        linhas = [indice + 2 for indice in grupo.index]
        linhas_texto = ", ".join(map(str, linhas))

        problemas.append({
            "linha": linhas_texto,
            "coluna": "todas",
            "valor": df.loc[grupo.index[0], "nome"],
            "problema": (
                "Duplicidade exata: registros encontrados "
                f"nas linhas {linhas_texto}"
            )
        })

    return problemas


def verificar_conflitos_disponibilidade(df):
    """Identifica nomes e sexos iguais com disponibilidades diferentes."""
    problemas = []

    if not all(coluna in df.columns for coluna in COLUNAS_ALUNOS):
        return problemas

    mascara = (
        df["nome"].apply(
            lambda valor: isinstance(valor, str) and not valor_ausente(valor)
        )
        & df["sexo"].isin(["F", "M"])
        & df["disponibilidade"].isin(["MANHÃ", "TARDE"])
    )

    dados = df.loc[mascara].copy()

    dados["nome_comparacao"] = dados["nome"].map(
        normalizar_nome_comparacao
    )

    grupos = dados.groupby(["nome_comparacao", "sexo"])

    for _, grupo in grupos:

        disponibilidades = grupo["disponibilidade"].unique()

        if len(disponibilidades) > 1:
            for indice, linha in grupo.iterrows():
                problemas.append({
                    "linha": indice + 2,
                    "coluna": "disponibilidade",
                    "valor": linha["disponibilidade"],
                    "problema": (
                        "Possível conflito: mesmo nome e sexo "
                        "com disponibilidades diferentes"
                    )
                })

    return problemas


def verificar_homonimos(df):
    """Identifica nomes iguais associados a sexos diferentes."""
    problemas = []

    if not all(coluna in df.columns for coluna in ["nome", "sexo"]):
        return problemas

    mascara = (
        df["nome"].apply(
            lambda valor: isinstance(valor, str) and not valor_ausente(valor)
        )
        & df["sexo"].isin(["F", "M"])
    )

    dados = df.loc[mascara].copy()

    dados["nome_comparacao"] = dados["nome"].map(
        normalizar_nome_comparacao
    )

    grupos = dados.groupby("nome_comparacao")

    for _, grupo in grupos:

        if len(grupo) > 1 and grupo["sexo"].nunique() > 1:
            for indice, linha in grupo.iterrows():
                problemas.append({
                    "linha": indice + 2,
                    "coluna": "nome/sexo",
                    "valor": linha["nome"],
                    "problema": (
                        "Possível homônimo: mesmo nome com sexos "
                        "diferentes. Revisar registros"
                    )
                })

    return problemas


def classificar_problema(problema):
    """Classifica cada inconsistência encontrada."""
    if problema in ["Valor ausente", "Linha totalmente vazia"]:
        return "Preenchimento"

    if "Tipo incorreto" in problema:
        return "Tipo/formato"

    if "inválido" in problema or "inválida" in problema:
        return "Valor inválido"

    if "Duplicidade" in problema:
        return "Duplicidade"

    if "conflito" in problema or "homônimo" in problema:
        return "Conflito de cadastro"

    if "Nome sem letras" in problema:
        return "Dado suspeito"

    return "Não classificado"


def orientar_correcao(problema):
    """Fornece uma orientação para a correção de cada problema."""
    if "Duplicidade exata" in problema:
        return (
            "Conferir se os registros representam a mesma pessoa. "
            "Se forem duplicados, corrigir a planilha manualmente."
        )

    if "Valor ausente" in problema or "Linha totalmente vazia" in problema:
        return "Preencher os campos obrigatórios ou remover a linha vazia"

    if "Tipo incorreto" in problema:
        return "Corrigir o valor para o formato de texto"

    if "sexo inválido" in problema:
        return "Corrigir para F ou M"

    if "Disponibilidade inválida" in problema:
        return "Corrigir para MANHÃ ou TARDE"

    if "Nome sem letras" in problema:
        return "Conferir e preencher o nome corretamente"

    if "conflito" in problema:
        return (
            "Conferir se os registros pertencem à mesma pessoa "
            "e corrigir a disponibilidade, se necessário"
        )

    if "homônimo" in problema:
        return (
            "Conferir os cadastros para verificar se são pessoas diferentes"
        )

    return "Revisar o registro na planilha"


def identificar_inconsistencias(df):
    """
    Reúne as inconsistências da aba Alunos em um único relatório.

    Retorna None quando não encontra problemas ou um DataFrame
    com os detalhes das inconsistências encontradas.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Os dados dos alunos devem estar em um DataFrame.")

    problemas = []

    verificacoes = [
        verificar_tipos,
        verificar_ausentes,
        verificar_valores_invalidos,
        verificar_nomes_suspeitos,
        verificar_linhas_vazias,
        verificar_duplicados_exatos,
        verificar_conflitos_disponibilidade,
        verificar_homonimos
    ]

    for verificacao in verificacoes:
        problemas.extend(verificacao(df))

    if not problemas:
        return None

    relatorio = pd.DataFrame(problemas)

    relatorio["categoria"] = relatorio["problema"].map(
        classificar_problema
    )

    relatorio["orientacao"] = relatorio["problema"].map(
        orientar_correcao
    )

    return relatorio[
        ["linha", "coluna", "valor", "categoria", "problema", "orientacao"]
    ]
