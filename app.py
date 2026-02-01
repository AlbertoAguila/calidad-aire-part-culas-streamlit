import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# =====================================================
# Configuración general
# =====================================================
st.set_page_config(
    page_title="Calidad del aire interior", 
    layout="wide",
    page_icon="🌬️"
)

# =====================================================
# Portada profesional
# =====================================================
st.markdown("""
<div style='text-align: center; padding: 2.5rem 1rem; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
    <h1 style='color: white; margin: 0; font-size: 2.8rem; font-weight: 700;'>
        🌬️ Análisis Integral de la Calidad del Aire Interior
    </h1>
    <p style='color: #e0e7ff; font-size: 1.3rem; margin-top: 1rem; font-weight: 300;'>
        Monitorización de Parámetros Ambientales y Material Particulado
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# Información del proyecto
# =====================================================
st.markdown("### 📚 Trabajo Académico — Diseño Electrónico e Instrumentación")

st.markdown("#### 👥 Integrantes del grupo:")
st.markdown("""
- Alberto Águila Prieto  
- Liberto Farfante López  
- Pedro Genebat Gutiérrez  
- Juan Mantero Clavero  
- Fernando Pedrosa Rodríguez  
""")

st.markdown("#### 🎯 Descripción del proyecto:")
st.markdown("""
Este proyecto presenta un análisis histórico integral de la calidad del aire interior en un entorno 
doméstico real, monitorizando tanto **parámetros ambientales básicos** (temperatura, humedad relativa, 
concentración de CO₂) como **partículas en suspensión** (PM 1.0, PM 2.5, PM 4.0, PM 10).

El sistema de adquisición de datos, diseñado e implementado por el grupo, integra múltiples sensores 
comerciales configurados con una **frecuencia de muestreo constante de 30 minutos**. Los datos se 
analizan de forma descriptiva para identificar patrones asociados a la ocupación del espacio, 
ventilación natural y calidad del aire respirado.
""")

st.markdown("<br>", unsafe_allow_html=True)

# Info sobre partículas
with st.expander("📖 Información sobre partículas PM y valores de referencia"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **¿Qué son las partículas PM?**
        
        Las partículas PM (Particulate Matter) se clasifican por tamaño:
        - **PM 1.0**: ≤ 1.0 µm (ultrafinas, penetran profundamente)
        - **PM 2.5**: ≤ 2.5 µm (finas, respirables)
        - **PM 4.0**: ≤ 4.0 µm 
        - **PM 10**: ≤ 10 µm (inhalables)
        """)
    
    with col2:
        st.markdown("""
        **Límites OMS (Organización Mundial de la Salud):**
        
        | Partícula | Media 24h | Media anual |
        |-----------|-----------|-------------|
        | PM 2.5 | 15 µg/m³ | 5 µg/m³ |
        | PM 10 | 45 µg/m³ | 15 µg/m³ |
        
        **CO₂:** < 800 ppm (óptimo), 800-1200 ppm (moderado), > 1200 ppm (elevado)
        """)

st.info("""
ℹ️ **Nota importante:** Este dashboard presenta análisis histórico de datos. 
No constituye un sistema de monitorización en tiempo real.
""")

st.divider()

# =====================================================
# Carga de datos
# =====================================================
CSV_PATH = "data/mediciones_completas_etiquetadas.csv"

@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")
    
    # Convertir todas las columnas numéricas (nombres correctos según tu CSV)
    numeric_cols = ["temperatura_C", "humedad_relativa_pct", "CO2_ppm", 
                    "PM1_ug_m3", "PM2_5_ug_m3", "PM4_ug_m3", "PM10_ug_m3"]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    return df

with st.spinner("🔄 Cargando datos del sistema de monitorización..."):
    df = load_data(CSV_PATH)

st.success(f"✅ Datos cargados correctamente: **{len(df):,}** registros")

# =====================================================
# Sidebar: filtros
# =====================================================
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 10px; margin-bottom: 1rem;'>
    <h2 style='color: white; margin: 0;'>🎛️ Panel de Control</h2>
</div>
""", unsafe_allow_html=True)

min_dt, max_dt = df["timestamp"].min(), df["timestamp"].max()
start_date, end_date = st.sidebar.date_input(
    "📅 Rango de fechas",
    value=(min_dt.date(), max_dt.date())
)

start_ts = pd.to_datetime(start_date, utc=True)
end_ts = pd.to_datetime(end_date, utc=True) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

df_f = df[(df["timestamp"] >= start_ts) & (df["timestamp"] <= end_ts)].copy()

resample = st.sidebar.selectbox(
    "⏱️ Intervalo de resample (promedio)",
    ["Sin resample", "30min", "1H", "2H", "6H", "1D"],
    index=1,
    help="Agrupa los datos calculando el promedio en el intervalo seleccionado"
)

if resample != "Sin resample":
    numeric_cols = [c for c in df_f.columns if c not in ["timestamp", "Evento"]]
    df_f = (
        df_f.set_index("timestamp")[numeric_cols]
        .resample(resample)
        .mean()
        .reset_index()
    )

st.sidebar.divider()
st.sidebar.markdown(f"""
<div style='background-color: #f1f5f9; padding: 1rem; border-radius: 8px;'>
    <p style='margin: 0; color: #475569;'><strong>📊 Total:</strong> {len(df):,} registros</p>
    <p style='margin: 0.5rem 0 0 0; color: #475569;'><strong>📊 Filtrados:</strong> {len(df_f):,} registros</p>
    <p style='margin: 0.5rem 0 0 0; color: #475569;'><strong>📅 Período:</strong><br>
    {min_dt.strftime('%d/%m/%Y')} - {max_dt.strftime('%d/%m/%Y')}</p>
</div>
""", unsafe_allow_html=True)

if df_f.empty:
    st.error("❌ No hay datos en el rango seleccionado.")
    st.stop()

# =====================================================
# KPIs - Parámetros medidos
# =====================================================
st.markdown("## 📊 Parámetros Básicos Medidos")

col1, col2, col3 = st.columns(3)

# Verificar qué columnas existen
has_temp = "temperatura_C" in df_f.columns
has_hum = "humedad_relativa_pct" in df_f.columns
has_co2 = "CO2_ppm" in df_f.columns

if has_temp:
    temp_mean = df_f["temperatura_C"].mean()
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
                    padding: 1.5rem; border-radius: 12px; text-align: center;
                    border: 2px solid #fbbf24; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
            <p style='color: #92400e; margin: 0; font-size: 0.9rem; font-weight: 600;'>🌡️ TEMPERATURA MEDIA</p>
            <p style='color: #78350f; margin: 0.8rem 0 0 0; font-size: 2.5rem; font-weight: 700;'>
                {temp_mean:.1f}°C
            </p>
        </div>
        """, unsafe_allow_html=True)

if has_hum:
    hum_mean = df_f["humedad_relativa_pct"].mean()
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); 
                    padding: 1.5rem; border-radius: 12px; text-align: center;
                    border: 2px solid #3b82f6; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
            <p style='color: #1e40af; margin: 0; font-size: 0.9rem; font-weight: 600;'>💧 HUMEDAD MEDIA</p>
            <p style='color: #1e3a8a; margin: 0.8rem 0 0 0; font-size: 2.5rem; font-weight: 700;'>
                {hum_mean:.1f}%
            </p>
        </div>
        """, unsafe_allow_html=True)

if has_co2:
    co2_mean = df_f["CO2_ppm"].mean()
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%); 
                    padding: 1.5rem; border-radius: 12px; text-align: center;
                    border: 2px solid #a855f7; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
            <p style='color: #6b21a8; margin: 0; font-size: 0.9rem; font-weight: 600;'>🫁 CO₂ MEDIO</p>
            <p style='color: #581c87; margin: 0.8rem 0 0 0; font-size: 2.5rem; font-weight: 700;'>
                {co2_mean:.0f} ppm
            </p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# KPIs de partículas
st.markdown("## 🌫️ Concentración Media de Partículas (PM)")

col1, col2, col3, col4 = st.columns(4)

pm_cols = {
    "PM1_ug_m3": ("PM 1.0", col1, "#ef4444"),
    "PM2_5_ug_m3": ("PM 2.5", col2, "#f97316"),
    "PM4_ug_m3": ("PM 4.0", col3, "#f59e0b"),
    "PM10_ug_m3": ("PM 10", col4, "#eab308")
}

for pm_col, (label, col, color) in pm_cols.items():
    if pm_col in df_f.columns:
        pm_mean = df_f[pm_col].mean()
        with col:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {color}22 0%, {color}44 100%); 
                        padding: 1.5rem; border-radius: 12px; text-align: center;
                        border: 2px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                <p style='color: #78350f; margin: 0; font-size: 0.9rem; font-weight: 600;'>🔬 {label}</p>
                <p style='color: #78350f; margin: 0.8rem 0 0 0; font-size: 2.2rem; font-weight: 700;'>
                    {pm_mean:.1f}
                </p>
                <p style='color: #92400e; margin: 0.3rem 0 0 0; font-size: 0.8rem;'>µg/m³</p>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# =====================================================
# Tabs de visualización
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Parámetros Básicos", 
    "🌫️ Partículas PM",
    "⏰ Perfil Horario",
    "📊 Estadísticas",
    "🧾 Datos Crudos"
])

with tab1:
    st.markdown("### Evolución Temporal de Parámetros Básicos")
    
    # Gráfico CO₂
    if has_co2:
        st.markdown("#### Concentración de CO₂")
        fig_co2 = go.Figure()
        
        fig_co2.add_hrect(y0=0, y1=800, fillcolor="green", opacity=0.08, line_width=0)
        fig_co2.add_hrect(y0=800, y1=1200, fillcolor="yellow", opacity=0.08, line_width=0)
        fig_co2.add_hrect(y0=1200, y1=df_f["CO2_ppm"].max()*1.1, fillcolor="red", opacity=0.08, line_width=0)
        
        fig_co2.add_trace(go.Scatter(
            x=df_f["timestamp"], 
            y=df_f["CO2_ppm"],
            mode='lines',
            name='CO₂',
            line=dict(color='#667eea', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.15)'
        ))
        
        fig_co2.add_hline(y=800, line_dash="dash", line_color="green", line_width=2)
        fig_co2.add_hline(y=1200, line_dash="dash", line_color="red", line_width=2)
        
        fig_co2.update_layout(
            title="Concentración de CO₂",
            xaxis_title="Fecha y hora",
            yaxis_title="CO₂ (ppm)",
            template='plotly_white',
            height=500
        )
        fig_co2.update_xaxes(rangeslider=dict(visible=True))
        st.plotly_chart(fig_co2, use_container_width=True)
    
    # Temperatura y Humedad
    colA, colB = st.columns(2)
    
    if has_temp:
        with colA:
            st.markdown("#### Temperatura")
            fig_t = go.Figure()
            fig_t.add_trace(go.Scatter(
                x=df_f["timestamp"], 
                y=df_f["temperatura_C"],
                mode='lines',
                line=dict(color='#f59e0b', width=2.5),
                fill='tozeroy',
                fillcolor='rgba(245, 158, 11, 0.15)'
            ))
            fig_t.update_layout(
                xaxis_title="Fecha y hora",
                yaxis_title="Temperatura (°C)",
                template='plotly_white',
                height=400
            )
            fig_t.update_xaxes(rangeslider=dict(visible=True))
            st.plotly_chart(fig_t, use_container_width=True)
    
    if has_hum:
        with colB:
            st.markdown("#### Humedad Relativa")
            fig_h = go.Figure()
            fig_h.add_trace(go.Scatter(
                x=df_f["timestamp"], 
                y=df_f["humedad_relativa_pct"],
                mode='lines',
                line=dict(color='#3b82f6', width=2.5),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.15)'
            ))
            fig_h.update_layout(
                xaxis_title="Fecha y hora",
                yaxis_title="Humedad (%)",
                template='plotly_white',
                height=400
            )
            fig_h.update_xaxes(rangeslider=dict(visible=True))
            st.plotly_chart(fig_h, use_container_width=True)

with tab2:
    st.markdown("### Evolución de Partículas en Suspensión")
    
    # Selección de partículas a visualizar
    pm_available = [col for col in ["PM1_ug_m3", "PM2_5_ug_m3", "PM4_ug_m3", "PM10_ug_m3"] if col in df_f.columns]
    
    if pm_available:
        pm_labels = {
            "PM1_ug_m3": "PM 1.0",
            "PM2_5_ug_m3": "PM 2.5",
            "PM4_ug_m3": "PM 4.0",
            "PM10_ug_m3": "PM 10"
        }
        
        selected_pm = st.multiselect(
            "Selecciona las partículas a visualizar:",
            options=pm_available,
            default=pm_available,
            format_func=lambda x: pm_labels.get(x, x)
        )
        
        if selected_pm:
            fig_pm = go.Figure()
            
            colors = {
                "PM1_ug_m3": "#ef4444",
                "PM2_5_ug_m3": "#f97316",
                "PM4_ug_m3": "#f59e0b",
                "PM10_ug_m3": "#eab308"
            }
            
            for pm_col in selected_pm:
                fig_pm.add_trace(go.Scatter(
                    x=df_f["timestamp"],
                    y=df_f[pm_col],
                    mode='lines',
                    name=pm_labels[pm_col],
                    line=dict(color=colors[pm_col], width=2.5)
                ))
            
            # Líneas de referencia OMS
            if "PM2_5_ug_m3" in selected_pm:
                fig_pm.add_hline(y=15, line_dash="dash", line_color="orange", 
                                annotation_text="OMS PM2.5 (24h): 15 µg/m³")
            if "PM10_ug_m3" in selected_pm:
                fig_pm.add_hline(y=45, line_dash="dash", line_color="red",
                                annotation_text="OMS PM10 (24h): 45 µg/m³")
            
            fig_pm.update_layout(
                title="Concentración de Partículas en Suspensión",
                xaxis_title="Fecha y hora",
                yaxis_title="Concentración (µg/m³)",
                template='plotly_white',
                height=550,
                hovermode='x unified'
            )
            fig_pm.update_xaxes(rangeslider=dict(visible=True))
            st.plotly_chart(fig_pm, use_container_width=True)
        else:
            st.warning("Selecciona al menos una partícula para visualizar")

with tab3:
    st.markdown("### Perfil Horario Medio")
    
    df_f["hora"] = df_f["timestamp"].dt.hour
    
    # Perfil horario de CO₂
    if has_co2:
        st.markdown("#### CO₂ por hora del día")
        df_hourly_co2 = df_f.groupby("hora")["CO2_ppm"].mean().reset_index()
        
        fig_h_co2 = go.Figure()
        fig_h_co2.add_trace(go.Scatter(
            x=df_hourly_co2["hora"],
            y=df_hourly_co2["CO2_ppm"],
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        fig_h_co2.update_layout(
            xaxis_title="Hora del día",
            yaxis_title="CO₂ medio (ppm)",
            template='plotly_white',
            height=400
        )
        st.plotly_chart(fig_h_co2, use_container_width=True)
    
    # Perfil horario de partículas
    if pm_available:
        st.markdown("#### Partículas PM por hora del día")
        df_hourly_pm = df_f.groupby("hora")[pm_available].mean().reset_index()
        
        fig_h_pm = go.Figure()
        for pm_col in pm_available:
            fig_h_pm.add_trace(go.Scatter(
                x=df_hourly_pm["hora"],
                y=df_hourly_pm[pm_col],
                mode='lines+markers',
                name=pm_labels.get(pm_col, pm_col),
                line=dict(width=3),
                marker=dict(size=8)
            ))
        
        fig_h_pm.update_layout(
            xaxis_title="Hora del día",
            yaxis_title="Concentración media (µg/m³)",
            template='plotly_white',
            height=400
        )
        st.plotly_chart(fig_h_pm, use_container_width=True)

with tab4:
    st.markdown("### Estadísticas Descriptivas")
    
    # Seleccionar columnas numéricas disponibles
    numeric_cols_available = []
    if has_temp:
        numeric_cols_available.append("temperatura_C")
    if has_hum:
        numeric_cols_available.append("humedad_relativa_pct")
    if has_co2:
        numeric_cols_available.append("CO2_ppm")
    numeric_cols_available.extend(pm_available)
    
    if numeric_cols_available:
        stats = df_f[numeric_cols_available].describe().T
        stats = stats.round(2)
        stats.columns = ["Recuento", "Media", "Desv. Est.", "Mínimo", "Q1 (25%)", "Mediana", "Q3 (75%)", "Máximo"]
        
        st.dataframe(stats, use_container_width=True)
        
        st.markdown("### Diagramas de Caja (Box Plots)")
        
        n_cols = len(numeric_cols_available)
        cols = st.columns(min(n_cols, 4))
        
        for idx, col_name in enumerate(numeric_cols_available[:4]):
            with cols[idx % 4]:
                fig_box = px.box(df_f, y=col_name)
                fig_box.update_layout(
                    title=col_name,
                    height=350,
                    template='plotly_white',
                    showlegend=False
                )
                st.plotly_chart(fig_box, use_container_width=True)

with tab5:
    st.markdown("### Tabla de Datos Registrados")
    
    show_all = st.checkbox("Mostrar todas las columnas del archivo CSV", value=False)
    
    if show_all:
        display_df = df_f.copy()
    else:
        display_cols = ["timestamp"] + numeric_cols_available
        display_df = df_f[[c for c in display_cols if c in df_f.columns]].copy()
    
    if "timestamp" in display_df.columns:
        display_df["timestamp"] = display_df["timestamp"].dt.strftime("%d/%m/%Y %H:%M:%S")
    
    st.dataframe(display_df, use_container_width=True, height=450)
    
    st.markdown("### ⬇️ Descarga de Datos")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        st.download_button(
            label="📥 Descargar datos filtrados (CSV)",
            data=df_f.to_csv(index=False).encode("utf-8"),
            file_name=f"datos_calidad_aire_{start_date}_{end_date}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_btn2:
        st.metric("Total de registros", f"{len(df_f):,}")
    
    with col3:
        st.metric("Período de datos", f"{(end_ts - start_ts).days + 1} días")

# =====================================================
# Footer
# =====================================================
st.divider()
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 1rem;'>
    <p style='margin: 0; font-size: 0.9rem;'>
        Dashboard desarrollado para el análisis integral de calidad del aire interior<br>
        <strong>Diseño Electrónico e Instrumentación</strong> — Curso 2024-2025
    </p>
</div>
""", unsafe_allow_html=True)
