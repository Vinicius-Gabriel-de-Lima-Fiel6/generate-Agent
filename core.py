import os
import streamlit as st
from groq import Groq
import google.generativeai as genai

def orchestrator_router(user_input, agents):
    """Usa Llama-3.3-70b para decidir qual agente usar"""
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    agent_desc = "\n".join([f"- ID: {a['id']} | Nome: {a['name']} | Função: {a['role']}" for a in agents])
    
    prompt = f"""
    Você é o Roteador de uma plataforma de IA. Analise a entrada do usuário e escolha o melhor agente.
    AGENTES DISPONÍVEIS:
    {agent_desc}

    ENTRADA DO USUÁRIO: "{user_input}"

    Responda APENAS com o ID (UUID) do agente escolhido. Nada mais.
    """
    
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1 # Baixa temperatura para precisão no ID
    )
    return res.choices[0].message.content.strip()

def get_llm_stream(agent, messages):
    """Gera resposta em stream do agente selecionado"""
    if agent['provider'] == 'groq':
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        # Injeta o System Prompt do agente específico
        full_history = [{"role": "system", "content": agent['system_prompt']}] + messages
        
        return client.chat.completions.create(
            model=agent['model_name'],
            messages=full_history,
            temperature=agent.get('temperature', 0.7),
            stream=True
        )
    
    elif agent['provider'] == 'gemini':
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(agent['model_name'])
        # Simplicidade para o Gemini (pode ser expandido para histórico real)
        return model.generate_content(messages[-1]['content'], stream=True)
