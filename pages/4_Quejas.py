import streamlit as st

if "usuario" not in st.session_state:
    st.warning("Por favor, inicia sesión para acceder al dashboard.")
    st.stop()
import pandas as pd
from datetime import datetime
from data.load_data import load_quejas, load_sales_orders, load_retrasos

st.set_page_config(page_title="Dashboard de Quejas", layout="wide")

# --- CARGA DE DATOS ---
@st.cache_data(ttl=60)
def load_data():
    quejas = load_quejas()
    ordenes = load_sales_orders()[["sales_date", "marca", "plataforma"]]
    retrasos = load_retrasos()
    return quejas, ordenes, retrasos

quejas, ordenes, retrasos = load_data()

# --- SIDEBAR ---
st.sidebar.header("Filtros de Quejas")
marca = st.sidebar.selectbox("Selecciona una marca:", ["Todas"] + sorted(quejas["marca"].unique()))
plataforma = st.sidebar.selectbox("Selecciona una plataforma:", ["Todas"] + sorted(quejas["plataforma"].unique()))
turno = st.sidebar.selectbox("Selecciona el turno:", ["Todos"] + sorted(quejas["turno"].unique()))
fecha_ini = st.sidebar.date_input("Fecha inicio:", value=quejas["fecha"].min())
fecha_fin = st.sidebar.date_input("Fecha fin:", value=quejas["fecha"].max())

# --- FILTRADO ---
q = quejas[(quejas["fecha"] >= pd.to_datetime(fecha_ini)) & (quejas["fecha"] <= pd.to_datetime(fecha_fin))]
r = retrasos[(retrasos["fecha_inicio_semana"] <= pd.to_datetime(fecha_fin)) & (retrasos["fecha_fin_semana"] >= pd.to_datetime(fecha_ini))]
o = ordenes[(ordenes["sales_date"] >= pd.to_datetime(fecha_ini)) & (ordenes["sales_date"] <= pd.to_datetime(fecha_fin))]

if marca != "Todas":
    q = q[q["marca"] == marca]
    r = r[r["marca"] == marca]
    o = o[o["marca"] == marca]

if plataforma != "Todas":
    q = q[q["plataforma"] == plataforma]
    r = r[r["plataforma"] == plataforma]
    o = o[o["plataforma"] == plataforma]

if turno != "Todos":
    q = q[q["turno"] == turno]

# --- MÉTRICAS ---
total_ordenes = o.shape[0]
total_quejas = q.shape[0]
total_retrasos = r["total_retrasos"].sum() if not r.empty else 0

pct_quejas = (total_quejas / total_ordenes) * 100 if total_ordenes else 0
pct_retrasos = (total_retrasos / total_ordenes) * 100 if total_ordenes else 0
pct_a_tiempo = 100 - pct_retrasos if total_ordenes else 0

# --- VISUALIZACIÓN ---
st.title("🤬 Dashboard de Quejas")
st.divider()

st.markdown("## Métricas Generales")
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total de Órdenes", f"{total_ordenes:,}")
col2.metric("Total de Quejas", f"{total_quejas}")
col3.metric("% de Quejas", f"{pct_quejas:.2f}%")
col4.metric("Total Retrasos", f"{total_retrasos:,}")
col5.metric("% de Retrasos", f"{pct_retrasos:.2f}%")
col6.metric("% Órdenes a Tiempo", f"{pct_a_tiempo:.2f}%")

st.divider()
st.markdown("## Comentarios y Quejas por Categoría")
st.dataframe(q[["categoria", "comentario"]], use_container_width=True)

# Tabla de quejas y retrasos por marca
st.divider()
st.markdown("## 📊 Quejas y Retrasos por Marca")

# Agrupar
tabla_marca = q.groupby("marca").size().reset_index(name="total_quejas")
tabla_retrasos = r.groupby("marca")["total_retrasos"].sum().reset_index()
tabla_comb = pd.merge(tabla_marca, tabla_retrasos, on="marca", how="outer").fillna(0)
tabla_comb["total_quejas"] = tabla_comb["total_quejas"].astype(int)
tabla_comb["total_retrasos"] = tabla_comb["total_retrasos"].astype(int)

# Mostrar
st.dataframe(tabla_comb, use_container_width=True)

# Tabla de número de quejas por categoría
st.divider()
st.markdown("## 📑 Número de Quejas por Categoría")

tabla_categoria = q["categoria"].value_counts().reset_index()
tabla_categoria.columns = ["Categoría", "Número de Quejas"]

st.dataframe(tabla_categoria, use_container_width=True)
