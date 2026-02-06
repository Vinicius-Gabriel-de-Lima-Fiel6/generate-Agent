import streamlit as st
from supabase import create_client

# Conexão
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.set_page_config(page_title="AgentOS", layout="wide")

st.title("🤖 AgentOS: Gestão Nativa")

tab1, tab2 = st.tabs(["⚡ Agentes Ativos", "🛠️ Novo Agente"])

with tab2:
    st.header("Configurar Nova Automação")
    with st.form("new_agent"):
        nome = st.text_input("Nome do Agente", placeholder="Ex: Analista de Vendas")
        modelo = st.selectbox("Modelo", ["Monitor de Leads", "Relatório Financeiro", "Suporte VIP"])
        prompt = st.text_area("Descreva a regra de funcionamento:")
        
        if st.form_submit_button("✅ Salvar e Ativar"):
            supabase.table("agents").insert({
                "company_id": "empresa_01", # Multi-tenant ready
                "name": nome,
                "template_name": modelo,
                "prompt_config": prompt,
                "status": "active"
            }).execute()
            st.success("Agente registrado no motor de execução.")
            st.rerun()

with tab1:
    agentes = supabase.table("agents").select("*").execute().data
    for ag in agentes:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"**{ag['name']}** ({ag['template_name']})")
            col1.caption(f"Prompt: {ag['prompt_config']}")
            
            status = "🟢 Ativo" if ag['status'] == "active" else "🔴 Pausado"
            col2.write(f"Status: {status}")
            
            if col3.button("Alternar", key=ag['id']):
                novo = "paused" if ag['status'] == "active" else "active"
                supabase.table("agents").update({"status": novo}).eq("id", ag['id']).execute()
                st.rerun()
            st.divider()
