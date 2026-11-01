
from src.otimizador import otimizar_ensalamento


def test_otimizador_encontra_solucao():
    alunos = [
        {"nome": "Ana", "sexo": "F", "disponibilidade": "MANHÃ"},
        {"nome": "João", "sexo": "M", "disponibilidade": "MANHÃ"},
        {"nome": "Maria", "sexo": "F", "disponibilidade": "TARDE"},
        {"nome": "Pedro", "sexo": "M", "disponibilidade": "TARDE"},
    ]

    import pandas as pd
    alunos = pd.DataFrame(alunos)

    turmas = [
        {
            "id_turma": 1,
            "identificacao": "Turma A",
            "turno": "MANHÃ",
            "capacidade": 2
        },
        {
            "id_turma": 2,
            "identificacao": "Turma B",
            "turno": "TARDE",
            "capacidade": 2
        }
    ]

    resultado = otimizar_ensalamento(alunos, turmas)

    assert resultado["status"] == "Optimal"
    assert len(resultado["alocacoes"]) == 4


def test_todos_alunos_recebem_turma():
    import pandas as pd

    alunos = pd.DataFrame([
        {"nome": "Ana", "sexo": "F", "disponibilidade": "MANHÃ"},
        {"nome": "João", "sexo": "M", "disponibilidade": "MANHÃ"}
    ])

    turmas = [
        {
            "id_turma": 1,
            "identificacao": "Turma A",
            "turno": "MANHÃ",
            "capacidade": 2
        }
    ]

    resultado = otimizar_ensalamento(alunos, turmas)

    assert resultado["status"] == "Optimal"
    assert len(resultado["alocacoes"]) == len(alunos)

