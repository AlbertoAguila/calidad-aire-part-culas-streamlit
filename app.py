import pandas as pd
import altair as alt
import streamlit as st

# -----------------------------
# Configuración de la app
# -----------------------------
st.set_page_config(
    page_title="Calidad del aire",
    layout="wide"
)

st.title("Calidad del aire - Dashboard")
st.write("Análisis de calidad del aire interior con especial atención a partículas en suspensión.")

# -----------------------------
# Carga de datos
# -----------------------------
CSV_PATH = "data/mediciones_completas_etiquetadas.csv"

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Parseo de tiempo
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)

    # Limpieza básica
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values("timestamp")

    return df

df = load_data(CSV_PATH)

st.success(f"Datos cargados correctamente ({len(df)} registros)")

# -----------------------------
# Vista rápida de los datos
# -----------------------------
with st.expander("Ver primeras filas del dataset"):
    st.dataframe(df.head(50), use_container_width=True)

# -----------------------------
# Selección de variables de partículas
# -----------------------------
pm_vars = [
    "PM1_ug_m3",
    "PM2_5_ug_m3",
    "PM4_ug_m3",
    "PM10_ug_m3"
]

pm_vars = [v for v in pm_vars if v in df.columns]

st.subheader("Selección de partículas")
selected_vars = st.multiselect(
    "Variables a visualizar",
    options=pm_vars,
    default=pm_vars
)

if not selected_vars:
    st.warning("Selecciona al menos una variable para mostrar el gráfico.")
    st.stop()

# -----------------------------
# Gráfico temporal
# -----------------------------
st.subheader("Evolución temporal de las partículas")

df_long = df[["timestamp"] + selected_vars].melt(
    id_vars="timestamp",
    var_name="Varia_
