import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide")

# Título principal
st.title("📊 Painel de Matrículas da UFV - Campus Florestal, Viçosa e Rio Paranaíba")

# Descrição introdutória
st.markdown("""
Este painel apresenta uma visão geral das **matrículas anuais** nos cursos de graduação da Universidade Federal de Viçosa (UFV), considerando os três campi: **Florestal**, **Viçosa** e **Rio Paranaíba**.

Utilizando dados dos alunos ingressantes, a visualização permite identificar padrões de admissão ao longo dos anos, comparar o volume de matrículas por campus e observar a evolução dos cursos oferecidos.

""")


caminho = os.path.join("datasets", "alunos-ingressantes.csv")
df = pd.read_csv(caminho, sep=";", encoding="latin-1")

df["Curso"]=df["Curso"].replace(["Física - Licenciatura", "Matemática - Licenciatura","Química - Licenciatura","Educação Física - Licenciatura","Ciências Biológicas - Licenciatura"],["Física", "Matemática","Química","Educação Física","Ciências Biológicas"])


df2=df[df["NivelAgrupado"] == "Graduação"]
df3=df2[df2["Campus"] == "Florestal"]
df4=df2[df2["Campus"] == "Viçosa"]
df5=df2[df2["Campus"] == "Rio Paranaíba"]
df_group1 = df3.groupby("AnoAdmissao").count().reset_index()

dg1=df_group1[['AnoAdmissao','Campus']].rename(columns={
    "AnoAdmissao": "AnoAdmissao",
    "Campus": "Florestal"})
df_group2 = df4.groupby("AnoAdmissao").count().reset_index()


dg2=df_group2[['AnoAdmissao','Campus']].rename(columns={
    "AnoAdmissao": "AnoAdmissao",
    "Campus": "Viçosa"})
data_df = df3.groupby(['AnoAdmissao', 'Curso']).agg(avg_age=('AnoAdmissao', 'mean'), count=('AnoAdmissao', 'count'))
data_df = data_df.reset_index()

df_group3 = df5.groupby("AnoAdmissao").count().reset_index()
dg3=df_group3[['AnoAdmissao','Campus']].rename(columns={
    "AnoAdmissao": "AnoAdmissao",
    "Campus": "Rio Paranaíba"})
m = pd.merge(dg1, dg2, on = "AnoAdmissao")
m1 = pd.merge(m, dg3, on = "AnoAdmissao")



# Using "with" notation

st.title("Visão Geral")


col1, col2 = st.columns(2)
col3 = st.container

fig = px.bar(data_df, x="AnoAdmissao", y="count", color="Curso", barmode="group",title="Matrículas anuais por curso")
a1=px.line(m1, x="AnoAdmissao", y=["Florestal","Rio Paranaíba","Viçosa"],width=850, height=400, title="Matrículas anuais - Gráfico de Linhas")
a2=px.bar(m1,x="AnoAdmissao", y=["Florestal","Rio Paranaíba","Viçosa"],barmode="group",width=750, height=400, title="Matrículas anuais - Gráfico de Barras")

col1.plotly_chart(a2, use_container_width=True)
col2.plotly_chart(a1, use_container_width=True)
st.plotly_chart(fig, use_container_width=True)
