import os
import streamlit as st
from groq import Groq
import json

def generate_agent_blueprint(user_request):
    """Usa Llama 3.3 para criar a configuração técnica de um novo agente"""
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    prompt = f"""
    Você é um Engenheiro de Prompt Sênior. Sua tarefa é criar um agente de IA completo baseado no pedido do usuário.
    Pedido: "{user_request}"

    Retorne APENAS um JSON com esta estrutura:
    {{
        "name": "Nome curto do agente",
        "role": "Função específica",
        "system_prompt": "Prompt de sistema detalhado com instruções de comportamento, tom de voz e limites",
        "provider": "groq ou gemini",
        "model_name": "llama-3.3-70b-versatile ou gemini-1.5-pro",
        "temperature": 0.7
    }}
    """
    
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(res.choices[0].message.content)

# Mantenha as funções orchestrator_router e get_llm_stream do arquivo anterior aqui...
