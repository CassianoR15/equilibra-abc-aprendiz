"""
Responsável pela identificação e classificação de inconsistências.

Verifica valores ausentes ou inválidos, tipos inadequados,
nomes suspeitos, linhas vazias, duplicidades exatas,
conflitos de disponibilidade e homônimos.

Retorna um DataFrame com a linha, coluna, valor, categoria,
descrição do problema e orientação para correção.

As informações poderão ser apresentadas na interface para
que o usuário revise e corrija os problemas antes da otimização.
"""
import pandas as pd
import re
import unicodedata


# Verifica se um valor está vazio, considerando NaN, None e textos vazios
def valor_ausente(valor):

    if pd.isna(valor):
        return True

    if isinstance(valor, str) and valor.strip() == "":
        return True

    return False


# Verifica se o nome possui apenas números ou caracteres especiais
def verificar_nome_suspeito(nome):

    if not isinstance(nome, str):
        return False

    # Verifica se o nome contém pelo menos uma letra
    possui_letra = any(letra.isalpha() for letra in nome)

    return not possui_letra


# Normaliza o nome apenas para comparar possíveis duplicidades
# Não altera o nome original da tabela
def normalizar_nome_comparacao(nome):

    if not isinstance(nome, str):
        return nome

    nome = nome.strip().lower()
    nome = re.sub(r"\s+", " ", nome)

    # Remove acentos apenas para comparação
    nome = unicodedata.normalize("NFD", nome)
    nome = "".join(
        caractere for caractere in nome
        if unicodedata.category(caractere) != "Mn"
    )

    return nome


# 1. Verifica se os valores das colunas são strings
def verificar_tipos(df):

    problemas = []
    colunas = ["nome", "sexo", "disponibilidade"]

    for coluna in colunas:
        for indice, valor in df[coluna].items():

            if not valor_ausente(valor) and not isinstance(valor, str):

                problemas.append({
                    "linha": indice + 2,
                    "coluna": coluna,
                    "valor": valor,
                    "problema": "Tipo incorreto: esperado texto (string)"
                })

    return problemas


# 2. Verifica valores ausentes
def verificar_ausentes(df):

    problemas = []
    colunas = ["nome", "sexo", "disponibilidade"]

    for indice, linha in df.iterrows():

        # Verifica se a linha inteira está vazia
        if all(valor_ausente(linha[coluna]) for coluna in colunas):
            continue

        # Identifica os campos ausentes das linhas parcialmente preenchidas
        for coluna in colunas:

            if valor_ausente(linha[coluna]):

                problemas.append({
                    "linha": indice + 2,
                    "coluna": coluna,
                    "valor": linha[coluna],
                    "problema": "Valor ausente"
                })

    return problemas


# 3. Verifica se sexo e disponibilidade possuem valores permitidos
def verificar_valores_invalidos(df):

    problemas = []

    valores_sexo = ["F", "M"]
    valores_disponibilidade = ["MANHÃ", "TARDE"]

    for indice, linha in df.iterrows():

        sexo = linha["sexo"]
        disponibilidade = linha["disponibilidade"]

        if isinstance(sexo, str) and not valor_ausente(sexo):

            if sexo not in valores_sexo:

                problemas.append({
                    "linha": indice + 2,
                    "coluna": "sexo",
                    "valor": sexo,
                    "problema": "Valor de sexo inválido"
                })

        if isinstance(disponibilidade, str) and not valor_ausente(disponibilidade):

            if disponibilidade not in valores_disponibilidade:

                problemas.append({
                    "linha": indice + 2,
                    "coluna": "disponibilidade",
                    "valor": disponibilidade,
                    "problema": "Disponibilidade inválida"
                })

    return problemas


# 4. Verifica nomes suspeitos, sem letras
def verificar_nomes_suspeitos(df):

    problemas = []

    for indice, nome in df["nome"].items():

        if isinstance(nome, str) and not valor_ausente(nome):

            if verificar_nome_suspeito(nome):

                problemas.append({
                    "linha": indice + 2,
                    "coluna": "nome",
                    "valor": nome,
                    "problema": "Nome sem letras ou preenchido apenas com números/caracteres especiais"
                })

    return problemas


# 5. Identifica linhas totalmente vazias
def verificar_linhas_vazias(df):

    problemas = []
    colunas = ["nome", "sexo", "disponibilidade"]

    for indice, linha in df.iterrows():

        if all(valor_ausente(linha[coluna]) for coluna in colunas):

            problemas.append({
                "linha": indice + 2,
                "coluna": "todas",
                "valor": None,
                "problema": "Linha totalmente vazia"
            })

    return problemas


# 6. Identifica duplicidades exatas
def verificar_duplicados_exatos(df):

    problemas = []
    colunas = ["nome", "sexo", "disponibilidade"]

    # Considera somente registros completos e com tipos corretos
    mascara = df[colunas].apply(
        lambda linha: all(
            isinstance(valor, str) and not valor_ausente(valor)
            for valor in linha
        ),
        axis=1
    )

    dados = df.loc[mascara, colunas].copy()

    # Normaliza os nomes apenas para comparação
    dados["nome"] = dados["nome"].map(normalizar_nome_comparacao)

    # Identifica todas as ocorrências de registros repetidos
    duplicados = dados.duplicated(keep=False)

    # Agrupa os registros duplicados para facilitar a confirmação
    grupos = dados[duplicados].groupby(
        ["nome", "sexo", "disponibilidade"]
    )

    for _, grupo in grupos:

        linhas = [indice + 2 for indice in grupo.index]

        problemas.append({
            "linha": ", ".join(map(str, linhas)),
            "coluna": "todas",
            "valor": df.loc[grupo.index[0], "nome"],
            "problema": "Duplicidade exata: registros encontrados nas linhas " + ", ".join(map(str, linhas))
        })

    return problemas


# 7. Identifica possíveis conflitos de disponibilidade
def verificar_conflitos_disponibilidade(df):

    problemas = []

    # Considera somente registros com nome e sexo válidos
    mascara = (
        df["nome"].apply(
            lambda valor: isinstance(valor, str) and not valor_ausente(valor)
        )
        &
        df["sexo"].isin(["F", "M"])
        &
        df["disponibilidade"].isin(["MANHÃ", "TARDE"])
    )

    dados = df.loc[mascara].copy()

    dados["nome_comparacao"] = dados["nome"].map(
        normalizar_nome_comparacao
    )

    # Agrupa registros com o mesmo nome e sexo
    grupos = dados.groupby(
        ["nome_comparacao", "sexo"]
    )

    for _, grupo in grupos:

        disponibilidades = grupo["disponibilidade"].unique()

        # Verifica se existem disponibilidades diferentes
        if len(disponibilidades) > 1:

            for indice, linha in grupo.iterrows():

                problemas.append({
                    "linha": indice + 2,
                    "coluna": "disponibilidade",
                    "valor": linha["disponibilidade"],
                    "problema": "Possível conflito: mesmo nome e sexo com disponibilidades diferentes"
                })

    return problemas


# 8. Identifica possíveis homônimos
def verificar_homonimos(df):

    problemas = []

    # Considera somente registros com nome e sexo válidos
    mascara = (
        df["nome"].apply(
            lambda valor: isinstance(valor, str) and not valor_ausente(valor)
        )
        &
        df["sexo"].isin(["F", "M"])
    )

    dados = df.loc[mascara].copy()

    dados["nome_comparacao"] = dados["nome"].map(
        normalizar_nome_comparacao
    )

    grupos = dados.groupby("nome_comparacao")

    for _, grupo in grupos:

        if len(grupo) > 1:

            sexos = grupo["sexo"].unique()

            # Verifica se o mesmo nome aparece com sexos diferentes
            if len(sexos) > 1:

                for indice, linha in grupo.iterrows():

                    problemas.append({
                        "linha": indice + 2,
                        "coluna": "nome/sexo",
                        "valor": linha["nome"],
                        "problema": "Possível homônimo: mesmo nome com sexos diferentes. Revisar registros"
                    })

    return problemas


# Classifica os problemas encontrados
def classificar_problema(problema):

    if problema in ["Valor ausente", "Linha totalmente vazia"]:
        return "Preenchimento"

    elif "Tipo incorreto" in problema:
        return "Tipo/formato"

    elif "inválido" in problema or "inválida" in problema:
        return "Valor inválido"

    elif "Duplicidade" in problema or "duplicidade" in problema:
        return "Duplicidade"

    elif "conflito" in problema or "homônimo" in problema:
        return "Conflito de cadastro"

    elif "Nome sem letras" in problema:
        return "Dado suspeito"

    return "Não classificado"


# Orienta o usuário sobre como resolver cada problema
def orientar_correcao(problema):

    if "Duplicidade exata" in problema:
        return "Confirmar se os registros representam a mesma pessoa e, se sim, manter apenas um"

    elif "Valor ausente" in problema or "Linha totalmente vazia" in problema:
        return "Preencher os campos obrigatórios ou remover a linha vazia"

    elif "Tipo incorreto" in problema:
        return "Corrigir o valor para o formato de texto"

    elif "sexo inválido" in problema:
        return "Corrigir para F ou M"

    elif "Disponibilidade inválida" in problema:
        return "Corrigir para MANHÃ ou TARDE"

    elif "Nome sem letras" in problema:
        return "Conferir e preencher o nome corretamente"

    elif "conflito" in problema:
        return "Conferir se os registros pertencem à mesma pessoa e corrigir a disponibilidade"

    elif "homônimo" in problema:
        return "Conferir os cadastros para verificar se são pessoas diferentes"

    return "Revisar o registro na planilha"


# Reúne todas as inconsistências em um único relatório
def identificar_inconsistencias(df):

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

    # Executa todas as verificações e reúne os problemas encontrados
    for verificacao in verificacoes:
        problemas.extend(verificacao(df))

    # Se não houver inconsistências, não gera relatório
    if not problemas:
        return None

    # Organiza os problemas em formato de tabela
    relatorio = pd.DataFrame(problemas)

    # Adiciona a classificação e a orientação para cada problema
    relatorio["categoria"] = relatorio["problema"].map(
        classificar_problema
    )

    relatorio["orientacao"] = relatorio["problema"].map(
        orientar_correcao
    )

    # Organiza as colunas do relatório
    relatorio = relatorio[
        ["linha", "coluna", "valor", "categoria", "problema", "orientacao"]
    ]

    return relatorio
