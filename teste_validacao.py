
from src.etl import ler_excel
from src.validacao import validar_dados

print("INICIANDO TESTE DE VALIDAÇÃO...")

try:

    alunos, turmas = ler_excel("instancia_1.xlsx")

    resultado = validar_dados(alunos, turmas)

    print("\n========== VALIDAÇÃO ==========")

    print("Resultado:", resultado["valido"])

    if resultado["valido"]:

        print("Total de alunos:", resultado["total_alunos"])
        print("Total de turmas:", resultado["total_turmas"])
        print("Capacidade total:", resultado["capacidade_total"])

        print("\nTODOS OS DADOS SÃO VÁLIDOS!")

    else:

        print("\nERROS ENCONTRADOS:")

        for erro in resultado["erros"]:
            print("-", erro)

    print("===============================")

except Exception as erro:

    print("ERRO:", erro)

print("\n========== TESTE DE ERRO ==========")

alunos_teste = [
    {
        "id": 1,
        "nome": "",
        "sexo": "X",
        "disponibilidade": []
    }
]

turmas_teste = [
    {
        "id": 1,
        "turno": "NOITE",
        "capacidade": 0
    }
]

resultado_teste = validar_dados(
    alunos_teste,
    turmas_teste
)

print("Dados válidos:", resultado_teste["valido"])

print("Erros encontrados:")

for erro in resultado_teste["erros"]:
    print("-", erro)

print("===================================")