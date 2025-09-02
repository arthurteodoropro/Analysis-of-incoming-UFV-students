import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide")
st.title("🗺️ Distribuição dos Alunos por Naturalidade")

# ---------- Carregar dados ----------
@st.cache_data
def carregar_dados():
    caminho = os.path.join("datasets", "alunos-ingressantes.csv")
    df = pd.read_csv(caminho, sep=";", encoding="latin-1")
    df.columns = df.columns.str.strip()
    df = df[df["Naturalidade"].notna() & df["Curso"].notna() & df["Campus"].notna() & df["UF"].notna()]
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

@st.cache_data
def carregar_coordenadas():
    df_geo = pd.read_csv("datasets/dados_geocodificados.csv")
    df_geo["Naturalidade"] = df_geo["Naturalidade"].str.strip()
    return df_geo

df = carregar_dados()
df_geo = carregar_coordenadas()

# ---------- Filtros ----------
with st.sidebar.expander("🎛️ Filtros", expanded=True):
    st.markdown("### Filtro por Campus")
    campi = sorted(df["Campus"].unique().tolist())

    filtro_campi = st.multiselect(
        "Selecione os campi:",
        options=campi,
        default=campi
    )

    if not filtro_campi:
        st.warning("Selecione ao menos um campus.")
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

    # Filtrar dados pelo(s) campus
    df_filtrado_campi = df[df["Campus"].isin(filtro_campi)]
    df_filtrado_campi = df_filtrado_campi[df_filtrado_campi["AnoAdmissao"].between(filtro_ano[0], filtro_ano[1])]
    df_filtrado_campi["Curso_Campus"] = df_filtrado_campi["Curso"] + " (" + df_filtrado_campi["Campus"] + ")"

    # Adicionar "Todos os cursos"
    opcoes_curso = sorted(df_filtrado_campi["Curso_Campus"].unique())
    opcoes_curso.insert(0, "Todos os cursos")

    curso_selecionado = st.selectbox(
        "Curso (por campus):",
        options=opcoes_curso,
        help="Você pode ver todos os cursos do campus selecionado, ou apenas um curso específico."
    )

# ---------- Aplicar filtro final ----------
if curso_selecionado == "Todos os cursos":
    df_filtrado = df_filtrado_campi.copy()
    titulo_mapa = f"Todos os cursos ({', '.join(filtro_campi)}) - {filtro_ano[0]}-{filtro_ano[1]}"
else:
    curso_base = curso_selecionado.split(" (")[0]
    campus_base = curso_selecionado.split(" (")[1].replace(")", "")

    df_filtrado = df_filtrado_campi[
        (df_filtrado_campi["Curso"] == curso_base) &
        (df_filtrado_campi["Campus"] == campus_base)
    ]
    titulo_mapa = f"{curso_base} ({campus_base}) - {filtro_ano[0]}-{filtro_ano[1]}"

# ---------- Agrupar por cidade ----------
df_agrupado = df_filtrado.groupby("Naturalidade").size().reset_index(name="Quantidade")
df_mapa = pd.merge(df_agrupado, df_geo, on="Naturalidade", how="inner")

# ---------- Plotar mapa por cidade ----------
st.subheader(f"📍 Mapa por Cidade — {titulo_mapa}")

fig = px.scatter_mapbox(
    df_mapa,
    lat="lat",
    lon="lon",
    size="Quantidade",
    color="Quantidade",
    hover_name="Naturalidade",
    size_max=25,
    zoom=4.5,
    color_continuous_scale="Turbo",
    mapbox_style="open-street-map",
    title="Distribuição por cidade de naturalidade"
)
fig.update_layout(margin={"r":0, "t":40, "l":0, "b":0})
st.plotly_chart(fig, use_container_width=True)

# ---------- NOVO MAPA: por estado (UF) ----------
st.subheader(f"🗺️ Mapa por Estado (UF) — {titulo_mapa}")

# Mesclar coordenadas com estados
df_mapa_estado = pd.merge(df_filtrado[["Naturalidade", "UF"]], df_geo, on="Naturalidade", how="inner")

# Agrupar por UF (usando média da localização das cidades)
df_uf_grouped = df_mapa_estado.groupby("UF").agg({
    "lat": "mean",
    "lon": "mean",
    "Naturalidade": "count"
}).reset_index().rename(columns={"Naturalidade": "Quantidade"})

# Mapa por estado
fig_uf = px.scatter_mapbox(
    df_uf_grouped,
    lat="lat",
    lon="lon",
    size="Quantidade",
    color="Quantidade",
    hover_name="UF",
    size_max=40,
    zoom=3.5,
    color_continuous_scale="Viridis",
    mapbox_style="open-street-map",
    title="Distribuição dos alunos por estado (UF)"
)
fig_uf.update_layout(margin={"r":0, "t":40, "l":0, "b":0})
st.plotly_chart(fig_uf, use_container_width=True)