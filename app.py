import streamlit as st
import requests
import json
from groq import Groq

# --- CONFIGURAÇÃO DE SEGURANÇA ---
# No Streamlit Cloud, preencha estas chaves em 'Settings > Secrets'
try:
    N8N_API_KEY = st.secrets["N8N_API_KEY"]
    N8N_URL = st.secrets["N8N_URL"] # Ex: https://sua-instancia.app.n8n.cloud/api/v1
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("⚠️ Configure as chaves de API nos Secrets do Streamlit Cloud.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# --- ENGINE DE INTELIGÊNCIA ---
def gerar_blueprint_agente(descricao_usuario):
    """Transforma a descrição em uma estrutura lógica para o n8n"""
    
    prompt_engenharia = f"""
    Você é um arquiteto de automação n8n. O usuário quer: "{descricao_usuario}"
    
    Crie um JSON estrito para um workflow n8n com:
    1. 'name': Nome curto do agente.
    2. 'nodes': Lista de objetos com 'type' (ex: n8n-nodes-base.httpRequest, n8n-nodes-base.cron, n8n-nodes-base.emailSend) e 'parameters'.
    3. 'connections': Mapeie a ligação linear entre os nós.
    
    IMPORTANTE: Use apenas tipos de nós oficiais do n8n.
    Saída: APENAS o JSON cru.
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt_engenharia}],
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"}
    )
    return json.loads(chat_completion.choices[0].message.content)

# --- CONEXÃO COM N8N CLOUD ---
def implantar_no_n8n(workflow_json):
    """Envia o workflow para a API do n8n Cloud"""
    endpoint = f"{N8N_URL}/workflows"
    headers = {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Formatação padrão n8n
    payload = {
        "name": workflow_json.get("name", "Novo Agente IA"),
        "nodes": workflow_json.get("nodes", []),
        "connections": workflow_json.get("connections", {}),
        "active": True, # Já nasce rodando
        "settings": {"executionOrder": "v1"}
    }
    
    response = requests.post(endpoint, json=payload, headers=headers)
    return response

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="AgenteA - Criador de Agentes", page_icon="🧠")

st.title("🧠 AgenteA")
st.subheader("Criação de Agentes Autônomos via n8n Cloud")

# Pegar ID da empresa via URL (Integração com seu sistema principal)
company_id = st.query_params.get("company_id", "default")

with st.container(border=True):
    user_prompt = st.text_area(
        "O que o seu agente deve fazer?",
        placeholder="Ex: Monitore o preço do Bitcoin e me avise no Telegram se baixar de 50k",
        height=150
    )
    
    if st.button("🚀 Gerar e Ativar Agente", type="primary", use_container_width=True):
        if user_prompt:
            with st.status("🛠️ Projetando arquitetura...", expanded=True) as status:
                try:
                    # 1. IA cria o desenho do workflow
                    st.write("🤖 IA pensando na lógica...")
                    blueprint = gerar_blueprint_agente(user_prompt)
                    
                    # 2. Envio para o n8n
                    st.write("📡 Enviando para n8n Cloud...")
                    resultado = implantar_no_n8n(blueprint)
                    
                    if resultado.status_code == 200 or resultado.status_code == 201:
                        wf_id = resultado.json().get("id")
                        status.update(label="✅ Agente Ativado com Sucesso!", state="complete")
                        st.success(f"Agente implantado! ID: {wf_id}")
                        
                        # Link direto para o workflow no n8n Cloud
                        n8n_domain = N8N_URL.replace("/api/v1", "")
                        st.link_button("⚙️ Ver Agente no n8n", f"{n8n_domain}/workflow/{wf_id}")
                    else:
                        status.update(label="❌ Erro na Implantação", state="error")
                        st.error(f"Erro no n8n: {resultado.text}")
                except Exception as e:
                    st.error(f"Erro inesperado: {str(e)}")
        else:
            st.warning("Por favor, descreva a ideia do agente.")

st.caption(f"Tenant: {company_id} | Powered by Llama-3.3-70B & n8n Cloud")
