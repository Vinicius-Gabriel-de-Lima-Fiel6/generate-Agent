import streamlit as st
from supabase import create_client

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("🤖 AI Agent SaaS (Llama 3.3 Versatile)")

tab1, tab2 = st.tabs(["Dashboard", "Novo Agente IA"])

with tab2:
    with st.form("create_ia"):
        nome = st.text_input("Nome do Agente")
        config = st.text_area("Instruções (O que a IA deve fazer?)", 
                            placeholder="Ex: Monitore meu faturamento e sugira 3 ações de marketing se cair 10%")
        if st.form_submit_button("Lançar Agente"):
            supabase.table("agents").insert({
                "name": nome,
                "prompt_config": config,
                "company_id": "tenant_01",
                "status": "active"
            }).execute()
            st.success("Agente em órbita!")

with tab1:
    agentes = supabase.table("agents").select("*").execute().data
    for ag in agentes:
        with st.expander(f"🤖 {ag['name']} - {ag['status']}"):
            st.write("**Configuração do Usuário:**")
            st.info(ag['prompt_config'])
            
            st.write("**Última Execução da IA (Groq):**")
            st.success(ag.get('last_result', 'Aguardando processamento...'))
            
            if st.button("Pausar/Retomar", key=ag['id']):
                novo = "paused" if ag['status'] == "active" else "active"
                supabase.table("agents").update({"status": novo}).eq("id", ag['id']).execute()
                st.rerun()
