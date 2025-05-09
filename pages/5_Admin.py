import pandas as pd
import streamlit as st
from config.supa_base_client import get_supabase_client

supabase = get_supabase_client()

if st.session_state.get("rol") != "dueno":
    st.error("Acceso denegado.")
    st.stop()

st.title("👑 Administración de Usuarios")

usuarios = supabase.table("usuarios").select("*").execute().data
df = pd.DataFrame(usuarios)[["usuario", "rol", "fecha_creacion"]]
st.dataframe(df)

st.subheader("Agregar nuevo usuario")
with st.form("nuevo_usuario"):
    nuevo_user = st.text_input("Usuario")
    nueva_pass = st.text_input("Contraseña", type="password")
    nuevo_rol = st.selectbox("Rol", ["dueno", "empleado"])
    submitted = st.form_submit_button("Crear")
    if submitted:
        supabase.table("usuarios").insert({
            "usuario": nuevo_user,
            "contrasena": nueva_pass,
            "rol": nuevo_rol
        }).execute()
        st.success("Usuario creado")

# Registro de accesos (opcional)
if st.checkbox("Mostrar registro de accesos"):
    accesos = pd.DataFrame(
        supabase.table("accesos").select("usuario_id, fecha_hora").order("fecha_hora", desc=True).execute().data
    )
    usuarios_df = pd.DataFrame(usuarios)[["id", "usuario"]]
    accesos = accesos.merge(usuarios_df, left_on="usuario_id", right_on="id", how="left")
    accesos = accesos[["usuario", "fecha_hora"]]
    st.dataframe(accesos)
    
st.subheader("Eliminar Usuario")

usuarios = supabase.table("usuarios").select("usuario", "rol").execute().data
df_usuarios = pd.DataFrame(usuarios)

if not df_usuarios.empty:
    lista_usuarios = df_usuarios["usuario"].tolist()
    usuario_a_eliminar = st.selectbox("Selecciona el usuario a eliminar", lista_usuarios, key="elim_usuario")

    if st.button("Eliminar Usuario Seleccionado"):
        if usuario_a_eliminar == st.session_state["usuario"]:
            st.error("❌ No puedes eliminar tu propio usuario.")
        else:
            res = supabase.table("usuarios").delete().eq("usuario", usuario_a_eliminar).execute()
            if res.data:
                st.success(f"Usuario '{usuario_a_eliminar}' eliminado correctamente.")
                st.rerun()
            else:
                st.error("❌ Error al eliminar el usuario.")
else:
    st.info("No hay usuarios para eliminar.")


# --- Sección 1: Mostrar tabla de marcas actuales ---
st.markdown("## 🏷️ Marcas Registradas")

marcas = supabase.table("mapa_marcas").select("*").execute().data
df_marcas = pd.DataFrame(marcas)
if not df_marcas.empty:
    df_marcas = df_marcas[["codigo", "nombre"]].sort_values("nombre")
    st.dataframe(df_marcas, use_container_width=True)
else:
    st.info("No hay marcas registradas aún.")

# --- Sección 2: Agregar nueva marca ---
st.subheader("Agregar Nueva Marca")

with st.form("nueva_marca"):
    nuevo_codigo = st.text_input("Código (2-3 letras)", max_chars=4).strip().upper()
    nuevo_nombre = st.text_input("Nombre de la Marca").strip()
    enviar = st.form_submit_button("Agregar Marca")

    if enviar:
        if not nuevo_codigo or not nuevo_nombre:
            st.warning("Completa todos los campos.")
        elif any(row["codigo"] == nuevo_codigo for row in marcas):
            st.error("Este código ya está registrado.")
        else:
            res = supabase.table("mapa_marcas").insert({
                "codigo": nuevo_codigo,
                "nombre": nuevo_nombre
            }).execute()
            if res.data:
                st.success(f"Marca '{nuevo_nombre}' agregada exitosamente.")
                st.rerun()
            else:
                st.error("❌ Ocurrió un error al insertar la nueva marca.")

st.subheader("Eliminar Marca")

if not df_marcas.empty:
    codigos_marca = df_marcas["codigo"].tolist()
    marca_a_eliminar = st.selectbox("Selecciona el código de marca a eliminar", codigos_marca, key="elim_marca")
    if st.button("Eliminar Marca Seleccionada"):
        res = supabase.table("mapa_marcas").delete().eq("codigo", marca_a_eliminar).execute()
        if res.data:
            st.success(f"Marca '{marca_a_eliminar}' eliminada correctamente.")
            st.rerun()
        else:
            st.error("❌ Error al eliminar la marca.")
else:
    st.info("No hay marcas para eliminar.")
