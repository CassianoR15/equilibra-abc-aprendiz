
import pandas as pd

from src.padronizacao import padronizar_dados


def test_padronizacao_retorna_dicionario():
    dados = {
        "alunos": pd.DataFrame({
            "nome": ["  Maria Silva  "],
            "sexo": ["f"],
            "disponibilidade": ["manhã"]
        }),
        "turmas": pd.DataFrame({
            "identificacao": ["Turma A"],
            "turno": ["MANHÃ"],
            "capacidade": [30]
        })
    }

    resultado = padronizar_dados(dados)

    assert isinstance(resultado, dict)
    assert "alunos" in resultado
    assert "turmas" in resultado


def test_padronizacao_remove_espacos_do_nome():
    dados = {
        "alunos": pd.DataFrame({
            "nome": ["  Maria Silva  "],
            "sexo": ["f"],
            "disponibilidade": ["manhã"]
        }),
        "turmas": pd.DataFrame({
            "identificacao": ["Turma A"],
            "turno": ["MANHÃ"],
            "capacidade": [30]
        })
    }

    resultado = padronizar_dados(dados)

    assert resultado["alunos"].iloc[0]["nome"] == "Maria Silva"
