import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(page_title="Calidad del aire", layout="wide")
st.title("Calidad del aire - Dashboard")

CSV_PATH = "mediciones_completas_etiquetadas.csv"

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")
    return df

df = load_data(CSV_PATH)

st.write(f"Filas: {len(df):,}")
st.dataframe(df.head(50), use_container_width=True)

vars_pm = ["PM1_ug_m3", "PM2_5_ug_m3", "PM4_ug_m3", "PM10_ug_m3"]
vars_exist = [c for c in vars_pm if c in df.columns]

st.subheader("Partículas - evolución temporal")
sel = st.multiselect("Series", vars_exist, default=vars_exist)

if sel:
    long_df = df[["timestamp"] + sel].melt("timestamp", var_name="variable", value_name="ug_m3").dropna()
    chart = (
        alt.Chart(long_df)
        .mark_line()
        .encode(
            x=alt.X("timestamp:T", title="Tiempo"),
            y=alt.Y("ug_m3:Q", title="µg/m³"),
            color="variable:N",
            tooltip=["timestamp:T", "variable:N", "ug_m3:Q"],
        )
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("Selecciona al menos una serie.")

