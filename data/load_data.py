import pandas as pd
from config.supa_base_client import get_supabase_client

supabase = get_supabase_client()

def load_sales_orders():
    data = supabase.table("sales_orders").select("*").execute().data
    df = pd.DataFrame(data)
    if not df.empty and "sales_date" in df.columns:
        df["sales_date"] = pd.to_datetime(df["sales_date"])
    return df

def load_ad_spend():
    data = supabase.table("ad_spend").select("*").execute().data
    df = pd.DataFrame(data)
    if not df.empty:
        df["fecha_inicio_semana"] = pd.to_datetime(df["fecha_inicio_semana"])
        df["fecha_fin_semana"] = pd.to_datetime(df["fecha_fin_semana"])
    return df

def load_user_retention():
    data = supabase.table("user_retention").select("*").execute().data
    df = pd.DataFrame(data)
    if not df.empty:
        df["fecha_inicio_semana"] = pd.to_datetime(df["fecha_inicio_semana"])
        df["fecha_fin_semana"] = pd.to_datetime(df["fecha_fin_semana"])
    return df

def load_traffic_metrics():
    data = supabase.table("traffic_metrics").select("*").execute().data
    df = pd.DataFrame(data)
    if not df.empty:
        df["fecha_inicio_semana"] = pd.to_datetime(df["fecha_inicio_semana"])
        df["fecha_fin_semana"] = pd.to_datetime(df["fecha_fin_semana"])
    return df

def load_quejas():
    data = supabase.table("quejas").select("*").execute().data
    df = pd.DataFrame(data)
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])
    return df

def load_metricas_generales():
    data = supabase.table("metricas_generales").select("*").execute().data
    df = pd.DataFrame(data)
    if not df.empty:
        df["fecha_inicio_semana"] = pd.to_datetime(df["fecha_inicio_semana"])
        df["fecha_fin_semana"] = pd.to_datetime(df["fecha_fin_semana"])
    return df

import pandas as pd
from config.supa_base_client import get_supabase_client

supabase = get_supabase_client()

def load_retrasos():
    data = supabase.table("retrasos").select("*").execute().data
    df = pd.DataFrame(data)
    if not df.empty:
        df["fecha_inicio_semana"] = pd.to_datetime(df["fecha_inicio_semana"])
        df["fecha_fin_semana"] = pd.to_datetime(df["fecha_fin_semana"])
        df["total_retrasos"] = pd.to_numeric(df["total_retrasos"], errors="coerce").fillna(0).astype(int)
        if "plataforma" not in df.columns:
            df["plataforma"] = "Desconocido"  # Por si aún hay registros antiguos sin plataforma
        else:
            df["plataforma"] = df["plataforma"].fillna("Desconocido").astype(str)
    return df


def load_traffic_log():
    data = supabase.table("traffic_log").select("*").order("fecha", desc=True).execute().data
    df = pd.DataFrame(data)
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])
    return df
