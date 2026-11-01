
from src.etl import main


def test_etl_identifica_inconsistencias():
    resultado = main("instancia_4.xlsx")

    assert resultado["status"] == "inconsistencias"
    assert resultado["inconsistencias"] is not None
    assert len(resultado["inconsistencias"]) > 0


def test_etl_retorna_estrutura_padrao():
    resultado = main("instancia_4.xlsx")

    assert "status" in resultado
    assert "mensagem" in resultado
    assert "alunos" in resultado
    assert "turmas" in resultado
    assert "erros" in resultado
