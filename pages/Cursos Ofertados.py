import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide")

vagas={'Curso':['Administração','Agronomia','Ciência da Computação',
                'Ciências Biológicas','Educação Física','Engenharia de Alimentos',
                'Física','Matemática','Química','Tecnologia em Gestão Ambiental'],
                'Nº de vagas':[60,45,50,25,50,45,25,25,25,50]}
st.table(vagas)