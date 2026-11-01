
import pulp


def criar_modelo(alunos, turmas):

    modelo = pulp.LpProblem(
        "Equilibra_ABC",
        pulp.LpMinimize
    )

    x = {}

    # Variáveis de decisão
    for aluno in alunos:
        for turma in turmas:
            x[aluno["id"], turma["id"]] = pulp.LpVariable(
                f"x_{aluno['id']}_{turma['id']}",
                cat="Binary"
            )

    # Cada aluno deve estar em exatamente uma turma
    for aluno in alunos:
        modelo += pulp.lpSum(
            x[aluno["id"], turma["id"]]
            for turma in turmas
        ) == 1

    # Respeitar capacidade das turmas
    for turma in turmas:
        modelo += pulp.lpSum(
            x[aluno["id"], turma["id"]]
            for aluno in alunos
        ) <= turma["capacidade"]

    # Respeitar disponibilidade
    for aluno in alunos:
        for turma in turmas:
            if aluno["disponibilidade"] != turma["turno"]:
                modelo += x[aluno["id"], turma["id"]] == 0

    # Balanceamento quantitativo por turno
    desvios_quantidade = []

    for turno in ["MANHÃ", "TARDE"]:

        turmas_turno = [
            t for t in turmas
            if t["turno"] == turno
        ]

        if not turmas_turno:
            continue

        n_turmas = len(turmas_turno)

        total_turno = pulp.lpSum(
            x[a["id"], t["id"]]
            for a in alunos
            for t in turmas_turno
        )

        for turma in turmas_turno:

            quantidade = pulp.lpSum(
                x[a["id"], turma["id"]]
                for a in alunos
            )

            desvio = pulp.LpVariable(
                f"desvio_{turno}_{turma['id']}",
                lowBound=0
            )

            modelo += (
                n_turmas * quantidade - total_turno <= desvio
            )

            modelo += (
                total_turno - n_turmas * quantidade <= desvio
            )

            desvios_quantidade.append(desvio)

    # Balanceamento proporcional de gênero
    desvios_genero = []

    total_alunos = len(alunos)

    total_feminino = sum(
        1 for a in alunos if a["sexo"] == "F"
    )

    if total_alunos > 0:

        for turma in turmas:

            feminino = pulp.lpSum(
                x[a["id"], turma["id"]]
                for a in alunos
                if a["sexo"] == "F"
            )

            quantidade = pulp.lpSum(
                x[a["id"], turma["id"]]
                for a in alunos
            )

            desvio = pulp.LpVariable(
                f"genero_{turma['id']}",
                lowBound=0
            )

            diferenca = (
                total_alunos * feminino
                - total_feminino * quantidade
            )

            modelo += diferenca <= desvio
            modelo += -diferenca <= desvio

            desvios_genero.append(desvio)

    # Função objetivo
    modelo += (
        10 * pulp.lpSum(desvios_quantidade)
        + pulp.lpSum(desvios_genero)
    )

    return modelo, x
