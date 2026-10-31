"""
Responsável pela limpeza e padronização dos dados dos alunos.

Remove espaços desnecessários, padroniza a escrita dos nomes,
os valores de sexo e as disponibilidades, preparando os dados
para as verificações e para o modelo de otimização.
"""
import re

# Remove espaços no início e no final e substitui espaços repetidos por apenas um
def limpar_espacos(valor):

    if isinstance(valor, str):
        valor = valor.strip()
        valor = re.sub(r"\s+", " ", valor)
    return valor

#Padroniza os valores da tabela de alunos
def padronizar_dados(df):

    #Cria uma cópia da tabela para preservar os dados originais
    df = df.copy()

    #1. Limpa os espaços extras nas três colunas
    colunas = ["nome", "sexo", "disponibilidade"]

    for coluna in colunas:
        df[coluna] = df[coluna].map(limpar_espacos)

    #2. Padroniza os nomes, deixando a primeira letra de cada palavra maiúscula
    df["nome"] = df["nome"].map(
        lambda valor: valor.title()
        if isinstance(valor, str) else valor
    )

    #3. Padroniza o sexo, convertendo as diferentes formas de escrita para F ou M
    equivalencia_sexo = {
        "F": "F",
        "FEM": "F",
        "FEMININO": "F",
        "M": "M",
        "MASC": "M",
        "MASCULINO": "M"
    }

    #Converte os valores para maiúsculo antes de verificar as equivalências
    df["sexo"] = df["sexo"].map(
        lambda valor: equivalencia_sexo.get(
            valor.upper(), valor.upper()
        ) if isinstance(valor, str) else valor
    )

    #4. Padroniza a disponibilidade, uniformizando maiúsculas e acentuação
    equivalencia_disponibilidade = {
        "MANHA": "MANHÃ",
        "MANHÃ": "MANHÃ",
        "TARDE": "TARDE"
    }

    #Converte os valores para maiúsculo e aplica as equivalências definidas
    df["disponibilidade"] = df["disponibilidade"].map(
        lambda valor: equivalencia_disponibilidade.get(
            valor.upper(), valor.upper()
        ) if isinstance(valor, str) else valor
    )
    #Retorna a tabela com os valores padronizados
    return df
