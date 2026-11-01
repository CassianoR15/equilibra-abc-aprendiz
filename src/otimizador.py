
import pulp

from src.modelo import criar_modelo


def otimizar_ensalamento(alunos, turmas):

    # Adaptar dados do ETL para o modelo
    alunos_modelo = []

    for indice, aluno in alunos.iterrows():

        alunos_modelo.append({
            "id": indice + 1,
            "nome": aluno["nome"],
            "sexo": aluno["sexo"],
            "disponibilidade": aluno["disponibilidade"]
        })

    turmas_modelo = []

    for turma in turmas:

        turmas_modelo.append({
            "id": turma["id_turma"],
            "nome": turma["identificacao"],
            "turno": turma["turno"],
            "capacidade": turma["capacidade"]
        })

    modelo, variaveis = criar_modelo(
        alunos_modelo,
        turmas_modelo
    )

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    status = pulp.LpStatus[modelo.status]

    if status != "Optimal":
        return {
            "status": status,
            "alocacoes": []
        }

    alocacoes = []

    for aluno in alunos_modelo:

        for turma in turmas_modelo:

            valor = pulp.value(
                variaveis[aluno["id"], turma["id"]]
            )

            if valor is not None and valor > 0.5:

                alocacoes.append({
                    "id": aluno["id"],
                    "nome": aluno["nome"],
                    "sexo": aluno["sexo"],
                    "disponibilidade": aluno["disponibilidade"],
                    "turma": turma["nome"]
                })

    return {
        "status": status,
        "alocacoes": alocacoes,
        "objetivo": pulp.value(modelo.objective)
    }
