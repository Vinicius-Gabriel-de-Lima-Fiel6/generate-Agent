import streamlit as st
from groq import Groq
import requests
from supabase import create_client
import json
import threading
import time

# --- SETUP ---
st.set_page_config(page_title="AI Agent Factory Pro", layout="wide")

# Inicializa Supabase
if "supabase" not in st.session_state:
    st.session_state.supabase = create_client(
        st.secrets["SUPABASE_URL"], 
        st.secrets["SUPABASE_KEY"]
    )

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "agentes_ativos" not in st.session_state:
    st.session_state.agentes_ativos = {}

# --- MOTOR DO AGENTE ---
def worker_agente(nome, personalidade, intervalo, numero, api_url):
    while st.session_state.agentes_ativos.get(nome):
        try:
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": personalidade},
                    {"role": "user", "content": "Gere um status curto para WhatsApp."}
                ]
            )
            msg = chat.choices[0].message.content
            requests.post(api_url, json={"number": numero, "message": msg})
        except:
            pass
        time.sleep(intervalo)

# --- INTERFACE ---
st.title("🤖 Fábrica de Agentes com Supabase")

col_fabrica, col_monitor = st.columns([1, 1])

with col_fabrica:
    st.header("🛠️ Criar Agente")
    missao = st.text_area("O que o agente deve fazer?")
    api_whatsapp = st.text_input("URL da API WhatsApp", "https://sua-api.com/send")
    
    if st.button("Lançar Agente"):
        if missao:
            with st.spinner("IA configurando..."):
                # 1. IA gera configuração
                prompt_eng = f"Crie um JSON para a missão: {missao}. Responda apenas o JSON com: 'nome', 'segundos', 'numero', 'personalidade'."
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt_eng}],
                    response_format={"type": "json_object"}
                )
                data = json.loads(res.choices[0].message.content)
                
                # 2. Salva no Supabase
                db_data = {
                    "nome_agente": data['nome'],
                    "objetivo_bruto": missao,
                    "blueprint_json": data,
                    "company_id": "00000000-0000-0000-0000-000000000000"
                }
                st.session_state.supabase.table("agentes").insert(db_data).execute()
                
                # 3. Inicia Thread
                st.session_state.agentes_ativos[data['nome']] = True
                t = threading.Thread(target=worker_agente, args=(data['nome'], data['personalidade'], data['segundos'], data['numero'], api_whatsapp))
                t.daemon = True
                t.start()
                
                st.success(f"Agente {data['nome']} ativado!") # <-- O parênteses estava faltando aqui ou acima
        else:
            st.warning("Descreva a missão.")

with col_monitor:
    st.header("📊 Monitor")
    try:
        # Busca últimos 5 do banco
        agentes_db = st.session_state.supabase.table("agentes").select("*").order("created_at", desc=True).limit(5).execute()
        for ag in agentes_db.data:
            with st.expander(f"🤖 {ag['nome_agente']}"):
                st.write(f"Missão: {ag['objetivo_bruto']}")
                status = "🟢 Ativo" if st.session_state.agentes_ativos.get(ag['nome_agente']) else "🔴 Offline"
                st.write(f"Status: {status}")
    except:
        st.info("Aguardando primeiro agente...")
