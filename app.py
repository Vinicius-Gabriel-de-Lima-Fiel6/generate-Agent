import streamlit as st
import requests
import json
from groq import Groq
from supabase import create_client

# --- CONFIGURAÇÃO DE SEGURANÇA E CONEXÃO ---
def init_connections():
    try:
        # Inicializa Clientes
        st.session_state.groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
        st.session_state.supabase = create_client(
            st.secrets["SUPABASE_URL"], 
            st.secrets["SUPABASE_KEY"]
        )
        return True
    except Exception as e:
        st.error(f"Erro na configuração: {e}")
        return False

# --- ENGINE DE INTELIGÊNCIA (LLAMA-3.3-70B) ---
def architect_n8n_agent(user_prompt):
    system_instruction = """
    Você é um Arquiteto de Software especializado em n8n.
    Sua tarefa é converter a ideia do usuário em um JSON compatível com a API do n8n.

    REGRAS:
    1. Identifique o Trigger (n8n-nodes-base.cron para tempo, manualTrigger para botão).
    2. Adicione os nós lógicos necessários (n8n-nodes-base.httpRequest, n8n-nodes-base.emailSend, etc).
    3. Retorne APENAS um JSON estruturado com: 'name', 'nodes' e 'connections'.
    """
    
    completion = st.session_state.groq.chat.completions.create(
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)

# --- COMUNICAÇÃO COM N8N CLOUD ---
def deploy_to_n8n(blueprint):
    url = f"{st.secrets['N8N_URL']}/workflows"
    headers = {
        "X-N8N-API-KEY": st.secrets["N8N_API_KEY"],
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": blueprint.get("name", "Novo Agente Autônomo"),
        "nodes": blueprint.get("nodes", []),
        "connections": blueprint.get("connections", {}),
        "active": True,
        "settings": {"executionOrder": "v1"}
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response

# --- INTERFACE DO USUÁRIO ---
st.set_page_config(page_title="AgenteA | AI Builder", layout="wide")

if init_connections():
    # Recupera Contexto (Multi-tenant)
    company_id = st.query_params.get("company_id")
    
    st.title("🧠 AgenteA")
    st.caption("Fábrica de Agentes Inteligentes Autônomos")

    if not company_id:
        st.warning("⚠️ Atenção: ID da Empresa não detectado. O registro será feito como 'Acesso Público'.")
        company_id = "00000000-0000-0000-0000-000000000000" # UUID fake para teste

    # UI de Criação
    with st.container(border=True):
        st.markdown("### ➕ Descreva a missão do novo agente")
        user_input = st.text_area(
            label="O que o sistema deve fazer?",
            placeholder="Ex: Monitore o preço da soja e me avise no WhatsApp se subir mais de 5%.",
            height=150
        )
        
        if st.button("🚀 Criar e Ativar Agente", type="primary", use_container_width=True):
            if user_input:
                with st.status("🏗️ Gerando infraestrutura...", expanded=True) as status:
                    # 1. IA projeta o agente
                    st.write("🧠 Llama-3 projetando workflow...")
                    blueprint = architect_n8n_agent(user_input)
                    
                    # 2. n8n implanta na nuvem
                    st.write("📡 Enviando para n8n Cloud...")
                    n8n_res = deploy_to_n8n(blueprint)
                    
                    if n8n_res.status_code in [200, 201]:
                        wf_data = n8n_res.json()
                        wf_id = wf_data.get("id")
                        
                        # 3. Supabase registra no Banco Seguro (RLS)
                        st.write("💾 Registrando no Supabase...")
                        db_data = {
                            "company_id": company_id,
                            "nome_agente": blueprint.get("name"),
                            "objetivo_bruto": user_input,
                            "n8n_workflow_id": str(wf_id),
                            "blueprint_json": blueprint
                        }
                        st.session_state.supabase.table("agentes").insert(db_data).execute()
                        
                        status.update(label="✅ Agente Ativado com Sucesso!", state="complete")
                        st.balloons()
                        
                        st.success(f"Agente '{blueprint.get('name')}' está agora trabalhando para você.")
                        st.info(f"ID do Workflow: {wf_id}")
                    else:
                        st.error(f"Erro no n8n Cloud: {n8n_res.text}")
            else:
                st.warning("Por favor, descreva sua ideia.")

    st.divider()
    
    # Visualização de Agentes Ativos (Simulação de Dashboard)
    st.subheader("🤖 Agentes Ativos")
    try:
        resp = st.session_state.supabase.table("agentes").select("*").eq("company_id", company_id).execute()
        if resp.data:
            for ag in resp.data:
                with st.expander(f"Agente: {ag['nome_agente']} (Criado em: {ag['criado_em'][:10]})"):
                    st.write(f"**Objetivo:** {ag['objetivo_bruto']}")
                    st.caption(f"Status: {ag['status']} | n8n ID: {ag['n8n_workflow_id']}")
        else:
            st.info("Nenhum agente criado para esta empresa ainda.")
    except:
        st.info("Conecte-se via Dashboard Principal para ver seus agentes.")
