
from src.etl import ler_excel

print("INICIANDO TESTE DO ETL...")

try:
    alunos, turmas = ler_excel("instancia_1.xlsx")

    print("\n========== RESULTADO ==========")

    print("Total de alunos:", len(alunos))
    print("Total de turmas:", len(turmas))

    print("\nPRIMEIROS 5 ALUNOS:")

    for aluno in alunos[:5]:
        print(aluno)

    print("\nTURMAS:")

    for turma in turmas:
        print(turma)

    print("\nETL EXECUTADO COM SUCESSO!")

except Exception as erro:
    print("\nERRO NO ETL:")
    print(erro)

print("==============================")
