
def integrar_com_otimizacao(dados, funcao_otimizacao):

    # Recebe os dados preparados pelo ETL
    alunos = dados["alunos"]
    turmas = dados["turmas"]

    # Encaminha os dados para o modelo matemático
    resultado = funcao_otimizacao(
        alunos=alunos,
        turmas=turmas
    )

    # Retorna o resultado da otimização
    return resultado


def gerar_excel(resultado, caminho="resultado_otimizacao.xlsx"):

    # A estrutura das tabelas será definida
    # conforme o formato retornado pela otimização.

    pass
