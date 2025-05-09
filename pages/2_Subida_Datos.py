import streamlit as st

if "usuario" not in st.session_state:
    st.warning("Por favor, inicia sesión para acceder al dashboard.")
    st.stop()
import pandas as pd
from config.supa_base_client import get_supabase_client
supabase = get_supabase_client()

st.set_page_config(page_title="Subida de Datos", layout="wide")


st.title("📤 Subida de datos")
st.divider()

# ───── Subida de Pauta ─────
st.markdown("## 📣 Subida de Pauta")
st.caption("**Orden de columnas requerido:** `marca`, `plataforma`, `fecha_inicio_semana`, `fecha_fin_semana`, `gasto`")
archivo_pauta = st.file_uploader("Sube archivo de `ad_spend`", type=["xlsx", "csv"], key="pauta")
if archivo_pauta:
    try:
        df = pd.read_excel(archivo_pauta) if archivo_pauta.name.endswith("xlsx") else pd.read_csv(archivo_pauta)
        st.dataframe(df.head())

        required_cols = {"marca", "plataforma", "fecha_inicio_semana", "fecha_fin_semana", "gasto"}
        if not required_cols.issubset(df.columns):
            st.error(f"Faltan columnas: {required_cols}")
        else:
            df = df.dropna(subset=required_cols)
            df["fecha_inicio_semana"] = pd.to_datetime(df["fecha_inicio_semana"]).dt.strftime("%Y-%m-%d")
            df["fecha_fin_semana"] = pd.to_datetime(df["fecha_fin_semana"]).dt.strftime("%Y-%m-%d")
            df["gasto"] = pd.to_numeric(df["gasto"], errors="coerce").fillna(0)
            if st.button("Subir a Supabase", key="boton_pauta"):
                res = supabase.table("ad_spend").insert(df.to_dict("records")).execute()
                st.success("✅ Datos de pauta subidos correctamente")
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.divider()

# ───── Subida de Retención ─────
st.markdown("## 👩‍💻 Retención de Usuarios")
st.caption("**Orden de columnas requerido:** `marca`, `plataforma`, `fecha_inicio_semana`, `fecha_fin_semana`, `nuevos`, `frecuentes`")
archivo_retencion = st.file_uploader("Sube archivo de `user_retention`", type=["xlsx", "csv"], key="retencion")
if archivo_retencion:
    try:
        df = pd.read_excel(archivo_retencion) if archivo_retencion.name.endswith("xlsx") else pd.read_csv(archivo_retencion)
        st.dataframe(df.head())

        required_cols = {"marca", "plataforma", "fecha_inicio_semana", "fecha_fin_semana", "nuevos", "frecuentes"}
        if not required_cols.issubset(df.columns):
            st.error(f"Faltan columnas: {required_cols}")
        else:
            df = df.dropna(subset=required_cols)
            df["fecha_inicio_semana"] = pd.to_datetime(df["fecha_inicio_semana"]).dt.strftime("%Y-%m-%d")
            df["fecha_fin_semana"] = pd.to_datetime(df["fecha_fin_semana"]).dt.strftime("%Y-%m-%d")
            df["nuevos"] = pd.to_numeric(df["nuevos"], errors="coerce").fillna(0)
            df["frecuentes"] = pd.to_numeric(df["frecuentes"], errors="coerce").fillna(0)
            if st.button("Subir a Supabase", key="boton_retencion"):
                res = supabase.table("user_retention").insert(df.to_dict("records")).execute()
                st.success("✅ Datos de retención subidos correctamente")
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.divider()

# ───── Subida de Tráfico ─────
st.markdown("## 🚦 Tráfico y Conversión")
st.caption("**Orden de columnas requerido:** `marca`, `fecha_inicio_semana`, `fecha_fin_semana`, `trafico`, `vieron_menu`, `agregaron_articulos`")
archivo_trafico = st.file_uploader("Sube archivo de `traffic_metrics`", type=["xlsx", "csv"], key="trafico")
if archivo_trafico:
    try:
        df = pd.read_excel(archivo_trafico) if archivo_trafico.name.endswith("xlsx") else pd.read_csv(archivo_trafico)
        st.dataframe(df.head())

        required_cols = {"marca", "fecha_inicio_semana", "fecha_fin_semana", "trafico", "vieron_menu", "agregaron_articulos"}
        if not required_cols.issubset(df.columns):
            st.error(f"Faltan columnas: {required_cols}")
        else:
            df = df.dropna(subset=required_cols)
            df["fecha_inicio_semana"] = pd.to_datetime(df["fecha_inicio_semana"]).dt.strftime("%Y-%m-%d")
            df["fecha_fin_semana"] = pd.to_datetime(df["fecha_fin_semana"]).dt.strftime("%Y-%m-%d")
            df["trafico"] = pd.to_numeric(df["trafico"], errors="coerce").fillna(0)
            df["vieron_menu"] = pd.to_numeric(df["vieron_menu"], errors="coerce").fillna(0)
            df["agregaron_articulos"] = pd.to_numeric(df["agregaron_articulos"], errors="coerce").fillna(0)
            if st.button("Subir a Supabase", key="boton_trafico"):
                res = supabase.table("traffic_metrics").insert(df.to_dict("records")).execute()
                st.success("✅ Datos de tráfico subidos correctamente")
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.divider()

# ───── Subida de Bitácora ─────
st.markdown("## 📝 Bitácora de Acciones")
st.caption("Sube el archivo de `traffic_log` con columnas: plataforma, fecha, accion, marcas")
archivo_bitacora = st.file_uploader("", type=["xlsx", "csv"], key="bitacora")
if archivo_bitacora:
    try:
        df = pd.read_excel(archivo_bitacora) if archivo_bitacora.name.endswith("xlsx") else pd.read_csv(archivo_bitacora)
        st.dataframe(df.head())

        required_cols = {"plataforma", "fecha", "accion", "marcas"}
        if not required_cols.issubset(df.columns):
            st.error(f"Faltan columnas: {required_cols}")
        else:
            df = df.dropna(subset=required_cols)
            df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%Y-%m-%d")
            if st.button("Subir a Supabase", key="boton_bitacora"):
                res = supabase.table("traffic_log").insert(df.to_dict("records")).execute()
                st.success("✅ Bitácora subida correctamente")
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.divider()

# ───── Subida de Quejas ─────
st.markdown("## 😠 Quejas y Comentarios")
st.caption("Sube el archivo de `quejas` con columnas: fecha, marca, plataforma, turno, categoria, comentario")

archivo_quejas = st.file_uploader("", type=["xlsx", "csv"], key="quejas")
if archivo_quejas:
    try:
        df = pd.read_excel(archivo_quejas) if archivo_quejas.name.endswith("xlsx") else pd.read_csv(archivo_quejas)
        st.dataframe(df.head())

        required_cols = {"fecha", "marca", "plataforma", "turno", "categoria", "comentario"}
        if not required_cols.issubset(df.columns):
            st.error(f"❌ Faltan columnas requeridas. Se esperaban: {required_cols}")
        else:
            df = df.dropna(subset=required_cols)

            for col in required_cols:
                if df[col].astype(str).str.strip().eq("").any():
                    st.error(f"❌ Hay valores vacíos en la columna: {col}")
                    st.stop()

            df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.strftime("%Y-%m-%d")
            df["comentario"] = df["comentario"].astype(str)

            if st.button("Subir a Supabase", key="boton_quejas"):
                try:
                    res = supabase.table("quejas").insert(df.to_dict("records")).execute()
                    if res.data:
                        st.success("✅ Quejas subidas correctamente")
                    else:
                        st.error("⚠️ Error de Supabase: no se insertaron registros. Verifica que los datos sean válidos.")
                        st.write(res)
                except Exception as upload_err:
                    st.error(f"❌ Error de Supabase: {str(upload_err)}")

    except Exception as e:
        st.error(f"❌ Error procesando el archivo: {str(e)}")

st.divider()

# --- Subida de Retrasos ---
st.markdown("## 🕒 Subida de Retrasos")
st.caption("**Orden de columnas requerido:** `marca`, `fecha_inicio_semana`, `fecha_fin_semana`, `plataforma`, `total_retrasos`")
archivo_retrasos = st.file_uploader("Sube archivo de `retrasos`", type=["xlsx", "csv"], key="retrasos")
if archivo_retrasos:
    try:
        df = pd.read_excel(archivo_retrasos) if archivo_retrasos.name.endswith("xlsx") else pd.read_csv(archivo_retrasos)
        st.dataframe(df.head())

        required_cols = {"marca", "plataforma", "fecha_inicio_semana", "fecha_fin_semana", "total_retrasos"}
        if not required_cols.issubset(df.columns):
            st.error(f"❌ Faltan columnas requeridas. Se esperaban: {required_cols}")
        else:
            df = df.dropna(subset=required_cols)
            df["fecha_inicio_semana"] = pd.to_datetime(df["fecha_inicio_semana"]).dt.strftime("%Y-%m-%d")
            df["fecha_fin_semana"] = pd.to_datetime(df["fecha_fin_semana"]).dt.strftime("%Y-%m-%d")
            df["total_retrasos"] = pd.to_numeric(df["total_retrasos"], errors="coerce").fillna(0).astype(int)
            df["plataforma"] = df["plataforma"].astype(str)

            if st.button("Subir a Supabase", key="boton_retrasos"):
                res = supabase.table("retrasos").insert(df.to_dict("records")).execute()
                if res.data:
                    st.success("✅ Datos de retrasos subidos correctamente")
                else:
                    st.error("⚠️ Error al subir. Revisa la respuesta:")
                    st.write(res)
    except Exception as e:
        st.error(f"Error procesando el archivo: {str(e)}")


st.divider()
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta


# Configuración API Toteat
BASE_URL = "https://toteatglobal.appspot.com/mw/or/1.0/sales"
XIR = "4723725219659776"
XIL = "1"
XIU = "1001"
XAPITOKEN = "JH8yp24arxgaoIIk3S6qNqWOe1PmmgGm"

@st.cache_data(ttl=600)
def obtener_mapeo_marcas():
    rows = supabase.table("mapa_marcas").select("codigo", "nombre").execute().data
    return {row["codigo"]: row["nombre"] for row in rows}


# Funciones auxiliares

def extraer_marca(products, mapeo):
    if isinstance(products, list):
        for prod in products:
            pid = str(prod.get("id", "")).strip().upper()
            for n in (3, 2):
                pref = pid[:n]
                if pref in mapeo:
                    return mapeo[pref]
    return "Sin marca"



def extraer_plataforma(payment_forms):
    if isinstance(payment_forms, list) and payment_forms:
        return payment_forms[0].get("name")
    return None

st.markdown("## 📥 Descarga de ventas faltantes")
if st.button("Descargar ventas faltantes"):
    try:
        # Obtener la última fecha existente
        res = supabase.table("sales_orders").select("sales_date").order("sales_date", desc=True).limit(1).execute()
        if res.data:
            ultima_fecha = pd.to_datetime(res.data[0]["sales_date"]).date()
        else:
            ultima_fecha = datetime.strptime("2024-01-01", "%Y-%m-%d").date()  # Fecha mínima si no hay datos

        hoy = datetime.now().date()
        fechas_faltantes = pd.date_range(start=ultima_fecha + timedelta(days=1), end=hoy - timedelta(days=1)).date

        mapeo = obtener_mapeo_marcas()        
        
        if len(fechas_faltantes) == 0:
            st.info("✅ No hay fechas faltantes. Ya estás al día.")
        else:
            total_registros = 0
            for fecha in fechas_faltantes:
                fecha_str = fecha.strftime("%Y-%m-%d")
                fecha_api = fecha.strftime("%Y%m%d")

                params = {
                    "ini": fecha_api,
                    "end": fecha_api,
                    "xir": XIR,
                    "xil": XIL,
                    "xiu": XIU,
                    "xapitoken": XAPITOKEN
                }
                response = requests.get(BASE_URL, params=params)
                data = response.json()

                if "data" in data and isinstance(data["data"], list):
                    registros = []
                    for venta in data["data"]:
                        try:
                            order_id = venta.get("orderId")
                            date_str = venta.get("dateClosed") or venta.get("dateOpen")
                            sales_date = pd.to_datetime(date_str).date() if date_str else fecha

                            products = venta.get("products", [])
                            marca = extraer_marca(products, mapeo)

                            payment_forms = venta.get("paymentForms", [])
                            plataforma = extraer_plataforma(payment_forms)

                            total = venta.get("total", 0)
                            descuentos = venta.get("discounts", 0)
                            neto = total + descuentos

                            registros.append({
                                "order_id": order_id,
                                "sales_date": fecha_str,
                                "marca": marca,
                                "plataforma": plataforma,
                                "total": total,
                                "descuentos": descuentos,
                                "neto": neto
                            })
                        except Exception as e:
                            st.warning(f"Error procesando venta {order_id}: {e}")

                    if registros:
                        res_insert = supabase.table("sales_orders").insert(registros).execute()
                        total_registros += len(registros)

            st.success(f"✅ Se insertaron {total_registros} registros de ventas faltantes.")
    except Exception as e:
        st.error(f"❌ Error durante la descarga: {str(e)}")
        
st.divider()
        
# ───── Subida de Métricas Generales ─────
st.markdown("## 📈 Métricas Generales")
st.caption("**Orden de columnas requerido:** `marca`, `plataforma`, `fecha_inicio_semana`, `fecha_fin_semana`, `conectividad`, `calificacion`")

archivo_metricas = st.file_uploader("Sube archivo de `metricas_generales`", type=["xlsx", "csv"], key="metricas_generales")
if archivo_metricas:
    try:
        df = pd.read_excel(archivo_metricas) if archivo_metricas.name.endswith("xlsx") else pd.read_csv(archivo_metricas)
        st.dataframe(df.head())

        required_cols = {"marca", "plataforma", "fecha_inicio_semana", "fecha_fin_semana", "conectividad", "calificacion"}
        if not required_cols.issubset(df.columns):
            st.error(f"❌ Faltan columnas requeridas. Se esperaban: {required_cols}")
        else:
            df = df.dropna(subset=required_cols)
            df["fecha_inicio_semana"] = pd.to_datetime(df["fecha_inicio_semana"]).dt.strftime("%Y-%m-%d")
            df["fecha_fin_semana"] = pd.to_datetime(df["fecha_fin_semana"]).dt.strftime("%Y-%m-%d")
            df["conectividad"] = pd.to_numeric(df["conectividad"], errors="coerce").fillna(0)
            df["calificacion"] = pd.to_numeric(df["calificacion"], errors="coerce").fillna(0)

            if st.button("Subir a Supabase", key="boton_metricas"):
                res = supabase.table("metricas_generales").insert(df.to_dict("records")).execute()
                if res.data:
                    st.success("✅ Datos de métricas generales subidos correctamente")
                else:
                    st.error("⚠️ Hubo un error al insertar los datos. Revisa la respuesta:")
                    st.write(res)
    except Exception as e:
        st.error(f"❌ Error procesando el archivo: {str(e)}")
