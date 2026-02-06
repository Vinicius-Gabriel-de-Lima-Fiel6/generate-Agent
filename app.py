import streamlit as st
from openai import OpenAI
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

# Inicialização do OpenAI (Llama-3 via Groq ou similar)
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=st.secrets["GROQ_API_KEY"]
)

# --- FUNÇÕES ---

def deploy_to_automation(blueprint):
    """Envia o blueprint para o Webhook do Make"""
    url = st.secrets["N8N_WEBHOOK_URL"] # Mantive o nome da secret, mas use a URL do Make
    
    payload = {
        "workflow_name": blueprint.get("name", "Novo Agente"),
        "blueprint": blueprint
    }
    
    # Envio simples para o Webhook
    response = requests.post(url, json=payload)
    return response

# --- INTERFACE ---
st.title("🚀 Criador de Agentes Automáticos")
st.subheader("O que você deseja que o seu robô faça?")

user_input = st.text_area(
    "Descreva o objetivo (ex: me mande um oi de 30 em 30 segundos no WhatsApp)",
    placeholder="Eu quero um agente que..."
)

if st.button("Gerar e Ativar Agente"):
    if user_input:
        with st.spinner("Llama-3 criando a lógica do agente..."):
            try:
                # 1. IA gera o Blueprint
                prompt = f"""
                Você é um arquiteto de automação. Crie um JSON de configuração para um agente:
                Objetivo: {user_input}
                Retorne APENAS o JSON com: 'name', 'trigger' e 'action'.
                """
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Limpeza básica do retorno da IA
                content = completion.choices[0].message.content
                blueprint = json.loads(content[content.find("{"):content.rfind("}")+1])
                
                # 2. Envia para o Make (Automação)
                res = deploy_to_automation(blueprint)
                
                # --- CORREÇÃO DO ERRO DE JSON ---
                try:
                    wf_data = res.json()
                    wf_id = wf_data.get("id", "make-flow")
                except:
                    # Se o Make responder texto puro (Accepted), definimos um ID padrão
                    wf_id = "make-flow-active"
                
                # 3. Salva no Supabase (Banco de Dados)
                company_id = "00000000-0000-0000-0000-000000000000" # Use UUID ou texto se mudou o SQL
                
                db_data = {
                    "company_id": company_id,
                    "nome_agente": blueprint.get("name"),
                    "objetivo_bruto": user_input,
                    "n8n_workflow_id": str(wf_id),
                    "blueprint_json": blueprint
                }
                
                st.session_state.supabase.table("agentes").insert(db_data).execute()
                
                st.success("✅ Agente Criado e Enviado ao Make!")
                st.balloons()
                st.json(blueprint)
                
            except Exception as e:
                st.error(f"Erro no processo: {str(e)}")
    else:
        st.warning("Por favor, descreva o que o agente deve fazer.")

# --- FOOTER ---
st.sidebar.info("Utilizando Llama-3.3-70B + Make + Supabase")
