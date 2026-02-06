import streamlit as st
from groq import Groq
import requests
from supabase import create_client
import json

# --- SETUP ---
st.set_page_config(page_title="IA Agent Builder", page_icon="🤖", layout="wide")

# Inicializa Supabase e Groq
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🤖 Construtor Automático de Agentes")
st.markdown("---")

# Interface de Entrada
col1, col2 = st.columns([2, 1])

with col1:
    user_prompt = st.text_area(
        "Descreva a missão do agente:",
        placeholder="Ex: Monitore meu sistema e me mande um alerta no Telegram a cada 30 segundos dizendo que está tudo OK.",
        height=150
    )

if st.button("🚀 Criar e Ativar Agente Agora"):
    if not user_prompt:
        st.warning("Descreva o que o agente deve fazer.")
    else:
        with st.status("IA trabalhando...", expanded=True) as status:
            try:
                # PASSO 1: A IA planeja o agente
                st.write("🧠 Llama-3.3-70B desenhando a lógica...")
                sys_prompt = "Você é um engenheiro de automação. Responda APENAS com um JSON puro contendo: 'name', 'interval_sec', 'message'."
                
                chat = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"} # Força o JSON puro
                )
                
                blueprint = json.loads(chat.choices[0].message.content)
                st.write("✅ Lógica gerada!")

                # PASSO 2: Envio para o Make (Onde a execução acontece)
                st.write("📡 Ativando Webhook no Make.com...")
                response = requests.post(st.secrets["N8N_WEBHOOK_URL"], json=blueprint)
                
                # PASSO 3: Registro no Banco de Dados
                st.write("💾 Salvando configuração no Supabase...")
                db_entry = {
                    "company_id": "00000000-0000-0000-0000-000000000000",
                    "nome_agente": blueprint['name'],
                    "objetivo_bruto": user_prompt,
                    "blueprint_json": blueprint
                }
                supabase.table("agentes").insert(db_entry).execute()
                
                status.update(label="✨ Agente Criado com Sucesso!", state="complete")
                st.balloons()
                
                # Exibição do "Cérebro" do Agente
                st.subheader("Ficha Técnica do Agente")
                st.json(blueprint)
                
            except Exception as e:
                st.error(f"Falha na criação: {e}")

# Rodapé lateral
st.sidebar.success("Sistema conectado via Groq API")
