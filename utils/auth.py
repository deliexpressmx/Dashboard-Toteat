import pandas as pd
from config.supa_base_client import get_supabase_client

supabase = get_supabase_client()

def autenticar_usuario(usuario, contrasena):
    data = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("contrasena", contrasena).execute().data
    return data[0] if data else None

def registrar_acceso(usuario_id):
    supabase.table("accesos").insert({"usuario_id": usuario_id}).execute()