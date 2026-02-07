import streamlit as st
from database import fetch_agents, get_supabase
from core import orchestrator_router, get_llm_stream, generate_agent_blueprint

st.set_page_config(page_title="AI Factory SaaS", layout="wide")
supabase = get_supabase()

st.sidebar.title("🏢 Admin Painel")
org_id = st.sidebar.text_input("Organization ID", value="seu-uuid-aqui")

tab_chat, tab_factory = st.tabs(["💬 Chat Orquestrado", "🏭 Fábrica de Agentes"])

# --- ABA: FÁBRICA DE AGENTES ---
with tab_factory:
    st.header("Gerar Novo Agente Especialista")
    user_idea = st.text_area("Descreva o que este agente deve fazer:", 
                             placeholder="Ex: Um especialista em análise de contratos jurídicos que foca em cláusulas de rescisão.")
    
    if st.button("Gerar Agente via IA"):
        with st.spinner("O Engenheiro de Prompt está projetando seu agente..."):
            blueprint = generate_agent_blueprint(user_idea)
            
            # Salvar no Supabase
            blueprint["organization_id"] = org_id
            res = supabase.table("agents").insert(blueprint).execute()
            
            if res.data:
                st.success(f"Agente '{blueprint['name']}' criado e treinado com sucesso!")
                st.json(blueprint)
                st.rerun()

# --- ABA: CHAT (Lógica de Execução) ---
with tab_chat:
    agents = fetch_agents(org_id)
    if not agents:
        st.warning("Nenhum agente disponível. Vá na Fábrica e crie um!")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Diga o que você precisa..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Roteamento Automático
        with st.status("Roteando para o melhor especialista...") as status:
            target_id = orchestrator_router(prompt, agents)
            agent = next((a for a in agents if a['id'] == target_id), agents[0])
            status.update(label=f"Especialista Ativo: {agent['name']}", state="complete")

        # Resposta do Agente Gerado
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_res = ""
            stream = get_llm_stream(agent, st.session_state.messages)
            
            for chunk in stream:
                content = chunk.choices[0].delta.content if agent['provider'] == 'groq' else chunk.text
                if content:
                    full_res += content
                    response_placeholder.markdown(full_res + "▌")
            
            response_placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
