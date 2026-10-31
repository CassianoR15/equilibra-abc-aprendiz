"""
Módulo principal do processo ETL.

Responsável por coordenar as etapas de processamento dos dados
dos alunos, integrando os módulos de leitura, validação,
padronização e identificação de inconsistências.

Recebe a planilha enviada pelo usuário e executa o fluxo de
tratamento dos dados, retornando um resultado estruturado com
o status do processamento, os dados preparados, possíveis
inconsistências e duplicidades que precisam de confirmação.

Foi organizado para permitir a integração com a interface,
que poderá enviar o arquivo e apresentar os resultados ao
usuário antes de prosseguir para a etapa de otimização.
"""
import re
import unicodedata

# Importa as funções dos módulos do projeto
from src.leitura import ler_planilha
from src.validacao import validar_colunas
from src.padronizacao import padronizar_dados
from src.inconsistencias import identificar_inconsistencias

# Normaliza valores para comparar registros duplicados
def normalizar_valor(valor):

    if not isinstance(valor, str):
        return valor

    valor = valor.strip().upper()
    valor = re.sub(r"\s+", " ", valor)

    # Remove acentos para comparação
    valor = unicodedata.normalize("NFKD", valor)
    valor = "".join(
        caractere for caractere in valor
        if not unicodedata.combining(caractere)
    )

    return valor


# Cria uma chave para identificar um aluno
def criar_chave_aluno(linha):

    return (
        normalizar_valor(linha["nome"]),
        normalizar_valor(linha["sexo"]),
        normalizar_valor(linha["disponibilidade"])
    )


# Recupera as chaves dos grupos de duplicidades
def capturar_duplicidades(df, relatorio):

    chaves = set()

    duplicidades = relatorio[
        relatorio["problema"].str.contains(
            "Duplicidade exata",
            case=False,
            na=False
        )
    ]

    for _, duplicidade in duplicidades.iterrows():

        # Recupera os números das linhas indicadas no relatório
        linhas = [
            int(linha.strip())
            for linha in str(duplicidade["linha"]).split(",")
        ]

        # Identifica os registros correspondentes na tabela
        for numero_linha in linhas:

            indice = numero_linha - 2

            if 0 <= indice < len(df):

                aluno = df.iloc[indice]
                chaves.add(criar_chave_aluno(aluno))

    return chaves


# Remove somente as repetições confirmadas
def remover_duplicidades_confirmadas(df, chaves_confirmadas):

    if not chaves_confirmadas:
        return df.copy()

    # Padroniza uma cópia para realizar a comparação
    df_tratado = padronizar_dados(df)

    indices_remover = []
    chaves_encontradas = set()

    for indice, (_, aluno) in enumerate(df_tratado.iterrows()):

        chave = criar_chave_aluno(aluno)

        # Considera apenas os grupos de duplicidade confirmados
        if chave in chaves_confirmadas:

            if chave in chaves_encontradas:
                indices_remover.append(indice)
            else:
                chaves_encontradas.add(chave)

    # Remove as repetições apenas da tabela em memória
    df = df.drop(
        df.index[indices_remover]
    ).reset_index(drop=True)

    return df


# Organiza o retorno do processamento
def criar_retorno(
    status,
    mensagem,
    alunos=None,
    relatorio=None,
    duplicidades_pendentes=None
):

    return {
        "status": status,
        "mensagem": mensagem,
        "alunos": alunos,
        "relatorio": relatorio,
        "duplicidades_pendentes": (
            duplicidades_pendentes
            if duplicidades_pendentes is not None
            else set()
        )
    }


# Função principal do ETL
def main(arquivo, duplicidades_confirmadas=None):

    # Guarda as duplicidades que o usuário já confirmou
    if duplicidades_confirmadas is None:
        duplicidades_confirmadas = set()

    try:

        # 1. Realiza a leitura da planilha
        df = ler_planilha(arquivo)

        # 2. Verifica se as colunas obrigatórias estão presentes
        problemas_estruturais = validar_colunas(df)

        if problemas_estruturais:

            return criar_retorno(
                status="erro_estrutural",
                mensagem="A planilha possui problemas na estrutura.",
                relatorio=problemas_estruturais
            )

        # 3. Padroniza os nomes das colunas para os próximos módulos
        df.columns = [
            str(coluna).strip().lower()
            for coluna in df.columns
        ]

        # 4. Remove as duplicidades que já foram confirmadas
        df = remover_duplicidades_confirmadas(
            df,
            duplicidades_confirmadas
        )

        # 5. Padroniza os dados dos alunos
        df_tratado = padronizar_dados(df)

        # 6. Identifica as inconsistências
        relatorio = identificar_inconsistencias(df_tratado)

        # 7. Verifica se existem inconsistências
        if relatorio is not None:

            # Identifica as duplicidades ainda não confirmadas
            chaves_encontradas = capturar_duplicidades(
                df_tratado,
                relatorio
            )

            novas_duplicidades = (
                chaves_encontradas - duplicidades_confirmadas
            )

            # Se não houver outros problemas, aguarda a confirmação
            outros_problemas = relatorio[
                ~relatorio["problema"].str.contains(
                    "Duplicidade exata",
                    case=False,
                    na=False
                )
            ]

            if not outros_problemas.empty:

                return criar_retorno(
                    status="inconsistencias",
                    mensagem=(
                        "Foram encontradas inconsistências "
                        "que precisam ser verificadas."
                    ),
                    relatorio=relatorio,
                    duplicidades_pendentes=novas_duplicidades
                )

            if novas_duplicidades:

                return criar_retorno(
                    status="aguardando_confirmacao_duplicidades",
                    mensagem=(
                        "Foram encontrados possíveis registros "
                        "duplicados. É necessária a confirmação."
                    ),
                    relatorio=relatorio,
                    duplicidades_pendentes=novas_duplicidades
                )

        # 8. Planilha validada
        return criar_retorno(
            status="planilha_validada",
            mensagem="Planilha validada com sucesso.",
            alunos=df_tratado
        )

    except FileNotFoundError as erro:

        return criar_retorno(
            status="erro",
            mensagem=str(erro)
        )

    except PermissionError:

        return criar_retorno(
            status="erro",
            mensagem=(
                "Não foi possível acessar o arquivo. "
                "Verifique se ele está aberto em outro programa."
            )
        )

    except ValueError as erro:

        return criar_retorno(
            status="erro",
            mensagem=str(erro)
        )
