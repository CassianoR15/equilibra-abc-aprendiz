
import pulp

from src.modelo import criar_modelo


def criar_dados():
    alunos = [
        {"id": 1, "nome": "Ana", "sexo": "F", "disponibilidade": "MANHÃ"},
        {"id": 2, "nome": "João", "sexo": "M", "disponibilidade": "MANHÃ"},
        {"id": 3, "nome": "Maria", "sexo": "F", "disponibilidade": "TARDE"},
        {"id": 4, "nome": "Pedro", "sexo": "M", "disponibilidade": "TARDE"},
    ]

    turmas = [
        {"id": 1, "nome": "Turma A", "turno": "MANHÃ", "capacidade": 2},
        {"id": 2, "nome": "Turma B", "turno": "TARDE", "capacidade": 2},
    ]

    return alunos, turmas


def test_modelo_encontra_solucao_otima():
    alunos, turmas = criar_dados()

    modelo, variaveis = criar_modelo(alunos, turmas)

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    assert pulp.LpStatus[modelo.status] == "Optimal"


def test_todos_alunos_sao_alocados():
    alunos, turmas = criar_dados()

    modelo, variaveis = criar_modelo(alunos, turmas)

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    assert pulp.LpStatus[modelo.status] == "Optimal"

    for aluno in alunos:
        total = sum(
            pulp.value(variaveis[aluno["id"], turma["id"]])
            for turma in turmas
        )

        assert total == 1


def test_capacidade_das_turmas_e_respeitada():
    alunos, turmas = criar_dados()

    modelo, variaveis = criar_modelo(alunos, turmas)

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    assert pulp.LpStatus[modelo.status] == "Optimal"

    for turma in turmas:
        total = sum(
            pulp.value(variaveis[aluno["id"], turma["id"]])
            for aluno in alunos
        )

        assert total <= turma["capacidade"]


def test_disponibilidade_e_respeitada():
    alunos, turmas = criar_dados()

    modelo, variaveis = criar_modelo(alunos, turmas)

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    assert pulp.LpStatus[modelo.status] == "Optimal"

    for aluno in alunos:
        for turma in turmas:
            if aluno["disponibilidade"] != turma["turno"]:
                assert pulp.value(
                    variaveis[aluno["id"], turma["id"]]
                ) == 0
