import pandas as pd
import streamlit as st

st.title("Calidad del aire - Partículas")

df = pd.read_csv("data/mediciones_completas_etiquetadas.csv")

st.write(df.head())
