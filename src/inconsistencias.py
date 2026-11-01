
import pandas as pd
import unicodedata

COLUNAS_ALUNOS = ["nome", "sexo", "disponibilidade"]


def normalizar_texto(valor):
    if not isinstance(valor, str):
        return ""

    texto = unicodedata.normalize("NFKD", valor.strip().upper())

    return "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )


def identificar_inconsistencias(df):
    """
    Identifica problemas nos dados dos alunos.
    Não altera nem exclui registros.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Os dados devem ser um DataFrame.")

    problemas = []

    for indice, linha in df.iterrows():

        numero_linha = indice + 2

        nome = linha.get("nome")
        sexo = linha.get("sexo")
        disponibilidade = linha.get("disponibilidade")

        # Verificação do nome
        if pd.isna(nome) or not str(nome).strip():

            problemas.append({
                "linha": numero_linha,
                "coluna": "nome",
                "valor_atual": nome,
                "problema": "Nome não preenchido",
                "orientacao": "Informe o nome do aluno"
            })

        # Verificação do sexo
        sexo_normalizado = normalizar_texto(sexo)

        if sexo_normalizado not in ["F", "M", "FEMININO", "MASCULINO"]:
            problemas.append({
                "linha": numero_linha,
                "coluna": "sexo",
                "valor_atual": sexo,
                "problema": "Sexo inválido",
                "orientacao": "Informe F ou M"
            })

        # Verificação da disponibilidade
        disponibilidade_normalizada = normalizar_texto(
            disponibilidade
        )

        if disponibilidade_normalizada not in ["MANHA", "TARDE"]:
            problemas.append({
                "linha": numero_linha,
                "coluna": "disponibilidade",
                "valor_atual": disponibilidade,
                "problema": "Disponibilidade inválida",
                "orientacao": "Informe MANHÃ ou TARDE"
            })

    if not problemas:
        return pd.DataFrame(
            columns=[
                "linha",
                "coluna",
                "valor_atual",
                "problema",
                "orientacao"
            ]
        )

    return pd.DataFrame(problemas)
