
from src.etl import main
from src.otimizador import otimizar_ensalamento

import pandas as pd


instancias = [
    "instancia_1.xlsx",
    "instancia_2.xlsx",
    "instancia_3.xlsx",
    "instancia_4.xlsx"
]


for arquivo in instancias:

    print("\n" + "=" * 50)
    print(f"TESTANDO: {arquivo}")
    print("=" * 50)

    try:
        dados = main(arquivo)

        alunos = dados["alunos"]
        turmas = dados["turmas"]

        resultado = otimizar_ensalamento(alunos, turmas)

        print("Status:", resultado["status"])
        print("Alunos recebidos:", len(alunos))
        print("Alunos alocados:", len(resultado["alocacoes"]))
        print("Quantidade de turmas:", len(turmas))

        if resultado["status"] == "Optimal":

            df = pd.DataFrame(resultado["alocacoes"])

            print("\nDistribuição:")

            print(
                df.groupby(["turma", "disponibilidade"])
                .agg(
                    total=("id", "count"),
                    meninas=("sexo", lambda x: (x == "F").sum()),
                    meninos=("sexo", lambda x: (x == "M").sum())
                )
                .to_string()
            )

        else:
            print("ATENÇÃO: Não foi encontrada solução ótima.")

    except Exception as erro:
        print("ERRO:", erro)
