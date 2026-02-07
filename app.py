import streamlit as st
from database import fetch_agents
from core import orchestrator_router, get_llm_stream

st.set_page_config(page_title="AI Agent SaaS", layout="wide")

# Sidebar para simular Multi-tenancy
st.sidebar.title("🏢 Painel do Cliente")
org_id = st.sidebar.text_input("Organization ID", value="69792690-3773-455b-9d41-47754972e0b5") 

if not org_id:
    st.warning("Por favor, insira o Organization ID configurado no Supabase.")
    st.stop()

# Carregar agentes da organização
agents = fetch_agents(org_id)

if not agents:
    st.info("Nenhum agente encontrado para esta organização. Verifique o ID ou a tabela no Supabase.")
    st.stop()

st.sidebar.success(f"{len(agents)} agentes carregados.")

# Interface de Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar histórico
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input do Usuário
if prompt := st.chat_input("O que deseja saber?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Lógica do Orquestrador
    with st.status("IA Orquestradora analisando sua solicitação...") as status:
        try:
            target_agent_id = orchestrator_router(prompt, agents)
            # Encontra o agente pelo ID retornado pelo Llama
            agent = next((a for a in agents if a['id'] == target_agent_id), agents[0])
            status.update(label=f"Agente Ativado: **{agent['name']}**", state="complete")
        except Exception as e:
            status.update(label="Usando agente padrão...", state="error")
            agent = agents[0]

    # Gerar Resposta Final
    with st.chat_message("assistant", avatar="🤖"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            stream = get_llm_stream(agent, st.session_state.messages)
            
            for chunk in stream:
                if agent['provider'] == 'groq':
                    content = chunk.choices[0].delta.content
                else:
                    content = chunk.text
                
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Erro na geração da resposta: {e}")
