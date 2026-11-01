
import streamlit as st
import pandas as pd

from src.etl import main as executar_etl
from src.integracao import integrar_com_otimizacao
from src.otimizador import otimizar_ensalamento


st.set_page_config(
    page_title="Equilibra",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Equilibra")
st.subheader("Sistema de distribuição equilibrada de alunos")

st.write(
    "Envie uma planilha Excel para validar os dados "
    "antes de executar a otimização."
)

arquivo = st.file_uploader(
    "Selecione a planilha",
    type=["xlsx", "xls"]
)


if arquivo is not None:

    # Guarda os dados da planilha na sessão
    if st.button("Validar planilha", type="primary"):

        with st.spinner("Analisando os dados..."):

            dados = executar_etl(arquivo)

            st.session_state["dados_etl"] = dados
            st.session_state["nome_arquivo"] = arquivo.name

            # Invalida resultados anteriores
            st.session_state.pop("resultado", None)


    dados = st.session_state.get("dados_etl")

    if (
        dados is not None
        and st.session_state.get("nome_arquivo") == arquivo.name
    ):

        st.divider()

        if dados["status"] == "inconsistencias":

            st.error(
                "Foram encontrados problemas. "
                "A otimização está bloqueada."
            )

            inconsistencias = dados["inconsistencias"]

            if inconsistencias is not None:

                st.subheader("Relatório de inconsistências")

                st.dataframe(
                    inconsistencias,
                    use_container_width=True,
                    hide_index=True
                )

                st.warning(
                    "Corrija os problemas na planilha original "
                    "e envie novamente para validação."
                )

            if dados["erros"]:

                with st.expander("Detalhes dos erros"):

                    for erro in dados["erros"]:
                        st.write(f"- {erro}")

        elif dados["status"] == "erro":

            st.error(dados["mensagem"])

            for erro in dados["erros"]:
                st.write(f"- {erro}")

        elif dados["status"] == "sucesso":

            st.success(
                "Planilha aprovada! Todos os dados passaram "
                "pelas validações."
            )

            st.metric(
                "Total de alunos",
                len(dados["alunos"])
            )

            st.metric(
                "Total de turmas",
                len(dados["turmas"])
            )

            st.subheader("Prévia dos alunos")

            st.dataframe(
                dados["alunos"].head(10),
                use_container_width=True,
                hide_index=True
            )

            if st.button(
                "Executar otimização",
                type="primary"
            ):

                try:

                    with st.spinner(
                        "Executando o modelo matemático..."
                    ):

                        resultado = integrar_com_otimizacao(
                            dados,
                            otimizar_ensalamento
                        )

                        st.session_state["resultado"] = resultado

                except Exception as erro:

                    st.error(
                        f"Não foi possível executar a otimização: {erro}"
                    )


    resultado = st.session_state.get("resultado")

    if resultado is not None:

        st.divider()
        st.subheader("Resultado da otimização")

        if resultado["status"] == "Optimal":

            st.success("Otimização concluída com sucesso!")

            alocacoes = pd.DataFrame(
                resultado["alocacoes"]
            )

            st.metric(
                "Alunos alocados",
                len(alocacoes)
            )

            st.dataframe(
                alocacoes,
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Distribuição por turma")

            distribuicao = (
                alocacoes.groupby("turma")
                .agg(
                    total=("id", "count"),
                    meninas=("sexo", lambda x: (x == "F").sum()),
                    meninos=("sexo", lambda x: (x == "M").sum())
                )
                .reset_index()
            )

            st.dataframe(
                distribuicao,
                use_container_width=True,
                hide_index=True
            )

            # Exportação do resultado
            excel = alocacoes.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                "Baixar resultado CSV",
                data=excel,
                file_name="resultado_equilibra.csv",
                mime="text/csv"
            )

        else:

            st.error(
                f"O modelo não encontrou solução ótima. "
                f"Status: {resultado['status']}"
            )

else:

    st.info("Aguardando o envio de uma planilha Excel.")
