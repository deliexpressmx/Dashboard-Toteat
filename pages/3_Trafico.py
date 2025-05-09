import streamlit as st

if "usuario" not in st.session_state:
    st.warning("Por favor, inicia sesión para acceder al dashboard.")
    st.stop()
import pandas as pd
from datetime import datetime
from data.load_data import load_traffic_metrics, load_sales_orders, load_traffic_log


# Configura la página
st.set_page_config(page_title="Trafico y Conversion", layout="wide")


# Carga de datos
@st.cache_data(ttl=60)
def load_data():
    df_traffic = load_traffic_metrics()
    df_orders = load_sales_orders()[["sales_date", "marca"]]  # solo columnas necesarias
    df_log = load_traffic_log()
    return df_traffic, df_orders, df_log

df_traffic, df_orders, df_bitacora = load_data()

# Sidebar
st.sidebar.header("Filtros")
marca_sel = st.sidebar.selectbox("Marca", options=["Todos"] + sorted(df_traffic["marca"].dropna().unique()), index=0)

st.sidebar.subheader("Rango Base")
fecha_base_ini = st.sidebar.date_input("Inicio Rango Base", df_traffic["fecha_inicio_semana"].min())
fecha_base_fin = st.sidebar.date_input("Fin Rango Base", df_traffic["fecha_fin_semana"].max())

st.sidebar.subheader("Rango Comparativo")
fecha_comp_ini = st.sidebar.date_input("Inicio Rango Comp.", df_traffic["fecha_inicio_semana"].min())
fecha_comp_fin = st.sidebar.date_input("Fin Rango Comp.", df_traffic["fecha_fin_semana"].max())

modo = st.sidebar.radio("Modo Rango Comp.", ["Suma", "Promedio Semanal"])

# Filtro por marca
if marca_sel != "Todos":
    df_traffic = df_traffic[df_traffic["marca"] == marca_sel]
    df_orders = df_orders[df_orders["marca"] == marca_sel]

# Funciones

def calcular_metricas(df, inicio, fin, df_orders):
    df_filtro = df[(df["fecha_inicio_semana"] >= pd.to_datetime(inicio)) & (df["fecha_fin_semana"] <= pd.to_datetime(fin))]
    trafico = df_filtro["trafico"].sum()
    menu = df_filtro["vieron_menu"].sum()
    agregaron = df_filtro["agregaron_articulos"].sum()

    ordenes = df_orders[(df_orders["sales_date"] >= pd.to_datetime(inicio)) & (df_orders["sales_date"] <= pd.to_datetime(fin))].shape[0]
    conversion = ordenes / menu * 100 if trafico else 0
    semanas = max((pd.to_datetime(fin) - pd.to_datetime(inicio)).days / 7, 1)

    return {
        "trafico": trafico / semanas if modo == "Promedio Semanal" else trafico,
        "menu": menu / semanas if modo == "Promedio Semanal" else menu,
        "agregaron": agregaron / semanas if modo == "Promedio Semanal" else agregaron,
        "ordenes": ordenes / semanas if modo == "Promedio Semanal" else ordenes,
        "conversion": conversion
    }

def delta(v1, v2):
    return (v1 - v2) / v2 * 100 if v2 else 0

# Métricas
base = calcular_metricas(df_traffic, fecha_base_ini, fecha_base_fin, df_orders)
comp = calcular_metricas(df_traffic, fecha_comp_ini, fecha_comp_fin, df_orders)

# Display
st.title("📊 Trafico y Conversion")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Base")
    st.metric("Tráfico (Base)", f"{base['trafico']:,.0f}", f"{delta(base['trafico'], comp['trafico']):+.2f}%")
    st.metric("Vieron menú (Base)", f"{base['menu']:,.0f}", f"{delta(base['menu'], comp['menu']):+.2f}%")
    st.metric("Agregaron artículos (Base)", f"{base['agregaron']:,.0f}", f"{delta(base['agregaron'], comp['agregaron']):+.2f}%")
    st.metric("Pedidos realizados (Base)", f"{base['ordenes']:,.0f}", f"{delta(base['ordenes'], comp['ordenes']):+.2f}%")
    st.metric("Conversión (Base)", f"{base['conversion']:.2f}%", f"{delta(base['conversion'], comp['conversion']):+.2f}%")

with col2:
    st.subheader("Comparativo")
    st.metric("Tráfico (Comp.)", f"{comp['trafico']:,.0f}")
    st.metric("Vieron menú (Comp.)", f"{comp['menu']:,.0f}")
    st.metric("Agregaron artículos (Comp.)", f"{comp['agregaron']:,.0f}")
    st.metric("Pedidos realizados (Comp.)", f"{comp['ordenes']:,.0f}")
    st.metric("Conversión (Comp.)", f"{comp['conversion']:.2f}%")

st.divider()
st.markdown("## 📒 Bitácora de Acciones")

df_bitacora = load_traffic_log()


if marca_sel != "Todos":
    df_bitacora = df_bitacora[df_bitacora["marcas"].str.contains(marca_sel, case=False, na=False)]

st.dataframe(df_bitacora, use_container_width=True)

st.divider()

import plotly.express as px

# Filtrar datos al rango base
df_base_traffic = df_traffic[
    (df_traffic["fecha_inicio_semana"] >= pd.to_datetime(fecha_base_ini)) &
    (df_traffic["fecha_fin_semana"] <= pd.to_datetime(fecha_base_fin))
].copy()

df_base_orders = df_orders[
    (df_orders["sales_date"] >= pd.to_datetime(fecha_base_ini)) &
    (df_orders["sales_date"] <= pd.to_datetime(fecha_base_fin))
].copy()

# --- 1. Embudo de conversión ---
embudo = {
    "Etapa": ["Tráfico", "Vieron menú", "Agregaron artículos", "Órdenes"],
    "Usuarios": [
        df_base_traffic["trafico"].sum(),
        df_base_traffic["vieron_menu"].sum(),
        df_base_traffic["agregaron_articulos"].sum(),
        df_base_orders.shape[0]
    ]
}
fig1 = px.funnel(pd.DataFrame(embudo), x="Usuarios", y="Etapa", title="Embudo de Conversión")
fig1.update_layout(height=400, template="plotly_white", title_font=dict(size=18))

# --- 2. Evolución semanal de tráfico y órdenes ---
df_base_traffic["semana"] = df_base_traffic["fecha_inicio_semana"]
df_base_orders["semana"] = df_base_orders["sales_date"] - pd.to_timedelta(df_base_orders["sales_date"].dt.weekday, unit="d")

trafico_sem = df_base_traffic.groupby("semana")["trafico"].sum().reset_index()
ordenes_sem = df_base_orders.groupby("semana").size().reset_index(name="ordenes")
df_evo = pd.merge(trafico_sem, ordenes_sem, on="semana", how="outer").sort_values("semana")

fig2 = px.line(df_evo, x="semana", y=["trafico", "ordenes"], markers=True,
               title="Tráfico vs Órdenes por Semana",
               labels={"value": "Cantidad", "variable": "Métrica"})
fig2.update_layout(height=400, template="plotly_white", title_font=dict(size=18))

# --- 3. Conversión semanal ---
df_conv = df_base_traffic.groupby("semana").agg({
    "vieron_menu": "sum"
}).reset_index()

ordenes_sem = df_base_orders.groupby("semana").size().reset_index(name="ordenes")
df_conv = pd.merge(df_conv, ordenes_sem, on="semana", how="left")
df_conv["conversion"] = df_conv["ordenes"] / df_conv["vieron_menu"] * 100

fig3 = px.line(df_conv, x="semana", y="conversion", markers=True,
               title="Tasa de Conversión Semanal", labels={"conversion": "Conversión (%)"})
fig3.update_layout(height=400, template="plotly_white", title_font=dict(size=18))

# --- 4. Tráfico vs Órdenes por Marca ---
df_traffic_marca = df_base_traffic.groupby("marca")[["trafico"]].sum()
df_orders_marca = df_base_orders.groupby("marca").size().reset_index(name="ordenes")
df_traf_ord = pd.merge(df_traffic_marca, df_orders_marca, on="marca", how="inner")

fig4 = px.bar(df_traf_ord, x="trafico", y="marca", orientation="h",
              title="Tráfico vs Órdenes por Marca", text="ordenes",
              labels={"trafico": "Tráfico", "marca": "Marca"})
fig4.update_layout(height=400, template="plotly_white", title_font=dict(size=18))

# --- 5. Heatmap de Órdenes por Día de la Semana ---
df_base_orders["dia_semana"] = df_base_orders["sales_date"].dt.day_name()
df_base_orders["semana"] = df_base_orders["sales_date"] - pd.to_timedelta(df_base_orders["sales_date"].dt.weekday, unit="d")
heatmap_data = df_base_orders.groupby(["semana", "dia_semana"]).size().reset_index(name="ordenes")

dias_ordenados = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heatmap_data["dia_semana"] = pd.Categorical(heatmap_data["dia_semana"], categories=dias_ordenados, ordered=True)
heatmap_data = heatmap_data.pivot(index="dia_semana", columns="semana", values="ordenes").fillna(0)

fig5 = px.imshow(heatmap_data, text_auto=True, aspect="auto", color_continuous_scale="Blues",
                 labels=dict(color="Órdenes"), title="Heatmap de Pedidos por Día y Semana")
fig5.update_layout(height=400, template="plotly_white", title_font=dict(size=18))

# --- Mostrar en Layout 2x3 ---
cols = st.columns(2)
for i, fig in enumerate([fig1, fig2, fig3, fig4, fig5]):
    cols[i % 2].plotly_chart(fig, use_container_width=True)
