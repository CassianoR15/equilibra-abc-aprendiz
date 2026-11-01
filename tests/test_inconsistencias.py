
import pandas as pd

from src.inconsistencias import identificar_inconsistencias


def test_identifica_sexo_invalido():
    alunos = pd.DataFrame({
        "nome": ["Maria"],
        "sexo": ["X"],
        "disponibilidade": ["MANHÃ"]
    })

    resultado = identificar_inconsistencias(alunos)

    assert not resultado.empty
    assert "Sexo inválido" in resultado["problema"].values


def test_identifica_nome_vazio():
    alunos = pd.DataFrame({
        "nome": [None],
        "sexo": ["F"],
        "disponibilidade": ["MANHÃ"]
    })

    resultado = identificar_inconsistencias(alunos)

    assert not resultado.empty
    assert "Nome não preenchido" in resultado["problema"].values


def test_dados_validos_sem_inconsistencias():
    alunos = pd.DataFrame({
        "nome": ["Maria"],
        "sexo": ["F"],
        "disponibilidade": ["MANHÃ"]
    })

    resultado = identificar_inconsistencias(alunos)

    assert resultado.empty
