
# Colunas obrigatórias da tabela de alunos
COLUNAS_OBRIGATORIAS = [
    "nome",
    "sexo",
    "disponibilidade"
]


# Validação das colunas obrigatórias
def validar_colunas(df):

    # 1. Padroniza os nomes das colunas apenas para comparação
    colunas = [
        str(coluna).strip().lower()
        for coluna in df.columns
    ]

    # 2. Identifica as colunas obrigatórias ausentes
    colunas_faltantes = [
        coluna for coluna in COLUNAS_OBRIGATORIAS
        if coluna not in colunas
    ]

    # 3. Retorna os erros encontrados
    if colunas_faltantes:
        return [
            f"Colunas obrigatórias ausentes: {colunas_faltantes}"
        ]

    return []
