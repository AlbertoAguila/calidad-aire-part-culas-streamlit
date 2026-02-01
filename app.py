import pandas as pd
import streamlit as st

st.set_page_config(page_title="Calidad del aire", layout="wide")
st.title("Calidad del aire - Dashboard")

df = pd.read_csv("mediciones_completas_etiquetadas.csv")
st.write("Filas:", len(df))
st.dataframe(df.head(50), use_container_width=True)

