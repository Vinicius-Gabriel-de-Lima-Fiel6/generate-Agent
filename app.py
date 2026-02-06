import streamlit as st
from supabase import create_client

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("🚀 Construtor de Agentes Recorrentes")

with st.expander("➕ Criar Nova Automação"):
    with st.form("agente_form"):
        nome = st.text_input("Nome da Tarefa")
        freq = st.selectbox("Frequência", ["diario", "mensal", "anual"])
        config = st.text_area("O que o agente deve fazer?")
        
        if st.form_submit_button("Ligar Agente"):
            supabase.table("agents").insert({
                "name": nome,
                "frequency": freq,
                "prompt_config": config,
                "company_id": "meu_saas",
                "status": "active"
            }).execute()
            st.success(f"Agente {freq} ativado!")

# Listagem com contagem regressiva (Simulada)
st.subheader("📋 Agentes em Operação")
agentes = supabase.table("agents").select("*").execute().data

for ag in agentes:
    col1, col2 = st.columns([3, 1])
    col1.write(f"**{ag['name']}** ({ag['frequency']})")
    col2.write(f"Próxima: {ag['next_run'][:10] if ag['next_run'] else 'Agendando...'}")
    if ag['last_result']:
        st.info(f"Último resultado: {ag['last_result'][:100]}...")
