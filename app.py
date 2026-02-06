import streamlit as st
from groq import Groq
import requests
from supabase import create_client
import json
import threading
import time

# --- CONFIGURAÇÕES E CONEXÕES ---
st.set_page_config(page_title="AI Agent Factory Pro", layout="wide")

# Inicializa Supabase (mesma configuração anterior)
if "supabase" not in st.session_state:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    st.session_state.supabase = create_client(url, key)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Estado para monitorar agentes em tempo real nesta sessão
if "agentes_ativos" not in st.session_state:
    st.session_state.agentes_ativos = {}

# --- MOTOR DE EXECUÇÃO DO AGENTE ---
def worker_agente(nome, prompt_ia, intervalo, numero, api_url):
    """Função que roda em background para enviar as mensagens"""
    while st.session_state.agentes_ativos.get(nome, False):
        try:
            # IA gera a mensagem dinâmica baseada na personalidade
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": prompt_ia},
                          {"role": "user", "content": "Gere a mensagem de agora."}]
            )
            msg_texto = chat.choices[0].message.content
            
            # Envio real para o WhatsApp (Sua API)
            requests.post(api_url, json={"number": numero, "message": msg_texto})
        except Exception as e:
            print(f"Erro no agente {nome}: {e}")
        
        time.sleep(intervalo)

# --- INTERFACE ---
st.title("🤖 Fábrica de Agentes Autônomos")
st.sidebar.header("📊 Agentes Registrados (Supabase)")

# Layout de Colunas
col_input, col_monitor = st.columns([1, 1])

with col_input:
    st.subheader("🛠️ Criar Novo Agente")
    missao = st.text_area("O que o agente deve fazer?", "Ex: Me avisar sobre o clima a cada 30 segundos")
    api_whatsapp = st.text_input("URL da sua API WhatsApp", "https://sua-api.com/send")
    
    if st.button("Lançar Agente"):
        with st.spinner("IA configurando agente..."):
            # 1. IA cria o blueprint
            prompt_eng = f"Crie um JSON para: {missao}. Inclua 'nome', 'segundos', 'numero', 'personalidade'."
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
            
            # 3. Inicia o loop em segundo plano
            st.session_state.agentes_ativos[data['nome']] = True
            t = threading.Thread(target=worker_agente, args=(data['nome'], data['personalidade'], data['segundos'], data['numero'], api_whatsapp))
            t.daemon = True
            t.start()
            
            st.success(
