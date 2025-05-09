import streamlit as st

if "usuario" not in st.session_state:
    st.warning("Por favor, inicia sesión para acceder al dashboard.")
    st.stop()
import pandas as pd
from data.load_data import load_sales_orders, load_ad_spend, load_user_retention
from datetime import datetime, timedelta
from data.load_data import load_metricas_generales
df_metricas = load_metricas_generales()

st.set_page_config(page_title="Dashboard Ventas", layout="wide")

@st.cache_data(ttl=60)
def load_data():
    df_sales = load_sales_orders()
    df_pauta = load_ad_spend()
    df_retencion = load_user_retention()
    return df_sales, df_pauta, df_retencion

df, df_pauta, df_retencion = load_data()


# --- SIDEBAR ---
st.sidebar.header("Filtros generales")
marca_sel = st.sidebar.selectbox("Marca", options=["Todas"] + sorted(df["marca"].dropna().unique()), index=0)
plataforma_sel = st.sidebar.selectbox("Plataforma", options=["Todas"] + sorted(df["plataforma"].dropna().unique()), index=0)
rango1 = st.sidebar.date_input("Fechas Rango 1", [df["sales_date"].min(), df["sales_date"].max()])
rango2 = st.sidebar.date_input("Fechas Rango 2", [df["sales_date"].min(), df["sales_date"].max()])
accion = st.sidebar.radio("Selecciona acción", ["Sumar", "Promedio semanal"])

# --- FILTROS ---
df_filtrado = df.copy()
if marca_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["marca"] == marca_sel]
if plataforma_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["plataforma"] == plataforma_sel]

df_r1 = df_filtrado[(df_filtrado["sales_date"] >= pd.to_datetime(rango1[0])) & (df_filtrado["sales_date"] <= pd.to_datetime(rango1[1]))]
df_r2 = df_filtrado[(df_filtrado["sales_date"] >= pd.to_datetime(rango2[0])) & (df_filtrado["sales_date"] <= pd.to_datetime(rango2[1]))]

# --- MÉTRICAS RANGO 1 ---
ventas_r1 = df_r1["neto"].sum()
ordenes_r1 = df_r1.shape[0]
dias_r1 = (rango1[1] - rango1[0]).days + 1
ticket_promedio_r1 = ventas_r1 / ordenes_r1 if ordenes_r1 else 0
ordenes_dia_r1 = ordenes_r1 / dias_r1 if dias_r1 else 0

# --- MÉTRICAS RANGO 2 ---
ventas_r2_total = df_r2["neto"].sum()
ordenes_r2_total = df_r2.shape[0]
dias_r2 = (rango2[1] - rango2[0]).days + 1
semanas_r2 = dias_r2 / 7 if dias_r2 else 1

ventas_r2 = ventas_r2_total / semanas_r2 if accion == "Promedio semanal" else ventas_r2_total
ordenes_r2 = ordenes_r2_total / semanas_r2 if accion == "Promedio semanal" else ordenes_r2_total
ticket_promedio_r2 = ventas_r2 / ordenes_r2 if ordenes_r2 else 0
ordenes_dia_r2 = ordenes_r2_total / dias_r2 if dias_r2 else 0

def delta(x1, x2):
    return (x1 - x2) / x2 * 100 if x2 else 0

deltas = {
    "ventas": delta(ventas_r1, ventas_r2),
    "ordenes": delta(ordenes_r1, ordenes_r2),
    "ticket": delta(ticket_promedio_r1, ticket_promedio_r2),
    "ordenes_dia": delta(ordenes_dia_r1, ordenes_dia_r2),
}

# --- VISUALIZACIÓN: RANGO 1 ---
st.title("📊 Ventas")
st.divider()
st.markdown("### Rango 1")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ingresos netos", f"${ventas_r1:,.2f}", f"{deltas['ventas']:+.2f}%")
col2.metric("Órdenes", f"{ordenes_r1:,}", f"{deltas['ordenes']:+.2f}%")
col3.metric("Ticket promedio", f"${ticket_promedio_r1:,.2f}", f"{deltas['ticket']:+.2f}%")
col4.metric("Órdenes promedio por día", f"{ordenes_dia_r1:.2f}", f"{deltas['ordenes_dia']:+.2f}%")

# --- VISUALIZACIÓN: RANGO 2 ---

st.markdown("### Rango 2")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ingresos netos", f"${ventas_r2:,.2f}")
col2.metric("Órdenes", f"{ordenes_r2:,.2f}" if accion == "Promedio semanal" else f"{ordenes_r2:,}")
col3.metric("Ticket promedio", f"${ticket_promedio_r2:,.2f}")
col4.metric("Órdenes promedio por día", f"{ordenes_dia_r2:.2f}")

# --- FUNCIÓN PAUTA ---
def calcular_pauta(df_base, inicio, fin):
    df_p = df_base.copy()
    df_p["dias_utiles"] = df_p.apply(
        lambda row: len(pd.date_range(start=max(pd.to_datetime(row["fecha_inicio_semana"]), pd.to_datetime(inicio)),
                                      end=min(pd.to_datetime(row["fecha_fin_semana"]), pd.to_datetime(fin)))),
        axis=1
    )
    df_p = df_p[df_p["dias_utiles"] > 0]
    df_p["gasto_ajustado"] = df_p["gasto"] * (df_p["dias_utiles"] / 7)
    return df_p["gasto_ajustado"].sum()

# ────────────── SECCIÓN PAUTA ──────────────
st.divider()
st.markdown("## 📣 Pauta")
st.divider()
# Filtro pauta (excluye Didi)
df_pauta_filtrado = df_pauta[df_pauta["plataforma"] != "Didi"].copy()
if marca_sel != "Todas":
    df_pauta_filtrado = df_pauta_filtrado[df_pauta_filtrado["marca"] == marca_sel]
if plataforma_sel != "Todas" and plataforma_sel != "Didi":
    df_pauta_filtrado = df_pauta_filtrado[df_pauta_filtrado["plataforma"] == plataforma_sel]

# Función de prorrateo por rango
def calcular_pauta(inicio, fin):
    df_p = df_pauta_filtrado[
        (df_pauta_filtrado["fecha_inicio_semana"] <= pd.to_datetime(fin)) &
        (df_pauta_filtrado["fecha_fin_semana"] >= pd.to_datetime(inicio))
    ].copy()

    if df_p.empty:
        return 0

    df_p["dias_utiles"] = df_p.apply(
        lambda row: len(pd.date_range(
            start=max(pd.to_datetime(row["fecha_inicio_semana"]), pd.to_datetime(inicio)),
            end=min(pd.to_datetime(row["fecha_fin_semana"]), pd.to_datetime(fin))
        )),
        axis=1
    )
    df_p["gasto_ajustado"] = df_p["gasto"] * (df_p["dias_utiles"] / 7)
    return df_p["gasto_ajustado"].sum()


# Calcular pauta y ROAS por rango
pauta_r1 = calcular_pauta(rango1[0], rango1[1])
pauta_r2_total = calcular_pauta(rango2[0], rango2[1])

# Calcular pauta por rango
pauta_r1 = calcular_pauta(rango1[0], rango1[1])
pauta_r2_total = calcular_pauta(rango2[0], rango2[1])

# Ajustar ventas y pauta según acción
if accion == "Promedio semanal":
    semanas_r2 = ((rango2[1] - rango2[0]).days + 1) / 7
    ventas_r2_ajustada = ventas_r2_total / semanas_r2 if semanas_r2 else 0
    pauta_r2 = pauta_r2_total / semanas_r2 if semanas_r2 else 0
else:
    ventas_r2_ajustada = ventas_r2_total
    pauta_r2 = pauta_r2_total

# ROAS: ventas / pauta
roas_r1 = ventas_r1 / pauta_r1 if pauta_r1 else float("nan")
roas_r2 = ventas_r2_ajustada / pauta_r2 if pauta_r2 else float("nan")

# Deltas
delta_pauta = (pauta_r1 - pauta_r2) / pauta_r2 * 100 if pauta_r2 else 0
delta_roas = (roas_r1 - roas_r2) / roas_r2 * 100 if roas_r2 else 0

# Mostrar
st.markdown("### Rango 1")
col1, col2 = st.columns(2)
col1.metric("Gasto en pauta", f"${pauta_r1:,.2f}", f"{delta_pauta:+.2f}%")
col2.metric("ROAS", f"{roas_r1:.2f}", f"{delta_roas:+.2f}%")

st.markdown("### Rango 2")
col3, col4 = st.columns(2)
col3.metric("Gasto en pauta", f"${pauta_r2:,.2f}")
col4.metric("ROAS", f"{roas_r2:.2f}")
st.divider()

import plotly.express as px
import plotly.graph_objects as go

st.markdown("## 📊 Análisis Visual Semanal")
st.divider()

# --- Filtrar solo por rango 1, respetando marca y plataforma ---
df_viz = df_r1.copy()
df_ret_viz = df_retencion[
    (df_retencion["fecha_inicio_semana"] >= pd.to_datetime(rango1[0])) &
    (df_retencion["fecha_inicio_semana"] <= pd.to_datetime(rango1[1]))
].copy()
if marca_sel != "Todas":
    df_ret_viz = df_ret_viz[df_ret_viz["marca"] == marca_sel]
if plataforma_sel != "Todas":
    df_ret_viz = df_ret_viz[df_ret_viz["plataforma"] == plataforma_sel]

df_pauta_viz = df_pauta[
    (df_pauta["fecha_inicio_semana"] <= pd.to_datetime(rango1[1])) &
    (df_pauta["fecha_fin_semana"] >= pd.to_datetime(rango1[0])) &
    (df_pauta["plataforma"] != "Didi")
].copy()
if marca_sel != "Todas":
    df_pauta_viz = df_pauta_viz[df_pauta_viz["marca"] == marca_sel]
if plataforma_sel != "Todas" and plataforma_sel != "Didi":
    df_pauta_viz = df_pauta_viz[df_pauta_viz["plataforma"] == plataforma_sel]

# --- Agrupar por semana ---
df_viz["semana"] = df_viz["sales_date"] - pd.to_timedelta(df_viz["sales_date"].dt.weekday, unit="d")
df_grouped = df_viz.groupby("semana").agg({
    "neto": "sum", "order_id": "count"
}).rename(columns={"order_id": "ordenes"}).reset_index()
df_grouped["ticket_promedio"] = df_grouped["neto"] / df_grouped["ordenes"]

df_pauta_viz["semana"] = df_pauta_viz["fecha_inicio_semana"]
df_pauta_grouped = df_pauta_viz.groupby("semana").agg({"gasto": "sum"}).reset_index()

# ROAS semanal
df_roas = pd.merge(df_grouped, df_pauta_grouped, on="semana", how="left")
df_roas["roas"] = df_roas["neto"] / df_roas["gasto"]

# Retención
df_ret_viz["semana"] = df_ret_viz["fecha_inicio_semana"]
df_ret = df_ret_viz.groupby("semana").agg({
    "nuevos": "sum", "frecuentes": "sum"
}).reset_index()
df_ret["retencion"] = df_ret["frecuentes"] / (df_ret["nuevos"] + df_ret["frecuentes"]) * 100

# --- Gráficas ---
fig1 = px.line(df_roas, x="semana", y=["neto", "gasto"], markers=True,
               labels={"value": "Monto", "variable": "Métrica", "semana": "Semana"},
               title="Ventas Netas vs Gasto en Pauta")
fig1.update_layout(height=400, template="plotly_white", title_font=dict(size=18))

fig2 = px.line(df_roas, x="semana", y="roas", markers=True,
               title="ROAS Semanal", labels={"roas": "ROAS", "semana": "Semana"})
fig2.update_layout(height=400, template="plotly_white", title_font=dict(size=18))

df_plat = df_viz.groupby(["semana", "plataforma"]).size().reset_index(name="ordenes")
fig3 = px.bar(df_plat, x="semana", y="ordenes", color="plataforma", barmode="stack",
              title="Órdenes por Plataforma", labels={"semana": "Semana"})
fig3.update_layout(height=400, template="plotly_white", title_font=dict(size=18))

fig4 = px.line(df_ret, x="semana", y=["nuevos", "frecuentes", "retencion"], markers=True,
               title="Usuarios Nuevos, Frecuentes y Retención (%)",
               labels={"value": "Cantidad / %", "variable": "Tipo", "semana": "Semana"})
fig4.update_layout(height=400, template="plotly_white", title_font=dict(size=18))

df_grouped["ticket_promedio"] = df_grouped["neto"] / df_grouped["ordenes"]
df_grouped["ticket_promedio_ma7"] = df_grouped["ticket_promedio"].rolling(7).mean()  # <- Nueva columna

fig5 = px.line(df_grouped, x="semana", y=["ticket_promedio", "ticket_promedio_ma7"], markers=True,
               title="Ticket Promedio Semanal (con Media Móvil 7d)",
               labels={"value": "Ticket Promedio", "variable": "Tipo", "semana": "Semana"})
fig5.update_layout(height=400, template="plotly_white", title_font=dict(size=18))


df_dia = df_viz.groupby("sales_date").size().reset_index(name="ordenes")
df_dia["media_movil"] = df_dia["ordenes"].rolling(7).mean()
fig6 = px.line(df_dia, x="sales_date", y=["ordenes", "media_movil"],
               title="Órdenes por Día (con Media Móvil 7d)",
               labels={"value": "Órdenes", "variable": "Tipo", "sales_date": "Fecha"})
fig6.update_layout(height=400, template="plotly_white", title_font=dict(size=18))

fig7 = px.bar(df_viz.groupby("marca").size().reset_index(name="ordenes").sort_values("ordenes", ascending=False),
              x="ordenes", y="marca", orientation="h",
              title="📦 Órdenes por Marca", labels={"ordenes": "Órdenes", "marca": "Marca"},
              template="plotly_white", color_discrete_sequence=["#1f77b4"])
fig7.update_layout(height=400, title_font=dict(size=18))

fig8 = px.bar(df_viz.groupby("plataforma").size().reset_index(name="ordenes").sort_values("ordenes", ascending=False),
              x="ordenes", y="plataforma", orientation="h",
              title="🚚 Órdenes por Plataforma", labels={"ordenes": "Órdenes", "plataforma": "Plataforma"},
              template="plotly_white", color_discrete_sequence=["#2ca02c"])
fig8.update_layout(height=400, title_font=dict(size=18))

fig9 = px.bar(df_viz.groupby("plataforma")["neto"].sum().reset_index().sort_values("neto", ascending=False),
              x="neto", y="plataforma", orientation="h",
              title="💰 Ventas Netas por Plataforma", labels={"neto": "Ventas Netas", "plataforma": "Plataforma"},
              template="plotly_white", color_discrete_sequence=["#ff7f0e"])
fig9.update_layout(height=400, title_font=dict(size=18))

# --- Mostrar todas las gráficas juntas en layout 2xN fijo ---

cols = st.columns(2)
for i, fig in enumerate([fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9]):
    cols[i % 2].plotly_chart(fig, use_container_width=True)
    

# ────────────── BLOQUE RETENCIÓN DE USUARIOS ──────────────

st.markdown("## 👩‍💻 Retención de Usuarios")
st.divider()
# Filtro base
df_ret_f = df_retencion.copy()
if marca_sel != "Todas":
    df_ret_f = df_ret_f[df_ret_f["marca"] == marca_sel]
if plataforma_sel != "Todas":
    df_ret_f = df_ret_f[df_ret_f["plataforma"] == plataforma_sel]

# Rango 1
df_ret_r1 = df_ret_f[
    (df_ret_f["fecha_inicio_semana"] >= pd.to_datetime(rango1[0])) &
    (df_ret_f["fecha_inicio_semana"] <= pd.to_datetime(rango1[1]))
]

nuevos_r1 = df_ret_r1["nuevos"].sum()
frecuentes_r1 = df_ret_r1["frecuentes"].sum()
ordenes_r1_ret = df_r1.shape[0]
retencion_r1 = frecuentes_r1 / ordenes_r1_ret * 100 if ordenes_r1_ret else 0

# Rango 2
df_ret_r2 = df_ret_f[
    (df_ret_f["fecha_inicio_semana"] >= pd.to_datetime(rango2[0])) &
    (df_ret_f["fecha_inicio_semana"] <= pd.to_datetime(rango2[1]))
]

ordenes_r2_total_ret = df_r2.shape[0]
semanas_r2 = (rango2[1] - rango2[0]).days / 7
semanas_r2 = semanas_r2 if semanas_r2 else 1

if accion == "Promedio semanal":
    nuevos_r2 = round(df_ret_r2["nuevos"].sum() / semanas_r2, 0)
    frecuentes_r2 = round(df_ret_r2["frecuentes"].sum() / semanas_r2, 0)
    ordenes_r2_ret = ordenes_r2_total_ret / semanas_r2
else:
    nuevos_r2 = df_ret_r2["nuevos"].sum()
    frecuentes_r2 = df_ret_r2["frecuentes"].sum()
    ordenes_r2_ret = ordenes_r2_total_ret

retencion_r2 = frecuentes_r2 / ordenes_r2_ret * 100 if ordenes_r2_ret else 0

# Deltas
def delta(x1, x2):
    return (x1 - x2) / x2 * 100 if x2 else 0

delta_nuevos = delta(nuevos_r1, nuevos_r2)
delta_frecuentes = delta(frecuentes_r1, frecuentes_r2)
delta_retencion = delta(retencion_r1, retencion_r2)
delta_ordenes_ret = delta(ordenes_r1_ret, ordenes_r2_ret)

# Display
st.markdown("#### Rango 1")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Órdenes", f"{ordenes_r1_ret:,}", f"{delta_ordenes_ret:+.2f}%")
col2.metric("Usuarios nuevos", f"{nuevos_r1:,}", f"{delta_nuevos:+.2f}%")
col3.metric("Usuarios frecuentes", f"{frecuentes_r1:,}", f"{delta_frecuentes:+.2f}%")
col4.metric("Retención", f"{retencion_r1:.2f}%", f"{delta_retencion:+.2f}%")

st.markdown("#### Rango 2")
col5, col6, col7, col8 = st.columns(4)
col5.metric("Órdenes", f"{ordenes_r2_ret:,.2f}" if accion == "Promedio semanal" else f"{int(ordenes_r2_ret):,}")
col6.metric("Usuarios nuevos", f"{nuevos_r2:,}")
col7.metric("Usuarios frecuentes", f"{frecuentes_r2:,}")
col8.metric("Retención", f"{retencion_r2:.2f}%")

# ────────────── BLOQUE MÉTRICAS GENERALES ──────────────
st.markdown("## 📶 Métricas Generales")
st.divider()

# Filtros
df_m = df_metricas.copy()
if marca_sel != "Todas":
    df_m = df_m[df_m["marca"] == marca_sel]

# Rango 1
df_m_r1 = df_m[(df_m["fecha_inicio_semana"] >= pd.to_datetime(rango1[0])) &
               (df_m["fecha_fin_semana"] <= pd.to_datetime(rango1[1]))]
conect_r1 = df_m_r1["conectividad"].mean() * 100  # Ajustado
calif_r1 = df_m_r1["calificacion"].mean()

# Rango 2
df_m_r2 = df_m[(df_m["fecha_inicio_semana"] >= pd.to_datetime(rango2[0])) &
               (df_m["fecha_fin_semana"] <= pd.to_datetime(rango2[1]))]
conect_r2 = df_m_r2["conectividad"].mean() * 100  # Ajustado
calif_r2 = df_m_r2["calificacion"].mean()

# Deltas
delta_conect = (conect_r1 - conect_r2) / conect_r2 * 100 if conect_r2 else 0
delta_calif = (calif_r1 - calif_r2) / calif_r2 * 100 if calif_r2 else 0

# Semáforo
def color_delta(val):
    if val > 5:
        return "🟢"
    elif val > -5:
        return "🟡"
    else:
        return "🔴"

# Display
st.markdown("#### Rango 1")
col1, col2 = st.columns(2)
col1.metric("Conectividad", f"{conect_r1:.2f}%", f"{delta_conect:+.2f}%" + f" {color_delta(delta_conect)}")
col2.metric("Calificación", f"{calif_r1:.2f} / 5", f"{delta_calif:+.2f}%" + f" {color_delta(delta_calif)}")

st.markdown("#### Rango 2")
col3, col4 = st.columns(2)
col3.metric("Conectividad", f"{conect_r2:.2f}%")
col4.metric("Calificación", f"{calif_r2:.2f} / 5")

# ────────────── HEATMAP SEMANAL DE ÓRDENES ──────────────
st.markdown("## 📅 Heatmap Semanal de Órdenes")
st.divider()

# Agrupar por fecha y obtener día de la semana y semana
df_heatmap = df_r1.copy()
df_heatmap["dia_semana"] = df_heatmap["sales_date"].dt.day_name()
df_heatmap["semana"] = df_heatmap["sales_date"] - pd.to_timedelta(df_heatmap["sales_date"].dt.weekday, unit="d")

# Orden de días de la semana
dias_orden = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df_heatmap["dia_semana"] = pd.Categorical(df_heatmap["dia_semana"], categories=dias_orden, ordered=True)

# Agrupación y pivot
df_hm = df_heatmap.groupby(["semana", "dia_semana"]).size().reset_index(name="ordenes")
df_pivot = df_hm.pivot(index="dia_semana", columns="semana", values="ordenes").fillna(0)

# Graficar
import plotly.express as px
fig_heatmap = px.imshow(
    df_pivot,
    color_continuous_scale="Blues",
    aspect="auto",
    labels=dict(x="Semana", y="Día de la semana", color="Órdenes"),
    text_auto=True
)
fig_heatmap.update_layout(
    title="Heatmap de Pedidos por Día y Semana",
    height=500,
    title_font=dict(size=18),
    font=dict(color="black"),
    coloraxis_colorbar=dict(title="Órdenes")
)
st.plotly_chart(fig_heatmap, use_container_width=True)
