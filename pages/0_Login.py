import streamlit as st
from utils.auth import autenticar_usuario, registrar_acceso

st.set_page_config(page_title="Login", layout="centered")

st.title("🔐 Iniciar sesión")
usuario = st.text_input("Usuario")
contrasena = st.text_input("Contraseña", type="password")

if st.button("Ingresar"):
    user = autenticar_usuario(usuario, contrasena)
    if user:
        st.session_state.usuario = user["usuario"]
        st.session_state.rol = user["rol"]
        st.success(f"Bienvenido, {user['usuario']} ({user['rol']})")
        registrar_acceso(user["id"])
        st.switch_page("pages/1_Ventas.py")  # O redirige según el caso
    else:
        st.error("Credenciales incorrectas")