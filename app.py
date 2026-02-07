import streamlit as st
from supabase import create_client
from core import get_llm_response
import os

# Configuração da página
st.set_page_config(page_title="AI Multi-Agent SaaS", layout="wide")

# Conectar ao Supabase (Via Secrets no Streamlit Cloud)
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("🤖 Orchestrator SaaS")

# Simulação de Contexto Multi-tenant (Em prod, vem do login)
org_id = st.sidebar.text_input("ID da Organização Cliente", value="default-org")

# Sidebar: Lista de Agentes desta Org
st.sidebar.header("Seus Agentes")
agents_res = supabase.table("agents").select("*").eq("organization_id", org_id).execute()
agents = agents_res.data

if not agents:
    st.info("Crie seu primeiro agente no Supabase para começar!")
else:
    selected_agent_name = st.sidebar.selectbox("Agente Ativo", [a['name'] for a in agents])
    agent = next(a for a in agents if a['name'] == selected_agent_name)
    st.sidebar.caption(f"Role: {agent['role']} | Model: {agent['model_name']}")

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Como posso ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Chamada ao Core (Groq/Gemini)
        response_stream = get_llm_response(agent, st.session_state.messages)
        
        full_response = ""
        placeholder = st.empty()
        
        for chunk in response_stream:
            # Tratamento de chunk conforme o provedor
            content = chunk.choices[0].delta.content if agent['provider'] == 'groq' else chunk.text
            if content:
                full_response += content
                placeholder.markdown(full_response + "▌")
        
        placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
