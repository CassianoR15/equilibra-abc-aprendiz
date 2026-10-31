
import streamlit as st

# --------------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------------

st.set_page_config(
    page_title="ABC Aprendiz | Gestão de Turmas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

AZUL = "#2A469A"
VERDE = "#9CCD58"
TURQUESA = "#3DBD9D"
PETROLEO = "#2E9587"

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "Dashboard"


# --------------------------------------------------
# ESTILO
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Lato', sans-serif;
}

.stApp {
    background: #F4F7FA;
}

[data-testid="stHeader"] {
    background: transparent;
}

/* --------------------------------------------------
   BARRA LATERAL FIXA
-------------------------------------------------- */

/* Mantém a barra sempre visível e expandida */

section[data-testid="stSidebar"] {
    background: #C8D7F5 !important;
    border-right: 1px solid #AFC2E8 !important;

    width: 250px !important;
    min-width: 250px !important;
    max-width: 250px !important;

    display: block !important;
    visibility: visible !important;
    transform: translateX(0) !important;
    margin-left: 0 !important;
}

/* Mantém a largura mesmo quando o Streamlit tenta recolher */

section[data-testid="stSidebar"][aria-expanded="false"] {
    width: 250px !important;
    min-width: 250px !important;
    max-width: 250px !important;

    visibility: visible !important;
    transform: translateX(0) !important;
    margin-left: 0 !important;
}

/* Área interna da barra */

[data-testid="stSidebar"] > div:first-child {
    background: #C8D7F5 !important;
    width: 250px !important;
    min-width: 250px !important;
    padding-top: 1.5rem;
}

[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background: #C8D7F5 !important;
}

/* Remove as setinhas de recolher e expandir */

[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarExpandButton"],
[data-testid="collapsedControl"],
button[data-testid="baseButton-headerNoPadding"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}

/* Esconde a navegação padrão do Streamlit */

[data-testid="stSidebarNav"] {
    display: none !important;
}

/* --------------------------------------------------
   NAVEGAÇÃO
-------------------------------------------------- */

.sidebar-title {
    color: #263F83;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    margin: 8px 0 18px 5px;
}

[data-testid="stSidebar"] [data-testid="stButton"] {
    width: 100%;
    margin-bottom: 9px;
}

[data-testid="stSidebar"] [data-testid="stButton"] button {
    width: 100%;
    min-height: 54px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 12px;
    background: transparent;
    color: #263F83;
    border: 1px solid transparent;
    border-radius: 11px;
    text-align: left;
    padding: 12px 15px;
    font-size: 14px;
    font-weight: 700;
}

/* Ícones */

[data-testid="stSidebar"] [data-testid="stButton"] button [data-testid="stIconMaterial"] {
    color: #2A469A !important;
    font-size: 23px !important;
    min-width: 24px;
}

[data-testid="stSidebar"] [data-testid="stButton"] button svg {
    color: #2A469A !important;
    fill: #2A469A !important;
}

/* Texto */

[data-testid="stSidebar"] [data-testid="stButton"] button [data-testid="stMarkdownContainer"] {
    display: flex;
    align-items: center;
    text-align: left;
}

[data-testid="stSidebar"] [data-testid="stButton"] button p {
    margin: 0;
    text-align: left;
    color: inherit !important;
    font-size: 14px;
    font-weight: 700;
}

/* Efeito ao passar o mouse */

[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    background: rgba(255, 255, 255, 0.65) !important;
    color: #263F83 !important;
    border-color: rgba(42, 70, 154, 0.12);
}

/* Página selecionada */

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
    background: #FFFFFF !important;
    color: #2A469A !important;
    border: 1px solid #B7C8EA !important;
    box-shadow: 0 2px 8px rgba(42, 70, 154, 0.08);
}

[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] p,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] [data-testid="stIconMaterial"] {
    color: #2A469A !important;
}

.sidebar-description {
    color: #53658C;
    font-size: 12px;
    line-height: 1.8;
}

/* --------------------------------------------------
   CABEÇALHO
-------------------------------------------------- */

.header-label {
    color: #2E9587;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.5px;
    margin-bottom: 7px;
}

.header-subtitle {
    color: #65718A;
    font-size: 14px;
    margin-top: 5px;
}

h1, h2, h3 {
    color: #2A469A !important;
    font-family: 'Lato', sans-serif !important;
}

/* --------------------------------------------------
   CARTÕES
-------------------------------------------------- */

.metric-card, .content-card {
    background: white;
    border: 1px solid #E6EBF3;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 3px 12px rgba(42,70,154,0.04);
}

.metric-card {
    min-height: 125px;
}

.metric-top {
    display: flex;
    align-items: center;
    gap: 9px;
    color: #65718A;
    font-size: 13px;
    font-weight: 600;
}

.metric-value {
    color: #2A469A;
    font-size: 29px;
    font-weight: 800;
    margin-top: 13px;
}

.metric-line {
    width: 35px;
    height: 4px;
    border-radius: 5px;
    margin-top: 9px;
}

.section-title {
    color: #2A469A;
    font-size: 19px;
    font-weight: 700;
    margin-top: 28px;
    margin-bottom: 15px;
}

.empty-title {
    color: #2A469A;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 8px;
}

.empty-text {
    color: #65718A;
    font-size: 14px;
    line-height: 1.7;
}

/* --------------------------------------------------
   INFORMAÇÕES
-------------------------------------------------- */

.info-card {
    background: #EEF3FF;
    border-left: 4px solid #2A469A;
    border-radius: 10px;
    padding: 16px 18px;
    color: #40547E;
    font-size: 13px;
    line-height: 1.7;
}

.step-card {
    background: white;
    border: 1px solid #E6EBF3;
    border-radius: 12px;
    padding: 17px;
    min-height: 120px;
}

.step-number {
    color: #2E9587;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1px;
}

.step-name {
    color: #2A469A;
    font-size: 15px;
    font-weight: 700;
    margin-top: 8px;
}

.step-description {
    color: #65718A;
    font-size: 12px;
    margin-top: 5px;
    line-height: 1.5;
}

/* --------------------------------------------------
   BOTÕES GERAIS
-------------------------------------------------- */

.stButton button[kind="primary"] {
    background: #2A469A;
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 600;
}

.stButton button[kind="primary"]:hover {
    background: #203879;
    border: none;
}

/* --------------------------------------------------
   IMPORTAÇÃO
-------------------------------------------------- */

[data-testid="stFileUploader"] {
    background: #FFFFFF;
    border: 1px dashed #9BAED5;
    border-radius: 12px;
    padding: 12px;
}

/* --------------------------------------------------
   RODAPÉ
-------------------------------------------------- */

.footer {
    color: #8993A6;
    font-size: 11px;
    text-align: center;
    margin-top: 45px;
    padding: 15px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# MENU LATERAL
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        """
        <p class="sidebar-title">
            NAVEGAÇÃO
        </p>
        """,
        unsafe_allow_html=True
    )

    opcoes = [
        ("Dashboard", ":material/dashboard:"),
        ("Importação de dados", ":material/folder_open:"),
        ("Resultados", ":material/insert_chart_outlined:")
    ]

    for nome, icone in opcoes:

        pagina_ativa = st.session_state["pagina"] == nome

        if st.button(
            nome,
            key=f"menu_{nome}",
            icon=icone,
            type="primary" if pagina_ativa else "secondary",
            use_container_width=True
        ):
            st.session_state["pagina"] = nome
            st.rerun()

    st.markdown("---")

    st.markdown(
        """
        <div class="sidebar-description">
            Sistema de distribuição de alunos.<br><br>
            Organização, equilíbrio e oportunidades.
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# CABEÇALHO PRINCIPAL
# --------------------------------------------------

col_logo, col_texto = st.columns([1.7, 4])

with col_logo:
    st.image(
        "interface/assets/logo_abc_aprendiz.png",
        width=300
    )

with col_texto:
    st.markdown(
        """
        <div style="padding-top:12px;">
            <div class="header-label">
                ABC APRENDIZ • GESTÃO DE TURMAS
            </div>
            <div class="header-subtitle">
                Sistema de distribuição inteligente de alunos.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("""
<div style="
    height:3px;
    background:linear-gradient(90deg,#2A469A,#3DBD9D,#9CCD58);
    border-radius:5px;
    margin:18px 0 25px;">
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# PÁGINA 1 - DASHBOARD
# --------------------------------------------------

if st.session_state["pagina"] == "Dashboard":

    st.title("Visão geral")

    st.markdown(
        "<p style='color:#65718A;font-size:14px;'>"
        "Acompanhe os dados e a distribuição das turmas em um só lugar."
        "</p>",
        unsafe_allow_html=True
    )

    indicadores = [
        ("Total de alunos", "—", AZUL),
        ("Total de turmas", "—", TURQUESA),
        ("Capacidade total", "—", VERDE),
        ("Vagas ocupadas", "—", PETROLEO),
        ("Vagas disponíveis", "—", "#E5A83B")
    ]

    colunas = st.columns(5)

    for coluna, (titulo, valor, cor) in zip(colunas, indicadores):

        with coluna:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-top">{titulo}</div>
                    <div class="metric-value">{valor}</div>
                    <div class="metric-line" style="background:{cor};"></div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        "<div class='section-title'>Distribuição das turmas</div>",
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="content-card">
        <div style="font-size:30px;margin-bottom:12px;">📂</div>
        <div class="empty-title">
            Sua distribuição ainda não começou!
        </div>
        <div class="empty-text">
            Importe a planilha com os dados dos alunos e das turmas.
            Depois, o sistema poderá organizar as informações e
            preparar a distribuição.
        </div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# PÁGINA 2 - IMPORTAÇÃO DE DADOS
# --------------------------------------------------

elif st.session_state["pagina"] == "Importação de dados":

    st.title("Importação de dados")

    st.markdown(
        "<p style='color:#65718A;font-size:14px;'>"
        "Envie a planilha com as informações dos alunos e das turmas."
        "</p>",
        unsafe_allow_html=True
    )

    etapas = st.columns(3)

    etapas_info = [
        ("01", "Importar planilha", "Envie o arquivo Excel."),
        ("02", "Validar informações", "Confira os dados enviados."),
        ("03", "Gerar distribuição", "Prepare a organização das turmas.")
    ]

    for coluna, (numero, nome, descricao) in zip(etapas, etapas_info):

        with coluna:
            st.markdown(
                f"""
                <div class="step-card">
                    <div class="step-number">ETAPA {numero}</div>
                    <div class="step-name">{nome}</div>
                    <div class="step-description">{descricao}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        "<div class='section-title'>Envio da planilha</div>",
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-card">
        <b>Antes de enviar:</b> organize o arquivo Excel com duas abas:
        <b>Alunos</b> e <b>Turmas</b>. Os dados devem seguir o modelo
        solicitado para que possam ser validados corretamente.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    arquivo = st.file_uploader(
        "Selecione sua planilha Excel",
        type=["xlsx", "xls"],
        help="Selecione um arquivo no formato .xlsx ou .xls."
    )

    if arquivo is not None:
        st.success(f"Arquivo selecionado: {arquivo.name}")
        st.caption(
            "A validação e o processamento serão integrados na próxima etapa."
        )

    st.markdown(
        "<div class='section-title'>Estrutura esperada</div>",
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="content-card">
            <div style="color:#2E9587;font-size:13px;font-weight:800;">
                ABA 01
            </div>
            <div class="empty-title" style="font-size:17px;">
                Alunos
            </div>
            <div class="empty-text">
                Informações dos alunos, como nome, sexo e disponibilidade.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="content-card">
            <div style="color:#2E9587;font-size:13px;font-weight:800;">
                ABA 02
            </div>
            <div class="empty-title" style="font-size:17px;">
                Turmas
            </div>
            <div class="empty-text">
                Informações sobre turnos, quantidade de turmas e capacidade.
            </div>
        </div>
        """, unsafe_allow_html=True)


# --------------------------------------------------
# PÁGINA 3 - RESULTADOS
# --------------------------------------------------

elif st.session_state["pagina"] == "Resultados":

    st.title("Resultados")

    st.markdown(
        "<p style='color:#65718A;font-size:14px;'>"
        "Visualize os resultados da distribuição realizada."
        "</p>",
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="content-card">
        <div style="font-size:30px;margin-bottom:12px;">📊</div>
        <div class="empty-title">
            Os resultados aparecerão aqui
        </div>
        <div class="empty-text">
            Depois que os dados forem processados e a distribuição
            for realizada, você poderá acompanhar os resultados,
            consultar as turmas e visualizar os alunos alocados.
        </div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# RODAPÉ
# --------------------------------------------------

st.markdown("""
<div class="footer">
    ABC APRENDIZ • Centro Social de Educação para o Trabalho<br>
    Sistema de distribuição inteligente de alunos
</div>
""", unsafe_allow_html=True)

