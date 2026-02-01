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
    var_name="Variable",
    value_name="Concentracion_ug_m3"
).dropna()

chart = (
    alt.Chart(df_long)
    .mark_line()
    .encode(
        x=alt.X("timestamp:T", title="Tiempo"),
        y=alt.Y("Concentracion_ug_m3:Q", title="Concentración (µg/m³)"),
        color=alt.Color("Variable:N", title="Partícula"),
        tooltip=[
            alt.Tooltip("timestamp:T", title="Fecha y hora"),
            alt.Tooltip("Variable:N", title="Variable"),
            alt.Tooltip("Concentracion_ug_m3:Q", format=".2f", title="µg/m³")
        ]
    )
    .interactive()
)

st.altair_chart(chart, use_container_width=True)

# -----------------------------
# Perfil horario medio
# -----------------------------
st.subheader("Perfil horario medio")

df["hora"] = df["timestamp"].dt.hour
df_hourly = df.groupby("hora")[selected_vars].mean().reset_index()

df_hourly_long = df_hourly.melt(
    id_vars="hora",
    var_name="Variable",
    value_name="Media_ug_m3"
)

chart_hourly = (
    alt.Chart(df_hourly_long)
    .mark_line(point=True)
    .encode(
        x=alt.X("hora:O", title="Hora del día"),
        y=alt.Y("Media_ug_m3:Q", title="Concentración media (µg/m³)"),
        color=alt.Color("Variable:N", title="Partícula"),
        tooltip=[
            alt.Tooltip("hora:O", title="Hora"),
            alt.Tooltip("Variable:N", title="Variable"),
            alt.Tooltip("Media_ug_m3:Q", format=".2f", title="µg/m³")
        ]
    )
)

st.altair_chart(chart_hourly, use_container_width=True)

# -----------------------------
# Nota final
# -----------------------------
st.info(
    "Los valores mostrados corresponden a mediciones reales en un entorno doméstico. "
    "Los resultados deben interpretarse como análisis de tendencias y patrones temporales."
)
