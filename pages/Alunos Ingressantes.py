import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide")

# ---------- Função para carregar e limpar dados ----------
def carregar_dados():
    caminho = os.path.join("datasets", "alunos-ingressantes.csv")
    df = pd.read_csv(caminho, sep=";", encoding="latin-1")
    df.columns = df.columns.str.strip()

    df = df[df["Curso"].notna() & df["Campus"].notna() & df["AnoAdmissao"].notna()]
    df["AnoAdmissao"] = pd.to_numeric(df["AnoAdmissao"], errors="coerce").dropna().astype(int)

    df["Curso"] = df["Curso"].replace([
        "Física - Licenciatura", 
        "Matemática - Licenciatura",
        "Química - Licenciatura",
        "Educação Física - Licenciatura",
        "Ciências Biológicas - Licenciatura"
    ], [
        "Física", 
        "Matemática",
        "Química",
        "Educação Física",
        "Ciências Biológicas"
    ])

    return df

# ---------- Carregamento dos dados ----------
df = carregar_dados()

# ---------- FILTRO NA SIDEBAR: CAMPUS ----------
with st.sidebar.expander("🎛️ Filtros", expanded=True):
    st.markdown("### Filtro por Campus")
    campi = sorted(df["Campus"].unique().tolist())

    filtro_campi = st.multiselect(
        "Selecione os campi:",
        options=campi,
        default=campi,
        help="Você pode selecionar um ou mais campi."
    )

    if not filtro_campi:
        st.warning("Selecione ao menos um campus para visualizar os dados.")
        st.stop()

    # ---------- FILTRO ADICIONAL: ANO ----------
    st.markdown("### Filtro por Ano")
    anos = sorted(df["AnoAdmissao"].unique().tolist())
    min_ano, max_ano = min(anos), max(anos)
    filtro_ano = st.slider(
        "Selecione o intervalo de anos:",
        min_value=min_ano,
        max_value=max_ano,
        value=(min_ano, max_ano)
    )

# ---------- Filtrar cursos com base nos campi selecionados ----------
df_filtrado_campi = df[df["Campus"].isin(filtro_campi)]
df_filtrado_campi = df_filtrado_campi[df_filtrado_campi["AnoAdmissao"].between(filtro_ano[0], filtro_ano[1])]
df_filtrado_campi["Curso_Campus"] = df_filtrado_campi["Curso"] + " (" + df_filtrado_campi["Campus"] + ")"
opcoes_curso_campus = sorted(df_filtrado_campi["Curso_Campus"].unique())

# ---------- TÍTULO E FILTRO DE CURSO ----------
st.title("📊 Ingressantes por Ano")

curso_selecionado = st.selectbox(
    "Curso (por campus):",
    options=opcoes_curso_campus,
    help="Os cursos estão diferenciados por campus."
)

# Extrai o nome do curso e campus separadamente
curso_base = curso_selecionado.split(" (")[0]
campus_base = curso_selecionado.split(" (")[1].replace(")", "")

# ---------- Aplicar todos os filtros ----------
df_filtrado = df_filtrado_campi[
    (df_filtrado_campi["Curso"] == curso_base) & 
    (df_filtrado_campi["Campus"] == campus_base)
]

# ---------- GRÁFICO GERAL: Ingressantes por Ano ----------
df_ano = df_filtrado.groupby("AnoAdmissao").size().reset_index(name="Ingressantes")

st.markdown(f"**Campus:** {campus_base} &nbsp;&nbsp;&nbsp; **Curso:** {curso_base} &nbsp;&nbsp;&nbsp; **Período:** {filtro_ano[0]}-{filtro_ano[1]}")

fig_ano = px.bar(
    df_ano,
    x="AnoAdmissao",
    y="Ingressantes",
    title="Total de ingressantes por ano",
    labels={"AnoAdmissao": "Ano", "Ingressantes": "Total de Ingressantes"},
    height=600
)
fig_ano.update_layout(xaxis_title="Ano de Admissão", yaxis_title="Ingressantes")
st.plotly_chart(fig_ano, use_container_width=True)
