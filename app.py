import streamlit as st
from supabase import create_client

# Configuração de conexão
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Configure as chaves do Supabase no .streamlit/secrets.toml")

st.set_page_config(page_title="AI Agent SaaS", layout="wide")

st.title("🤖 Gerenciador de Agentes IA")

tab1, tab2 = st.tabs(["📋 Meus Agentes", "✨ Novo Agente"])

with tab2:
    st.subheader("Configurar novo agente autônomo")
    templates = supabase.table("agent_templates").select("*").execute().data
    
    with st.form("form_create"):
        nome_agente = st.text_input("Nome do Agente", placeholder="Ex: Meu Consultor de Vendas")
        template_escolhido = st.selectbox("Escolha um Modelo", [t['name'] for t in templates])
        instrucao = st.text_area("Descreva o que esse agente deve fazer por você:")
        
        if st.form_submit_button("✅ Ativar Agente"):
            supabase.table("agents").insert({
                "company_id": "cliente_01",
                "name": nome_agente,
                "prompt_config": f"Modelo: {template_escolhido}. Instrução: {instrucao}",
                "status": "active"
            }).execute()
            st.success("Agente ativado! O motor está processando sua solicitação.")
            st.rerun()

with tab1:
    agentes = supabase.table("agents").select("*").order("created_at", desc=True).execute().data
    
    for ag in agentes:
        with st.container():
            # Cabeçalho do Agente
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.subheader(f"🤖 {ag['name']}")
            status_text = "🟢 ATIVO" if ag['status'] == 'active' else "🔴 PAUSADO"
            c2.write(f"Status: **{status_text}**")
            
            if c3.button("Pausar/Ativar", key=ag['id']):
                novo_status = "paused" if ag['status'] == "active" else "active"
                supabase.table("agents").update({"status": novo_status}).eq("id", ag['id']).execute()
                st.rerun()

            # Resultado da IA
            if ag['last_result']:
                st.markdown("**Último Processamento (Llama 3.3):**")
                st.info(ag['last_result'])
            else:
                st.warning("⏳ Aguardando processamento pelo motor...")
            
            st.divider()
