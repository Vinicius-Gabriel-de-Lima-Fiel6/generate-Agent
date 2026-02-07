import os
import streamlit as st
from supabase import create_client

def get_supabase():
    # Busca das Secrets do Streamlit Cloud
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def fetch_agents(org_id):
    supabase = get_supabase()
    try:
        res = supabase.table("agents").select("*").eq("organization_id", org_id).execute()
        return res.data
    except Exception as e:
        st.error(f"Erro ao buscar agentes: {e}")
        return []
