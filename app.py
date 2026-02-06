import streamlit as st
from groq import Groq
import requests
from supabase import create_client, Client
import json

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Gerador de Agentes AI", page_icon="🤖")

# Inicialização do Supabase
if "supabase" not in st.session_state:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    st.session_state.supabase = create_client(url, key)

# Inicialização do GROQ (Usando a biblioteca oficial do Groq)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FUNÇÕES ---

def deploy_to_automation(blueprint):
    """Envia o blueprint para o Webhook do Make"""
    url = st.secrets["N8N_WEBHOOK_URL"] # URL do seu Webhook no Make
    
    payload = {
        "workflow_name": blueprint.get("name", "Novo Agente"),
        "blueprint": blueprint
    }
    
    # Envio para o Make
    response = requests.post(url, json=payload)
    return response

# --- INTERFACE ---
st.title("🚀 Criador de Agentes Automáticos")
st.subheader("Llama-3.3-70B + Make + Supabase")

user_input = st.text_area(
    "O que seu robô deve fazer?",
    placeholder="Ex: Mandar mensagem de 30 em 30 segundos..."
)

if st.button("Gerar e Ativar Agente"):
    if user_input:
        with st.spinner("Groq processando Llama-3.3-70B..."):
            try:
                # 1. IA gera o Blueprint
                prompt = f"Crie um JSON para um agente: {user_input}. Retorne APENAS o JSON com 'name', 'trigger' e 'action'."
                
                chat_completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Extração do JSON
                content = chat_completion.choices[0].message.content
                blueprint = json.loads(content[content.find("{"):content.rfind("}")+1])
                
                # 2. Envia para o Make
                res = deploy_to_automation(blueprint)
                
                # Tratamento de resposta do Make (evita o erro JSONDecodeError)
                try:
                    wf_data = res.json()
                    wf_id = wf_data.get("id", "make-flow")
                except:
                    wf_id = "make-flow-ativo"
                
                # 3. Salva no Supabase
                # Nota: Certifique-se que o RLS está desativado no Supabase para este teste
                db_data = {
                    "company_id": "00000000-0000-0000-0000-000000000000",
                    "nome_agente": blueprint.get("name"),
                    "objetivo_bruto": user_input,
                    "n8n_workflow_id": str(wf_id),
                    "blueprint_json": blueprint
                }
                
                st.session_state.supabase.table("agentes").insert(db_data).execute()
                
                st.success("✅ Sucesso! Agente registrado e enviado ao Make.")
                st.balloons()
                st.json(blueprint)
                
            except Exception as e:
                st.error(f"Erro detectado: {str(e)}")
    else:
        st.warning("Descreva o objetivo do agente.")
